# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernize deprecated Dict, List imports to native types in WaveC checkpoint
# estimate: 10min | priority: medium | dependencies: core-wavec-system

"""WaveC checkpoint system with drift-based branching metadata."""
from typing import Any, Optional
from datetime import datetime
from copy import deepcopy
import hashlib
import json


class CheckpointSnapshot:
    """Represents a WaveC state snapshot."""

    def __init__(
        self,
        snapshot_id: str,
        state: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a checkpoint snapshot.

        Args:
            snapshot_id: Unique identifier for this snapshot
            state: State data captured in this snapshot
            metadata: Additional metadata about the snapshot
            timestamp: When the snapshot was created (defaults to now)
        """
        self.snapshot_id = snapshot_id
        self.state = state
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.utcnow()

    def get_hash(self) -> str:
        """Compute hash of the snapshot state."""
        state_str = json.dumps(self.state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary representation."""
        return {
            "snapshot_id": self.snapshot_id,
            "state": deepcopy(self.state),
            "metadata": deepcopy(self.metadata),
            "timestamp": self.timestamp.isoformat(),
            "hash": self.get_hash()
        }


class WaveCCheckpoint:
    """
    WaveC checkpoint system with drift-based branching.

    When drift detection triggers a rollback, metadata is annotated
    with branch information for continuity analysis.
    """

    def __init__(self, drift_threshold: float = 0.5):
        """
        Initialize WaveC checkpoint system.

        Args:
            drift_threshold: Threshold for drift-based branching (0.0 to 1.0)
        """
        self.drift_threshold = drift_threshold
        self.snapshots: list[CheckpointSnapshot] = []
        self.current_state: dict[str, Any] = {}
        self.branch_history: list[dict[str, Any]] = []

    def create_snapshot(
        self,
        state: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None
    ) -> CheckpointSnapshot:
        """
        Create a new checkpoint snapshot.

        Args:
            state: Current state to snapshot
            metadata: Additional metadata

        Returns:
            Created CheckpointSnapshot
        """
        snapshot_id = f"snap_{len(self.snapshots):04d}_{datetime.utcnow().timestamp()}"
        snapshot = CheckpointSnapshot(snapshot_id, state, metadata)
        self.snapshots.append(snapshot)
        self.current_state = deepcopy(state)
        return snapshot

    def detect_drift(self, current_state: dict[str, Any], reference_state: dict[str, Any]) -> float:
        """
        Detect drift between current and reference states.

        Args:
            current_state: Current state to check
            reference_state: Reference state to compare against

        Returns:
            Drift value (0.0 = no drift, 1.0 = maximum drift)
        """
        # Simple drift calculation based on state differences
        # In a real implementation, this would use semantic embeddings, etc.

        if not current_state or not reference_state:
            return 0.0

        # Count differing keys
        all_keys = set(current_state.keys()) | set(reference_state.keys())
        if not all_keys:
            return 0.0

        differing_keys = 0
        for key in all_keys:
            current_val = current_state.get(key)
            reference_val = reference_state.get(key)
            if current_val != reference_val:
                differing_keys += 1

        drift = differing_keys / len(all_keys)
        return min(1.0, drift)

    def check_and_rollback(
        self,
        current_state: dict[str, Any],
        reference_snapshot: Optional[CheckpointSnapshot] = None
    ) -> Optional[CheckpointSnapshot]:
        """
        Check for drift and rollback if threshold exceeded.

        Args:
            current_state: Current state to check
            reference_snapshot: Reference snapshot (uses last snapshot if None)

        Returns:
            Rollback snapshot if rollback occurred, None otherwise
        """
        if not reference_snapshot:
            if not self.snapshots:
                return None
            reference_snapshot = self.snapshots[-1]

        # Calculate drift
        drift_value = self.detect_drift(current_state, reference_snapshot.state)

        # Check if rollback is needed
        if drift_value >= self.drift_threshold:
            return self._perform_rollback(
                current_state=current_state,
                reference_snapshot=reference_snapshot,
                drift_value=drift_value
            )

        return None

    def _perform_rollback(
        self,
        current_state: dict[str, Any],
        reference_snapshot: CheckpointSnapshot,
        drift_value: float
    ) -> CheckpointSnapshot:
        """
        Perform rollback with drift metadata annotation.

        Args:
            current_state: State that triggered rollback
            reference_snapshot: Snapshot to rollback to
            drift_value: Measured drift value

        Returns:
            New snapshot with branch metadata
        """
        # Create metadata for the branch
        branch_metadata = {
            "branch_from": reference_snapshot.snapshot_id,
            "drift_value": drift_value,
            "threshold": self.drift_threshold,
            "branch_type": "drift_rollback",
            "rollback_timestamp": datetime.utcnow().isoformat(),
            "original_state_hash": self._hash_state(current_state),
            "reference_state_hash": reference_snapshot.get_hash()
        }

        # Record branch event in history
        self.branch_history.append({
            "event": "rollback",
            "timestamp": datetime.utcnow().isoformat(),
            **branch_metadata
        })

        # Create new snapshot with branch metadata
        rollback_state = deepcopy(reference_snapshot.state)
        new_metadata = deepcopy(reference_snapshot.metadata)
        new_metadata.update(branch_metadata)

        rollback_snapshot = self.create_snapshot(
            state=rollback_state,
            metadata=new_metadata
        )

        return rollback_snapshot

    def _hash_state(self, state: dict[str, Any]) -> str:
        """Hash a state dictionary."""
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()

    def get_current_snapshot(self) -> Optional[CheckpointSnapshot]:
        """Get the most recent snapshot."""
        return self.snapshots[-1] if self.snapshots else None

    def get_branch_history(self) -> list[dict[str, Any]]:
        """Get complete branch history."""
        return deepcopy(self.branch_history)

    def get_snapshots_with_drift_metadata(self) -> List[Dict[str, Any]]:
        """Get all snapshots that have drift metadata."""
        return [
            snapshot.to_dict()
            for snapshot in self.snapshots
            if "drift_value" in snapshot.metadata
        ]


if __name__ == "__main__":
    # Demonstration
    print("=== WaveC Checkpoint with Drift Branching Demo ===\n")

    # Initialize checkpoint system
    wavec = WaveCCheckpoint(drift_threshold=0.4)

    # Create initial snapshot
    initial_state = {
        "memory": "state_a",
        "emotion": "neutral",
        "context": "initial"
    }
    snap1 = wavec.create_snapshot(initial_state, {"note": "Initial state"})
    print(f"Created snapshot: {snap1.snapshot_id}")
    print(f"Hash: {snap1.get_hash()}\n")

    # Simulate drift
    drifted_state = {
        "memory": "state_b",  # Changed
        "emotion": "anxious",  # Changed
        "context": "diverged"  # Changed
    }

    print(f"Checking drift...")
    drift_value = wavec.detect_drift(drifted_state, initial_state)
    print(f"Drift value: {drift_value:.2f} (threshold: {wavec.drift_threshold})\n")

    # Trigger rollback
    if drift_value >= wavec.drift_threshold:
        print("Drift threshold exceeded, performing rollback...")
        rollback_snap = wavec.check_and_rollback(drifted_state)

        if rollback_snap:
            print(f"Rollback snapshot: {rollback_snap.snapshot_id}")
            print(f"Branch metadata: {json.dumps(rollback_snap.metadata, indent=2)}\n")

    # Show branch history
    print("Branch history:")
    for event in wavec.get_branch_history():
        print(f"  - {event['event']} at {event['timestamp']}")
        print(f"    drift_value: {event.get('drift_value', 'N/A')}")
        print(f"    branch_from: {event.get('branch_from', 'N/A')}\n")

    # Show all snapshots with drift metadata
    print("Snapshots with drift metadata:")
    for snap_dict in wavec.get_snapshots_with_drift_metadata():
        print(f"  - {snap_dict['snapshot_id']}: drift={snap_dict['metadata'].get('drift_value', 'N/A')}")
