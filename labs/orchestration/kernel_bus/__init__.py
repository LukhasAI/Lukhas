"""Bridge for candidate.orchestration.kernel_bus."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import List

__all__: List[str] = []
_BACKEND: ModuleType | None = None

for _candidate in (
    "labs.candidate.orchestration.kernel_bus",
    "lukhas_website.orchestration.kernel_bus",
    "orchestration.kernel_bus",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    _BACKEND = _mod
    for _attr in dir(_mod):
        if _attr.startswith("_"):
            continue
        globals()[_attr] = getattr(_mod, _attr)
        if _attr not in __all__:
            __all__.append(_attr)
    break


def __getattr__(name: str):
    if _BACKEND and hasattr(_BACKEND, name):
        value = getattr(_BACKEND, name)
        globals()[name] = value
        if name not in __all__:
            __all__.append(name)
        return value
    raise AttributeError(name)
