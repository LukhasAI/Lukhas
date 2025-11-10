"""
LUKHAS Consciousness Wrapper Module
====================================

Production-safe wrapper for core consciousness functionality.
All features are gated behind LUKHAS_CONSCIOUSNESS_ENABLED flag (default: OFF).

Usage:
    from lukhas.consciousness import is_enabled, get_consciousness_state

    if is_enabled():
        state = get_consciousness_state()
"""
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Feature flag - default OFF for safety
_CONSCIOUSNESS_ENABLED = (os.getenv("LUKHAS_CONSCIOUSNESS_ENABLED", "0") or "0").strip() == "1"

# Import core modules safely
_CONSCIOUSNESS_AVAILABLE = False
_consciousness_state_manager = None
_consciousness_orchestrator = None

if _CONSCIOUSNESS_ENABLED:
    try:
        from labs.core.consciousness import (
            ConsciousnessState,
            ConsciousnessType,
            EvolutionaryStage,
            MatrizConsciousnessStateManager,
            MatrizConsciousnessOrchestrator,
            consciousness_state_manager,
            consciousness_orchestrator,
            create_consciousness_state,
        )
        _CONSCIOUSNESS_AVAILABLE = True
        _consciousness_state_manager = consciousness_state_manager
        _consciousness_orchestrator = consciousness_orchestrator
        logger.info("Consciousness subsystem initialized successfully")
    except ImportError as e:
        logger.warning(f"Consciousness subsystem unavailable: {e}")
    except Exception as e:
        logger.error(f"Error initializing consciousness subsystem: {e}")


def is_enabled() -> bool:
    """Check if consciousness subsystem is enabled and available."""
    return _CONSCIOUSNESS_ENABLED and _CONSCIOUSNESS_AVAILABLE


def get_consciousness_state(agent_id: str = "default") -> Optional[Any]:
    """
    Get consciousness state for an agent.

    Args:
        agent_id: Agent identifier

    Returns:
        ConsciousnessState if available, None otherwise
    """
    if not is_enabled():
        logger.debug("Consciousness subsystem not enabled")
        return None

    try:
        if _consciousness_state_manager:
            return _consciousness_state_manager.get_state(agent_id)
    except Exception as e:
        logger.error(f"Error getting consciousness state: {e}")
    return None


def create_state(
    agent_id: str,
    consciousness_type: Optional[str] = None,
    metadata: Optional[dict] = None
) -> Optional[Any]:
    """
    Create a new consciousness state.

    Args:
        agent_id: Agent identifier
        consciousness_type: Type of consciousness (e.g., "agent", "collective")
        metadata: Additional metadata

    Returns:
        ConsciousnessState if created successfully, None otherwise
    """
    if not is_enabled():
        logger.debug("Consciousness subsystem not enabled")
        return None

    try:
        if _CONSCIOUSNESS_AVAILABLE:
            from labs.core.consciousness import create_consciousness_state
            return create_consciousness_state(
                agent_id=agent_id,
                consciousness_type=consciousness_type,
                metadata=metadata or {}
            )
    except Exception as e:
        logger.error(f"Error creating consciousness state: {e}")
    return None


def get_orchestrator() -> Optional[Any]:
    """
    Get the consciousness orchestrator instance.

    Returns:
        MatrizConsciousnessOrchestrator if available, None otherwise
    """
    if not is_enabled():
        logger.debug("Consciousness subsystem not enabled")
        return None
    return _consciousness_orchestrator


def get_network_metrics() -> dict[str, Any]:
    """
    Get consciousness network metrics.

    Returns:
        Dictionary of metrics, or empty dict if unavailable
    """
    if not is_enabled():
        return {"enabled": False, "reason": "Consciousness subsystem not enabled"}

    try:
        if _consciousness_orchestrator:
            return _consciousness_orchestrator.get_metrics()
    except Exception as e:
        logger.error(f"Error getting network metrics: {e}")

    return {"enabled": True, "error": "Metrics unavailable"}


# Public API
__all__ = [
    "is_enabled",
    "get_consciousness_state",
    "create_state",
    "get_orchestrator",
    "get_network_metrics",
]
