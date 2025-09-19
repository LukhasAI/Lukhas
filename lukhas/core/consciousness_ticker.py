"""
core/consciousness_ticker.py

Consciousness tick routing with ring buffer decimation and backpressure handling.

Usage:
  from core.consciousness_ticker import ConsciousnessTicker
  ct = ConsciousnessTicker(fps=30, cap=120)
  ct.start()
"""
from lukhas.core.clock import Ticker
from lukhas.core.ring import Ring
from time import perf_counter

try:
    from prometheus_client import Histogram, Counter
    TICK = Histogram("lukhas_tick_duration_seconds","Tick time",["lane"])
    TICKS_DROPPED = Counter("lukhas_ticks_dropped_total","Dropped ticks",["lane"])
    SUB_EXC = Counter("lukhas_subscriber_exceptions_total","Subscriber exceptions",["lane"])
    PROM=True
except Exception:
    class _N:
        def labels(self,*_,**__): return self
        def observe(self,*_): pass
        def inc(self,*_): pass
    TICK=_N(); TICKS_DROPPED=_N(); SUB_EXC=_N(); PROM=False

import os
LANE = os.getenv("LUKHAS_LANE","experimental")

class ConsciousnessTicker:
    def __init__(self, fps: int = 30, cap: int = 120):
        self.ticker = Ticker(fps=fps)
        self.buffer = Ring(capacity=cap)
        self.ticker.subscribe(self._on_tick)

    def _on_tick(self, tick_count: int):
        t0 = perf_counter()
        try:
            frame = {"id": tick_count}  # keep it deterministic for tests
            self.buffer.push(frame)
            if len(self.buffer) > int(self.buffer.capacity * 0.8):
                self._decimate()
        except Exception:
            SUB_EXC.labels(lane=LANE).inc()
            raise
        finally:
            dur = perf_counter() - t0
            TICK.labels(lane=LANE).observe(dur)

    def _decimate(self):
        frames = self.buffer.pop_all()
        keep = frames[-(self.buffer.capacity // 2):]
        for f in keep:
            self.buffer.push(f)
        # A "drop" is conceptual at the coordinator level too
        TICKS_DROPPED.labels(lane=LANE).inc()

    def start(self, seconds: int = 0):
        """Start the consciousness ticker"""
        self.ticker.run(seconds=seconds)

    def stop(self):
        """Stop the consciousness ticker"""
        self.ticker.running = False