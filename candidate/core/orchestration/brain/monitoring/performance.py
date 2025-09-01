"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ lukhas CLI Performance Module                                             ║
║ DESCRIPTION: Performance monitoring, optimization, and profiling     ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import functools
import gc
import logging
import os
import sys
import threading
import time
import tracemalloc
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import psutil


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""

    cpu_percent: float = 0.0
    memory_usage: int = 0  # bytes
    memory_percent: float = 0.0
    disk_io_read: int = 0  # bytes
    disk_io_write: int = 0  # bytes
    network_sent: int = 0  # bytes
    network_recv: int = 0  # bytes
    thread_count: int = 0
    open_files: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cpu_percent": self.cpu_percent,
            "memory_usage": self.memory_usage,
            "memory_percent": self.memory_percent,
            "disk_io_read": self.disk_io_read,
            "disk_io_write": self.disk_io_write,
            "network_sent": self.network_sent,
            "network_recv": self.network_recv,
            "thread_count": self.thread_count,
            "open_files": self.open_files,
            "timestamp": self.timestamp,
        }


@dataclass
class FunctionProfile:
    """Function profiling data."""

    name: str
    call_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    last_called: Optional[float] = None

    def add_call(self, execution_time: float):
        """Add a function call to the profile."""
        self.call_count += 1
        self.total_time += execution_time
        self.avg_time = self.total_time / self.call_count
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.last_called = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "call_count": self.call_count,
            "total_time": self.total_time,
            "avg_time": self.avg_time,
            "min_time": (self.min_time if self.min_time != float("inf") else 0.0),
            "max_time": self.max_time,
            "last_called": self.last_called,
        }


