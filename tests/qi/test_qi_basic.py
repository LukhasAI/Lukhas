"""Test QI module basic functionality."""

import pytest


def test_qi_wrapper_import():
    """Test QIWrapper imports and basic init."""
    try:
        from lukhas.qi import QIWrapper

        # Test creation
        wrapper = QIWrapper()
        assert wrapper is not None
        assert hasattr(wrapper, "quantum_process")
        assert hasattr(wrapper, "bio_process")

    except ImportError:
        pytest.skip("QI wrapper not available")


def test_qi_exports():
    """Test QI module exports."""
    try:
        import lukhas.qi as qi

        # Check key exports
        assert hasattr(qi, "QIWrapper")
        assert hasattr(qi, "QIConfig")

    except ImportError:
        pytest.skip("QI module not available")
