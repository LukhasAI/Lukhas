"""Shim: core.identity → identity (preferred) with lazy labs fallback.

This shim avoids importing `labs.identity` at import time to respect lane
boundaries. If attributes are accessed that aren't provided by the primary
`identity` package, they are lazily resolved from `labs.identity`.
"""

from __future__ import annotations

import importlib
from typing import Any

# Prefer the top-level identity package if available (no labs edge)
try:  # pragma: no cover - import-time availability
    from identity import *  # type: ignore  # noqa: F403,F401

    _HAS_PRIMARY = True
except Exception:  # pragma: no cover
    _HAS_PRIMARY = False


def __getattr__(name: str) -> Any:  # pragma: no cover - lazy path
    """Lazy-load attributes from labs.identity only when accessed."""
    try:
        mod = importlib.import_module("labs.identity")
        return getattr(mod, name)
    except Exception as e:  # align with Python attribute semantics
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}: {e}") from e


# Intentionally omit __all__ for labs fallback to discourage star imports.
