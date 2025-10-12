"""Bridge for ConsciousnessStream surface."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

__all__: list[str] = []

_CANDIDATES = (
    "labs.consciousness.consciousness_stream",
    "consciousness.consciousness_stream",
    "lukhas_website.lukhas.consciousness.consciousness_stream",
)

_backend: ModuleType | None = None
for _module in _CANDIDATES:
    try:
        _backend = import_module(_module)
        break
    except Exception:  # pragma: no cover - best effort bridge
        continue

if _backend:
    for _name, _value in vars(_backend).items():
        if not _name.startswith("_"):
            globals()[_name] = _value
            __all__.append(_name)
else:

    class ConsciousnessStream:
        """Fallback consciousness stream implementation."""

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def start(self) -> None:
            """Begin stream processing (noop)."""

        def stop(self) -> None:
            """Stop stream processing (noop)."""

        def emit(self, *args, **kwargs) -> None:
            """Best-effort emit hook."""

    __all__ = ["ConsciousnessStream"]
