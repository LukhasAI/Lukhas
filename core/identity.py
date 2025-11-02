"""Shim: core.identity → labs.identity (lazy fallback).

This shim avoids importing `labs.identity` at import time to respect lane
boundaries. All attributes are lazily resolved from `labs.identity` on first access.

TODO: migrate to ProviderRegistry pattern for better dependency injection.
"""
from __future__ import annotations
import importlib
from typing import Any


def __getattr__(name: str) -> Any:
    """Lazy-load attributes from labs.identity only when accessed."""
    try:
        mod = importlib.import_module("labs.identity")
        return getattr(mod, name)
    except Exception as e:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}: {e}") from e


# Intentionally omit __all__ for labs fallback to discourage star imports.