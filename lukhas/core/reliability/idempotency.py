"""
Idempotency-Key support for safe request replays.

Implements in-memory cache for idempotent requests:
- Cache keyed by (route, Idempotency-Key, body-hash)
- TTL of 24 hours
- Returns cached response for matching replays

Phase 3: Added for production reliability.
"""
import time
import hashlib
from typing import Dict, Tuple, Optional

_TTL = 24 * 3600  # 24h
# key -> (ts, status, body_bytes, content_type)
_cache: Dict[str, Tuple[float, int, bytes, str]] = {}


def _hash(b: bytes) -> str:
    """Compute short hash of request body."""
    return hashlib.sha256(b).hexdigest()[:16]


def cache_key(route: str, idem_key: str, body: bytes) -> str:
    """
    Generate cache key for idempotent request.

    Args:
        route: API route path
        idem_key: Idempotency-Key header value
        body: Request body bytes

    Returns:
        Cache key string
    """
    return f"{route}:{idem_key}:{_hash(body)}"


def get(key: str) -> Optional[Tuple[int, bytes, str]]:
    """
    Retrieve cached response if not expired.

    Args:
        key: Cache key from cache_key()

    Returns:
        (status, body_bytes, content_type) tuple or None if not cached/expired
    """
    item = _cache.get(key)
    if not item:
        return None

    ts, status, body, ctype = item
    if time.time() - ts > _TTL:
        _cache.pop(key, None)
        return None

    return status, body, ctype


def put(key: str, status: int, body: bytes, content_type: str) -> None:
    """
    Cache response for future replays.

    Args:
        key: Cache key from cache_key()
        status: HTTP status code
        body: Response body bytes
        content_type: Content-Type header value
    """
    _cache[key] = (time.time(), status, body, content_type)


def clear() -> None:
    """Clear all cached responses (useful for testing)."""
    _cache.clear()
