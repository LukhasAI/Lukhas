"""Shim exposing labs qi financial consciousness engine for candidate tests."""

from __future__ import annotations

from importlib import import_module

_MODULE = import_module("labs.core.qi_financial.qi_financial_consciousness_engine")
__all__ = getattr(_MODULE, "__all__", [name for name in dir(_MODULE) if not name.startswith("_")])
for _name in __all__:
    globals()[_name] = getattr(_MODULE, _name)
