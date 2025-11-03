"""Bridge for core.common (+ real 'exceptions' submodule).

Exports from the richest available backend (core.common preferred).
Also provides real exceptions submodule for explicit imports.
"""
from __future__ import annotations

from importlib import import_module
from typing import List, Optional

__all__: List[str] = []
_SRC: object | None = None

def _bind(modname: str) -> bool:
    global _SRC, __all__
    try:
        m = import_module(modname)
    except Exception:
        return False
    _SRC = m
    __all__ = [n for n in dir(m) if not n.startswith("_")]
    # Guarantee `exceptions` symbol is present for `from core.common import exceptions`
    if "exceptions" not in __all__:
        __all__.append("exceptions")
    return True

for _mod in (
    "labs.core.common",
    "core.common",
    "lukhas_website.core.common",
):
    if _bind(_mod):
        break
else:
    # Minimal fallback (package still presents `exceptions` submodule)
    pass

# Always expose our submodule path
from . import exceptions  # noqa: E402  (ensures attr exists even if backend lacks it)

if _SRC is not None:
    def __getattr__(name: str):
        return getattr(_SRC, name)
