from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - PRACTICAL OPTIMIZATION STRATEGIES
║ Implementation of resource-efficient patterns for Symbiotic Swarm
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: practical_optimizations.py
║ Path: lukhas/core/practical_optimizations.py
║ Version: 1.0.0 | Created: 2025-07-27
║ Authors: LUKHAS AI Core Team
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ intelligent, collaborative AI systems while reducing energy and memory consumption.
║ Implements key patterns for efficiency in the Symbiotic Swarm architecture.
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import gc
import json
import logging
import pickle
import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

import numpy as np
from core.common import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

T = TypeVar("T")


class OptimizationStrategy(ABC):
    """Base class for optimization strategies"""

    @abstractmethod
    def apply(self, *args, **kwargs) -> Any:
        """Apply the optimization strategy"""

    @abstractmethod
    def get_metrics(self) -> dict[str, Any]:
        """Get metrics about strategy effectiveness"""


@dataclass
class CacheEntry:
    """Entry in adaptive cache with metadata"""

    key: str
    value: Any
    size: int
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    creation_time: float = field(default_factory=time.time)
    ttl: Optional[float] = None

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.creation_time > self.ttl

    def access(self):
        """Update access metadata"""
        self.access_count += 1
        self.last_access = time.time()

    @property
    def score(self) -> float:
        """Calculate cache priority score"""
        age = time.time() - self.creation_time
        recency = time.time() - self.last_access

        # LFU with decay - balance frequency and recency
        frequency_score = self.access_count / max(age, 1)
        recency_score = 1 / (recency + 1)

        return frequency_score * 0.7 + recency_score * 0.3


class AdaptiveCache(OptimizationStrategy):
    """
    Adaptive caching with intelligent eviction and prefetching
    Reduces repeated computations and I/O operations
    """

    def __init__(
        self,
        max_size_mb: int = 100,
        ttl_seconds: float = 3600,
        prefetch_threshold: float = 0.8,
    ):
        """
        Initialize adaptive cache

        Args:
            max_size_mb: Maximum cache size in megabytes
            ttl_seconds: Default time-to-live for entries
            prefetch_threshold: Access frequency threshold for prefetching
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = ttl_seconds
        self.prefetch_threshold = prefetch_threshold

        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_size = 0
        self.lock = threading.RLock()

        # Metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.prefetch_success = 0

        # Prefetch predictions
        self.access_patterns: dict[str, list[str]] = defaultdict(list)

        logger.info(f"Adaptive cache initialized: {max_size_mb}MB, TTL={ttl_seconds}s")

    def get(self, key: str, compute_fn: Optional[Callable] = None) -> Optional[Any]:
        """
        Get value from cache or compute if missing

        Args:
            key: Cache key
            compute_fn: Function to compute value if not cached

        Returns:
            Cached or computed value
        """
        with self.lock:
            entry = self.cache.get(key)

            if entry and not entry.is_expired():
                # Cache hit
                entry.access()
                self.hits += 1

                # Move to end (LRU behavior)
                self.cache.move_to_end(key)

                # Trigger prefetch if high access frequency
                if entry.score > self.prefetch_threshold:
                    self._prefetch_related(key)

                return entry.value

            # Cache miss
            self.misses += 1

            if compute_fn:
                value = compute_fn()
                self.put(key, value)
                return value

            return None

    def put(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        size_hint: Optional[int] = None,
    ):
        """
        Put value in cache with adaptive eviction

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            size_hint: Size hint in bytes (estimated if not provided)
        """
        # Estimate size if not provided
        if size_hint is None:
            size_hint = self._estimate_size(value)

        with self.lock:
            # Remove old entry if exists
            if key in self.cache:
                old_entry = self.cache.pop(key)
                self.current_size -= old_entry.size

            # Evict if necessary
            while self.current_size + size_hint > self.max_size_bytes and self.cache:
                self._evict_one()

            # Add new entry
            entry = CacheEntry(
                key=key,
                value=value,
                size=size_hint,
                ttl=ttl or self.default_ttl,
            )

            self.cache[key] = entry
            self.current_size += size_hint

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        try:
            # Use pickle for size estimation
            return len(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))
        except BaseException:
            # Fallback estimation
            return 1024  # 1KB default

    def _evict_one(self):
        """Evict one entry using adaptive scoring"""
        if not self.cache:
            return

        # Find entry with lowest score
        min_score = float("inf")
        evict_key = None

        for key, entry in self.cache.items():
            if entry.score < min_score:
                min_score = entry.score
                evict_key = key

        if evict_key:
            entry = self.cache.pop(evict_key)
            self.current_size -= entry.size
            self.evictions += 1

    def _prefetch_related(self, key: str):
        """Prefetch related entries based on access patterns"""
        # Simple pattern: prefetch next in sequence
        # In production, use more sophisticated ML-based prediction

        related_keys = self.access_patterns.get(key, [])
        for related_key in related_keys[:3]:  # Prefetch up to 3 related
            if related_key not in self.cache:
                # Trigger async prefetch (simplified)
                self.prefetch_success += 1

    def clear_expired(self):
        """Clear all expired entries"""
        with self.lock:
            expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]

            for key in expired_keys:
                entry = self.cache.pop(key)
                self.current_size -= entry.size

    def apply(self, key: str, compute_fn: Callable) -> Any:
        """Apply caching strategy"""
        return self.get(key, compute_fn)

    def get_metrics(self) -> dict[str, Any]:
        """Get cache metrics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0

            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "evictions": self.evictions,
                "current_size_mb": self.current_size / 1024 / 1024,
                "entries": len(self.cache),
                "prefetch_success": self.prefetch_success,
            }


