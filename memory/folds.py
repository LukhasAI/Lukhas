"""
memory/folds.py

FoldGuard with circuit breaker for memory cascade prevention.

Usage:
  from memory.folds import FoldGuard
  guard = FoldGuard(max_fanout=8, max_depth=4, window_budget=256)
  guard.start_tick()
  if guard.allow(fanout=3, depth=2):
      # proceed with memory operation
"""
from __future__ import annotations
from dataclasses import dataclass

try:
    from prometheus_client import Counter
    MEM_BREAKS = Counter("lukhas_memory_circuit_breaks_total", "Memory circuit trips")
    PROM = True
except Exception:
    PROM = False
    class _No:
        def inc(self,*_): pass
    MEM_BREAKS = _No()

@dataclass
class FoldGuard:
    max_fanout: int = 8
    max_depth: int = 4
    window_budget: int = 256

    def __post_init__(self):
        self._ops = 0
        self._fan = 0
        self._depth = 0
        self.tripped = False

    def start_tick(self):
        self._ops = 0; self._fan = 0; self._depth = 0; self.tripped = False

    def allow(self, fanout: int, depth: int, cost: int = 1) -> bool:
        if self.tripped: return False
        self._fan += fanout
        self._depth = max(self._depth, depth)
        self._ops += cost
        ok = (self._fan <= self.max_fanout and
              self._depth <= self.max_depth and
              self._ops <= self.window_budget)
        if not ok:
            self.tripped = True
            if PROM: MEM_BREAKS.inc()
        return ok

    @property
    def window(self) -> int: return self._fan
    @property
    def ops(self) -> int: return self._ops
    @property
    def depth(self) -> int: return self._depth