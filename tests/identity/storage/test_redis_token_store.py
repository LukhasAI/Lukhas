"""Comprehensive tests for RedisTokenStore.

Tests cover:
- Token storage with TTL
- Token retrieval and expiry
- Token revocation (<10ms target)
- RFC 7662 introspection
- Concurrent operations
- Health checks
"""

import asyncio
import time
from datetime import datetime, timedelta

import pytest
import redis

from core.identity.storage.redis_token_store import RedisTokenStore, TokenMetadata


@pytest.fixture
def redis_url():
    """Redis connection URL for tests."""
    # Use separate DB for tests to avoid polluting production data
    return "redis://localhost:6379/15"


@pytest.fixture
async def token_store(redis_url):
    """RedisTokenStore instance for testing."""
    store = RedisTokenStore(redis_url=redis_url)

    # Clear test database before each test
    store.client.flushdb()

    yield store

    # Cleanup
    store.client.flushdb()
    store.close()


@pytest.mark.asyncio
async def test_store_and_retrieve_token(token_store):
    """Test basic token storage and retrieval."""
    jti = "tok_test_001"
    metadata = {
        "sub": "usr_alice",
        "scope": "openid profile",
        "client_id": "lukhas_web",
        "lid_type": "USR",
    }

    # Store token
    success = await token_store.store_token(jti, metadata, ttl_seconds=3600)
    assert success is True

    # Retrieve token
    token_data = await token_store.get_token(jti)
    assert token_data is not None
    assert token_data.jti == jti
    assert token_data.sub == "usr_alice"
    assert token_data.scope == "openid profile"
    assert token_data.active is True
    assert token_data.lid_type == "USR"


@pytest.mark.asyncio
async def test_token_ttl_expiry(token_store):
    """Test that tokens expire after TTL."""
    jti = "tok_expire_001"
    metadata = {"sub": "usr_bob", "scope": "openid"}

    # Store token with 2-second TTL
    await token_store.store_token(jti, metadata, ttl_seconds=2)

    # Token should exist immediately
    token_data = await token_store.get_token(jti)
    assert token_data is not None

    # Wait for expiry
    await asyncio.sleep(3)

    # Token should be gone
    token_data = await token_store.get_token(jti)
    assert token_data is None


@pytest.mark.asyncio
async def test_token_revocation(token_store):
    """Test immediate token revocation (<10ms target)."""
    jti = "tok_revoke_001"
    metadata = {"sub": "usr_charlie", "scope": "openid"}

    # Store token
    await token_store.store_token(jti, metadata, ttl_seconds=3600)

    # Verify token exists
    assert await token_store.get_token(jti) is not None

    # Revoke token (measure latency)
    start = time.perf_counter()
    success = await token_store.revoke_token(jti, reason="user_logout")
    latency_ms = (time.perf_counter() - start) * 1000

    assert success is True
    assert latency_ms < 10, f"Revocation took {latency_ms:.2f}ms (target: <10ms)"

    # Token should be revoked
    assert await token_store.is_revoked(jti) is True

    # get_token should return None for revoked tokens
    token_data = await token_store.get_token(jti)
    assert token_data is None

    # Revocation info should be available
    revocation_info = await token_store.get_revocation_info(jti)
    assert revocation_info is not None
    assert revocation_info["reason"] == "user_logout"


@pytest.mark.asyncio
async def test_introspect_active_token(token_store):
    """Test RFC 7662 token introspection for active tokens."""
    jti = "tok_introspect_001"
    metadata = {
        "sub": "usr_dave",
        "scope": "openid profile email",
        "client_id": "lukhas_mobile",
        "lid_type": "USR",
    }

    # Store token
    await token_store.store_token(jti, metadata, ttl_seconds=3600)

    # Introspect
    response = await token_store.introspect_token(jti)

    # Verify RFC 7662 compliance
    assert response["active"] is True
    assert response["sub"] == "usr_dave"
    assert response["scope"] == "openid profile email"
    assert response["client_id"] == "lukhas_mobile"
    assert "exp" in response
    assert "iat" in response
    assert response["token_type"] == "Bearer"
    assert response["lid_type"] == "USR"


@pytest.mark.asyncio
async def test_introspect_revoked_token(token_store):
    """Test RFC 7662 introspection for revoked tokens."""
    jti = "tok_introspect_revoked"
    metadata = {"sub": "usr_eve", "scope": "openid"}

    # Store and revoke token
    await token_store.store_token(jti, metadata, ttl_seconds=3600)
    await token_store.revoke_token(jti)

    # Introspect
    response = await token_store.introspect_token(jti)

    # Revoked tokens return only {"active": false}
    assert response == {"active": False}


@pytest.mark.asyncio
async def test_introspect_nonexistent_token(token_store):
    """Test introspection of non-existent token."""
    response = await token_store.introspect_token("tok_does_not_exist")
    assert response == {"active": False}


