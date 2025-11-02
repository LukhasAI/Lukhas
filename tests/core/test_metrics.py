"""Tests for LUKHAS core metrics."""
from unittest import mock
import pytest
import importlib

# Import the module so pytest-cov can see it. We will reload it under mock.
from core import metrics

@pytest.fixture
def mocked_observability():
    """Fixture to reload the metrics module with mocked observability functions."""
    with mock.patch("observability.counter") as mock_counter, \
         mock.patch("observability.gauge") as mock_gauge, \
         mock.patch("observability.histogram") as mock_histogram:
        # Reload the module to ensure the mocks are used
        importlib.reload(metrics)
        yield {
            "metrics": metrics,
            "mock_counter": mock_counter,
            "mock_gauge": mock_gauge,
            "mock_histogram": mock_histogram,
        }


def test_prometheus_availability_flag(mocked_observability):
    """Test that the PROMETHEUS_AVAILABLE flag is correctly set."""
    # This test relies on the test environment having prometheus-client installed.
    assert mocked_observability["metrics"].PROMETHEUS_AVAILABLE


def test_router_metrics_defined(mocked_observability):
    """Verify that all router-related metrics are defined."""
    metrics_module = mocked_observability["metrics"]
    mock_counter = mocked_observability["mock_counter"]
    mock_histogram = mocked_observability["mock_histogram"]

    assert metrics_module.router_no_rule_total is not None
    assert metrics_module.router_signal_processing_time is not None
    assert metrics_module.router_cascade_preventions_total is not None

    mock_counter.assert_any_call(
        "lukhas_router_no_rule_total",
        "Signals that matched no routing rule",
        labelnames=("signal_type", "producer_module"),
    )
    mock_histogram.assert_any_call(
        "lukhas_router_signal_processing_seconds",
        "Time spent processing signals in router",
        labelnames=("signal_type", "routing_strategy"),
    )
    mock_counter.assert_any_call(
        "lukhas_router_cascade_preventions_total",
        "Number of signals blocked by cascade prevention",
        labelnames=("producer_module",),
    )


def test_network_health_metrics_defined(mocked_observability):
    """Verify that all network health metrics are defined."""
    metrics_module = mocked_observability["metrics"]
    mock_gauge = mocked_observability["mock_gauge"]

    assert metrics_module.network_coherence_score is not None
    assert metrics_module.network_active_nodes is not None

    mock_gauge.assert_any_call(
        "lukhas_network_coherence_score",
        "Current network coherence score (0-1)",
    )
    mock_gauge.assert_any_call(
        "lukhas_network_active_nodes",
        "Number of active nodes in the network",
    )


def test_bio_symbolic_metrics_defined(mocked_observability):
    """Verify that all bio-symbolic processing metrics are defined."""
    metrics_module = mocked_observability["metrics"]
    mock_counter = mocked_observability["mock_counter"]

    assert metrics_module.bio_processor_signals_total is not None
    assert metrics_module.bio_processor_adaptations_total is not None

    mock_counter.assert_any_call(
        "lukhas_bio_processor_signals_total",
        "Total signals processed by bio-symbolic processor",
        labelnames=("pattern_type",),
    )
    mock_counter.assert_any_call(
        "lukhas_bio_processor_adaptations_total",
        "Total adaptations applied by bio-symbolic processor",
        labelnames=("adaptation_rule",),
    )


def test_all_exports_are_valid(mocked_observability):
    """Ensure all exported metrics are non-None."""
    metrics_module = mocked_observability["metrics"]
    for metric_name in metrics_module.__all__:
        if metric_name not in ("PROMETHEUS_AVAILABLE", "Summary"):
            assert getattr(metrics_module, metric_name) is not None
