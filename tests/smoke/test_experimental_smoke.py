"""Smoke test for experimental lane."""

import os
import pytest


@pytest.mark.xfail(reason="Experimental lane renamed to 'candidate' directory")
def test_experimental_lane_accessible():
    """Test that experimental lane directory is accessible."""
    experimental_dir = os.path.join(os.path.dirname(__file__), "../../experimental")
    assert os.path.exists(experimental_dir), "Experimental lane directory exists"
    # Experimental is newly created placeholder, just check existence
    assert True, "Experimental lane accessible"


def test_candidate_lane_accessible():
    """Test that candidate lane directory is accessible."""
    candidate_dir = os.path.join(os.path.dirname(__file__), "../../candidate")
    assert os.path.exists(candidate_dir), "Candidate lane directory exists"
    assert os.path.isdir(candidate_dir), "Candidate lane is a directory"
