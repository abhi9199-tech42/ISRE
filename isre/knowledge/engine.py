"""Knowledge query engine with pluggable backends."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .backends.base import KnowledgeBackend
from .backends.json_backend import JSONKnowledgeBackend


class KnowledgeQueryResult(BaseModel):
    """
    Standardized result from any knowledge source.
    """
    source_id: str
    fact_id: str
    content: Any
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeQueryEngine:
    """
    Interfaces with external structured knowledge sources.
    Requirement 4.1: Query external structured knowledge sources.
    Requirement 4.4: Separation between reasoning and knowledge.
    """
    
    def __init__(self, schema_version: str = "1.0", backend: Optional[KnowledgeBackend] = None):
        self.schema_version = schema_version
        self._backend = backend or JSONKnowledgeBackend()
        self._cache: Dict[str, KnowledgeQueryResult] = {}
        self.query_log: List[Dict[str, Any]] = []
    
    def query(self, concept_key: str) -> Optional[KnowledgeQueryResult]:
        """
        Retrieves knowledge for a specific concept.
        Returns None if knowledge is missing (Knowledge Gap).
        """
        import time
        concept_key = concept_key.lower()
        self.query_log.append({"concept": concept_key, "timestamp": time.time()})
        
        if concept_key in self._cache:
            return self._cache[concept_key]

        data = self._backend.query(concept_key)
        if data:
            res = KnowledgeQueryResult(
                source_id="json_backend",
                fact_id=f"fact_{concept_key}",
                content=data,
                confidence=1.0,
                metadata={"schema": self.schema_version, "backend": type(self._backend).__name__}
            )
            self._cache[concept_key] = res
            return res
        return None
    
    def update_knowledge(self, concept_key: str, data: Any):
        """Update or add a new fact to the knowledge base."""
        self._backend.update(concept_key, data)
        # Invalidate cache
        if concept_key.lower() in self._cache:
            del self._cache[concept_key.lower()]
    
    def query_concepts(self, concepts: List[str]) -> Dict[str, Optional[KnowledgeQueryResult]]:
        """Batch query for multiple concepts."""
        return {c: self.query(c) for c in concepts}
    
    def get_backend(self) -> KnowledgeBackend:
        """Get the current knowledge backend."""
        return self._backend
    
    def set_backend(self, backend: KnowledgeBackend):
        """Set a new knowledge backend."""
        self._backend = backend
        self._cache.clear()