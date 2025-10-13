"""Smoke test for experimental/labs lane."""


def test_experimental_lane_accessible(labs_root):
    """Test that experimental lane directory is accessible (labs is the successor)."""
    assert labs_root.exists(), "Labs lane (formerly experimental/candidate) directory exists"


def test_labs_lane_accessible(labs_root):
    """Test that labs lane directory is accessible."""
    assert labs_root.exists(), "Labs lane directory exists"
    assert labs_root.is_dir(), "Labs lane is a directory"
