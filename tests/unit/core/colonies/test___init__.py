from core.colonies.__init__ import __all__


def test_package_metadata():
    """
    Test that the package's __all__ variable is defined.
    This ensures that the package's public API is explicitly declared.
    """
    assert isinstance(__all__, list)
