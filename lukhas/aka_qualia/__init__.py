"""
Bridge for `lukhas.aka_qualia` expected by integration tests.
Search order: website → candidate → root; provides subpackages via shims.
"""
from __future__ import annotations

from importlib import import_module
from typing import List, Optional

__all__: List[str] = []
_SRC: Optional[object] = None

def _bind(modname: str) -> bool:
    global _SRC, __all__
    try:
        m = import_module(modname)
    except Exception:
        return False
    _SRC = m
    __all__ = [n for n in dir(m) if not n.startswith("_")]
    # ensure common subpackages appear as attrs too
    for name in ("core", "lukhas.memory", "metrics"):
        if name not in __all__:
            __all__.append(name)
    return True

for _mod in (
    "lukhas_website.lukhas.aka_qualia",
    "labs.aka_qualia",
    "aka_qualia",
):
    if _bind(_mod):
        break
else:
    # Minimal facade if nothing is available
    __all__ = ["core", "lukhas.memory", "metrics"]

if _SRC is not None:
    def __getattr__(name: str):
        return getattr(_SRC, name)
