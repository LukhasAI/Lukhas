#!/usr/bin/env python3
"""
LUKHAS OpenTelemetry Tracing Integration
Enterprise-grade distributed tracing with performance monitoring.

Features:
- Automatic span creation for MATRIZ operations
- Memory system tracing with fold and recall metrics
- Plugin discovery and registry operation tracing
- Custom metrics and attributes for LUKHAS-specific operations
- Jaeger and OTLP export support
"""

import functools
import os
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional

try:
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import (
        SQLAlchemyInstrumentor,  # noqa: F401  # TODO: opentelemetry.instrumentation....
    )
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.semconv.trace import (
        SpanAttributes,  # noqa: F401  # TODO: opentelemetry.semconv.trace.Sp...
    )
    from opentelemetry.trace.status import Status, StatusCode

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Mock classes for when OpenTelemetry is not available
    class MockStatus:
        def __init__(self, status_code, description=""):
            self.status_code = status_code
            self.description = description

    class MockStatusCode:
        OK = "OK"
        ERROR = "ERROR"

    Status = MockStatus
    StatusCode = MockStatusCode

    class MockSpan:
        def set_attribute(self, key: str, value: Any) -> None:
            pass
        def set_status(self, status: Any) -> None:
            pass
        def record_exception(self, exception: Exception) -> None:
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    class MockTracer:
        def start_as_current_span(self, name: str, **kwargs):
            return MockSpan()


