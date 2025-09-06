"""
Tool Use Framework with Dream-Guided Selection for AGI

Advanced tool selection and usage framework that integrates with LUKHAS
consciousness system for intelligent tool selection based on context,
experience, and dream insights.
"""

from .dream_guided_tools import DreamGuidedToolFramework, ToolInsight, ToolRecommendation
from .tool_learning import ToolExperience, ToolLearningEngine, ToolMastery
from .tool_orchestrator import ExecutionPlan, ToolChain, ToolOrchestrator
from .tool_selector import SelectionCriteria, ToolSelection, ToolSelector

__all__ = [
    "ToolSelector",
    "ToolSelection",
    "SelectionCriteria",
    "DreamGuidedToolFramework",
    "ToolInsight",
    "ToolRecommendation",
    "ToolOrchestrator",
    "ToolChain",
    "ExecutionPlan",
    "ToolLearningEngine",
    "ToolExperience",
    "ToolMastery",
]
