import logging
logger = logging.getLogger(__name__)
"""
Proteome Module
Auto-generated module initialization file
"""

from candidate.core.common import get_logger

logger = get_logger(__name__)

try:
    from .symbolic_proteome import SymbolicProteome

    logger.debug("Imported SymbolicProteome from .symbolic_proteome")
except ImportError as e:
    logger.warning(f"Could not import SymbolicProteome: {e}")
    SymbolicProteome = None

__all__ = [
    "SymbolicProteome",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"proteome module initialized. Available components: {__all__}")