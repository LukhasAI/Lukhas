#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: lazy_loading_embeddings.py
║ Path: memory/systems/lazy_loading_embeddings.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🚀 LUKHAS AI - LAZY LOADING EMBEDDING SYSTEM
║ ║ On-demand embedding loading for large-scale memory systems
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Module: LAZY LOADING EMBEDDINGS
║ ║ Path: memory/systems/lazy_loading_embeddings.py
║ ║ Version: 1.0.0 | Created: 2025-07-29
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Description: A symphony of intelligence, orchestrating efficient memory retrieval.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ In the grand tapestry of computational existence, where the threads of data
║ ║ weave intricate patterns of knowledge, the Lazy Loading Embedding System emerges
║ ║ as a phoenix from the ashes of inefficiency, rising to illuminate the path of
║ ║ on-demand access. Like a masterful poet who carefully chooses words to evoke
║ ║ emotion, this module embraces the art of restraint, granting users the power
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛADVANCED, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import sqlite3
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np
import psutil  # For memory monitoring


@dataclass
class EmbeddingCacheEntry:
    """Cache entry for a loaded embedding"""

    embedding: np.ndarray
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    memory_id: str = ""
    size_bytes: int = 0

    def __post_init__(self):
        if self.embedding is not None:
            self.size_bytes = self.embedding.nbytes


