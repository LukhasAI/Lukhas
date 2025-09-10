"""Safe-mode symbolic filter logic.

#REVIVED_25_07_2025
"""
from __future__ import annotations

from collections.abc import Iterable

# ΛTAG: ethics_fallback


class FallbackEthicsLayer:
    """Simple symbol filter enforcing safe-mode policies."""

    def __init__(self, banned_symbols: Iterable[str] | None = None) -> None:
        self.banned = set(banned_symbols or [])

    def is_allowed(self, symbol: str) -> bool:
        """Return True if symbol passes the fallback ethics check."""
        return symbol not in self.banned
