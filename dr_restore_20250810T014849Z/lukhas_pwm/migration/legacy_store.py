from typing import Iterable, Dict, Any, Optional, Tuple, Iterator


class LegacyStore:
    """Abstract interface for the existing memory store."""

    def iter_all(self, start_after: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """Yield dicts with at least: key, value, version (int), strength (float?), meta (dict?)."""
        raise NotImplementedError

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def write(
        self, key: str, value: Any, *, version: int, strength: float, meta: Dict
    ) -> bool:
        """Return True if upserted/updated."""
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError
