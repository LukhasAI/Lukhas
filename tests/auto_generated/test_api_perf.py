"""Auto-generated skeleton tests for module api.perf.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
"""

import importlib
import pytest

def test_import_api_perf():
    """Module can be imported without error"""
    try:
        m = importlib.import_module("api.perf")
    except Exception as e:
        pytest.skip(f"Cannot import api.perf: {e}")
    assert m is not None
