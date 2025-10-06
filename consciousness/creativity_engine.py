"""Bridge for consciousness.creativity_engine -> candidate implementations."""
from __future__ import annotations

from lukhas._bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=(
        "candidate.consciousness.creativity",
        "candidate.consciousness.engines.creativity",
    ),
    deprecation=(
        "Importing from 'consciousness.creativity_engine' is deprecated; "
        "prefer 'lukhas.consciousness' public API."
    ),
)

globals().update(_exports)
del _mod, _exports
