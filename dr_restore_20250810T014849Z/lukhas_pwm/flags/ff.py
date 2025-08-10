import os
import time
from typing import Optional


class Flags:
    """Tiny env-backed feature flag reader.
    Reads FLAG_* env vars and caches for 5s.
    True values: 1, true, on (case-insensitive)
    """

    _cache = {}
    _ts = 0.0

    @classmethod
    def _refresh(cls):
        cls._cache = {
            k[5:]: v.lower() in ("1", "true", "on")
            for k, v in os.environ.items()
            if k.startswith("FLAG_")
        }
        cls._ts = time.time()

    @classmethod
    def get(cls, name: str, default: bool = False) -> bool:
        """Return boolean flag value.
        Prefers direct env read for immediacy; falls back to a cached snapshot.
        """
        raw = os.getenv(f"FLAG_{name}")
        if raw is not None:
            return raw.strip().lower() in ("1", "true", "on")
        # Fallback to cached snapshot for non-existent flags (refresh occasionally).
        now = time.time()
        if now - cls._ts > 5:
            cls._refresh()
        return cls._cache.get(name, default)

    @classmethod
    def get_str(cls, name: str, default: Optional[str] = None) -> Optional[str]:
        """Return string flag value directly from env (no caching)."""
        return os.getenv(f"FLAG_{name}", default)
