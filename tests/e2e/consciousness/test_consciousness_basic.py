"""Test consciousness module basic functionality."""

from datetime import timezone

import pytest


def test_consciousness_wrapper_import():
    """Test ConsciousnessWrapper imports and basic init."""
    try:
        from consciousness import ConsciousnessWrapper

        # Test creation with default config
        wrapper = ConsciousnessWrapper()
        assert wrapper is not None
        # Check for actual method that exists
        assert hasattr(wrapper, "check_awareness")

    except ImportError:
        pytest.skip("Consciousness wrapper not available")


def test_consciousness_exports():
    """Test consciousness module exports."""
    try:
        import consciousness as consciousness

        # Check key exports exist
        assert hasattr(consciousness, "ConsciousnessWrapper")

    except ImportError:
        pytest.skip("Consciousness module not available")


def test_consciousness_state_uses_utc():
    """Ensure ConsciousnessState timestamps are timezone-aware in UTC."""
    try:
        from consciousness.consciousness_wrapper import ConsciousnessState

        state = ConsciousnessState()
        assert state.last_update.tzinfo == timezone.utc  # ΛTAG: utc
    except ImportError:
        pytest.skip("ConsciousnessState not available")
