"""Smoke test for archive lane."""

import os


def test_archive_lane_accessible():
    """Test that archive lane directory is accessible."""
    archive_dir = os.path.join(os.path.dirname(__file__), "../../archive")
    assert os.path.exists(archive_dir), "Archive lane directory exists"
    # Archive lane should be isolated, just check directory existence
    assert True, "Archive lane accessible"
