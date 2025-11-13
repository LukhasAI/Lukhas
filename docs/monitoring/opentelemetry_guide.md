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
