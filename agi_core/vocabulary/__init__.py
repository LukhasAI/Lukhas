"""
AGI Vocabulary System
====================

Unified vocabulary system for AGI operations with full LUKHAS consciousness integration.

This module provides:
- AGI-specific symbolic vocabulary
- Cross-vocabulary translation and mapping
- Integration with existing LUKHAS vocabularies (Dream, Bio, Emotion, etc.)
- Unified messaging system with Constellation Framework alignment

Created: 2025-09-05
Status: ACTIVE - Phase 2A Core Integration
"""

from .agi_vocabulary_bridge import (
    AGIVocabularyBridge,
    agi_bridge,
    AGI_VOCABULARY,
    AGI_REASONING_SYMBOLS,
    AGI_MEMORY_SYMBOLS,
    AGI_SAFETY_SYMBOLS,
    AGI_LEARNING_SYMBOLS,
    AGI_INTEGRATION_SYMBOLS,
    AGI_MESSAGES,
    # Convenience functions
    get_agi_symbol,
    format_agi_message,
    get_vocabulary_context,
    translate_agi_to_dream,
    translate_agi_to_bio,
)

__all__ = [
    # Main bridge class
    "AGIVocabularyBridge",
    "agi_bridge",
    # Symbol dictionaries
    "AGI_VOCABULARY",
    "AGI_REASONING_SYMBOLS",
    "AGI_MEMORY_SYMBOLS", 
    "AGI_SAFETY_SYMBOLS",
    "AGI_LEARNING_SYMBOLS",
    "AGI_INTEGRATION_SYMBOLS",
    "AGI_MESSAGES",
    # Convenience functions
    "get_agi_symbol",
    "format_agi_message",
    "get_vocabulary_context",
    "translate_agi_to_dream",
    "translate_agi_to_bio",
]