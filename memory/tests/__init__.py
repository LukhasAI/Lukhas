"""
Tests Module
Auto-generated module initialization file
"""

from core.common import get_logger

logger = get_logger(__name__)

try:
    from .test_unified_memory import TestUnifiedMemory

    logger.debug("Imported TestUnifiedMemory from .test_unified_memory")
except ImportError as e:
    logger.warning(f"Could not import TestUnifiedMemory: {e}")
    TestUnifiedMemory = None

__all__ = [
    "TestUnifiedMemory",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"tests module initialized. Available components: {__all__}")
