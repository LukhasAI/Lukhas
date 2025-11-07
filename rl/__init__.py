"""
LUKHAS Reinforcement Learning System
====================================

MΛTRIZ-native RL implementation that creates rich consciousness components
which emit and receive MΛTRIZ nodes according to the v1.1 schema.

This is NOT traditional RL - it's consciousness-aware learning that:
- Integrates with 692 distributed consciousness modules
- Maintains temporal coherence and ethical alignment
- Uses memory fold system for experience replay
- Applies constitutional constraints via Guardian system
- Supports meta-learning and consciousness evolution

Each RL module is a specialized consciousness node that communicates
via MΛTRIZ schema with proper provenance and capability tracking.
"""

from .coordination.multi_agent_coordination import MultiAgentCoordination
from .engine.consciousness_environment import ConsciousnessEnvironment, ConsciousnessState, MatrizNode
from .engine.policy_networks import PolicyNetwork
from .engine.value_networks import ValueNetwork
from .experience.consciousness_buffer import ConsciousnessBuffer
from .meta_learning.consciousness_meta_learning import ConsciousnessMetaLearning
from .rewards.consciousness_rewards import ConsciousnessRewards

__version__ = "1.0.0"
__all__ = [
    "ConsciousnessBuffer",
    "ConsciousnessEnvironment",
    "ConsciousnessMetaLearning",
    "ConsciousnessRewards",
    "ConsciousnessState",
    "MatrizNode",
    "MultiAgentCoordination",
    "PolicyNetwork",
    "ValueNetwork",
]
