"""
Bio Utils bridge - canonical namespace for bio-symbolic utilities.

Bridges to existing bio utility implementations.
"""
from __future__ import annotations

from importlib import import_module

_backend_paths = [
    "candidate.bio.utils",
    "bio.utils",
]

for p in _backend_paths:
    try:
        _m = import_module(p)
        __all__ = getattr(_m, "__all__", [n for n in dir(_m) if not n.startswith("_")])
        globals().update({n: getattr(_m, n) for n in __all__})
        break
    except Exception:
        continue

if "__all__" not in globals():
    __all__ = []
