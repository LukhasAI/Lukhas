import logging
logger = logging.getLogger(__name__)
"""
Integrity Module
Auto-generated module initialization file
"""

from candidate.core.common import get_logger

logger = get_logger(__name__)

try:
    from .collapse_hash import CollapseHash

    logger.debug("Imported CollapseHash from .collapse_hash")
except ImportError as e:
    logger.warning(f"Could not import CollapseHash: {e}")
    CollapseHash = None

__all__ = [
    "CollapseHash",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"integrity module initialized. Available components: {__all__}")