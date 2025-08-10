"""
Universal Language Module for LUKHAS PWM
=========================================

A unified, standalone language system that consolidates all symbolic,
grammatical, and multi-modal communication capabilities.

This module replaces and unifies:
- /symbolic/ - Multi-modal language and entropy passwords
- /core/symbolic/ - Core GLYPH processing
- /bio_symbolic/ - Biological symbolic integration
- LUKHAS Grammar - Syntax and grammar rules
- Universal Language - Private symbolic language

Author: LUKHAS AI Systems
Version: 1.0.0
License: Proprietary
"""

from universal_language.core import (
    UniversalLanguageCore,
    Symbol,
    Concept,
    Grammar,
    Vocabulary
)

from universal_language.glyph import (
    GLYPHEngine,
    GLYPHMap,
    GLYPHToken
)

from universal_language.grammar import (
    GrammarEngine,
    SyntaxRule,
    GrammarValidator,
    LanguageParser
)

from universal_language.vocabulary import (
    UnifiedVocabulary,
    VocabularyManager,
    DomainVocabulary
)

from universal_language.translator import (
    UniversalTranslator,
    ConceptMapper,
    CrossModalTranslator
)

from universal_language.multimodal import (
    MultiModalProcessor,
    ModalityType,
    ModalityFeatures
)

from universal_language.privacy import (
    PrivateSymbolVault,
    SymbolEncryption,
    ConceptAnonymizer
)

__version__ = "1.0.0"
__all__ = [
    # Core
    "UniversalLanguageCore",
    "Symbol",
    "Concept",
    "Grammar",
    "Vocabulary",
    # GLYPH
    "GLYPHEngine",
    "GLYPHMap",
    "GLYPHToken",
    # Grammar
    "GrammarEngine",
    "SyntaxRule",
    "GrammarValidator",
    "LanguageParser",
    # Vocabulary
    "UnifiedVocabulary",
    "VocabularyManager",
    "DomainVocabulary",
    # Translator
    "UniversalTranslator",
    "ConceptMapper",
    "CrossModalTranslator",
    # Multimodal
    "MultiModalProcessor",
    "ModalityType",
    "ModalityFeatures",
    # Privacy
    "PrivateSymbolVault",
    "SymbolEncryption",
    "ConceptAnonymizer"
]