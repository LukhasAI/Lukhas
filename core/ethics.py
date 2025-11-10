"""Shim: core.ethics → prefer package `core.ethics`, lazy labs fallback.

Removes import-time dependency on `labs.core.ethics` by exposing a lazy
attribute proxy. Prefer `core/ethics/__init__.py` implementation in-repo.
"""
from __future__ import annotations

import importlib
from typing import Any

try:  # pragma: no cover
    from core.ethics import EthicsEngine, EthicalValidator, validate_ethical_compliance  # type: ignore
    _HAS_PRIMARY = True
    __all__ = ["EthicsEngine", "EthicalValidator", "validate_ethical_compliance"]
except Exception:  # pragma: no cover
    _HAS_PRIMARY = False
    __all__ = []


def __getattr__(name: str) -> Any:  # pragma: no cover
    try:
        mod = importlib.import_module("labs.core.ethics")
        return getattr(mod, name)
    except Exception as e:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}: {e}") from e


# No __all__ exposure for labs fallback to discourage star imports.
