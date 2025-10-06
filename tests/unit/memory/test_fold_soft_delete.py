from __future__ import annotations

from datetime import datetime, timedelta

from candidate.memory.fold_system import FoldManager

# ΛTAG: memory_soft_delete_test


def test_soft_delete_allows_restore() -> None:
    manager = FoldManager()
    fold = manager.create_fold({"content": "test"}, mode="live")
    assert fold.id in manager.folds

    manager._soft_delete(fold)
    assert fold.id not in manager.folds
    assert fold.id in manager.deleted_folds
    assert fold.deleted_at is not None

    restored = manager.restore_fold(fold.id)
    assert restored is not None
    assert restored.deleted_at is None
    assert fold.id in manager.folds


def test_purge_expired_soft_deletes() -> None:
    manager = FoldManager()
    fold = manager.create_fold({"content": "expire"}, mode="live")
    manager._soft_delete(fold)
    assert fold.id in manager.deleted_folds

    # Force expiry
    fold.deleted_at = datetime.now() - timedelta(days=10)
    manager._purge_expired_soft_deletes()
    assert fold.id not in manager.deleted_folds
