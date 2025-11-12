"""
In-memory implementation of memory indexing systems.
"""

from collections import defaultdict
from functools import lru_cache
from typing import Any, Optional, Tuple, TypedDict

import numpy as np


class SearchResult(TypedDict):
    id: str
    vector: list[float]
    metadata: dict[str, Any]
    similarity: float


class EmbeddingIndex:
    """A simple in-memory embedding index with caching."""

    def __init__(self, max_cache_size: int = 128):
        self._vectors: dict[str, np.ndarray] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._vector_matrix: Optional[np.ndarray] = None
        self._vector_ids: list[str] = []
        self._dirty = True
        # The internal search function is cached
        self._search_internal = lru_cache(maxsize=max_cache_size)(self._search_implementation)

    def add(self, vector_id: str, vector: list[float], metadata: Optional[dict[str, Any]] = None):
        """Adds a vector to the index and clears the cache."""
        self._vectors[vector_id] = np.array(vector)
        if metadata:
            self._metadata[vector_id] = metadata
        self._dirty = True
        self._search_internal.cache_clear()

    def _rebuild_matrix(self):
        """Rebuilds the cached vector matrix if it's dirty."""
        if self._dirty:
            if not self._vectors:
                self._vector_matrix = None
                self._vector_ids = []
            else:
                self._vector_ids = list(self._vectors.keys())
                self._vector_matrix = np.array([self._vectors[vid] for vid in self._vector_ids])
            self._dirty = False

    def search(self, query_vector: list[float], top_k: int = 5) -> list[SearchResult]:
        """
        Performs a vectorized cosine similarity search, using a cache.
        """
        # Convert list to tuple to make it hashable for the cache
        return self._search_internal(tuple(query_vector), top_k)

    def _search_implementation(
        self, query_vector: Tuple[float, ...], top_k: int = 5
    ) -> list[SearchResult]:
        """
        The actual implementation of the search, which is cached.
        """
        self._rebuild_matrix()

        if self._vector_matrix is None or len(self._vector_ids) == 0:
            return []

        query_np = np.array(query_vector)

        # Normalize the query vector and the matrix
        query_norm = np.linalg.norm(query_np)
        if query_norm == 0:
            return []

        normalized_query = query_np / query_norm

        matrix_norms = np.linalg.norm(self._vector_matrix, axis=1)
        non_zero_norms_mask = matrix_norms > 0
        normalized_matrix = np.zeros_like(self._vector_matrix, dtype=np.float32)

        # Use np.newaxis to ensure correct broadcasting for division
        normalized_matrix[non_zero_norms_mask] = self._vector_matrix[non_zero_norms_mask] / matrix_norms[non_zero_norms_mask, np.newaxis]

        similarities = np.dot(normalized_matrix, normalized_query)

        # Get the indices of the top_k results
        num_vectors = len(self._vector_ids)
        if top_k >= num_vectors:
            top_k_indices = np.argsort(similarities)[::-1][:top_k]
        else:
            top_k_indices_unsorted = np.argpartition(similarities, -top_k)[-top_k:]
            top_k_indices = top_k_indices_unsorted[np.argsort(similarities[top_k_indices_unsorted])[::-1]]

        results: list[SearchResult] = []
        for i in top_k_indices:
            vector_id = self._vector_ids[i]
            results.append(
                {
                    "id": vector_id,
                    "vector": self._vectors[vector_id].tolist(),
                    "metadata": self._metadata.get(vector_id, {}),
                    "similarity": float(similarities[i]),
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
