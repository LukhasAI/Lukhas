"""Test memory module basic functionality."""

from unittest.mock import patch
from importlib.util import find_spec

import pytest

HAS_MEMORY_WRAPPER = find_spec("memory.MemoryWrapper") is not None
HAS_FOLD_SYSTEM = find_spec("memory.fold_system") is not None
HAS_MEMORY_CONFIG = find_spec("memory.config") is not None
HAS_LABS_FOLD_SYSTEM = find_spec("labs.memory.fold_system") is not None


@pytest.mark.skipif(not HAS_MEMORY_WRAPPER, reason="Memory wrapper not available")
def test_memory_wrapper_import():
    """Test MemoryWrapper imports and basic init."""
    from memory import MemoryWrapper

    # Test creation with default config
    wrapper = MemoryWrapper()
    assert wrapper is not None
    assert hasattr(wrapper, "access_memory")
    assert hasattr(wrapper, "create_fold")


@pytest.mark.skipif(not HAS_FOLD_SYSTEM, reason="Fold system not available")
def test_fold_system_import():
    """Test fold system imports."""
    from memory import fold_system

    # Check key functions and classes
    assert hasattr(fold_system, "FoldManager")
    assert hasattr(fold_system, "get_fold_manager")


@pytest.mark.skipif(not HAS_MEMORY_CONFIG, reason="Memory config not available")
def test_memory_config():
    """Test memory configuration."""
    from memory.config import MemoryConfig

    # Test default config creation
    config = MemoryConfig()
    assert config is not None
    assert hasattr(config, "max_folds")


@pytest.mark.skipif(not HAS_LABS_FOLD_SYSTEM, reason="Fold system not available")
def test_fold_manager_metrics_hooks():
    """Ensure FoldManager emits Prometheus hooks for key operations."""
    from labs.memory.fold_system import FoldManager

    with (
        patch("memory.fold_system.observe_fold_count") as mock_count,
        patch("memory.fold_system.observe_recall_latency") as mock_latency,
        patch("memory.fold_system.increment_cascade_events") as mock_cascade,
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