class LUKHASTracer:
    """
    LUKHAS-specific tracer with enterprise observability patterns.
    Provides comprehensive tracing for all system components.
    """

    def __init__(
        self,
        service_name: str = "lukhas-ai",
        service_version: str = "1.0.0",
        jaeger_endpoint: Optional[str] = None,
        otlp_endpoint: Optional[str] = None,
        enable_auto_instrumentation: bool = True,
    ):
        """
        Initialize LUKHAS tracer with OpenTelemetry.

        Args:
            service_name: Name of the LUKHAS service
            service_version: Version identifier
            jaeger_endpoint: Jaeger collector endpoint (optional)
            otlp_endpoint: OTLP endpoint for trace export (optional)
            enable_auto_instrumentation: Enable automatic library instrumentation
        """
        self.service_name = service_name
        self.service_version = service_version
        self.enabled = OTEL_AVAILABLE

        if not OTEL_AVAILABLE:
            print("Warning: OpenTelemetry not available. Tracing disabled.")
            self._tracer = MockTracer()
            self._meter = None
            return

        # Configure trace provider
        self._setup_tracing(jaeger_endpoint, otlp_endpoint)

        # Configure metrics
        self._setup_metrics(otlp_endpoint)

        # Get tracer
        self._tracer = trace.get_tracer(
            __name__,
            version=service_version,
        )

        # Setup custom metrics
        self._setup_custom_metrics()

        # Auto-instrumentation
        if enable_auto_instrumentation:
            self._setup_auto_instrumentation()

    def _setup_tracing(self, jaeger_endpoint: Optional[str], otlp_endpoint: Optional[str]):
        """Setup OpenTelemetry tracing with exporters"""
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

        # Setup exporters
        exporters = []

        # Jaeger exporter
        if jaeger_endpoint:
            jaeger_exporter = JaegerExporter(
                agent_host_name=jaeger_endpoint.split(':')[0],
                agent_port=int(jaeger_endpoint.split(':')[1]) if ':' in jaeger_endpoint else 14268,
            )
            exporters.append(jaeger_exporter)

        # OTLP exporter
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            exporters.append(otlp_exporter)

        # Default console exporter for development
        if not exporters:
            from opentelemetry.exporter.console import ConsoleSpanExporter
            exporters.append(ConsoleSpanExporter())

        # Add span processors
        for exporter in exporters:
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)

    def _setup_metrics(self, otlp_endpoint: Optional[str]):
        """Setup OpenTelemetry metrics"""
        if otlp_endpoint:
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=otlp_endpoint),
                export_interval_millis=30000,  # 30 seconds
            )
        else:
            # Console exporter for development
            from opentelemetry.exporter.console import ConsoleMetricExporter
            metric_reader = PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=60000,  # 1 minute
            )

        provider = MeterProvider(metric_readers=[metric_reader])
        metrics.set_meter_provider(provider)

        self._meter = metrics.get_meter(
            __name__,
            version=self.service_version,
        )

    def _setup_custom_metrics(self):
        """Setup LUKHAS-specific metrics"""
        if not self._meter:
            return

        # Memory system metrics
        self.memory_operations_counter = self._meter.create_counter(
            name="lukhas_memory_operations_total",
            description="Total number of memory operations",
        )

        self.memory_recall_latency = self._meter.create_histogram(
            name="lukhas_memory_recall_latency_ms",
            description="Memory recall latency in milliseconds",
        )

        self.fold_operations_counter = self._meter.create_counter(
            name="lukhas_fold_operations_total",
            description="Total number of fold operations",
        )

        # MATRIZ orchestration metrics
        self.matriz_stage_duration = self._meter.create_histogram(
            name="lukhas_matriz_stage_duration_ms",
            description="MATRIZ stage execution duration in milliseconds",
        )

        self.matriz_pipeline_duration = self._meter.create_histogram(
            name="lukhas_matriz_pipeline_duration_ms",
            description="Complete MATRIZ pipeline duration in milliseconds",
        )

        # Plugin system metrics
        self.plugin_discovery_counter = self._meter.create_counter(
            name="lukhas_plugin_discovery_total",
            description="Total number of plugin discovery operations",
        )

        self.plugin_instantiation_counter = self._meter.create_counter(
            name="lukhas_plugin_instantiation_total",
            description="Total number of plugin instantiation operations",
        )

    def _setup_auto_instrumentation(self):
        """Setup automatic instrumentation for common libraries"""
        try:
            RequestsInstrumentor().instrument()
            # SQLAlchemyInstrumentor().instrument()  # Enable if using SQLAlchemy
        except Exception as e:
            print(f"Warning: Auto-instrumentation setup failed: {e}")

    @contextmanager
    def trace_operation(
        self,
        operation_name: str,
        attributes: Optional[Dict[str, Any]] = None,
        record_exception: bool = True,
    ):
        """
        Context manager for tracing operations.

        Args:
            operation_name: Name of the operation being traced
            attributes: Additional span attributes
            record_exception: Whether to record exceptions automatically

        Yields:
            OpenTelemetry span object
        """
        with self._tracer.start_as_current_span(operation_name) as span:
            # Set service attributes
            span.set_attribute("service.name", self.service_name)
            span.set_attribute("service.version", self.service_version)
            span.set_attribute("operation", operation_name)

            # Set custom attributes
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)

            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                if record_exception:
                    span.record_exception(e)
                raise

    def trace_memory_operation(
        self,
        operation_type: str,
        item_count: Optional[int] = None,
        latency_ms: Optional[float] = None,
        success: bool = True,
    ):
        """
        Trace memory system operations.

        Args:
            operation_type: Type of memory operation (store, recall, fold, etc.)
            item_count: Number of items involved
            latency_ms: Operation latency in milliseconds
            success: Whether operation succeeded
        """
        attributes = {
            "memory.operation": operation_type,
            "memory.success": success,
        }

        if item_count is not None:
            attributes["memory.item_count"] = item_count

        with self.trace_operation(f"memory_{operation_type}", attributes):
            # Record metrics
            if self._meter:
                self.memory_operations_counter.add(
                    1,
                    {"operation": operation_type, "success": str(success)}
                )

                if latency_ms is not None and operation_type == "recall":
                    self.memory_recall_latency.record(
                        latency_ms,
                        {"success": str(success)}
                    )

    def trace_matriz_stage(
        self,
        stage_name: str,
        duration_ms: float,
        success: bool = True,
        timeout: bool = False,
        error: Optional[str] = None,
    ):
        """
        Trace MATRIZ orchestration stage.

        Args:
            stage_name: Name of the MATRIZ stage
            duration_ms: Stage execution duration
            success: Whether stage succeeded
            timeout: Whether stage timed out
            error: Error message if failed
        """
        attributes = {
            "matriz.stage": stage_name,
            "matriz.success": success,
            "matriz.timeout": timeout,
            "matriz.duration_ms": duration_ms,
        }

        if error:
            attributes["matriz.error"] = error

        with self.trace_operation(f"matriz_stage_{stage_name}", attributes):
            # Record metrics
            if self._meter:
                self.matriz_stage_duration.record(
                    duration_ms,
                    {
                        "stage": stage_name,
                        "success": str(success),
                        "timeout": str(timeout),
                    }
                )

    def trace_matriz_pipeline(
        self,
        total_duration_ms: float,
        stages_completed: int,
        stages_failed: int,
        within_budget: bool,
        user_query: Optional[str] = None,
    ):
        """
        Trace complete MATRIZ pipeline execution.

        Args:
            total_duration_ms: Total pipeline duration
            stages_completed: Number of successful stages
            stages_failed: Number of failed stages
            within_budget: Whether execution was within time budget
            user_query: User's query (optional, for correlation)
        """
        attributes = {
            "matriz.pipeline.duration_ms": total_duration_ms,
            "matriz.pipeline.stages_completed": stages_completed,
            "matriz.pipeline.stages_failed": stages_failed,
            "matriz.pipeline.within_budget": within_budget,
        }

        if user_query:
            # Hash or truncate for privacy
            attributes["matriz.query_hash"] = str(hash(user_query))

        with self.trace_operation("matriz_pipeline", attributes):
            # Record metrics
            if self._meter:
                self.matriz_pipeline_duration.record(
                    total_duration_ms,
                    {
                        "within_budget": str(within_budget),
                        "stages_completed": str(stages_completed),
                    }
                )

    def trace_plugin_operation(
        self,
        operation_type: str,
        plugin_name: Optional[str] = None,
        plugin_count: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """
        Trace plugin system operations.

        Args:
            operation_type: Type of plugin operation (discovery, instantiation, etc.)
            plugin_name: Name of specific plugin
            plugin_count: Number of plugins involved
            success: Whether operation succeeded
            error: Error message if failed
        """
        attributes = {
            "plugin.operation": operation_type,
            "plugin.success": success,
        }

        if plugin_name:
            attributes["plugin.name"] = plugin_name

        if plugin_count is not None:
            attributes["plugin.count"] = plugin_count

        if error:
            attributes["plugin.error"] = error

        with self.trace_operation(f"plugin_{operation_type}", attributes):
            # Record metrics
            if self._meter:
                if operation_type == "discovery":
                    self.plugin_discovery_counter.add(
                        1,
                        {"success": str(success)}
                    )
                elif operation_type == "instantiation":
                    self.plugin_instantiation_counter.add(
                        1,
                        {"success": str(success), "plugin": plugin_name or "unknown"}
                    )

    def trace_fold_operation(
        self,
        operation_type: str,
        fold_count: Optional[int] = None,
        compression_ratio: Optional[float] = None,
        success: bool = True,
    ):
        """
        Trace memory fold operations.

        Args:
            operation_type: Type of fold operation (compression, eviction, etc.)
            fold_count: Number of folds involved
            compression_ratio: Compression ratio achieved
            success: Whether operation succeeded
        """
        attributes = {
            "fold.operation": operation_type,
            "fold.success": success,
        }

        if fold_count is not None:
            attributes["fold.count"] = fold_count

        if compression_ratio is not None:
            attributes["fold.compression_ratio"] = compression_ratio

        with self.trace_operation(f"fold_{operation_type}", attributes):
            # Record metrics
            if self._meter:
                self.fold_operations_counter.add(
                    1,
                    {"operation": operation_type, "success": str(success)}
                )


def trace_function(
    operation_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
):
    """
    Decorator for tracing function execution.

    Args:
        operation_name: Custom operation name (defaults to function name)
        attributes: Additional span attributes

    Example:
        @trace_function("custom_operation", {"component": "memory"})
        def my_function():
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_lukhas_tracer()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            # Extract self attributes for class methods
            func_attributes = attributes or {}
            if args and hasattr(args[0], '__class__'):
                func_attributes["class"] = args[0].__class__.__name__

            with tracer.trace_operation(op_name, func_attributes):
                return func(*args, **kwargs)

        return wrapper
    return decorator


# Global tracer instance
_lukhas_tracer: Optional[LUKHASTracer] = None


def initialize_tracing(
    service_name: str = "lukhas-ai",
    service_version: str = "1.0.0",
    jaeger_endpoint: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
    enable_auto_instrumentation: bool = True,
) -> LUKHASTracer:
    """
    Initialize global LUKHAS tracing.

    Args:
        service_name: Name of the LUKHAS service
        service_version: Version identifier
        jaeger_endpoint: Jaeger collector endpoint
        otlp_endpoint: OTLP endpoint for trace/metric export
        enable_auto_instrumentation: Enable automatic library instrumentation

    Returns:
        Configured LUKHASTracer instance
    """
    global _lukhas_tracer

    # Use environment variables as defaults
    jaeger_endpoint = jaeger_endpoint or os.getenv("LUKHAS_JAEGER_ENDPOINT")
    otlp_endpoint = otlp_endpoint or os.getenv("LUKHAS_OTLP_ENDPOINT")

    _lukhas_tracer = LUKHASTracer(
        service_name=service_name,
        service_version=service_version,
        jaeger_endpoint=jaeger_endpoint,
        otlp_endpoint=otlp_endpoint,
        enable_auto_instrumentation=enable_auto_instrumentation,
    )

    return _lukhas_tracer


def get_lukhas_tracer() -> LUKHASTracer:
    """Get or create the global LUKHAS tracer"""
    global _lukhas_tracer
    if _lukhas_tracer is None:
        _lukhas_tracer = initialize_tracing()
    return _lukhas_tracer


def shutdown_tracing():
    """Shutdown tracing and flush remaining spans"""
    if OTEL_AVAILABLE:
        try:
            # Flush and shutdown trace provider
            if hasattr(trace.get_tracer_provider(), 'shutdown'):
                trace.get_tracer_provider().shutdown()

            # Flush and shutdown metrics provider
            if hasattr(metrics.get_meter_provider(), 'shutdown'):
                metrics.get_meter_provider().shutdown()
        except Exception as e:
            print(f"Warning: Error during tracing shutdown: {e}")


# Context managers for common operations
@contextmanager
def trace_memory_recall(item_count: int):
    """Context manager for tracing memory recall operations"""
    tracer = get_lukhas_tracer()
    start_time = time.perf_counter()

    try:
        with tracer.trace_operation(
            "memory_recall",
            {"memory.item_count": item_count}
        ):
            yield
        # Record successful operation
        latency_ms = (time.perf_counter() - start_time) * 1000
        tracer.trace_memory_operation("recall", item_count, latency_ms, True)

    except Exception:
        # Record failed operation
        latency_ms = (time.perf_counter() - start_time) * 1000
        tracer.trace_memory_operation("recall", item_count, latency_ms, False)
        raise


@contextmanager
def trace_matriz_execution():
    """Context manager for tracing complete MATRIZ pipeline"""
    tracer = get_lukhas_tracer()
    start_time = time.perf_counter()
    stages_completed = 0
    stages_failed = 0

    try:
        yield {"stages_completed": stages_completed, "stages_failed": stages_failed}
        # Record successful pipeline
        duration_ms = (time.perf_counter() - start_time) * 1000
        tracer.trace_matriz_pipeline(
            duration_ms,
            stages_completed,
            stages_failed,
            duration_ms < 250,  # Within T4/0.01% budget
        )

    except Exception:
        # Record failed pipeline
        duration_ms = (time.perf_counter() - start_time) * 1000
        tracer.trace_matriz_pipeline(
            duration_ms,
            stages_completed,
            stages_failed + 1,
            False,
        )
        raise