class ObjectPool(OptimizationStrategy):
    """
    Object pooling to reduce allocation/deallocation overhead
    Especially useful for frequently created/destroyed objects
    """

    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 100,
        reset_fn: Optional[Callable[[T], None]] = None,
    ):
        """
        Initialize object pool

        Args:
            factory: Function to create new objects
            max_size: Maximum pool size
            reset_fn: Function to reset object state before reuse
        """
        self.factory = factory
        self.max_size = max_size
        self.reset_fn = reset_fn

        self.pool: list[T] = []
        self.in_use: set[int] = set()
        self.lock = threading.Lock()

        # Metrics
        self.allocations = 0
        self.reuses = 0
        self.pool_hits = 0
        self.pool_misses = 0

        # Pre-populate pool
        self._prepopulate(min(10, max_size))

    def _prepopulate(self, count: int):
        """Pre-populate pool with objects"""
        for _ in range(count):
            obj = self.factory()
            self.pool.append(obj)
            self.allocations += 1

    def acquire(self) -> T:
        """Acquire object from pool"""
        with self.lock:
            if self.pool:
                # Reuse from pool
                obj = self.pool.pop()
                self.in_use.add(id(obj))
                self.pool_hits += 1
                self.reuses += 1

                # Reset object state
                if self.reset_fn:
                    self.reset_fn(obj)

                return obj
            else:
                # Create new object
                obj = self.factory()
                self.in_use.add(id(obj))
                self.allocations += 1
                self.pool_misses += 1
                return obj

    def release(self, obj: T):
        """Release object back to pool"""
        with self.lock:
            obj_id = id(obj)

            if obj_id in self.in_use:
                self.in_use.remove(obj_id)

                # Return to pool if not full
                if len(self.pool) < self.max_size:
                    self.pool.append(obj)
                # Otherwise let it be garbage collected

    @contextmanager
    def borrowed(self):
        """Context manager for borrowing objects"""
        obj = self.acquire()
        try:
            yield obj
        finally:
            self.release(obj)

    def apply(self, *args, **kwargs) -> Any:
        """Apply pooling strategy"""
        return self.acquire()

    def get_metrics(self) -> dict[str, Any]:
        """Get pool metrics"""
        with self.lock:
            reuse_rate = self.reuses / self.allocations if self.allocations > 0 else 0

            return {
                "allocations": self.allocations,
                "reuses": self.reuses,
                "reuse_rate": reuse_rate,
                "pool_size": len(self.pool),
                "in_use": len(self.in_use),
                "pool_hits": self.pool_hits,
                "pool_misses": self.pool_misses,
            }


