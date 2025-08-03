"""
Episodic Module
Auto-generated module initialization file
"""

from core.common import get_logger

logger = get_logger(__name__)

try:
    from .recaller import Recaller
    logger.debug("Imported Recaller from .recaller")
except ImportError as e:
    logger.warning(f"Could not import Recaller: {e}")
    Recaller = None

try:
    from .drift_tracker import DriftTracker
    logger.debug("Imported DriftTracker from .drift_tracker")
except ImportError as e:
    logger.warning(f"Could not import DriftTracker: {e}")
    DriftTracker = None

__all__ = [
    'Recaller',
    'DriftTracker',
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"episodic module initialized. Available components: {__all__}")
