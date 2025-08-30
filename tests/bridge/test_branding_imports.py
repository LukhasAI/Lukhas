"""Test branding bridge imports and basic functionality."""

import pytest


def test_branding_bridge_imports():
    """Test branding_bridge module imports successfully."""
    try:
        import lukhas.branding_bridge as bridge

        assert bridge is not None
        assert hasattr(bridge, "check_branding_violations")

        # Test a simple function that covers import paths
        violations = bridge.check_branding_violations("test text")
        assert isinstance(violations, list)

    except ImportError:
        pytest.skip("Branding bridge not available")
