"""
LUKHAS Metrics Contract and Compatibility Layer

Provides canonical metric schemas and compatibility shims for legacy aliases.
Prevents test/UI drift by normalizing metric key names across the system.
"""
from dataclasses import dataclass
from typing import Any, Dict, Mapping


@dataclass(frozen=True)
class BioProcessorStats:
    """Canonical schema for bio-symbolic processor statistics"""
    signals_processed: int
    adaptations_applied: int
    patterns_evolved: int
    coherence_violations: int
    avg_processing_time_ms: float
    adaptation_rate: float
    p95_processing_time_ms: float = 0.0
    min_processing_time_ms: float = 0.0
    max_processing_time_ms: float = 0.0


@dataclass(frozen=True)
class RouterStats:
    """Canonical schema for consciousness signal router statistics"""
    signals_processed: int
    cascade_preventions: int
    avg_routing_time_ms: float
    max_routing_time_ms: float = 0.0
    min_routing_time_ms: float = 0.0
    p95_routing_time_ms: float = 0.0
    cascade_prevention_rate: float = 0.0
    queue_overflow_rate: float = 0.0


@dataclass(frozen=True)
class NetworkMetrics:
    """Canonical schema for network health metrics"""
    total_nodes: int
    active_nodes: int
    network_coherence: float
    average_latency_ms: float
    processing_load_avg: float
    queue_utilization_avg: float
    cascade_events: int = 0
    signals_dropped: int = 0


# Legacy alias mappings for backward compatibility
LEGACY_ALIASES: Mapping[str, str] = {
    # Bio processor aliases
    "patterns_processed": "signals_processed",
    "total_processed": "signals_processed",
    "avg_processing_time": "avg_processing_time_ms",
    "adaptation_success_rate": "adaptation_rate",

    # Router aliases
    "signals_routed": "signals_processed",
    "cascade_prevented": "cascade_preventions",
    "routing_latency_avg": "avg_routing_time_ms",

    # Network aliases
    "coherence_score": "network_coherence",
    "node_count": "total_nodes",
    "active_node_count": "active_nodes",
}


def normalize_metrics(metrics_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize metrics dictionary by adding canonical keys for legacy aliases.

    Args:
        metrics_dict: Raw metrics dictionary from processor/router

    Returns:
        Dictionary with both original keys and canonical aliases
    """
    normalized = dict(metrics_dict)

    # Add canonical keys for any legacy aliases found
    for legacy_key, canonical_key in LEGACY_ALIASES.items():
        if legacy_key in normalized and canonical_key not in normalized:
            normalized[canonical_key] = normalized[legacy_key]

    return normalized


def validate_bio_processor_stats(stats: Dict[str, Any]) -> bool:
    """
    Validate that bio processor stats contain required canonical keys.

    Args:
        stats: Bio processor statistics dictionary

    Returns:
        True if all required keys are present
    """
    required_keys = {"signals_processed", "adaptations_applied", "avg_processing_time_ms"}
    return all(key in stats for key in required_keys)


def validate_router_stats(stats: Dict[str, Any]) -> bool:
    """
    Validate that router stats contain required canonical keys.

    Args:
        stats: Router statistics dictionary

    Returns:
        True if all required keys are present
    """
    required_keys = {"signals_processed", "cascade_preventions", "avg_routing_time_ms"}
    return all(key in stats for key in required_keys)


# Test helper functions for contract compliance
def assert_bio_processor_contract(stats: Dict[str, Any]) -> None:
    """Assert that bio processor stats meet the canonical contract"""
    normalized = normalize_metrics(stats)

    assert "signals_processed" in normalized, "Missing signals_processed"
    assert "adaptations_applied" in normalized, "Missing adaptations_applied"
    assert "avg_processing_time_ms" in normalized, "Missing avg_processing_time_ms"
    assert "adaptation_rate" in normalized, "Missing adaptation_rate"

    # Validate types
    assert isinstance(normalized["signals_processed"], (int, float)), "signals_processed must be numeric"
    assert isinstance(normalized["adaptations_applied"], (int, float)), "adaptations_applied must be numeric"
    assert isinstance(normalized["avg_processing_time_ms"], (float, int)), "avg_processing_time_ms must be numeric"
    assert isinstance(normalized["adaptation_rate"], (float, int)), "adaptation_rate must be numeric"


def assert_router_contract(stats: Dict[str, Any]) -> None:
    """Assert that router stats meet the canonical contract"""
    normalized = normalize_metrics(stats)

    assert "signals_processed" in normalized, "Missing signals_processed"
    assert "cascade_preventions" in normalized, "Missing cascade_preventions"
    assert "avg_routing_time_ms" in normalized, "Missing avg_routing_time_ms"

    # Validate types
    assert isinstance(normalized["signals_processed"], (int, float)), "signals_processed must be numeric"
    assert isinstance(normalized["cascade_preventions"], (int, float)), "cascade_preventions must be numeric"
    assert isinstance(normalized["avg_routing_time_ms"], (float, int)), "avg_routing_time_ms must be numeric"


# Export for easy access
__all__ = [
    "BioProcessorStats",
    "RouterStats",
    "NetworkMetrics",
    "LEGACY_ALIASES",
    "normalize_metrics",
    "validate_bio_processor_stats",
    "validate_router_stats",
    "assert_bio_processor_contract",
    "assert_router_contract",
]