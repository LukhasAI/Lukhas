"""Bridge for cognition internals -> candidate.consciousness.cognitive."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from 'consciousness.cognitive' is deprecated; " "prefer `consciousness` public API.",
    DeprecationWarning,
    stacklevel=2,
)

# Minimal stub to unblock collection
__all__ = []
