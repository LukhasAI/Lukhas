"""Bridge for candidate.consciousness.types."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

__all__: list[str] = []

_CANDIDATES = (
    "lukhas_website.lukhas.candidate.consciousness.types",
    "labs.candidate.consciousness.types",
    "consciousness.types",
)

_backend: ModuleType | None = None
for _module in _CANDIDATES:
    try:
        _backend = import_module(_module)
        break
    except Exception:  # pragma: no cover
        continue

if _backend:
    for _name, _value in vars(_backend).items():
        if not _name.startswith("_"):
            globals()[_name] = _value
            __all__.append(_name)
