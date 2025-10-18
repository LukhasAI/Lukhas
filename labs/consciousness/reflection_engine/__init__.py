"""Bridge for candidate.consciousness.reflection_engine."""

from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []

for _candidate in (
    "labs.candidate.consciousness.reflection_engine",
    "lukhas_website.consciousness.reflection_engine",
    "consciousness.reflection_engine",
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


if "ReflectionConfig" not in globals():

    class ReflectionConfig:
        def __init__(self, **kwargs):
            self.options = kwargs

    __all__.append("ReflectionConfig")
