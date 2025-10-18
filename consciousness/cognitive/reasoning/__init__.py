"""Bridge for consciousness.cognitive.reasoning -> candidate."""
from __future__ import annotations

from _bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=("candidate.consciousness.cognitive.reasoning", "candidate.consciousness.reasoning"),
)

globals().update(_exports)
del _mod, _exports
