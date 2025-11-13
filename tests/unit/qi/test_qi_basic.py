"""Test QI module basic functionality."""

from importlib.util import find_spec

import pytest

HAS_QI_WRAPPER = find_spec("qi.QIWrapper") is not None
HAS_QI = find_spec("qi") is not None


@pytest.mark.skipif(not HAS_QI_WRAPPER, reason="QI wrapper not available")
def test_qi_wrapper_import():
    """Test QIWrapper imports and basic init."""
    from qi import QIWrapper

    # Test creation
    wrapper = QIWrapper()
    assert wrapper is not None
    assert hasattr(wrapper, "quantum_process")
    assert hasattr(wrapper, "bio_process")


@pytest.mark.skipif(not HAS_QI, reason="QI module not available")
def test_qi_exports():
    """Test QI module exports."""
    import qi as qi

    # Check key exports
    assert hasattr(qi, "QIWrapper")
    assert hasattr(qi, "QIConfig")
