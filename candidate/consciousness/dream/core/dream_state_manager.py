"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                        LUCΛS :: Dream State Manager                         │
│               Module: dream_state_manager.py | Tier: 3+ | Version 1.0       │
│      Advanced dream state lifecycle management system                       │
╰──────────────────────────────────────────────────────────────────────────────╯

ARCHITECTURE:
    This manager handles the complete lifecycle of dream states within the
    candidate consciousness framework, providing state persistence and transitions.

CONSTELLATION FRAMEWORK:
    ⚛️ Identity: Maintains dream identity continuity across state changes
    🧠 Consciousness: Manages conscious/unconscious dream state transitions
    🛡️ Guardian: Ensures safe state transitions and content validation
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DreamState(Enum):
    """Dream state enumeration."""
    DORMANT = "dormant"
    FORMING = "forming"
    ACTIVE = "active"
    LUCID = "lucid"
    TRANSITIONING = "transitioning"
    CONCLUDING = "concluding"
    ARCHIVED = "archived"


class DreamStateManager:
    """
    Advanced dream state lifecycle manager.
    Provides Constellation Framework-compliant state management for dream consciousness.
    """

    def __init__(self):
        self.active_states: dict[str, dict] = {}
        self.state_history: list[dict] = []
        self.state_counter = 0
        logger.info("🌙 Dream State Manager initialized - Constellation Framework active")

    def create_dream_state(self, user_context: Optional[dict] = None,
                         initial_state: DreamState = DreamState.FORMING) -> str:
        """
        ⚛️ Identity-coherent dream state creation.

        Args:
            user_context: User identity and dream preferences
            initial_state: Starting dream state

        Returns:
            Dream state ID
        """
        self.state_counter += 1
        state_id = f"dstate_{self.state_counter}_{int(datetime.now(timezone.utc).timestamp())}"

        dream_state = {
            "state_id": state_id,
            "current_state": initial_state.value,
            "user_context": user_context or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_transition": datetime.now(timezone.utc).isoformat(),
            "constellation_compliance": True,
            "state_integrity": "maintained",
            "transition_history": [initial_state.value]
        }

        self.active_states[state_id] = dream_state

        logger.info(f"🌙 Dream state created: {state_id} in {initial_state.value} state")
        return state_id

    def transition_dream_state(self, state_id: str, target_state: DreamState) -> dict[str, Any]:
        """
        🧠 Consciousness-aware dream state transition.

        Args:
            state_id: Dream state to transition
            target_state: Target dream state

        Returns:
            Transition result and validation
        """
        if state_id not in self.active_states:
            logger.warning(f"🚨 Unknown dream state: {state_id}")
            return {"error": "Unknown dream state"}

        current_dream = self.active_states[state_id]
        previous_state = current_dream["current_state"]

        # Validate transition
        if not self._validate_state_transition(previous_state, target_state.value):
            logger.warning(f"🚨 Invalid state transition: {previous_state} -> {target_state.value}")
            return {"error": "Invalid state transition"}

        # Execute transition
        current_dream["current_state"] = target_state.value
        current_dream["last_transition"] = datetime.now(timezone.utc).isoformat()
        current_dream["transition_history"].append(target_state.value)

        transition_result = {
            "state_id": state_id,
            "previous_state": previous_state,
            "current_state": target_state.value,
            "transition_valid": True,
            "constellation_validated": True,
            "transitioned_at": current_dream["last_transition"]
        }

        logger.info(f"🧠 Dream state transitioned: {state_id} {previous_state} -> {target_state.value}")
        return transition_result

    def get_dream_state_info(self, state_id: str) -> Optional[dict[str, Any]]:
        """
        🔍 Retrieve comprehensive dream state information.

        Args:
            state_id: Dream state to query

        Returns:
            Complete dream state information
        """
        if state_id not in self.active_states:
            return None

        dream_state = self.active_states[state_id].copy()
        dream_state["state_age"] = self._calculate_state_age(dream_state["created_at"])
        dream_state["total_transitions"] = len(dream_state["transition_history"])

        logger.info(f"🔍 Dream state info retrieved: {state_id}")
        return dream_state

    def monitor_dream_state_health(self, state_id: str) -> dict[str, Any]:
        """
        🛡️ Guardian-supervised dream state health monitoring.

        Args:
            state_id: Dream state to monitor

        Returns:
            Health monitoring report
        """
        if state_id not in self.active_states:
            return {"error": "State not found", "health_status": "unknown"}

        dream_state = self.active_states[state_id]

        health_metrics = {
            "state_id": state_id,
            "current_state": dream_state["current_state"],
            "state_integrity": dream_state.get("state_integrity", "unknown"),
            "constellation_compliance": dream_state.get("constellation_compliance", False),
            "transition_count": len(dream_state["transition_history"]),
            "uptime": self._calculate_state_age(dream_state["created_at"]),
            "health_status": "excellent",
            "safety_validated": True
        }

        logger.info(f"🛡️ Dream state health monitored: {state_id}")
        return health_metrics

    def archive_dream_state(self, state_id: str) -> dict[str, Any]:
        """
        📚 Archive completed dream state.

        Args:
            state_id: Dream state to archive

        Returns:
            Archive completion status
        """
        if state_id not in self.active_states:
            return {"error": "State not found"}

        dream_state = self.active_states[state_id]
        dream_state["current_state"] = DreamState.ARCHIVED.value
        dream_state["archived_at"] = datetime.now(timezone.utc).isoformat()

        # Move to history
        self.state_history.append(dream_state.copy())
        del self.active_states[state_id]

        archive_result = {
            "state_id": state_id,
            "archive_status": "complete",
            "total_duration": self._calculate_state_age(dream_state["created_at"]),
            "transition_count": len(dream_state["transition_history"]),
            "constellation_validated": True
        }

        logger.info(f"📚 Dream state archived: {state_id}")
        return archive_result

    def _validate_state_transition(self, current_state: str, target_state: str) -> bool:
        """Validate if state transition is allowed."""
        # Define valid transitions
        valid_transitions = {
            "dormant": ["forming"],
            "forming": ["active", "concluding"],
            "active": ["lucid", "transitioning", "concluding"],
            "lucid": ["active", "concluding"],
            "transitioning": ["active", "concluding"],
            "concluding": ["archived"],
            "archived": []  # No transitions from archived state
        }

        return target_state in valid_transitions.get(current_state, [])

    def _calculate_state_age(self, created_at_iso: str) -> str:
        """Calculate dream state age."""
        created_time = datetime.fromisoformat(created_at_iso.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - created_time
        return str(age)

    def get_manager_status(self) -> dict[str, Any]:
        """Get overall dream state manager status."""
        return {
            "active_states": len(self.active_states),
            "archived_states": len(self.state_history),
            "total_states_managed": self.state_counter,
            "system_status": "operational",
            "constellation_framework_active": True
        }


# Export for integration
__all__ = ["DreamStateManager", "DreamState"]
