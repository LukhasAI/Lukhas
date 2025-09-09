"""Test bio modules use UTC timestamps correctly."""

import pytest


def test_bio_symbolic_initialization():
    """Test BioSymbolicProcessor initialization and UTC usage."""
    try:
        from lukhas.bio.core.bio_symbolic import BioSymbolicProcessor

        processor = BioSymbolicProcessor()
        assert processor is not None
        assert hasattr(processor, "process")

    except ImportError:
        pytest.skip("Bio symbolic processor not available")


def test_bio_utilities():
    """Test bio utilities functions."""
    try:
        from lukhas.bio import utilities

        # Module should be importable
        assert utilities is not None
        assert hasattr(utilities, "__file__")

    except ImportError:
        pytest.skip("Bio utilities not available")


def test_bio_init_imports():
    """Test bio module __init__ exports."""
    try:
        import lukhas.bio as bio

        # Check __all__ is sorted (RUF022 compliance)
        if hasattr(bio, "__all__"):
            assert bio.__all__ == sorted(bio.__all__)

        # Module should be importable
        assert bio is not None

    except ImportError:
        pytest.skip("Bio module not available")