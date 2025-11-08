"""Bridge for `candidate.ledger`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.candidate.ledger
  2) candidate.candidate.ledger
  3) ledger

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
    "lukhas_website.candidate.ledger",
    "labs.candidate.ledger",
    "ledger",
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
    if _SRC is not None:
        # Use try/except to avoid recursion from hasattr()
        try:
            return object.__getattribute__(_SRC, name)
        except AttributeError:
            pass
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
