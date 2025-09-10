"""
Integrations Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .nias_dream_bridge import NiasDreamBridge

    logger.debug("Imported NiasDreamBridge from .nias_dream_bridge")
except ImportError as e:
    logger.warning(f"Could not import NiasDreamBridge: {e}")
    NiasDreamBridge = None

__all__ = [
    "NiasDreamBridge",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"integrations module initialized. Available components: {__all__}")