class LazyComputation(OptimizationStrategy):
    """
    Lazy computation pattern - defer expensive operations until needed
    Reduces unnecessary calculations
    """

    def __init__(self):
        """Initialize lazy computation tracker"""
        self.deferred_computations = 0
        self.executed_computations = 0
        self.saved_computations = 0

    @staticmethod
    def lazy_property(func):
        """Decorator for lazy property evaluation"""
        attr_name = f"_lazy_{func.__name__}"

        @wraps(func)
        def wrapper(self):
            if not hasattr(self, attr_name):
                setattr(self, attr_name, func(self))
            return getattr(self, attr_name)

        return property(wrapper)

    def defer(self, compute_fn: Callable[[], T]) -> "DeferredComputation[T]":
        """Create deferred computation"""
        self.deferred_computations += 1
        return DeferredComputation(compute_fn, self)

    def apply(self, compute_fn: Callable) -> "DeferredComputation":
        """Apply lazy computation strategy"""
        return self.defer(compute_fn)

    def get_metrics(self) -> dict[str, Any]:
        """Get lazy computation metrics"""
        return {
            "deferred": self.deferred_computations,
            "executed": self.executed_computations,
            "saved": self.saved_computations,
            "savings_rate": (
                self.saved_computations / self.deferred_computations if self.deferred_computations > 0 else 0
            ),
        }


class DeferredComputation:
    """Represents a deferred computation"""

    def __init__(self, compute_fn: Callable[[], T], tracker: LazyComputation):
        self.compute_fn = compute_fn
        self.tracker = tracker
        self._result = None
        self._computed = False

    def get(self) -> T:
        """Get result, computing if necessary"""
        if not self._computed:
            self._result = self.compute_fn()
            self._computed = True
            self.tracker.executed_computations += 1
        return self._result

    def is_computed(self) -> bool:
        """Check if computation has been performed"""
        return self._computed

    def __del__(self):
        """Track saved computations on cleanup"""
        if not self._computed:
            self.tracker.saved_computations += 1


class BatchProcessor(OptimizationStrategy):
    """
    Batch processing to reduce overhead and improve throughput
    Accumulates items and processes in batches
    """

    def __init__(
        self,
        process_fn: Callable[[list[Any]], list[Any]],
        batch_size: int = 100,
        timeout_seconds: float = 1.0,
    ):
        """
        Initialize batch processor

        Args:
            process_fn: Function to process a batch of items
            batch_size: Maximum batch size
            timeout_seconds: Maximum time to wait before processing
        """
        self.process_fn = process_fn
        self.batch_size = batch_size
        self.timeout = timeout_seconds

        self.pending_items: list[tuple[Any, asyncio.Future]] = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

        # Metrics
        self.total_items = 0
        self.total_batches = 0
        self.average_batch_size = 0

        # Start processing thread
        self._running = True
        self._processor_thread = threading.Thread(target=self._process_loop, daemon=True)
        self._processor_thread.start()

    def add(self, item: Any) -> asyncio.Future:
        """Add item for batch processing"""
        future = asyncio.Future()

        with self.condition:
            self.pending_items.append((item, future))
            self.total_items += 1

            # Process immediately if batch is full
            if len(self.pending_items) >= self.batch_size:
                self.condition.notify()

        return future

    def _process_loop(self):
        """Background processing loop"""
        while self._running:
            with self.condition:
                # Wait for items or timeout
                self.condition.wait(timeout=self.timeout)

                if not self.pending_items:
                    continue

                # Check if we should process
                should_process = (
                    len(self.pending_items) >= self.batch_size or time.time() - self._last_process_time > self.timeout
                )

                if should_process:
                    # Extract batch
                    batch_items = self.pending_items[: self.batch_size]
                    self.pending_items = self.pending_items[self.batch_size :]

                    # Process batch
                    items = [item for item, _ in batch_items]
                    futures = [future for _, future in batch_items]

                    try:
                        results = self.process_fn(items)

                        # Set results
                        for future, result in zip(futures, results):
                            future.set_result(result)

                        # Update metrics
                        self.total_batches += 1
                        self.average_batch_size = (
                            self.average_batch_size * (self.total_batches - 1) + len(items)
                        ) / self.total_batches
                    except Exception as e:
                        # Set exception on all futures
                        for future in futures:
                            future.set_exception(e)

    def flush(self):
        """Force process all pending items"""
        with self.condition:
            self.condition.notify()

    def apply(self, items: list[Any]) -> list[Any]:
        """Apply batch processing strategy"""
        futures = [self.add(item) for item in items]
        return [future.result() for future in futures]

    def get_metrics(self) -> dict[str, Any]:
        """Get batch processing metrics"""
        return {
            "total_items": self.total_items,
            "total_batches": self.total_batches,
            "average_batch_size": self.average_batch_size,
            "efficiency": (self.average_batch_size / self.batch_size if self.batch_size > 0 else 0),
            "pending_items": len(self.pending_items),
        }

    def shutdown(self):
        """Shutdown batch processor"""
        self._running = False
        self.flush()
        self._processor_thread.join(timeout=5)


