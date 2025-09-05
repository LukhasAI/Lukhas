"""
Multi-Model Orchestration for AGI

Advanced orchestration system for coordinating multiple AI models
including GPT-4, Claude, Gemini, and others for consensus-based
reasoning and optimal model selection.
"""

from .model_router import ModelRouter
from .consensus_engine import ConsensusEngine
from .capability_matrix import CapabilityMatrix
from .cost_optimizer import CostOptimizer

__all__ = [
    "ModelRouter",
    "ConsensusEngine", 
    "CapabilityMatrix",
    "CostOptimizer"
]