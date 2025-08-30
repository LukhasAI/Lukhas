#!/usr/bin/env python3
"""
LUKHAS  Performance Optimizations
Production-ready optimizations for improved system performance
"""

import asyncio
import contextlib
import functools
import gc
import logging
import threading
import time
import weakref
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Optional, TypeVar, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T")


class LRUCache:
    """High-performance LRU cache with TTL support"""

    def __init__(self, maxsize: int = 256, ttl: Optional[float] = None):
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {} if ttl else None
        self._lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str, default=None):
        """Get item from cache"""
        with self._lock:
            if key not in self.cache:
                self.misses += 1
                return default

            # Check TTL
            if self.ttl and self.timestamps:
                if time.time() - self.timestamps[key] > self.ttl:
                    self._delete(key)
                    self.misses += 1
                    return default

            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            self.hits += 1
            return value

    def set(self, key: str, value: Any):
        """Set item in cache"""
        with self._lock:
            if key in self.cache:
                # Update existing
                self.cache.pop(key)
            elif len(self.cache) >= self.maxsize:
                # Remove LRU item
                oldest_key = next(iter(self.cache))
                self._delete(oldest_key)

            self.cache[key] = value
            if self.timestamps is not None:
                self.timestamps[key] = time.time()

    def _delete(self, key: str):
        """Delete item from cache"""
        self.cache.pop(key, None)
        if self.timestamps:
            self.timestamps.pop(key, None)

    def clear(self):
        """Clear all items from cache"""
        with self._lock:
            self.cache.clear()
            if self.timestamps:
                self.timestamps.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> dict[str, Union[int, float]]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }


class ObjectPool:
    """Object pool for expensive-to-create objects"""

    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 100,
        reset_func: Optional[Callable[[T], None]] = None,
    ):
        self.factory = factory
        self.max_size = max_size
        self.reset_func = reset_func
        self.pool = []
        self._lock = threading.RLock()
        self.created_count = 0
        self.reused_count = 0

    def acquire(self) -> T:
        """Acquire object from pool"""
        with self._lock:
            if self.pool:
                obj = self.pool.pop()
                self.reused_count += 1
                return obj
            else:
                obj = self.factory()
                self.created_count += 1
                return obj

    def release(self, obj: T):
        """Release object back to pool"""
        with self._lock:
            if len(self.pool) < self.max_size:
                if self.reset_func:
                    self.reset_func(obj)
                self.pool.append(obj)
            # If pool is full, let object be garbage collected

    def stats(self) -> dict[str, int]:
        """Get pool statistics"""
        return {
            "pool_size": len(self.pool),
            "max_size": self.max_size,
            "created": self.created_count,
            "reused": self.reused_count,
            "reuse_rate": self.reused_count / max(1, self.created_count + self.reused_count),
        }


class AsyncBatcher:
    """Batch async operations for improved throughput"""

    def __init__(self, batch_size: int = 10, timeout: float = 0.1):
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending = []
        self.futures = []
        self._lock = asyncio.Lock()
        self._processor_task = None

    async def add(self, item: Any) -> Any:
        """Add item to batch and return result when processed"""
        future = asyncio.Future()

        async with self._lock:
            self.pending.append(item)
            self.futures.append(future)

            # Start processor if not running
            if self._processor_task is None or self._processor_task.done():
                self._processor_task = asyncio.create_task(self._process_batches())

        return await future

    async def _process_batches(self):
        """Process batched items"""
        while True:
            await asyncio.sleep(self.timeout)

            async with self._lock:
                if not self.pending:
                    break

                batch = self.pending[: self.batch_size]
                batch_futures = self.futures[: self.batch_size]

                self.pending = self.pending[self.batch_size :]
                self.futures = self.futures[self.batch_size :]

            # Process batch
            try:
                results = await self._process_batch(batch)
                for future, result in zip(batch_futures, results):
                    future.set_result(result)
            except Exception as e:
                for future in batch_futures:
                    future.set_exception(e)

    async def _process_batch(self, batch: list) -> list:
        """Override this method to define batch processing logic"""
        # Default: return batch as-is
        return batch


