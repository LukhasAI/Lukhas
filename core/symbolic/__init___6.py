"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony


Symbolic Core Module

Unified symbolic language framework for DAST, ABAS, and NIAS communication.
"""

from .symbolic_language import (
    Symbol,
    SymbolicDomain,
    SymbolicType,
    SymbolicAttribute,
    SymbolicRelation,
    SymbolicExpression,
    SymbolicTranslator,
    SymbolicVocabulary,
    get_symbolic_translator,
    get_symbolic_vocabulary
)

__all__ = [
    "Symbol",
    "SymbolicDomain",
    "SymbolicType",
    "SymbolicAttribute",
    "SymbolicRelation",
    "SymbolicExpression",
    "SymbolicTranslator",
    "SymbolicVocabulary",
    "get_symbolic_translator",
    "get_symbolic_vocabulary"
]

__version__ = "1.0.0"