#!/usr/bin/env python3
"""
Memory Fold Performance Optimizer

Optimizes memory fold operations with intelligent caching, batch processing,
and performance monitoring for enterprise-scale memory management.

# ΛTAG: memory_optimization, performance_enhancement, fold_acceleration
"""

import asyncio
import hashlib
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from weakref import WeakSet

try:
    from memory.core.memory_core import MemoryFold, MemoryItem
    from memory.fold_lineage_tracker import CausalLink, CausationType
    MEMORY_AVAILABLE = True
except ImportError:
    # Fallback for testing without full memory system
    MEMORY_AVAILABLE = False

    @dataclass
    class CausalLink:
        source_fold_key: str
        target_fold_key: str
        causation_type: str
        timestamp_utc: str
        strength: float
        metadata: dict

    class CausationType:
        ASSOCIATION = "association"
        PERFORMANCE_OPTIMIZATION = "performance_optimization"

    class MemoryFold:
        def __init__(self, id: str):
            self.id = id
            self.items = []

    class MemoryItem:
        def __init__(self, id: str, content: dict):
            self.id = id
            self.content = content


@dataclass
class PerformanceMetrics:
    """Performance metrics for fold operations."""

    operation_count: int = 0
    total_duration_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    batch_operations: int = 0
    optimization_saves_ms: float = 0.0

    @property
    def average_duration_ms(self) -> float:
        return self.total_duration_ms / max(1, self.operation_count)

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / max(1, total)


