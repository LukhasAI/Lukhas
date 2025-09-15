"""Smoke test for accepted lane (lukhas/)."""

import importlib
import os
import sys


def test_accepted_lane_import():
    """Test that we can import something from the accepted lane."""
    try:
        importlib.import_module("lukhas")
        assert True, "Basic lukhas import successful"
    except ImportError:
        # ΛTAG: dynamic_import
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lukhas"))
        importlib.import_module("lukhas")
        assert True, "Accepted lane accessible"
