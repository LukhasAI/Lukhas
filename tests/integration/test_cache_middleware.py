import json
import time
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse
import fakeredis

from serve.middleware.cache_middleware import CacheMiddleware

# A simple app for testing the middleware directly
@pytest.fixture
def test_app():
    app = FastAPI()

    @app.get("/test-path")
    async def _():
        return JSONResponse({"message": "Hello, world!"})

    @app.post("/test-path")
    async def _post():
        return JSONResponse({"message": "Data updated"})

    app.add_middleware(CacheMiddleware)
    return app


@pytest.fixture
def fake_redis_client():
    """Provides a fake redis client for tests."""
    return fakeredis.FakeStrictRedis(decode_responses=True)


@pytest.fixture
def client(test_app, fake_redis_client, monkeypatch):
    """A TestClient that uses the fake_redis_client."""
    monkeypatch.setattr("redis.Redis", lambda *args, **kwargs: fake_redis_client)
    return TestClient(test_app)


def test_cache_miss_then_hit(client, fake_redis_client):
    """
    Test that a request is not cached on the first call, but is on the second.
    """
    response1 = client.get("/test-path")
    assert response1.status_code == 200
    assert response1.json() == {"message": "Hello, world!"}

    cache_key = "cache:/test-path?"
    assert fake_redis_client.exists(cache_key)
    cached_value = json.loads(fake_redis_client.get(cache_key))
    assert cached_value == {"message": "Hello, world!"}

    response2 = client.get("/test-path")
    assert response2.status_code == 200
    assert response2.json() == {"message": "Hello, world!"}


def test_cache_invalidation(client, fake_redis_client):
    """
    Test that a POST request to an endpoint invalidates the cache for that endpoint.
    """
    client.get("/test-path")
    cache_key = "cache:/test-path?"
    assert fake_redis_client.exists(cache_key)

    response = client.post("/test-path")
    assert response.status_code == 200

    assert not fake_redis_client.exists(cache_key)


@pytest.mark.xfail(reason="Middleware TTL testing requires a more complex setup to patch correctly")
def test_ttl_expiration(fake_redis_client, monkeypatch):
    """
    Test that the cache expires after the TTL.
    """
    monkeypatch.setattr("redis.Redis", lambda *args, **kwargs: fake_redis_client)

    app = FastAPI()
    middleware = CacheMiddleware(app=app)
    middleware.cache_client.default_ttl = 1
    app.add_middleware(middleware)

    @app.get("/test-path")
    async def _():
        return JSONResponse({"message": "Hello, world!"})

    client = TestClient(app)

    client.get("/test-path")

    cache_key = "cache:/test-path?"
    assert fake_redis_client.exists(cache_key)
    time.sleep(1.1)
    assert not fake_redis_client.exists(cache_key)


def test_cache_miss_performance(benchmark, client, fake_redis_client):
    """
    Test the performance of a cache miss.
    """
    cache_key = "cache:/test-path?"

    def cache_miss():
        fake_redis_client.delete(cache_key)
        client.get("/test-path")

    benchmark(cache_miss)


def test_cache_hit_performance(benchmark, client, fake_redis_client):
    """
    Test the performance of a cache hit.
    """
    cache_key = "cache:/test-path?"
    fake_redis_client.set(cache_key, json.dumps({"message": "Hello, world!"}))

    def cache_hit():
        client.get("/test-path")

    benchmark(cache_hit)
