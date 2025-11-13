"""Dream persistence with memory fold linkage."""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class DreamRecord:
    """Represents a persisted dream with fold linkage."""

    def __init__(
        self,
        dream_id: str,
        content: Dict[str, Any],
        fold_id: Optional[str] = None,
        wavec_snapshot_hash: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a dream record.

        Args:
            dream_id: Unique identifier for the dream
            content: Dream content and metadata
            fold_id: Memory fold ID linking this dream to a memory snapshot
            wavec_snapshot_hash: Hash of the WaveC snapshot at dream time
            timestamp: When the dream was created (defaults to now)
        """
        self.dream_id = dream_id
        self.content = content
        self.fold_id = fold_id
        self.wavec_snapshot_hash = wavec_snapshot_hash
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary format."""
        return {
            "dream_id": self.dream_id,
            "content": self.content,
            "fold_id": self.fold_id,
            "wavec_snapshot_hash": self.wavec_snapshot_hash,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DreamRecord":
        """Create record from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])

        return cls(
            dream_id=data["dream_id"],
            content=data["content"],
            fold_id=data.get("fold_id"),
            wavec_snapshot_hash=data.get("wavec_snapshot_hash"),
            timestamp=timestamp
        )


class DreamPersistence:
    """Manages dream persistence with memory fold tracking."""

    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize dream persistence.

        Args:
            storage_backend: Backend for actual storage (optional, uses in-memory if None)
        """
        self.storage = storage_backend or InMemoryStorage()
        self.wavec_interface = None  # Will be set if WaveC integration is available

    def set_wavec_interface(self, wavec_interface: Any) -> None:
        """
        Set WaveC interface for snapshot hash retrieval.

        Args:
            wavec_interface: Interface to WaveC checkpoint system
        """
        self.wavec_interface = wavec_interface

    def save_dream(
        self,
        dream: Dict[str, Any],
        fold_id: Optional[str] = None,
        auto_link_wavec: bool = True
    ) -> DreamRecord:
        """
        Save a dream with fold linkage.

        Args:
            dream: Dream data to save
            fold_id: Optional memory fold ID to link
            auto_link_wavec: If True, automatically capture WaveC snapshot hash

        Returns:
            Created DreamRecord
        """
        dream_id = dream.get("id") or self._generate_dream_id(dream)

        # Capture WaveC snapshot hash if available and requested
        wavec_hash = None
        if auto_link_wavec and self.wavec_interface:
            wavec_hash = self._get_current_wavec_hash()

        record = DreamRecord(
            dream_id=dream_id,
            content=dream,
            fold_id=fold_id,
            wavec_snapshot_hash=wavec_hash
        )

        self.storage.save(record)
        return record

    def get_dream(self, dream_id: str) -> Optional[DreamRecord]:
        """
        Retrieve a dream by ID.

        Args:
            dream_id: Dream identifier

        Returns:
            DreamRecord if found, None otherwise
        """
        return self.storage.get(dream_id)

    def get_dreams_by_fold(self, fold_id: str) -> List[DreamRecord]:
        """
        Get all dreams linked to a specific memory fold.

        Args:
            fold_id: Memory fold identifier

        Returns:
            List of DreamRecords linked to this fold
        """
        return self.storage.query_by_fold(fold_id)

    def get_dreams_by_wavec_hash(self, snapshot_hash: str) -> List[DreamRecord]:
        """
        Get all dreams linked to a specific WaveC snapshot.

        Args:
            snapshot_hash: WaveC snapshot hash

        Returns:
            List of DreamRecords with this snapshot hash
        """
        return self.storage.query_by_wavec_hash(snapshot_hash)

    def _generate_dream_id(self, dream: Dict[str, Any]) -> str:
        """Generate a unique dream ID from content."""
        content_str = json.dumps(dream, sort_keys=True)
        timestamp = datetime.utcnow().isoformat()
        combined = f"{content_str}:{timestamp}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _get_current_wavec_hash(self) -> Optional[str]:
        """Get current WaveC snapshot hash."""
        if not self.wavec_interface:
            return None

        try:
            snapshot = self.wavec_interface.get_current_snapshot()
            if snapshot:
                return snapshot.get("hash") or self._hash_snapshot(snapshot)
        except Exception as e:
            print(f"Warning: Failed to get WaveC snapshot: {e}")

        return None

    def _hash_snapshot(self, snapshot: Dict[str, Any]) -> str:
        """Hash a snapshot object."""
        snapshot_str = json.dumps(snapshot, sort_keys=True)
        return hashlib.sha256(snapshot_str.encode()).hexdigest()


class InMemoryStorage:
    """Simple in-memory storage for dreams."""

    def __init__(self):
        self.dreams: Dict[str, DreamRecord] = {}

    def save(self, record: DreamRecord) -> None:
        """Save a dream record."""
        self.dreams[record.dream_id] = record

    def get(self, dream_id: str) -> Optional[DreamRecord]:
        """Get a dream by ID."""
        return self.dreams.get(dream_id)

    def query_by_fold(self, fold_id: str) -> List[DreamRecord]:
        """Query dreams by fold ID."""
        return [
            record for record in self.dreams.values()
            if record.fold_id == fold_id
        ]

    def query_by_wavec_hash(self, snapshot_hash: str) -> List[DreamRecord]:
        """Query dreams by WaveC snapshot hash."""
        return [
            record for record in self.dreams.values()
            if record.wavec_snapshot_hash == snapshot_hash
        ]


if __name__ == "__main__":
    # Demonstration
    persistence = DreamPersistence()

    # Save a dream with fold linkage
    dream = {
        "id": "dream_001",
        "content": "A vivid landscape",
        "themes": ["nature", "beauty"],
        "intensity": 0.8
    }

    record = persistence.save_dream(
        dream,
        fold_id="fold_abc123",
        auto_link_wavec=False  # No WaveC interface configured
    )

    print("Saved dream:", record.to_dict())

    # Retrieve by fold
    fold_dreams = persistence.get_dreams_by_fold("fold_abc123")
    print(f"Dreams in fold: {len(fold_dreams)}")
