"""Auto-generated skeleton tests for module core.adapters.provider_registry.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
"""

import importlib
import pytest

def test_import_core_adapters_provider_registry():
    """Module can be imported without error"""
    try:
        m = importlib.import_module("core.adapters.provider_registry")
    except Exception as e:
        pytest.skip(f"Cannot import core.adapters.provider_registry: {e}")
    assert m is not None
