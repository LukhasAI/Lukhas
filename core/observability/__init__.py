"""
Observability Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .collector import Collector

    logger.debug("Imported Collector from .collector")
except ImportError as e:
    logger.warning(f"Could not import Collector: {e}")
    Collector = None

__all__ = [
    "Collector",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"observability module initialized. Available components: {__all__}")
