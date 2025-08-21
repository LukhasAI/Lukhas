"""
Common utilities for LUKHAS accepted modules
Provides logging and shared functionality
"""

import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for the given module name

    Args:
        name: Module name for the logger, defaults to root logger

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)

    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


# Common constants
DRIFT_THRESHOLD = 0.15  # Guardian system drift threshold
FOLD_LIMIT = 1000  # Memory fold limit
TRINITY_SYMBOLS = {"identity": "⚛️", "consciousness": "🧠", "guardian": "🛡️"}
