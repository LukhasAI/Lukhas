"""
LUKHAS Reinforcement Learning Framework
=====================================

Consciousness-aware reinforcement learning for distributed AGI systems.

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian

This module implements RL specifically designed for consciousness architecture,
enabling 692 distributed modules to learn, coordinate, and evolve together.
"""
import streamlit as st

from .coordination.multi_agent_trainer import MultiAgentConsciousnessTrainer
from .engine.actor_critic import ConsciousnessActorCritic
from .engine.consciousness_environment import ConsciousnessEnvironment
from .engine.policy_networks import ConsciousnessPolicy, ConsciousnessValueNetwork
from .experience.consciousness_buffer import ConsciousnessReplayBuffer

__version__ = "0.1.0"
__all__ = [
    "ConsciousnessActorCritic",
    "ConsciousnessEnvironment",
    "ConsciousnessPolicy",
    "ConsciousnessReplayBuffer",
    "ConsciousnessValueNetwork",
    "MultiAgentConsciousnessTrainer",
]

# RL Framework metadata for consciousness integration
RL_METADATA = {
    "framework": "LUKHAS-RL",
    "consciousness_aware": True,
    "multi_agent": True,
    "ethical_constraints": True,
    "temporal_coherence": True,
    "reflection_enabled": True,
    "trinity_compliant": True,
}
