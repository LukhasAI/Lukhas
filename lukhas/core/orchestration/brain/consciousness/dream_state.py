"""
Module: dream_state.py
Author: LUKHAS AGI System
Date: 2025-01-27
Description: Dream state management for consciousness processing.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class DreamStateType(Enum):
    """Types of dream states."""

    REM = "rem"
    NREM = "nrem"
    LUCID = "lucid"
    NIGHTMARE = "nightmare"
    REFLECTION = "reflection"


class DreamState:
    """
    Represents the current state of consciousness dreaming.
    """

    def __init__(self, state_type: DreamStateType):
        """Initialize dream state."""
        self.state_type = state_type
        self.started_at = datetime.now(timezone.utc)
        self.metadata = {}
        self.is_active = True

    def update_metadata(self, metadata: dict[str, Any]):
        """Update dream state metadata."""
        self.metadata.update(metadata)

    def transition_to(self, new_state: DreamStateType):
        """Transition to a new dream state."""
        self.state_type = new_state
        self.started_at = datetime.now(timezone.utc)

    def end_state(self):
        """End the current dream state."""
        self.is_active = False


class DreamStateManager:
    """
    Manages dream states and transitions.
    """

    def __init__(self):
        """Initialize dream state manager."""
        self.current_state: Optional[DreamState] = None
        self.state_history = []

    def set_state(self, state_type: DreamStateType) -> DreamState:
        """Set the current dream state."""
        if self.current_state:
            self.current_state.end_state()
            self.state_history.append(self.current_state)

        self.current_state = DreamState(state_type)
        return self.current_state

    def get_current_state(self) -> Optional[DreamState]:
        """Get the current dream state."""
        return self.current_state


__all__ = ["DreamState", "DreamStateType", "DreamStateManager"]