class MemoryOptimizer:
    """Memory usage optimizer with automatic garbage collection"""

    def __init__(self, gc_threshold: int = 1000, memory_limit_mb: Optional[int] = None):
        self.gc_threshold = gc_threshold
        self.memory_limit_mb = memory_limit_mb
        self.operation_count = 0
        self.weak_refs = weakref.WeakSet()
        self._last_gc = time.time()

    def track_object(self, obj: Any):
        """Track object for memory management"""
        self.weak_refs.add(obj)

    def increment_operations(self):
        """Increment operation count and trigger GC if needed"""
        self.operation_count += 1

        if self.operation_count >= self.gc_threshold:
            self.force_gc()

    def force_gc(self):
        """Force garbage collection"""
        collected = gc.collect()
        self.operation_count = 0
        self._last_gc = time.time()

        logger.debug(f"Garbage collection: {collected} objects collected")

        # Check memory usage if limit set
        if self.memory_limit_mb:
            import psutil

            memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
            if memory_mb > self.memory_limit_mb:
                logger.warning(
                    f"Memory usage {memory_mb:.1f}MB exceeds limit {self.memory_limit_mb}MB"
                )

    def get_stats(self) -> dict[str, Any]:
        """Get memory optimizer statistics"""
        return {
            "tracked_objects": len(self.weak_refs),
            "operations_since_gc": self.operation_count,
            "gc_threshold": self.gc_threshold,
            "time_since_gc": time.time() - self._last_gc,
            "gc_stats": gc.get_stats(),
        }


class ConnectionPool:
    """Generic connection pool for database/HTTP connections"""

    def __init__(self, factory: Callable, max_connections: int = 10, timeout: float = 30.0):
        self.factory = factory
        self.max_connections = max_connections
        self.timeout = timeout
        self.available = []
        self.in_use = set()
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
        self.created_count = 0

    async def acquire(self):
        """Acquire connection from pool"""
        async with self._condition:
            while True:
                # Return available connection
                if self.available:
                    conn = self.available.pop()
                    self.in_use.add(conn)
                    return conn

                # Create new connection if under limit
                if len(self.in_use) < self.max_connections:
                    conn = await self.factory()
                    self.in_use.add(conn)
                    self.created_count += 1
                    return conn

                # Wait for connection to be released
                try:
                    await asyncio.wait_for(self._condition.wait(), timeout=self.timeout)
                except asyncio.TimeoutError:
                    raise RuntimeError("Connection pool timeout")

    async def release(self, conn):
        """Release connection back to pool"""
        async with self._condition:
            if conn in self.in_use:
                self.in_use.remove(conn)
                self.available.append(conn)
                self._condition.notify()

    async def close_all(self):
        """Close all connections"""
        async with self._lock:
            all_connections = list(self.in_use) + self.available
            for conn in all_connections:
                if hasattr(conn, "close"):
                    await conn.close()
            self.in_use.clear()
            self.available.clear()

    def stats(self) -> dict[str, int]:
        """Get connection pool statistics"""
        return {
            "available": len(self.available),
            "in_use": len(self.in_use),
            "total_created": self.created_count,
            "max_connections": self.max_connections,
        }


