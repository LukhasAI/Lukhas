"""Test consciousness module basic functionality."""

import pytest


def test_consciousness_wrapper_import():
    """Test ConsciousnessWrapper imports and basic init."""
    try:
        from lukhas.consciousness import ConsciousnessWrapper
        
        # Test creation with default config
        wrapper = ConsciousnessWrapper()
        assert wrapper is not None
        # Check for actual method that exists
        assert hasattr(wrapper, 'check_awareness')
        
    except ImportError:
        pytest.skip("Consciousness wrapper not available")


def test_consciousness_exports():
    """Test consciousness module exports."""
    try:
        import lukhas.consciousness as consciousness
        
        # Check key exports exist
        assert hasattr(consciousness, 'ConsciousnessWrapper')
        
    except ImportError:
        pytest.skip("Consciousness module not available")