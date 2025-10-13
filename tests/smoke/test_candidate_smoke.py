"""Smoke test for labs lane."""


def test_labs_lane_accessible(labs_root):
    """Test that labs lane directory is accessible."""
    assert labs_root.exists(), "Labs lane directory exists"
    assert labs_root.is_dir(), "Labs lane is a directory"
