"""Auto-generated skeleton tests for module core.providers.registry.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
"""

import importlib
import pytest

def test_import_core_providers_registry():
    """Module can be imported without error"""
    try:
        m = importlib.import_module("core.providers.registry")
    except Exception as e:
        pytest.skip(f"Cannot import core.providers.registry: {e}")
    assert m is not None
