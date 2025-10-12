"""
OpenTelemetry distributed tracing for LUKHAS MATRIZ.

Provides W3C trace context propagation, span hierarchy for request flows,
and integration with OTLP exporters for observability platforms.
"""
import os
import logging
from typing import Optional
from contextlib import contextmanager

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.semconv.resource import ResourceAttributes
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None  # type: ignore
    TracerProvider = None  # type: ignore
    BatchSpanProcessor = None  # type: ignore
    OTLPSpanExporter = None  # type: ignore

logger = logging.getLogger(__name__)


def setup_otel(service_name: str = "lukhas-matriz") -> Optional[any]:
    """
    Initialize OpenTelemetry tracing if endpoint configured.

    Returns tracer instance if OTEL is available and configured,
    None otherwise (graceful degradation).

    Args:
        service_name: Name of the service for trace identification

    Returns:
        Tracer instance or None
    """
    if not OTEL_AVAILABLE:
        logger.info("OpenTelemetry not available, tracing disabled")
        return None

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        logger.info("OTEL_EXPORTER_OTLP_ENDPOINT not set, tracing disabled")
        return None

    try:
        # Create resource with service metadata
        resource = Resource(attributes={
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.SERVICE_VERSION: os.getenv("LUKHAS_VERSION", "0.1.0"),
            "deployment.environment": os.getenv("LUKHAS_ENV", "development")
        })

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Add OTLP exporter with batch processing
        exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        # Set as global tracer provider
        trace.set_tracer_provider(provider)

        logger.info(f"OpenTelemetry tracing initialized, exporting to {endpoint}")
        return trace.get_tracer(__name__)

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}")
        return None


@contextmanager
def traced_operation(tracer, operation_name: str, **attributes):
    """
    Context manager for tracing an operation.

    Usage:
        with traced_operation(tracer, "matriz.process_query", user_id="123"):
            result = do_work()

    Args:
        tracer: OpenTelemetry tracer instance
        operation_name: Name of the operation (span name)
        **attributes: Additional span attributes
    """
    if not tracer or not OTEL_AVAILABLE:
        yield None
        return

    with tracer.start_as_current_span(operation_name) as span:
        # Set all provided attributes
        for key, value in attributes.items():
            span.set_attribute(key, str(value))
        yield span


def add_span_event(span, event_name: str, **attributes):
    """
    Add an event to the current span.

    Args:
        span: OpenTelemetry span instance
        event_name: Name of the event
        **attributes: Event attributes
    """
    if span and OTEL_AVAILABLE:
        span.add_event(event_name, attributes=attributes)


def get_trace_id_hex(span) -> Optional[str]:
    """
    Extract trace ID from span as hex string.

    Args:
        span: OpenTelemetry span instance

    Returns:
        32-character hex trace ID or None
    """
    if not span or not OTEL_AVAILABLE:
        return None

    try:
        trace_id = span.get_span_context().trace_id
        return format(trace_id, '032x')
    except Exception:
        return None
