import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from serve.middleware.cache_middleware import CacheMiddleware
from serve.utils.cache_manager import CacheManager
from starlette.testclient import TestClient


class TestCacheMiddleware(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.cache_manager = MagicMock(spec=CacheManager)
        self.app.add_middleware(CacheMiddleware, cache_manager=self.cache_manager)

        @self.app.get("/test")
        async def test_endpoint(request: Request):
            return JSONResponse({"foo": "bar"})

        @self.app.post("/test")
        async def test_post_endpoint(request: Request):
            return JSONResponse({"status": "ok"})

        self.client = TestClient(self.app)

    def test_cache_miss(self):
        async def run_test():
            self.cache_manager.get = AsyncMock(return_value=None)
            self.cache_manager.set = AsyncMock()

            response = self.client.get("/test")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"foo": "bar"})
            self.cache_manager.get.assert_called_once()
            self.cache_manager.set.assert_called_once()

        asyncio.run(run_test())

    def test_cache_hit(self):
        async def run_test():
            self.cache_manager.get = AsyncMock(return_value={"foo": "bar"})
            self.cache_manager.set = AsyncMock()

            response = self.client.get("/test")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"foo": "bar"})
            self.cache_manager.get.assert_called_once()
            self.cache_manager.set.assert_not_called()

        asyncio.run(run_test())

    def test_cache_invalidation(self):
        async def run_test():
            self.cache_manager.invalidate = AsyncMock()

            response = self.client.post("/test")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "ok"})
            self.cache_manager.invalidate.assert_called_once_with("/test")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
