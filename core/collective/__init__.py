"""Bridge to candidate collective.

This module lazily proxies attributes from `labs.core.collective` to avoid
import-time dependencies on `labs` for production lanes. Callers can still
access names as if imported, e.g. `from core.collective import Foo`, but the
actual `labs` package is imported only at attribute access time.
"""
from __future__ import annotations

import importlib
from typing import Any, List


# Lazy-loaded module placeholder
_collective_module: Any | None = None


def _load_collective() -> Any | None:
    """Attempt to import labs.core.collective and cache the module.

    Returns the module on success, or None if `labs` is not available.
    """
    global _collective_module
    if _collective_module is not None:
        return _collective_module
    try:
        _collective_module = importlib.import_module("labs.core.collective")
    except Exception:
        _collective_module = None
    return _collective_module


def __getattr__(name: str):
    """Proxy attribute access to the labs.collective module at runtime.

    Raises AttributeError if the attribute or module is unavailable.
    """
    m = _load_collective()
    if m is None:
        raise AttributeError(name)
    return getattr(m, name)


def __dir__() -> List[str]:
    base = list(globals().keys())
    m = _load_collective()
    if m is not None:
        base.extend([n for n in dir(m) if not n.startswith("_")])
    return sorted(set(base))


def __all__() -> List[str]:
    m = _load_collective()
    return [n for n in dir(m) if not n.startswith("_")] if m is not None else []
