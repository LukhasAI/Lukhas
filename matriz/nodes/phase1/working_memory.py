from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .base import Node, NodeContext, NodeMetrics
from .events import NodeEvent, emit_event


@dataclass
class WorkingMemory(Node):
    """
    Bounded, recency-biased store (7±2 by default).
    Exposes simple push semantics via `item=...` in process().
    """
    name: str = "working_memory"
    capacity: int = 7
    _items: List[Dict[str, Any]] = field(default_factory=list)
    _metrics: NodeMetrics = field(default_factory=NodeMetrics)

    def configure(self, **kwargs: Any) -> None:
        self.capacity = int(kwargs.get("capacity", self.capacity))

    def warmup(self, ctx: NodeContext) -> None:
        self._items.clear()

    def process(self, ctx: NodeContext, **inputs: Any) -> Dict[str, Any]:
        item = inputs.get("item")
        if item is not None:
            self._items.append(item)
            if len(self._items) > self.capacity:
                # Simple eviction: drop oldest
                self._items.pop(0)
                self._metrics.counters["wm_evictions"] = self._metrics.counters.get("wm_evictions", 0) + 1
        emit_event(NodeEvent(node=self.name, run_id=ctx.run_id, cycle_idx=ctx.cycle_idx,
                             payload={"size": len(self._items)}))
        return {"wm_items": list(self._items)}

    def metrics(self) -> NodeMetrics:
        return self._metrics
