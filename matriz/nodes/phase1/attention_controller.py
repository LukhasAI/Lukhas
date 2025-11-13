from __future__ import annotations
import math
from typing import Any, Dict, List
from .base import Node, NodeContext, NodeMetrics

class AttentionController(Node):
    """
    Central resource allocator.
    Inputs: scores: List[float]
    Outputs: indices of top‑k attended items and entropy (diagnostic).
    """
    name: str = "attention_controller"

    def __init__(self, top_k: int = 3, temperature: float = 1.0) -> None:
        self.top_k = top_k
        self.temperature = temperature
        self._m = NodeMetrics(counters={"conflicts": 0}, gauges={"entropy": 0.0})

    def configure(self, **kwargs: Any) -> None:
        self.top_k = int(kwargs.get("top_k", self.top_k))
        self.temperature = float(kwargs.get("temperature", self.temperature))

    def warmup(self, ctx: NodeContext) -> None:
        # nothing to reset yet
        pass

    def process(self, ctx: NodeContext, **inputs: Any) -> Dict[str, Any]:
        scores: List[float] = inputs.get("scores", [])
        if not scores:
            return {"attn": [], "entropy": 0.0}
        probs = self._softmax(scores, self.temperature)
        entropy = -sum(p * math.log(max(p, 1e-9)) for p in probs)
        self._m.gauges["entropy"] = float(entropy)
        # Select top‑k indices
        top = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[: self.top_k]
        return {"attn": top, "entropy": float(entropy)}

    def metrics(self) -> NodeMetrics:
        return self._m

    @staticmethod
    def _softmax(x: List[float], t: float) -> List[float]:
        t = max(t, 1e-6)
        ex = [math.exp(v / t) for v in x]
        s = sum(ex) or 1.0
        return [v / s for v in ex]
