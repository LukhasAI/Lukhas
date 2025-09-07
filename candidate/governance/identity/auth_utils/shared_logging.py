import logging

logger = logging.getLogger(__name__)
# shared_logging.py
import logging

# Centralized logger for LUKHAS modules
import sys

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, stream=sys.stdout)

"""Get a logger with a unified format and level."""
return logging.getLogger(name)
