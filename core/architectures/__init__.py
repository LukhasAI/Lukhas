"""
LUKHAS Architectures Module
===========================

Consolidated architecture systems:
- DAST: Distributed Adaptive Symbolic Thinking
- ABAS: Adaptive Biological Architecture System
- NIAS: Neural Integration Architecture System

These architectures work together to provide the foundation
for LUKHAS's adaptive and symbolic processing capabilities.
"""

# Import main components from each architecture
from .dast.core.dast_engine import DASTEngine
from .abas.core.abas_engine import ABASEngine
from .nias.core.nias_engine import NIASEngine

__all__ = ["DASTEngine", "ABASEngine", "NIASEngine"]