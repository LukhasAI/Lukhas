"""Shim: core.registry → prefer package `core.registry`, with lazy labs fallback.

Avoid import-time dependency on `labs.core.registry`. This module provides a
lazy attribute proxy for labs fallback while preferring the in-repo package.
"""

from __future__ import annotations

import importlib
from typing import Any

# Prefer the in-repo package if available (no labs edge)
try:  # pragma: no cover
    from core.registry import *  # type: ignore  # noqa: F403,F401

    _HAS_PRIMARY = True
except Exception:  # pragma: no cover
    _HAS_PRIMARY = False


def __getattr__(name: str) -> Any:  # pragma: no cover
    try:
        mod = importlib.import_module("labs.core.registry")
        return getattr(mod, name)
    except Exception as e:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}: {e}") from e


# No __all__ exposure for labs fallback to discourage star imports.
