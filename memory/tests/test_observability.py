
import unittest
from unittest.mock import MagicMock, patch

from memory.observability import MemorySpan, MemoryTracer, PrometheusMetrics


class TestPrometheusMetrics(unittest.TestCase):

    @patch('memory.observability.Histogram')
    @patch('memory.observability.Counter')
    def test_initialization(self, MockCounter, MockHistogram):
        """Test that metrics are initialized correctly."""
        metrics = PrometheusMetrics()
        MockHistogram.assert_called_once_with(
            'memory_query_duration_ms',
            'Memory query latency in milliseconds',
            ['operation']
        )
        MockCounter.assert_called_once_with(
            'memory_operations_total',
            'Total memory operations',
            ['operation', 'status']
        )

    @patch('memory.observability.Histogram')
    @patch('memory.observability.Counter')
    def test_observe_latency(self, MockCounter, MockHistogram):
        """Test that observe_latency records the duration."""
        mock_histogram_instance = MockHistogram.return_value

        metrics = PrometheusMetrics()
        metrics.observe_latency("search", 123.4)

        mock_histogram_instance.labels.assert_called_once_with(operation="search")
        mock_histogram_instance.labels.return_value.observe.assert_called_once_with(123.4)

    @patch('memory.observability.Histogram')
    @patch('memory.observability.Counter')
    def test_increment_counter(self, MockCounter, MockHistogram):
        """Test that increment_counter increments the correct counter."""
        mock_counter_instance = MockCounter.return_value

        metrics = PrometheusMetrics()
        labels = {"operation": "add", "status": "success"}
        metrics.increment_counter("memory_operations_total", labels)

        mock_counter_instance.labels.assert_called_once_with(**labels)
        mock_counter_instance.labels.return_value.inc.assert_called_once()


class TestMemoryTracer(unittest.TestCase):

    @patch('memory.observability.PrometheusMetrics')
    @patch('memory.observability.trace.get_tracer')
    def test_tracer_initialization(self, mock_get_tracer, mock_prometheus_metrics):
        """Test that the tracer is initialized correctly."""
        tracer = MemoryTracer(service_name="test-service")
        mock_get_tracer.assert_called_once_with("test-service")
        # Verify that a PrometheusMetrics object is instantiated
        mock_prometheus_metrics.assert_called_once()

    @patch('memory.observability.PrometheusMetrics')
    @patch('memory.observability.trace.get_tracer')
    def test_trace_operation_starts_span(self, mock_get_tracer, mock_prometheus_metrics):
        """Test that trace_operation starts a new span."""
        mock_tracer = mock_get_tracer.return_value

        tracer = MemoryTracer()
        with tracer.trace_operation("test_op"):
            pass

        mock_tracer.start_span.assert_called_once_with("memory.test_op")

class TestMemorySpan(unittest.TestCase):

    def setUp(self):
        self.mock_span = MagicMock()
        self.mock_metrics = MagicMock()

    def test_span_success_exit(self):
        """Test the context manager exit on a successful operation."""
        with MemorySpan(self.mock_span, self.mock_metrics, "test_op"):
            pass

        self.mock_span.set_status.assert_called_once()
        status_arg = self.mock_span.set_status.call_args[0][0]
        # Can't directly compare Status objects, so check the code
        from opentelemetry.trace import StatusCode
        self.assertEqual(status_arg.status_code, StatusCode.OK)

        self.mock_metrics.increment_counter.assert_called_once_with(
            "memory_operations_total", {"operation": "test_op", "status": "success"}
        )
        self.mock_metrics.observe_latency.assert_called_once()
        self.mock_span.end.assert_called_once()

    def test_span_error_exit(self):
        """Test the context manager exit on an exception."""
        with self.assertRaises(ValueError):
            with MemorySpan(self.mock_span, self.mock_metrics, "test_op"):
                raise ValueError("test error")

        self.mock_span.set_status.assert_called_once()
        status_arg = self.mock_span.set_status.call_args[0][0]
        from opentelemetry.trace import StatusCode
        self.assertEqual(status_arg.status_code, StatusCode.ERROR)

        self.mock_metrics.increment_counter.assert_called_once_with(
            "memory_operations_total", {"operation": "test_op", "status": "error"}
        )
        self.mock_metrics.observe_latency.assert_called_once()
        self.mock_span.end.assert_called_once()

if __name__ == '__main__':
    unittest.main()
