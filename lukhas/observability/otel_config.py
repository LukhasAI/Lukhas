# lukhas/observability/otel_config.py

import logging
from typing import Optional

# Mock missing modules if they are not installed
try:
    from fastapi import FastAPI
except ImportError:
    FastAPI = None

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
except ImportError:
    trace = None
    # Assign mock objects for the rest so checks don't fail
    OTLPSpanExporter = FastAPIInstrumentor = HTTPXClientInstrumentor = Psycopg2Instrumentor = RequestsInstrumentor = object
    Resource = SERVICE_NAME = TracerProvider = BatchSpanProcessor = object

try:
    from lukhas.core.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

# Global flag to ensure telemetry is configured only once.
_TELEMETRY_CONFIGURED = False

def setup_telemetry(app: Optional[FastAPI] = None, service_name: str = "lukhas-service"):
    """
    Configures OpenTelemetry tracing for the application.
    This function is idempotent and will only configure tracing once.
    """
    global _TELEMETRY_CONFIGURED
    if _TELEMETRY_CONFIGURED:
        logger.info("OpenTelemetry tracing is already configured.")
        return

    if not trace:
        logger.warning("OpenTelemetry packages not found. Tracing will be disabled.")
        return

    try:
        resource = Resource(attributes={
            SERVICE_NAME: service_name
        })

        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        otlp_exporter = OTLPSpanExporter()
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)

        if app and FastAPI and isinstance(app, FastAPI):
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI application instrumented for OpenTelemetry.")

        RequestsInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTP clients (requests, httpx) instrumented.")

        try:
            Psycopg2Instrumentor().instrument()
            logger.info("Psycopg2 (PostgreSQL) driver instrumented.")
        except ImportError:
            logger.debug("Psycopg2 not found, skipping instrumentation.")

        logger.info("OpenTelemetry tracing setup complete for service: %s", service_name)
        _TELEMETRY_CONFIGURED = True

    except Exception as e:
        logger.error("Failed to setup OpenTelemetry tracing: %s", e, exc_info=True)

def get_tracer(module_name: str):
    """
    Returns a tracer instance for a given module.
    """
    if not trace:
        class NoOpTracer:
            def start_as_current_span(self, *args, **kwargs):
                class NoOpSpan:
                    def __enter__(self): return self
                    def __exit__(self, *args): pass
                    def set_attribute(self, key, value): pass
                    def add_event(self, name, attributes=None): pass
                return NoOpSpan()
        return NoOpTracer()

    return trace.get_tracer(module_name)
