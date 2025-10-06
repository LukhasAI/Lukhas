"""Bridge: memory.folds (fold engines, ops, etc.)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.memory.folds",
    "candidate.memory.folds",
    "memory.folds",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
