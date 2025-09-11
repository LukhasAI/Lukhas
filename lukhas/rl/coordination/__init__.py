"""
LUKHAS RL Coordination Systems
=============================

Multi-agent coordination and training systems for consciousness modules.
"""

import streamlit as st

from .multi_agent_trainer import ConsciousnessModuleAgent, MultiAgentConsciousnessTrainer, TrainingConfiguration

__all__ = ["ConsciousnessModuleAgent", "MultiAgentConsciousnessTrainer", "TrainingConfiguration"]
