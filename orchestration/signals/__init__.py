"""Bridge for orchestration.signals."""
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
    "lukhas_website.lukhas.orchestration.signals",
    "candidate.orchestration.signals",
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
if "Signal" not in globals():
    class Signal:  # pragma: no cover - stub
        """Stub for Signal."""
        def __init__(self, *a, **kw):
            pass
        def emit(self, *a, **kw):
            pass
    __all__.append("Signal")

def __getattr__(name: str):
    """Lazy attribute access fallback."""
    if _SRC and hasattr(_SRC, name):
        return getattr(_SRC, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
