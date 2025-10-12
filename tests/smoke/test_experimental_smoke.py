"""Smoke test for experimental lane."""

import os

import pytest


def test_experimental_lane_accessible():
    """Test that experimental lane directory is accessible (NOTE: experimental was renamed to candidate)."""
    # Experimental lane was renamed to 'candidate', so this test now just passes
    # as the migration is complete
    candidate_dir = os.path.join(os.path.dirname(__file__), "../../candidate")
    assert os.path.exists(candidate_dir), "Candidate lane (formerly experimental) directory exists"


def test_candidate_lane_accessible():
    """Test that candidate lane directory is accessible."""
    candidate_dir = os.path.join(os.path.dirname(__file__), "../../candidate")
    assert os.path.exists(candidate_dir), "Candidate lane directory exists"
    assert os.path.isdir(candidate_dir), "Candidate lane is a directory"
