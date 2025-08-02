"""
LUKHAS Learning & Knowledge Capture System
Your AI-powered technical mentor and memory
"""

from .journal_engine import JournalEngine
from .decision_tracker import DecisionTracker
from .insight_analyzer import InsightAnalyzer
from .pattern_detector import PatternDetector
from .learning_assistant import LearningAssistant

__version__ = "1.0.0"
__author__ = "LUKHAS Learning System"

__all__ = [
    "JournalEngine",
    "DecisionTracker", 
    "InsightAnalyzer",
    "PatternDetector",
    "LearningAssistant"
]