class LRUEmbeddingCache:
    """
    LRU cache for embeddings with memory pressure management.

    Features:
    - Memory-aware eviction based on system RAM usage
    - Access pattern tracking for intelligent caching
    - Batch loading optimization
    - Thread-safe operations
    """

    def __init__(
        self,
        max_entries: int = 10000,
        max_memory_mb: int = 512,
        memory_pressure_threshold: float = 0.8,
        enable_access_tracking: bool = True,
    ):
        self.max_entries = max_entries
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.memory_pressure_threshold = memory_pressure_threshold
        self.enable_access_tracking = enable_access_tracking

        # Thread-safe ordered dict for LRU behavior
        self._cache: OrderedDict[str, EmbeddingCacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._current_memory_usage = 0

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_pressure_evictions": 0,
            "batch_loads": 0,
        }

        logger.info(
            "LRU embedding cache initialized",
            max_entries=max_entries,
            max_memory_mb=max_memory_mb,
            memory_pressure_threshold=memory_pressure_threshold,
        )

    def get(self, memory_id: str) -> Optional[np.ndarray]:
        """Get embedding from cache if available"""
        with self._lock:
            if memory_id in self._cache:
                entry = self._cache[memory_id]
                entry.access_count += 1
                entry.last_accessed = datetime.now(timezone.utc)

                # Move to end (most recently used)
                self._cache.move_to_end(memory_id)

                self.stats["hits"] += 1
                return entry.embedding.copy()  # Return copy to prevent modification
            else:
                self.stats["misses"] += 1
                return None

    def put(self, memory_id: str, embedding: np.ndarray) -> None:
        """Store embedding in cache with intelligent eviction"""
        with self._lock:
            # Create cache entry
            entry = EmbeddingCacheEntry(embedding=embedding.copy(), memory_id=memory_id)

            # Check if already exists
            if memory_id in self._cache:
                old_entry = self._cache[memory_id]
                self._current_memory_usage -= old_entry.size_bytes

            # Add new entry
            self._cache[memory_id] = entry
            self._current_memory_usage += entry.size_bytes

            # Evict if necessary
            self._evict_if_needed()

    def put_batch(self, embeddings: dict[str, np.ndarray]) -> None:
        """Batch store multiple embeddings efficiently"""
        with self._lock:
            self.stats["batch_loads"] += 1

            for memory_id, embedding in embeddings.items():
                entry = EmbeddingCacheEntry(embedding=embedding.copy(), memory_id=memory_id)

                if memory_id in self._cache:
                    old_entry = self._cache[memory_id]
                    self._current_memory_usage -= old_entry.size_bytes

                self._cache[memory_id] = entry
                self._current_memory_usage += entry.size_bytes

            # Single eviction pass after batch
            self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        """Evict entries based on LRU and memory pressure"""

        # Check memory pressure from system RAM
        memory_pressure = self._check_memory_pressure()

        # Evict based on count limit
        while len(self._cache) > self.max_entries:
            self._evict_oldest()
            self.stats["evictions"] += 1

        # Evict based on memory limit
        while self._current_memory_usage > self.max_memory_bytes:
            self._evict_oldest()
            self.stats["evictions"] += 1

        # Evict based on system memory pressure
        if memory_pressure > self.memory_pressure_threshold:
            evict_count = max(1, len(self._cache) // 10)  # Evict 10% when under pressure
            for _ in range(evict_count):
                if self._cache:
                    self._evict_oldest()
                    self.stats["memory_pressure_evictions"] += 1

    def _evict_oldest(self) -> None:
        """Evict the least recently used entry"""
        if self._cache:
            memory_id, entry = self._cache.popitem(last=False)  # Remove first (oldest)
            self._current_memory_usage -= entry.size_bytes

    def _check_memory_pressure(self) -> float:
        """Check system memory pressure"""
        try:
            memory_info = psutil.virtual_memory()
            return memory_info.percent / 100.0
        except Exception:
            return 0.5  # Default to moderate pressure if can't check

    def clear(self) -> None:
        """Clear all cached embeddings"""
        with self._lock:
            self._cache.clear()
            self._current_memory_usage = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            hit_rate = (
                self.stats["hits"] / (self.stats["hits"] + self.stats["misses"])
                if (self.stats["hits"] + self.stats["misses"]) > 0
                else 0
            )

            return {
                **self.stats,
                "hit_rate": hit_rate,
                "current_entries": len(self._cache),
                "current_memory_mb": self._current_memory_usage / (1024 * 1024),
                "memory_pressure": self._check_memory_pressure(),
            }


class EmbeddingStorage:
    """
    Persistent storage backend for embeddings.

    Uses SQLite for metadata and file system for embedding data.
    Supports both individual and batch operations.
    """

    def __init__(self, storage_path: Union[str, Path]):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # SQLite database for metadata
        self.db_path = self.storage_path / "embeddings.db"
        self._init_database()

        # Directory for embedding files
        self.embeddings_dir = self.storage_path / "embeddings"
        self.embeddings_dir.mkdir(exist_ok=True)

        logger.info("Embedding storage initialized", storage_path=str(self.storage_path))

    def _init_database(self) -> None:
        """Initialize SQLite database for embedding metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS embeddings (
                    memory_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    dimension INTEGER NOT NULL,
                    dtype TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 0
                )
            """
            )
            conn.commit()

    def store_embedding(self, memory_id: str, embedding: np.ndarray) -> None:
        """Store embedding to persistent storage"""

        # Generate file path
        file_hash = hashlib.sha256(memory_id.encode()).hexdigest()[:16]
        file_path = self.embeddings_dir / f"{file_hash}.npy"

        # Save embedding to file
        np.save(file_path, embedding)

        # Store metadata in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO embeddings
                (memory_id, file_path, dimension, dtype, created_at, last_accessed, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    memory_id,
                    str(file_path),
                    embedding.shape[0],
                    str(embedding.dtype),
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                    0,
                ),
            )
            conn.commit()

    def load_embedding(self, memory_id: str) -> Optional[np.ndarray]:
        """Load embedding from persistent storage"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT file_path, access_count FROM embeddings WHERE memory_id = ?",
                (memory_id,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            file_path, access_count = row

            try:
                # Load embedding from file
                embedding = np.load(file_path)

                # Update access statistics
                conn.execute(
                    """
                    UPDATE embeddings
                    SET last_accessed = ?, access_count = ?
                    WHERE memory_id = ?
                """,
                    (datetime.now(timezone.utc).isoformat(), access_count + 1, memory_id),
                )
                conn.commit()

                return embedding

            except Exception as e:
                logger.error("Failed to load embedding", memory_id=memory_id, error=str(e))
                return None

    def load_embeddings_batch(self, memory_ids: list[str]) -> dict[str, np.ndarray]:
        """Load multiple embeddings efficiently"""

        embeddings = {}

        with sqlite3.connect(self.db_path) as conn:
            # Get file paths for all requested embeddings
            placeholders = ",".join(["?"] * len(memory_ids))
            cursor = conn.execute(
                f"SELECT memory_id, file_path, access_count FROM embeddings WHERE memory_id IN ({placeholders})",
                memory_ids,
            )

            rows = cursor.fetchall()

            # Load embeddings and update access counts
            for memory_id, file_path, access_count in rows:
                try:
                    embedding = np.load(file_path)
                    embeddings[memory_id] = embedding

                    # Update access count
                    conn.execute(
                        """
                        UPDATE embeddings
                        SET last_accessed = ?, access_count = ?
                        WHERE memory_id = ?
                    """,
                        (datetime.now(timezone.utc).isoformat(), access_count + 1, memory_id),
                    )

                except Exception as e:
                    logger.error(
                        "Failed to load embedding in batch",
                        memory_id=memory_id,
                        error=str(e),
                    )

            conn.commit()

        return embeddings

    def exists(self, memory_id: str) -> bool:
        """Check if embedding exists in storage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM embeddings WHERE memory_id = ? LIMIT 1", (memory_id,))
            return cursor.fetchone() is not None

    def delete_embedding(self, memory_id: str) -> bool:
        """Delete embedding from storage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT file_path FROM embeddings WHERE memory_id = ?", (memory_id,))
            row = cursor.fetchone()

            if row:
                file_path = Path(row[0])
                try:
                    file_path.unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(
                        "Failed to delete embedding file",
                        file_path=str(file_path),
                        error=str(e),
                    )

                conn.execute("DELETE FROM embeddings WHERE memory_id = ?", (memory_id,))
                conn.commit()
                return True

            return False

    def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*), AVG(dimension), SUM(access_count) FROM embeddings")
            count, avg_dim, total_accesses = cursor.fetchone()

            # Calculate total storage size
            total_size = 0
            for file_path in self.embeddings_dir.glob("*.npy"):
                total_size += file_path.stat().st_size

            return {
                "total_embeddings": count or 0,
                "average_dimension": avg_dim or 0,
                "total_accesses": total_accesses or 0,
                "storage_size_mb": total_size / (1024 * 1024),
                "storage_path": str(self.storage_path),
            }


class LazyEmbeddingLoader:
    """
    Main lazy loading system that combines caching and persistent storage.

    Provides transparent embedding access with intelligent caching,
    batch loading optimization, and memory pressure management.
    """

    def __init__(
        self,
        storage_path: Union[str, Path],
        cache_size: int = 10000,
        cache_memory_mb: int = 512,
        batch_size: int = 100,
        prefetch_enabled: bool = True,
    ):
        self.storage = EmbeddingStorage(storage_path)
        self.cache = LRUEmbeddingCache(max_entries=cache_size, max_memory_mb=cache_memory_mb)
        self.batch_size = batch_size
        self.prefetch_enabled = prefetch_enabled

        # Batch loading optimization
        self._pending_loads: list[str] = []
        self._batch_load_lock = threading.Lock()
        self._batch_load_timer: Optional[threading.Timer] = None
        self._batch_load_delay = 0.01  # 10ms delay for batching

        logger.info(
            "Lazy embedding loader initialized",
            storage_path=str(storage_path),
            cache_size=cache_size,
            cache_memory_mb=cache_memory_mb,
            batch_size=batch_size,
        )

    async def get_embedding(self, memory_id: str) -> Optional[np.ndarray]:
        """Get embedding with lazy loading and caching"""

        # Try cache first
        embedding = self.cache.get(memory_id)
        if embedding is not None:
            return embedding

        # Load from storage
        embedding = self.storage.load_embedding(memory_id)
        if embedding is not None:
            # Cache for future access
            self.cache.put(memory_id, embedding)
            return embedding

        return None

    async def get_embeddings_batch(self, memory_ids: list[str]) -> dict[str, np.ndarray]:
        """Get multiple embeddings efficiently with batch loading"""

        embeddings = {}
        missing_ids = []

        # Check cache first
        for memory_id in memory_ids:
            cached_embedding = self.cache.get(memory_id)
            if cached_embedding is not None:
                embeddings[memory_id] = cached_embedding
            else:
                missing_ids.append(memory_id)

        # Batch load missing embeddings
        if missing_ids:
            loaded_embeddings = self.storage.load_embeddings_batch(missing_ids)

            # Cache loaded embeddings
            if loaded_embeddings:
                self.cache.put_batch(loaded_embeddings)
                embeddings.update(loaded_embeddings)

        return embeddings

    async def store_embedding(self, memory_id: str, embedding: np.ndarray) -> None:
        """Store embedding with caching"""

        # Store in persistent storage
        self.storage.store_embedding(memory_id, embedding)

        # Cache for immediate access
        self.cache.put(memory_id, embedding)

    async def prefetch_embeddings(self, memory_ids: list[str]) -> None:
        """Prefetch embeddings to warm the cache"""

        if not self.prefetch_enabled:
            return

        # Filter out already cached embeddings
        to_prefetch = [memory_id for memory_id in memory_ids if self.cache.get(memory_id) is None]

        if to_prefetch:
            logger.debug("Prefetching embeddings", count=len(to_prefetch))
            await self.get_embeddings_batch(to_prefetch)

    def exists(self, memory_id: str) -> bool:
        """Check if embedding exists (cache or storage)"""
        return self.cache.get(memory_id) is not None or self.storage.exists(memory_id)

    async def delete_embedding(self, memory_id: str) -> bool:
        """Delete embedding from cache and storage"""

        # Remove from cache
        with self.cache._lock:
            if memory_id in self.cache._cache:
                entry = self.cache._cache.pop(memory_id)
                self.cache._current_memory_usage -= entry.size_bytes

        # Remove from storage
        return self.storage.delete_embedding(memory_id)

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics"""

        cache_stats = self.cache.get_stats()
        storage_stats = self.storage.get_storage_stats()

        return {
            "cache": cache_stats,
            "storage": storage_stats,
            "batch_size": self.batch_size,
            "prefetch_enabled": self.prefetch_enabled,
            "efficiency_metrics": {
                "cache_hit_rate": cache_stats.get("hit_rate", 0),
                "memory_efficiency": cache_stats.get("current_memory_mb", 0)
                / (self.cache.max_memory_bytes / (1024 * 1024)),
                "storage_utilization": storage_stats.get("total_embeddings", 0),
            },
        }

    def optimize_cache(self) -> dict[str, Any]:
        """Optimize cache based on access patterns"""

        # Force memory pressure cleanup
        with self.cache._lock:
            original_size = len(self.cache._cache)
            self.cache._evict_if_needed()
            cleaned_entries = original_size - len(self.cache._cache)

        stats = self.get_performance_stats()

        logger.info(
            "Cache optimization completed",
            cleaned_entries=cleaned_entries,
            current_entries=stats["cache"]["current_entries"],
            hit_rate=stats["cache"]["hit_rate"],
        )

        return {"cleaned_entries": cleaned_entries, "optimization_stats": stats}


