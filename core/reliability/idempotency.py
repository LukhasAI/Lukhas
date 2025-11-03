"""
Idempotency-Key support for safe request replays.

Unified approach combining Jules' class-based architecture with Phase 3 contracts.
Supports both in-memory (dev) and Redis (production) backends.

Features:
- Abstract Store protocol for extensibility
- In-memory store with TTL (300s default)
- Redis backend via jules' implementation
- Per-tenant keying with hashed tokens (non-PII)
- Backward-compatible function shims

Usage:
    # New class-based API
    store = InMemoryIdempotencyStore(ttl_seconds=300)
    key = store.key("/v1/responses", "tenant123", "idem-key-456")
    cached = store.get(key)

    # Legacy function API (back-compat)
    from core.reliability.idempotency import build_cache_key, get, put
    key = build_cache_key("POST", "/v1/responses", "idem-key", principal="user-token")
    cached = get(key)
"""

from __future__ import annotations

import hashlib
import os
import time
from typing import Dict, Protocol, Tuple


class IdempotencyStore(Protocol):
    """Abstract base class for idempotency stores."""

    def get(self, key: str) -> Tuple[int, Dict, bytes, str] | None:
        """
        Gets a cached response and its body hash.
        Returns a tuple of (status_code, headers, body, body_sha256) or None.
        """
        ...

    def put(self, key: str, status: int, headers: Dict, body: bytes) -> None:
        """
        Stores a response. The implementation should hash the body.
        """
        ...

    @staticmethod
    def _hash_body(body: bytes) -> str:
        return hashlib.sha256(body or b"").hexdigest()

    def key(self, route: str, tenant: str, idem_key: str) -> str:
        """
        Constructs a key for the store.
        Note: Does not include body hash, as per RFC-0007.
        """
        return f"idem:{route}:{tenant}:{idem_key}"


class InMemoryIdempotencyStore(IdempotencyStore):
    """In-memory idempotency store for testing and single-replica deployments."""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Tuple[float, int, Dict, bytes, str]] = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Tuple[int, Dict, bytes, str] | None:
        item = self._cache.get(key)
        if not item:
            return None

        ts, status, headers, body, body_sha256 = item
        if time.time() - ts > self.ttl:
            self._cache.pop(key, None)
            return None

        return status, headers, body, body_sha256

    def put(self, key: str, status: int, headers: Dict, body: bytes) -> None:
        body_sha256 = self._hash_body(body)
        self._cache[key] = (time.time(), status, headers, body, body_sha256)

    def clear(self) -> None:
        """Clear all cached responses (useful for testing)."""
        self._cache.clear()


# Try to import Jules' Redis store if available
try:
    from core.reliability.idempotency_redis import RedisIdempotencyStore
except ImportError:  # pragma: no cover
    RedisIdempotencyStore = None  # type: ignore


def _hash_token(tok: str) -> str:
    """Hash token to 16-hex digest for compact non-PII keys."""
    return hashlib.sha256(tok.encode()).hexdigest()[:16]


def build_cache_key(method: str, path: str, idempotency_key: str, principal: str = "anon") -> str:
    """
    Build cache key with hashed principal to avoid raw tokens in memory/backends.

    Args:
        method: HTTP method (POST, PUT, PATCH)
        path: Request path (e.g., "/v1/responses")
        idempotency_key: Client-provided idempotency key
        principal: Token or principal identifier (will be hashed)

    Returns:
        Cache key: "{method}:{path}:{hashed_principal}:{idempotency_key}"
    """
    return f"{method}:{path}:{_hash_token(principal)}:{idempotency_key}"


def _select_store() -> IdempotencyStore:
    """Select idempotency backend from environment."""
    backend = os.getenv("LUKHAS_IDEMPOTENCY_BACKEND", "memory").lower()
    if backend == "redis" and RedisIdempotencyStore:
        return RedisIdempotencyStore.from_env()  # Jules' factory
    return InMemoryIdempotencyStore()


# Global store instance
_STORE: IdempotencyStore = _select_store()


# Back-compat function shims (keeps older call sites working)
def get(key: str) -> Tuple[int, bytes, str] | None:
    """
    Legacy API: Retrieve cached response if not expired.

    Returns:
        (status, body_bytes, content_type) tuple or None

    Note: Simplified signature for back-compat. Use IdempotencyStore directly for full API.
    """
    cached = _STORE.get(key)
    if not cached:
        return None
    status, headers, body, _body_sha = cached
    content_type = headers.get("content-type", "application/json")
    return status, body, content_type


def put(key: str, status: int, body: bytes, content_type: str) -> None:
    """
    Legacy API: Cache response for future replays.

    Args:
        key: Cache key from build_cache_key()
        status: HTTP status code
        body: Response body bytes
        content_type: Content-Type header value

    Note: Simplified signature for back-compat. Use IdempotencyStore directly for full API.
    """
    headers = {"content-type": content_type}
    _STORE.put(key, status, headers, body)


def clear() -> None:
    """Clear all cached responses (useful for testing)."""
    if hasattr(_STORE, "clear"):
        _STORE.clear()
