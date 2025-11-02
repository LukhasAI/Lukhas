"""
Bio-Inspired Memory Systems
==========================

Bio-inspired memory processing including symbolic proteome functionality.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .symbolic_proteome import MemoryProtein, SymbolicProteome

    logger.info("Successfully imported SymbolicProteome")
    __all__ = ["SymbolicProteome", "MemoryProtein"]
except ImportError as e:
    logger.warning(f"Could not import symbolic proteome: {e}")
    __all__ = []

logger.info(f"bio.memory module initialized. Available components: {__all__}")
