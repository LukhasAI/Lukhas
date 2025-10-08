"""Bridge for ConsciousnessWrapper surface."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Any

__all__: list[str] = []

_CANDIDATES = (
    "candidate.consciousness.consciousness_wrapper",
    "consciousness.consciousness_wrapper",
    "lukhas_website.lukhas.consciousness.consciousness_wrapper",
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
else:

    class ConsciousnessWrapper:
        """Fallback wrapper stub."""

        def __init__(self, engine: Any = None):
            self.engine = engine

        def run(self, *args: Any, **kwargs: Any) -> Any:
            """Return neutral result."""
            return None

    __all__ = ["ConsciousnessWrapper"]
