#!/usr/bin/env python3

"""
LUKHAS Guardian Serializers Observability Integration
====================================================

Comprehensive observability integration for Guardian schema serialization system.
Provides metrics collection, performance monitoring, and CI validation.

Features:
- Prometheus metrics collection
- OpenTelemetry tracing integration
- Performance monitoring dashboards
- SLA validation and alerting
- Custom metrics for Guardian operations
- Health check endpoints
- Circuit breaker monitoring

Metrics Categories:
- Performance: Latency, throughput, error rates
- Business: Decision types, policy usage, compliance scores
- System: Memory usage, cache performance, circuit breaker states
- Security: Authentication failures, unauthorized access attempts

Author: LUKHAS AI System
Version: 1.0.0
Phase: 7 - Guardian Schema Serializers
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

# Try to import observability dependencies with graceful degradation
try:
    import prometheus_client
    from prometheus_client import Counter, Enum as PrometheusEnum, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

from .guardian_serializers import GuardianOperation, GuardianResult

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to collect"""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    ENUM = "enum"


@dataclass
class MetricDefinition:
    """Definition of a metric to collect"""
    name: str
    type: MetricType
    description: str
    labels: list[str]
    buckets: Optional[list[float]] = None


class GuardianMetricsCollector:
    """Metrics collector for Guardian serialization operations"""

    def __init__(self):
        self.metrics: dict[str, Any] = {}
        self._initialize_metrics()

    def record_operation(self, result: GuardianResult) -> None:
        """Record metrics for Guardian operation"""
        if not PROMETHEUS_AVAILABLE:
            return

        operation_type = result.operation.operation_type.value
        success_status = "success" if result.success else "failure"

        # Record operation counter
        self.metrics["guardian_operations_total"].labels(
            operation=operation_type,
            status=success_status,
            format=result.operation.format.value if hasattr(result.operation, 'format') else "unknown"
        ).inc()

        # Record operation latency
        self.metrics["guardian_operation_duration_seconds"].labels(
            operation=operation_type
        ).observe(result.execution_time_ms / 1000.0)

        # Record validation metrics if available
        if result.validation_result:
            self._record_validation_metrics(result.validation_result)

        # Record migration metrics if available
        if result.migration_result:
            self._record_migration_metrics(result.migration_result)

        # Record serialization metrics if available
        if hasattr(result, 'metrics') and result.metrics:
            self._record_serialization_metrics(result.metrics)

    def record_validation_metrics(self, validation_result: Any) -> None:
        """Record validation-specific metrics"""
        if not PROMETHEUS_AVAILABLE or not validation_result:
            return

        # Record validation result
        status = "success" if validation_result.is_valid else "failure"
        self.metrics["guardian_validations_total"].labels(status=status).inc()

        # Record validation latency
        self.metrics["guardian_validation_duration_seconds"].observe(
            validation_result.validation_time_ms / 1000.0
        )

        # Record compliance score
        if hasattr(validation_result, 'compliance_score'):
            self.metrics["guardian_compliance_score"].set(validation_result.compliance_score)

        # Record issue counts
        if hasattr(validation_result, 'issues'):
            for issue in validation_result.issues:
                self.metrics["guardian_validation_issues_total"].labels(
                    severity=issue.severity.value,
                    tier=issue.tier.name
                ).inc()

    def record_serialization_metrics(self, serialization_metrics: dict[str, Any]) -> None:
        """Record serialization-specific metrics"""
        if not PROMETHEUS_AVAILABLE:
            return

        # Record serialization size metrics
        if "compressed_size" in serialization_metrics:
            self.metrics["guardian_serialization_bytes"].observe(
                serialization_metrics["compressed_size"]
            )

        # Record compression ratio
        if "compression_ratio" in serialization_metrics:
            self.metrics["guardian_compression_ratio"].observe(
                serialization_metrics["compression_ratio"]
            )

        # Record serialization time
        if "serialization_time_ms" in serialization_metrics:
            self.metrics["guardian_serialization_duration_seconds"].observe(
                serialization_metrics["serialization_time_ms"] / 1000.0
            )

    def record_cache_metrics(self, cache_metrics: dict[str, Any]) -> None:
        """Record cache performance metrics"""
        if not PROMETHEUS_AVAILABLE:
            return

        # Cache hit rate
        if "cache_hit_rate" in cache_metrics:
            self.metrics["guardian_cache_hit_rate"].set(cache_metrics["cache_hit_rate"])

        # Cache size
        if "cache_size" in cache_metrics:
            self.metrics["guardian_cache_size"].set(cache_metrics["cache_size"])

        # Memory usage
        if "memory_usage_mb" in cache_metrics:
            self.metrics["guardian_memory_usage_mb"].set(cache_metrics["memory_usage_mb"])

    def record_circuit_breaker_metrics(self, integration_health: dict[str, Any]) -> None:
        """Record circuit breaker metrics"""
        if not PROMETHEUS_AVAILABLE:
            return

        for integration, health_info in integration_health.items():
            if isinstance(health_info, dict):
                # Circuit breaker state
                if "circuit_state" in health_info:
                    self.metrics["guardian_circuit_breaker_state"].labels(
                        integration=integration
                    ).state(health_info["circuit_state"])

                # Failure count
                if "failure_count" in health_info:
                    self.metrics["guardian_circuit_breaker_failures_total"].labels(
                        integration=integration
                    ).set(health_info["failure_count"])

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics"""
        if not PROMETHEUS_AVAILABLE:
            return {"status": "prometheus_not_available"}

        try:
            # Collect current metric values
            registry = prometheus_client.REGISTRY
            families = list(registry.collect())

            summary = {
                "total_metrics": len(families),
                "guardian_specific_metrics": len([f for f in families if f.name.startswith("guardian_")]),
                "collection_timestamp": time.time()
            }

            return summary

        except Exception as e:
            logger.error(f"Error collecting metrics summary: {e}")
            return {"status": "error", "error": str(e)}

    def _initialize_metrics(self) -> None:
        """Initialize Prometheus metrics"""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus not available - metrics collection disabled")
            return

        # Define metric definitions
        metric_definitions = [
            MetricDefinition(
                "guardian_operations_total",
                MetricType.COUNTER,
                "Total Guardian operations",
                ["operation", "status", "format"]
            ),
            MetricDefinition(
                "guardian_operation_duration_seconds",
                MetricType.HISTOGRAM,
                "Guardian operation duration",
                ["operation"],
                [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
            ),
            MetricDefinition(
                "guardian_validations_total",
                MetricType.COUNTER,
                "Total Guardian validations",
                ["status"]
            ),
            MetricDefinition(
                "guardian_validation_duration_seconds",
                MetricType.HISTOGRAM,
                "Guardian validation duration",
                [],
                [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
            ),
            MetricDefinition(
                "guardian_compliance_score",
                MetricType.GAUGE,
                "Guardian compliance score",
                []
            ),
            MetricDefinition(
                "guardian_validation_issues_total",
                MetricType.COUNTER,
                "Total validation issues",
                ["severity", "tier"]
            ),
            MetricDefinition(
                "guardian_serialization_bytes",
                MetricType.HISTOGRAM,
                "Guardian serialization size in bytes",
                [],
                [100, 500, 1000, 5000, 10000, 50000, 100000]
            ),
            MetricDefinition(
                "guardian_compression_ratio",
                MetricType.HISTOGRAM,
                "Guardian compression ratio",
                [],
                [1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
            ),
            MetricDefinition(
                "guardian_serialization_duration_seconds",
                MetricType.HISTOGRAM,
                "Guardian serialization duration",
                [],
                [0.001, 0.005, 0.01, 0.05, 0.1]
            ),
            MetricDefinition(
                "guardian_cache_hit_rate",
                MetricType.GAUGE,
                "Guardian cache hit rate",
                []
            ),
            MetricDefinition(
                "guardian_cache_size",
                MetricType.GAUGE,
                "Guardian cache size",
                []
            ),
            MetricDefinition(
                "guardian_memory_usage_mb",
                MetricType.GAUGE,
                "Guardian memory usage in MB",
                []
            ),
            MetricDefinition(
                "guardian_circuit_breaker_state",
                MetricType.ENUM,
                "Circuit breaker state",
                ["integration"]
            ),
            MetricDefinition(
                "guardian_circuit_breaker_failures_total",
                MetricType.GAUGE,
                "Circuit breaker failure count",
                ["integration"]
            )
        ]

        # Create Prometheus metrics
        for metric_def in metric_definitions:
            if metric_def.type == MetricType.COUNTER:
                self.metrics[metric_def.name] = Counter(
                    metric_def.name, metric_def.description, metric_def.labels
                )
            elif metric_def.type == MetricType.HISTOGRAM:
                self.metrics[metric_def.name] = Histogram(
                    metric_def.name, metric_def.description, metric_def.labels,
                    buckets=metric_def.buckets
                )
            elif metric_def.type == MetricType.GAUGE:
                self.metrics[metric_def.name] = Gauge(
                    metric_def.name, metric_def.description, metric_def.labels
                )
            elif metric_def.type == MetricType.ENUM:
                self.metrics[metric_def.name] = PrometheusEnum(
                    metric_def.name, metric_def.description,
                    states=["closed", "open", "half_open"],
                    labelnames=metric_def.labels
                )

        logger.info("Guardian metrics collector initialized")

    def _record_validation_metrics(self, validation_result: Any) -> None:
        """Internal method to record validation metrics"""
        self.record_validation_metrics(validation_result)

    def _record_migration_metrics(self, migration_result: Any) -> None:
        """Record migration-specific metrics"""
        if not PROMETHEUS_AVAILABLE or not migration_result:
            return

        # Record migration result
        status = "success" if migration_result.success else "failure"
        self.metrics["guardian_migrations_total"] = self.metrics.get(
            "guardian_migrations_total",
            Counter("guardian_migrations_total", "Total Guardian migrations", ["status"])
        )
        self.metrics["guardian_migrations_total"].labels(status=status).inc()

    def _record_serialization_metrics(self, serialization_metrics: dict[str, Any]) -> None:
        """Internal method to record serialization metrics"""
        self.record_serialization_metrics(serialization_metrics)


class GuardianTracing:
    """OpenTelemetry tracing integration for Guardian operations"""

    def __init__(self):
        self.tracer = None
        self._initialize_tracing()

    def trace_operation(self, operation_name: str, operation: GuardianOperation):
        """Create trace span for Guardian operation"""
        if not self.tracer:
            return self._noop_context_manager()

        return self.tracer.start_as_current_span(
            operation_name,
            attributes={
                "guardian.operation_id": operation.operation_id,
                "guardian.operation_type": operation.operation_type.value,
                "guardian.schema_version": operation.schema_version,
                "guardian.format": operation.format.value if hasattr(operation, 'format') else "unknown",
                "guardian.compression": operation.compression.value if hasattr(operation, 'compression') else "none",
                "guardian.validation_enabled": operation.validation_enabled,
                "guardian.migration_enabled": operation.migration_enabled
            }
        )

    def add_span_event(self, event_name: str, attributes: Optional[dict[str, Any]] = None):
        """Add event to current span"""
        if not self.tracer:
            return

        try:
            span = trace.get_current_span()
            if span:
                span.add_event(event_name, attributes or {})
        except Exception as e:
            logger.debug(f"Failed to add span event: {e}")

    def set_span_status(self, success: bool, error_message: Optional[str] = None):
        """Set span status based on operation result"""
        if not self.tracer:
            return

        try:
            span = trace.get_current_span()
            if span:
                if success:
                    span.set_status(trace.Status(trace.StatusCode.OK))
                else:
                    span.set_status(trace.Status(
                        trace.StatusCode.ERROR,
                        error_message or "Operation failed"
                    ))
        except Exception as e:
            logger.debug(f"Failed to set span status: {e}")

    def _initialize_tracing(self) -> None:
        """Initialize OpenTelemetry tracing"""
        if not OPENTELEMETRY_AVAILABLE:
            logger.warning("OpenTelemetry not available - tracing disabled")
            return

        try:
            # Set up tracer provider
            trace.set_tracer_provider(TracerProvider())

            # Configure Jaeger exporter (if available)
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=14268,
            )

            # Add span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)

            # Create tracer
            self.tracer = trace.get_tracer(__name__)

            logger.info("Guardian tracing initialized with Jaeger exporter")

        except Exception as e:
            logger.warning(f"Failed to initialize tracing: {e}")

    def _noop_context_manager(self):
        """No-op context manager when tracing is not available"""
        class NoopContext:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass

        return NoopContext()


class GuardianHealthCheck:
    """Health check endpoint for Guardian serialization system"""

    def __init__(self):
        self.metrics_collector = GuardianMetricsCollector()
        self.start_time = time.time()

    def get_health_status(self) -> dict[str, Any]:
        """Get comprehensive health status"""
        from .guardian_serializers import get_system_health

        # Get system health
        system_health = get_system_health()

        # Add observability-specific health
        observability_health = {
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "opentelemetry_available": OPENTELEMETRY_AVAILABLE,
            "metrics_collector_healthy": True,
            "uptime_seconds": time.time() - self.start_time
        }

        # Combine health status
        health_status = {
            **system_health,
            "observability": observability_health,
            "timestamp": time.time(),
            "overall_status": self._determine_overall_status(system_health, observability_health)
        }

        return health_status

    def get_readiness_status(self) -> dict[str, Any]:
        """Get readiness status for Kubernetes/container orchestration"""
        health = self.get_health_status()
        integration_health = health.get("integration_health", {})

        # System is ready if core components are healthy
        ready = (
            integration_health.get("schema_registry_healthy", False) and
            integration_health.get("serialization_healthy", False) and
            integration_health.get("validation_healthy", False)
        )

        return {
            "ready": ready,
            "timestamp": time.time(),
            "components": integration_health
        }

    def get_liveness_status(self) -> dict[str, Any]:
        """Get liveness status for Kubernetes/container orchestration"""
        # Basic liveness check - system is alive if it can respond
        return {
            "alive": True,
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.start_time
        }

    def _determine_overall_status(
        self,
        system_health: dict[str, Any],
        observability_health: dict[str, Any]
    ) -> str:
        """Determine overall system status"""
        integration_health = system_health.get("integration_health", {})

        # Critical components must be healthy
        critical_healthy = (
            integration_health.get("schema_registry_healthy", False) and
            integration_health.get("serialization_healthy", False)
        )

        if not critical_healthy:
            return "unhealthy"

        # Performance should be acceptable
        performance_ok = integration_health.get("performance_optimal", True)
        validation_ok = integration_health.get("validation_healthy", True)

        if not (performance_ok and validation_ok):
            return "degraded"

        return "healthy"


# Global observability instances
_metrics_collector: Optional[GuardianMetricsCollector] = None
_tracer: Optional[GuardianTracing] = None
_health_check: Optional[GuardianHealthCheck] = None


def get_metrics_collector() -> GuardianMetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = GuardianMetricsCollector()
    return _metrics_collector


def get_tracer() -> GuardianTracing:
    """Get global tracer instance"""
    global _tracer
    if _tracer is None:
        _tracer = GuardianTracing()
    return _tracer


def get_health_check() -> GuardianHealthCheck:
    """Get global health check instance"""
    global _health_check
    if _health_check is None:
        _health_check = GuardianHealthCheck()
    return _health_check


# Decorator for automatic tracing
def trace_guardian_operation(operation_name: str):
    """Decorator to automatically trace Guardian operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            operation = kwargs.get('operation') or (args[1] if len(args) > 1 else None)

            if not operation or not hasattr(operation, 'operation_id'):
                # Create dummy operation for tracing
                from .guardian_serializers import GuardianOperation
                operation = GuardianOperation()

            with tracer.trace_operation(operation_name, operation):
                try:
                    result = func(*args, **kwargs)

                    # Record success
                    tracer.set_span_status(True)
                    tracer.add_span_event("operation_completed", {
                        "success": getattr(result, 'success', True)
                    })

                    # Record metrics
                    if hasattr(result, 'success') and hasattr(result, 'operation'):
                        metrics_collector = get_metrics_collector()
                        metrics_collector.record_operation(result)

                    return result

                except Exception as e:
                    # Record failure
                    tracer.set_span_status(False, str(e))
                    tracer.add_span_event("operation_failed", {
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
                    raise

        return wrapper
    return decorator


# Utility functions for metric collection
def record_guardian_operation(result: GuardianResult) -> None:
    """Record metrics for Guardian operation"""
    metrics_collector = get_metrics_collector()
    metrics_collector.record_operation(result)


def record_system_metrics(system_status: dict[str, Any]) -> None:
    """Record system-level metrics"""
    metrics_collector = get_metrics_collector()

    # Record cache metrics
    if "performance_optimizer" in system_status:
        cache_metrics = system_status["performance_optimizer"]
        metrics_collector.record_cache_metrics(cache_metrics)

    # Record circuit breaker metrics
    if "integration_health" in system_status:
        integration_health = system_status["integration_health"]
        metrics_collector.record_circuit_breaker_metrics(integration_health)


# Health check endpoints (for web framework integration)
def health_endpoint() -> dict[str, Any]:
    """Health check endpoint"""
    health_check = get_health_check()
    return health_check.get_health_status()


def ready_endpoint() -> dict[str, Any]:
    """Readiness check endpoint"""
    health_check = get_health_check()
    return health_check.get_readiness_status()


def live_endpoint() -> dict[str, Any]:
    """Liveness check endpoint"""
    health_check = get_health_check()
    return health_check.get_liveness_status()


def metrics_endpoint() -> str:
    """Prometheus metrics endpoint"""
    if not PROMETHEUS_AVAILABLE:
        return "# Prometheus not available\n"

    try:
        return prometheus_client.generate_latest().decode('utf-8')
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return f"# Error generating metrics: {e!s}\n"
