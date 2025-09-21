"""
Multi-Model Orchestration for Cognitive AI

Advanced orchestration system for coordinating multiple AI models
including GPT-4, Claude, Gemini, and others for consensus-based
reasoning and optimal model selection.
"""

from .capability_matrix import CapabilityMatrix
from .consensus_engine import ConsensusEngine
from .cost_optimizer import CostOptimizer
from .model_router import ModelRouter

__all__ = ["CapabilityMatrix", "ConsensusEngine", "CostOptimizer", "ModelRouter"]
