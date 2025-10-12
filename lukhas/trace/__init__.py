"""
Bridge for `lukhas.trace` (e.g., TraceRepairEngine).
Prefers richest backends; falls back to a no-op engine.
"""
from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import List

__all__: List[str] = []
_SRC: ModuleType | None = None

def _bind(modname: str) -> bool:
    global _SRC, __all__
    try:
        m = import_module(modname)
    except Exception:
        return False
    _SRC = m
    __all__ = [n for n in dir(m) if not n.startswith("_")]
    return True

# Define fallback symbols first
class TraceRepairEngine:
    def repair(self, records):
        n = len(records) if hasattr(records, "__len__") else 0
        return {"repaired": 0, "n": n, "status": "noop"}

# Richest → leanest sources
for _mod in (
    "labs.trace",
    "lukhas_website.lukhas.trace",
    "trace",
):
    if _bind(_mod):
        break

# Update __all__ to include fallback if not already present
if "TraceRepairEngine" not in __all__:
    __all__.append("TraceRepairEngine")

if _SRC is not None:
    # Delegate attributes to the bound source module, but keep our fallbacks
    def __getattr__(name: str):
        # Try source first, fall back to our own module
        try:
            return getattr(_SRC, name)
        except AttributeError:
            # Let Python handle the normal AttributeError
            raise
