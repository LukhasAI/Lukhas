"""Bridge: memory.folds.fold_engine"""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.memory.folds.fold_engine",
    "candidate.memory.folds.fold_engine",
    "memory.fold_engine",  # historical
)
globals().update(_exp)
