"""Memory subsystem Prometheus metrics helpers."""

from __future__ import annotations

import os
from typing import Optional

# ΛTAG: memory_metrics -- deterministic lane-aware Prometheus instruments
try:
    from prometheus_client import Counter, Gauge, Histogram
except Exception:  # pragma: no cover - Prometheus optional dependency

    class _NoopMetric:
        def labels(self, *_, **__):  # type: ignore[return-value]
            return self

        def inc(self, *_, **__):
            return None

        def set(self, *_, **__):
            return None

        def observe(self, *_, **__):
            return None

    Gauge = Counter = Histogram = _NoopMetric  # type: ignore


def _resolve_lane(explicit_lane: Optional[str] = None) -> str:
    """Resolve the effective lane label for metrics."""
    lane = (explicit_lane or os.getenv("LUKHAS_LANE", "experimental")).strip().lower()
    return lane or "unknown"


if isinstance(Gauge, type):  # Prometheus available
    MEMORY_FOLD_COUNT = Gauge(
        "lukhas_memory_fold_count",
        "Active memory folds per lane",
        ["lane"],
    )
    MEMORY_CASCADE_EVENTS = Counter(
        "lukhas_memory_cascade_events_total",
        "Cascade prevention activations",
        ["lane"],
    )
    MEMORY_RECALL_LATENCY = Histogram(
        "lukhas_memory_recall_latency_seconds",
        "Memory recall latency distribution",
        ["lane", "result"],
        buckets=[
            0.001,
            0.005,
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
        ],
    )
else:  # pragma: no cover - Prometheus optional dependency fallback
    MEMORY_FOLD_COUNT = Gauge()
    MEMORY_CASCADE_EVENTS = Counter()
    MEMORY_RECALL_LATENCY = Histogram()


def observe_fold_count(count: int, lane: Optional[str] = None) -> None:
    """Set the gauge representing active fold count."""
    MEMORY_FOLD_COUNT.labels(lane=_resolve_lane(lane)).set(max(count, 0))


def increment_cascade_events(lane: Optional[str] = None) -> None:
    """Increment the cascade prevention counter."""
    MEMORY_CASCADE_EVENTS.labels(lane=_resolve_lane(lane)).inc()


def observe_recall_latency(latency_seconds: float, result: str, lane: Optional[str] = None) -> None:
    """Record memory recall latency histogram sample."""
    # ΛTAG: metrics_cardinality -- normalise result labels
    normalized = result if result in {"hit", "miss", "dry_run", "error"} else "unknown"
    MEMORY_RECALL_LATENCY.labels(
        lane=_resolve_lane(lane),
        result=normalized,
    ).observe(max(latency_seconds, 0.0))


__all__ = [
    "observe_fold_count",
    "increment_cascade_events",
    "observe_recall_latency",
]
