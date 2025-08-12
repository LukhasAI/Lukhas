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

from universal_language.compositional import (
    CompositionTemplate,
    SymbolComposer,
    SymbolProgramSynthesizer,
    get_program_synthesizer,
    get_symbol_composer,
)
from universal_language.constitutional import (
    ConstitutionalAPI,
    ConstitutionalGuardrails,
    ConstitutionalValidator,
    SymbolSandbox,
    get_constitutional_api,
)
from universal_language.core import (
    Concept,
    Grammar,
    Symbol,
    UniversalLanguageCore,
    Vocabulary,
)
from universal_language.glyph import GLYPH_MAP, GLYPHEngine, GLYPHToken
from universal_language.grammar import (
    GrammarEngine,
    GrammarValidator,
    LanguageParser,
    SyntaxRule,
)

# AGI-level enhancements
from universal_language.llm_integration import (
    LLMLanguageBridge,
    LLMSymbolAPI,
    SymbolRLHF,
    get_llm_symbol_api,
)
from universal_language.multimodal import (
    ModalityFeatures,
    ModalityType,
    MultiModalProcessor,
)
from universal_language.neuromemory import (
    CorticalNetwork,
    HippocampalBuffer,
    NeuroSymbolicMemory,
    WorkingMemory,
    get_neurosymbolic_memory,
)
from universal_language.privacy import (
    ConceptAnonymizer,
    PrivateSymbolVault,
    SymbolEncryption,
)
from universal_language.translator import (
    ConceptMapper,
    CrossModalTranslator,
    UniversalTranslator,
)
from universal_language.vocabulary import (
    DomainVocabulary,
    UnifiedVocabulary,
    VocabularyManager,
)

__version__ = "2.0.0"  # Upgraded for AGI capabilities
__all__ = [
    # Core
    "UniversalLanguageCore",
    "Symbol",
    "Concept",
    "Grammar",
    "Vocabulary",
    # GLYPH
    "GLYPHEngine",
    "GLYPH_MAP",
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
    "ConceptAnonymizer",
    # AGI Enhancements - LLM Integration
    "LLMLanguageBridge",
    "LLMSymbolAPI",
    "SymbolRLHF",
    "get_llm_symbol_api",
    # AGI Enhancements - Constitutional AI
    "ConstitutionalValidator",
    "ConstitutionalGuardrails",
    "SymbolSandbox",
    "ConstitutionalAPI",
    "get_constitutional_api",
    # AGI Enhancements - Neuroscience Memory
    "NeuroSymbolicMemory",
    "HippocampalBuffer",
    "CorticalNetwork",
    "WorkingMemory",
    "get_neurosymbolic_memory",
    # AGI Enhancements - Compositional & Synthesis
    "SymbolComposer",
    "SymbolProgramSynthesizer",
    "CompositionTemplate",
    "get_symbol_composer",
    "get_program_synthesizer"
]
