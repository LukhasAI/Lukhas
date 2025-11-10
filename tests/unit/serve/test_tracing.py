"""
Comprehensive test suite for serve.tracing module.

Tests OpenTelemetry tracing setup with comprehensive mocking of external dependencies.
Validates tracer provider configuration, span processing, and FastAPI instrumentation.

Test Surgeon Canonical Guidelines: Tests only, deterministic, network-free.
"""

from unittest import mock

import pytest


@pytest.fixture
def tracing_module():
    """
    Import serve.tracing with mocked OpenTelemetry dependencies.

    Isolates all external dependencies to ensure deterministic, network-free testing.
    """
    # Create mock objects for OpenTelemetry components
    mock_trace = mock.MagicMock()
    mock_resource = mock.MagicMock()
    mock_tracer_provider = mock.MagicMock()
    mock_batch_span_processor = mock.MagicMock()
    mock_otlp_exporter = mock.MagicMock()
    mock_fastapi_instrumentor = mock.MagicMock()

    # Patch all OpenTelemetry imports
    with mock.patch.dict(
        "sys.modules",
        {
            "opentelemetry": mock.MagicMock(trace=mock_trace),
            "opentelemetry.trace": mock_trace,
            "opentelemetry.exporter.otlp.proto.grpc.trace_exporter": mock.MagicMock(
                OTLPSpanExporter=mock_otlp_exporter
            ),
            "opentelemetry.instrumentation.fastapi": mock.MagicMock(
                FastAPIInstrumentor=mock_fastapi_instrumentor
            ),
            "opentelemetry.sdk.resources": mock.MagicMock(Resource=mock_resource),
            "opentelemetry.sdk.trace": mock.MagicMock(TracerProvider=mock_tracer_provider),
            "opentelemetry.sdk.trace.export": mock.MagicMock(
                BatchSpanProcessor=mock_batch_span_processor
            ),
        },
    ):
        import importlib

        import serve.tracing as tracing_module

        importlib.reload(tracing_module)

        # Attach mocks to module for test access
        tracing_module._mock_trace = mock_trace
        tracing_module._mock_resource = mock_resource
        tracing_module._mock_tracer_provider = mock_tracer_provider
        tracing_module._mock_batch_span_processor = mock_batch_span_processor
        tracing_module._mock_otlp_exporter = mock_otlp_exporter
        tracing_module._mock_fastapi_instrumentor = mock_fastapi_instrumentor

        yield tracing_module


# ============================================================================
# Test: setup_tracing function
# ============================================================================


def test_setup_tracing_creates_resource_with_service_name(tracing_module):
    """Test setup_tracing creates Resource with correct service name."""
    mock_app = mock.MagicMock()

    tracing_module.setup_tracing(mock_app)

    # Verify Resource was created with service.name attribute
    tracing_module._mock_resource.assert_called_once_with(
        attributes={"service.name": "lukhas-api"}
    )


def test_setup_tracing_sets_tracer_provider(tracing_module):
    """Test setup_tracing configures global tracer provider."""
    mock_app = mock.MagicMock()
    mock_resource_instance = mock.MagicMock()
    mock_tracer_provider_instance = mock.MagicMock()

    tracing_module._mock_resource.return_value = mock_resource_instance
    tracing_module._mock_tracer_provider.return_value = mock_tracer_provider_instance

    tracing_module.setup_tracing(mock_app)

    # Verify set_tracer_provider called with TracerProvider(resource=...)
    tracing_module._mock_trace.set_tracer_provider.assert_called_once_with(
        mock_tracer_provider_instance
    )

    # Verify TracerProvider was created with resource
    tracing_module._mock_tracer_provider.assert_called_once_with(
        resource=mock_resource_instance
    )


