"""
Dream-Guided Learning System for AGI

Advanced learning system that integrates with LUKHAS dream architecture
for creative learning, pattern discovery, and skill acquisition.
"""

from .dream_guided_learner import DreamGuidedLearner, LearningOutcome, LearningSession
from .meta_learning import LearningStrategy, MetaLearner, MetaLearningInsight
from .pattern_learning import LearningPattern, PatternLearner, PatternType
from .skill_acquisition import Skill, SkillAcquisitionEngine, SkillLevel

__all__ = [
    "DreamGuidedLearner",
    "LearningOutcome",
    "LearningPattern",
    "LearningSession",
    "LearningStrategy",
    "MetaLearner",
    "MetaLearningInsight",
    "PatternLearner",
    "PatternType",
    "Skill",
    "SkillAcquisitionEngine",
    "SkillLevel",
]