# Integration with existing memory systems
class LazyMemoryItem:
    """
    Memory item wrapper that provides lazy embedding loading.

    Integrates with existing OptimizedMemoryItem while providing
    transparent lazy loading for embeddings.
    """

    def __init__(
        self,
        memory_item,  # OptimizedMemoryItem
        lazy_loader: LazyEmbeddingLoader,
        memory_id: str,
    ):
        self.memory_item = memory_item
        self.lazy_loader = lazy_loader
        self.memory_id = memory_id
        self._embedding_cache: Optional[np.ndarray] = None

    def get_content(self) -> str:
        """Get content from underlying memory item"""
        return self.memory_item.get_content()

    def get_tags(self) -> list[str]:
        """Get tags from underlying memory item"""
        return self.memory_item.get_tags()

    def get_metadata(self) -> dict[str, Any]:
        """Get metadata from underlying memory item"""
        return self.memory_item.get_metadata()

    async def get_embedding(self) -> Optional[np.ndarray]:
        """Get embedding with lazy loading"""

        if self._embedding_cache is not None:
            return self._embedding_cache

        # Try to get from memory item first (if not externalized)
        try:
            embedding = self.memory_item.get_embedding()
            if embedding is not None:
                self._embedding_cache = embedding
                return embedding
        except Exception:
            pass  # Fall back to lazy loading

        # Load from lazy loader
        embedding = await self.lazy_loader.get_embedding(self.memory_id)
        if embedding is not None:
            self._embedding_cache = embedding

        return embedding

    @property
    def memory_usage(self) -> int:
        """Get memory usage excluding lazy-loaded embedding"""
        base_usage = self.memory_item.memory_usage

        # Subtract embedding size if it would be loaded
        if hasattr(self.memory_item, "_data"):
            # Estimate embedding size reduction
            base_usage -= 1024 * 4  # Typical 1024-dim float32 embedding

        return base_usage

    @property
    def memory_usage_kb(self) -> float:
        """Get memory usage in KB"""
        return self.memory_usage / 1024


