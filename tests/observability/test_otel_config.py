# tests/observability/test_otel_config.py

import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock all external dependencies before importing the module under test
sys.modules['fastapi'] = MagicMock()
sys.modules['opentelemetry'] = MagicMock()
sys.modules['opentelemetry.trace'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.grpc.trace_exporter'] = MagicMock()
sys.modules['opentelemetry.instrumentation.fastapi'] = MagicMock()
sys.modules['opentelemetry.instrumentation.httpx'] = MagicMock()
sys.modules['opentelemetry.instrumentation.psycopg2'] = MagicMock()
sys.modules['opentelemetry.instrumentation.requests'] = MagicMock()
sys.modules['opentelemetry.sdk.resources'] = MagicMock()
sys.modules['opentelemetry.sdk.trace'] = MagicMock()
sys.modules['opentelemetry.sdk.trace.export'] = MagicMock()

from lukhas.observability import otel_config

# Dummy class to correctly handle 'isinstance' checks in the code under test
class DummyFastAPI(MagicMock):
    pass

@patch('lukhas.observability.otel_config.FastAPI', new=DummyFastAPI)
class TestOtelConfig(unittest.TestCase):

    def setUp(self):
        # Reset the global flag before each test to ensure isolation
        otel_config._TELEMETRY_CONFIGURED = False
        # Also reset mocks that might be called
        otel_config.FastAPIInstrumentor.reset_mock()
        otel_config.trace.reset_mock()

    @patch('lukhas.observability.otel_config.Resource')
    @patch('lukhas.observability.otel_config.Psycopg2Instrumentor')
    @patch('lukhas.observability.otel_config.HTTPXClientInstrumentor')
    @patch('lukhas.observability.otel_config.RequestsInstrumentor')
    @patch('lukhas.observability.otel_config.OTLPSpanExporter')
    @patch('lukhas.observability.otel_config.BatchSpanProcessor')
    @patch('lukhas.observability.otel_config.TracerProvider')
    def test_setup_telemetry_configures_once(
        self, MockTracerProvider, MockBatchSpanProcessor, MockOTLPSpanExporter,
        MockRequestsInstrumentor, MockHTTPXClientInstrumentor, MockPsycopg2Instrumentor,
        MockResource
    ):
        """
        Tests that setup_telemetry correctly configures all components on the first call.
        """
        self.assertFalse(otel_config._TELEMETRY_CONFIGURED)

        # Use an instance of our dummy class
        mock_app = DummyFastAPI()

        otel_config.setup_telemetry(app=mock_app, service_name="test-service")

        # Verify that all components were configured
        MockResource.assert_called_once()
        MockTracerProvider.assert_called_once()
        otel_config.trace.set_tracer_provider.assert_called_once()
        MockBatchSpanProcessor.assert_called_once()
        # Check that the instrumentor was called on our dummy app
        otel_config.FastAPIInstrumentor.instrument_app.assert_called_once_with(mock_app)
        MockRequestsInstrumentor().instrument.assert_called_once()
        MockHTTPXClientInstrumentor().instrument.assert_called_once()
        MockPsycopg2Instrumentor().instrument.assert_called_once()

        self.assertTrue(otel_config._TELEMETRY_CONFIGURED)

    @patch('lukhas.observability.otel_config.logger')
    def test_setup_telemetry_does_not_reconfigure(self, mock_logger):
        """
        Tests that setup_telemetry does not re-run configuration if the global flag is set.
        """
        otel_config._TELEMETRY_CONFIGURED = True

        otel_config.setup_telemetry()

        otel_config.trace.set_tracer_provider.assert_not_called()
        mock_logger.info.assert_called_with("OpenTelemetry tracing is already configured.")

    @patch('lukhas.observability.otel_config.logger')
    def test_setup_telemetry_disables_if_packages_missing(self, mock_logger):
        """
        Tests that setup_telemetry is disabled if OpenTelemetry is not installed.
        """
        with patch('lukhas.observability.otel_config.trace', None):
            otel_config.setup_telemetry()
            mock_logger.warning.assert_called_with("OpenTelemetry packages not found. Tracing will be disabled.")

    def test_get_tracer_returns_tracer(self):
        """
        Tests that get_tracer returns a tracer instance when packages are available.
        """
        otel_config.get_tracer("test_module")
        otel_config.trace.get_tracer.assert_called_once_with("test_module")

    def test_get_tracer_returns_noop_if_packages_missing(self):
        """
        Tests that get_tracer returns a NoOp tracer if OpenTelemetry is not installed.
        """
        with patch('lukhas.observability.otel_config.trace', None):
            tracer = otel_config.get_tracer("test_module")
            self.assertTrue(hasattr(tracer, 'start_as_current_span'))


if __name__ == '__main__':
    unittest.main()
