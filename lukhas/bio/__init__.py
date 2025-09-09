"""
LUKHAS AI Bio Module
Biological-inspired processing and utilities
Trinity Framework: ⚛️🧠🛡️
"""
import streamlit as st

# Import utilities
# Import core bio-symbolic components
from .core import (
    BioSymbolic,
    BioSymbolicOrchestrator,
    SymbolicGlyph,
    symbolic_bio_symbolic,
    symbolic_bio_symbolic_orchestrator,
)
from .utilities import BioUtilities, apply_evolution, calculate_bio_energy

# Module info
__version__ = "2.0.0"
__module_name__ = "bio"
__description__ = "Biological-inspired processing for LUKHAS AI"

# Export public interface
__all__ = [
    "BioSymbolic",
    "BioSymbolicOrchestrator",
    "BioUtilities",
    "SymbolicGlyph",
    "apply_evolution",
    "calculate_bio_energy",
    "symbolic_bio_symbolic",
    "symbolic_bio_symbolic_orchestrator",
]