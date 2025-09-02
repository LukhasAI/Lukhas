"""
LUKHAS RL Environments
=====================

Gym-compatible environments for consciousness training.
"""

from .consciousness_environment import (
    ConsciousnessEnvironment,
    ConsciousnessState,
    ConsciousnessAction, 
    ConsciousnessActionType
)

__all__ = [
    "ConsciousnessEnvironment",
    "ConsciousnessState",
    "ConsciousnessAction",
    "ConsciousnessActionType"
]
