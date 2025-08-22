"""
LUKHAS AGI Core Systems
Advanced AGI capabilities for autonomous operation
"""

from .autonomous_learning import (
    AutonomousLearningPipeline,
    KnowledgeType,
    LearningGoal,
    LearningStrategy,
)
from .consciousness_stream import (
    ConsciousnessFrame,
    ConsciousnessStreamClient,
    ConsciousnessStreamServer,
    StreamType,
)
from .self_improvement import (
    AGIGoalAlignment,
    ImprovementDomain,
    ImprovementGoal,
    SelfImprovementEngine,
)

__all__ = [
    # Self-improvement
    "SelfImprovementEngine",
    "AGIGoalAlignment",
    "ImprovementDomain",
    "ImprovementGoal",
    # Consciousness streaming
    "ConsciousnessStreamServer",
    "ConsciousnessStreamClient",
    "ConsciousnessFrame",
    "StreamType",
    # Autonomous learning
    "AutonomousLearningPipeline",
    "LearningStrategy",
    "KnowledgeType",
    "LearningGoal",
]
