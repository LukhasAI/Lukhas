from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Dict, Protocol


@dataclass(frozen=True)
class NodeContext:
    """
    Immutable per-cycle context passed into every node.
    Budget fields are advisory limits; nodes should instrument themselves.
    """
    run_id: str
    cycle_idx: int
    seed: int
    latency_budget_ms: int = 20
    memory_budget_bytes: int = 1_000_000

@dataclass
class NodeMetrics:
    p95_ms: float = 0.0
    rss_bytes: int = 0
    counters: Dict[str, int] = field(default_factory=dict)
    gauges: Dict[str, float] = field(default_factory=dict)

class Node(Protocol):
    """Minimal contract all Phase‑1 nodes implement."""
    name: str
    def configure(self, **kwargs: Any) -> None: ...
    def warmup(self, ctx: NodeContext) -> None: ...
    def process(self, ctx: NodeContext, **inputs: Any) -> Dict[str, Any]: ...
    def metrics(self) -> NodeMetrics: ...

class NodeRegistry:
    """Simple registry to resolve nodes by name; used by compose stub."""
    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}

    def register(self, node: Node) -> None:
        if node.name in self._nodes:
            raise ValueError(f"duplicate node: {node.name}")
        self._nodes[node.name] = node

    def get(self, name: str) -> Node:
        return self._nodes[name]

    def all(self) -> Mapping[str, Node]:
        return dict(self._nodes)
