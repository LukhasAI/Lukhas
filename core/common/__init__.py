"""Bridge for core.common (+ real 'exceptions' submodule).

Exports from the richest available backend (core.common preferred).
Also provides real exceptions submodule for explicit imports.
"""
from __future__ import annotations

import sys
from importlib import import_module
# Always expose our submodule path
from . import exceptions

__all__: list[str] = []
_SRC: object | None = None

def _bind(modname: str) -> bool:
    global _SRC, __all__
    try:
        m = import_module(modname)
    except Exception:
        return False
    # Skip if we imported ourselves (circular reference protection)
    if m is sys.modules.get(__name__):
        return False
    _SRC = m
    __all__ = [n for n in dir(m) if not n.startswith("_")]
    # Guarantee `exceptions` symbol is present for `from core.common import exceptions`
    if "exceptions" not in __all__:
        __all__.append("exceptions")
    return True

for _mod in (
    "core.common",
    "lukhas_website.core.common",
):
    if _bind(_mod):
        break
else:
    # Minimal fallback - load from shadowed core/common.py file
    import importlib.util
    from pathlib import Path
    _common_file = Path(__file__).parent.parent / "common.py"
    if _common_file.exists():
        spec = importlib.util.spec_from_file_location("core._common_module", _common_file)
        if spec and spec.loader:
            _common_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_common_mod)
            _SRC = _common_mod
            __all__ = [n for n in dir(_common_mod) if not n.startswith("_")]
            if "exceptions" not in __all__:
                __all__.append("exceptions")

if _SRC is not None:
    def __getattr__(name: str):
        if _SRC is None:
            raise AttributeError(f"module 'core.common' has no attribute '{name}'")
        try:
            return getattr(_SRC, name)
        except AttributeError:
            raise AttributeError(f"module 'core.common' has no attribute '{name}'") from None
