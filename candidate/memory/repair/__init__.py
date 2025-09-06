import logging
logger = logging.getLogger(__name__)
"""
Repair Module
Auto-generated module initialization file
"""

from candidate.core.common import get_logger

logger = get_logger(__name__)

try:
    from .advanced_trauma_repair import AdvancedTraumaRepair

    logger.debug("Imported AdvancedTraumaRepair from .advanced_trauma_repair")
except ImportError as e:
    logger.warning(f"Could not import AdvancedTraumaRepair: {e}")
    AdvancedTraumaRepair = None

try:
    from .helix_repair_module import HelixRepairModule

    logger.debug("Imported HelixRepairModule from .helix_repair_module")
except ImportError as e:
    logger.warning(f"Could not import HelixRepairModule: {e}")
    HelixRepairModule = None

__all__ = [
    "AdvancedTraumaRepair",
    "HelixRepairModule",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"repair module initialized. Available components: {__all__}")