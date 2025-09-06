"""
Enhanced Memory Architecture with Vector Store Integration

Advanced memory system for AGI that integrates with LUKHAS fold-based memory
and dream system for persistent, contextual, and associative memory storage.
"""

from .dream_memory import DreamMemoryBridge, DreamMemoryPattern
from .episodic_memory import Episode, EpisodicMemorySystem, EpisodicQuery
from .memory_consolidation import ConsolidationStrategy, MemoryConsolidator
from .semantic_memory import SemanticMemoryGraph, SemanticNode, SemanticRelation
from .vector_memory import MemoryVector, VectorMemoryStore, VectorSearchResult

__all__ = [
    "VectorMemoryStore",
    "MemoryVector",
    "VectorSearchResult",
    "MemoryConsolidator",
    "ConsolidationStrategy",
    "DreamMemoryBridge",
    "DreamMemoryPattern",
    "EpisodicMemorySystem",
    "Episode",
    "EpisodicQuery",
    "SemanticMemoryGraph",
    "SemanticNode",
    "SemanticRelation"
]