class MemoryMappedStorage(OptimizationStrategy):
    """
    Memory-mapped file storage for efficient large data access
    Reduces memory usage for large datasets
    """

    def __init__(self, base_path: str = "/tmp/mmap_storage"):
        """Initialize memory-mapped storage"""
        self.base_path = base_path
        self.open_mmaps: dict[str, np.memmap] = {}
        self.lock = threading.Lock()

        # Metrics
        self.total_reads = 0
        self.total_writes = 0
        self.memory_saved_mb = 0

        # Create base directory
        import os

        os.makedirs(base_path, exist_ok=True)

    def store_array(
        self,
        key: str,
        array: np.ndarray,
        dtype: Optional[np.dtype] = None,
    ) -> str:
        """Store numpy array as memory-mapped file"""
        filepath = f"{self.base_path}/{key}.mmap"

        if dtype is None:
            dtype = array.dtype

        # Create memory-mapped file
        mmap = np.memmap(
            filepath,
            dtype=dtype,
            mode="w+",
            shape=array.shape,
        )

        # Copy data
        mmap[:] = array[:]
        mmap.flush()

        # Track memory saved
        self.memory_saved_mb += array.nbytes / 1024 / 1024
        self.total_writes += 1

        # Keep reference for efficient access
        with self.lock:
            self.open_mmaps[key] = mmap

        return filepath

    def get_array(
        self,
        key: str,
        mode: str = "r",
    ) -> Optional[np.memmap]:
        """Get memory-mapped array"""
        with self.lock:
            # Check cache
            if key in self.open_mmaps:
                self.total_reads += 1
                return self.open_mmaps[key]

        # Load from disk
        filepath = f"{self.base_path}/{key}.mmap"
        import os

        if os.path.exists(filepath):
            # Load metadata (would be stored separately in production)
            # For demo, assume we know the shape and dtype
            mmap = np.memmap(filepath, mode=mode)

            with self.lock:
                self.open_mmaps[key] = mmap

            self.total_reads += 1
            return mmap

        return None

    def apply(self, key: str, array: Optional[np.ndarray] = None) -> Any:
        """Apply memory-mapped storage strategy"""
        if array is not None:
            return self.store_array(key, array)
        else:
            return self.get_array(key)

    def get_metrics(self) -> dict[str, Any]:
        """Get storage metrics"""
        return {
            "total_reads": self.total_reads,
            "total_writes": self.total_writes,
            "memory_saved_mb": self.memory_saved_mb,
            "open_files": len(self.open_mmaps),
        }

    def cleanup(self):
        """Clean up open memory maps"""
        with self.lock:
            for mmap in self.open_mmaps.values():
                del mmap
            self.open_mmaps.clear()


