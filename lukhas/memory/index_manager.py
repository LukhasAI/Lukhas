"""
SPDX-License-Identifier: Apache-2.0

lukhas/memory/index_manager.py

IndexManager: Thread-safe management of multiple EmbeddingIndex instances.
Provides CRUD operations for named indexes with metadata tracking.

Usage:
    manager = IndexManager()

    # Create index
    index_id = manager.create_index(name="docs", metric="angular", dimension=1536)

    # Add vectors
    manager.add_vector(index_id, "doc-1", vector)

    # Search
    results = manager.search(index_id, query_vector, k=10)

    # Delete
    manager.delete_index(index_id)
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
from uuid import uuid4

from lukhas.memory.embedding_index import EmbeddingIndex

logger = logging.getLogger(__name__)


@dataclass
class IndexMetadata:
    """Metadata for a managed index."""
    id: str
    name: str
    metric: str
    dimension: Optional[int]
    created_at: float
    updated_at: float
    vector_count: int = 0


class IndexManager:
    """
    Thread-safe manager for multiple EmbeddingIndex instances.

    Provides CRUD operations with automatic metadata tracking.
    Supports named indexes with unique IDs.
    """

    def __init__(self):
        """Initialize the index manager."""
        self._indexes: Dict[str, EmbeddingIndex] = {}
        self._metadata: Dict[str, IndexMetadata] = {}
        self._name_to_id: Dict[str, str] = {}
        self._lock = threading.RLock()
        logger.info("IndexManager initialized", extra={
            "ΛTAG": "memory_index_manager_init",
            "driftScore": 0.0,
            "affect_delta": 0.01,
        })

    def create_index(
        self,
        name: str,
        metric: str = "angular",
        trees: int = 10,
        dimension: Optional[int] = None
    ) -> str:
        """
        Create a new embedding index.

        Args:
            name: Unique name for the index
            metric: Distance metric ("angular" or "euclidean")
            trees: Number of trees for Annoy index
            dimension: Vector dimension (auto-detected if None)

        Returns:
            Index ID (UUID)

        Raises:
            ValueError: If index with this name already exists
        """
        with self._lock:
            if name in self._name_to_id:
                raise ValueError(f"Index with name '{name}' already exists")

            index_id = f"idx_{uuid4().hex[:16]}"
            index = EmbeddingIndex(metric=metric, trees=trees, dimension=dimension)

            now = time.time()
            metadata = IndexMetadata(
                id=index_id,
                name=name,
                metric=metric,
                dimension=dimension,
                created_at=now,
                updated_at=now,
                vector_count=0
            )

            self._indexes[index_id] = index
            self._metadata[index_id] = metadata
            self._name_to_id[name] = index_id

            logger.info(
                f"Created index: {name}",
                extra={
                    "ΛTAG": "memory_index_manager_create",
                    "index_id": index_id,
                    "name": name,
                    "metric": metric,
                    "dimension": dimension,
                    "driftScore": 0.0,
                    "affect_delta": 0.02,
                }
            )

            return index_id

    def get_index(self, index_id: str) -> Optional[EmbeddingIndex]:
        """
        Get an index by ID.

        Args:
            index_id: Index ID

        Returns:
            EmbeddingIndex instance or None if not found
        """
        with self._lock:
            return self._indexes.get(index_id)

    def get_metadata(self, index_id: str) -> Optional[IndexMetadata]:
        """
        Get index metadata by ID.

        Args:
            index_id: Index ID

        Returns:
            IndexMetadata or None if not found
        """
        with self._lock:
            return self._metadata.get(index_id)

    def list_indexes(self) -> List[IndexMetadata]:
        """
        List all indexes with metadata.

        Returns:
            List of IndexMetadata for all indexes
        """
        with self._lock:
            return list(self._metadata.values())

    def delete_index(self, index_id: str) -> bool:
        """
        Delete an index by ID.

        Args:
            index_id: Index ID

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if index_id not in self._indexes:
                return False

            metadata = self._metadata[index_id]

            # Remove from all tracking structures
            del self._indexes[index_id]
            del self._metadata[index_id]
            del self._name_to_id[metadata.name]

            logger.info(
                f"Deleted index: {metadata.name}",
                extra={
                    "ΛTAG": "memory_index_manager_delete",
                    "index_id": index_id,
                    "name": metadata.name,
                    "driftScore": 0.0,
                    "affect_delta": 0.01,
                }
            )

            return True

    def add_vector(
        self,
        index_id: str,
        item_id: str,
        vector: Iterable[float]
    ) -> None:
        """
        Add a vector to an index.

        Args:
            index_id: Index ID
            item_id: Unique item identifier
            vector: Vector embedding

        Raises:
            KeyError: If index not found
            ValueError: If dimension mismatch
        """
        with self._lock:
            if index_id not in self._indexes:
                raise KeyError(f"Index not found: {index_id}")

            index = self._indexes[index_id]
            metadata = self._metadata[index_id]

            # Validate dimension before adding
            vector_list = list(vector)
            if metadata.dimension is not None and len(vector_list) != metadata.dimension:
                raise ValueError(
                    f"Dimension mismatch: expected {metadata.dimension}, got {len(vector_list)}"
                )

            # Add vector to index (will auto-detect dimension if needed)
            old_size = index.size()
            index.add(item_id, vector_list)
            new_size = index.size()

            # Check if add was actually successful (EmbeddingIndex silently skips on dimension mismatch)
            if new_size == old_size and item_id not in index._vectors:
                raise ValueError(
                    f"Failed to add vector {item_id}: dimension mismatch or invalid vector"
                )

            # Update metadata
            metadata.updated_at = time.time()
            metadata.vector_count = new_size

            # Auto-detect dimension on first add
            if metadata.dimension is None and index.dimension is not None:
                metadata.dimension = index.dimension

            logger.debug(
                f"Added vector to index {metadata.name}",
                extra={
                    "ΛTAG": "memory_index_manager_add_vector",
                    "index_id": index_id,
                    "item_id": item_id,
                    "vector_count": metadata.vector_count,
                }
            )

    def remove_vector(
        self,
        index_id: str,
        item_id: str
    ) -> bool:
        """
        Remove a vector from an index.

        Args:
            index_id: Index ID
            item_id: Item identifier to remove

        Returns:
            True if removed, False if item not found

        Raises:
            KeyError: If index not found
        """
        with self._lock:
            if index_id not in self._indexes:
                raise KeyError(f"Index not found: {index_id}")

            index = self._indexes[index_id]
            metadata = self._metadata[index_id]

            # Check if item exists
            if item_id not in index._vectors:
                return False

            # Remove from index
            index.remove(item_id)

            # Update metadata
            metadata.updated_at = time.time()
            metadata.vector_count = index.size()

            logger.debug(
                f"Removed vector from index {metadata.name}",
                extra={
                    "ΛTAG": "memory_index_manager_remove_vector",
                    "index_id": index_id,
                    "item_id": item_id,
                    "vector_count": metadata.vector_count,
                }
            )

            return True

    def search(
        self,
        index_id: str,
        query_vector: Iterable[float],
        k: int = 10
    ) -> List[str]:
        """
        Search for nearest neighbors in an index.

        Args:
            index_id: Index ID
            query_vector: Query vector
            k: Number of nearest neighbors to return

        Returns:
            List of item IDs (nearest neighbors)

        Raises:
            KeyError: If index not found
        """
        with self._lock:
            if index_id not in self._indexes:
                raise KeyError(f"Index not found: {index_id}")

            index = self._indexes[index_id]
            results = index.query(query_vector, k=k)

            logger.debug(
                f"Searched index {self._metadata[index_id].name}",
                extra={
                    "ΛTAG": "memory_index_manager_search",
                    "index_id": index_id,
                    "k": k,
                    "results_count": len(results),
                }
            )

            return results

    def get_vector(
        self,
        index_id: str,
        item_id: str
    ) -> Optional[List[float]]:
        """
        Get a vector from an index by item ID.

        Args:
            index_id: Index ID
            item_id: Item identifier

        Returns:
            Vector as list of floats, or None if not found

        Raises:
            KeyError: If index not found
        """
        with self._lock:
            if index_id not in self._indexes:
                raise KeyError(f"Index not found: {index_id}")

            index = self._indexes[index_id]
            return index._vectors.get(item_id)

    def size(self) -> int:
        """
        Get total number of managed indexes.

        Returns:
            Number of indexes
        """
        with self._lock:
            return len(self._indexes)

    def total_vectors(self) -> int:
        """
        Get total number of vectors across all indexes.

        Returns:
            Total vector count
        """
        with self._lock:
            return sum(meta.vector_count for meta in self._metadata.values())
