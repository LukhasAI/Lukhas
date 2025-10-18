import logging
from datetime import timezone

logger = logging.getLogger(__name__)
"""

#TAG:memory
#TAG:folds
#TAG:neuroplastic
#TAG:colony


Dream Memory Fold System for LUKHAS Cognitive AI.

This module implements the DreamMemoryFold syncing system for persistent
introspective content with symbolic annotation.

ΛTAG: dream_memory, snapshot_memory, recur_loop, symbolic_ai
ΛLOCKED: false
ΛCANONICAL: Dream memory folding and snapshot persistence
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from core.common import get_logger

logger = get_logger(__name__)


@dataclass
class DreamSnapshot:
    """Represents a snapshot of dream state with symbolic annotation."""

    snapshot_id: str
    timestamp: datetime
    dream_state: dict[str, Any]
    symbolic_annotations: dict[str, Any]
    introspective_content: dict[str, Any]
    drift_metrics: dict[str, float]
    memory_fold_index: int
    # ΛTAG: survival_score - heuristic score for value-preservation bias
    survival_score: float = 0.0
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert snapshot to dictionary for serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DreamSnapshot":
        """Create snapshot from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if "survival_score" not in data:
            data["survival_score"] = 0.0
        return cls(**data)


@dataclass
class MemoryFoldState:
    """Represents the state of a memory fold."""

    fold_id: str
    creation_time: datetime
    last_sync: datetime
    snapshots: list[DreamSnapshot] = field(default_factory=list)
    fold_depth: int = 0
    convergence_score: float = 0.0
    symbolic_tags: list[str] = field(default_factory=list)

    def add_snapshot(self, snapshot: DreamSnapshot) -> None:
        """Add a snapshot to this fold."""
        self.snapshots.append(snapshot)
        self.last_sync = datetime.now(timezone.utc)
        self.fold_depth += 1


