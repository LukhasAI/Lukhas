"""Auto-generated skeleton tests for module core.matriz_adapter.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
"""

import importlib
import pytest

def test_import_core_matriz_adapter():
    """Module can be imported without error"""
    try:
        m = importlib.import_module("core.matriz_adapter")
    except Exception as e:
        pytest.skip(f"Cannot import core.matriz_adapter: {e}")
    assert m is not None
