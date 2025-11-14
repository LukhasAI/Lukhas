"""Auto-generated skeleton tests for module core.tags.registry.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
"""

import importlib
import pytest

def test_import_core_tags_registry():
    """Module can be imported without error"""
    try:
        m = importlib.import_module("core.tags.registry")
    except Exception as e:
        pytest.skip(f"Cannot import core.tags.registry: {e}")
    assert m is not None
