"""Test core.metrics bridge exports and contract."""

import pytest


def test_metrics_exports():
    """Verify core.metrics bridge exports expected symbols."""
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

    # Verify metrics exist
    assert isinstance(PROMETHEUS_AVAILABLE, bool)
    # Metrics are either Counter/Gauge/Histogram or noop stubs
    assert hasattr(router_cascade_preventions_total, "inc")
    assert hasattr(network_coherence_score, "set")
    assert hasattr(router_signal_processing_time, "observe")


def test_metrics_single_source_of_truth():
    """Verify metrics come from core.metrics module."""
    from core.metrics import router_cascade_preventions_total

    # Metrics are defined in core.metrics.py directly
    # Just verify it's callable/usable
    assert hasattr(router_cascade_preventions_total, "inc")


def test_metrics_all_defined():
    """Verify __all__ is properly defined."""
    import core.metrics as metrics

    assert hasattr(metrics, "__all__")
    assert isinstance(metrics.__all__, list)
    assert len(metrics.__all__) == 8
    assert "router_cascade_preventions_total" in metrics.__all__
