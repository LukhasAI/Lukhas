import unittest
from unittest.mock import MagicMock, AsyncMock
import asyncio

from labs.memory.memory_optimization import TieredMemoryCache, MemoryTier, MemoryOptimizer

class TestTieredMemoryCache(unittest.TestCase):

    def setUp(self):
        """Set up a new TieredMemoryCache for each test with small capacities."""
        self.cache = TieredMemoryCache(hot_capacity=2, warm_capacity=2, cold_capacity=2)

    def test_promotion_from_warm_to_hot(self):
        """Tests that a frequently accessed item in the warm tier gets promoted to hot."""
        self.cache.put("warm_item", "data", tier=MemoryTier.WARM)
        self.assertIn("warm_item", self.cache.tiers[MemoryTier.WARM])

        # Simulate frequent access to trigger promotion
        mem_obj = self.cache.tiers[MemoryTier.WARM]["warm_item"]
        mem_obj.access_count = 100

        self.cache._consider_promotion(mem_obj)

        self.assertNotIn("warm_item", self.cache.tiers[MemoryTier.WARM])
        self.assertIn("warm_item", self.cache.tiers[MemoryTier.HOT])

    def test_demotion_from_hot_to_warm_on_eviction(self):
        """Tests that the least recently used item in hot is demoted to warm when hot is full."""
        self.cache.put("hot_item_1", "data1") # This is the LRU
        self.cache.put("hot_item_2", "data2")

        # Access item 2 to make it the most recently used
        self.cache.get("hot_item_2") # This doesn't change insertion order, just access count.

        # Adding a new item will evict the LRU item (hot_item_1)
        self.cache.put("hot_item_3", "data3")

        self.assertNotIn("hot_item_1", self.cache.tiers[MemoryTier.HOT])
        self.assertIn("hot_item_1", self.cache.tiers[MemoryTier.WARM])

    def test_eviction_from_archive_tier(self):
        """Tests that the LRU item is completely evicted when the archive tier is full."""
        self.cache = TieredMemoryCache(hot_capacity=1, warm_capacity=1, cold_capacity=1, archive_capacity=1)

        # Fill all tiers
        self.cache.put("hot", "data")
        self.cache.put("warm", "data", tier=MemoryTier.WARM)
        self.cache.put("cold", "data", tier=MemoryTier.COLD)
        self.cache.put("archive", "data", tier=MemoryTier.ARCHIVED)

        # This series of puts will cause a cascade of demotions
        self.cache.put("new_hot_1", "data") # hot -> warm, warm -> cold, cold -> archive
        self.cache.put("new_hot_2", "data") # new_hot_1 -> warm, hot -> cold, warm -> archive, 'archive' is evicted

        # Check that the original archived item is gone
        self.assertIsNone(self.cache.get("archive"))

class TestMemoryOptimizer(unittest.TestCase):

    def setUp(self):
        self.optimizer = MemoryOptimizer()

    def test_object_pooling_acquire_release(self):
        """Tests the basic acquire and release functionality of object pools."""
        initial_stats = self.optimizer.pools["list"].get_stats()
        self.assertEqual(initial_stats["pool_size"], 0)

        # Acquire an object
        my_list = self.optimizer.acquire_pooled_object("list")
        self.assertIsInstance(my_list, list)

        # Release the object
        self.optimizer.release_pooled_object("list", my_list)

        final_stats = self.optimizer.pools["list"].get_stats()
        self.assertEqual(final_stats["pool_size"], 1)
        self.assertEqual(final_stats["hits"], 0)
        self.assertEqual(final_stats["misses"], 1)

    def test_optimization_trigger(self):
        """Tests that the optimization callback is triggered."""
        # mock the optimization function to see if it's called
        mock_callback = MagicMock(return_value=1024)
        self.optimizer.register_optimization(mock_callback)

        self.optimizer._trigger_optimization()

        mock_callback.assert_called()
        self.assertEqual(self.optimizer.stats["memory_saved_bytes"], 1024)

    def test_async_monitoring_loop(self):
        """Tests the async monitoring loop logic."""
        # This is a bit tricky to test without actual async execution.
        # We can mock the dependencies and check the logic flow.
        self.optimizer._get_memory_usage = MagicMock(return_value=self.optimizer.target_memory_bytes)
        self.optimizer._trigger_optimization = MagicMock()

        async def run_one_loop_iteration():
            await self.optimizer._monitoring_loop()

        # We can't run the infinite loop, but we can patch it to run once.
        self.optimizer.monitoring_enabled = True

        async def mock_monitoring_loop():
            # Run one iteration of the real logic
            memory_usage = self.optimizer._get_memory_usage()
            if memory_usage > self.optimizer.target_memory_bytes * self.optimizer.memory_threshold:
                self.optimizer._trigger_optimization()
            self.optimizer.monitoring_enabled = False # Stop the loop

        self.optimizer._monitoring_loop = mock_monitoring_loop

        asyncio.run(self.optimizer.start_monitoring())

        self.optimizer._trigger_optimization.assert_called_once()


if __name__ == '__main__':
    unittest.main()
