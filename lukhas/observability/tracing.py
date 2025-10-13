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


def current_trace_id_hex() -> Optional[str]:
    """
    Get the current active trace ID as a 32-char hex string.

    Useful for error responses and exception handlers to include trace correlation.

    Returns:
        32-character hex trace ID or None if no active span
    """
    if not OTEL_AVAILABLE or not trace:
        return None

    try:
        span = trace.get_current_span()
        if span:
            ctx = span.get_span_context()
            if ctx and ctx.trace_id:
                return format(ctx.trace_id, '032x')
    except Exception:
        pass

    return None


# Phase 3: Trace header middleware for X-Trace-Id response header
try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response
    import uuid

    # Try to import Prometheus counter for trace coverage metrics
    try:
        from prometheus_client import Counter
        TRACE_COUNTER = Counter(
            "lukhas_trace_header_total",
            "Total responses with X-Trace-Id header",
            ["present", "source"]
        )
        PROMETHEUS_AVAILABLE_TRACE = True
    except ImportError:
        PROMETHEUS_AVAILABLE_TRACE = False
        TRACE_COUNTER = None

    class TraceHeaderMiddleware(BaseHTTPMiddleware):
        """
        Middleware to attach X-Trace-Id header to all responses.

        Extracts the current OpenTelemetry trace ID and adds it as a response
        header for correlation and debugging. If OpenTelemetry is unavailable
        or no span is active, generates a random UUID-based trace ID.

        Phase 3: Added as part of OpenAI surface polish.
        Phase 3.1: Added Prometheus counter for trace coverage alerting.
        """

        async def dispatch(self, request: Request, call_next) -> Response:
            resp = await call_next(request)

            # Attach trace ID if available from OTEL
            trace_id = None
            source = "fallback"
            if OTEL_AVAILABLE and trace:
                try:
                    span = trace.get_current_span()
                    ctx = span.get_span_context() if span else None
                    if ctx and ctx.trace_id:
                        trace_id = format(ctx.trace_id, "032x")
                        source = "otel"
                except Exception as e:
                    logger.debug(f"Failed to extract trace ID: {e}")

            # Generate trace ID if not from OTEL (32 hex chars)
            if not trace_id:
                trace_id = uuid.uuid4().hex

            resp.headers.setdefault("X-Trace-Id", trace_id)

            # Record trace coverage metrics
            if PROMETHEUS_AVAILABLE_TRACE and TRACE_COUNTER:
                try:
                    TRACE_COUNTER.labels(present="true", source=source).inc()
                except Exception:
                    pass

            return resp

except ImportError:
    # Starlette not available, middleware not usable
    TraceHeaderMiddleware = None  # type: ignore
