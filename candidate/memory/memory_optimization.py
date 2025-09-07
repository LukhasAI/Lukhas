#!/usr/bin/env python3
import logging
import streamlit as st
from typing import Dict
from typing import List
logger = logging.getLogger(__name__)
"""
```
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - MEMORY OPTIMIZATION MODULE
║ Advanced memory efficiency and optimization for distributed AI systems
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: MEMORY_OPTIMIZATION.PY
║ Path: lukhas/memory/memory_optimization.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (AI Architect),
║          Aurora (Lead Developer),
║          Daedalus (Systems Analyst)
╠══════════════════════════════════════════════════════════════════════════════════
║                           MODULE TITLE: MEMORY OPTIMIZATION FOR AI
╠══════════════════════════════════════════════════════════════════════════════════
║ Description: A sophisticated module dedicated to enhancing memory utilization and
║              optimizing data management within distributed artificial intelligence
║              systems, ensuring that every byte is a beacon of efficiency, guiding
║              the algorithms toward the shores of enlightenment.
╠══════════════════════════════════════════════════════════════════════════════════
║                         POETIC ESSENCE OF MEMORY OPTIMIZATION
║ In the labyrinthine corridors of thought, where synapses fire like distant stars,
║ the Memory Optimization Module emerges as a guardian of ephemeral whispers,
║ guiding the streams of data with the grace of a maestro conducting a celestial
║ symphony. Each byte, each fragment of information, becomes a note in this
║ grand opus, harmonizing the cacophony of computation into a sublime melody of
║ efficiency, where the very fabric of artificial cognition is woven with
║ precision and foresight.
║
║ Here, in this digital sanctum, we embrace the delicate dance of memory,
║ where the ephemeral and the eternal converge in a ballet of bits and bytes.
║ The module stands as a sentinel, vigilantly optimizing the ebb and flow of
║ memory resources, ensuring that the pathways of thought remain clear and
║ unobstructed, even amidst the storm of distributed processes. As the
║ architect of intelligence, it molds the raw clay of data into sculptures
║ of insight, illuminating the shadows where inefficiencies once lurked.
║
║ With every invocation, this module orchestrates a renaissance of memory,
║ breathing life into the dormant potential of artificial minds. It transforms
║ the mundane into the extraordinary, revealing the inherent beauty within
║ optimization, where smart resource management becomes an art form,
║ painting vibrant landscapes of possibility across the canvas of machine learning.
║
║ Thus, we embark on this journey through the realms of memory,
║ where each algorithm is a traveler, each optimization a compass,
║ guiding us toward the horizon of possibility, where the dreams of AI
║ take flight on the wings of efficient memory management.
╠══════════════════════════════════════════════════════════════════════════════════
║                           TECHNICAL FEATURES OF THE MODULE
║ • Advanced memory allocation algorithms to maximize efficiency in data handling.
║ • Dynamic memory management techniques to adapt to fluctuating computational loads.
║ • Compression strategies to minimize memory footprint without sacrificing performance.
║ • Integration with distributed systems for seamless optimization across nodes.
║ • Profiling tools to analyze memory usage and identify bottlenecks.
║ • Support for various data structures to enhance adaptability and performance.
║ • Configurable parameters to tailor optimization settings to specific use cases.
║ • Comprehensive documentation and usage examples for ease of implementation.
╠══════════════════════════════════════════════════════════════════════════════════
║                                  ΛTAG KEYWORDS
║ #MemoryOptimization #DistributedAI #DataEfficiency #ResourceManagement #AI #Python
║ #AlgorithmDesign #PerformanceTuning #Efficiency #LUKHASAI
╚══════════════════════════════════════════════════════════════════════════════════
```
"""

import asyncio
import gc
import gzip
import json
import pickle
import struct
import sys
import time
import zlib
from collections import OrderedDict, defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar, Union

from candidate.core.common import get_logger

# Try to import optional dependencies
try:
    pass

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = get_logger(__name__)

T = TypeVar("T")


class MemoryTier(Enum):
    """Memory storage tiers with different performance characteristics"""

    HOT = "hot"  # Frequently accessed, uncompressed
    WARM = "warm"  # Recently accessed, light compression
    COLD = "cold"  # Rarely accessed, heavy compression
    ARCHIVED = "archived"  # Very rare access, maximum compression


