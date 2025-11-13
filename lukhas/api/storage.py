"""
Storage abstractions for rate limiting and session management.

Provides pluggable storage backends:
- InMemoryStorage: Simple dict-based storage (default, single-process only)
- RedisStorage: Redis-backed storage (production-ready, multi-process/server)

Usage:
    # Auto-configure based on environment
    storage = get_storage_backend()

    # Explicit configuration
    storage = InMemoryStorage()  # Development
    storage = RedisStorage(url="redis://localhost:6379")  # Production

Environment Variables:
    REDIS_URL: Redis connection URL (e.g., "redis://localhost:6379/0")
    STORAGE_BACKEND: "memory" or "redis" (default: "memory")
"""
import json
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value with optional TTL.

        Args:
            key: Storage key
            value: Value to store
            ttl: Time-to-live in seconds (None = no expiration)
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key. Returns True if key existed."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def list_append(self, key: str, value: Any) -> None:
        """Append value to list."""
        pass

    @abstractmethod
    def list_get(self, key: str) -> List[Any]:
        """Get list values."""
        pass

    @abstractmethod
    def list_filter(self, key: str, predicate) -> None:
        """Filter list by predicate (keep items where predicate returns True)."""
        pass


class InMemoryStorage(StorageBackend):
    """
    In-memory storage backend using Python dict.

    WARNING: Not suitable for production multi-process/multi-server deployments.
    Data is not shared between processes and is lost on restart.
    """

    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    def _is_expired(self, key: str) -> bool:
        """Check if key has expired."""
        if key not in self._expiry:
            return False
        return time.time() > self._expiry[key]

    def _cleanup_expired(self, key: str) -> None:
        """Remove key if expired."""
        if self._is_expired(key):
            self._store.pop(key, None)
            self._expiry.pop(key, None)

    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        self._cleanup_expired(key)
        return self._store.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value with optional TTL."""
        self._store[key] = value
        if ttl is not None:
            self._expiry[key] = time.time() + ttl
        else:
            self._expiry.pop(key, None)

    def delete(self, key: str) -> bool:
        """Delete key."""
        existed = key in self._store
        self._store.pop(key, None)
        self._expiry.pop(key, None)
        return existed

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        self._cleanup_expired(key)
        return key in self._store

    def list_append(self, key: str, value: Any) -> None:
        """Append value to list."""
        if key not in self._store:
            self._store[key] = []
        self._store[key].append(value)

    def list_get(self, key: str) -> List[Any]:
        """Get list values."""
        self._cleanup_expired(key)
        return self._store.get(key, [])

    def list_filter(self, key: str, predicate) -> None:
        """Filter list by predicate."""
        if key in self._store:
            self._store[key] = [item for item in self._store[key] if predicate(item)]


class RedisStorage(StorageBackend):
    """
    Redis-backed storage for production deployments.

    Supports multi-process and multi-server deployments.
    Requires redis package: pip install redis
    """

    def __init__(self, url: Optional[str] = None):
        """
        Initialize Redis storage.

        Args:
            url: Redis connection URL (e.g., "redis://localhost:6379/0")
                 If None, uses REDIS_URL environment variable
        """
        try:
            import redis
        except ImportError:
            raise ImportError(
                "Redis storage requires the 'redis' package. "
                "Install with: pip install redis"
            )

        self.url = url or os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(self.url, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        value = self.client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value with optional TTL."""
        serialized = json.dumps(value)
        if ttl is not None:
            self.client.setex(key, ttl, serialized)
        else:
            self.client.set(key, serialized)

    def delete(self, key: str) -> bool:
        """Delete key."""
        return self.client.delete(key) > 0

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.client.exists(key) > 0

    def list_append(self, key: str, value: Any) -> None:
        """Append value to list."""
        self.client.rpush(key, json.dumps(value))

    def list_get(self, key: str) -> List[Any]:
        """Get list values."""
        raw_list = self.client.lrange(key, 0, -1)
        return [json.loads(item) for item in raw_list]

    def list_filter(self, key: str, predicate) -> None:
        """Filter list by predicate."""
        # Get all items
        items = self.list_get(key)
        # Filter
        filtered = [item for item in items if predicate(item)]
        # Replace list
        self.client.delete(key)
        for item in filtered:
            self.list_append(key, item)


def get_storage_backend() -> StorageBackend:
    """
    Get storage backend based on configuration.

    Checks environment variables:
    - STORAGE_BACKEND: "memory" or "redis" (default: "memory")
    - REDIS_URL: Redis connection URL (required if backend=redis)

    Returns:
        Configured storage backend instance
    """
    backend_type = os.environ.get("STORAGE_BACKEND", "memory").lower()

    if backend_type == "redis":
        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            raise ValueError(
                "REDIS_URL environment variable required when STORAGE_BACKEND=redis"
            )
        try:
            return RedisStorage(url=redis_url)
        except ImportError:
            # Redis not available, fall back to memory with warning
            import warnings

            warnings.warn(
                "Redis storage requested but redis package not installed. "
                "Falling back to InMemoryStorage. Install redis with: pip install redis",
                RuntimeWarning,
            )
            return InMemoryStorage()

    return InMemoryStorage()
