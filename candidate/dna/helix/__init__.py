"""
🧬 DNA Helix Memory Module
=========================

Immutable memory architecture with DNA-inspired structure for LUKHAS.
Provides drift detection, controlled repair, and multi-dimensional memory storage.
Implements MATADA cognitive DNA framework for AGI memory.
"""
import streamlit as st

from .dna_healix import (
    DNAHealixCore,  # Data classes; Enums; Core classes
    MemoryHelix,
    RepairMetadata,
    RepairMethod,
    SymbolicRepairLoop,
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
    "CognitiveState",
    "DNAHealixCore",
    "DNAHelixMemory",
    "LinkType",
    "MemoryHelix",
    "MemoryLink",
    "MemoryNode",
    # New MATADA cognitive DNA classes
    "NodeType",
    "RepairMetadata",
    "RepairMethod",
    "SymbolicRepairLoop",
    # Original DNA helix classes
    "SymbolicStrand",
    "get_dna_memory",
]
