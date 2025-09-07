"""
Symbolism Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .tags import TagScope

    logger.debug("Imported TagScope from .tags")
except ImportError as e:
    logger.warning(f"Could not import TagScope: {e}")
    TagScope = None

try:
    from .methylation_model import MethylationModel

    logger.debug("Imported MethylationModel from .methylation_model")
except ImportError as e:
    logger.warning(f"Could not import MethylationModel: {e}")
    MethylationModel = None

try:
    from .archiver import Archiver

    logger.debug("Imported Archiver from .archiver")
except ImportError as e:
    logger.warning(f"Could not import Archiver: {e}")
    Archiver = None

__all__ = [
    "Archiver",
    "MethylationModel",
    "Tags",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"symbolism module initialized. Available components: {__all__}")
