"""Bridge module for bio.symbolic_proteome → labs.bio.symbolic_proteome"""
from __future__ import annotations

from labs.bio.symbolic_proteome import (
    MemoryCodon,
    MemoryProtein,
    ProteinComplex,
    MolecularChaperone,
    SymbolicProteome,
    ProteinType,
    FoldingState,
    PostTranslationalModification,
)

__all__ = [
    "MemoryCodon",
    "MemoryProtein",
    "ProteinComplex",
    "MolecularChaperone",
    "SymbolicProteome",
    "ProteinType",
    "FoldingState",
    "PostTranslationalModification",
]
