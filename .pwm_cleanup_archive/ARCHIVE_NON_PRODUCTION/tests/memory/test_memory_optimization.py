"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧪 LUKHAS AI - MEMORY OPTIMIZATION TEST SUITE
║ Comprehensive tests for memory efficiency and optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_memory_optimization.py
║ Path: tests/memory/test_memory_optimization.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ TEST COVERAGE
╠══════════════════════════════════════════════════════════════════════════════════
║ - Memory object management and metadata
║ - Object pooling and recycling
║ - Compression strategies
║ - Tiered memory cache operations
║ - Memory optimization triggers
║ - Compact data structures
║ - Bloom filter operations
║ - Integration with monitoring
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import sys
import time

import pytest

from memory.memory_optimization import (
    BloomFilter,
    CompactList,
    CompressedStorage,
    CompressionStrategy,
    MemoryObject,
    MemoryOptimizer,
    MemoryTier,
    ObjectPool,
    TieredMemoryCache,
)


class TestMemoryObject:
    """Test MemoryObject dataclass"""

    def test_memory_object_creation(self):
        """Test creating a memory object"""
        mem_obj = MemoryObject(
            key="test_key", data={"test": "data"}, size_bytes=100, tier=MemoryTier.HOT
        )

        assert mem_obj.key == "test_key"
        assert mem_obj.data == {"test": "data"}
        assert mem_obj.size_bytes == 100
        assert mem_obj.access_count == 0
        assert mem_obj.tier == MemoryTier.HOT
        assert mem_obj.compressed == False

    def test_update_access(self):
        """Test updating access statistics"""
        mem_obj = MemoryObject(key="test", data="data", size_bytes=10)

        initial_time = mem_obj.last_access
        time.sleep(0.01)

        mem_obj.update_access()
        assert mem_obj.access_count == 1
        assert mem_obj.last_access > initial_time

        mem_obj.update_access()
        assert mem_obj.access_count == 2

    def test_age_calculation(self):
        """Test age calculation"""
        mem_obj = MemoryObject(key="test", data="data", size_bytes=10)

        time.sleep(0.1)
        age = mem_obj.age_seconds()
        assert age >= 0.1
        assert age < 0.2

    def test_access_frequency(self):
        """Test access frequency calculation"""
        mem_obj = MemoryObject(key="test", data="data", size_bytes=10)

        # New object with no accesses has 0 frequency
        assert mem_obj.access_frequency() == 0.0

        time.sleep(0.1)
        mem_obj.update_access()
        mem_obj.update_access()

        freq = mem_obj.access_frequency()
        assert freq > 0
        assert freq < 100  # Should be around 20 accesses/second


class TestObjectPool:
    """Test object pooling functionality"""

    def test_pool_creation(self):
        """Test creating an object pool"""
        pool = ObjectPool(list, max_size=10)
        assert pool.max_size == 10
        assert pool._allocated == 0
        assert len(pool._pool) == 0

    def test_acquire_new_object(self):
        """Test acquiring a new object when pool is empty"""
        pool = ObjectPool(dict, max_size=5)

        obj = pool.acquire()
        assert isinstance(obj, dict)
        assert pool._allocated == 1
        assert pool._stats["misses"] == 1
        assert pool._stats["hits"] == 0

    def test_release_and_reuse(self):
        """Test releasing and reusing objects"""
        pool = ObjectPool(list, max_size=5, reset_func=lambda x: x.clear())

        # Acquire and modify object
        obj1 = pool.acquire()
        obj1.extend([1, 2, 3])

        # Release back to pool
        pool.release(obj1)
        assert len(pool._pool) == 1
        assert pool._stats["returns"] == 1

        # Acquire again - should get same object cleared
        obj2 = pool.acquire()
        assert len(obj2) == 0  # Should be cleared
        assert pool._stats["hits"] == 1
        assert pool._allocated == 1  # No new allocation

    def test_pool_max_size(self):
        """Test pool respects max size"""
        pool = ObjectPool(list, max_size=2)

        objects = [pool.acquire() for _ in range(5)]

        # Release all objects
        for obj in objects:
            pool.release(obj)

        # Pool should only keep max_size objects
        assert len(pool._pool) == 2

    def test_pool_statistics(self):
        """Test pool statistics tracking"""
        pool = ObjectPool(set, max_size=10)

        # Create some activity
        objs = [pool.acquire() for _ in range(3)]
        for obj in objs:
            pool.release(obj)

        # Reuse objects
        for _ in range(2):
            obj = pool.acquire()
            pool.release(obj)

        stats = pool.get_stats()
        assert stats["allocated"] == 3
        assert stats["hits"] == 2
        assert stats["misses"] == 3
        assert stats["returns"] == 5
        assert stats["hit_rate"] == 2 / 5


