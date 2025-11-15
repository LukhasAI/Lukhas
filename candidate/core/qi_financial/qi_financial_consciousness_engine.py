"""Shim exposing labs qi financial consciousness engine for candidate tests."""

from __future__ import annotations

import sys
from importlib import import_module

# Avoid circular import when loaded via spec_from_file_location
_target_module = "labs.core.qi_financial.qi_financial_consciousness_engine"
if __name__ == _target_module and _target_module in sys.modules:
    # We are being loaded as the target module via importlib.util.spec_from_file_location
    # Remove ourselves temporarily to allow the real import
    _self = sys.modules.pop(_target_module)
    _MODULE = import_module(_target_module)
    sys.modules[_target_module] = _self
else:
    _MODULE = import_module(_target_module)

__all__ = getattr(_MODULE, "__all__", [name for name in dir(_MODULE) if not name.startswith("_")])
for _name in __all__:
    globals()[_name] = getattr(_MODULE, _name)
