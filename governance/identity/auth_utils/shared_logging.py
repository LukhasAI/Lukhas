# shared_logging.py
# Centralized logger for LUKHAS modules

import logging
import sys

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    stream=sys.stdout
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with a unified format and level."""
    return logging.getLogger(name)