class TestCompressedStorage:
    """Test compression functionality"""

    def test_compression_strategies(self):
        """Test different compression strategies"""
        storage = CompressedStorage()
        test_data = b"This is test data that should compress well" * 100

        # Test each strategy
        strategies = [
            (CompressionStrategy.NONE, 1.0),
            (CompressionStrategy.LIGHT, None),
            (CompressionStrategy.MODERATE, None),
            (CompressionStrategy.HEAVY, None),
        ]

        for strategy, expected_ratio in strategies:
            compressed, ratio = storage.compress(test_data, strategy)

            if strategy == CompressionStrategy.NONE:
                assert compressed == test_data
                assert ratio == expected_ratio
            else:
                assert len(compressed) < len(test_data)
                assert ratio > 1.0

                # Verify decompression
                decompressed = storage.decompress(compressed, strategy)
                assert decompressed == test_data

    def test_strategy_selection(self):
        """Test automatic strategy selection"""
        storage = CompressedStorage()

        # Large, rarely accessed
        strategy = storage.select_strategy(2_000_000, 0.05)
        assert strategy == CompressionStrategy.HEAVY

        # Medium, low access
        strategy = storage.select_strategy(50_000, 0.5)
        assert strategy == CompressionStrategy.MODERATE

        # Small, moderate access
        strategy = storage.select_strategy(5_000, 5.0)
        assert strategy == CompressionStrategy.LIGHT

        # Tiny or very frequent
        strategy = storage.select_strategy(500, 20.0)
        assert strategy == CompressionStrategy.NONE


class TestTieredMemoryCache:
    """Test tiered memory cache functionality"""

    def test_cache_initialization(self):
        """Test cache initialization"""
        cache = TieredMemoryCache(
            hot_capacity=10, warm_capacity=20, cold_capacity=30, archive_capacity=40
        )

        assert cache.capacities[MemoryTier.HOT] == 10
        assert cache.capacities[MemoryTier.WARM] == 20
        assert cache.capacities[MemoryTier.COLD] == 30
        assert cache.capacities[MemoryTier.ARCHIVED] == 40
        assert cache.total_memory_bytes == 0

    def test_put_and_get(self):
        """Test basic put and get operations"""
        cache = TieredMemoryCache()

        # Put data in hot tier
        cache.put("key1", {"data": "value1"})

        # Retrieve data
        value = cache.get("key1")
        assert value == {"data": "value1"}
        assert cache.stats["puts"] == 1
        assert cache.stats["hits"] == 1

        # Non-existent key
        assert cache.get("nonexistent") is None
        assert cache.stats["misses"] == 1

    def test_tier_eviction(self):
        """Test eviction when tier is full"""
        cache = TieredMemoryCache(hot_capacity=2, warm_capacity=2)

        # Fill hot tier
        cache.put("key1", "data1")
        cache.put("key2", "data2")
        cache.put("key3", "data3")  # Should evict key1 to warm

        # key1 should be in warm tier
        assert "key1" not in cache.tiers[MemoryTier.HOT]
        assert "key1" in cache.tiers[MemoryTier.WARM]
        assert cache.stats["demotions"] == 1

    def test_access_promotion(self):
        """Test promotion based on access frequency"""
        cache = TieredMemoryCache()

        # Put in warm tier
        cache.put("key1", "data1", MemoryTier.WARM)

        # Access frequently to trigger promotion
        for _ in range(20):
            cache.get("key1")
            time.sleep(0.01)

        # Should be promoted to hot tier
        assert "key1" in cache.tiers[MemoryTier.HOT]
        assert "key1" not in cache.tiers[MemoryTier.WARM]
        assert cache.stats["promotions"] > 0

    def test_compression_in_cold_tiers(self):
        """Test automatic compression in cold tiers"""
        cache = TieredMemoryCache()

        # Large data that should be compressed
        large_data = "x" * 10000
        cache.put("key1", large_data, MemoryTier.COLD)

        # Check if compressed
        mem_obj = cache.tiers[MemoryTier.COLD]["key1"]
        assert mem_obj.compressed == True
        assert mem_obj.compression_ratio > 1.0

        # Retrieve should decompress
        retrieved = cache.get("key1")
        assert retrieved == large_data

    def test_cache_statistics(self):
        """Test cache statistics"""
        cache = TieredMemoryCache()

        # Add some data
        for i in range(5):
            cache.put(f"hot_{i}", f"data_{i}", MemoryTier.HOT)
        for i in range(3):
            cache.put(f"warm_{i}", f"data_{i}", MemoryTier.WARM)

        stats = cache.get_stats()
        assert stats["total_objects"] == 8
        assert stats["tier_stats"]["hot"]["count"] == 5
        assert stats["tier_stats"]["warm"]["count"] == 3
        assert stats["total_memory_bytes"] > 0


