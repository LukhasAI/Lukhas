"""
Core Metrics - Canonical Public API
Bridge to core.metrics (single source of truth)

Exports Prometheus metrics for monitoring and observability
"""
from core.metrics import (
    PROMETHEUS_AVAILABLE,
    bio_processor_adaptations_total,
    bio_processor_signals_total,
    network_active_nodes,
    network_coherence_score,
    router_cascade_preventions_total,
    router_no_rule_total,
    router_signal_processing_time,
)

__all__ = [
    "PROMETHEUS_AVAILABLE",
    "bio_processor_adaptations_total",
    "bio_processor_signals_total",
    "network_active_nodes",
    "network_coherence_score",
    "router_cascade_preventions_total",
    "router_no_rule_total",
    "router_signal_processing_time",
]
