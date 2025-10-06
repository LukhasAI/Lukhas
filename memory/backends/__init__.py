"""Bridge: memory.backends."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.memory.backends",
    "candidate.memory.backends",
    "memory.backends",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
