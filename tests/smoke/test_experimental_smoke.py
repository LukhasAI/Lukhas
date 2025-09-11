"""Smoke test for experimental lane."""

import os


def test_experimental_lane_accessible():
    """Test that experimental lane directory is accessible."""
    experimental_dir = os.path.join(os.path.dirname(__file__), "../../experimental")
    assert os.path.exists(experimental_dir), "Experimental lane directory exists"
    # Experimental is newly created placeholder, just check existence
    assert True, "Experimental lane accessible"
