import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch

from serve.utils.cache_manager import CacheManager


class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.cache_manager = CacheManager("redis://localhost:6379")

    @patch("redis.asyncio.Redis.get", new_callable=AsyncMock)
    def test_get_cache_hit(self, mock_get):
        async def run_test():
            mock_get.return_value = json.dumps({"foo": "bar"})
            result = await self.cache_manager.get("test_key")
            self.assertEqual(result, {"foo": "bar"})
            mock_get.assert_awaited_once_with("test_key")

        asyncio.run(run_test())

    @patch("redis.asyncio.Redis.get", new_callable=AsyncMock)
    def test_get_cache_miss(self, mock_get):
        async def run_test():
            mock_get.return_value = None
            result = await self.cache_manager.get("test_key")
            self.assertIsNone(result)
            mock_get.assert_awaited_once_with("test_key")

        asyncio.run(run_test())

    @patch("redis.asyncio.Redis.setex", new_callable=AsyncMock)
    def test_set(self, mock_setex):
        async def run_test():
            await self.cache_manager.set("test_key", {"foo": "bar"}, ttl=60)
            mock_setex.assert_awaited_once_with(
                "test_key", 60, json.dumps({"foo": "bar"})
            )

        asyncio.run(run_test())

    @patch("redis.asyncio.Redis.delete", new_callable=AsyncMock)
    @patch("redis.asyncio.Redis.scan_iter")
    def test_invalidate(self, mock_scan_iter, mock_delete):
        async def async_iterator_mock(items):
            for item in items:
                yield item

        async def run_test():
            mock_scan_iter.return_value = async_iterator_mock(["key1", "key2"])
            await self.cache_manager.invalidate("test_pattern")
            mock_delete.assert_awaited_once_with("key1", "key2")

        asyncio.run(run_test())

    @patch(
        "serve.utils.cache_manager.CacheManager.invalidate", new_callable=AsyncMock
    )
    def test_clear_user_cache(self, mock_invalidate):
        async def run_test():
            await self.cache_manager.clear_user_cache("test_user")
            mock_invalidate.assert_awaited_once_with("user:test_user:*")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
