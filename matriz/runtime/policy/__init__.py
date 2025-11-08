"""Bridge for `matriz.runtime.policy`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.matriz.runtime.policy
  2) candidate.matriz.runtime.policy
  3) matriz.runtime.policy

Graceful fallback to stubs if no backend available.
"""

from __future__ import annotations

from importlib import import_module

__all__: list[str] = []


def _try(n: str):
    try:
        return import_module(n)
    except Exception:
        return None


# Try backends in order (exclude self to prevent recursion)
_CANDIDATES = (
    "lukhas_website.matriz.runtime.policy",
    "candidate.matriz.runtime.policy",
    # "matriz.runtime.policy",  # Removed - would cause self-import recursion
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
    if _SRC:
        # Use try/except instead of hasattr to avoid recursion
        try:
            return getattr(_SRC, name)
        except AttributeError:
            pass
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
