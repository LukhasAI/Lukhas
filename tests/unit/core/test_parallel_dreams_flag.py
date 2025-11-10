"""
Unit tests for parallel dreams feature flag wiring.

Tests Task 4: Dynamic engine switching based on PARALLEL_DREAMS_ENABLED flag.
Validates that get_dream_engine() returns appropriate engine configuration.

Note: Uses mocking to avoid RecursionError in memory/backends/base (known issue).
"""
import os
import pytest
from unittest.mock import Mock, patch


@pytest.fixture(autouse=True)
def reset_dream_module():
    """Reset dream module state before and after each test"""
    # Save original values
    original_dreams_enabled = os.environ.get("DREAMS_ENABLED")
    original_parallel_enabled = os.environ.get("PARALLEL_DREAMS_ENABLED")

    # Clear environment variables
    os.environ.pop("DREAMS_ENABLED", None)
    os.environ.pop("PARALLEL_DREAMS_ENABLED", None)

    yield

    # Restore original environment
    if original_dreams_enabled is not None:
        os.environ["DREAMS_ENABLED"] = original_dreams_enabled
    else:
        os.environ.pop("DREAMS_ENABLED", None)

    if original_parallel_enabled is not None:
        os.environ["PARALLEL_DREAMS_ENABLED"] = original_parallel_enabled
    else:
        os.environ.pop("PARALLEL_DREAMS_ENABLED", None)


def test_sequential_engine_by_default():
    """Test that sequential engine is used when PARALLEL_DREAMS_ENABLED=false"""
    os.environ["DREAMS_ENABLED"] = "true"
    os.environ["PARALLEL_DREAMS_ENABLED"] = "false"

    import lukhas_website.lukhas.dream as dream_module

    # Mock the import inside get_dream_engine to avoid RecursionError
    mock_instance = Mock()
    mock_instance.config = {}

    # We need to mock the import that happens inside get_dream_engine()
    # Patch the module path that will be imported
    import sys
    mock_dream_engine_module = Mock()
    mock_dream_engine_class = Mock(return_value=mock_instance)
    mock_dream_engine_module.DreamEngine = mock_dream_engine_class

    sys.modules["lukhas_website.lukhas.consciousness.dream_engine"] = mock_dream_engine_module

    try:
        # Clear module cache to force new import
        dream_module._dream_engine = None

        # Call get_dream_engine - it will import and use our mocked DreamEngine
        engine = dream_module.get_dream_engine()

        # Verify DreamEngine was called with config containing mode="sequential"
        mock_dream_engine_class.assert_called_once()
        call_args = mock_dream_engine_class.call_args

        # Extract config argument
        if call_args.kwargs and "config" in call_args.kwargs:
            config = call_args.kwargs["config"]
        elif call_args.args:
            config = call_args.args[0] if isinstance(call_args.args[0], dict) else {}
        else:
            config = {}

        assert config.get("mode") == "sequential", \
            f"Expected mode='sequential', got {config.get('mode')}"

    finally:
        # Cleanup mock from sys.modules
        if "lukhas_website.lukhas.consciousness.dream_engine" in sys.modules:
            del sys.modules["lukhas_website.lukhas.consciousness.dream_engine"]


def test_parallel_engine_when_enabled():
    """Test that parallel engine is used when PARALLEL_DREAMS_ENABLED=true"""
    os.environ["DREAMS_ENABLED"] = "true"
    os.environ["PARALLEL_DREAMS_ENABLED"] = "true"

    import lukhas_website.lukhas.dream as dream_module

    mock_instance = Mock()
    mock_instance.config = {}

    import sys
    mock_dream_engine_module = Mock()
    mock_dream_engine_class = Mock(return_value=mock_instance)
    mock_dream_engine_module.DreamEngine = mock_dream_engine_class

    sys.modules["lukhas_website.lukhas.consciousness.dream_engine"] = mock_dream_engine_module

    try:
        dream_module._dream_engine = None

        engine = dream_module.get_dream_engine()

        mock_dream_engine_class.assert_called_once()
        call_args = mock_dream_engine_class.call_args

        if call_args.kwargs and "config" in call_args.kwargs:
            config = call_args.kwargs["config"]
        elif call_args.args:
            config = call_args.args[0] if isinstance(call_args.args[0], dict) else {}
        else:
            config = {}

        assert config.get("mode") == "parallel", \
            f"Expected mode='parallel', got {config.get('mode')}"

    finally:
        if "lukhas_website.lukhas.consciousness.dream_engine" in sys.modules:
            del sys.modules["lukhas_website.lukhas.consciousness.dream_engine"]


def test_engine_switches_when_flag_changes():
    """Test that engine is recreated when flag changes at runtime"""
    import lukhas_website.lukhas.dream as dream_module
    import sys

    mock_instance1 = Mock()
    mock_instance1.config = {"mode": "sequential"}
    mock_instance2 = Mock()
    mock_instance2.config = {"mode": "parallel"}

    mock_dream_engine_module = Mock()
    mock_dream_engine_class = Mock(side_effect=[mock_instance1, mock_instance2])
    mock_dream_engine_module.DreamEngine = mock_dream_engine_class

    sys.modules["lukhas_website.lukhas.consciousness.dream_engine"] = mock_dream_engine_module

    try:
        # Start with sequential
        os.environ["DREAMS_ENABLED"] = "true"
        os.environ["PARALLEL_DREAMS_ENABLED"] = "false"
        dream_module._dream_engine = None

        # Get first engine (sequential)
        engine1 = dream_module.get_dream_engine()
        engine1_id = id(engine1)

        # Change flag to parallel
        os.environ["PARALLEL_DREAMS_ENABLED"] = "true"
        dream_module._dream_engine = None  # Clear cache to trigger recreation

        # Get second engine (parallel)
        engine2 = dream_module.get_dream_engine()
        engine2_id = id(engine2)

        # Should be different instances
        assert engine1_id != engine2_id, "Engine should be recreated when flag changes"
        assert mock_dream_engine_class.call_count == 2, "DreamEngine should be instantiated twice"

    finally:
        if "lukhas_website.lukhas.consciousness.dream_engine" in sys.modules:
            del sys.modules["lukhas_website.lukhas.consciousness.dream_engine"]


def test_raises_error_when_dreams_disabled():
    """Test that RuntimeError is raised when DREAMS_ENABLED=false"""
    os.environ["DREAMS_ENABLED"] = "false"

    import importlib
    import lukhas_website.lukhas.dream as dream_module
    importlib.reload(dream_module)

    dream_module._dream_engine = None

    with pytest.raises(RuntimeError, match="Dreams subsystem not enabled"):
        dream_module.get_dream_engine()


def test_flag_reading():
    """Test that flags are read correctly from environment"""
    os.environ["DREAMS_ENABLED"] = "true"
    os.environ["PARALLEL_DREAMS_ENABLED"] = "true"

    import importlib
    import lukhas_website.lukhas.dream as dream_module
    importlib.reload(dream_module)

    assert dream_module.DREAMS_ENABLED is True
    assert dream_module.PARALLEL_DREAMS_ENABLED is True

    os.environ["PARALLEL_DREAMS_ENABLED"] = "false"
    importlib.reload(dream_module)

    assert dream_module.PARALLEL_DREAMS_ENABLED is False
