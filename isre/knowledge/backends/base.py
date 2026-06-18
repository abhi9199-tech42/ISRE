"""Abstract base class for knowledge backends."""

from abc import ABC, abstractmethod
from typing import Any


class KnowledgeBackend(ABC):
    """
    Abstract base class for knowledge backends.
    All knowledge storage implementations must inherit from this class.
    """

    @abstractmethod
    def query(self, concept_key: str) -> Any | None:
        """
        Query knowledge for a specific concept.

        Args:
            concept_key: The key to query (case-insensitive)

        Returns:
            The knowledge data if found, None otherwise
        """
        pass

    @abstractmethod
    def query_concepts(self, concepts: list[str]) -> dict[str, Any | None]:
        """
        Batch query for multiple concepts.

        Args:
            concepts: List of concept keys to query

        Returns:
            Dictionary mapping concept keys to their knowledge data
        """
        pass

    @abstractmethod
    def update(self, concept_key: str, data: Any):
        """
        Update or add a new fact to the knowledge base.

        Args:
            concept_key: The key to update
            data: The knowledge data to store
        """
        pass

    def get_all(self) -> dict[str, Any]:
        """
        Get all knowledge facts.

        Returns:
            Dictionary of all knowledge facts
        """
        return {}

    @abstractmethod
    def clear(self):
        """Clear all knowledge."""
        pass

    def bulk_update(self, data: dict[str, Any]):
        """
        Bulk load multiple facts efficiently.

        Args:
            data: Dictionary mapping keys to knowledge data
        """
        for key, value in data.items():
            self.update(key, value)

    def is_modified(self) -> bool:
        """
        Check if the knowledge storage has been modified.

        Returns:
            True if the storage has been modified since last load
        """
        return False
