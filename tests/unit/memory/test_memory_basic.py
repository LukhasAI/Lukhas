"""Test memory module basic functionality."""

from unittest.mock import patch

import pytest


def test_memory_wrapper_import():
    """Test MemoryWrapper imports and basic init."""
    try:
        from lukhas.memory import MemoryWrapper

        # Test creation with default config
        wrapper = MemoryWrapper()
        assert wrapper is not None
        assert hasattr(wrapper, "access_memory")
        assert hasattr(wrapper, "create_fold")

    except ImportError:
        pytest.skip("Memory wrapper not available")


def test_fold_system_import():
    """Test fold system imports."""
    try:
        from lukhas.memory import fold_system

        # Check key functions and classes
        assert hasattr(fold_system, "FoldManager")
        assert hasattr(fold_system, "get_fold_manager")

    except ImportError:
        pytest.skip("Fold system not available")


def test_memory_config():
    """Test memory configuration."""
    try:
        from lukhas.memory.config import MemoryConfig

        # Test default config creation
        config = MemoryConfig()
        assert config is not None
        assert hasattr(config, "max_folds")

    except ImportError:
        pytest.skip("Memory config not available")


def test_fold_manager_metrics_hooks():
    """Ensure FoldManager emits Prometheus hooks for key operations."""
    try:
        from lukhas.memory.fold_system import FoldManager
    except ImportError:
        pytest.skip("Fold system not available")

    with (
        patch("lukhas.memory.fold_system.observe_fold_count") as mock_count,
        patch("lukhas.memory.fold_system.observe_recall_latency") as mock_latency,
        patch("lukhas.memory.fold_system.increment_cascade_events") as mock_cascade,
    ):
        manager = FoldManager()

        assert mock_count.called  # initial gauge synchronisation
        mock_count.reset_mock()

        fold = manager.create_fold({"content": "metric"}, mode="active")
        mock_count.assert_called_with(len(manager.folds))

        mock_latency.reset_mock()
        manager.retrieve_fold(fold.id, mode="active")
        assert mock_latency.called

        mock_cascade.reset_mock()
        manager._prevent_cascade()
        assert mock_cascade.called
