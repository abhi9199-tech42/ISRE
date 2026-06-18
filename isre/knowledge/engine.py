"""Knowledge query engine with pluggable backends."""

import time
from typing import Any

from pydantic import BaseModel, Field

from .backends.base import KnowledgeBackend
from .backends.json_backend import JSONKnowledgeBackend


def create_backend(backend_type: str = "memory", **kwargs) -> KnowledgeBackend:
    """Factory: create a knowledge backend by type name.

    Args:
        backend_type: One of "memory", "json", "sqlite"
        kwargs: Passed to the backend constructor

    Returns:
        A configured KnowledgeBackend instance
    """
    if backend_type == "sqlite":
        from .backends.sqlite_backend import SQLiteKnowledgeBackend
        return SQLiteKnowledgeBackend(**kwargs)
    elif backend_type == "json":
        return JSONKnowledgeBackend(**kwargs)
    else:
        return JSONKnowledgeBackend(**kwargs)


class KnowledgeQueryResult(BaseModel):
    """
    Standardized result from any knowledge source.
    """
    source_id: str
    fact_id: str
    content: Any
    confidence: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeQueryEngine:
    """
    Interfaces with external structured knowledge sources.
    Requirement 4.1: Query external structured knowledge sources.
    Requirement 4.4: Separation between reasoning and knowledge.
    """

    def __init__(self, schema_version: str = "1.0", backend: KnowledgeBackend | None = None,
                 backend_type: str = "memory", **backend_kwargs):
        self.schema_version = schema_version
        self._backend = backend or create_backend(backend_type, **backend_kwargs)
        self._cache: dict[str, KnowledgeQueryResult] = {}
        self.query_log: list[dict[str, Any]] = []

    def query(self, concept_key: str) -> KnowledgeQueryResult | None:
        """
        Retrieves knowledge for a specific concept.
        Returns None if knowledge is missing (Knowledge Gap).
        """
        concept_key = concept_key.lower()
        self.query_log.append({"concept": concept_key, "timestamp": time.time()})

        if concept_key in self._cache:
            return self._cache[concept_key]

        data = self._backend.query(concept_key)
        if data:
            res = KnowledgeQueryResult(
                source_id=type(self._backend).__name__.replace("KnowledgeBackend", "").lower(),
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

    def query_concepts(self, concepts: list[str]) -> dict[str, KnowledgeQueryResult | None]:
        """Batch query for multiple concepts."""
        return {c: self.query(c) for c in concepts}

    def get_backend(self) -> KnowledgeBackend:
        """Get the current knowledge backend."""
        return self._backend

    def set_backend(self, backend: KnowledgeBackend):
        """Set a new knowledge backend."""
        self._backend = backend
        self._cache.clear()
