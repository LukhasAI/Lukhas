"""
Dream-Guided Learning System for AGI

Advanced learning system that integrates with LUKHAS dream architecture
for creative learning, pattern discovery, and skill acquisition.
"""

from .dream_guided_learner import DreamGuidedLearner, LearningSession, LearningOutcome
from .pattern_learning import PatternLearner, LearningPattern, PatternType
from .skill_acquisition import SkillAcquisitionEngine, Skill, SkillLevel
from .meta_learning import MetaLearner, LearningStrategy, MetaLearningInsight

__all__ = [
    "DreamGuidedLearner",
    "LearningSession", 
    "LearningOutcome",
    "PatternLearner",
    "LearningPattern",
    "PatternType",
    "SkillAcquisitionEngine",
    "Skill",
    "SkillLevel",
    "MetaLearner",
    "LearningStrategy",
    "MetaLearningInsight"
]