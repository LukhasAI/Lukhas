"""Dream subsystem bridge."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

__all__: list[str] = []

_CANDIDATES = (
    "labs.consciousness.dream",
    "consciousness.dream",
    "lukhas_website.lukhas.consciousness.dream",
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
            if _name not in __all__:
                __all__.append(_name)

if "DreamEngine" not in globals():
    class DreamEngine:
        """Fallback dream engine."""

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def run(self, prompt: str, **kwargs):
            return {"dream": prompt, "insight": None}

    __all__.append("DreamEngine")
