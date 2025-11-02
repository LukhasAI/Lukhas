"""Bridge for core.breakthrough package."""

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
    "lukhas_website.core.breakthrough",
    "labs.core.breakthrough",
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
if "BreakthroughDetector" not in globals():

    class BreakthroughDetector:  # pragma: no cover - stub
        """Stub for BreakthroughDetector."""

        def __init__(self, *a, **kw):
            pass

        def __call__(self, *a, **kw):
            return None

    __all__.append("BreakthroughDetector")


def __getattr__(name: str):
    """Lazy attribute access fallback."""
    if _SRC and hasattr(_SRC, name):
        return getattr(_SRC, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