def cache_with_ttl(maxsize: int = 128, ttl: float = 300):
    """Decorator for function caching with TTL"""

    def decorator(func: Callable) -> Callable:
        cache = LRUCache(maxsize=maxsize, ttl=ttl)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(hash((args, tuple(sorted(kwargs.items())))))

            # Try cache first
            result = cache.get(key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        # Expose cache stats
        wrapper.cache = cache
        return wrapper

    return decorator


def async_cache_with_ttl(maxsize: int = 128, ttl: float = 300):
    """Decorator for async function caching with TTL"""

    def decorator(func: Callable) -> Callable:
        cache = LRUCache(maxsize=maxsize, ttl=ttl)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            key = str(hash((args, tuple(sorted(kwargs.items())))))

            # Try cache first
            result = cache.get(key)
            if result is not None:
                return result

            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(key, result)
            return result

        # Expose cache stats
        wrapper.cache = cache
        return wrapper

    return decorator


def batch_async_operations(batch_size: int = 10, timeout: float = 0.1):
    """Decorator to batch async operations"""

    def decorator(func: Callable) -> Callable:
        batcher = AsyncBatcher(batch_size=batch_size, timeout=timeout)

        # Override batch processor
        async def process_batch(batch):
            # Process each item in batch
            results = []
            for args, kwargs in batch:
                result = await func(*args, **kwargs)
                results.append(result)
            return results

        batcher._process_batch = process_batch

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await batcher.add((args, kwargs))

        return wrapper

    return decorator


class PerformanceMonitor:
    """Monitor and report performance metrics"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self._lock = threading.Lock()

    def time_operation(self, operation_name: str):
        """Context manager to time operations"""
        return self.TimingContext(self, operation_name)

    def increment_counter(self, counter_name: str, value: int = 1):
        """Increment a counter"""
        with self._lock:
            self.counters[counter_name] += value

    def record_metric(self, metric_name: str, value: float):
        """Record a metric value"""
        with self._lock:
            self.metrics[metric_name].append({"value": value, "timestamp": time.time()})

            # Keep only recent metrics (last 1000)
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name] = self.metrics[metric_name][-1000:]

    def get_stats(self) -> dict[str, Any]:
        """Get performance statistics"""
        with self._lock:
            stats = {"counters": dict(self.counters), "metrics": {}}

            for metric_name, values in self.metrics.items():
                if values:
                    recent_values = [v["value"] for v in values[-100:]]  # Last 100 values
                    stats["metrics"][metric_name] = {
                        "count": len(values),
                        "average": sum(recent_values) / len(recent_values),
                        "min": min(recent_values),
                        "max": max(recent_values),
                        "recent": recent_values[-10:],  # Last 10 values
                    }

            return stats

    class TimingContext:
        def __init__(self, monitor, operation_name: str):
            self.monitor = monitor
            self.operation_name = operation_name
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            self.monitor.record_metric(f"{self.operation_name}_duration", duration)
            if exc_type is None:
                self.monitor.increment_counter(f"{self.operation_name}_success")
            else:
                self.monitor.increment_counter(f"{self.operation_name}_error")


# Global instances
global_cache = LRUCache(maxsize=1000, ttl=300)
global_monitor = PerformanceMonitor()
global_memory_optimizer = MemoryOptimizer(gc_threshold=1000)

# Thread pool for CPU-intensive tasks
cpu_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="lukhas-cpu")
io_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="lukhas-io")


async def run_in_cpu_executor(func: Callable, *args, **kwargs):
    """Run CPU-intensive function in thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(cpu_executor, functools.partial(func, **kwargs), *args)


async def run_in_io_executor(func: Callable, *args, **kwargs):
    """Run I/O function in thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(io_executor, functools.partial(func, **kwargs), *args)


def optimize_imports():
    """Optimize module imports for faster startup"""
    import importlib.util
    import sys

    # Cache frequently used modules
    common_modules = [
        "json",
        "time",
        "asyncio",
        "logging",
        "pathlib",
        "typing",
        "dataclasses",
    ]

    for module_name in common_modules:
        if module_name not in sys.modules:
            with contextlib.suppress(ImportError):
                importlib.import_module(module_name)


def setup_optimizations():
    """Setup all performance optimizations"""
    logger.info("🚀 Setting up LUKHAS  performance optimizations...")

    # Optimize imports
    optimize_imports()

    # Configure garbage collection
    import gc

    gc.set_threshold(1000, 15, 10)  # More aggressive GC

    # Enable cyclic GC debugging in development
    if __debug__:
        gc.set_debug(gc.DEBUG_STATS)

    logger.info("✅ Performance optimizations active")


def get_optimization_stats() -> dict[str, Any]:
    """Get statistics from all optimization components"""
    return {
        "global_cache": global_cache.stats(),
        "performance_monitor": global_monitor.get_stats(),
        "memory_optimizer": global_memory_optimizer.get_stats(),
        "thread_pools": {
            "cpu_executor": {
                "max_workers": cpu_executor._max_workers,
                "threads": (len(cpu_executor._threads) if hasattr(cpu_executor, "_threads") else 0),
            },
            "io_executor": {
                "max_workers": io_executor._max_workers,
                "threads": (len(io_executor._threads) if hasattr(io_executor, "_threads") else 0),
            },
        },
    }


# Example usage
if __name__ == "__main__":
    # Setup optimizations
    setup_optimizations()

    # Example cached function
    @cache_with_ttl(maxsize=100, ttl=60)
    def expensive_calculation(n: int) -> int:
        """Example expensive calculation"""
        time.sleep(0.01)  # Simulate work
        return sum(i**2 for i in range(n))

    # Test the cache
    print("Testing cache performance...")

    # First call (cache miss)
    start = time.time()
    result1 = expensive_calculation(100)
    first_call_time = time.time() - start

    # Second call (cache hit)
    start = time.time()
    result2 = expensive_calculation(100)
    second_call_time = time.time() - start

    print(f"First call: {first_call_time:.3f}s")
    print(f"Second call: {second_call_time:.3f}s")
    print(f"Speedup: {first_call_time / second_call_time:.1f}x")
    print(f"Cache stats: {expensive_calculation.cache.stats()}")

    # Print optimization stats
    import json

    print("\nOptimization Statistics:")
    print(json.dumps(get_optimization_stats(), indent=2))
