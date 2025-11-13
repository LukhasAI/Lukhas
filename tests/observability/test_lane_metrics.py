import importlib
from unittest.mock import patch

# The lane_metrics module is imported here to be reloaded in the tests.
from lukhas.observability import lane_metrics


@patch('observability.prometheus_registry.counter')
def test_lane_operations_total_created(mock_counter):
    """Verify that the LANE_OPERATIONS_TOTAL counter is created correctly."""
    # The metric is created at module import time, so we need to reload it
    # to trigger the factory call with our mock.
    importlib.reload(lane_metrics)

    mock_counter.assert_called_once_with(
        "lane_operations_total",
        "Total number of operations executed in a specific lane.",
        ["lane", "operation"],
    )


@patch('observability.prometheus_registry.gauge')
def test_lane_active_requests_created(mock_gauge):
    """Verify that the LANE_ACTIVE_REQUESTS gauge is created correctly."""
    importlib.reload(lane_metrics)

    mock_gauge.assert_called_once_with(
        "lane_active_requests",
        "Number of active requests in a specific lane.",
        ["lane"],
    )
