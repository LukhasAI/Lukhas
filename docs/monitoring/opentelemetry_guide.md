<<<<<<< HEAD
# OpenTelemetry Integration Guide

This guide provides instructions on how to use the automated OpenTelemetry (OTel) tracing integration within the `lukhas` platform.

## Overview

The `lukhas.observability.otel_config` module provides a centralized setup function to configure OpenTelemetry tracing for any service in the platform. When enabled, it automatically instruments common libraries to trace requests and operations across service boundaries.

Supported auto-instrumentation includes:
- FastAPI (for web application entry points)
- Requests (for synchronous HTTP calls)
- HTTPX (for asynchronous HTTP calls)
- AsyncPG and Psycopg2 (for database interactions)

## Configuration

### 1. Enabling the OTLP Exporter

To export traces, you must configure the OTLP exporter endpoint by setting an environment variable. The exporter sends traces to an OTel collector, such as Jaeger or Datadog.

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://<your-collector-host>:4317"
```

If this variable is not set, auto-instrumentation will still be active, but the collected traces will not be exported. This is safe for local development but not useful for production monitoring.

### 2. Initializing Tracing in Your Service

To enable tracing, call the `setup_opentelemetry` function once at the startup of your application. It is crucial to provide a `service_name` to correctly identify traces in your observability platform.

**Example for a FastAPI Application:**

```python
# in your main application file (e.g., serve/main.py)
from fastapi import FastAPI
from lukhas.observability.otel_config import setup_opentelemetry

# Define your service name
SERVICE_NAME = "my_fastapi_service"

app = FastAPI()

@app.on_event("startup")
def on_startup():
    """
    Application startup event handler.
    """
    # Initialize OpenTelemetry tracing
    setup_opentelemetry(service_name=SERVICE_NAME)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

# All routes on this app will now be traced automatically.
```

## Manual Tracing

While auto-instrumentation covers many cases, you may need to create custom spans to trace specific business logic or internal operations. The `lukhas.observability.distributed_tracing` module provides helpers for this.

### Creating Custom Spans

To create a new span, get a `Tracer` instance and use it as a context manager.

```python
from lukhas.observability.distributed_tracing import get_tracer

tracer = get_tracer(__name__)

def my_complex_function(arg1, arg2):
    with tracer.start_as_current_span("my_complex_function") as span:
        # Add attributes to the span for context
        span.set_attribute("function.arg1", str(arg1))
        span.set_attribute("function.arg2", str(arg2))

        # ... your function logic here ...

        result = arg1 + arg2
        span.set_attribute("function.result", result)
        return result
```

### Tracing MATRIZ Cognitive Nodes

For developers working with the MATRIZ engine, a decorator is available to automatically trace the `process` method of a cognitive node. This also handles the propagation of the trace context through the `ctx` dictionary.

```python
from lukhas.observability.distributed_tracing import trace_node_process

class MyCognitiveNode(ICognitiveNode):
    # ... other node methods ...

    @trace_node_process
    async def process(self, ctx: dict, *args, **kwargs) -> dict:
        # This method is now automatically traced.
        # The trace context will be passed to any downstream nodes.
        # ... your processing logic ...
        return {"status": "complete"}
```

By following this guide, you can ensure your services are properly instrumented for distributed tracing, providing valuable insights into the performance and behavior of the `lukhas` platform.
=======
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
>>>>>>> origin/main
