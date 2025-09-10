"""
Unified Module
Auto-generated module initialization file
"""
import logging

import streamlit as st

logger = logging.getLogger(__name__)

try:
    from .bio_signals import BioSignals

    logger.debug("Imported BioSignals from .bio_signals")
except ImportError as e:
    logger.warning(f"Could not import BioSignals: {e}")
    BioSignals = None

try:
    from .integration import Integration

    logger.debug("Imported Integration from .integration")
except ImportError as e:
    logger.warning(f"Could not import Integration: {e}")
    Integration = None

try:
    from .orchestration import Orchestration

    logger.debug("Imported Orchestration from .orchestration")
except ImportError as e:
    logger.warning(f"Could not import Orchestration: {e}")
    Orchestration = None

__all__ = [
    "BioSignals",
    "Integration",
    "Orchestration",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"unified module initialized. Available components: {__all__}")
