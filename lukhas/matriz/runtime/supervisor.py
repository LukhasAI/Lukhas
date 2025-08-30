from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EdgeBudget:
    from_id: str
    to_id: str
    p95_budget_ms: float = 25.0
    drop_on_breach: bool = True


@dataclass
class RuntimeSupervisor:
    """
    Minimal runtime envelope.
    - Tracks per-edge latency samples.
    - Applies simple drop-on-breach policy when p95 estimate exceeds budget.
    - Placeholder hooks for constitutional and safety checks.
    """

    edges: list[EdgeBudget]
    p95_window: int = 200
    latencies_ms: dict[tuple[str, str], list[float]] = field(default_factory=dict)

    def observe_edge_latency(self, from_id: str, to_id: str, latency_ms: float) -> bool:
        key = (from_id, to_id)
        buf = self.latencies_ms.setdefault(key, [])
        buf.append(float(latency_ms))
        if len(buf) > self.p95_window:
            del buf[: len(buf) - self.p95_window]
        return self._within_budget(from_id, to_id)

    def _within_budget(self, from_id: str, to_id: str) -> bool:
        key = (from_id, to_id)
        samples = list(self.latencies_ms.get(key, ()))
        if not samples:
            return True
        samples.sort()
        p95_idx = max(0, int(0.95 * (len(samples) - 1)))
        p95 = samples[p95_idx]
        budget = next(
            (e.p95_budget_ms for e in self.edges if e.from_id == from_id and e.to_id == to_id), 25.0
        )
        return p95 <= budget

    def should_drop(self, from_id: str, to_id: str) -> bool:
        budget = next((e for e in self.edges if e.from_id == from_id and e.to_id == to_id), None)
        if not budget:
            return False
        if budget.drop_on_breach and not self._within_budget(from_id, to_id):
            return True
        return False