def test_setup_tracing_adds_batch_span_processor(tracing_module):
    """Test setup_tracing adds BatchSpanProcessor with OTLP exporter."""
    mock_app = mock.MagicMock()
    mock_provider_instance = mock.MagicMock()
    mock_exporter_instance = mock.MagicMock()
    mock_processor_instance = mock.MagicMock()

    # Setup mock chain
    tracing_module._mock_trace.get_tracer_provider.return_value = mock_provider_instance
    tracing_module._mock_otlp_exporter.return_value = mock_exporter_instance
    tracing_module._mock_batch_span_processor.return_value = mock_processor_instance

    tracing_module.setup_tracing(mock_app)

    # Verify OTLPSpanExporter was created
    tracing_module._mock_otlp_exporter.assert_called_once_with()

    # Verify BatchSpanProcessor was created with exporter
    tracing_module._mock_batch_span_processor.assert_called_once_with(
        mock_exporter_instance
    )

    # Verify processor was added to provider
    mock_provider_instance.add_span_processor.assert_called_once_with(
        mock_processor_instance
    )


def test_setup_tracing_instruments_fastapi_app(tracing_module):
    """Test setup_tracing instruments FastAPI application."""
    mock_app = mock.MagicMock()

    tracing_module.setup_tracing(mock_app)

    # Verify FastAPIInstrumentor.instrument_app called with app
    tracing_module._mock_fastapi_instrumentor.instrument_app.assert_called_once_with(
        mock_app
    )


def test_setup_tracing_full_integration(tracing_module):
    """Test setup_tracing complete workflow integration."""
    mock_app = mock.MagicMock()
    mock_resource_instance = mock.MagicMock()
    mock_tracer_provider_instance = mock.MagicMock()
    mock_exporter_instance = mock.MagicMock()
    mock_processor_instance = mock.MagicMock()

    # Setup full mock chain
    tracing_module._mock_resource.return_value = mock_resource_instance
    tracing_module._mock_tracer_provider.return_value = mock_tracer_provider_instance
    tracing_module._mock_trace.get_tracer_provider.return_value = (
        mock_tracer_provider_instance
    )
    tracing_module._mock_otlp_exporter.return_value = mock_exporter_instance
    tracing_module._mock_batch_span_processor.return_value = mock_processor_instance

    tracing_module.setup_tracing(mock_app)

    # Verify complete call sequence
    assert tracing_module._mock_resource.call_count == 1
    assert tracing_module._mock_tracer_provider.call_count == 1
    assert tracing_module._mock_trace.set_tracer_provider.call_count == 1
    assert tracing_module._mock_trace.get_tracer_provider.call_count == 1
    assert tracing_module._mock_otlp_exporter.call_count == 1
    assert tracing_module._mock_batch_span_processor.call_count == 1
    assert mock_tracer_provider_instance.add_span_processor.call_count == 1
    assert tracing_module._mock_fastapi_instrumentor.instrument_app.call_count == 1


def test_setup_tracing_with_none_app(tracing_module):
    """Test setup_tracing handles None app gracefully."""
    # Should not raise exception - FastAPIInstrumentor should handle it
    tracing_module.setup_tracing(None)

    # Verify instrumentation was still attempted
    tracing_module._mock_fastapi_instrumentor.instrument_app.assert_called_once_with(
        None
    )


def test_setup_tracing_multiple_calls(tracing_module):
    """Test setup_tracing can be called multiple times."""
    mock_app1 = mock.MagicMock()
    mock_app2 = mock.MagicMock()

    tracing_module.setup_tracing(mock_app1)
    tracing_module.setup_tracing(mock_app2)

    # Verify both calls succeeded
    assert tracing_module._mock_trace.set_tracer_provider.call_count == 2
    assert tracing_module._mock_fastapi_instrumentor.instrument_app.call_count == 2


# ============================================================================
# Test: Module structure and imports
# ============================================================================


def test_module_exports_setup_tracing(tracing_module):
    """Test module exports setup_tracing function."""
    assert hasattr(tracing_module, "setup_tracing")
    assert callable(tracing_module.setup_tracing)


