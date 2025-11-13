"""Memory observability with OpenTelemetry and Prometheus."""

from __future__ import annotations

import time

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Histogram


class PrometheusMetrics:
    def __init__(self):
        self.latency_histogram = Histogram(
            'memory_query_duration_ms',
            'Memory query latency in milliseconds',
            ['operation']
        )
        self.op_counter = Counter(
            'memory_operations_total',
            'Total memory operations',
            ['operation', 'status']
        )

    def observe_latency(self, operation: str, duration_ms: float):
        """Record operation latency."""
        self.latency_histogram.labels(operation=operation).observe(duration_ms)

    def increment_counter(self, metric: str, labels: dict):
        """Increment operation counter."""
        # The metric name is passed from the caller, but we've hard-coded it for simplicity
        if metric == 'memory_operations_total':
            self.op_counter.labels(**labels).inc()


class MemoryTracer:
    """OpenTelemetry tracing for memory operations."""

    def __init__(self, service_name: str = "lukhas-memory"):
        self.tracer = trace.get_tracer(service_name)
        self.metrics = PrometheusMetrics()

    def trace_operation(self, operation: str, span_name: str | None = None):
        """Context manager for tracing memory operations."""
        return MemorySpan(
            self.tracer.start_span(span_name or f"memory.{operation}"),
            self.metrics,
            operation
        )

class MemorySpan:
    """Context manager for traced memory operations."""

    def __init__(self, span, metrics: PrometheusMetrics, operation: str):
        self.span = span
        self.metrics = metrics
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type is None:
            self.span.set_status(Status(StatusCode.OK))
            self.metrics.increment_counter("memory_operations_total", {"operation": self.operation, "status": "success"})
        else:
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
            self.metrics.increment_counter("memory_operations_total", {"operation": self.operation, "status": "error"})

        self.metrics.observe_latency(self.operation, duration_ms)
        self.span.set_attribute("operation.duration_ms", duration_ms)
        self.span.end()

    def add_attributes(self, **attrs):
        """Add attributes to the current span."""
        for key, value in attrs.items():
            self.span.set_attribute(key, value)
