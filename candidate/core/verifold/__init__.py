"""
Verifold Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .verifold_unified import VerifoldUnified

    logger.debug("Imported VerifoldUnified from .verifold_unified")
except ImportError as e:
    logger.warning(f"Could not import VerifoldUnified: {e}")
    VerifoldUnified = None

__all__ = [
    "VerifoldUnified",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"verifold module initialized. Available components: {__all__}")