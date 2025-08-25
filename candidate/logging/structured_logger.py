import logging
import sys
import structlog
from typing import Literal, Optional, List

# Define a type for log level strings
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(
    log_level: LogLevel = "INFO",
    log_format: Literal["json", "text"] = "text",
    is_dev_mode: bool = False,
):
    """
    Configures structured logging for the entire application.

    This should be called once at application startup.

    Args:
        log_level: The minimum log level to output.
        log_format: The format for logs ('json' for machine-readable, 'text' for human-readable).
        is_dev_mode: If True, uses more development-friendly settings like pretty-printed JSON.
    """
    log_level = log_level.upper()

    # Define processors shared across different formats
    shared_processors: List[structlog.types.Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.contextvars.merge_contextvars,
        structlog.processors.format_exc_info,
        structlog.processors.StackInfoRenderer(),
    ]

    # Select renderer based on format
    if log_format == "json":
        renderer = structlog.processors.JSONRenderer(
            indent=2 if is_dev_mode else None
        )
    else:  # text format
        renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.rich_traceback,
        )

    processors = shared_processors + [renderer]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure the standard logging library to play nicely with structlog
    # This ensures that logs from other libraries are also processed by structlog
    stdlib_log_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=stdlib_log_level,
    )

    logger = structlog.get_logger("structured_logger_setup")
    logger.info(
        "Structured logging configured",
        log_level=log_level,
        log_format=log_format,
        dev_mode=is_dev_mode,
    )


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Returns a configured structlog logger instance.

    Args:
        name: The name of the logger, typically __name__ of the calling module.

    Returns:
        A BoundLogger instance.
    """
    return structlog.get_logger(name)


if __name__ == "__main__":
    print("--- Demonstrating Structured Logging ---")

    print("\n--- 1. Text format (INFO level) ---")
    setup_logging(log_level="INFO", log_format="text", is_dev_mode=True)
    log = get_logger(__name__)
    log.debug("This is a debug message.", data={"key": "value"})
    log.info("This is an info message.", user_id="user-123")
    log.warning("This is a warning.", details="Something might be wrong.")
    try:
        1 / 0
    except ZeroDivisionError:
        log.error("An exception occurred.", exc_info=True)

    print("\n--- 2. JSON format (DEBUG level) ---")
    setup_logging(log_level="DEBUG", log_format="json", is_dev_mode=True)
    log = get_logger("json_logger_demo")
    log.debug("This is a debug message.", data={"key": "value"})
    log.info(
        "This is an info message with more context.",
        user_id="user-456",
        request_id="req-abc",
    )
    log.bind(session_id="session-xyz").warning("This warning has bound context.")
