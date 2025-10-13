"""Bridge: lukhas.cognitive_core.reasoning -> candidate implementations."""
from __future__ import annotations

try:
    from labs.cognitive_core.reasoning import *
    __all__ = [n for n in locals().keys() if not n.startswith("_")]
except Exception:
    try:
        from consciousness.cognitive.reasoning import *
        __all__ = [n for n in locals().keys() if not n.startswith("_")]
    except Exception:
        __all__ = []
