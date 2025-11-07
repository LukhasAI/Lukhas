"""Bridge: memory.folds.fold_soft_delete."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.memory.folds.fold_soft_delete",
    "candidate.memory.folds.fold_soft_delete",
    "memory.folds.fold_soft_delete",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_memory_folds_fold_soft_delete___init___py_L11"}
