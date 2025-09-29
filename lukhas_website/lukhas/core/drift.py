"""
core/drift.py

DriftScore v2 - windowed cosine similarity with EMA smoothing and per-lane thresholds.

Usage:
  from core.drift import DriftMonitor
  monitor = DriftMonitor(lane="experimental")
  result = monitor.update(intent=[1.0, 0.0], action=[0.9, 0.1])
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import math
import os

# Optional metrics
try:
    from prometheus_client import Gauge
    DRIFT_EMA = Gauge("lukhas_drift_ema", "EMA drift", ["lane"])
    PROM = True
except Exception:
    PROM = False
    class _Noop:  # minimal no-op
        def labels(self, *_, **__): return self
        def set(self, *_): pass
    DRIFT_EMA = _Noop()

@dataclass(frozen=True)
class DriftConfig:
    warn_threshold: float
    block_threshold: float
    alpha: float = 0.2
    window: int = 64  # small, bounded

LANE_CFG: Dict[str, DriftConfig] = {
    "experimental": DriftConfig(0.30, 0.50),
    "candidate":    DriftConfig(0.20, 0.35),
    "prod":         DriftConfig(0.15, 0.25),
}

def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b): return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    na  = math.sqrt(sum(x*x for x in a))
    nb  = math.sqrt(sum(y*y for y in b))
    if na == 0.0 or nb == 0.0: return 0.0
    # Clamp to avoid FP wobble
    v = max(-1.0, min(1.0, dot/(na*nb)))
    return v

class DriftMonitor:
    __slots__ = ("lane","cfg","ema","_raw")
    def __init__(self, lane: Optional[str] = None):
        self.lane = (lane or os.getenv("LUKHAS_LANE", "experimental")).lower()
        self.cfg  = LANE_CFG.get(self.lane, LANE_CFG["experimental"])
        self.ema: float = 0.0
        self._raw: List[float] = []

    def update(self, intent: List[float], action: List[float]) -> Dict[str, object]:
        sim   = _cosine(intent, action)
        drift = 1.0 - sim

        # windowed raw drift
        self._raw.append(drift)
        if len(self._raw) > self.cfg.window:
            self._raw.pop(0)

        # EMA smoothing
        self.ema = self.cfg.alpha * drift + (1.0 - self.cfg.alpha) * self.ema

        # decision
        guardian = "allow"
        if self.ema >= self.cfg.block_threshold:
            guardian = "block"
        elif self.ema >= self.cfg.warn_threshold:
            guardian = "warn"

        if PROM:
            DRIFT_EMA.labels(lane=self.lane).set(self.ema)

        return {
            "lane": self.lane,
            "drift": drift,
            "ema": self.ema,
            "guardian": guardian,
            "n": len(self._raw),
        }