class SystemMonitor:
    """System resource monitoring."""

    def __init__(self, interval: float = 1.0, history_size: int = 100):
        self.interval = interval
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.process = psutil.Process()
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None

    def start_monitoring(self):
        """Start continuous monitoring."""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                metrics = self.get_current_metrics()
                self.metrics_history.append(metrics)
                time.sleep(self.interval)
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(self.interval)

    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current system metrics."""
        try:
            # CPU usage
            cpu_percent = self.process.cpu_percent()

            # Memory usage
            memory_info = self.process.memory_info()
            memory_usage = memory_info.rss
            memory_percent = self.process.memory_percent()

            # I/O stats (handle macOS compatibility)
            disk_io_read = disk_io_write = 0
            try:
                if hasattr(self.process, "io_counters"):
                    io_counters = self.process.io_counters()
                    disk_io_read = io_counters.read_bytes
                    disk_io_write = io_counters.write_bytes
            except (AttributeError, psutil.AccessDenied, NotImplementedError):
                # macOS may not support io_counters for all processes
                pass

            # Network stats (if available)
            try:
                net_io = psutil.net_io_counters()
                network_sent = net_io.bytes_sent
                network_recv = net_io.bytes_recv
            except Exception:
                network_sent = network_recv = 0

            # Thread and file counts
            thread_count = self.process.num_threads()
            open_files = len(self.process.open_files())

            return PerformanceMetrics(
                cpu_percent=cpu_percent,
                memory_usage=memory_usage,
                memory_percent=memory_percent,
                disk_io_read=disk_io_read,
                disk_io_write=disk_io_write,
                network_sent=network_sent,
                network_recv=network_recv,
                thread_count=thread_count,
                open_files=open_files,
            )

        except Exception as e:
            logging.error(f"Error getting system metrics: {e}")
            return PerformanceMetrics()

    def get_metrics_history(self) -> list[PerformanceMetrics]:
        """Get historical metrics."""
        return list(self.metrics_history)

    def get_average_metrics(self, last_n: Optional[int] = None) -> PerformanceMetrics:
        """Get average metrics over specified period."""
        if not self.metrics_history:
            return PerformanceMetrics()

        history = list(self.metrics_history)
        if last_n:
            history = history[-last_n:]

        if not history:
            return PerformanceMetrics()

        avg_metrics = PerformanceMetrics()
        count = len(history)

        for metrics in history:
            avg_metrics.cpu_percent += metrics.cpu_percent
            avg_metrics.memory_usage += metrics.memory_usage
            avg_metrics.memory_percent += metrics.memory_percent
            avg_metrics.disk_io_read += metrics.disk_io_read
            avg_metrics.disk_io_write += metrics.disk_io_write
            avg_metrics.network_sent += metrics.network_sent
            avg_metrics.network_recv += metrics.network_recv
            avg_metrics.thread_count += metrics.thread_count
            avg_metrics.open_files += metrics.open_files

        avg_metrics.cpu_percent /= count
        avg_metrics.memory_usage //= count
        avg_metrics.memory_percent /= count
        avg_metrics.disk_io_read //= count
        avg_metrics.disk_io_write //= count
        avg_metrics.network_sent //= count
        avg_metrics.network_recv //= count
        avg_metrics.thread_count //= count
        avg_metrics.open_files //= count

        return avg_metrics


class FunctionProfiler:
    """Function execution profiling."""

    def __init__(self):
        self.profiles: dict[str, FunctionProfile] = {}
        self._enabled = True

    def enable(self):
        """Enable profiling."""
        self._enabled = True

    def disable(self):
        """Disable profiling."""
        self._enabled = False

    def profile(self, func: Callable) -> Callable:
        """Decorator to profile function execution."""
        func_name = f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self._enabled:
                return func(*args, **kwargs)

            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time = end_time - start_time

                if func_name not in self.profiles:
                    self.profiles[func_name] = FunctionProfile(func_name)

                self.profiles[func_name].add_call(execution_time)

        return wrapper

    def profile_async(self, func: Callable) -> Callable:
        """Decorator to profile async function execution."""
        func_name = f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not self._enabled:
                return await func(*args, **kwargs)

            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time = end_time - start_time

                if func_name not in self.profiles:
                    self.profiles[func_name] = FunctionProfile(func_name)

                self.profiles[func_name].add_call(execution_time)

        return wrapper

    def get_profiles(self) -> dict[str, FunctionProfile]:
        """Get all function profiles."""
        return self.profiles.copy()

    def get_top_functions(self, n: int = 10, sort_by: str = "total_time") -> list[FunctionProfile]:
        """Get top N functions by specified metric."""
        profiles = list(self.profiles.values())
        profiles.sort(key=lambda p: getattr(p, sort_by, 0), reverse=True)
        return profiles[:n]

    def clear_profiles(self):
        """Clear all profiles."""
        self.profiles.clear()


class MemoryProfiler:
    """Memory usage profiling."""

    def __init__(self):
        self.snapshots: list[tuple[str, Any]] = []
        self._enabled = False

    def start(self):
        """Start memory profiling."""
        if not self._enabled:
            tracemalloc.start()
            self._enabled = True

    def stop(self):
        """Stop memory profiling."""
        if self._enabled:
            tracemalloc.stop()
            self._enabled = False

    def take_snapshot(self, description: str = ""):
        """Take a memory snapshot."""
        if not self._enabled:
            return

        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append((description, snapshot))

    def get_top_stats(self, snapshot_index: int = -1, limit: int = 10) -> list[dict[str, Any]]:
        """Get top memory allocation statistics."""
        if not self.snapshots:
            return []

        _, snapshot = self.snapshots[snapshot_index]
        top_stats = snapshot.statistics("lineno")[:limit]

        return [
            {
                "filename": stat.traceback.format()[0],
                "size": stat.size,
                "count": stat.count,
            }
            for stat in top_stats
        ]

    def compare_snapshots(self, index1: int = 0, index2: int = -1) -> list[dict[str, Any]]:
        """Compare two memory snapshots."""
        if len(self.snapshots) < 2:
            return []

        _, snapshot1 = self.snapshots[index1]
        _, snapshot2 = self.snapshots[index2]

        top_stats = snapshot2.compare_to(snapshot1, "lineno")[:10]

        return [
            {
                "filename": stat.traceback.format()[0],
                "size_diff": stat.size_diff,
                "count_diff": stat.count_diff,
            }
            for stat in top_stats
        ]


class CacheManager:
    """Simple in-memory cache with TTL support."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: dict[str, tuple[Any, float]] = {}
        self._access_order: deque = deque()
        self._lock = threading.RLock()

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                return default

            value, expires_at = self._cache[key]

            # Check if expired
            if time.time() > expires_at:
                del self._cache[key]
                with suppress(ValueError):
                    self._access_order.remove(key)
                return default

            # Update access order
            with suppress(ValueError):
                self._access_order.remove(key)
            self._access_order.append(key)

            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl

            # Remove if exists
            if key in self._cache:
                with suppress(ValueError):
                    self._access_order.remove(key)

            # Check size limit
            if len(self._cache) >= self.max_size and key not in self._cache:
                # Remove least recently used
                if self._access_order:
                    lru_key = self._access_order.popleft()
                    self._cache.pop(lru_key, None)

            self._cache[key] = (value, expires_at)
            self._access_order.append(key)

            return True

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                with suppress(ValueError):
                    self._access_order.remove(key)
                return True
            return False

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()

    def cleanup_expired(self):
        """Remove expired entries."""
        with self._lock:
            current_time = time.time()
            expired_keys = [key for key, (_, expires_at) in self._cache.items() if current_time > expires_at]

            for key in expired_keys:
                del self._cache[key]
                with suppress(ValueError):
                    self._access_order.remove(key)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_ratio": 0.0,  # Would need hit/miss tracking
                "expired_count": 0,  # Would need tracking
            }