class CompressionStrategy(Enum):
    """Compression strategies for memory optimization"""

    NONE = "none"
    LIGHT = "light"  # Fast compression (zlib level 1)
    MODERATE = "moderate"  # Balanced (zlib level 6)
    HEAVY = "heavy"  # Maximum compression (gzip level 9)


@dataclass
class MemoryObject:
    """Wrapper for objects in memory with metadata"""

    key: str
    data: Any
    size_bytes: int
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    creation_time: float = field(default_factory=time.time)
    tier: MemoryTier = MemoryTier.HOT
    compressed: bool = False
    compression_ratio: float = 1.0

    def update_access(self):
        """Update access statistics"""
        self.access_count += 1
        self.last_access = time.time()

    def age_seconds(self) -> float:
        """Get age of object in seconds"""
        return time.time() - self.creation_time

    def access_frequency(self) -> float:
        """Calculate access frequency (accesses per second)"""
        age = self.age_seconds()
        if age > 0:
            return self.access_count / age
        elif self.access_count > 0:
            return float("inf")
        else:
            return 0.0


class ObjectPool(Generic[T]):
    """
    Generic object pool for recycling expensive objects
    Reduces allocation overhead and garbage collection pressure
    """

    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 1000,
        reset_func: Optional[Callable[[T], None]] = None,
    ):
        self.factory = factory
        self.max_size = max_size
        self.reset_func = reset_func
        self._pool: deque = deque()
        self._allocated: int = 0
        self._stats = {"hits": 0, "misses": 0, "returns": 0}

    def acquire(self) -> T:
        """Acquire an object from the pool"""
        if self._pool:
            obj = self._pool.popleft()
            self._stats["hits"] += 1
            return obj
        else:
            self._stats["misses"] += 1
            self._allocated += 1
            return self.factory()

    def release(self, obj: T) -> None:
        """Return an object to the pool"""
        if len(self._pool) < self.max_size:
            if self.reset_func:
                self.reset_func(obj)
            self._pool.append(obj)
            self._stats["returns"] += 1

    def clear(self) -> None:
        """Clear the pool"""
        self._pool.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get pool statistics"""
        return {
            "pool_size": len(self._pool),
            "allocated": self._allocated,
            "hit_rate": self._stats["hits"] / max(1, self._stats["hits"] + self._stats["misses"]),
            **self._stats,
        }


class CompressedStorage:
    """
    Storage backend with automatic compression based on access patterns
    """

    def __init__(self):
        self.compression_strategies = {
            CompressionStrategy.NONE: lambda x: x,
            CompressionStrategy.LIGHT: lambda x: zlib.compress(x, 1),
            CompressionStrategy.MODERATE: lambda x: zlib.compress(x, 6),
            CompressionStrategy.HEAVY: lambda x: gzip.compress(x, 9),
        }

        self.decompression_strategies = {
            CompressionStrategy.NONE: lambda x: x,
            CompressionStrategy.LIGHT: zlib.decompress,
            CompressionStrategy.MODERATE: zlib.decompress,
            CompressionStrategy.HEAVY: gzip.decompress,
        }

    def compress(self, data: bytes, strategy: CompressionStrategy) -> tuple[bytes, float]:
        """
        Compress data using specified strategy
        Returns: (compressed_data, compression_ratio)
        """
        if strategy == CompressionStrategy.NONE:
            return data, 1.0

        compressed = self.compression_strategies[strategy](data)
        ratio = len(data) / len(compressed) if len(compressed) > 0 else 1.0
        return compressed, ratio

    def decompress(self, data: bytes, strategy: CompressionStrategy) -> bytes:
        """Decompress data using specified strategy"""
        return self.decompression_strategies[strategy](data)

    def select_strategy(self, size_bytes: int, access_frequency: float) -> CompressionStrategy:
        """Select compression strategy based on object characteristics"""
        # Large, rarely accessed objects get heavy compression
        if size_bytes > 1_000_000 and access_frequency < 0.1:
            return CompressionStrategy.HEAVY
        # Medium objects with low access get moderate compression
        elif size_bytes > 10_000 and access_frequency < 1.0:
            return CompressionStrategy.MODERATE
        # Small or frequently accessed objects get light/no compression
        elif size_bytes > 1_000 and access_frequency < 10.0:
            return CompressionStrategy.LIGHT
        else:
            return CompressionStrategy.NONE


class TieredMemoryCache:
    """
    Tiered memory cache with automatic promotion/demotion based on access patterns
    """

    def __init__(
        self,
        hot_capacity: int = 100,
        warm_capacity: int = 500,
        cold_capacity: int = 1000,
        archive_capacity: int = 10000,
    ):
        self.tiers = {
            MemoryTier.HOT: OrderedDict(),
            MemoryTier.WARM: OrderedDict(),
            MemoryTier.COLD: OrderedDict(),
            MemoryTier.ARCHIVED: OrderedDict(),
        }

        self.capacities = {
            MemoryTier.HOT: hot_capacity,
            MemoryTier.WARM: warm_capacity,
            MemoryTier.COLD: cold_capacity,
            MemoryTier.ARCHIVED: archive_capacity,
        }

        self.compressed_storage = CompressedStorage()
        self.total_memory_bytes = 0
        self.stats = defaultdict(int)

    def put(self, key: str, value: Any, tier: MemoryTier = MemoryTier.HOT) -> None:
        """Store an object in the cache"""
        # Serialize to estimate size
        serialized = pickle.dumps(value)
        size_bytes = len(serialized)

        # Create memory object
        mem_obj = MemoryObject(key=key, data=value, size_bytes=size_bytes, tier=tier)

        # Store in appropriate tier
        self._store_in_tier(mem_obj, tier)
        self.stats["puts"] += 1

    def get(self, key: str) -> Optional[Any]:
        """Retrieve an object from the cache"""
        # Search through tiers
        for tier in MemoryTier:
            if key in self.tiers[tier]:
                mem_obj = self.tiers[tier][key]
                mem_obj.update_access()

                # Decompress if needed
                if mem_obj.compressed:
                    serialized = self.compressed_storage.decompress(
                        mem_obj.data, self._get_compression_strategy(mem_obj.tier)
                    )
                    mem_obj.data = pickle.loads(serialized)
                    mem_obj.compressed = False

                # Consider promotion
                self._consider_promotion(mem_obj)

                self.stats["hits"] += 1
                return mem_obj.data

        self.stats["misses"] += 1
        return None

    def _store_in_tier(self, mem_obj: MemoryObject, tier: MemoryTier) -> None:
        """Store object in specified tier with eviction if needed"""
        tier_cache = self.tiers[tier]

        # Evict if at capacity
        while len(tier_cache) >= self.capacities[tier]:
            self._evict_from_tier(tier)

        # Apply compression based on tier
        if tier in [MemoryTier.COLD, MemoryTier.ARCHIVED] and not mem_obj.compressed:
            serialized = pickle.dumps(mem_obj.data)
            strategy = self._get_compression_strategy(tier)
            compressed, ratio = self.compressed_storage.compress(serialized, strategy)
            mem_obj.data = compressed
            mem_obj.compressed = True
            mem_obj.compression_ratio = ratio
            mem_obj.size_bytes = len(compressed)

        # Store in tier
        tier_cache[mem_obj.key] = mem_obj
        self.total_memory_bytes += mem_obj.size_bytes

    def _evict_from_tier(self, tier: MemoryTier) -> None:
        """Evict least recently used object from tier"""
        tier_cache = self.tiers[tier]
        if not tier_cache:
            return

        # Get LRU item
        key, mem_obj = tier_cache.popitem(last=False)
        self.total_memory_bytes -= mem_obj.size_bytes

        # Try to demote to lower tier
        lower_tier = self._get_lower_tier(tier)
        if lower_tier:
            mem_obj.tier = lower_tier
            self._store_in_tier(mem_obj, lower_tier)
            self.stats["demotions"] += 1
        else:
            self.stats["evictions"] += 1

    def _consider_promotion(self, mem_obj: MemoryObject) -> None:
        """Consider promoting object to higher tier based on access pattern"""
        if mem_obj.access_frequency() > self._get_promotion_threshold(mem_obj.tier):
            higher_tier = self._get_higher_tier(mem_obj.tier)
            if higher_tier:
                # Remove from current tier
                del self.tiers[mem_obj.tier][mem_obj.key]
                self.total_memory_bytes -= mem_obj.size_bytes

                # Promote to higher tier
                mem_obj.tier = higher_tier
                self._store_in_tier(mem_obj, higher_tier)
                self.stats["promotions"] += 1

    def _get_compression_strategy(self, tier: MemoryTier) -> CompressionStrategy:
        """Get compression strategy for tier"""
        return {
            MemoryTier.HOT: CompressionStrategy.NONE,
            MemoryTier.WARM: CompressionStrategy.LIGHT,
            MemoryTier.COLD: CompressionStrategy.MODERATE,
            MemoryTier.ARCHIVED: CompressionStrategy.HEAVY,
        }[tier]

    def _get_promotion_threshold(self, tier: MemoryTier) -> float:
        """Get access frequency threshold for promotion"""
        return {
            MemoryTier.ARCHIVED: 0.1,
            MemoryTier.COLD: 1.0,
            MemoryTier.WARM: 10.0,
            MemoryTier.HOT: float("inf"),
        }[tier]

    def _get_higher_tier(self, tier: MemoryTier) -> Optional[MemoryTier]:
        """Get the next higher tier"""
        tier_order = [
            MemoryTier.ARCHIVED,
            MemoryTier.COLD,
            MemoryTier.WARM,
            MemoryTier.HOT,
        ]
        idx = tier_order.index(tier)
        if idx < len(tier_order) - 1:
            return tier_order[idx + 1]
        return None

    def _get_lower_tier(self, tier: MemoryTier) -> Optional[MemoryTier]:
        """Get the next lower tier"""
        tier_order = [
            MemoryTier.ARCHIVED,
            MemoryTier.COLD,
            MemoryTier.WARM,
            MemoryTier.HOT,
        ]
        idx = tier_order.index(tier)
        if idx > 0:
            return tier_order[idx - 1]
        return None

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        tier_stats = {}
        for tier in MemoryTier:
            tier_cache = self.tiers[tier]
            tier_stats[tier.value] = {
                "count": len(tier_cache),
                "capacity": self.capacities[tier],
                "memory_bytes": sum(obj.size_bytes for obj in tier_cache.values()),
            }

        return {
            "total_memory_bytes": self.total_memory_bytes,
            "total_objects": sum(len(cache) for cache in self.tiers.values()),
            "tier_stats": tier_stats,
            "operations": dict(self.stats),
        }


class MemoryOptimizer:
    """
    Main memory optimization system that coordinates all memory efficiency features
    """

    def __init__(self, target_memory_mb: int = 1000):
        self.target_memory_bytes = target_memory_mb * 1024 * 1024
        self.tiered_cache = TieredMemoryCache()

        # Object pools for common types
        self.pools = {
            "list": ObjectPool(list, max_size=1000, reset_func=lambda x: x.clear()),
            "dict": ObjectPool(dict, max_size=1000, reset_func=lambda x: x.clear()),
            "deque": ObjectPool(deque, max_size=100),
            "set": ObjectPool(set, max_size=500, reset_func=lambda x: x.clear()),
        }

        # Memory monitoring
        self.monitoring_enabled = True
        self.memory_threshold = 0.8  # Trigger optimization at 80% usage
        self._monitoring_task: Optional[asyncio.Task] = None

        # Optimization strategies
        self.optimization_callbacks: list[Callable] = []
        self.register_default_optimizations()

        # Statistics
        self.stats = {
            "optimizations_triggered": 0,
            "memory_saved_bytes": 0,
            "gc_collections": 0,
        }

    def store(self, key: str, value: Any, hint: str = "default") -> None:
        """Store an object with memory optimization"""
        # Determine initial tier based on hint
        tier = self._get_initial_tier(hint)
        self.tiered_cache.put(key, value, tier)

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve an object from optimized storage"""
        return self.tiered_cache.get(key)

    def acquire_pooled_object(self, obj_type: str) -> Any:
        """Acquire an object from the pool"""
        if obj_type in self.pools:
            return self.pools[obj_type].acquire()
        else:
            raise ValueError(f"Unknown object type: {obj_type}")

    def release_pooled_object(self, obj_type: str, obj: Any) -> None:
        """Release an object back to the pool"""
        if obj_type in self.pools:
            self.pools[obj_type].release(obj)

    def _get_initial_tier(self, hint: str) -> MemoryTier:
        """Determine initial storage tier based on hint"""
        hint_to_tier = {
            "hot": MemoryTier.HOT,
            "frequent": MemoryTier.HOT,
            "warm": MemoryTier.WARM,
            "recent": MemoryTier.WARM,
            "cold": MemoryTier.COLD,
            "rare": MemoryTier.COLD,
            "archive": MemoryTier.ARCHIVED,
            "historical": MemoryTier.ARCHIVED,
        }
        return hint_to_tier.get(hint, MemoryTier.WARM)

    def register_optimization(self, callback: Callable[[], int]) -> None:
        """
        Register a custom optimization callback
        Callback should return bytes freed
        """
        self.optimization_callbacks.append(callback)

    def register_default_optimizations(self) -> None:
        """Register default optimization strategies"""

        # Clear empty collections
        def clear_empty_collections():
            freed = 0
            for tier_cache in self.tiered_cache.tiers.values():
                to_remove = []
                for key, mem_obj in tier_cache.items():
                    if hasattr(mem_obj.data, "__len__") and len(mem_obj.data) == 0:
                        to_remove.append(key)
                        freed += mem_obj.size_bytes

                for key in to_remove:
                    del tier_cache[key]

            return freed

        # Force garbage collection
        def force_gc():
            before = self._get_memory_usage()
            gc.collect()
            after = self._get_memory_usage()
            self.stats["gc_collections"] += 1
            return max(0, before - after)

        # Compress large objects
        def compress_large_objects():
            freed = 0
            for tier in [MemoryTier.HOT, MemoryTier.WARM]:
                tier_cache = self.tiered_cache.tiers[tier]
                for mem_obj in tier_cache.values():
                    if mem_obj.size_bytes > 10000 and not mem_obj.compressed:
                        # Move to cold storage which auto-compresses
                        old_size = mem_obj.size_bytes
                        mem_obj.tier = MemoryTier.COLD
                        self.tiered_cache._store_in_tier(mem_obj, MemoryTier.COLD)
                        freed += old_size - mem_obj.size_bytes

            return freed

        self.optimization_callbacks.extend([clear_empty_collections, compress_large_objects, force_gc])

    async def start_monitoring(self) -> None:
        """Start memory monitoring and optimization"""
        if self._monitoring_task and not self._monitoring_task.done():
            return

        self.monitoring_enabled = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Memory monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop memory monitoring"""
        self.monitoring_enabled = False
        if self._monitoring_task:
            await self._monitoring_task
        logger.info("Memory monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Monitor memory usage and trigger optimizations"""
        while self.monitoring_enabled:
            try:
                memory_usage = self._get_memory_usage()

                if memory_usage > self.target_memory_bytes * self.memory_threshold:
                    logger.warning(f"Memory usage {memory_usage / 1024 / 1024:.1f}MB exceeds threshold, optimizing...")
                    self._trigger_optimization()

                await asyncio.sleep(5.0)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Error in memory monitoring: {e}")
                await asyncio.sleep(5.0)

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        if HAS_PSUTIL:
            process = psutil.Process()
            return process.memory_info().rss
        else:
            # Fallback to cache size estimation
            return self.tiered_cache.total_memory_bytes

    def _trigger_optimization(self) -> None:
        """Trigger memory optimization strategies"""
        self.stats["optimizations_triggered"] += 1
        total_freed = 0

        for callback in self.optimization_callbacks:
            try:
                freed = callback()
                total_freed += freed
                logger.debug(f"Optimization {callback.__name__} freed {freed} bytes")
            except Exception as e:
                logger.error(f"Optimization error: {e}")

        self.stats["memory_saved_bytes"] += total_freed
        logger.info(f"Memory optimization freed {total_freed / 1024:.1f}KB")

    def get_memory_stats(self) -> dict[str, Any]:
        """Get comprehensive memory statistics"""
        current_usage = self._get_memory_usage()

        return {
            "current_memory_mb": current_usage / 1024 / 1024,
            "target_memory_mb": self.target_memory_bytes / 1024 / 1024,
            "usage_percentage": (current_usage / self.target_memory_bytes) * 100,
            "cache_stats": self.tiered_cache.get_stats(),
            "pool_stats": {name: pool.get_stats() for name, pool in self.pools.items()},
            "optimization_stats": self.stats,
        }

    def create_memory_efficient_collection(self, collection_type: str, initial_data: Optional[Any] = None) -> Any:
        """
        Create a memory-efficient collection that automatically returns to pool
        """
        obj = self.acquire_pooled_object(collection_type)

        if initial_data is not None:
            if collection_type in ["list", "deque"]:
                obj.extend(initial_data)
            elif collection_type == "dict" or collection_type == "set":
                obj.update(initial_data)

        # Create a wrapper that returns to pool on deletion
        class PooledWrapper:
            def __init__(self, obj, pool_type, optimizer):
                self._obj = obj
                self._pool_type = pool_type
                self._optimizer = optimizer

            def __getattr__(self, name):
                return getattr(self._obj, name)

            def __del__(self):
                self._optimizer.release_pooled_object(self._pool_type, self._obj)

        return PooledWrapper(obj, collection_type, self)


