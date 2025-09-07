"""
Core Orchestration Module
Exposes the OrchestrationCore class for system coordination
"""
import logging

import streamlit as st

logger = logging.getLogger(__name__)

# Import the OrchestrationCore class and make it available
# The core.py file is in the parent orchestration directory
try:
    from candidate.core.orchestration.core import OrchestrationCore

    __all__ = ["OrchestrationCore"]
except ImportError as e:
    logger.warning(f"Could not import OrchestrationCore: {e}")
    __all__ = []

logger.info(f"core module initialized. Available components: {__all__}")