class ThreadPoolManager:
    """Thread pool management utilities."""

    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self._executor: Optional[ThreadPoolExecutor] = None
        self._lock = threading.Lock()

    def get_executor(self) -> ThreadPoolExecutor:
        """Get or create thread pool executor."""
        if self._executor is None:
            with self._lock:
                if self._executor is None:
                    self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self._executor

    def submit(self, func: Callable, *args, **kwargs):
        """Submit task to thread pool."""
        executor = self.get_executor()
        return executor.submit(func, *args, **kwargs)

    def map(self, func: Callable, iterable):
        """Map function over iterable using thread pool."""
        executor = self.get_executor()
        return executor.map(func, iterable)

    def shutdown(self, wait: bool = True):
        """Shutdown thread pool."""
        if self._executor:
            self._executor.shutdown(wait=wait)
            self._executor = None


class AsyncTaskManager:
    """Async task management utilities."""

    def __init__(self):
        self.tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def create_task(self, coro, name: Optional[str] = None) -> str:
        """Create and track an async task."""
        task_id = name or f"task_{len(self.tasks)}"

        async with self._lock:
            if task_id in self.tasks:
                # Cancel existing task with same name
                self.tasks[task_id].cancel()

            task = asyncio.create_task(coro)
            self.tasks[task_id] = task

        return task_id

    async def get_task(self, task_id: str) -> Optional[asyncio.Task]:
        """Get task by ID."""
        async with self._lock:
            return self.tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel task by ID."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if task and not task.done():
                task.cancel()
                return True
            return False

    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None):
        """Wait for task completion."""
        task = await self.get_task(task_id)
        if task:
            return await asyncio.wait_for(task, timeout=timeout)

    async def cleanup_completed_tasks(self):
        """Remove completed tasks."""
        async with self._lock:
            completed_tasks = [task_id for task_id, task in self.tasks.items() if task.done()]

            for task_id in completed_tasks:
                del self.tasks[task_id]

    async def get_task_status(self) -> dict[str, str]:
        """Get status of all tasks."""
        async with self._lock:
            return {task_id: "completed" if task.done() else "running" for task_id, task in self.tasks.items()}


# Performance decorators


def timed(func: Callable) -> Callable:
    """Decorator to time function execution."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            logging.info(f"{func.__name__} executed in {execution_time:.4f} seconds")

    return wrapper


def memory_limit(max_mb: int):
    """Decorator to limit function memory usage."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # This is a simplified version - real implementation would need more
            # sophisticated memory monitoring
            process = psutil.Process()
            initial_memory = process.memory_info().rss

            try:
                result = func(*args, **kwargs)

                final_memory = process.memory_info().rss
                memory_used_mb = (final_memory - initial_memory) / 1024 / 1024

                if memory_used_mb > max_mb:
                    logging.warning(f"{func.__name__} used {memory_used_mb:.1f}MB (limit: {max_mb}MB)")

                return result
            except MemoryError:
                logging.error(f"{func.__name__} exceeded memory limit of {max_mb}MB")
                raise

        return wrapper

    return decorator


@contextmanager
def performance_context(description: str = "Operation"):
    """Context manager for performance monitoring."""
    start_time = time.perf_counter()
    start_memory = psutil.Process().memory_info().rss

    try:
        yield
    finally:
        end_time = time.perf_counter()
        end_memory = psutil.Process().memory_info().rss

        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory

        logging.info(
            f"{description} completed in {execution_time:.4f}s, memory delta: {memory_delta / 1024 / 1024:.1f}MB"
        )


# Global instances
system_monitor = SystemMonitor()
function_profiler = FunctionProfiler()
memory_profiler = MemoryProfiler()
cache_manager = CacheManager()
thread_pool_manager = ThreadPoolManager()

# Utility functions


def get_system_info() -> dict[str, Any]:
    """Get comprehensive system information."""
    return {
        "platform": sys.platform,
        "python_version": sys.version,
        "cpu_count": os.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "disk_usage": psutil.disk_usage("/").total,
        "pid": os.getpid(),
        "thread_count": threading.active_count(),
    }


def optimize_gc():
    """Optimize garbage collection."""
    # Force garbage collection
    collected = gc.collect()

    # Tune GC thresholds for better performance
    gc.set_threshold(700, 10, 10)

    return collected


def profile_function(func: Callable) -> Callable:
    """Convenience function to profile a function."""
    return function_profiler.profile(func)


def profile_async_function(func: Callable) -> Callable:
    """Convenience function to profile an async function."""
    return function_profiler.profile_async(func)
