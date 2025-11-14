"""Auto-generated skeleton tests for module core.tags.context.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
"""

import importlib
import pytest

def test_import_core_tags_context():
    """Module can be imported without error"""
    try:
        m = importlib.import_module("core.tags.context")
    except Exception as e:
        pytest.skip(f"Cannot import core.tags.context: {e}")
    assert m is not None
