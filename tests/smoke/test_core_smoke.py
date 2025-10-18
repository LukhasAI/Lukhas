"""Smoke test for core lane (now at root level after Phase 5B)."""

import os


def test_core_lane_import():
    """Test that we can access the core module at root level."""
    # After Phase 5B: core/ is at project root, not under lukhas/
    core_dir = os.path.join(os.path.dirname(__file__), "../../core")
    assert os.path.exists(core_dir), "Core directory exists at root level"
    assert os.path.isdir(core_dir), "Core is a directory"
    
    # Verify core/__init__.py exists
    core_init = os.path.join(core_dir, "__init__.py")
    assert os.path.exists(core_init), "Core module is properly initialized"
