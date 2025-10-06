"""Bridge: lukhas.observability.advanced_metrics -> candidate implementations."""
from __future__ import annotations

from importlib import import_module

for path in [
    "candidate.observability.advanced_metrics",
    "candidate.observability",
]:
    try:
        _m = import_module(path)
        names = getattr(_m, "__all__", [n for n in dir(_m) if not n.startswith("_")])
        globals().update({n: getattr(_m, n) for n in names})
        __all__ = names
        break
    except Exception:
        continue

if "__all__" not in globals():
    __all__ = []
