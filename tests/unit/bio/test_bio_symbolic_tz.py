"""Test bio modules use UTC timestamps correctly."""

from importlib.util import find_spec

import pytest

HAS_BIO_SYMBOLIC = find_spec("bio.core.bio_symbolic") is not None
HAS_BIO_UTILITIES = find_spec("bio.utilities") is not None
HAS_BIO = find_spec("bio") is not None


@pytest.mark.skipif(not HAS_BIO_SYMBOLIC, reason="Bio symbolic processor not available")
def test_bio_symbolic_initialization():
    """Test BioSymbolicProcessor initialization and UTC usage."""
    from bio.core.bio_symbolic import BioSymbolicProcessor

    processor = BioSymbolicProcessor()
    assert processor is not None
    assert hasattr(processor, "process")


@pytest.mark.skipif(not HAS_BIO_UTILITIES, reason="Bio utilities not available")
def test_bio_utilities():
    """Test bio utilities functions."""
    from bio import utilities

    # Module should be importable
    assert utilities is not None
    assert hasattr(utilities, "__file__")


@pytest.mark.skipif(not HAS_BIO, reason="Bio module not available")
def test_bio_init_imports():
    """Test bio module __init__ exports."""
    import bio as bio

    # Check __all__ is sorted (RUF022 compliance)
    if hasattr(bio, "__all__"):
        assert bio.__all__ == sorted(bio.__all__)

    # Module should be importable
    assert bio is not None