@dataclass
class OptimizationResult:
    """Result of a fold optimization operation."""

    fold_id: str
    original_size: int
    optimized_size: int
    compression_ratio: float
    optimization_time_ms: float
    cache_efficiency: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class FoldPerformanceOptimizer:
    """High-performance optimizer for memory fold operations."""

    def __init__(self,
                 cache_size: int = 10000,
                 batch_threshold: int = 50,
                 optimization_interval_sec: float = 30.0):
        """
        Initialize performance optimizer.
        
        Args:
            cache_size: Maximum number of cached fold operations
            batch_threshold: Minimum items for batch processing
            optimization_interval_sec: Auto-optimization interval
        """

        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.operation_history: deque = deque(maxlen=1000)

        # Caching system
        self.cache_size = cache_size
        self.fold_cache: Dict[str, Tuple[Any, float]] = {}  # fold_id -> (data, timestamp)
        self.result_cache: Dict[str, Tuple[Any, float]] = {}  # operation_hash -> (result, timestamp)
        self.cache_ttl_sec = 300.0  # 5 minutes

        # Batch processing
        self.batch_threshold = batch_threshold
        self.pending_operations: Dict[str, List[Any]] = defaultdict(list)
        self.batch_timer_tasks: Dict[str, asyncio.Task] = {}

        # Optimization scheduling
        self.optimization_interval_sec = optimization_interval_sec
        self.auto_optimization_task: Optional[asyncio.Task] = None
        self.optimization_queue: asyncio.Queue = asyncio.Queue()

        # Weak references to active folds for memory efficiency
        self.active_folds: WeakSet = WeakSet()

        # Performance thresholds
        self.slow_operation_threshold_ms = 100.0
        self.memory_pressure_threshold = 0.8  # 80% memory usage

    async def start_optimization_service(self) -> None:
        """Start the background optimization service."""

        if self.auto_optimization_task is None:
            self.auto_optimization_task = asyncio.create_task(
                self._auto_optimization_loop()
            )

    async def stop_optimization_service(self) -> None:
        """Stop the background optimization service."""

        if self.auto_optimization_task:
            self.auto_optimization_task.cancel()
            try:
                await self.auto_optimization_task
            except asyncio.CancelledError:
                pass
            self.auto_optimization_task = None

        # Cancel any pending batch timers
        for task in self.batch_timer_tasks.values():
            task.cancel()
        self.batch_timer_tasks.clear()

    def _generate_operation_hash(self, operation: str, params: Dict[str, Any]) -> str:
        """Generate hash for caching operation results."""

        # Create deterministic hash from operation and parameters
        param_str = str(sorted(params.items()))
        content = f"{operation}:{param_str}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached entry is still valid."""
        return (time.time() - timestamp) < self.cache_ttl_sec

    async def _get_cached_result(self, operation_hash: str) -> Optional[Any]:
        """Get cached operation result if valid."""

        if operation_hash in self.result_cache:
            result, timestamp = self.result_cache[operation_hash]
            if self._is_cache_valid(timestamp):
                self.metrics.cache_hits += 1
                return result
            else:
                del self.result_cache[operation_hash]

        self.metrics.cache_misses += 1
        return None

    async def _cache_result(self, operation_hash: str, result: Any) -> None:
        """Cache operation result with timestamp."""

        # Implement LRU eviction if cache is full
        if len(self.result_cache) >= self.cache_size:
            # Remove oldest 10% of entries
            sorted_entries = sorted(
                self.result_cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            remove_count = max(1, len(sorted_entries) // 10)
            for key, _ in sorted_entries[:remove_count]:
                del self.result_cache[key]

        self.result_cache[operation_hash] = (result, time.time())

    async def optimize_fold_consolidation(self, fold: MemoryFold) -> OptimizationResult:
        """Optimize fold consolidation with intelligent caching and batching."""

        start_time = time.time()
        operation_hash = self._generate_operation_hash(
            "consolidate",
            {"fold_id": fold.id, "item_count": len(fold.items)}
        )

        # Check cache first
        cached_result = await self._get_cached_result(operation_hash)
        if cached_result:
            return cached_result

        # Track operation
        self.metrics.operation_count += 1
        original_size = len(fold.items)

        # Optimize consolidation process
        optimized_items = await self._optimize_items_batch(fold.items)

        # Calculate compression metrics
        optimized_size = len(optimized_items)
        compression_ratio = optimized_size / max(1, original_size)

        # Performance measurement
        optimization_time_ms = (time.time() - start_time) * 1000
        self.metrics.total_duration_ms += optimization_time_ms

        # Create optimization result
        result = OptimizationResult(
            fold_id=fold.id,
            original_size=original_size,
            optimized_size=optimized_size,
            compression_ratio=compression_ratio,
            optimization_time_ms=optimization_time_ms,
            cache_efficiency=self.metrics.cache_hit_rate,
            metadata={
                "optimization_type": "intelligent_consolidation",
                "batch_processed": original_size >= self.batch_threshold,
                "performance_tier": "fast" if optimization_time_ms < 50 else "normal"
            }
        )

        # Cache result
        await self._cache_result(operation_hash, result)

        # Record performance
        self.operation_history.append({
            "timestamp": time.time(),
            "operation": "consolidation",
            "duration_ms": optimization_time_ms,
            "cache_hit": False,
            "fold_id": fold.id
        })

        return result

    async def _optimize_items_batch(self, items: List[MemoryItem]) -> List[MemoryItem]:
        """Optimize memory items using batch processing."""

        if len(items) < self.batch_threshold:
            return await self._optimize_items_single(items)

        # Batch processing for large sets
        self.metrics.batch_operations += 1

        # Group items by similarity for efficient processing
        similarity_groups = self._group_items_by_similarity(items)
        optimized_items = []

        # Process each group
        for group in similarity_groups:
            group_optimized = await self._optimize_similar_items(group)
            optimized_items.extend(group_optimized)

        return optimized_items

    async def _optimize_items_single(self, items: List[MemoryItem]) -> List[MemoryItem]:
        """Optimize small sets of memory items."""

        # Simple optimization for small sets
        return [item for item in items if self._is_item_worth_keeping(item)]

    def _group_items_by_similarity(self, items: List[MemoryItem]) -> List[List[MemoryItem]]:
        """Group items by content similarity for batch optimization."""

        # Simple similarity grouping based on content type
        groups: Dict[str, List[MemoryItem]] = defaultdict(list)

        for item in items:
            # Group by content type or tags
            if hasattr(item, 'tags') and item.tags:
                group_key = sorted(item.tags)[0]  # Use first tag as group key
            elif hasattr(item, 'content') and isinstance(item.content, dict):
                group_key = item.content.get('type', 'default')
            else:
                group_key = 'default'

            groups[group_key].append(item)

        return list(groups.values())

    async def _optimize_similar_items(self, items: List[MemoryItem]) -> List[MemoryItem]:
        """Optimize a group of similar items."""

        # Remove duplicates and low-importance items
        unique_items = []
        seen_content = set()

        for item in sorted(items, key=lambda x: getattr(x, 'importance_score', 0.0), reverse=True):
            # Create content hash for deduplication
            content_str = str(item.content) if hasattr(item, 'content') else str(item.id)
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()

            if content_hash not in seen_content and self._is_item_worth_keeping(item):
                unique_items.append(item)
                seen_content.add(content_hash)

        return unique_items

    def _is_item_worth_keeping(self, item: MemoryItem) -> bool:
        """Determine if memory item is worth keeping."""

        # Basic importance threshold
        if hasattr(item, 'importance_score'):
            return item.importance_score > 0.1

        # Content-based filtering
        if hasattr(item, 'content') and isinstance(item.content, dict):
            # Keep items with substantive content
            return len(str(item.content)) > 10

        return True  # Conservative default

    async def _auto_optimization_loop(self) -> None:
        """Background optimization service loop."""

        while True:
            try:
                await asyncio.sleep(self.optimization_interval_sec)

                # Clean expired cache entries
                await self._cleanup_expired_cache()

                # Process optimization queue
                await self._process_optimization_queue()

                # Check for performance issues
                await self._check_performance_health()

            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue service
                print(f"Auto-optimization error: {e}")
                await asyncio.sleep(1.0)  # Brief pause before retry

    async def _cleanup_expired_cache(self) -> None:
        """Remove expired entries from caches."""

        current_time = time.time()

        # Clean result cache
        expired_keys = [
            key for key, (_, timestamp) in self.result_cache.items()
            if (current_time - timestamp) > self.cache_ttl_sec
        ]

        for key in expired_keys:
            del self.result_cache[key]

        # Clean fold cache
        expired_keys = [
            key for key, (_, timestamp) in self.fold_cache.items()
            if (current_time - timestamp) > self.cache_ttl_sec
        ]

        for key in expired_keys:
            del self.fold_cache[key]

    async def _process_optimization_queue(self) -> None:
        """Process pending optimization requests."""

        while not self.optimization_queue.empty():
            try:
                optimization_request = await asyncio.wait_for(
                    self.optimization_queue.get(),
                    timeout=0.1
                )
                await self._handle_optimization_request(optimization_request)
            except asyncio.TimeoutError:
                break

    async def _handle_optimization_request(self, request: Dict[str, Any]) -> None:
        """Handle individual optimization request."""

        # Process optimization request based on type
        if request.get("type") == "fold_consolidation":
            fold = request.get("fold")
            if fold:
                result = await self.optimize_fold_consolidation(fold)
                # Store result if callback provided
                if "callback" in request:
                    await request["callback"](result)

    async def _check_performance_health(self) -> None:
        """Check system performance health and trigger optimizations."""

        # Check average response time
        if self.metrics.average_duration_ms > self.slow_operation_threshold_ms:
            # Trigger cache optimization
            await self._optimize_cache_performance()

        # Check cache hit rate
        if self.metrics.cache_hit_rate < 0.7:  # Below 70%
            # Adjust cache TTL for better performance
            self.cache_ttl_sec = min(600.0, self.cache_ttl_sec * 1.1)

    async def _optimize_cache_performance(self) -> None:
        """Optimize cache performance settings."""

        # Increase cache size if memory allows
        if self.cache_size < 20000:  # Reasonable upper limit
            self.cache_size = int(self.cache_size * 1.2)

        # Adjust batch threshold for better performance
        if self.metrics.batch_operations > 0:
            avg_batch_duration = self.metrics.total_duration_ms / self.metrics.batch_operations
            if avg_batch_duration > 200:  # Too slow
                self.batch_threshold = int(self.batch_threshold * 1.5)

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""

        return {
            "metrics": {
                "operation_count": self.metrics.operation_count,
                "average_duration_ms": self.metrics.average_duration_ms,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "batch_operations": self.metrics.batch_operations,
                "optimization_saves_ms": self.metrics.optimization_saves_ms
            },
            "cache_status": {
                "result_cache_size": len(self.result_cache),
                "fold_cache_size": len(self.fold_cache),
                "cache_ttl_sec": self.cache_ttl_sec,
                "max_cache_size": self.cache_size
            },
            "performance_health": {
                "is_healthy": self.metrics.average_duration_ms < self.slow_operation_threshold_ms,
                "cache_efficiency": "good" if self.metrics.cache_hit_rate > 0.7 else "needs_improvement",
                "batch_efficiency": "enabled" if self.metrics.batch_operations > 0 else "not_used"
            },
            "recent_operations": list(self.operation_history)[-10:]  # Last 10 operations
        }


# Global optimizer instance for system-wide use
_global_optimizer: Optional[FoldPerformanceOptimizer] = None


def get_fold_optimizer() -> FoldPerformanceOptimizer:
    """Get global fold performance optimizer instance."""
    global _global_optimizer

    if _global_optimizer is None:
        _global_optimizer = FoldPerformanceOptimizer()

    return _global_optimizer


async def optimize_fold_async(fold: MemoryFold) -> OptimizationResult:
    """Convenient async function to optimize a memory fold."""
    optimizer = get_fold_optimizer()
    return await optimizer.optimize_fold_consolidation(fold)


if __name__ == "__main__":
    # Performance testing
    async def test_optimizer():
        optimizer = FoldPerformanceOptimizer()
        await optimizer.start_optimization_service()

        # Create test fold
        test_fold = MemoryFold("test_fold")

        # Simulate optimization
        result = await optimizer.optimize_fold_consolidation(test_fold)
        print(f"Optimization result: {result}")

        # Get performance report
        report = optimizer.get_performance_report()
        print(f"Performance report: {report}")

        await optimizer.stop_optimization_service()

    asyncio.run(test_optimizer())
