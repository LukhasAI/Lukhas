"""Bridge: aka_qualia.core -> candidate implementations."""
from __future__ import annotations

try:
    from candidate.consciousness.aka_qualia.core import *  # noqa: F401, F403
    __all__ = [n for n in locals().keys() if not n.startswith("_")]
except Exception:
    try:
        from consciousness.aka_qualia import *  # noqa: F401, F403
        __all__ = [n for n in locals().keys() if not n.startswith("_")]
    except Exception:
        __all__ = []
