"""Aka_qualia bridge contract tests."""

import importlib as I


def test_aka_qualia_root():
    """aka_qualia root package imports successfully."""
    m = I.import_module("aka_qualia")
    assert hasattr(m, "__all__")


def test_aka_qualia_core():
    """aka_qualia.core subpackage imports successfully."""
    m = I.import_module("aka_qualia.core")
    # Optional features; presence proves bridge works
    assert hasattr(m, "__all__")
