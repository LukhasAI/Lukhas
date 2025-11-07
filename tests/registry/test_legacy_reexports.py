#!/usr/bin/env python3
"""Ensure legacy registry helpers remain import-compatible."""

import importlib
from typing import Any

import pytest


def test_package_exports_legacy_helpers(monkeypatch):
    """`from core.registry import register` should expose legacy helpers."""
    import core.registry as pkg

    # Snapshot registry state for clean-up
    original_reg = dict(pkg._REG)  # type: ignore[attr-defined]

    try:
        register = pkg.register
        resolve = pkg.resolve
        autoload = pkg.autoload

        assert callable(register)
        assert callable(resolve)
        assert callable(autoload)

        unique_kind = "test:legacy_reexport"
        test_obj: dict[str, Any] = {"value": 1}

        register(unique_kind, test_obj)
        assert resolve(unique_kind) is test_obj

    finally:
        pkg._REG.clear()  # type: ignore[attr-defined]
        pkg._REG.update(original_reg)  # type: ignore[attr-defined]


def test_module_and_package_share_registry():
    """Importing via module path keeps state consistent with package imports."""
    pkg = importlib.import_module("core.registry")
    legacy_module = importlib.import_module("core._registry_legacy")

    unique_kind = "test:module_share"
    sentinel = object()

    snapshot = dict(pkg._REG)  # type: ignore[attr-defined]
    try:
        pkg.register(unique_kind, sentinel)
        assert legacy_module.resolve(unique_kind) is sentinel
    finally:
        pkg._REG.clear()  # type: ignore[attr-defined]
        pkg._REG.update(snapshot)  # type: ignore[attr-defined]


@pytest.fixture(autouse=True)
def ensure_reload():
    """Reload the package to ensure legacy module is initialised for each test."""
    import sys

    for name in [
        "core.registry",
        "core._registry_legacy",
    ]:
        if name in sys.modules:
            del sys.modules[name]
    importlib.import_module("core.registry")
    yield
