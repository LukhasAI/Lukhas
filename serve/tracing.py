# serve/tracing.py

try:
    from lukhas.observability.otel_config import setup_telemetry
except ImportError:
    # If the central config is not found, define a no-op function
    # to ensure the application can still run.
    def setup_telemetry(*args, **kwargs):
        # You could add a log warning here that tracing is not configured.
        pass

def setup_tracing(app):
    """
    Sets up OpenTelemetry tracing for the FastAPI application.
    This is a wrapper around the centralized telemetry setup function.
    """
    # The service name is hardcoded here, but could be read from config
    setup_telemetry(app, service_name="lukhas-api")
