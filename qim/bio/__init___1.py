"""

#TAG:qim
#TAG:bio
#TAG:neuroplastic
#TAG:colony


Memory Evolution Module for DocuTutor.
Combines version control, knowledge adaptation, and usage-based learning.
"""

# from memory.core_memory.memory_evolution import MemoryEvolution  # Removed circular import
from .version_control import DocumentVersionControl
from .knowledge_adaptation import KnowledgeAdaptation, KnowledgeGraph
from .usage_learning import UsageBasedLearning, UserInteraction

__all__ = [
    'MemoryEvolution',
    'DocumentVersionControl',
    'KnowledgeAdaptation',
    'KnowledgeGraph',
    'UsageBasedLearning',
    'UserInteraction'
]
