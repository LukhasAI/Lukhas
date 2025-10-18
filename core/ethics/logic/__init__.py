"""Bridge: core.ethics.logic."""
from __future__ import annotations

from importlib import import_module

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "labs.core.ethics.logic",
    "core.ethics.logic",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)


def _try(module_name: str):
    try:
        return import_module(module_name)
    except Exception:
        return None


for candidate in _CANDIDATES:
    module = _try(candidate)
    if module:
        for attr in dir(module):
            if not attr.startswith("_"):
                globals()[attr] = getattr(module, attr)
                __all__.append(attr)
        break
