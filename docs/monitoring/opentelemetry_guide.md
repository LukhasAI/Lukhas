# OpenTelemetry Tracing Guide

This guide provides an overview of the OpenTelemetry tracing setup in the `lukhas` project and explains how to use it for instrumenting your code.

## 1. Overview

The project uses a centralized OpenTelemetry configuration located in `lukhas/observability/otel_config.py`. This module is the single source of truth for all tracing-related setup and provides a simple, idempotent function to initialize telemetry.

The configuration is designed to be robust and will not crash the application if OpenTelemetry packages are not installed, allowing for flexible setups in different environments.

## 2. Automatic Instrumentation

The centralized setup automatically instruments several common libraries to provide out-of-the-box tracing for:

- **FastAPI**: Incoming web requests are automatically traced.
- **requests & httpx**: Outgoing HTTP calls made with these libraries are traced.
- **psycopg2**: Database calls to PostgreSQL are traced.

This means you get a good level of visibility into your application's performance without needing to add any manual instrumentation.

## 3. How to Initialize Tracing

To enable OpenTelemetry tracing, you need to call the `setup_telemetry` function once during your application's startup.

### For FastAPI Applications

If you are working with a FastAPI application, the best place to initialize tracing is in your main application file (e.g., `serve/main.py`).

```python
# serve/main.py
from fastapi import FastAPI
from lukhas.observability.otel_config import setup_telemetry

app = FastAPI()

# Call this function once to set up tracing
setup_telemetry(app=app, service_name="my-fastapi-service")

# ... rest of your application setup
```

The `setup_telemetry` function is idempotent, meaning it's safe to call it multiple times—it will only configure tracing on the first call.

## 4. Manual Instrumentation

For more detailed insights into your application's logic, you can add manual instrumentation using custom spans.

### Getting a Tracer

First, get a tracer instance for your module using the `get_tracer` helper function:

```python
# my_module.py
from lukhas.observability.otel_config import get_tracer

tracer = get_tracer(__name__)
```

### Creating Spans

You can create spans to trace specific blocks of code. The recommended way is to use the `start_as_current_span` context manager:

```python
def my_complex_function():
    with tracer.start_as_current_span("my_complex_function") as span:
        # Your complex logic here

        # You can add attributes (metadata) to the span
        span.set_attribute("my.custom.attribute", "some_value")

        # You can also add events
        span.add_event("Starting data processing")

        # ... process data ...

        span.add_event("Finished data processing")
```

These custom spans will be nested under the automatic spans (e.g., the FastAPI request span), giving you a detailed, hierarchical view of your application's execution.

## 5. Configuration via Environment Variables

The OpenTelemetry exporter can be configured using standard environment variables. The most common one you'll need is for setting the OTLP collector endpoint:

- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`: The full URL of the OTLP collector's gRPC endpoint (e.g., `http://localhost:4317`).
- `OTEL_EXPORTER_OTLP_ENDPOINT`: A fallback endpoint if the specific traces endpoint is not set.
- `OTEL_SERVICE_NAME`: This can be used to set the service name, although it's recommended to pass it explicitly to `setup_telemetry`.

By default, the exporter will try to connect to a local OTLP collector.

---
This guide should provide everything you need to get started with OpenTelemetry tracing in this project. Remember to consult the official [OpenTelemetry Python documentation](https://opentelemetry-python.readthedocs.io/) for more advanced usage.