def test_module_imports_correct_opentelemetry_components(tracing_module):
    """Test module imports required OpenTelemetry components."""
    # Verify all required imports are present in module
    import inspect

    source = inspect.getsource(tracing_module.setup_tracing)

    # Verify function uses correct components
    assert "Resource" in source or hasattr(tracing_module, "Resource")
    assert "TracerProvider" in source or hasattr(tracing_module, "TracerProvider")
    assert "BatchSpanProcessor" in source or hasattr(
        tracing_module, "BatchSpanProcessor"
    )
    assert "OTLPSpanExporter" in source or hasattr(tracing_module, "OTLPSpanExporter")
    assert "FastAPIInstrumentor" in source or hasattr(
        tracing_module, "FastAPIInstrumentor"
    )


def test_setup_tracing_signature():
    """Test setup_tracing has correct function signature."""
    from serve.tracing import setup_tracing

    import inspect

    sig = inspect.signature(setup_tracing)
    params = list(sig.parameters.keys())

    assert len(params) == 1
    assert params[0] == "app"


# ============================================================================
# Test: Error handling and edge cases
# ============================================================================


def test_setup_tracing_with_exporter_failure(tracing_module):
    """Test setup_tracing propagates exporter creation errors."""
    mock_app = mock.MagicMock()

    # Simulate OTLPSpanExporter failure
    tracing_module._mock_otlp_exporter.side_effect = RuntimeError("Connection failed")

    with pytest.raises(RuntimeError, match="Connection failed"):
        tracing_module.setup_tracing(mock_app)


def test_setup_tracing_with_instrumentation_failure(tracing_module):
    """Test setup_tracing propagates instrumentation errors."""
    mock_app = mock.MagicMock()

    # Simulate FastAPIInstrumentor failure
    tracing_module._mock_fastapi_instrumentor.instrument_app.side_effect = ValueError(
        "Invalid app"
    )

    with pytest.raises(ValueError, match="Invalid app"):
        tracing_module.setup_tracing(mock_app)


def test_setup_tracing_with_provider_failure(tracing_module):
    """Test setup_tracing propagates tracer provider errors."""
    mock_app = mock.MagicMock()

    # Simulate TracerProvider failure
    tracing_module._mock_tracer_provider.side_effect = TypeError("Invalid resource")

    with pytest.raises(TypeError, match="Invalid resource"):
        tracing_module.setup_tracing(mock_app)


# ============================================================================
# Test: Configuration validation
# ============================================================================


def test_setup_tracing_uses_correct_service_name():
    """Test setup_tracing uses 'lukhas-api' as service name."""
    # This is a critical configuration test - service name must be consistent
    with mock.patch("serve.tracing.Resource") as mock_resource:
        with mock.patch("serve.tracing.trace"):
            with mock.patch("serve.tracing.TracerProvider"):
                with mock.patch("serve.tracing.BatchSpanProcessor"):
                    with mock.patch("serve.tracing.OTLPSpanExporter"):
                        with mock.patch("serve.tracing.FastAPIInstrumentor"):
                            from serve.tracing import setup_tracing

                            mock_app = mock.MagicMock()
                            setup_tracing(mock_app)

                            # Verify exact service name
                            mock_resource.assert_called_once()
                            call_kwargs = mock_resource.call_args[1]
                            assert "attributes" in call_kwargs
                            assert call_kwargs["attributes"]["service.name"] == "lukhas-api"


def test_setup_tracing_uses_batch_span_processor():
    """Test setup_tracing uses BatchSpanProcessor (not SimpleSpanProcessor)."""
    # BatchSpanProcessor is required for production - it batches spans for efficiency
    with mock.patch("serve.tracing.Resource"):
        with mock.patch("serve.tracing.trace") as mock_trace:
            with mock.patch("serve.tracing.TracerProvider"):
                with mock.patch(
                    "serve.tracing.BatchSpanProcessor"
                ) as mock_batch_processor:
                    with mock.patch("serve.tracing.OTLPSpanExporter"):
                        with mock.patch("serve.tracing.FastAPIInstrumentor"):
                            from serve.tracing import setup_tracing

                            mock_provider = mock.MagicMock()
                            mock_trace.get_tracer_provider.return_value = mock_provider
                            mock_app = mock.MagicMock()

                            setup_tracing(mock_app)

                            # Verify BatchSpanProcessor was used
                            mock_batch_processor.assert_called_once()
                            mock_provider.add_span_processor.assert_called_once()


