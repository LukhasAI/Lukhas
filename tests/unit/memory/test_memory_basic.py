"""Test memory module basic functionality."""

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
