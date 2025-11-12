import asyncio
import json
import time
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from fakeredis import aioredis as fake_aioredis
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient
from serve.middleware.cache_middleware import CacheMiddleware
from serve.middleware.strict_auth import StrictAuthMiddleware

# This is the fake client that the middleware will be patched to use.
fake_redis_instance = fake_aioredis.FakeRedis(decode_responses=True)

@pytest.fixture
def mock_auth_system():
    """Provides a mock auth system that can be manipulated in tests."""
    auth_system = MagicMock()
    auth_system.verify_jwt.return_value = {"user_id": "test_user"}
    return auth_system

@pytest.fixture(autouse=True)
def patch_redis_and_auth(monkeypatch, mock_auth_system):
    """Patches Redis to use our fake instance and mocks the auth system."""
    monkeypatch.setattr(
        "serve.middleware.cache_middleware.Redis",
        lambda *args, **kwargs: fake_redis_instance
    )
    monkeypatch.setattr(
        "serve.middleware.strict_auth.get_auth_system",
        lambda: mock_auth_system
    )

@pytest.fixture
def app():
    """Creates a new FastAPI app instance for each test."""
    app = FastAPI()
    # Middleware order is crucial: Auth first, then Cache
    app.add_middleware(StrictAuthMiddleware)
    app.add_middleware(CacheMiddleware)

    # Endpoint must be under /v1/ to trigger auth middleware
    @app.get("/v1/cached")
    async def get_cached_endpoint(request: Request):
        user_id = request.state.user_id
        return JSONResponse(content={"message": f"Data for {user_id}"})

    @app.post("/v1/cached")
    async def post_cached_endpoint():
        return JSONResponse(content={"message": "This should invalidate the cache."})

    return app

@pytest_asyncio.fixture
async def client(app):
    """Creates an async test client for the app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.headers["Authorization"] = "Bearer valid_token"
        yield ac

@pytest_asyncio.fixture(autouse=True)
async def clear_cache():
    """Clears the fake redis cache before and after each test."""
    await fake_redis_instance.flushdb()
    yield
    await fake_redis_instance.flushdb()

@pytest.mark.asyncio
async def test_cache_miss(client: AsyncClient):
    response = await client.get("/v1/cached")
    assert response.status_code == 200
    assert response.json() == {"message": "Data for test_user"}

    cached = await fake_redis_instance.get("cache:test_user:/v1/cached?")
    assert cached is not None
    assert json.loads(cached) == {"message": "Data for test_user"}

@pytest.mark.asyncio
async def test_cache_hit(client: AsyncClient):
    await client.get("/v1/cached")

    start_time = time.time()
    response = await client.get("/v1/cached")
    end_time = time.time()

    assert response.status_code == 200
    assert response.json() == {"message": "Data for test_user"}
    assert (end_time - start_time) < 0.01

@pytest.mark.asyncio
async def test_cache_invalidation(client: AsyncClient):
    await client.get("/v1/cached")
    assert await fake_redis_instance.get("cache:test_user:/v1/cached?") is not None

    await client.post("/v1/cached")

    cached = await fake_redis_instance.get("cache:test_user:/v1/cached?")
    assert cached is None

@pytest.mark.asyncio
async def test_ttl_expiration(client: AsyncClient):
    headers = {"X-Test-Cache-TTL": "1", "Authorization": "Bearer valid_token"}
    await client.get("/v1/cached", headers=headers)
    assert await fake_redis_instance.get("cache:test_user:/v1/cached?") is not None

    await asyncio.sleep(1.1)

    cached = await fake_redis_instance.get("cache:test_user:/v1/cached?")
    assert cached is None

@pytest.mark.asyncio
async def test_user_isolation(client: AsyncClient, mock_auth_system):
    # Request for user 1
    mock_auth_system.verify_jwt.return_value = {"user_id": "user_1"}
    response1 = await client.get("/v1/cached")
    assert response1.json() == {"message": "Data for user_1"}
    assert await fake_redis_instance.get("cache:user_1:/v1/cached?") is not None

    # Request for user 2 - should be a cache miss
    mock_auth_system.verify_jwt.return_value = {"user_id": "user_2"}
    response2 = await client.get("/v1/cached")
    assert response2.json() == {"message": "Data for user_2"}
    assert await fake_redis_instance.get("cache:user_2:/v1/cached?") is not None

    # Verify user 1's cache is untouched
    cached1 = await fake_redis_instance.get("cache:user_1:/v1/cached?")
    assert json.loads(cached1) == {"message": "Data for user_1"}
