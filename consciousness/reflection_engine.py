"""Bridge for consciousness.reflection_engine -> candidate.consciousness.reflection."""
from __future__ import annotations

from lukhas._bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=("candidate.consciousness.reflection",),
    deprecation=(
        "Importing from 'consciousness.reflection_engine' is deprecated; "
        "use 'consciousness.reflection' instead."
    ),
)

globals().update(_exports)
del _mod, _exports
