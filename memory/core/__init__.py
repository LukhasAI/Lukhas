"""
Memory Core Module

Unified memory orchestration system for LUKHAS AI, providing:
- Multi-tier memory architecture (working, episodic, semantic, fold)
- Automatic consolidation between tiers
- Semantic search and retrieval
- Memory fold compression for long-term storage
"""

from .unified_memory_orchestrator import (
    ConsolidationResult,
    FoldEngine,
    Memory,
    MemoryType,
    UnifiedMemoryOrchestrator,
    WorkingMemory,
)

__all__ = [
    "UnifiedMemoryOrchestrator",
    "MemoryType",
    "Memory",
    "ConsolidationResult",
    "WorkingMemory",
    "FoldEngine",
]

__version__ = "1.0.0"
