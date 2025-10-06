"""Bridge for consciousness.matriz_thought_loop -> lukhas.consciousness implementation."""
from __future__ import annotations

from lukhas._bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=(
        "lukhas.consciousness.matriz_thought_loop",
        "candidate.consciousness.core.matriz",
    ),
    deprecation=(
        "Importing from 'consciousness.matriz_thought_loop' is deprecated; "
        "use 'lukhas.consciousness.matriz_thought_loop' instead."
    ),
)

globals().update(_exports)
del _mod, _exports
