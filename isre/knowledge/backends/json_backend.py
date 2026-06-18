"""JSON file-based knowledge backend implementation."""

from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import time
from .base import KnowledgeBackend


class JSONKnowledgeBackend(KnowledgeBackend):
    """
    JSON file-based knowledge backend.
    Persistent storage of knowledge facts with caching.
    """
    
    def __init__(self, path: str = "knowledge.json"):
        self.path = Path(path)
        self._cache: Dict[str, Any] = {}
        self._last_modified = 0
        
        # Default knowledge for backward compatibility
        self._default_knowledge = {
            "apple": {"category": "fruit", "edible": True, "color": ["red", "green"]},
            "run": {"category": "action", "energy_cost": "high"},
            "physics_gravity": {"value": 9.81, "unit": "m/s^2"}
        }
        
        self._load()
    
    def _load(self):
        """Load knowledge from JSON file."""
        try:
            if self.path.exists():
                with open(self.path, 'r') as f:
                    file_knowledge = json.load(f)
                # Merge with default knowledge (file overrides defaults)
                self._cache = {**self._default_knowledge, **file_knowledge}
                self._last_modified = self.path.stat().st_mtime
            else:
                self._cache = self._default_knowledge.copy()
        except (json.JSONDecodeError, IOError):
            self._cache = self._default_knowledge.copy()
    
    def _save(self):
        """Save knowledge to JSON file."""
        try:
            # Create parent directory if it doesn't exist
            self.path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write only the knowledge (not defaults)
            with open(self.path, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except IOError:
            pass
    
    def query(self, concept_key: str) -> Optional[Any]:
        """Query knowledge for a specific concept."""
        return self._cache.get(concept_key.lower())
    
    def query_concepts(self, concepts: List[str]) -> Dict[str, Optional[Any]]:
        """Batch query for multiple concepts."""
        return {c: self.query(c) for c in concepts}
    
    def update(self, concept_key: str, data: Any):
        """Update or add a new fact to the knowledge base."""
        self._cache[concept_key.lower()] = data
        self._save()
    
    def bulk_update(self, data: Dict[str, Any]):
        """Bulk load multiple facts efficiently (single file write)."""
        for key, value in data.items():
            self._cache[key.lower()] = value
        # Only save for reasonably sized updates to avoid massive JSON writes
        if len(data) < 10000:
            self._save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all knowledge facts."""
        return self._cache.copy()
    
    def clear(self):
        """Clear all knowledge."""
        self._cache = self._default_knowledge.copy()
        self._save()