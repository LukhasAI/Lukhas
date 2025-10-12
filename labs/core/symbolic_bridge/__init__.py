"""
Symbolic Bridge Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .token_map import TokenMap

    logger.debug("Imported TokenMap from .token_map")
except ImportError as e:
    logger.warning(f"Could not import TokenMap: {e}")
    TokenMap = None

try:
    from .integrator import Integrator

    logger.debug("Imported Integrator from .integrator")
except ImportError as e:
    logger.warning(f"Could not import Integrator: {e}")
    Integrator = None

__all__ = [
    "Integrator",
    "TokenMap",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"symbolic bridge module initialized. Available components: {__all__}")