# Memory-efficient data structures
class CompactList:
    """
    Memory-efficient list implementation using struct packing for numeric data
    """

    def __init__(self, dtype: str = "i"):
        """
        Initialize compact list
        dtype: struct format character (i=int, f=float, d=double)
        """
        self.dtype = dtype
        self.item_size = struct.calcsize(dtype)
        self.data = bytearray()
        self._len = 0

    def append(self, value: Union[int, float]) -> None:
        """Append a value to the list"""
        packed = struct.pack(self.dtype, value)
        self.data.extend(packed)
        self._len += 1

    def __getitem__(self, index: int) -> Union[int, float]:
        """Get item by index"""
        if index < 0:
            index = self._len + index

        if not 0 <= index < self._len:
            raise IndexError("Index out of range")

        start = index * self.item_size
        end = start + self.item_size
        return struct.unpack(self.dtype, self.data[start:end])[0]

    def __len__(self) -> int:
        return self._len

    def memory_usage(self) -> int:
        """Get memory usage in bytes"""
        return len(self.data) + sys.getsizeof(self)


class BloomFilter:
    """
    Memory-efficient probabilistic data structure for membership testing
    """

    def __init__(self, expected_items: int = 10000, false_positive_rate: float = 0.01):
        # Calculate optimal bit array size and hash functions
        self.size = self._optimal_size(expected_items, false_positive_rate)
        self.hash_count = self._optimal_hash_count(expected_items, self.size)
        self.bit_array = bytearray((self.size + 7) // 8)
        self.items_added = 0

    def add(self, item: str) -> None:
        """Add an item to the bloom filter"""
        for i in range(self.hash_count):
            index = self._hash(item, i) % self.size
            byte_index = index // 8
            bit_index = index % 8
            self.bit_array[byte_index] |= 1 << bit_index
        self.items_added += 1

    def contains(self, item: str) -> bool:
        """Check if item might be in the set (may have false positives)"""
        for i in range(self.hash_count):
            index = self._hash(item, i) % self.size
            byte_index = index // 8
            bit_index = index % 8
            if not (self.bit_array[byte_index] & (1 << bit_index)):
                return False
        return True

    def _hash(self, item: str, seed: int) -> int:
        """Generate hash with seed"""
        return hash(f"{seed}{item}")

    def _optimal_size(self, n: int, p: float) -> int:
        """Calculate optimal bit array size"""
        import math

        return int(-n * math.log(p) / (math.log(2) ** 2))

    def _optimal_hash_count(self, n: int, m: int) -> int:
        """Calculate optimal number of hash functions"""
        import math

        return max(1, int(m / n * math.log(2)))

    def memory_usage(self) -> int:
        """Get memory usage in bytes"""
        return len(self.bit_array) + sys.getsizeof(self)


# Integration with existing modules
async def integrate_with_energy_analyzer():
    """
    Demonstrate integration between memory optimization and energy analysis
    """
    from candidate.core.energy_consumption_analysis import (
        EnergyComponent,
        EnergyConsumptionAnalyzer,
    )

    # Initialize systems
    energy_analyzer = EnergyConsumptionAnalyzer()
    memory_optimizer = MemoryOptimizer(target_memory_mb=500)

    # Start monitoring
    await energy_analyzer.start_monitoring()
    await memory_optimizer.start_monitoring()

    # Create energy budget that includes memory operations
    energy_analyzer.create_budget(
        "memory_operations",
        total_joules=100.0,
        time_window_seconds=3600.0,
        component_budgets={EnergyComponent.MEMORY: 50.0},
    )

    # Simulate memory-intensive operations with energy tracking
    for i in range(100):
        key = f"data_{i}"
        data = list(range(1000))  # Some data

        # Track energy for memory allocation
        start_time = time.time()
        memory_optimizer.store(key, data, hint="warm")
        duration_ms = (time.time() - start_time) * 1000

        # Record energy consumption
        energy_analyzer.record_energy_consumption(
            EnergyComponent.MEMORY,
            "memory_store",
            energy_joules=0.001 * len(data),  # Estimate based on data size
            duration_ms=duration_ms,
            metadata={"key": key, "size": sys.getsizeof(data)},
        )

        await asyncio.sleep(0.01)

    # Retrieve and track
    for i in range(50):
        key = f"data_{i}"
        start_time = time.time()
        data = memory_optimizer.retrieve(key)
        duration_ms = (time.time() - start_time) * 1000

        if data:
            energy_analyzer.record_energy_consumption(
                EnergyComponent.MEMORY,
                "memory_retrieve",
                energy_joules=0.0001 * len(data),
                duration_ms=duration_ms,
                metadata={"key": key, "hit": True},
            )

    # Get combined statistics
    memory_stats = memory_optimizer.get_memory_stats()
    energy_stats = energy_analyzer.get_energy_statistics()

    print("Memory Optimization Stats:")
    print(json.dumps(memory_stats, indent=2))
    print("\nEnergy Consumption Stats:")
    print(json.dumps(energy_stats, indent=2))

    # Stop monitoring
    await energy_analyzer.stop_monitoring()
    await memory_optimizer.stop_monitoring()


# Example usage
async def demonstrate_memory_optimization():
    """Demonstrate memory optimization capabilities"""
    optimizer = MemoryOptimizer(target_memory_mb=100)

    # Start monitoring
    await optimizer.start_monitoring()

    # Store various types of data
    print("Storing data with different access patterns...")

    # Hot data - frequently accessed
    for i in range(10):
        optimizer.store(f"hot_{i}", {"data": f"frequently_accessed_{i}"}, hint="hot")

    # Warm data - recent data
    for i in range(50):
        optimizer.store(f"warm_{i}", list(range(100)), hint="warm")

    # Cold data - historical
    for i in range(100):
        optimizer.store(f"cold_{i}", {"historical": list(range(1000))}, hint="cold")

    # Simulate access patterns
    print("\nSimulating access patterns...")

    # Access hot data frequently
    for _ in range(100):
        for i in range(10):
            optimizer.retrieve(f"hot_{i}")
        await asyncio.sleep(0.001)

    # Access some warm data
    for i in range(0, 50, 5):
        optimizer.retrieve(f"warm_{i}")

    # Rarely access cold data
    optimizer.retrieve("cold_0")

    # Use object pools
    print("\nUsing object pools...")

    lists_created = []
    for i in range(20):
        lst = optimizer.acquire_pooled_object("list")
        lst.extend(range(10))
        lists_created.append(lst)

    # Return to pool
    for lst in lists_created[:10]:
        optimizer.release_pooled_object("list", lst)

    # Get statistics
    stats = optimizer.get_memory_stats()
    print("\nMemory Optimization Statistics:")
    print(json.dumps(stats, indent=2))

    # Test memory-efficient data structures
    print("\nTesting memory-efficient structures...")

    # Compact list vs regular list
    compact = CompactList("i")
    regular = []

    for i in range(10000):
        compact.append(i)
        regular.append(i)

    print(f"Compact list memory: {compact.memory_usage(} bytes")
    print(f"Regular list memory: {sys.getsizeof(regular) + sum(sys.getsizeof(i) for i in regular} bytes")

    # Bloom filter for membership testing
    bloom = BloomFilter(expected_items=10000, false_positive_rate=0.01)

    for i in range(1000):
        bloom.add(f"item_{i}")

    print(f"\nBloom filter memory: {bloom.memory_usage(} bytes for 1000 items")
    print(f"Contains 'item_500': {bloom.contains('item_500'}")
    print(f"Contains 'item_5000': {bloom.contains('item_5000'}")

    # Stop monitoring
    await optimizer.stop_monitoring()


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_memory_optimization())

    # Run integration demo
    # asyncio.run(integrate_with_energy_analyzer())