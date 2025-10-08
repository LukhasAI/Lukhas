"""Bridge for consciousness.reflection_engine."""

from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []

for _candidate in (
    "lukhas_website.lukhas.consciousness.reflection_engine",
    "lukhas.consciousness.reflection_engine",
    "candidate.consciousness.reflection_engine",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    for _attr in dir(_mod):
        if _attr.startswith("_"):
            continue
        globals()[_attr] = getattr(_mod, _attr)
        if _attr not in __all__:
            __all__.append(_attr)
    break
