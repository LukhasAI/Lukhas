#!/usr/bin/env python3
"""
T4-Grade Logging Configuration for LUKHAS AI
===========================================

Production-ready logging system with:
- Structured logging with JSON format
- Security-aware log filtering
- Performance monitoring integration
- Audit trail compliance
- Trinity Framework context inclusion

Author: LUKHAS AI T4 Team
Version: 1.0.0
"""
import streamlit as st

import logging
import logging.config
import os
import sys
import threading  # Import at top to avoid E402
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar, Optional

import structlog
from pythonjsonlogger import jsonlogger

# ======================================================================
# SECURITY LOG FILTERING
# ======================================================================


class SecurityLogFilter(logging.Filter):
    """Filter sensitive information from log messages."""

    SENSITIVE_PATTERNS: ClassVar[list[str]] = [
        # API keys and tokens
        r'(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[\'"][^\'"]+[\'"]',
        r"sk-[a-zA-Z0-9]{32,}",  # OpenAI API keys
        r"Bearer\s+[a-zA-Z0-9\-._~+/]+=*",  # Bearer tokens
        # Personal information
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email addresses
        r"\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b",  # Credit card numbers
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        # Internal paths and IPs
        r"/home/[^/\s]+",
        r"/Users/[^/\s]+",
        r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",  # IP addresses
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out sensitive information from log records."""
        import re

        # Sanitize the message
        if hasattr(record, "msg") and record.msg:
            message = str(record.msg)
            for pattern in self.SENSITIVE_PATTERNS:
                message = re.sub(pattern, "[REDACTED]", message)
            record.msg = message

        # Sanitize args if present
        if hasattr(record, "args") and record.args:
            safe_args = []
            for arg in record.args:
                arg_str = str(arg)
                for pattern in self.SENSITIVE_PATTERNS:
                    arg_str = re.sub(pattern, "[REDACTED]", arg_str)
                safe_args.append(arg_str)
            record.args = tuple(safe_args)

        return True


# ======================================================================
# PERFORMANCE LOG FILTER
# ======================================================================


class PerformanceLogFilter(logging.Filter):
    """Add performance context to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add performance timing information to log records."""
        import time

        # Add timestamp with microsecond precision
        record.timestamp_us = int(time.time() * 1000000)

        # Add process and thread info for performance debugging
        record.process_id = os.getpid()
        record.thread_id = int(f"{threading.current_thread()}.ident}")

        return True


# ======================================================================
# TRINITY FRAMEWORK LOG FILTER
# ======================================================================


class TrinityLogFilter(logging.Filter):
    """Add Trinity Framework context to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add Trinity Framework (⚛️🧠🛡️) context to log records."""
        # Add Trinity context
        record.trinity_identity = getattr(record, "identity_context", "unknown")
        record.trinity_consciousness = getattr(record, "consciousness_state", "inactive")
        record.trinity_guardian = getattr(record, "guardian_active", False)

        # Add module categorization
        module = getattr(record, "name", "")
        if "identity" in module:
            record.trinity_component = "⚛️_identity"
        elif "consciousness" in module or "memory" in module:
            record.trinity_component = "🧠_consciousness"
        elif "guardian" in module or "governance" in module:
            record.trinity_component = "🛡️_guardian"
        else:
            record.trinity_component = "🔧_system"

        return True


# ======================================================================
# CUSTOM JSON FORMATTER
# ======================================================================


class LukhasJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for LUKHAS AI logs."""

    def add_fields(self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]) -> None:
        """Add custom fields to log records."""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = getattr(record, "module", "unknown")
        log_record["function"] = getattr(record, "funcName", "unknown")
        log_record["line"] = getattr(record, "lineno", 0)

        # Add Trinity Framework context
        log_record["trinity_component"] = getattr(record, "trinity_component", "🔧_system")
        log_record["trinity_identity"] = getattr(record, "trinity_identity", "unknown")
        log_record["trinity_consciousness"] = getattr(record, "trinity_consciousness", "inactive")
        log_record["trinity_guardian"] = getattr(record, "trinity_guardian", False)

        # Add performance context
        log_record["process_id"] = getattr(record, "process_id", os.getpid())
        log_record["thread_id"] = getattr(record, "thread_id", 0)
        log_record["timestamp_us"] = getattr(record, "timestamp_us", 0)

        # Add environment context
        log_record["environment"] = os.getenv("ENVIRONMENT", "development")
        log_record["version"] = os.getenv("LUKHAS_VERSION", "1.0.0")

        # Add exception information if present
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }


# ======================================================================
# LOG CONFIGURATION
# ======================================================================


def get_log_level() -> str:
    """Get log level from environment."""
    level = os.getenv("LUKHAS_LOG_LEVEL", "INFO").upper()
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    return level if level in valid_levels else "INFO"


