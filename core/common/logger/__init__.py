"""Compat logger shim exposing getLogger(name: str=None) -> Logger."""
from __future__ import annotations

import logging
from typing import Optional

from lukhas._bridgeutils import bridge_from_candidates, safe_guard

# Try to get backend implementation
_CANDIDATES = (
    "lukhas_website.lukhas.core.common.logger",
    "labs.core.common.logger",
)
__all__, _exp = bridge_from_candidates(*_CANDIDATES)
globals().update(_exp)

# Ensure getLogger exists with proper signature
if "getLogger" not in globals():
    def getLogger(name: Optional[str] = None) -> logging.Logger:
        """Get logger with optional name (strict but forgiving)."""
        return logging.getLogger(name or "")
    __all__ = list(__all__) + ["getLogger"] if __all__ else ["getLogger"]
else:
    # Wrap existing getLogger for compat
    _orig = globals()["getLogger"]
    def getLogger(name: Optional[str] = None) -> logging.Logger:
        """Compat wrapper for getLogger."""
        try:
            return _orig(name) if name else _orig()
        except TypeError:
            # Fallback to stdlib if signature mismatch
            return logging.getLogger(name or "")

safe_guard(__name__, __all__)
