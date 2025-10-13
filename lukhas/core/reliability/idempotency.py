from abc import ABC, abstractmethod
import hashlib
import time
from typing import Dict, Tuple, Optional

class IdempotencyStore(ABC):
    """Abstract base class for idempotency stores."""

    @abstractmethod
    def get(self, key: str) -> Optional[Tuple[int, Dict, bytes, str]]:
        """
        Gets a cached response and its body hash.
        Returns a tuple of (status_code, headers, body, body_sha256) or None.
        """
        pass

    @abstractmethod
    def put(self, key: str, status: int, headers: Dict, body: bytes) -> None:
        """
        Stores a response. The implementation should hash the body.
        """
        pass

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

    def get(self, key: str) -> Optional[Tuple[int, Dict, bytes, str]]:
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
