"""Bridge: lukhas.memory.sync -> memory.sync variants."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.memory.sync",
    "candidate.memory.sync",
    "memory.sync",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
