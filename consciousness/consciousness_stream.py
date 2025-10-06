"""Bridge for consciousness.consciousness_stream -> candidate implementations."""
from __future__ import annotations

from lukhas._bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=(
        "candidate.consciousness.streams",
        "candidate.consciousness.core.stream",
    ),
    deprecation=(
        "Importing from 'consciousness.consciousness_stream' is deprecated; "
        "prefer 'lukhas.consciousness' public API."
    ),
)

globals().update(_exports)
del _mod, _exports
