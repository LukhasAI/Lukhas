"""Touch test to ensure coverage properly measures lukhas code."""


def test_imports_touch():
    """Import stable entry points so coverage sees them."""
    import labs.governance.auth_governance_policies as _pol
    import core.common.exceptions as _exc

    assert _exc is not None
    assert _pol is not None
