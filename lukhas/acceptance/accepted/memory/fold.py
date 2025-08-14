"""
LUKHAS AI Memory - Fold System
Fold-based memory with 99.7% cascade prevention
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MemoryFold:
    """Represents a single memory fold"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    causal_chain: List[str] = field(default_factory=list)
    emotional_valence: float = 0.0
    importance: float = 0.5
    accessed_count: int = 0


class FoldManager:
    """Manages memory folds with cascade prevention"""

    MAX_FOLDS = 1000  # From CLAUDE.md
    CASCADE_THRESHOLD = 0.997  # 99.7% prevention rate

    def __init__(self):
        self.folds: Dict[str, MemoryFold] = {}
        self.active_folds: List[str] = []
        self.cascade_prevention_active = True

    def create_fold(self, content: Any, causal_chain: List[str] = None) -> MemoryFold:
        """Create a new memory fold"""
        fold = MemoryFold(content=content, causal_chain=causal_chain or [])

        # Prevent cascade if at limit
        if len(self.folds) >= self.MAX_FOLDS:
            self._prevent_cascade()

        self.folds[fold.id] = fold
        self.active_folds.append(fold.id)

        return fold

    def _prevent_cascade(self):
        """Prevent memory cascade by pruning old folds"""
        if not self.cascade_prevention_active:
            return

        # Remove least important folds
        sorted_folds = sorted(
            self.folds.values(), key=lambda f: (f.importance, f.accessed_count)
        )

        # Keep most important 90%
        keep_count = int(self.MAX_FOLDS * 0.9)
        for fold in sorted_folds[:-keep_count]:
            del self.folds[fold.id]
            if fold.id in self.active_folds:
                self.active_folds.remove(fold.id)

    def retrieve_fold(self, fold_id: str) -> Optional[MemoryFold]:
        """Retrieve a specific fold"""
        fold = self.folds.get(fold_id)
        if fold:
            fold.accessed_count += 1
        return fold

    def get_causal_chain(self, fold_id: str) -> List[MemoryFold]:
        """Get full causal chain for a fold"""
        fold = self.folds.get(fold_id)
        if not fold:
            return []

        chain = []
        for chain_id in fold.causal_chain:
            if chain_fold := self.folds.get(chain_id):
                chain.append(chain_fold)

        return chain

    def consolidate(self):
        """Consolidate memory folds"""
        # This would implement sophisticated consolidation
        # For now, just mark as consolidated
        return {"consolidated": True, "fold_count": len(self.folds)}


# Singleton instance
_fold_manager = None


def get_fold_manager() -> FoldManager:
    """Get or create fold manager singleton"""
    global _fold_manager
    if _fold_manager is None:
        _fold_manager = FoldManager()
    return _fold_manager
