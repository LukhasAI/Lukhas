"""
In-memory implementation of memory indexing systems.
"""
from collections import defaultdict
from typing import Any, Dict, List, Optional, TypedDict

import numpy as np


class SearchResult(TypedDict):
    id: str
    vector: list[float]
    metadata: dict[str, Any]
    similarity: float

class EmbeddingIndex:
    """A simple in-memory embedding index."""

    def __init__(self):
        self._vectors: dict[str, np.ndarray] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def add(self, vector_id: str, vector: list[float], metadata: Optional[dict[str, Any]] = None):
        """Adds a vector to the index."""
        self._vectors[vector_id] = np.array(vector)
        if metadata:
            self._metadata[vector_id] = metadata

    def search(self, query_vector: list[float], top_k: int = 5) -> list[SearchResult]:
        """
        Performs a cosine similarity search.
        """
        if not self._vectors:
            return []

        query_np = np.array(query_vector)

        # Calculate cosine similarity
        similarities = {}
        for vector_id, vector in self._vectors.items():
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
            results.append({
                "id": vector_id,
                "vector": self._vectors[vector_id].tolist(),
                "metadata": self._metadata.get(vector_id, {}),
                "similarity": similarities[vector_id]
            })
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
