"""
Configuration for OpenTelemetry tracing.

This module provides a centralized setup for the OpenTelemetry SDK,
including the tracer provider, span processor, and OTLP exporter.
It also enables auto-instrumentation for common libraries.
"""
from __future__ import annotations

import os
import logging
from typing import TYPE_CHECKING, List

# Use a try-except block to gracefully handle missing OpenTelemetry installation.
# This aligns with the pattern in distributed_tracing.py.
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Define dummy classes and objects to prevent NameError when OTel is not installed.
    # This ensures the code inside setup_opentelemetry can be safely executed.
    class _NoOpTracerProvider:
        def add_span_processor(self, processor): pass

    class _NoOpTrace:
        def get_tracer_provider(self):
            return _NoOpTracerProvider()
        def set_tracer_provider(self, provider): pass

    trace = _NoOpTrace()
    TracerProvider = _NoOpTracerProvider
    if TYPE_CHECKING:
        class BaseInstrumentor: pass


# List of instrumentors to apply. We will attempt to import and apply them safely.
# This makes the configuration extensible.
INSTRUMENTORS: List[str] = [
    "opentelemetry.instrumentation.fastapi.FastAPIInstrumentor",
    "opentelemetry.instrumentation.requests.RequestsInstrumentor",
    "opentelemetry.instrumentation.httpx.HTTPXClientInstrumentor",
    "opentelemetry.instrumentation.asyncpg.AsyncPGInstrumentor",
    "opentelemetry.instrumentation.psycopg2.Psycopg2Instrumentor",
]

_logger = logging.getLogger(__name__)


def _import_instrumentor(instrumentor_path: str):
    """
    Imports and returns an instrumentor class from its full path.
    Raises ImportError if the module or class cannot be found.
    """
    module_path, class_name = instrumentor_path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


def _get_instrumentors() -> List[BaseInstrumentor]:
    """Dynamically import and instantiate available instrumentors."""
    instrumentors = []
    if not OTEL_AVAILABLE:
        return []

    for instrumentor_path in INSTRUMENTORS:
        try:
            instrumentor_class = _import_instrumentor(instrumentor_path)
            instrumentors.append(instrumentor_class())
        except ImportError:
            _logger.debug(f"Instrumentation package for {instrumentor_path} not found. Skipping.")
        except Exception as e:
            _logger.error(f"Failed to instantiate instrumentor {instrumentor_path}: {e}")
    return instrumentors


def setup_opentelemetry(service_name: str = "lukhas_service") -> None:
    """
    Configures OpenTelemetry for the application.

    - Sets up a TracerProvider.
    - Configures a BatchSpanProcessor with an OTLPSpanExporter.
    - The exporter endpoint is configured via the OTEL_EXPORTER_OTLP_ENDPOINT env var.
    - Applies auto-instrumentation for supported libraries.
    """
    if not OTEL_AVAILABLE:
        _logger.warning("OpenTelemetry SDK not found. Tracing will be disabled.")
        return

    # Check if tracing is already configured
    if isinstance(trace.get_tracer_provider(), TracerProvider):
         _logger.info("OpenTelemetry TracerProvider already configured.")
         return

    # Configure the resource for the service
    resource = Resource.create(attributes={
        "service.name": service_name,
    })

    # Set up the tracer provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure the OTLP exporter
    # Endpoint is typically configured via OTEL_EXPORTER_OTLP_ENDPOINT
    # e.g., "http://localhost:4317"
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        _logger.warning("OTEL_EXPORTER_OTLP_ENDPOINT not set. Traces will not be exported.")
        # We can still instrument, but spans won't go anywhere.
        # Alternatively, could add a ConsoleSpanExporter for local dev.
    else:
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True) # Insecure for local dev
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        _logger.info(f"OpenTelemetry configured to export traces to {endpoint}.")


    # Apply auto-instrumentation
    for instrumentor in _get_instrumentors():
        try:
            # Check if already instrumented to avoid issues with double-instrumenting
            if not getattr(instrumentor, "is_instrumented_by_opentelemetry", False):
                instrumentor.instrument()
                _logger.info(f"Successfully instrumented {instrumentor.__class__.__name__}.")
        except Exception as e:
            _logger.error(f"Failed to apply instrumentation for {instrumentor.__class__.__name__}: {e}")

if __name__ == "__main__":
    # Example usage:
    logging.basicConfig(level=logging.INFO)
    _logger.info("Setting up OpenTelemetry for demonstration...")
    # In a real app, you would call this function at startup.
    # For example, in a FastAPI app:
    # @app.on_event("startup")
    # def on_startup():
    #     setup_opentelemetry(service_name="my_fastapi_app")
    setup_opentelemetry(service_name="example_service")

    # The following code would now be traced automatically if it makes calls
    # using libraries like requests or FastAPI.
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("example_span"):
        _logger.info("Inside a manually created span.")
    _logger.info("Demonstration complete.")
