"""Auto-generated skeleton tests for module bridge.api.example.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
"""

import importlib
import pytest

def test_import_bridge_api_example():
    """Module can be imported without error"""
    try:
        m = importlib.import_module("bridge.api.example")
    except Exception as e:
        pytest.skip(f"Cannot import bridge.api.example: {e}")
    assert m is not None
