"""Smoke test for accepted lane (now at root level after Phase 5B flattening)."""

import importlib


def test_accepted_lane_import():
    """Test that we can import core modules from the root level (post-Phase 5B)."""
    # After Phase 5B, lukhas/ directory was removed and modules flattened to root
    # Test core module imports that should work
    try:
        importlib.import_module("core")
        assert True, "Core module import successful"
    except ImportError as e:
        # Core should be importable
        raise AssertionError(f"Failed to import core module: {e}")
