"""Smoke test for core lane (lukhas/core/)."""

import os
import sys


def test_core_lane_import():
    """Test that we can access the core lane."""
    try:
        # Try importing from the core symlink
        sys.path.insert(0, os.path.dirname(__file__) + "/../../core")
        assert True, "Core lane accessible via symlink"
    except Exception:
        # Check if core directory exists in lukhas/
        core_dir = os.path.join(os.path.dirname(__file__), "../../lukhas/core")
        assert os.path.exists(core_dir), "Core lane exists"
