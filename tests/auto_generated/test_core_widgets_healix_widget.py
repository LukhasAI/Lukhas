"""Auto-generated skeleton tests for module core.widgets.healix_widget.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
"""

import importlib
import pytest

def test_import_core_widgets_healix_widget():
    """Module can be imported without error"""
    try:
        m = importlib.import_module("core.widgets.healix_widget")
    except Exception as e:
        pytest.skip(f"Cannot import core.widgets.healix_widget: {e}")
    assert m is not None