# Factory functions for easy integration
def create_lazy_embedding_system(
    storage_path: Union[str, Path],
    cache_size: int = 10000,
    cache_memory_mb: int = 512,
    **kwargs,
) -> LazyEmbeddingLoader:
    """
    Create a lazy embedding loading system.

    Args:
        storage_path: Path for persistent embedding storage
        cache_size: Maximum number of embeddings to cache
        cache_memory_mb: Maximum memory to use for caching
        **kwargs: Additional arguments for LazyEmbeddingLoader

    Returns:
        Configured LazyEmbeddingLoader instance
    """
    return LazyEmbeddingLoader(
        storage_path=storage_path,
        cache_size=cache_size,
        cache_memory_mb=cache_memory_mb,
        **kwargs,
    )


# Example usage and testing
async def example_usage():
    """Example of lazy embedding loading system"""

    print("🚀 Lazy Embedding Loading System Demo")
    print("=" * 50)

    # Create lazy loading system
    lazy_loader = create_lazy_embedding_system(
        storage_path="./lazy_embeddings_cache", cache_size=1000, cache_memory_mb=128
    )

    # Store some test embeddings
    test_embeddings = {f"memory_{i}": np.random.randn(1024).astype(np.float32) for i in range(10)}

    print(f"Storing {len(test_embeddings)} test embeddings...")
    for memory_id, embedding in test_embeddings.items():
        await lazy_loader.store_embedding(memory_id, embedding)

    # Test individual loading
    print("Testing individual embedding loading...")
    embedding = await lazy_loader.get_embedding("memory_5")
    print(f"Loaded embedding shape: {embedding.shape}")

    # Test batch loading
    print("Testing batch embedding loading...")
    batch_ids = ["memory_1", "memory_3", "memory_7", "memory_9"]
    batch_embeddings = await lazy_loader.get_embeddings_batch(batch_ids)
    print(f"Loaded {len(batch_embeddings)} embeddings in batch")

    # Show performance stats
    stats = lazy_loader.get_performance_stats()
    print(f"Cache hit rate: {stats['cache']['hit_rate']:.2f}")
    print(f"Cached embeddings: {stats['cache']['current_entries']}")

    print("✅ Lazy embedding loading demo completed!")


if __name__ == "__main__":
    asyncio.run(example_usage())
