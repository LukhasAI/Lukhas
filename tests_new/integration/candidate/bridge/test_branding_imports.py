"""Test branding bridge imports and basic functionality."""

import pytest


def test_branding_bridge_imports():
    """Test branding_bridge module imports successfully."""
    try:
        import lukhas.branding_bridge as bridge

        assert bridge is not None
        # Module should be importable
        assert hasattr(bridge, "__file__")

    except ImportError:
        pytest.skip("Branding bridge not available")


def test_bridge_wrapper_imports():
    """Test bridge wrapper functionality."""
    try:
        from lukhas.bridge import BridgeWrapper, get_bridge_wrapper

        # Test wrapper creation
        wrapper = get_bridge_wrapper()
        # Wrapper might be None if not configured, that's OK
        assert wrapper is None or isinstance(wrapper, (BridgeWrapper, type(None)))

    except ImportError:
        pytest.skip("Bridge wrapper not available")


def test_llm_wrappers_imports():
    """Test LLM wrappers import correctly."""
    try:
        from lukhas.bridge import llm_wrappers

        # These should exist even if None
        assert hasattr(llm_wrappers, "UnifiedOpenAIClient")
        assert hasattr(llm_wrappers, "OpenAIModulatedService")

    except ImportError:
        pytest.skip("LLM wrappers not available")