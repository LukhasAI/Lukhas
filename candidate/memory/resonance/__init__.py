import logging

logger = logging.getLogger(__name__)
"""
Resonance Module
Auto-generated module initialization file
"""

from lukhas.core.common import get_logger

logger = get_logger(__name__)

try:
    from .resonant_memory_access import ResonantMemoryAccess

    logger.debug("Imported ResonantMemoryAccess from .resonant_memory_access")
except ImportError as e:
    logger.warning(f"Could not import ResonantMemoryAccess: {e}")
    ResonantMemoryAccess = None

__all__ = [
    "ResonantMemoryAccess",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"resonance module initialized. Available components: {__all__}")
