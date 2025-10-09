"""In-memory vector store used by tests."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


class InMemoryVectorStore:
    """Minimal implementation with cosine similarity search."""

    def __init__(self):
        self._vectors: Dict[str, List[float]] = {}

    def index(self, key: str, vector: Iterable[float]):
        self._vectors[key] = list(vector)

    def search(self, query: Iterable[float], top_k: int = 5) -> List[Tuple[str, float]]:
        import math

        query_vec = list(query)
        results: List[Tuple[str, float]] = []
        for key, vec in self._vectors.items():
            dot = sum(a * b for a, b in zip(query_vec, vec))
            norm_query = math.sqrt(sum(a * a for a in query_vec)) or 1.0
            norm_vec = math.sqrt(sum(a * a for a in vec)) or 1.0
            similarity = dot / (norm_query * norm_vec)
            results.append((key, similarity))
        results.sort(key=lambda item: item[1], reverse=True)
        return results[:top_k]
