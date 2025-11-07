"""Bridge for `memory.backends.base`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.memory.backends.base
  2) candidate.memory.backends.base
  3) memory.backends.base

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
from typing import List

__all__: list[str] = []

def _try(n: str):
    try:
        return import_module(n)
    except Exception:
        return None

# Try backends in order
_CANDIDATES = (
    "lukhas_website.memory.backends.base",
    "candidate.memory.backends.base",
    "memory.backends.base",
)

_SRC = None
for _cand in _CANDIDATES:
    _m = _try(_cand)
    if _m:
        _SRC = _m
        for _k in dir(_m):
            if not _k.startswith("_"):
                globals()[_k] = getattr(_m, _k)
                __all__.append(_k)
        break

# Add expected symbols as stubs if not found
# No pre-defined stubs

def __getattr__(name: str):
    """Lazy attribute access fallback."""
    if _SRC and hasattr(_SRC, name):
        return getattr(_SRC, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
