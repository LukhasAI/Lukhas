"""
In-memory implementation of memory indexing systems.
"""
import datetime
from collections import defaultdict
from typing import Any, Optional, TypedDict

import numpy as np

from lukhas.memory.soft_delete import SoftDeletable


class SearchResult(TypedDict):
    id: str
    vector: list[float]
    metadata: dict[str, Any]
    similarity: float


class MemoryEntry(SoftDeletable):
    """Represents a single entry in the embedding index."""
    def __init__(self, vector: list[float], metadata: Optional[dict[str, Any]] = None):
        super().__init__()
        self.vector_np = np.array(vector)
        self.metadata = metadata if metadata else {}

    @property
    def vector(self) -> list[float]:
        return self.vector_np.tolist()


class EmbeddingIndex:
    """A simple in-memory embedding index."""

    def __init__(self):
        self._entries: dict[str, MemoryEntry] = {}

    def add(self, vector_id: str, vector: list[float], metadata: Optional[dict[str, Any]] = None):
        """Adds a vector to the index."""
        self._entries[vector_id] = MemoryEntry(vector, metadata)

    def soft_delete(self, vector_id: str):
        """Marks a vector as deleted."""
        if entry := self._entries.get(vector_id):
            entry.soft_delete()

    def restore(self, vector_id: str):
        """Restores a soft-deleted vector."""
        if entry := self._entries.get(vector_id):
            entry.restore()

    def is_deleted(self, vector_id: str) -> bool:
        """Checks if a vector is soft-deleted."""
        if entry := self._entries.get(vector_id):
            return entry.is_deleted
        return False

    def get_deleted_at(self, vector_id: str) -> Optional[datetime.datetime]:
        """Gets the deletion timestamp for a vector."""
        if entry := self._entries.get(vector_id):
            return entry.deleted_at
        return None

    def search(self, query_vector: list[float], top_k: int = 5) -> list[SearchResult]:
        """
        Performs a cosine similarity search.
        """
        if not self._entries:
            return []

        query_np = np.array(query_vector)

        # Calculate cosine similarity
        similarities = {}
        for vector_id, entry in self._entries.items():
            if entry.is_deleted:
                continue

            vector = entry.vector_np
            norm_query = np.linalg.norm(query_np)
            norm_vector = np.linalg.norm(vector)
            if norm_query == 0 or norm_vector == 0:
                similarity = 0.0
            else:
                similarity = np.dot(query_np, vector) / (norm_query * norm_vector)
            similarities[vector_id] = similarity

        # Sort by similarity and return top_k results
        sorted_ids = sorted(similarities.keys(), key=lambda x: similarities[x], reverse=True)

        results: list[SearchResult] = []
        for vector_id in sorted_ids[:top_k]:
            entry = self._entries[vector_id]
            results.append(
                {
                    "id": vector_id,
                    "vector": entry.vector,
                    "metadata": entry.metadata,
                    "similarity": similarities[vector_id],
                }
            )
        return results


class IndexManager:
    """Manages embedding indexes for different tenants."""

    def __init__(self):
        self._indexes: dict[str, EmbeddingIndex] = defaultdict(EmbeddingIndex)

    def get_index(self, tenant_id: str) -> EmbeddingIndex:
        """Returns the index for a given tenant."""
        return self._indexes[tenant_id]


# Singleton instance of the IndexManager
index_manager = IndexManager()
