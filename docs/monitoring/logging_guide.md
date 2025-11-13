# LUKHAS Logging Guide

This document provides a guide to the centralized logging system used in the LUKHAS
project. The logging system is built on `structlog` and is designed to
produce structured, JSON-formatted logs that are easy to parse, search, and
analyze.

## Configuration

The logging system is configured in the `lukhas.observability.log_aggregation`
module. The `configure_logging` function in this module sets up the
necessary processors and formatters to produce the structured logs.

By default, logs are output to `stdout`.

## Log Format

All logs are formatted as JSON objects, with each log entry being a single line
in the output. This format is designed for easy integration with log aggregation
systems like Grafana Loki, Elasticsearch, or Splunk.

An example log entry looks like this:

```json
{
  "event": "This is an informational message.",
  "level": "info",
  "timestamp": "2023-10-27T10:00:00.000000Z",
  "trace_id": "mock-trace-id-12345"
}
```

### Standard Fields

-   `event`: The main log message.
-   `level`: The log level (e.g., `info`, `warning`, `error`).
-   `timestamp`: An ISO 8601 formatted timestamp indicating when the log was
    created.
-   `trace_id`: A unique identifier for the current request or transaction. This
    is used to correlate logs across different services.

You can add additional key-value pairs to the log entry by passing them as
keyword arguments to the logger:

```python
import structlog

logger = structlog.get_logger(__name__)
logger.info("User logged in.", user_id=123, ip_address="192.168.1.1")
```

This will produce a log entry like this:

```json
{
  "event": "User logged in.",
  "level": "info",
  "timestamp": "2023-10-27T10:05:00.000000Z",
  "trace_id": "mock-trace-id-67890",
  "user_id": 123,
  "ip_address": "192.168.1.1"
}
```

## Trace ID Correlation

The `trace_id` field is crucial for debugging and monitoring in a distributed
system. It allows you to trace a single request as it flows through multiple
services. The `trace_id` is automatically added to every log entry by the
`add_trace_id` processor.

The `get_current_trace_id` function from `lukhas.trace` is used to retrieve the
current trace ID. If no trace ID is found, a mock value is used.

## Grafana Loki Integration

The logging system is designed to be easily integrated with Grafana Loki. A
placeholder for the Loki handler is included in the `configure_logging` function.
To enable Loki integration, you will need to install a Loki handler library and
uncomment the placeholder code.
