"""
Core Safety Module
Comprehensive AI safety system with multiple protection layers
"""

import logging

import streamlit as st

logger = logging.getLogger(__name__)

try:
    from .ai_safety_orchestrator import AISafetyOrchestrator

    logger.debug("Imported AISafetyOrchestrator from .ai_safety_orchestrator")
except ImportError as e:
    logger.warning(f"Could not import AISafetyOrchestrator: {e}")
    AISafetyOrchestrator = None

try:
    from .constitutional_safety import ConstitutionalSafety

    logger.debug("Imported ConstitutionalSafety from .constitutional_safety")
except ImportError as e:
    logger.warning(f"Could not import ConstitutionalSafety: {e}")
    ConstitutionalSafety = None

try:
    from .adversarial_testing import AdversarialTesting

    logger.debug("Imported AdversarialTesting from .adversarial_testing")
except ImportError as e:
    logger.warning(f"Could not import AdversarialTesting: {e}")
    AdversarialTesting = None

try:
    from .predictive_harm_prevention import PredictiveHarmPrevention

    logger.debug("Imported PredictiveHarmPrevention from .predictive_harm_prevention")
except ImportError as e:
    logger.warning(f"Could not import PredictiveHarmPrevention: {e}")
    PredictiveHarmPrevention = None

try:
    from .multi_agent_consensus import MultiAgentConsensus

    logger.debug("Imported MultiAgentConsensus from .multi_agent_consensus")
except ImportError as e:
    logger.warning(f"Could not import MultiAgentConsensus: {e}")
    MultiAgentConsensus = None

__all__ = [
    "AISafetyOrchestrator",
    "AdversarialTesting",
    "ConstitutionalSafety",
    "MultiAgentConsensus",
    "PredictiveHarmPrevention",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"Core safety module initialized. Available components: {__all__}")
