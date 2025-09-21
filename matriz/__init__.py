"""Compatibility package providing lowercase access to MATRIZ modules."""
# ΛTAG: matriz_lowercase_shim
import importlib
import sys

_upper = importlib.import_module("MATRIZ")
core_module = importlib.import_module("MATRIZ.core")

sys.modules[__name__ + ".core"] = core_module

__all__ = ["core"]
