"""
Bio Core Module
Exposes the BioEngine class for bio-inspired processing
"""

import logging

logger = logging.getLogger(__name__)

# Import the BioEngine class and make it available
# The core.py file is in the parent bio directory
try:
    from ..core import BioEngine

    __all__ = ["BioEngine"]
except ImportError as e:
    logger.warning(f"Could not import BioEngine: {e}")
    __all__ = []

logger.info(f"bio core module initialized. Available components: {__all__}")
