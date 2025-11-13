"""Unit tests for LUKHAS business metrics."""

import sys
import unittest
from importlib import reload
from unittest.mock import MagicMock, patch

# Mock the prometheus_client before it's imported by the registry.
# This is crucial to prevent actual metric registration during tests.
# The mock needs a `__name__` attribute to avoid an AttributeError during
# the prometheus_registry's initialization when it builds a cache key.
mock_prometheus_client = MagicMock()
mock_prometheus_client.Counter = MagicMock(spec=object)
mock_prometheus_client.Counter.__name__ = 'Counter'
mock_prometheus_client.Gauge = MagicMock(spec=object)
mock_prometheus_client.Gauge.__name__ = 'Gauge'

# We must patch `sys.modules` *before* the module under test is imported.
sys.modules['prometheus_client'] = mock_prometheus_client

# The module under test is imported once at collection time.
from lukhas.observability import custom_metrics


class TestCustomMetrics(unittest.TestCase):
    """Test cases for the custom business metrics."""

    # The metric objects in `custom_metrics` are created at module load time.
    # To test the parameters they were created with, we patch the factory
    # functions (`counter`, `gauge`) and then reload the `custom_metrics`
    # module. This re-triggers the metric creation, but this time using our mocks.
    # We use `assert_any_call` because reloading the module calls ALL metric
    # factories, so we just need to ensure our target factory was called at
    # some point with the correct arguments.
    @patch('observability.prometheus_registry.counter')
    def test_qrg_signatures_total(self, mock_counter):
        """Test the QRG_SIGNATURES_TOTAL counter."""
        reload(custom_metrics)
        mock_counter.assert_any_call(
            "qrg_signatures_total",
            "Total number of QRG signatures generated.",
            ["credential_id"],
        )

    @patch('observability.prometheus_registry.counter')
    def test_guardian_vetoes_total(self, mock_counter):
        """Test the GUARDIAN_VETOES_TOTAL counter."""
        reload(custom_metrics)
        mock_counter.assert_any_call(
            "guardian_vetoes_total",
            "Total number of Guardian vetoes.",
            ["policy_id", "decision"],
        )

    @patch('observability.prometheus_registry.gauge')
    def test_dream_drift(self, mock_gauge):
        """Test the DREAM_DRIFT gauge."""
        reload(custom_metrics)
        mock_gauge.assert_any_call(
            "dream_drift",
            "Current dream drift value.",
            ["dream_id"],
        )

    @patch('observability.prometheus_registry.gauge')
    def test_memory_fold_rate(self, mock_gauge):
        """Test the MEMORY_FOLD_RATE gauge."""
        reload(custom_metrics)
        mock_gauge.assert_any_call(
            "memory_fold_rate",
            "Current memory fold rate.",
            ["index_name"],
        )


if __name__ == '__main__':
    unittest.main()
