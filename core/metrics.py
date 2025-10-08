"""LUKHAS Core Metrics backed by centralized LUKHAS Prometheus registry.

These factories are duplicate-tolerant and register into a shared
registry so repeated imports or pytest collection won't throw:
    ValueError: Duplicated timeseries in CollectorRegistry
"""
from __future__ import annotations

from typing import Any

# Use centralized, duplicate-tolerant registry
from lukhas.observability import counter, gauge, histogram, summary

# For backward compatibility with code that checks this flag
try:
    from prometheus_client import Summary as _PrometheusCheck  # type: ignore
    PROMETHEUS_AVAILABLE = True
    Summary = _PrometheusCheck  # export for compatibility
except ImportError:  # pragma: no cover
    PROMETHEUS_AVAILABLE = False
    class Summary:  # type: ignore
        def __init__(self, *a, **k): pass
        def observe(self, *a, **k): pass


# Router metrics ------------------------------------------------------------
router_no_rule_total = counter(
    "lukhas_router_no_rule_total",
    "Signals that matched no routing rule",
    labelnames=("signal_type", "producer_module"),
)

router_signal_processing_time = histogram(
    "lukhas_router_signal_processing_seconds",
    "Time spent processing signals in router",
    labelnames=("signal_type", "routing_strategy"),
)

router_cascade_preventions_total = counter(
    "lukhas_router_cascade_preventions_total",
    "Number of signals blocked by cascade prevention",
    labelnames=("producer_module",),
)

# Network health metrics ----------------------------------------------------
network_coherence_score = gauge(
    "lukhas_network_coherence_score",
    "Current network coherence score (0-1)",
)

network_active_nodes = gauge(
    "lukhas_network_active_nodes",
    "Number of active nodes in the network",
)

# Bio-symbolic processing metrics -------------------------------------------
bio_processor_signals_total = counter(
    "lukhas_bio_processor_signals_total",
    "Total signals processed by bio-symbolic processor",
    labelnames=("pattern_type",),
)

bio_processor_adaptations_total = counter(
    "lukhas_bio_processor_adaptations_total",
    "Total adaptations applied by bio-symbolic processor",
    labelnames=("adaptation_rule",),
)

# Public exports ------------------------------------------------------------
__all__ = [
    "router_no_rule_total",
    "router_signal_processing_time",
    "router_cascade_preventions_total",
    "network_coherence_score",
    "network_active_nodes",
    "bio_processor_signals_total",
    "bio_processor_adaptations_total",
    "PROMETHEUS_AVAILABLE",
    "Summary",
]
