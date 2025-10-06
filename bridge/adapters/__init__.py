"""Bridge: bridge.adapters -> candidate implementations."""
from __future__ import annotations

from importlib import import_module

__all__ = []

for path in ["candidate.bridge.adapters", "adapters"]:
    try:
        _m = import_module(path)
        names = getattr(_m, "__all__", [n for n in dir(_m) if not n.startswith("_")])
        globals().update({n: getattr(_m, n) for n in names})
        __all__ = names
        break
    except Exception:
        continue
