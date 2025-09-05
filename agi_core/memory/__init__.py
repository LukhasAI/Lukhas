"""
Enhanced Memory Architecture with Vector Store Integration

Advanced memory system for AGI that integrates with LUKHAS fold-based memory
and dream system for persistent, contextual, and associative memory storage.
"""

from .vector_memory import VectorMemoryStore, MemoryVector, VectorSearchResult
from .memory_consolidation import MemoryConsolidator, ConsolidationStrategy
from .dream_memory import DreamMemoryBridge, DreamMemoryPattern
from .episodic_memory import EpisodicMemorySystem, Episode, EpisodicQuery
from .semantic_memory import SemanticMemoryGraph, SemanticNode, SemanticRelation

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