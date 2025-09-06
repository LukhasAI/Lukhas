import logging
logger = logging.getLogger(__name__)
"""
Protection Module
Auto-generated module initialization file
"""

from candidate.core.common import get_logger

logger = get_logger(__name__)

try:
    from .symbolic_quarantine_sanctum import SymbolicQuarantineSanctum

    logger.debug("Imported SymbolicQuarantineSanctum from .symbolic_quarantine_sanctum")
except ImportError as e:
    logger.warning(f"Could not import SymbolicQuarantineSanctum: {e}")
    SymbolicQuarantineSanctum = None

__all__ = [
    "SymbolicQuarantineSanctum",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"protection module initialized. Available components: {__all__}")