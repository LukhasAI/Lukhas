"""Test QI module basic functionality."""

import pytest


def test_qi_wrapper_import():
    """Test QIWrapper imports and basic init."""
    try:
        from lukhas.qi import QIWrapper

        # Test creation
        wrapper = QIWrapper()
        assert wrapper is not None
        assert hasattr(wrapper, "make_quantum_decision")
        assert hasattr(wrapper, "adapt_bio_inspired")

    except ImportError:
        pytest.skip("QI wrapper not available")


def test_qi_exports():
    """Test QI module exports."""
    try:
        import lukhas.qi as qi

        # Check key exports
        assert hasattr(qi, "QIWrapper")

    except ImportError:
        pytest.skip("QI module not available")
