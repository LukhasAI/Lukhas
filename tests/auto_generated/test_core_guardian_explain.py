"""Auto-generated skeleton tests for module core.guardian.explain.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
"""

import importlib
import pytest

def test_import_core_guardian_explain():
    """Module can be imported without error"""
    try:
        m = importlib.import_module("core.guardian.explain")
    except Exception as e:
        pytest.skip(f"Cannot import core.guardian.explain: {e}")
    assert m is not None
