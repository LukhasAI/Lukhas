"""
🧬 DNA Helix Memory Module
=========================

Immutable memory architecture with DNA-inspired structure for LUKHAS.
Provides drift detection, controlled repair, and multi-dimensional memory storage.
Implements MATADA cognitive DNA framework for AGI memory.
"""

from .dna_healix import (
    DNAHealixCore,
    MemoryHelix,
    # Data classes
    RepairMetadata,
    # Enums
    RepairMethod,
    SymbolicRepairLoop,
    # Core classes
    SymbolicStrand,
)
from .dna_memory_architecture import (
    CognitiveState,
    DNAHelixMemory,
    LinkType,
    MemoryLink,
    MemoryNode,
    NodeType,
    get_dna_memory,
)

# Version
__version__ = "2.0.0"

# Module metadata
__author__ = "LUKHAS AGI Framework"
__description__ = "DNA-inspired immutable memory architecture with MATADA cognitive framework"

__all__ = [
    # Original DNA helix classes
    "SymbolicStrand",
    "DNAHealixCore",
    "SymbolicRepairLoop",
    "MemoryHelix",
    "RepairMethod",
    "RepairMetadata",
    # New MATADA cognitive DNA classes
    "NodeType",
    "LinkType",
    "CognitiveState",
    "MemoryLink",
    "MemoryNode",
    "DNAHelixMemory",
    "get_dna_memory",
]