def get_log_config() -> dict[str, Any]:
    """Get comprehensive logging configuration."""

    log_level = get_log_level()
    environment = os.getenv("ENVIRONMENT", "development")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": LukhasJsonFormatter,
                "format": "%(timestamp)s %(level)s %(logger)s %(message)s",
            },
        },
        "filters": {
            "security_filter": {
                "()": SecurityLogFilter,
            },
            "performance_filter": {
                "()": PerformanceLogFilter,
            },
            "trinity_filter": {
                "()": TrinityLogFilter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "detailed" if environment == "development" else "standard",
                "stream": sys.stdout,
                "filters": ["security_filter", "trinity_filter"],
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json",
                "filename": str(log_dir / "lukhas.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "filters": ["security_filter", "performance_filter", "trinity_filter"],
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": str(log_dir / "lukhas_errors.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "filters": ["security_filter", "trinity_filter"],
            },
            "audit_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": str(log_dir / "lukhas_audit.log"),
                "maxBytes": 104857600,  # 100MB
                "backupCount": 50,
                "filters": ["security_filter", "trinity_filter"],
            },
            "performance_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "json",
                "filename": str(log_dir / "lukhas_performance.log"),
                "maxBytes": 52428800,  # 50MB
                "backupCount": 10,
                "filters": ["performance_filter"],
            },
        },
        "loggers": {
            # Root logger
            "": {
                "handlers": ["console", "file", "error_file"],
                "level": log_level,
                "propagate": False,
            },
            # LUKHAS core loggers
            "lukhas": {
                "handlers": ["console", "file", "error_file", "audit_file"],
                "level": log_level,
                "propagate": False,
            },
            "lukhas.governance": {
                "handlers": ["console", "file", "audit_file"],
                "level": log_level,
                "propagate": False,
            },
            "lukhas.consciousness": {
                "handlers": ["console", "file", "audit_file"],
                "level": log_level,
                "propagate": False,
            },
            "lukhas.identity": {
                "handlers": ["console", "file", "audit_file"],
                "level": log_level,
                "propagate": False,
            },
            "lukhas.bridge": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "lukhas.memory": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            # Performance logger
            "performance": {"handlers": ["performance_file"], "level": "DEBUG", "propagate": False},
            # Audit logger
            "audit": {"handlers": ["audit_file"], "level": "INFO", "propagate": False},
            # Third-party loggers
            "urllib3": {"handlers": ["file"], "level": "WARNING", "propagate": False},
            "requests": {"handlers": ["file"], "level": "WARNING", "propagate": False},
            "asyncio": {"handlers": ["file"], "level": "WARNING", "propagate": False},
        },
    }

    return config


# ======================================================================
# LOGGING SETUP FUNCTIONS
# ======================================================================


def setup_logging(config: Optional[dict[str, Any]] = None) -> None:
    """Set up comprehensive logging for LUKHAS AI."""
    if config is None:
        config = get_log_config()

    # Apply the logging configuration
    logging.config.dictConfig(config)

    # Set up structlog for structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        "LUKHAS AI T4-Grade Logging System Initialized",
        extra={
            "environment": os.getenv("ENVIRONMENT", "development"),
            "log_level": get_log_level(),
            "trinity_component": "🔧_system",
            "trinity_guardian": True,
        },
    )


def get_logger(name: str, **kwargs) -> logging.Logger:
    """Get a configured logger for a LUKHAS module."""
    logger = logging.getLogger(name)

    # Add module-specific context
    logger = structlog.wrap_logger(logger, module=name, **kwargs)

    return logger


def get_performance_logger() -> logging.Logger:
    """Get a logger specifically for performance metrics."""
    return logging.getLogger("performance")


def get_audit_logger() -> logging.Logger:
    """Get a logger specifically for audit trails."""
    return logging.getLogger("audit")


# ======================================================================
# CONTEXT MANAGERS
# ======================================================================


class LoggingContext:
    """Context manager for adding structured context to logs."""

    def __init__(self, logger: logging.Logger, **context: Any) -> None:
        self.logger = logger
        self.context = context
        self.original_extra = {}

    def __enter__(self) -> logging.Logger:
        # Store original context if it exists
        if hasattr(self.logger, "_context"):
            self.original_extra = self.logger._context.copy()
        else:
            self.logger._context = {}

        # Add new context
        self.logger._context.update(self.context)
        return self.logger

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        # Restore original context
        if self.original_extra:
            self.logger._context = self.original_extra
        else:
            self.logger._context = {}


class PerformanceLoggingContext:
    """Context manager for performance logging."""

    def __init__(self, logger: logging.Logger, operation: str, **context) -> None:
        self.logger = logger
        self.operation = operation
        self.context = context
        # Annotate timing fields for static type-checkers
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self) -> "PerformanceLoggingContext":
        import time

        self.start_time = time.perf_counter()
        self.logger.debug(
            f"Starting {self.operation}",
            extra={"operation": self.operation, "operation_status": "started", **self.context},
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        import time

        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time

        status = "completed" if exc_type is None else "failed"

        self.logger.info(
            f"{self.operation.title()} {status}",
            extra={
                "operation": self.operation,
                "operation_status": status,
                "duration_ms": duration * 1000,
                "duration_seconds": duration,
                "exception_type": exc_type.__name__ if exc_type else None,
                **self.context,
            },
        )


# ======================================================================
# INITIALIZATION
# ======================================================================

# Threading import moved to top of file

# Initialize logging on module import
if not os.getenv("LUKHAS_SKIP_LOG_INIT"):
    setup_logging()

# Export main functions
__all__ = [
    "LoggingContext",
    "PerformanceLoggingContext",
    "get_audit_logger",
    "get_log_config",
    "get_logger",
    "get_performance_logger",
    "setup_logging",
]