class ComputationReuse(OptimizationStrategy):
    """
    Computation reuse through memoization and result sharing
    Eliminates redundant calculations across the swarm
    """

    def __init__(self, max_cache_size: int = 1000):
        """Initialize computation reuse system"""
        self.max_cache_size = max_cache_size
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.computation_graph: dict[str, set[str]] = defaultdict(set)
        self.lock = threading.RLock()

        # Metrics
        self.computations_saved = 0
        self.total_computations = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def memoize(self, key_prefix: str = ""):
        """Decorator for memoizing function results"""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                key_parts = [key_prefix, func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)

                with self.lock:
                    # Check cache
                    if cache_key in self.cache:
                        self.cache_hits += 1
                        self.computations_saved += 1
                        # Move to end (LRU)
                        self.cache.move_to_end(cache_key)
                        return self.cache[cache_key]

                    # Compute result
                    self.cache_misses += 1
                    self.total_computations += 1
                    result = func(*args, **kwargs)

                    # Store in cache
                    self.cache[cache_key] = result

                    # Evict if necessary
                    if len(self.cache) > self.max_cache_size:
                        self.cache.popitem(last=False)

                    return result

            return wrapper

        return decorator

    def share_computation(
        self,
        computation_id: str,
        dependencies: list[str],
        compute_fn: Callable,
    ) -> Any:
        """Share computation results across nodes"""
        # Track computation dependencies
        for dep in dependencies:
            self.computation_graph[dep].add(computation_id)

        # Check if already computed
        with self.lock:
            if computation_id in self.cache:
                self.cache_hits += 1
                self.computations_saved += 1
                return self.cache[computation_id]

        # Compute and cache
        result = compute_fn()

        with self.lock:
            self.cache[computation_id] = result
            self.total_computations += 1

        return result

    def invalidate_dependents(self, computation_id: str):
        """Invalidate computations that depend on given ID"""
        with self.lock:
            # Find all dependents
            to_invalidate = set()
            queue = [computation_id]

            while queue:
                current = queue.pop()
                dependents = self.computation_graph.get(current, set())

                for dep in dependents:
                    if dep not in to_invalidate:
                        to_invalidate.add(dep)
                        queue.append(dep)

            # Remove from cache
            for comp_id in to_invalidate:
                self.cache.pop(comp_id, None)

    def apply(self, computation_id: str, compute_fn: Callable) -> Any:
        """Apply computation reuse strategy"""
        return self.share_computation(computation_id, [], compute_fn)

    def get_metrics(self) -> dict[str, Any]:
        """Get computation reuse metrics"""
        with self.lock:
            hit_rate = (
                self.cache_hits / (self.cache_hits + self.cache_misses)
                if (self.cache_hits + self.cache_misses) > 0
                else 0
            )

            return {
                "computations_saved": self.computations_saved,
                "total_computations": self.total_computations,
                "savings_rate": (
                    self.computations_saved / self.total_computations if self.total_computations > 0 else 0
                ),
                "cache_size": len(self.cache),
                "hit_rate": hit_rate,
                "dependency_graph_size": len(self.computation_graph),
            }


