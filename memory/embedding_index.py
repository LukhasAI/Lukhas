"""Lightweight embedding index with optional Annoy acceleration."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
# ΛTAG: memory_embedding_index_bootstrap
logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from annoy import AnnoyIndex  # type: ignore
except Exception:
    AnnoyIndex = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import numpy as _np
except Exception:
    _np = None


@dataclass
class EmbeddingIndex:
    """Approximate nearest neighbour index with symbolic tracing."""

    metric: str = "angular"
    trees: int = 10
    dimension: int | None = None
    _vectors: dict[str, list[float]] = field(default_factory=dict)
    _annoy_index: AnnoyIndex | None = None
    _annoy_id_map: dict[int, str] = field(default_factory=dict)
    _dirty: bool = True

    def add(self, item_id: str, vector: Iterable[float]) -> None:
        """Add or update a vector in the index."""
        vector_list = list(vector)
        if not vector_list:
            logger.debug("Skipping empty embedding", extra={"fold_id": item_id})
            return

        if self.dimension is None:
            self.dimension = len(vector_list)
            logger.debug(
                "Initializing embedding index dimension",
                extra={
                    "dimension": self.dimension,
                    "driftScore": 0.0,
                    "affect_delta": 0.05,
                },
            )

        if len(vector_list) != self.dimension:
            logger.warning(
                "Embedding dimension mismatch",
                extra={
                    "fold_id": item_id,
                    "expected": self.dimension,
                    "actual": len(vector_list),
                    "ΛTAG": "memory_embedding_index_dimension",
                },
            )
            return

        self._vectors[item_id] = vector_list
        self._dirty = True

    def remove(self, item_id: str) -> None:
        """Remove a vector from the index if present."""
        if item_id in self._vectors:
            self._vectors.pop(item_id)
            self._dirty = True

    def _ensure_annoy(self) -> None:
        if AnnoyIndex is None or self.dimension is None:
            return
        if not self._dirty and self._annoy_index is not None:
            return

        index = AnnoyIndex(self.dimension, self.metric)
        id_map: dict[int, str] = {}
        for idx, (item_id, vector) in enumerate(self._vectors.items()):
            index.add_item(idx, vector)
            id_map[idx] = item_id
        if self._vectors:
            index.build(self.trees)
        self._annoy_index = index
        self._annoy_id_map = id_map
        self._dirty = False
        logger.debug(
            "Rebuilt Annoy index",
            extra={
                "items": len(self._vectors),
                "trees": self.trees,
                "driftScore": 0.0,
                "affect_delta": 0.01,
            },
        )

    # ΛTAG: memory_embedding_index
    def query(self, vector: Iterable[float], k: int = 10) -> list[str]:
        """Return nearest neighbours for the given vector."""
        vector_list = list(vector)
        if not vector_list or self.dimension is None:
            return []
        if len(vector_list) != self.dimension:
            return []

        if AnnoyIndex is not None:
            self._ensure_annoy()
            if self._annoy_index is None:
                return []
            indices = self._annoy_index.get_nns_by_vector(vector_list, k)
            return [self._annoy_id_map[idx] for idx in indices if idx in self._annoy_id_map]

        if _np is not None and self._vectors:
            matrix = _np.array(list(self._vectors.values()))
            query = _np.array(vector_list)
            scores = matrix @ query
            order = scores.argsort()[::-1]
            ids = list(self._vectors.keys())
            return [ids[i] for i in order[:k]]

        # Fallback to manual scoring
        scored: list[tuple[float, str]] = []
        for item_id, stored in self._vectors.items():
            score = sum(a * b for a, b in zip(vector_list, stored))
            scored.append((score, item_id))
        scored.sort(reverse=True)
        return [item_id for _, item_id in scored[:k]]

    def size(self) -> int:
        """Return number of vectors tracked."""
        return len(self._vectors)