@pytest.mark.asyncio
async def test_concurrent_token_operations(token_store):
    """Test thread-safe concurrent token operations."""
    # Create multiple tokens concurrently
    tasks = []
    for i in range(50):
        jti = f"tok_concurrent_{i:03d}"
        metadata = {"sub": f"usr_user{i}", "scope": "openid"}
        tasks.append(token_store.store_token(jti, metadata, ttl_seconds=60))

    results = await asyncio.gather(*tasks)
    assert all(results), "Some concurrent stores failed"

    # Retrieve all tokens concurrently
    retrieve_tasks = [
        token_store.get_token(f"tok_concurrent_{i:03d}") for i in range(50)
    ]
    tokens = await asyncio.gather(*retrieve_tasks)

    # All tokens should exist
    assert all(t is not None for t in tokens)
    assert len(tokens) == 50


@pytest.mark.asyncio
async def test_revocation_ttl(token_store):
    """Test that revocation records expire after TTL."""
    jti = "tok_revoke_ttl"
    metadata = {"sub": "usr_frank", "scope": "openid"}

    # Store and revoke with short TTL
    await token_store.store_token(jti, metadata, ttl_seconds=60)
    await token_store.revoke_token(jti, reason="test", ttl_seconds=2)

    # Revocation should be active immediately
    assert await token_store.is_revoked(jti) is True

    # Wait for revocation record to expire
    await asyncio.sleep(3)

    # Revocation record should be gone
    assert await token_store.is_revoked(jti) is False
    revocation_info = await token_store.get_revocation_info(jti)
    assert revocation_info is None


@pytest.mark.asyncio
async def test_health_check_healthy(token_store):
    """Test health check with healthy Redis."""
    health = token_store.health_check()
    assert health["status"] == "healthy"
    assert "pool" in health
    assert health["pool"]["max_connections"] == 50


@pytest.mark.asyncio
async def test_health_check_unhealthy():
    """Test health check with unavailable Redis."""
    # Connect to invalid Redis instance
    bad_store = RedisTokenStore(redis_url="redis://localhost:9999/0")

    health = bad_store.health_check()
    assert health["status"] == "unhealthy"
    assert "error" in health

    bad_store.close()


@pytest.mark.asyncio
async def test_token_metadata_validation(token_store):
    """Test that invalid metadata is rejected."""
    jti = "tok_invalid"

    # Missing required field 'sub'
    invalid_metadata = {"scope": "openid"}

    with pytest.raises(Exception):  # Pydantic validation error
        await token_store.store_token(jti, invalid_metadata)


@pytest.mark.asyncio
async def test_automatic_timestamps(token_store):
    """Test that iat/exp are auto-generated if not provided."""
    jti = "tok_timestamps"
    metadata = {"sub": "usr_grace", "scope": "openid"}

    now_before = int(datetime.utcnow().timestamp())

    await token_store.store_token(jti, metadata, ttl_seconds=3600)

    token_data = await token_store.get_token(jti)
    assert token_data is not None

    # Check iat is set and recent
    assert token_data.iat >= now_before
    assert token_data.iat <= int(datetime.utcnow().timestamp())

    # Check exp is iat + ttl
    expected_exp = token_data.iat + 3600
    assert abs(token_data.exp - expected_exp) <= 1  # Allow 1 second tolerance


@pytest.mark.asyncio
async def test_revoke_already_revoked_token(token_store):
    """Test revoking a token that's already revoked (idempotent)."""
    jti = "tok_double_revoke"
    metadata = {"sub": "usr_heidi", "scope": "openid"}

    await token_store.store_token(jti, metadata, ttl_seconds=3600)

    # Revoke twice
    await token_store.revoke_token(jti, reason="first_revoke")
    await token_store.revoke_token(jti, reason="second_revoke")

    # Should still be revoked
    assert await token_store.is_revoked(jti) is True

    # Revocation info should reflect latest revocation
    info = await token_store.get_revocation_info(jti)
    assert info["reason"] == "second_revoke"


@pytest.mark.asyncio
async def test_large_token_payload(token_store):
    """Test storage of tokens with large metadata."""
    jti = "tok_large"
    metadata = {
        "sub": "usr_ivan",
        "scope": " ".join([f"scope_{i}" for i in range(100)]),  # Long scope string
        "client_id": "lukhas_test",
        "lid_type": "USR",
    }

    await token_store.store_token(jti, metadata, ttl_seconds=3600)

    token_data = await token_store.get_token(jti)
    assert token_data is not None
    assert "scope_99" in token_data.scope


@pytest.mark.asyncio
async def test_cleanup_expired_noop(token_store):
    """Test that cleanup_expired is a no-op (Redis TTL handles this)."""
    # cleanup_expired should return 0 (no manual cleanup needed)
    count = await token_store.cleanup_expired()
    assert count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