class ResourceManager:
    """
    Central resource manager implementing all optimization strategies
    Coordinates optimizations across the Symbiotic Swarm
    """

    def __init__(self):
        """Initialize resource manager with all strategies"""
        self.strategies = {
            "cache": AdaptiveCache(max_size_mb=100),
            "object_pool": ObjectPool(factory=lambda: {}, max_size=1000),
            "lazy": LazyComputation(),
            "batch": BatchProcessor(
                process_fn=lambda items: [item * 2 for item in items],
                batch_size=50,
            ),
            "mmap": MemoryMappedStorage(),
            "reuse": ComputationReuse(max_cache_size=500),
        }

        # Global optimization settings
        self.optimization_level = "balanced"  # "aggressive", "balanced", "conservative"
        self.resource_limits = {
            "memory_mb": 1024,
            "cpu_percent": 80,
            "io_ops_per_sec": 1000,
        }

        # Monitoring
        self._monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self._monitor_thread.start()

        logger.info("Resource manager initialized with all optimization strategies")

    def _monitor_resources(self):
        """Monitor and adjust optimization strategies"""
        while True:
            time.sleep(10)  # Check every 10 seconds

            # Get current resource usage
            try:
                import psutil

                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()

                # Adjust strategies based on usage
                if memory_mb > self.resource_limits["memory_mb"] * 0.9:
                    # High memory pressure - be more aggressive
                    self._adjust_for_memory_pressure()

                if cpu_percent > self.resource_limits["cpu_percent"]:
                    # High CPU - optimize for CPU
                    self._adjust_for_cpu_pressure()

            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")

    def _adjust_for_memory_pressure(self):
        """Adjust strategies for memory pressure"""
        logger.info("Adjusting for memory pressure")

        # Reduce cache sizes
        cache = self.strategies["cache"]
        cache.max_size_bytes = int(cache.max_size_bytes * 0.8)

        # Trigger garbage collection
        gc.collect()

    def _adjust_for_cpu_pressure(self):
        """Adjust strategies for CPU pressure"""
        logger.info("Adjusting for CPU pressure")

        # Increase batch sizes to reduce overhead
        batch = self.strategies["batch"]
        batch.batch_size = min(200, int(batch.batch_size * 1.5))

    def get_strategy(self, name: str) -> OptimizationStrategy:
        """Get specific optimization strategy"""
        return self.strategies.get(name)

    def get_all_metrics(self) -> dict[str, dict[str, Any]]:
        """Get metrics from all strategies"""
        return {name: strategy.get_metrics() for name, strategy in self.strategies.items()}

    def optimize_computation(
        self,
        computation_id: str,
        compute_fn: Callable,
        optimization_hints: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Optimize a computation using appropriate strategies

        Args:
            computation_id: Unique computation identifier
            compute_fn: Function to compute result
            optimization_hints: Hints about computation characteristics

        Returns:
            Computation result
        """
        hints = optimization_hints or {}

        # Check cache first
        cache_key = f"computation:{computation_id}"
        cached = self.strategies["cache"].get(cache_key)
        if cached is not None:
            return cached

        # Check if computation can be reused
        if hints.get("deterministic", True):
            result = self.strategies["reuse"].share_computation(
                computation_id, hints.get("dependencies", []), compute_fn
            )
        else:
            # Non-deterministic, compute directly
            result = compute_fn()

        # Cache result
        self.strategies["cache"].put(
            cache_key,
            result,
            ttl=hints.get("cache_ttl", 3600),
        )

        return result

    def optimize_memory_access(
        self,
        data_id: str,
        data: Optional[np.ndarray] = None,
        access_pattern: str = "sequential",
    ) -> Union[np.ndarray, np.memmap]:
        """
        Optimize memory access for large data

        Args:
            data_id: Data identifier
            data: Data to store (if writing)
            access_pattern: "sequential", "random", "streaming"

        Returns:
            Optimized data accessor
        """
        if data is not None and data.nbytes > 10 * 1024 * 1024:  # > 10MB
            # Use memory-mapped storage for large data
            return self.strategies["mmap"].store_array(data_id, data)
        elif data is not None:
            # Use regular cache for small data
            self.strategies["cache"].put(data_id, data)
            return data
        else:
            # Try cache first, then mmap
            cached = self.strategies["cache"].get(data_id)
            if cached is not None:
                return cached

            return self.strategies["mmap"].get_array(data_id)

    def create_resource_report(self) -> str:
        """Create comprehensive resource optimization report"""
        metrics = self.get_all_metrics()

        report = "RESOURCE OPTIMIZATION REPORT\n"
        report += "=" * 50 + "\n\n"

        # Cache efficiency
        cache_metrics = metrics.get("cache", {})
        report += "CACHE EFFICIENCY:\n"
        report += f"  Hit Rate: {cache_metrics.get('hit_rate', 0):.2%}\n"
        report += f"  Size: {cache_metrics.get('current_size_mb', 0):.1f} MB\n"
        report += f"  Entries: {cache_metrics.get('entries', 0)}\n\n"

        # Object pooling
        pool_metrics = metrics.get("object_pool", {})
        report += "OBJECT POOLING:\n"
        report += f"  Reuse Rate: {pool_metrics.get('reuse_rate', 0):.2%}\n"
        report += f"  Pool Size: {pool_metrics.get('pool_size', 0)}\n\n"

        # Computation reuse
        reuse_metrics = metrics.get("reuse", {})
        report += "COMPUTATION REUSE:\n"
        report += f"  Savings Rate: {reuse_metrics.get('savings_rate', 0):.2%}\n"
        report += f"  Computations Saved: {reuse_metrics.get('computations_saved', 0)}\n\n"

        # Memory efficiency
        mmap_metrics = metrics.get("mmap", {})
        report += "MEMORY OPTIMIZATION:\n"
        report += f"  Memory Saved: {mmap_metrics.get('memory_saved_mb', 0):.1f} MB\n"

        return report


# Practical optimization utilities
def optimize_swarm_communication(payload: dict[str, Any]) -> bytes:
    """
    Optimize inter-node communication in the swarm
    Uses compression and efficient serialization
    """
    import zlib

    import msgpack

    # Use msgpack for efficient serialization
    packed = msgpack.packb(payload, use_bin_type=True)

    # Compress if beneficial
    if len(packed) > 1024:  # Only compress if > 1KB
        compressed = zlib.compress(packed, level=6)
        if len(compressed) < len(packed) * 0.9:  # 10% savings threshold
            return b"Z" + compressed  # Prefix to indicate compression

    return b"U" + packed  # Uncompressed


def deserialize_swarm_message(data: bytes) -> dict[str, Any]:
    """Deserialize optimized swarm message"""
    import zlib

    import msgpack

    if data[0] == ord("Z"):
        # Compressed
        packed = zlib.decompress(data[1:])
    else:
        # Uncompressed
        packed = data[1:]

    return msgpack.unpackb(packed, raw=False)


# Demo usage
if __name__ == "__main__":
    # Initialize resource manager
    manager = ResourceManager()

    print("Demonstrating practical optimizations...\n")

    # 1. Adaptive caching
    print("1. ADAPTIVE CACHING")
    cache = manager.get_strategy("cache")

    def expensive_computation(x):
        time.sleep(0.1)  # Simulate expensive operation
        return x**2

    # First call - cache miss
    start = time.time()
    result1 = cache.get("compute_100", lambda: expensive_computation(100))
    print(f"   First call (miss): {time.time() - start:.3f}s, result={result1}")

    # Second call - cache hit
    start = time.time()
    result2 = cache.get("compute_100", lambda: expensive_computation(100))
    print(f"   Second call (hit): {time.time() - start:.3f}s, result={result2}")
    print(f"   Cache metrics: {cache.get_metrics()}\n")

    # 2. Object pooling
    print("2. OBJECT POOLING")

    class ExpensiveObject:
        def __init__(self):
            self.data = [0] * 10000  # Simulate expensive initialization
            time.sleep(0.01)

        def reset(self):
            self.data = [0] * 10000

    pool = ObjectPool(
        factory=ExpensiveObject,
        max_size=10,
        reset_fn=lambda obj: obj.reset(),
    )

    # Use objects from pool
    objects = []
    start = time.time()
    for _i in range(5):
        obj = pool.acquire()
        objects.append(obj)
    print(f"   Acquired 5 objects: {time.time() - start:.3f}s")

    # Release back to pool
    for obj in objects:
        pool.release(obj)

    # Reacquire - should be faster
    start = time.time()
    for _i in range(5):
        obj = pool.acquire()
    print(f"   Reacquired 5 objects: {time.time() - start:.3f}s")
    print(f"   Pool metrics: {pool.get_metrics()}\n")

    # 3. Computation reuse
    print("3. COMPUTATION REUSE")
    reuse = manager.get_strategy("reuse")

    @reuse.memoize("fibonacci")
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    # Calculate fibonacci numbers
    start = time.time()
    fib30 = fibonacci(30)
    print(f"   Fibonacci(30) first: {time.time() - start:.3f}s, result={fib30}")

    start = time.time()
    fib30_cached = fibonacci(30)
    print(f"   Fibonacci(30) cached: {time.time() - start:.3f}s, result={fib30_cached}")
    print(f"   Reuse metrics: {reuse.get_metrics()}\n")

    # 4. Resource optimization report
    print("\n" + manager.create_resource_report())

    # 5. Swarm communication optimization
    print("\nSWARM COMMUNICATION OPTIMIZATION")
    test_payload = {
        "node_id": "node-001",
        "timestamp": time.time(),
        "data": list(range(1000)),
        "metadata": {"type": "sensor_reading", "location": "zone_a"},
    }

    import json

    json_size = len(json.dumps(test_payload).encode())
    optimized = optimize_swarm_communication(test_payload)
    optimized_size = len(optimized)

    print(f"   Original size (JSON): {json_size} bytes")
    print(f"   Optimized size: {optimized_size} bytes")
    print(f"   Compression ratio: {json_size / optimized_size:.2f}x")

    # Verify deserialization
    restored = deserialize_swarm_message(optimized)
    print(f"   Deserialization successful: {restored['node_id'] == test_payload['node_id']}")