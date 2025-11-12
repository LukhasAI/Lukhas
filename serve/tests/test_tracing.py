import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from unittest.mock import patch, MagicMock

from serve.tracing import setup_tracing


@pytest.fixture(autouse=True)
def reset_tracing_globals():
    """
    Ensures a clean global tracing state for each test by resetting the
    internal 'once' guard in the opentelemetry-api library. This allows
    each test to configure the global TracerProvider independently.
    """
    from opentelemetry.util._once import Once
    trace._TRACER_PROVIDER_SET_ONCE = Once()
    yield
    trace._TRACER_PROVIDER_SET_ONCE = Once()
    trace.set_tracer_provider(TracerProvider())


@pytest.fixture
def app():
    """Provides a simple FastAPI app for testing and ensures it's uninstrumented afterward."""
    _app = FastAPI()

    @_app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    yield _app

    FastAPIInstrumentor.uninstrument_app(_app)


def test_setup_tracing_sets_tracer_provider():
    """Verifies that a TracerProvider is set globally."""
    mock_provider_instance = MagicMock(spec=TracerProvider)
    with patch("serve.tracing.trace.set_tracer_provider") as mock_set_provider, \
         patch("serve.tracing.trace.get_tracer_provider", return_value=mock_provider_instance):
        setup_tracing(MagicMock())
        mock_set_provider.assert_called_once()
        provider_arg = mock_set_provider.call_args[0][0]
        assert isinstance(provider_arg, TracerProvider)
        assert provider_arg.resource.attributes["service.name"] == "lukhas-api"


def test_setup_tracing_adds_batch_span_processor():
    """Verifies that a BatchSpanProcessor is added to the provider."""
    mock_provider = MagicMock(spec=TracerProvider)
    with patch("serve.tracing.trace.get_tracer_provider", return_value=mock_provider), \
         patch("serve.tracing.trace.set_tracer_provider"), \
         patch("serve.tracing.OTLPSpanExporter"):
        setup_tracing(MagicMock())
        mock_provider.add_span_processor.assert_called_once()
        processor_arg = mock_provider.add_span_processor.call_args[0][0]
        assert isinstance(processor_arg, BatchSpanProcessor)


def test_setup_tracing_uses_otlp_exporter():
    """Verifies that the BatchSpanProcessor is configured with an OTLPSpanExporter."""
    with patch("serve.tracing.BatchSpanProcessor") as mock_batch_processor, \
         patch("serve.tracing.OTLPSpanExporter") as mock_otlp_exporter, \
         patch("serve.tracing.trace.set_tracer_provider"), \
         patch("serve.tracing.trace.get_tracer_provider"):
        setup_tracing(MagicMock())
        mock_batch_processor.assert_called_once()
        exporter_arg = mock_batch_processor.call_args[0][0]
        assert isinstance(exporter_arg, mock_otlp_exporter.return_value.__class__)


def test_setup_tracing_instruments_fastapi_app():
    """Verifies that the FastAPI app is instrumented."""
    with patch("serve.tracing.FastAPIInstrumentor.instrument_app") as mock_instrument, \
         patch("serve.tracing.trace.set_tracer_provider"), \
         patch("serve.tracing.trace.get_tracer_provider"):
        app = MagicMock()
        setup_tracing(app)
        mock_instrument.assert_called_once_with(app)


def test_trace_generation_after_setup(app):
    """
    An integration-style test to verify that after setup_tracing is called,
    requests to the instrumented app generate spans with the correct resource.
    """
    in_memory_exporter = InMemorySpanExporter()
    span_processor = SimpleSpanProcessor(in_memory_exporter)

    with patch("serve.tracing.OTLPSpanExporter", return_value=in_memory_exporter), \
         patch("serve.tracing.BatchSpanProcessor", return_value=span_processor):
        setup_tracing(app)

    with TestClient(app) as client:
        client.get("/test")

    spans = in_memory_exporter.get_finished_spans()
    assert len(spans) > 0

    server_span = next((s for s in spans if s.name == "GET /test"), None)

    assert server_span is not None
    assert server_span.resource.attributes["service.name"] == "lukhas-api"


def test_uninstrumented_performance(benchmark, app):
    """Measures the performance of the uninstrumented application."""
    with TestClient(app) as client:
        benchmark(client.get, "/test")


def test_instrumented_performance(benchmark, app):
    """Measures the performance of the instrumented application."""
    setup_tracing(app)
    with TestClient(app) as client:
        benchmark(client.get, "/test")
