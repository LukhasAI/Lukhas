"""
Logging Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Provide a stable logging entrypoint used by legacy tests."""
    return logging.getLogger(name)


__all__ = ["get_logger"]

logger.info(f"logging module initialized. Available components: {__all__}")
