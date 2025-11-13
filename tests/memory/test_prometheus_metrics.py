"""
Tests for LUKHAS Memory system Prometheus metrics.
"""

import unittest
from unittest.mock import MagicMock, patch

# Mock the prometheus_registry module before importing the metrics module.
# This is crucial to ensure that the metrics module uses our mock objects.
mock_registry = MagicMock()
mock_counter = MagicMock()
mock_gauge = MagicMock()
mock_histogram = MagicMock()

# Configure the mock functions to return another mock, simulating the chained calls.
mock_registry.counter.return_value = mock_counter
mock_registry.gauge.return_value = mock_gauge
mock_registry.histogram.return_value = mock_histogram

# We need to mock the labels call as well.
mock_counter.labels.return_value = MagicMock()
mock_gauge.labels.return_value = MagicMock()
mock_histogram.labels.return_value = MagicMock()


# Now, apply the patch to the sys.modules.
# This ensures that any import of 'lukhas.observability.prometheus_registry'
# will return our mock_registry.
with patch.dict('sys.modules', {'lukhas.observability.prometheus_registry': mock_registry}):
    from lukhas.memory import prometheus_metrics as memory_metrics

class TestMemoryPrometheusMetrics(unittest.TestCase):
    """Test suite for memory system Prometheus metrics."""

    def tearDown(self):
        """Reset mocks after each test."""
        mock_counter.labels.return_value.inc.reset_mock()
        mock_gauge.labels.return_value.set.reset_mock()
        mock_histogram.labels.return_value.observe.reset_mock()
        mock_counter.reset_mock()
        mock_gauge.reset_mock()
        mock_histogram.reset_mock()

    def test_record_fold_operation(self):
        """Test that fold operations are correctly recorded."""
        memory_metrics.record_fold_operation(tenant_id="tenant-1", operation_type="compact")
        memory_metrics.MEMORY_FOLD_OPERATIONS_TOTAL.labels.assert_called_with(
            tenant_id="tenant-1", operation_type="compact"
        )
        memory_metrics.MEMORY_FOLD_OPERATIONS_TOTAL.labels.return_value.inc.assert_called_once()

    def test_record_recall_latency(self):
        """Test that recall latency is correctly recorded."""
        memory_metrics.record_recall_latency(tenant_id="tenant-2", index_type="vector", duration_seconds=0.123)
        memory_metrics.MEMORY_RECALL_LATENCY_SECONDS.labels.assert_called_with(
            tenant_id="tenant-2", index_type="vector"
        )
        memory_metrics.MEMORY_RECALL_LATENCY_SECONDS.labels.return_value.observe.assert_called_with(0.123)

    def test_record_cache_hit(self):
        """Test that cache hits are correctly recorded."""
        memory_metrics.record_cache_hit(tenant_id="tenant-3", cache_type="embedding")
        memory_metrics.MEMORY_CACHE_HITS_TOTAL.labels.assert_called_with(
            tenant_id="tenant-3", cache_type="embedding"
        )
        memory_metrics.MEMORY_CACHE_HITS_TOTAL.labels.return_value.inc.assert_called_once()

    def test_record_cache_miss(self):
        """Test that cache misses are correctly recorded."""
        memory_metrics.record_cache_miss(tenant_id="tenant-4", cache_type="query")
        memory_metrics.MEMORY_CACHE_MISSES_TOTAL.labels.assert_called_with(
            tenant_id="tenant-4", cache_type="query"
        )
        memory_metrics.MEMORY_CACHE_MISSES_TOTAL.labels.return_value.inc.assert_called_once()

    def test_update_cache_hit_rate(self):
        """Test that the cache hit rate is correctly updated."""
        memory_metrics.update_cache_hit_rate(tenant_id="tenant-5", cache_type="embedding", hit_rate=0.95)
        memory_metrics.MEMORY_CACHE_HIT_RATE.labels.assert_called_with(
            tenant_id="tenant-5", cache_type="embedding"
        )
        memory_metrics.MEMORY_CACHE_HIT_RATE.labels.return_value.set.assert_called_with(0.95)

    def test_update_storage_size(self):
        """Test that the storage size is correctly updated."""
        memory_metrics.update_storage_size(tenant_id="tenant-6", storage_type="index", size_bytes=1024)
        memory_metrics.MEMORY_STORAGE_SIZE_BYTES.labels.assert_called_with(
            tenant_id="tenant-6", storage_type="index"
        )
        memory_metrics.MEMORY_STORAGE_SIZE_BYTES.labels.return_value.set.assert_called_with(1024)

if __name__ == '__main__':
    unittest.main()
