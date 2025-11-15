"""
Minimal smoke test for lukhas.observability.otel_config.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock the entire opentelemetry package before the module under test is imported.
sys.modules['opentelemetry'] = MagicMock()
sys.modules['opentelemetry.trace'] = MagicMock()
sys.modules['opentelemetry.sdk'] = MagicMock()
sys.modules['opentelemetry.sdk.trace'] = MagicMock()
sys.modules['opentelemetry.sdk.trace.export'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.grpc.trace_exporter'] = MagicMock()
sys.modules['opentelemetry.sdk.resources'] = MagicMock()

class TestOtelConfigSmoke(unittest.TestCase):
    """A minimal smoke test to ensure the setup function can be called."""

    def setUp(self):
        """Unload the module to ensure a fresh import."""
        if 'lukhas.observability.otel_config' in sys.modules:
            del sys.modules['lukhas.observability.otel_config']

    @patch('lukhas.observability.otel_config.os.getenv')
    def test_setup_opentelemetry_runs_without_error(self, mock_getenv):
        """
        Verify that setup_opentelemetry can be called without raising an exception
        when the OTel libraries are mocked.
        """
        # --- Arrange ---
        # By having the 'opentelemetry' key in sys.modules, the import should succeed
        # and OTEL_AVAILABLE should be True.
        from lukhas.observability import otel_config

        mock_getenv.return_value = "http://localhost:4317"

        # --- Act & Assert ---
        try:
            otel_config.setup_opentelemetry(service_name="smoke_test")
            # If we get here, the test has passed.
        except Exception as e:
            self.fail(f"setup_opentelemetry raised an unexpected exception: {e}")

if __name__ == '__main__':
    unittest.main()
