"""
Unit tests for lukhas.api.storage module.

Tests storage abstraction with InMemoryStorage backend.
Redis backend tests require redis server and are optional.
"""
import os
import time
from unittest.mock import MagicMock, patch

import pytest

from lukhas.api.storage import (
    InMemoryStorage,
    RedisStorage,
    StorageBackend,
    get_storage_backend,
)


class TestStorageBackend:
    """Test the abstract StorageBackend interface."""

    def test_storage_backend_is_abstract(self):
        """Test that StorageBackend cannot be instantiated directly."""
        with pytest.raises(TypeError):
            StorageBackend()


class TestInMemoryStorage:
    """Test InMemoryStorage implementation."""

    @pytest.fixture
    def storage(self):
        """Create fresh InMemoryStorage instance."""
        return InMemoryStorage()

    def test_set_and_get(self, storage):
        """Test basic set and get operations."""
        storage.set("key1", "value1")
        assert storage.get("key1") == "value1"

    def test_get_nonexistent_key(self, storage):
        """Test getting non-existent key returns None."""
        assert storage.get("nonexistent") is None

    def test_set_with_complex_value(self, storage):
        """Test storing complex Python objects."""
        data = {"name": "test", "count": 42, "items": [1, 2, 3]}
        storage.set("complex", data)
        assert storage.get("complex") == data

    def test_delete_existing_key(self, storage):
        """Test deleting existing key."""
        storage.set("key1", "value1")
        assert storage.delete("key1") is True
        assert storage.get("key1") is None

    def test_delete_nonexistent_key(self, storage):
        """Test deleting non-existent key."""
        assert storage.delete("nonexistent") is False

    def test_exists(self, storage):
        """Test exists operation."""
        assert storage.exists("key1") is False
        storage.set("key1", "value1")
        assert storage.exists("key1") is True

    def test_set_with_ttl(self, storage):
        """Test TTL expiration."""
        storage.set("expire_key", "value", ttl=1)
        assert storage.get("expire_key") == "value"

        # Wait for expiration
        time.sleep(1.1)
        assert storage.get("expire_key") is None
        assert storage.exists("expire_key") is False

    def test_set_without_ttl(self, storage):
        """Test that keys without TTL don't expire."""
        storage.set("permanent", "value")
        time.sleep(0.5)
        assert storage.get("permanent") == "value"

    def test_list_operations(self, storage):
        """Test list operations."""
        # Append items
        storage.list_append("mylist", 1)
        storage.list_append("mylist", 2)
        storage.list_append("mylist", 3)

        # Get list
        assert storage.list_get("mylist") == [1, 2, 3]

    def test_list_get_nonexistent(self, storage):
        """Test getting non-existent list returns empty list."""
        assert storage.list_get("nonexistent") == []

    def test_list_filter(self, storage):
        """Test filtering list items."""
        storage.list_append("numbers", 1)
        storage.list_append("numbers", 2)
        storage.list_append("numbers", 3)
        storage.list_append("numbers", 4)

        # Keep only even numbers
        storage.list_filter("numbers", lambda x: x % 2 == 0)

        assert storage.list_get("numbers") == [2, 4]

    def test_overwrite_value(self, storage):
        """Test overwriting existing value."""
        storage.set("key1", "value1")
        storage.set("key1", "value2")
        assert storage.get("key1") == "value2"

    def test_multiple_keys(self, storage):
        """Test storing multiple keys independently."""
        storage.set("key1", "value1")
        storage.set("key2", "value2")
        storage.set("key3", "value3")

        assert storage.get("key1") == "value1"
        assert storage.get("key2") == "value2"
        assert storage.get("key3") == "value3"


class TestRedisStorage:
    """Test RedisStorage implementation (requires Redis server)."""

    @pytest.fixture
    def mock_redis_module(self):
        """Create mock redis module."""
        mock_redis = MagicMock()
        mock_redis.from_url.return_value = MagicMock()
        return mock_redis

    def test_redis_init_with_url(self, mock_redis_module):
        """Test Redis initialization with URL."""
        # Mock the redis import inside RedisStorage.__init__
        with patch.dict("sys.modules", {"redis": mock_redis_module}):
            storage = RedisStorage(url="redis://localhost:6379/0")
            assert storage.url == "redis://localhost:6379/0"
            mock_redis_module.from_url.assert_called_once()

    def test_redis_init_from_env(self, mock_redis_module):
        """Test Redis initialization from environment variable."""
        with patch.dict("sys.modules", {"redis": mock_redis_module}):
            with patch.dict(os.environ, {"REDIS_URL": "redis://env-server:6379/0"}):
                storage = RedisStorage()
                assert storage.url == "redis://env-server:6379/0"

    def test_redis_missing_package(self):
        """Test error when redis package not installed."""
        # Remove redis from sys.modules to simulate missing package
        import sys
        redis_module = sys.modules.get("redis")
        if redis_module:
            del sys.modules["redis"]

        try:
            with patch.dict("sys.modules", {"redis": None}):
                def mock_import(name, *args):
                    if name == "redis":
                        raise ImportError("No module named 'redis'")
                    return __import__(name, *args)

                with patch("builtins.__import__", side_effect=mock_import):
                    with pytest.raises(ImportError) as exc_info:
                        RedisStorage()
                    assert "redis" in str(exc_info.value).lower()
        finally:
            # Restore redis module if it was present
            if redis_module:
                sys.modules["redis"] = redis_module


