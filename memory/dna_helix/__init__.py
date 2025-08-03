"""
🧬 DNA Helix Memory Module
=========================

Immutable memory architecture with DNA-inspired structure for LUKHAS.
Provides drift detection, controlled repair, and multi-dimensional memory storage.
"""

from .dna_healix import (
    # Core classes
    SymbolicStrand,
    DNAHealixCore,
    SymbolicRepairLoop,
    MemoryHelix,
    
    # Enums
    RepairMethod,
    
    # Data classes
    RepairMetadata,
)

# Version
__version__ = "1.0.0"

# Module metadata
__author__ = "LUKHAS AGI Framework"
__description__ = "DNA-inspired immutable memory architecture"

__all__ = [
    'SymbolicStrand',
    'DNAHealixCore', 
    'SymbolicRepairLoop',
    'MemoryHelix',
    'RepairMethod',
    'RepairMetadata',
]