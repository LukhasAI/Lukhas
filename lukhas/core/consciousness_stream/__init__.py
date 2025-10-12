"""Bridge for lukhas.core.consciousness_stream."""

from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = [
    "ConsciousnessStream",
    "StreamSnapshot",
    "ConsciousnessEvent",
]

_CANDIDATES = (
    "lukhas_website.lukhas.core.consciousness_stream",
    "core.consciousness_stream",
    "labs.core.consciousness_stream",
    "consciousness.streams",
)


def _load(name: str):
    for module in _CANDIDATES:
        try:
            mod = import_module(module)
        except Exception:
            continue
        if hasattr(mod, name):
            return getattr(mod, name)
    return None


for _name in list(__all__):
    value = _load(_name)
    if value is not None:
        globals()[_name] = value


if "StreamSnapshot" not in globals():

    class StreamSnapshot(dict):  # type: ignore[misc]
        """Fallback snapshot representation."""


if "ConsciousnessEvent" not in globals():

    class ConsciousnessEvent(dict):  # type: ignore[misc]
        """Fallback event payload."""


if "ConsciousnessStream" not in globals():

    class ConsciousnessStream:  # type: ignore[misc]
        """Fallback consciousness stream implementation."""

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def snapshot(self) -> StreamSnapshot:
            return StreamSnapshot(state="idle")

        def publish(self, event: ConsciousnessEvent) -> None:
            return None
