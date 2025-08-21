"""
Ai Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .integration_manager import IntegrationManager

    logger.debug("Imported IntegrationManager from .integration_manager")
except ImportError as e:
    logger.warning(f"Could not import IntegrationManager: {e}")
    IntegrationManager = None

__all__ = [
    "IntegrationManager",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"ai module initialized. Available components: {__all__}")
