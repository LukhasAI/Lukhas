from datetime import datetime
from typing import Optional, Any

import numpy as np

from lukhas.memory.index import EmbeddingIndex, SearchResult


class SoftDeleteEmbeddingIndex(EmbeddingIndex):
    """An embedding index with soft-delete functionality."""

    def add(self, vector_id: str, vector: list[float], metadata: Optional[dict[str, Any]] = None):
        """Adds a vector to the index, ensuring soft-delete fields are initialized."""
        if metadata is None:
            metadata = {}
        metadata["is_deleted"] = False
        metadata["deleted_at"] = None
        super().add(vector_id, vector, metadata)

    def soft_delete(self, vector_id: str):
        """Soft-deletes a vector by marking it as deleted and adding a timestamp."""
        if vector_id in self._metadata:
            self._metadata[vector_id]["is_deleted"] = True
            self._metadata[vector_id]["deleted_at"] = datetime.utcnow().isoformat()

    def restore(self, vector_id: str):
        """Restores a soft-deleted vector."""
        if vector_id in self._metadata:
            self._metadata[vector_id]["is_deleted"] = False
            self._metadata[vector_id]["deleted_at"] = None

    def search(
        self, query_vector: list[float], top_k: int = 5, include_deleted: bool = False
    ) -> list[SearchResult]:
        """
        Performs a cosine similarity search, optionally including soft-deleted items.
        This implementation is optimized to avoid searching over soft-deleted items.
        """
        if not self._vectors:
            return []

        query_np = np.array(query_vector)

        if include_deleted:
            search_vectors = self._vectors
        else:
            # Filter vectors before calculating similarity
            search_vectors = {
                vector_id: vector
                for vector_id, vector in self._vectors.items()
                if not self._metadata.get(vector_id, {}).get("is_deleted", False)
            }

        if not search_vectors:
            return []

        norm_query = np.linalg.norm(query_np)

        if norm_query == 0:
            # If query norm is 0, all similarities are 0. Just return top_k active items.
            # To have a deterministic result, sort by id.
            sorted_ids = sorted(search_vectors.keys())
            results: list[SearchResult] = []
            for vector_id in sorted_ids[:top_k]:
                 results.append({
                    "id": vector_id,
                    "vector": self._vectors[vector_id].tolist(),
                    "metadata": self._metadata.get(vector_id, {}),
                    "similarity": 0.0,
                })
            return results

        # Calculate cosine similarity only for active vectors
        similarities = {}
        for vector_id, vector in search_vectors.items():
            norm_vector = np.linalg.norm(vector)
            if norm_vector == 0:
                similarity = 0.0
            else:
                similarity = np.dot(query_np, vector) / (norm_query * norm_vector)
            similarities[vector_id] = similarity

        # Sort by similarity and return top_k results
        sorted_ids = sorted(similarities.keys(), key=lambda x: similarities[x], reverse=True)

        results: list[SearchResult] = []
        for vector_id in sorted_ids[:top_k]:
            results.append(
                {
                    "id": vector_id,
                    "vector": self._vectors[vector_id].tolist(),
                    "metadata": self._metadata.get(vector_id, {}),
                    "similarity": similarities[vector_id],
                }
            )
        return results
