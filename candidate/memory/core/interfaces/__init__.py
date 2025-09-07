"""
Memory Interface Definitions
Standard interfaces for all memory types with colony compatibility
"""
import streamlit as st

from .episodic_interface import (
    EpisodicContext,
    EpisodicMemoryContent,
    EpisodicMemoryInterface,
)
from .memory_interface import (
    BaseMemoryInterface,
    MemoryInterfaceRegistry,
    MemoryMetadata,
    MemoryOperation,
    MemoryResponse,
    MemoryState,
    MemoryType,
    ValidationResult,
    memory_registry,
)
from .semantic_interface import (
    ConceptNode,
    SemanticMemoryContent,
    SemanticMemoryInterface,
    SemanticRelation,
    SemanticRelationType,
)

__all__ = [
    # Base interfaces
    "BaseMemoryInterface",
    "MemoryType",
    "MemoryState",
    "MemoryMetadata",
    "MemoryOperation",
    "MemoryResponse",
    "ValidationResult",
    "MemoryInterfaceRegistry",
    "memory_registry",
    # Episodic interface
    "EpisodicMemoryInterface",
    "EpisodicContext",
    "EpisodicMemoryContent",
    # Semantic interface
    "SemanticMemoryInterface",
    "SemanticRelationType",
    "SemanticRelation",
    "ConceptNode",
    "SemanticMemoryContent",
]
