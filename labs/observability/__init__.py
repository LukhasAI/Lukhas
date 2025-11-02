"""
Observability package - canonical namespace for metrics/tracing/logging.

Production-safe façade for observability primitives.
Incremental implementation - start minimal, flesh out as needed.
"""

from __future__ import annotations

__all__ = [
    "Tracer",
    "Metrics",
    "Counter",
    "Histogram",
    "observe_latency",
    "log_event",
    "get_tracer",
    "get_metrics",
]


class Counter:
    """Prometheus-style counter metric."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def inc(self, n: int = 1) -> None:
        """Increment counter by n."""
        pass  # Implementation placeholder


class Histogram:
    """Prometheus-style histogram metric."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def observe(self, value: float) -> None:
        """Observe a value in the histogram."""
        pass  # Implementation placeholder


class Metrics:
    """Metrics registry and factory."""

    def counter(self, name: str, description: str = "") -> Counter:
        """Create or retrieve a counter metric."""
        return Counter(name, description)

    def histogram(self, name: str, description: str = "") -> Histogram:
        """Create or retrieve a histogram metric."""
        return Histogram(name, description)


class Tracer:
    """Distributed tracing interface."""

    def start_span(self, name: str):
        """Start a new trace span."""

        class _Span:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        return _Span()


# Singleton instances
_METRICS = Metrics()
_TRACER = Tracer()


def get_metrics() -> Metrics:
    """Get the global metrics instance."""
    return _METRICS


def get_tracer() -> Tracer:
    """Get the global tracer instance."""
    return _TRACER


def observe_latency(name: str, value_ms: float) -> None:
    """Convenience function to observe latency."""
    _METRICS.histogram(name).observe(value_ms)


def log_event(name: str, **kwargs) -> None:
    """Breadcrumb event logging (no-op placeholder)."""
    _ = (name, kwargs)
