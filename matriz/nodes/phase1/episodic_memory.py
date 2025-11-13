from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .base import Node, NodeContext, NodeMetrics
from .events import NodeEvent, emit_event

@dataclass
class EpisodicMemory(Node):
    """
    Append‑only autobiographical episodes with time/context/affect.
    process(...):
      - append: bool = True -> appends {'time','context','affect','payload'}
      - query_last: int -> returns last N episodes (most recent last)
    """
    name: str = "episodic_memory"
    _episodes: List[Dict[str, Any]] = field(default_factory=list)
    _m: NodeMetrics = field(default_factory=NodeMetrics)

    def configure(self, **kwargs: Any) -> None:
        pass

    def warmup(self, ctx: NodeContext) -> None:
        # keep episodes across cycles by default; no clear unless requested
        pass

    def process(self, ctx: NodeContext, **inputs: Any) -> Dict[str, Any]:
        if inputs.get("append"):
            episode = {
                "time": inputs.get("time"),
                "context": inputs.get("context", {}),
                "affect": inputs.get("affect", {}),
                "payload": inputs.get("payload", {}),
                "cycle_idx": ctx.cycle_idx,
            }
            self._episodes.append(episode)
            emit_event(NodeEvent(node=self.name, run_id=ctx.run_id, cycle_idx=ctx.cycle_idx,
                                 payload={"op": "append"}))
            return {"count": len(self._episodes)}
        qn: Optional[int] = inputs.get("query_last")
        if qn is not None:
            result = self._episodes[-qn:] if qn > 0 else []
            return {"episodes": list(result)}
        return {"count": len(self._episodes)}

    def metrics(self) -> NodeMetrics:
        return self._m
