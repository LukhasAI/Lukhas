"""
Collapse Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .vector_ops import VectorOps

    logger.debug("Imported VectorOps from .vector_ops")
except ImportError as e:
    logger.warning(f"Could not import VectorOps: {e}")
    VectorOps = None

__all__ = [
    "VectorOps",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"collapse module initialized. Available components: {__all__}")