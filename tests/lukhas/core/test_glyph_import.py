"""Tests for core import structure."""

# ΛTAG: import_test

import warnings


def test_glyph_import() -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from lukhas.core import glyph

    assert hasattr(glyph, "GLYPHSymbol")
