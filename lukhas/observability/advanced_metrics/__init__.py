"""Advanced observability metrics backed by centralized LUKHAS Prometheus registry."""
from __future__ import annotations

# Use centralized, duplicate-tolerant registry
from lukhas.observability import counter, gauge, summary

router_cascade_preventions_total = counter(
    "router_cascade_preventions_total",
    "Number of signals blocked by cascade prevention",
    labelnames=("route",),
)

network_coherence_score = gauge(
    "network_coherence_score",
    "Current network coherence score (0-1)",
)

signal_processing_time_seconds = summary(
    "signal_processing_time_seconds",
    "Time spent processing signals in router",
    labelnames=("signal_type",),
)

# Additional advanced metrics
cache_hits_total = counter(
    "cache_hits_total",
    "Cache hits",
    labelnames=("cache",),
)

cache_misses_total = counter(
    "cache_misses_total",
    "Cache misses",
    labelnames=("cache",),
)

queue_depth = gauge(
    "queue_depth",
    "Work queue depth",
    labelnames=("name",),
)

__all__ = [
    "router_cascade_preventions_total",
    "network_coherence_score",
    "signal_processing_time_seconds",
    "cache_hits_total",
    "cache_misses_total",
    "queue_depth",
]
