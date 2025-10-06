"""Bridge: memory.folds.fold_engine (FoldEngine, APIs)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.memory.folds.fold_engine",
    "candidate.memory.folds.fold_engine",
    "memory.folds.fold_engine",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
