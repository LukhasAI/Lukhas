"""
Unit tests for the centralized LUKHAS orchestration metrics module.
"""

import unittest
from unittest.mock import MagicMock, patch

# Mock the prometheus_client library before it's imported by the module under test.
# This is critical to prevent actual metric registration during tests.
mock_prometheus_client = MagicMock()
mock_prometheus_client.Histogram.return_value = MagicMock()
mock_prometheus_client.Counter.return_value = MagicMock()

# We need to patch 'prometheus_client' in sys.modules BEFORE importing stage_metrics
import sys

sys.modules['prometheus_client'] = mock_prometheus_client

from lukhas.orchestration import stage_metrics


class TestStageMetrics(unittest.TestCase):
    """Test suite for the orchestration stage_metrics module."""

    def setUp(self):
        """Reset mocks before each test."""
        # It's good practice to reset mocks to ensure test isolation.
        mock_prometheus_client.reset_mock()
        # Re-assign the mocked classes to the module's globals to be safe
        stage_metrics.Histogram = mock_prometheus_client.Histogram
        stage_metrics.Counter = mock_prometheus_client.Counter
        # Clear any memoized metric instances in the module
        stage_metrics.PIPELINE_DURATION = stage_metrics._register_metric(
            stage_metrics.Histogram, "lukhas_orchestration_pipeline_duration_seconds", "desc", []
        )
        stage_metrics.PIPELINE_TOTAL = stage_metrics._register_metric(
            stage_metrics.Counter, "lukhas_orchestration_pipeline_total", "desc", []
        )
        stage_metrics.STAGE_DURATION = stage_metrics._register_metric(
            stage_metrics.Histogram, "lukhas_orchestration_stage_duration_seconds", "desc", []
        )
        stage_metrics.STAGE_TOTAL = stage_metrics._register_metric(
            stage_metrics.Counter, "lukhas_orchestration_stage_total", "desc", []
        )


    @patch.dict('os.environ', {'LUKHAS_LANE': 'test-lane'})
    def test_record_stage_metrics_success(self):
        """Verify that stage metrics are recorded correctly for a success case."""
        mock_histogram_instance = MagicMock()
        mock_counter_instance = MagicMock()
        stage_metrics.STAGE_DURATION.labels.return_value = mock_histogram_instance
        stage_metrics.STAGE_TOTAL.labels.return_value = mock_counter_instance

        stage_metrics.record_stage_metrics(
            pipeline_name="test_pipeline",
            stage_name="test_stage",
            duration_sec=0.123,
            outcome="success",
        )

        # Verify that the correct labels were used
        stage_metrics.STAGE_DURATION.labels.assert_called_once_with(
            lane="test-lane",
            pipeline_name="test_pipeline",
            stage_name="test_stage",
            outcome="success",
        )
        stage_metrics.STAGE_TOTAL.labels.assert_called_once_with(
            lane="test-lane",
            pipeline_name="test_pipeline",
            stage_name="test_stage",
            outcome="success",
        )

        # Verify that the metrics were updated
        mock_histogram_instance.observe.assert_called_once_with(0.123)
        mock_counter_instance.inc.assert_called_once()


    @patch.dict('os.environ', {'LUKHAS_LANE': 'prod'})
    def test_record_pipeline_metrics_failure(self):
        """Verify that pipeline metrics are recorded correctly for a failure case."""
        mock_histogram_instance = MagicMock()
        mock_counter_instance = MagicMock()
        stage_metrics.PIPELINE_DURATION.labels.return_value = mock_histogram_instance
        stage_metrics.PIPELINE_TOTAL.labels.return_value = mock_counter_instance

        stage_metrics.record_pipeline_metrics(
            pipeline_name="main_processing",
            duration_sec=0.456,
            status="failure",
        )

        # Verify labels
        stage_metrics.PIPELINE_DURATION.labels.assert_called_once_with(
            lane="prod",
            pipeline_name="main_processing",
            status="failure",
        )
        stage_metrics.PIPELINE_TOTAL.labels.assert_called_once_with(
            lane="prod",
            pipeline_name="main_processing",
            status="failure",
        )

        # Verify metric updates
        mock_histogram_instance.observe.assert_called_once_with(0.456)
        mock_counter_instance.inc.assert_called_once()

    def test_unknown_outcome_is_normalized(self):
        """Ensure that an unrecognized outcome string is normalized to 'unknown'."""
        stage_metrics.STAGE_TOTAL.labels.reset_mock()
        stage_metrics.record_stage_metrics(
            pipeline_name="p", stage_name="s", duration_sec=0.1, outcome="weird_result"
        )
        stage_metrics.STAGE_TOTAL.labels.assert_called_once_with(
            lane=unittest.mock.ANY,
            pipeline_name=unittest.mock.ANY,
            stage_name=unittest.mock.ANY,
            outcome="unknown",
        )

    def test_negative_duration_is_clamped_to_zero(self):
        """Ensure that a negative duration is recorded as zero."""
        mock_histogram_instance = MagicMock()
        stage_metrics.STAGE_DURATION.labels.return_value = mock_histogram_instance

        stage_metrics.record_stage_metrics(
            pipeline_name="p", stage_name="s", duration_sec=-0.5, outcome="success"
        )
        mock_histogram_instance.observe.assert_called_once_with(0.0)

if __name__ == '__main__':
    unittest.main()
