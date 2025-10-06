"""Bridge: memory.folds (namespace for fold engines)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.memory.folds",
    "candidate.memory.folds",
    "memory.folds",
)
globals().update(_exp)