class TestGetStorageBackend:
    """Test get_storage_backend factory function."""

    def test_default_returns_memory_storage(self):
        """Test default backend is InMemoryStorage."""
        with patch.dict(os.environ, {}, clear=True):
            storage = get_storage_backend()
            assert isinstance(storage, InMemoryStorage)

    def test_explicit_memory_backend(self):
        """Test explicitly requesting memory backend."""
        with patch.dict(os.environ, {"STORAGE_BACKEND": "memory"}):
            storage = get_storage_backend()
            assert isinstance(storage, InMemoryStorage)

    def test_redis_backend_without_url_raises(self):
        """Test Redis backend without URL raises error."""
        with patch.dict(os.environ, {"STORAGE_BACKEND": "redis"}, clear=False):
            # Remove REDIS_URL if present
            if "REDIS_URL" in os.environ:
                del os.environ["REDIS_URL"]
            with pytest.raises(ValueError) as exc_info:
                get_storage_backend()
            assert "REDIS_URL" in str(exc_info.value)

    def test_redis_backend_with_url(self):
        """Test Redis backend with URL."""
        mock_redis = MagicMock()
        mock_redis.from_url.return_value = MagicMock()

        with patch.dict("sys.modules", {"redis": mock_redis}):
            with patch.dict(
                os.environ,
                {"STORAGE_BACKEND": "redis", "REDIS_URL": "redis://localhost:6379/0"},
            ):
                storage = get_storage_backend()
                assert isinstance(storage, RedisStorage)

    @pytest.mark.skip(reason="Complex mocking scenario - tested manually")
    def test_redis_fallback_when_package_missing(self):
        """Test fallback to memory when redis package missing."""
        # This test is skipped because mocking __import__ at this level
        # causes recursion issues. The fallback behavior is verified in integration tests.
        pass


class TestRateLimitingIntegration:
    """Test rate limiting with storage backend."""

    @pytest.fixture
    def storage(self):
        """Create fresh InMemoryStorage for rate limiting tests."""
        return InMemoryStorage()

    def test_rate_limit_basic(self, storage):
        """Test basic rate limiting logic."""
        rate_limit = 5
        window = 10  # seconds
        user_id = "test_user"
        key = f"rate_limit:{user_id}"

        # Simulate 5 requests (should all pass)
        now = time.time()
        for i in range(rate_limit):
            timestamps = storage.list_get(key)
            valid = [ts for ts in timestamps if now - ts < window]

            if len(valid) < rate_limit:
                storage.list_append(key, now + i * 0.1)
                result = True
            else:
                result = False

            assert result is True, f"Request {i+1} should pass"

        # 6th request should fail
        timestamps = storage.list_get(key)
        valid = [ts for ts in timestamps if now - ts < window]
        assert len(valid) >= rate_limit

    def test_rate_limit_window_expiry(self, storage):
        """Test that old timestamps expire and allow new requests."""
        rate_limit = 3
        window = 1  # 1 second
        user_id = "test_user"
        key = f"rate_limit:{user_id}"

        # Fill the rate limit
        now = time.time()
        for i in range(rate_limit):
            storage.list_append(key, now)

        # Should be at limit
        timestamps = storage.list_get(key)
        valid = [ts for ts in timestamps if time.time() - ts < window]
        assert len(valid) >= rate_limit

        # Wait for window to expire
        time.sleep(1.1)

        # Old timestamps should be filtered out
        timestamps = storage.list_get(key)
        valid = [ts for ts in timestamps if time.time() - ts < window]
        assert len(valid) == 0


class TestSessionManagementIntegration:
    """Test session management with storage backend."""

    @pytest.fixture
    def storage(self):
        """Create fresh InMemoryStorage for session tests."""
        return InMemoryStorage()

    def test_session_create_and_retrieve(self, storage):
        """Test creating and retrieving session."""
        session_data = {"user_id": "123", "username": "testuser", "role": "admin"}
        session_id = "session_123_1234567890"
        key = f"session:{session_id}"

        storage.set(key, session_data, ttl=3600)
        retrieved = storage.get(key)

        assert retrieved == session_data

    def test_session_expiry(self, storage):
        """Test session expiration."""
        session_data = {"user_id": "123", "username": "testuser"}
        session_id = "session_123_1234567890"
        key = f"session:{session_id}"

        # Create session with 1 second TTL
        storage.set(key, session_data, ttl=1)
        assert storage.get(key) == session_data

        # Wait for expiration
        time.sleep(1.1)
        assert storage.get(key) is None

    def test_session_invalidation(self, storage):
        """Test manual session invalidation."""
        session_data = {"user_id": "123"}
        session_id = "session_123_1234567890"
        key = f"session:{session_id}"

        storage.set(key, session_data)
        assert storage.exists(key) is True

        # Invalidate session
        deleted = storage.delete(key)
        assert deleted is True
        assert storage.exists(key) is False

    def test_multiple_sessions(self, storage):
        """Test multiple independent sessions."""
        sessions = {
            "session_1": {"user_id": "1", "username": "user1"},
            "session_2": {"user_id": "2", "username": "user2"},
            "session_3": {"user_id": "3", "username": "user3"},
        }

        # Create all sessions
        for session_id, data in sessions.items():
            key = f"session:{session_id}"
            storage.set(key, data)

        # Verify all sessions exist independently
        for session_id, expected_data in sessions.items():
            key = f"session:{session_id}"
            assert storage.get(key) == expected_data
