"""Compatibility shim: make `MATRIZ` package alias the existing `matriz` package.

This is a minimal, reversible shim intended for local test runs only.
It sets the package `MATRIZ` to use the same __path__ as `matriz`, so imports
like `from MATRIZ.adapters.foo import Bar` resolve to `matriz.adapters.foo`.
"""
import importlib
import sys
try:
    matriz = importlib.import_module("matriz")
    # Make this package expose the same submodule search path as matriz
    __path__ = getattr(matriz, "__path__", __path__)
    # Re-export public names for convenience (not strictly necessary)
    for _name in dir(matriz):
        if not _name.startswith("__"):
            try:
                globals()[_name] = getattr(matriz, _name)
            except Exception:
                pass
except Exception:
    # If anything fails, leave an empty package to avoid import crashes
    pass
