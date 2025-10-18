"""Bridge for consciousness.dream.core -> candidate.consciousness.dream.core."""
from __future__ import annotations

from _bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=("candidate.consciousness.dream.core",),
    deprecation=(
        "Importing from 'consciousness.dream.core' is deprecated; "
        "prefer 'consciousness' public API where possible."
    ),
)

globals().update(_exports)
del _mod, _exports
