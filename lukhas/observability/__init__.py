"""
LUKHAS Observability Module
Enterprise-grade monitoring, tracing, and metrics collection.
"""

from .opentelemetry_tracing import (
    LUKHASTracer,
    initialize_tracing,
    get_lukhas_tracer,
    shutdown_tracing,
    trace_function,
    trace_memory_recall,
    trace_matriz_execution,
    OTEL_AVAILABLE,
)

from .prometheus_metrics import (
    LUKHASMetrics,
    MetricsConfig,
    initialize_metrics,
    get_lukhas_metrics,
    shutdown_metrics,
    PROMETHEUS_AVAILABLE,
)

__all__ = [
    # OpenTelemetry tracing
    "LUKHASTracer",
    "initialize_tracing",
    "get_lukhas_tracer",
    "shutdown_tracing",
    "trace_function",
    "trace_memory_recall",
    "trace_matriz_execution",
    "OTEL_AVAILABLE",
    # Prometheus metrics
    "LUKHASMetrics",
    "MetricsConfig",
    "initialize_metrics",
    "get_lukhas_metrics",
    "shutdown_metrics",
    "PROMETHEUS_AVAILABLE",
]