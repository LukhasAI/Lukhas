"""Reflection engine facade that bridges multiple backends."""
from __future__ import annotations

from importlib import import_module

__all__ = ["ReflectionEngine", "ReflectionEntry", "AlignmentScore", "ReflectionConfig"]

_CANDIDATES = (
    "labs.consciousness.reflection_engine",
    "lukhas_website.lukhas.consciousness.reflection_engine",
    "consciousness.reflection_engine",
    "consciousness.reflection",
)


def _grab(name: str):
    for module in _CANDIDATES:
        try:
            mod = import_module(module)
        except Exception:
            continue
        if hasattr(mod, name):
            return getattr(mod, name)
    return None


for _name in list(__all__):
    value = _grab(_name)
    if value is not None:
        globals()[_name] = value


if "ReflectionEntry" not in globals():
    class ReflectionEntry:  # type: ignore[misc]
        def __init__(self, text: str = "") -> None:
            self.text = text


if "AlignmentScore" not in globals():
    class AlignmentScore:  # type: ignore[misc]
        def __init__(self, score: float = 0.0) -> None:
            self.score = score


if "ReflectionEngine" not in globals():
    class ReflectionEngine:  # type: ignore[misc]
        def run(self, *args, **kwargs):
            return [ReflectionEntry("noop")]


if "ReflectionConfig" not in globals():
    class ReflectionConfig:  # type: ignore[misc]
        def __init__(self, **kwargs) -> None:
            self.options = kwargs
