import importlib


def test_lid_import_and_normalize():
    # Import the governance.identity package and access lid helper
    identity_pkg = importlib.import_module("lukhas.governance.identity")

    # `lid` may be a callable that returns the module; handle both
    lid_module = identity_pkg.lid() if callable(identity_pkg.lid) else identity_pkg.lid

    assert lid_module is not None, "lid helper should be available"

    # Basic behavior
    assert hasattr(lid_module, "normalize_lid")
    assert lid_module.normalize_lid("LAMBDA:User123") == "user123"