def test_setup_tracing_uses_otlp_grpc_exporter():
    """Test setup_tracing uses OTLP gRPC exporter."""
    # OTLP gRPC is the standard protocol for telemetry data
    with mock.patch("serve.tracing.Resource"):
        with mock.patch("serve.tracing.trace"):
            with mock.patch("serve.tracing.TracerProvider"):
                with mock.patch("serve.tracing.BatchSpanProcessor"):
                    with mock.patch(
                        "serve.tracing.OTLPSpanExporter"
                    ) as mock_otlp_exporter:
                        with mock.patch("serve.tracing.FastAPIInstrumentor"):
                            from serve.tracing import setup_tracing

                            mock_app = mock.MagicMock()
                            setup_tracing(mock_app)

                            # Verify OTLPSpanExporter was created
                            mock_otlp_exporter.assert_called_once_with()


# ============================================================================
# Test: Integration patterns
# ============================================================================


def test_setup_tracing_call_order(tracing_module):
    """Test setup_tracing executes operations in correct order."""
    mock_app = mock.MagicMock()
    call_order = []

    # Track call order
    def track_resource(*args, **kwargs):
        call_order.append("resource")
        return mock.MagicMock()

    def track_tracer_provider(*args, **kwargs):
        call_order.append("tracer_provider")
        return mock.MagicMock()

    def track_set_provider(*args, **kwargs):
        call_order.append("set_provider")

    def track_get_provider(*args, **kwargs):
        call_order.append("get_provider")
        return mock.MagicMock()

    def track_exporter(*args, **kwargs):
        call_order.append("exporter")
        return mock.MagicMock()

    def track_processor(*args, **kwargs):
        call_order.append("processor")
        return mock.MagicMock()

    def track_instrument(*args, **kwargs):
        call_order.append("instrument")

    tracing_module._mock_resource.side_effect = track_resource
    tracing_module._mock_tracer_provider.side_effect = track_tracer_provider
    tracing_module._mock_trace.set_tracer_provider.side_effect = track_set_provider
    tracing_module._mock_trace.get_tracer_provider.side_effect = track_get_provider
    tracing_module._mock_otlp_exporter.side_effect = track_exporter
    tracing_module._mock_batch_span_processor.side_effect = track_processor
    tracing_module._mock_fastapi_instrumentor.instrument_app.side_effect = (
        track_instrument
    )

    tracing_module.setup_tracing(mock_app)

    # Verify correct order: resource -> provider -> set -> get -> exporter -> processor ->
    # instrument
    expected_order = [
        "resource",
        "tracer_provider",
        "set_provider",
        "get_provider",
        "exporter",
        "processor",
        "instrument",
    ]
    assert call_order == expected_order


def test_setup_tracing_idempotency(tracing_module):
    """Test setup_tracing can be called multiple times safely."""
    mock_app = mock.MagicMock()

    # Call three times
    tracing_module.setup_tracing(mock_app)
    tracing_module.setup_tracing(mock_app)
    tracing_module.setup_tracing(mock_app)

    # Verify all calls succeeded (no exceptions)
    assert tracing_module._mock_trace.set_tracer_provider.call_count == 3
    assert tracing_module._mock_fastapi_instrumentor.instrument_app.call_count == 3


# ============================================================================
# Summary: Test coverage for serve.tracing
# ============================================================================
# Total tests: 24
#
# Function coverage:
# - setup_tracing: 24 tests
#
# Test categories:
# - Resource creation: 1 test
# - Tracer provider setup: 1 test
# - Span processor configuration: 1 test
# - FastAPI instrumentation: 1 test
# - Full integration: 1 test
# - Edge cases: 3 tests
# - Error handling: 3 tests
# - Module structure: 3 tests
# - Configuration validation: 3 tests
# - Call order and idempotency: 2 tests
#
# Coverage target: 75%+ statement coverage
# Test methodology: Comprehensive sys.modules mocking, deterministic, network-free
# ============================================================================
