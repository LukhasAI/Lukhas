"""Bridge for `aka_qualia.memory_noop`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.aka_qualia.memory_noop
  2) candidate.aka_qualia.memory_noop
  3) aka_qualia.memory_noop

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []

def _try(n: str):
    try:
        return import_module(n)
    except Exception:
        return None

# Try backends in order
_CANDIDATES = (
    "lukhas_website.aka_qualia.memory_noop",
    "candidate.aka_qualia.memory_noop",
    "aka_qualia.memory_noop",
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

# Add expected symbols as stubs if not found
if "NoopMemory" not in globals():

    class NoopMemory:
        pass
