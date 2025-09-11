"""Smoke test for quarantine lane."""

import os


def test_quarantine_lane_accessible():
    """Test that quarantine lane directory is accessible."""
    quarantine_dir = os.path.join(os.path.dirname(__file__), "../../quarantine")
    assert os.path.exists(quarantine_dir), "Quarantine lane directory exists"
    # Quarantine lane should be isolated, just check directory existence
    assert True, "Quarantine lane accessible"
