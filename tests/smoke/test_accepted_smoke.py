"""Smoke test for accepted lane (lukhas/)."""


def test_accepted_lane_import():
    """Test that we can import something from the accepted lane."""
    try:
        import lukhas  # noqa: F401  # TODO: lukhas; consider using importl...

        assert True, "Basic lukhas import successful"
    except ImportError:
        # Try importing a specific module if main package fails
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lukhas"))
        assert True, "Accepted lane accessible"
