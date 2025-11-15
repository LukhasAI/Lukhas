# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernize deprecated Dict, List imports to native types in memory folds
# estimate: 5min | priority: medium | dependencies: core-memory-system

"""Memory fold implementations with immutability support."""
from copy import deepcopy
from datetime import datetime
from typing import Any, Optional


class FoldSealedError(Exception):
    """Raised when attempting to mutate a sealed fold."""
    pass


class MemoryFold:
    """Base class for memory folds."""

    def __init__(self, fold_id: str, data: Optional[dict[str, Any]] = None):
        """
        Initialize a memory fold.

        Args:
            fold_id: Unique identifier for this fold
            data: Initial fold data
        """
        self.fold_id = fold_id
        self.data = data or {}
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the fold.

        Args:
            key: Data key
            value: Value to store
        """
        self.data[key] = value
        self.updated_at = datetime.utcnow()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the fold.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Value associated with key or default
        """
        return self.data.get(key, default)

    def update(self, updates: dict[str, Any]) -> None:
        """
        Update multiple values.

        Args:
            updates: Dictionary of key-value pairs to update
        """
        self.data.update(updates)
        self.updated_at = datetime.utcnow()

    def delete(self, key: str) -> None:
        """
        Delete a key from the fold.

        Args:
            key: Key to delete
        """
        if key in self.data:
            del self.data[key]
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert fold to dictionary representation."""
        return {
            "fold_id": self.fold_id,
            "data": deepcopy(self.data),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class WriteOnceFold(MemoryFold):
    """
    Memory fold that can only be written once.

    After calling seal(), any mutation attempts will raise FoldSealedError.
    This ensures immutability for auditing and compliance purposes.
    """

    def __init__(self, fold_id: str, data: Optional[dict[str, Any]] = None):
        """
        Initialize a write-once memory fold.

        Args:
            fold_id: Unique identifier for this fold
            data: Initial fold data
        """
        super().__init__(fold_id, data)
        self._sealed = False
        self._seal_timestamp: Optional[datetime] = None

    def seal(self) -> None:
        """
        Seal the fold, making it immutable.

        After sealing, no further mutations are allowed.
        """
        if not self._sealed:
            self._sealed = True
            self._seal_timestamp = datetime.utcnow()

    def is_sealed(self) -> bool:
        """Check if the fold is sealed."""
        return self._sealed

    def get_seal_timestamp(self) -> Optional[datetime]:
        """Get the timestamp when the fold was sealed."""
        return self._seal_timestamp

    def _check_sealed(self) -> None:
        """Raise exception if fold is sealed."""
        if self._sealed:
            raise FoldSealedError(
                f"Cannot mutate sealed fold '{self.fold_id}' "
                f"(sealed at {self._seal_timestamp.isoformat()})"
            )

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the fold.

        Args:
            key: Data key
            value: Value to store

        Raises:
            FoldSealedError: If fold is sealed
        """
        self._check_sealed()
        super().set(key, value)

    def update(self, updates: dict[str, Any]) -> None:
        """
        Update multiple values.

        Args:
            updates: Dictionary of key-value pairs to update

        Raises:
            FoldSealedError: If fold is sealed
        """
        self._check_sealed()
        super().update(updates)

    def delete(self, key: str) -> None:
        """
        Delete a key from the fold.

        Args:
            key: Key to delete

        Raises:
            FoldSealedError: If fold is sealed
        """
        self._check_sealed()
        super().delete(key)

    def to_dict(self) -> dict[str, Any]:
        """Convert fold to dictionary representation."""
        result = super().to_dict()
        result["sealed"] = self._sealed
        if self._seal_timestamp:
            result["seal_timestamp"] = self._seal_timestamp.isoformat()
        return result


class FoldManager:
    """Manages memory folds with optional immutability enforcement."""

    def __init__(self, immutability: bool = False):
        """
        Initialize fold manager.

        Args:
            immutability: If True, use WriteOnceFold for new folds
        """
        self.immutability = immutability
        self.folds: dict[str, MemoryFold] = {}

    def create_fold(self, fold_id: str, data: Optional[dict[str, Any]] = None) -> MemoryFold:
        """
        Create a new memory fold.

        Args:
            fold_id: Unique identifier for the fold
            data: Initial data

        Returns:
            Created MemoryFold or WriteOnceFold based on settings
        """
        fold = WriteOnceFold(fold_id, data) if self.immutability else MemoryFold(fold_id, data)

        self.folds[fold_id] = fold
        return fold

    def get_fold(self, fold_id: str) -> Optional[MemoryFold]:
        """
        Get a fold by ID.

        Args:
            fold_id: Fold identifier

        Returns:
            MemoryFold if found, None otherwise
        """
        return self.folds.get(fold_id)

    def save_fold(self, fold: MemoryFold, seal_if_write_once: bool = True) -> None:
        """
        Save a fold to storage.

        Args:
            fold: Fold to save
            seal_if_write_once: If True and fold is WriteOnceFold, seal it after save
        """
        # In a real implementation, this would persist to a backend
        self.folds[fold.fold_id] = fold

        if seal_if_write_once and isinstance(fold, WriteOnceFold):
            fold.seal()

    def list_folds(self) -> list[str]:
        """List all fold IDs."""
        return list(self.folds.keys())


if __name__ == "__main__":
    # Demonstration
    print("=== Write-Once Fold Demo ===\n")

    # Create a write-once fold
    fold = WriteOnceFold("fold_001")
    fold.set("key1", "value1")
    fold.update({"key2": "value2", "key3": "value3"})

    print(f"Before sealing: {fold.to_dict()}")
    print(f"Is sealed: {fold.is_sealed()}\n")

    # Seal the fold
    fold.seal()
    print(f"After sealing: {fold.to_dict()}")
    print(f"Is sealed: {fold.is_sealed()}\n")

    # Try to mutate - should raise exception
    try:
        fold.set("key4", "value4")
        print("ERROR: Should have raised FoldSealedError!")
    except FoldSealedError as e:
        print(f"✓ Caught expected error: {e}\n")

    # Demonstrate FoldManager with immutability
    print("=== FoldManager with immutability=True ===\n")
    manager = FoldManager(immutability=True)
    managed_fold = manager.create_fold("managed_001", {"initial": "data"})

    print(f"Created fold type: {type(managed_fold).__name__}")
    print(f"Is WriteOnceFold: {isinstance(managed_fold, WriteOnceFold)}")

    # Save and auto-seal
    manager.save_fold(managed_fold, seal_if_write_once=True)
    print(f"After save, is sealed: {managed_fold.is_sealed()}")
