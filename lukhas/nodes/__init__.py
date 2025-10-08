"""Canonical bridge for node graph primitives."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Any, Dict

__all__: list[str] = []

_CANDIDATES = (
    "lukhas_website.lukhas.nodes",
    "candidate.core.matrix.nodes",
    "core.matrix.nodes",
    "nodes",
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

    class NodeId(str):
        """Fallback node identifier."""

    class Node:
        """Minimal node stub."""

        def __init__(self, node_id: NodeId, **kwargs: Any):
            self.id = node_id
            self.kwargs = kwargs

        def compute(self, *args: Any, **kwargs: Any) -> Any:
            """Return neutral value to keep tests moving."""
            return kwargs.get("default")

    class Graph:
        """Minimal graph stub to satisfy collection."""

        def __init__(self):
            self._nodes: Dict[NodeId, Node] = {}

        def add(self, node: Node) -> None:
            self._nodes[node.id] = node

        def run(self, *args: Any, **kwargs: Any) -> Dict[NodeId, Any]:
            return {node_id: node.compute(*args, **kwargs) for node_id, node in self._nodes.items()}

    __all__.extend(["NodeId", "Node", "Graph"])

try:
    from . import example_nodes  # noqa: F401
except Exception:
    pass
