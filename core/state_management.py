"""Bridge module for core.state_management → labs.core.state_management"""
from __future__ import annotations

from labs.core.state_management import StateHandler, StateManager, create_state_manager

__all__ = ["StateHandler", "StateManager", "create_state_manager"]
