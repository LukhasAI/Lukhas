"""Bridge for lukhas.core.common (+ virtual 'exceptions' submodule).

Exports from the richest available backend (core.common preferred).
Also registers 'lukhas.core.common.exceptions' as an alias to this module,
so tests importing the submodule succeed without converting layouts.
"""
from __future__ import annotations
import sys as _sys

_BOUND = False
try:
    from core.common import *  # noqa: F401,F403
    _BOUND = True
except Exception:
    try:
        from candidate.core.common import *  # noqa: F401,F403
        _BOUND = True
    except Exception:
        # Minimal safety symbol used by a few tests
        if "GLYPHToken" not in globals():
            class GLYPHToken(str):  # pragma: no cover - stub
                """Glyph token placeholder"""
                pass

# Present a virtual submodule: lukhas.core.common.exceptions → this module
_sys.modules[__name__ + ".exceptions"] = _sys.modules[__name__]

# Be explicit; add more if you know them
__all__ = sorted(name for name in globals()
                 if not name.startswith("_"))
