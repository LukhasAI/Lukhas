"""
📝 Common Logger Factory
=======================
Centralized logging configuration for all LUKHAS modules.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Optional


class LukhasFormatter(logging.Formatter):
    """Custom formatter with GLYPH symbols for log levels"""

    SYMBOLS = {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }

    def format(self, record):
        # Add symbol to record
        record.symbol = self.SYMBOLS.get(record.levelno, "📝")

        # Add module context
        if hasattr(record, "module_name"):
            record.module_context = f"[{record.module_name}]"
        else:
            record.module_context = ""

        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "thread": record.thread,
            "thread_name": record.threadName,
        }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


# Global logger cache
_loggers: dict[str, logging.Logger] = {}

# Global configuration
_logging_config = {
    "level": logging.INFO,
    "format": "standard",
    "handlers": ["console"],
    "propagate": False,
}


def configure_logging(
    level: str = "INFO",
    format_type: str = "standard",
    log_file: Optional[str] = None,
    json_output: bool = False,
) -> None:
    """
    Configure global logging settings.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type ('standard', 'detailed', 'minimal')
        log_file: Optional log file path
        json_output: Use JSON formatting
    """
    global _logging_config

    _logging_config["level"] = getattr(logging, level.upper())
    _logging_config["format"] = format_type
    _logging_config["json_output"] = json_output

    if log_file:
        _logging_config["log_file"] = log_file
        _logging_config["handlers"].append("file")

    # Apply to existing loggers
    for logger in _loggers.values():
        _configure_logger(logger)


def get_logger(name: str, module_name: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (usually __name__)
        module_name: Optional LUKHAS module name for context

    Returns:
        Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)

    # Add module context
    if module_name:
        logger = logging.LoggerAdapter(logger, {"module_name": module_name})

    _configure_logger(logger)
    _loggers[name] = logger

    return logger


def _configure_logger(logger: logging.Logger) -> None:
    """Apply configuration to a logger"""
    # Clear existing handlers
    logger.handlers.clear()

    # Set level
    logger.setLevel(_logging_config["level"])
    logger.propagate = _logging_config.get("propagate", False)

    # Configure formatter
    if _logging_config.get("json_output"):
        formatter = JSONFormatter()
    else:
        formats = {
            "standard": "%(symbol)s %(asctime)s %(module_context)s %(name)s - %(levelname)s - %(message)s",
            "detailed": "%(symbol)s %(asctime)s %(module_context)s [%(name)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
            "minimal": "%(symbol)s %(levelname)s - %(message)s",
        }

        format_str = formats.get(_logging_config["format"], formats["standard"])
        formatter = LukhasFormatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")

    # Add console handler
    if "console" in _logging_config.get("handlers", ["console"]):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler
    if "file" in _logging_config.get("handlers", []) and "log_file" in _logging_config:
        file_handler = logging.FileHandler(_logging_config["log_file"])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


# Convenience function for module loggers


def get_module_logger(module_path: str) -> logging.Logger:
    """
    Get logger for a LUKHAS module.

    Args:
        module_path: Full module path (e.g., 'consciousness.unified.auto_consciousness')

    Returns:
        Configured logger with module context
    """
    parts = module_path.split(".")
    if parts and parts[0] in [
        "consciousness",
        "memory",
        "governance",
        "reasoning",
        "quantum",
        "bio",
        "emotion",
        "creativity",
        "identity",
        "bridge",
        "security",
        "orchestration",
        "core",
        "api",
    ]:
        module_name = parts[0].upper()
    else:
        module_name = "LUKHAS"

    return get_logger(module_path, module_name)
