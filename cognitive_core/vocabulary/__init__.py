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
    AGI_INTEGRATION_SYMBOLS,
    AGI_LEARNING_SYMBOLS,
    AGI_MEMORY_SYMBOLS,
    AGI_MESSAGES,
    AGI_REASONING_SYMBOLS,
    AGI_SAFETY_SYMBOLS,
    AGI_VOCABULARY,
    AGIVocabularyBridge,
    agi_bridge,
    format_agi_message,
    # Convenience functions
    get_agi_symbol,
    get_vocabulary_context,
    translate_agi_to_bio,
    translate_agi_to_dream,
)

__all__ = [
    "AGI_INTEGRATION_SYMBOLS",
    "AGI_LEARNING_SYMBOLS",
    "AGI_MEMORY_SYMBOLS",
    "AGI_MESSAGES",
    "AGI_REASONING_SYMBOLS",
    "AGI_SAFETY_SYMBOLS",
    # Symbol dictionaries
    "AGI_VOCABULARY",
    # Main bridge class
    "AGIVocabularyBridge",
    "agi_bridge",
    "format_agi_message",
    # Convenience functions
    "get_agi_symbol",
    "get_vocabulary_context",
    "translate_agi_to_bio",
    "translate_agi_to_dream",
]
