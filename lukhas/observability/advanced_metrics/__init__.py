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

# Advanced metrics system class
class AdvancedMetricsSystem:
    """Centralized advanced metrics system for LUKHAS observability."""

    def __init__(self):
        self.router_cascade_preventions_total = router_cascade_preventions_total
        self.network_coherence_score = network_coherence_score
        self.signal_processing_time_seconds = signal_processing_time_seconds
        self.cache_hits_total = cache_hits_total
        self.cache_misses_total = cache_misses_total
        self.queue_depth = queue_depth

    def record_cache_hit(self, cache: str):
        """Record cache hit."""
        self.cache_hits_total.labels(cache=cache).inc()

    def record_cache_miss(self, cache: str):
        """Record cache miss."""
        self.cache_misses_total.labels(cache=cache).inc()

    def set_queue_depth(self, name: str, depth: int):
        """Set queue depth gauge."""
        self.queue_depth.labels(name=name).set(depth)

__all__ = [
    "router_cascade_preventions_total",
    "network_coherence_score",
    "signal_processing_time_seconds",
    "cache_hits_total",
    "cache_misses_total",
    "queue_depth",
    "AdvancedMetricsSystem",
]

# Added for test compatibility (lukhas.observability.advanced_metrics.AnomalyType)
try:
    from candidate.observability.advanced_metrics import AnomalyType  # noqa: F401
except ImportError:
    from enum import Enum

    class AnomalyType(Enum):
        """Stub for AnomalyType."""
        UNKNOWN = "unknown"
        DEFAULT = "default"
try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "AnomalyType" not in __all__:
    __all__.append("AnomalyType")
