def test_constellation_shims_imports():
    """Ensure both the new Constellation triad and legacy branding.trinity import.

    This test is intentionally minimal: it verifies the import surface so shims
    remain functional during migration.
    """
    # Import new path
    import importlib

    triad = importlib.import_module("constellation.triad")
    assert hasattr(triad, "Identity")

    # Import legacy shim
    legacy = importlib.import_module("branding.trinity")
    assert hasattr(legacy, "Identity")
