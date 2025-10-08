"""Bridge for candidate.nodes."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

__all__: list[str] = []

_CANDIDATES = (
    "lukhas_website.lukhas.candidate.nodes",
    "candidate.candidate.nodes",
    "lukhas.nodes",
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
    from lukhas.nodes import Graph, Node, NodeId  # type: ignore  # noqa: F401

    __all__.extend(["NodeId", "Node", "Graph"])

try:
    from . import example_nodes  # noqa: F401
except Exception:
    pass

__all__ = [name for name in globals().keys() if not name.startswith("_")]
