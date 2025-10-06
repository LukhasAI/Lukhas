"""Bridge for consciousness.dream.expand -> candidate.consciousness.dream expansion."""
from __future__ import annotations

from lukhas._bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=(
        "candidate.consciousness.dream.expand",
        "candidate.consciousness.expansion",  # fallback
    ),
    deprecation=(
        "Importing from 'consciousness.dream.expand' is deprecated; "
        "prefer 'lukhas.consciousness' public API where possible."
    ),
)

globals().update(_exports)
del _mod, _exports
