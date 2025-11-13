"""Prometheus metrics configuration for LUKHAS."""

from observability.prometheus_registry import counter, histogram

REQUEST_DURATION_SECONDS = histogram(
    "request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

REQUESTS_TOTAL = counter(
    "requests_total",
    "Total number of requests",
    ["method", "endpoint", "http_status"],
)

ERRORS_TOTAL = counter(
    "errors_total",
    "Total number of errors",
    ["method", "endpoint", "error_type"],
)
