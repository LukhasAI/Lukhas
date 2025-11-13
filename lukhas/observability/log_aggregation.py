"""
Centralized logging configuration for LUKHAS using structlog.

This module provides a standardized logging setup that outputs logs in JSON format.
It includes trace ID correlation for distributed tracing and is prepared for
integration with Grafana Loki.
"""

import logging
import sys
from unittest.mock import MagicMock

# Mock missing modules that are not yet implemented.
# This allows for development and testing of this module without having the
# full application available.
try:
    from lukhas.trace import get_current_trace_id
except ImportError:
    get_current_trace_id = MagicMock(return_value="mock-trace-id-not-found")

try:
    import structlog
    from structlog.processors import JSONRenderer, TimeStamper, add_log_level
except ImportError:
    # If structlog is not installed, we mock it to prevent import errors.
    # In a real environment, this should be a dependency.
    structlog = MagicMock()

# Attempt to import a Loki handler. If it's not available, we can't send
# logs to Loki, but the application will still function.
try:
    from logging_loki import LokiHandler
    LOKI_ENABLED = True
except ImportError:
    LOKI_ENABLED = False


def add_trace_id(_, __, event_dict):
    """
    A structlog processor to add the current trace ID to the log entry.
    """
    event_dict["trace_id"] = get_current_trace_id()
    return event_dict


def configure_logging(log_level: str = "INFO", loki_url: str = None):
    """
    Configures the logging system for the application.

    Sets up structlog to process all logs, outputting them in JSON format
    to stdout. This configuration is designed to be used by all components

    of the LUKHAS system.

    Args:
        log_level: The minimum log level to output. Defaults to "INFO".
        loki_url: The URL of the Grafana Loki instance to send logs to.
                  If not provided, Loki integration is disabled.
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        stream=sys.stdout,
        format="%(message)s",
    )

    # Configure structlog processors.
    # These processors enrich the log entries with additional context.
    processors = [
        add_log_level,
        TimeStamper(fmt="iso"),
        add_trace_id,
        JSONRenderer(sort_keys=True),
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure Grafana Loki integration if enabled and a URL is provided.
    if LOKI_ENABLED and loki_url:
        handler = LokiHandler(
            url=loki_url,
            tags={"application": "lukhas"},
            version="1",
        )
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

    # Get a logger to confirm configuration.
    logger = structlog.get_logger("lukhas.observability.log_aggregation")
    logger.info("Logging configured successfully.", log_level=log_level, loki_enabled=LOKI_ENABLED and bool(loki_url))


if __name__ == "__main__":
    import os

    # Example: Get Loki URL from an environment variable.
    LOKI_URL_FROM_ENV = os.environ.get("LOKI_URL")

    configure_logging(loki_url=LOKI_URL_FROM_ENV)

    logger = structlog.get_logger(__name__)
    logger.info("This is an informational message.")
    logger.warning("This is a warning message.", some_key="some_value")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("An error occurred.")
