"""Unit tests for memory observability."""

from unittest.mock import Mock, patch

from memory.observability import MemorySpan, MemoryTracer, PrometheusMetrics


def test_prometheus_metrics_initialization():
    metrics = PrometheusMetrics()
    # Just ensure it initializes without error
    assert metrics is not None

def test_prometheus_metrics_methods():
    metrics = PrometheusMetrics()

    # These should not raise errors (placeholders)
    metrics.observe_latency("test_op", 10.5)
    metrics.increment_counter("test_metric", {"label": "value"})

def test_memory_tracer_initialization():
    tracer = MemoryTracer("test-service")
    assert tracer.metrics is not None

def test_memory_tracer_trace_operation():
    tracer = MemoryTracer()

    with patch('memory.observability.trace.get_tracer') as mock_get_tracer:
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value = mock_span
        mock_get_tracer.return_value = mock_tracer

        tracer = MemoryTracer()
        span_context = tracer.trace_operation("test_op")

        assert isinstance(span_context, MemorySpan)
        mock_tracer.start_span.assert_called_with("memory.test_op")

def test_memory_span_context_manager():
    mock_span = Mock()
    mock_metrics = Mock()

    span_context = MemorySpan(mock_span, mock_metrics, "test_op")

    # Test successful execution
    with span_context as span:
        span.add_attributes(test_attr="value")
        mock_span.set_attribute.assert_called_with("test_attr", "value")

    # Verify span was completed successfully
    mock_span.set_status.assert_called()
    mock_span.end.assert_called()
    mock_metrics.increment_counter.assert_called()
    mock_metrics.observe_latency.assert_called()

def test_memory_span_with_exception():
    mock_span = Mock()
    mock_metrics = Mock()

    span_context = MemorySpan(mock_span, mock_metrics, "test_op")

    # Test exception handling
    try:
        with span_context:
            raise ValueError("Test error")
    except ValueError:
        pass

    # Verify error was recorded
    mock_span.set_status.assert_called()
    mock_span.end.assert_called()
    mock_metrics.increment_counter.assert_called()

    # Check that error status was set
    status_calls = mock_span.set_status.call_args_list
    assert len(status_calls) > 0