class DreamMemoryFold:
    """
    Dream Memory Fold system for syncing and persisting introspective content.

    This system creates 'folds' in dream memory that can be synced, snapshots
    that capture dream states, and symbolic annotations for introspection.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the Dream Memory Fold system."""
        self.storage_path = Path(storage_path) if storage_path else Path("dream_memory_folds")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.active_folds: dict[str, MemoryFoldState] = {}
        self.snapshot_cache: dict[str, DreamSnapshot] = {}
        self.sync_callbacks: list[Callable] = []

        # Initialize drift tracker integration
        self.drift_tracker_available = False
        try:
            from oneiric.oneiric_core.utils.drift_tracker import SymbolicDriftTracker

            self.drift_tracker = SymbolicDriftTracker()
            self.drift_tracker_available = True
            logger.info("Drift tracker integration available for memory folding")
        except ImportError:
            logger.warning("Drift tracker not available for memory folding")

    async def create_fold(self, fold_id: str, initial_tags: Optional[list[str]] = None) -> MemoryFoldState:
        """Create a new memory fold."""
        if fold_id in self.active_folds:
            raise ValueError(f"Fold {fold_id} already exists")

        fold = MemoryFoldState(
            fold_id=fold_id,
            creation_time=datetime.now(timezone.utc),
            last_sync=datetime.now(timezone.utc),
            symbolic_tags=initial_tags or [],
        )

        self.active_folds[fold_id] = fold
        await self._persist_fold(fold)

        logger.info(f"Created new memory fold: {fold_id}")
        return fold

    async def dream_snapshot(
        self,
        fold_id: str,
        dream_state: dict[str, Any],
        introspective_content: dict[str, Any],
        symbolic_annotations: Optional[dict[str, Any]] = None,
    ) -> DreamSnapshot:
        """
        Create a dream snapshot with symbolic annotation.

        Args:
            fold_id: The memory fold to store the snapshot in
            dream_state: Current dream processing state
            introspective_content: Introspective analysis content
            symbolic_annotations: Optional symbolic annotations

        Returns:
            DreamSnapshot: The created snapshot
        """
        if fold_id not in self.active_folds:
            await self.create_fold(fold_id)

        fold = self.active_folds[fold_id]

        # Generate snapshot ID
        snapshot_id = f"{fold_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Get drift metrics if available
        drift_metrics = {}
        if self.drift_tracker_available:
            try:
                # Use snapshot_id as symbol_id for drift tracking
                symbol_id = f"dream_{fold_id}"
                self.drift_tracker.register_drift(symbol_id, dream_state)
                drift_metrics = {
                    "symbol_id": symbol_id,
                    "drift_registered": True,
                    "dream_state_size": len(str(dream_state)),
                }
            except Exception as e:
                logger.warning(f"Error calculating drift metrics: {e}")
                drift_metrics = {"error": str(e)}

        # Create snapshot
        snapshot = DreamSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(timezone.utc),
            dream_state=dream_state,
            symbolic_annotations=symbolic_annotations or {},
            introspective_content=introspective_content,
            drift_metrics=drift_metrics,
            memory_fold_index=fold.fold_depth,
            survival_score=max(0.0, 1.0 - drift_metrics.get("drift_score", 0.0)),
            tags=fold.symbolic_tags.copy(),
        )

        # Add to fold
        fold.add_snapshot(snapshot)
        self.snapshot_cache[snapshot_id] = snapshot

        # Persist the snapshot
        await self._persist_snapshot(snapshot)

        # Update fold convergence score
        await self._update_convergence_score(fold)

        # Trigger sync callbacks
        for callback in self.sync_callbacks:
            try:
                await callback(fold, snapshot)
            except Exception as e:
                logger.error(f"Error in sync callback: {e}")

        logger.info(f"Created dream snapshot: {snapshot_id} in fold {fold_id}")
        return snapshot

    async def sync_fold(self, fold_id: str) -> bool:
        """Synchronize a memory fold with persistent storage."""
        if fold_id not in self.active_folds:
            logger.warning(f"Fold {fold_id} not found for sync")
            return False

        fold = self.active_folds[fold_id]

        try:
            # Persist fold state
            await self._persist_fold(fold)

            # Persist all snapshots
            for snapshot in fold.snapshots:
                await self._persist_snapshot(snapshot)

            fold.last_sync = datetime.now(timezone.utc)
            logger.info(f"Synchronized fold {fold_id} with {len(fold.snapshots)} snapshots")
            return True

        except Exception as e:
            logger.error(f"Error syncing fold {fold_id}: {e}")
            return False

    async def get_fold_snapshots(self, fold_id: str) -> list[DreamSnapshot]:
        """Get all snapshots for a memory fold."""
        if fold_id not in self.active_folds:
            return []

        return self.active_folds[fold_id].snapshots.copy()

    async def get_snapshot(self, snapshot_id: str) -> Optional[DreamSnapshot]:
        """Get a specific snapshot by ID."""
        if snapshot_id in self.snapshot_cache:
            return self.snapshot_cache[snapshot_id]

        # Try to load from storage
        return await self._load_snapshot(snapshot_id)

    async def add_sync_callback(self, callback: Callable) -> None:
        """Add a callback to be called on fold sync."""
        self.sync_callbacks.append(callback)

    async def _persist_fold(self, fold: MemoryFoldState) -> None:
        """Persist a memory fold to storage."""
        fold_file = self.storage_path / f"fold_{fold.fold_id}.json"

        fold_data = {
            "fold_id": fold.fold_id,
            "creation_time": fold.creation_time.isoformat(),
            "last_sync": fold.last_sync.isoformat(),
            "fold_depth": fold.fold_depth,
            "convergence_score": fold.convergence_score,
            "symbolic_tags": fold.symbolic_tags,
            "snapshot_ids": [s.snapshot_id for s in fold.snapshots],
        }

        with open(fold_file, "w") as f:
            json.dump(fold_data, f, indent=2)

    async def _persist_snapshot(self, snapshot: DreamSnapshot) -> None:
        """Persist a dream snapshot to storage."""
        snapshot_file = self.storage_path / f"snapshot_{snapshot.snapshot_id}.json"

        with open(snapshot_file, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=2)

    async def _load_snapshot(self, snapshot_id: str) -> Optional[DreamSnapshot]:
        """Load a snapshot from storage."""
        snapshot_file = self.storage_path / f"snapshot_{snapshot_id}.json"

        if not snapshot_file.exists():
            return None

        try:
            with open(snapshot_file) as f:
                data = json.load(f)

            snapshot = DreamSnapshot.from_dict(data)
            self.snapshot_cache[snapshot_id] = snapshot
            return snapshot

        except Exception as e:
            logger.error(f"Error loading snapshot {snapshot_id}: {e}")
            return None

    async def _update_convergence_score(self, fold: MemoryFoldState) -> None:
        """Update the convergence score for a memory fold."""
        if len(fold.snapshots) < 2:
            fold.convergence_score = 0.0
            return

        # Calculate convergence based on drift metrics and symbolic consistency
        recent_snapshots = fold.snapshots[-5:]  # Last 5 snapshots

        if self.drift_tracker_available:
            # Use drift metrics for convergence calculation
            drift_scores = [s.drift_metrics.get("drift_score", 0.0) for s in recent_snapshots]
            avg_drift = sum(drift_scores) / len(drift_scores) if drift_scores else 0.0

            # Lower drift = higher convergence
            fold.convergence_score = max(0.0, 1.0 - avg_drift)
        else:
            # Fallback: use symbolic tag consistency
            all_tags = set()
            for snapshot in recent_snapshots:
                all_tags.update(snapshot.tags)

            # Calculate tag consistency across snapshots
            if all_tags:
                consistency_scores = []
                for snapshot in recent_snapshots:
                    consistency = len(set(snapshot.tags) & all_tags) / len(all_tags)
                    consistency_scores.append(consistency)

                fold.convergence_score = sum(consistency_scores) / len(consistency_scores)
            else:
                fold.convergence_score = 0.0

    async def get_fold_statistics(self, fold_id: str) -> dict[str, Any]:
        """Get statistics for a memory fold."""
        if fold_id not in self.active_folds:
            return {}

        fold = self.active_folds[fold_id]

        return {
            "fold_id": fold_id,
            "creation_time": fold.creation_time.isoformat(),
            "last_sync": fold.last_sync.isoformat(),
            "snapshot_count": len(fold.snapshots),
            "fold_depth": fold.fold_depth,
            "convergence_score": fold.convergence_score,
            "symbolic_tags": fold.symbolic_tags,
            "drift_metrics_available": self.drift_tracker_available,
        }


# Global instance
_global_dream_memory_fold = None


def get_global_dream_memory_fold() -> DreamMemoryFold:
    """Get the global dream memory fold instance."""
    global _global_dream_memory_fold
    if _global_dream_memory_fold is None:
        _global_dream_memory_fold = DreamMemoryFold()
    return _global_dream_memory_fold
