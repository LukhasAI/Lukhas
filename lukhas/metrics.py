# lukhas/metrics.py
"""
Prometheus metrics (optional). Falls back to no-op if client missing.
Env:
- ENABLE_PROM=1 to start an exporter on PROM_PORT (default 9108)
"""

from __future__ import annotations
import os
from contextlib import contextmanager

try:
    from prometheus_client import Counter, Histogram, start_http_server  # type: ignore
except Exception:  # pragma: no cover
    Counter = Histogram = None
    start_http_server = None


ENABLED = os.getenv("ENABLE_PROM", "0") == "1"
if ENABLED and start_http_server is not None:
    try:
        start_http_server(int(os.getenv("PROM_PORT", "9108")))
    except Exception:
        pass


def _noop_histogram(*_labels):
    @contextmanager
    def _timer():
        yield
    return _timer()


class _NoopCounter:
    def labels(self, *_args, **_kwargs): return self
    def inc(self, *_args, **_kwargs): pass


class _NoopHistogram:
    def labels(self, *_args, **_kwargs): return self
    def time(self): return _noop_histogram()


if Counter is None or Histogram is None:
    stage_latency = _NoopHistogram()
    stage_timeouts = _NoopCounter()
    guardian_band = _NoopCounter()
else:
    stage_latency = Histogram("matriz_stage_latency_seconds", "Latency per stage", ["stage"])
    stage_timeouts = Counter("matriz_stage_timeouts_total", "Timeouts per stage", ["stage"])
    guardian_band = Counter("guardian_risk_band_total", "Decisions per risk band", ["band"])

__all__ = ["stage_latency", "stage_timeouts", "guardian_band"]