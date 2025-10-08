"""Example node library bridge."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Any

__all__: list[str] = []

_CANDIDATES = (
    "lukhas_website.lukhas.nodes.example_nodes",
    "candidate.nodes.example_nodes",
    "core.matrix.example_nodes",
    "nodes.example_nodes",
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

    class EchoNode:
        """Fallback echo node returning provided value."""

        def __init__(self, value: Any = None):
            self.value = value

        def compute(self, x: Any = None) -> Any:
            return self.value if x is None else x

    class SumNode:
        """Fallback sum node aggregating numeric inputs."""

        def compute(self, *values: Any) -> float:
            return sum(v for v in values if isinstance(v, (int, float)))

    __all__ = ["EchoNode", "SumNode"]
