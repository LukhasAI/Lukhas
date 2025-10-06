"""Bridge: memory.folds.fold_soft_delete."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.memory.folds.fold_soft_delete",
    "candidate.memory.folds.fold_soft_delete",
    "memory.folds.fold_soft_delete",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