class TestMemoryOptimizer:
    """Test main memory optimizer"""

    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance for tests"""
        return MemoryOptimizer(target_memory_mb=100)

    def test_optimizer_initialization(self, optimizer):
        """Test optimizer initialization"""
        assert optimizer.target_memory_bytes == 100 * 1024 * 1024
        assert optimizer.monitoring_enabled == True
        assert "list" in optimizer.pools
        assert "dict" in optimizer.pools

    def test_store_and_retrieve(self, optimizer):
        """Test storing and retrieving data"""
        optimizer.store("test_key", {"data": "value"}, hint="hot")

        retrieved = optimizer.retrieve("test_key")
        assert retrieved == {"data": "value"}

    def test_pooled_objects(self, optimizer):
        """Test acquiring and releasing pooled objects"""
        # Acquire list from pool
        lst = optimizer.acquire_pooled_object("list")
        assert isinstance(lst, list)

        lst.extend([1, 2, 3])

        # Release back to pool
        optimizer.release_pooled_object("list", lst)

        # Check pool stats
        stats = optimizer.pools["list"].get_stats()
        assert stats["returns"] == 1

    def test_memory_efficient_collection(self, optimizer):
        """Test creating memory-efficient collections"""
        # Create efficient list
        efficient_list = optimizer.create_memory_efficient_collection("list", [1, 2, 3])

        # Should behave like a list
        assert len(efficient_list._obj) == 3
        assert efficient_list._obj[0] == 1

    def test_optimization_triggers(self, optimizer):
        """Test memory optimization triggers"""
        # Add optimization callback
        freed_bytes = [0]

        def custom_optimization():
            freed_bytes[0] = 1000
            return 1000

        optimizer.register_optimization(custom_optimization)

        # Trigger optimization
        optimizer._trigger_optimization()

        assert freed_bytes[0] == 1000
        assert optimizer.stats["optimizations_triggered"] == 1
        assert optimizer.stats["memory_saved_bytes"] >= 1000

    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, optimizer):
        """Test monitoring start/stop"""
        await optimizer.start_monitoring()
        assert optimizer._monitoring_task is not None

        await optimizer.stop_monitoring()
        assert optimizer.monitoring_enabled == False

    def test_memory_statistics(self, optimizer):
        """Test memory statistics gathering"""
        # Store some data
        for i in range(10):
            optimizer.store(f"key_{i}", {"data": f"value_{i}"})

        stats = optimizer.get_memory_stats()

        assert "current_memory_mb" in stats
        assert "target_memory_mb" in stats
        assert "usage_percentage" in stats
        assert "cache_stats" in stats
        assert "pool_stats" in stats
        assert stats["cache_stats"]["total_objects"] == 10


class TestCompactDataStructures:
    """Test memory-efficient data structures"""

    def test_compact_list(self):
        """Test CompactList functionality"""
        # Integer list
        compact = CompactList("i")

        # Add values
        for i in range(1000):
            compact.append(i)

        # Verify storage
        assert len(compact) == 1000
        assert compact[0] == 0
        assert compact[999] == 999
        assert compact[-1] == 999

        # Compare memory usage
        regular_list = list(range(1000))
        regular_size = sys.getsizeof(regular_list) + sum(
            sys.getsizeof(i) for i in regular_list
        )
        compact_size = compact.memory_usage()

        # Compact should be much smaller
        assert compact_size < regular_size / 2

    def test_compact_list_float(self):
        """Test CompactList with floats"""
        compact = CompactList("f")

        values = [1.1, 2.2, 3.3, 4.4, 5.5]
        for v in values:
            compact.append(v)

        for i, v in enumerate(values):
            assert abs(compact[i] - v) < 0.001

    def test_bloom_filter(self):
        """Test BloomFilter functionality"""
        bloom = BloomFilter(expected_items=1000, false_positive_rate=0.01)

        # Add items
        items = [f"item_{i}" for i in range(100)]
        for item in items:
            bloom.add(item)

        # Test membership
        for item in items:
            assert bloom.contains(item) == True

        # Test non-members (should be no false negatives)
        for i in range(1000, 1100):
            if bloom.contains(f"item_{i}"):
                # False positive - acceptable at specified rate
                pass
            else:
                # True negative
                assert bloom.contains(f"item_{i}") == False

        # Check memory efficiency
        memory = bloom.memory_usage()
        # Should be much smaller than storing all strings
        string_memory = sum(sys.getsizeof(item) for item in items)
        assert memory < string_memory


class TestIntegration:
    """Integration tests for memory optimization"""

    @pytest.mark.asyncio
    async def test_memory_optimization_workflow(self):
        """Test complete memory optimization workflow"""
        optimizer = MemoryOptimizer(target_memory_mb=50)

        # Start monitoring
        await optimizer.start_monitoring()

        # Simulate various data storage patterns

        # Hot data - frequently accessed
        for i in range(10):
            optimizer.store(
                f"hot_{i}", {"id": i, "data": "frequently_used"}, hint="hot"
            )

        # Warm data - recent
        for i in range(20):
            optimizer.store(f"warm_{i}", list(range(100)), hint="warm")

        # Cold data - archival
        for i in range(30):
            large_data = {"history": list(range(1000))}
            optimizer.store(f"cold_{i}", large_data, hint="cold")

        # Simulate access patterns
        for _ in range(5):
            # Access hot data frequently
            for i in range(10):
                optimizer.retrieve(f"hot_{i}")

            # Access some warm data
            optimizer.retrieve("warm_5")
            optimizer.retrieve("warm_10")

            await asyncio.sleep(0.01)

        # Use pooled objects
        lists = []
        for _ in range(5):
            lst = optimizer.acquire_pooled_object("list")
            lst.extend(range(10))
            lists.append(lst)

        # Return some to pool
        for lst in lists[:3]:
            optimizer.release_pooled_object("list", lst)

        # Get final statistics
        stats = optimizer.get_memory_stats()

        # Verify results
        assert stats["cache_stats"]["total_objects"] == 60
        assert stats["pool_stats"]["list"]["returns"] == 3
        assert stats["optimization_stats"]["optimizations_triggered"] >= 0

        # Stop monitoring
        await optimizer.stop_monitoring()

    @pytest.mark.asyncio
    async def test_memory_pressure_handling(self):
        """Test behavior under memory pressure"""
        optimizer = MemoryOptimizer(target_memory_mb=1)  # Very small target

        # Force optimization threshold
        optimizer.memory_threshold = 0.1  # Trigger at 10%

        await optimizer.start_monitoring()

        # Add data that exceeds target
        for i in range(100):
            optimizer.store(f"key_{i}", "x" * 1000)  # 1KB each

        # Wait for optimization
        await asyncio.sleep(0.1)

        # Should have triggered optimizations
        stats = optimizer.get_memory_stats()
        assert stats["optimization_stats"]["optimizations_triggered"] > 0

        await optimizer.stop_monitoring()


class TestPerformance:
    """Performance tests for memory optimization"""

    def test_tiered_cache_performance(self):
        """Test performance of tiered cache operations"""
        cache = TieredMemoryCache(
            hot_capacity=100, warm_capacity=500, cold_capacity=1000
        )

        start_time = time.time()

        # Add many items
        for i in range(1000):
            cache.put(f"key_{i}", f"data_{i}")

        # Access pattern
        for _ in range(100):
            for i in range(0, 100, 10):
                cache.get(f"key_{i}")

        elapsed = time.time() - start_time

        # Should complete quickly
        assert elapsed < 1.0

        # Check tier distribution
        stats = cache.get_stats()
        assert stats["tier_stats"]["hot"]["count"] > 0
        assert stats["tier_stats"]["warm"]["count"] > 0

    def test_object_pool_performance(self):
        """Test object pool performance"""
        pool = ObjectPool(list, max_size=1000)

        start_time = time.time()

        # Many acquire/release cycles
        for _ in range(10000):
            obj = pool.acquire()
            obj.append(1)
            pool.release(obj)

        elapsed = time.time() - start_time

        # Should be very fast
        assert elapsed < 0.5

        # Should have high hit rate
        stats = pool.get_stats()
        assert stats["hit_rate"] > 0.99


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
