"""Bridge for `candidate.core.tagging`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.lukhas.candidate.core.tagging
  2) candidate.candidate.core.tagging
  3) core.tagging

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []


def _try(module_name: str):
    try:
        return import_module(module_name)
    except Exception:  # pragma: no cover - best effort bridge
        return None


_CANDIDATES = (
    "lukhas_website.lukhas.candidate.core.tagging",
    "candidate.candidate.core.tagging",
    "core.tagging",
)

_SRC = None
for _candidate in _CANDIDATES:
    module = _try(_candidate)
    if module:
        _SRC = module
        for name in dir(module):
            if not name.startswith("_"):
                globals()[name] = getattr(module, name)
                __all__.append(name)
        break


if "DeduplicationCache" not in globals():
    class DeduplicationCache:
        """Stub for DeduplicationCache."""

        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    __all__.append("DeduplicationCache")


def __getattr__(name: str):
    if _SRC:
        module_dict = getattr(_SRC, "__dict__", {})
        if name in module_dict:
            return module_dict[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
