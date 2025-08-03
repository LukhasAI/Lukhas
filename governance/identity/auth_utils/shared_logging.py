# shared_logging.py
# Centralized logger for LUKHAS modules

from core.common import get_logger
import sys

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    stream=sys.stdout
)

    """Get a logger with a unified format and level."""
    return logging.getLogger(name)
