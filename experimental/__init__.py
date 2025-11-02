"""
Compatibility package for experimental/ → labs/ migration.

Legacy code may import from 'experimental.*' - this shim re-exports
everything from 'labs' (formerly candidate) for backward compatibility.

Phase 2: candidate → labs rename complete
Phase 3: This compatibility layer deprecated, will be removed in v1.0
"""

import importlib as _importlib

# Re-export everything from labs (formerly candidate)
try:
    _labs_mod = _importlib.import_module("labs")
except Exception:
    _labs_mod = None

if _labs_mod is not None:
    _names = getattr(_labs_mod, "__all__", None)
    if _names is None:
        _names = [n for n in dir(_labs_mod) if not n.startswith("_")]
    for _name in _names:
        globals()[_name] = getattr(_labs_mod, _name)
    __all__ = list(_names)
else:
    __all__ = []
