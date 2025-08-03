"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony


LUKHAS Symbolic Vocabularies
============================

🌟 VALUABLE ASSET - DO NOT DELETE 🌟

This module contains the symbolic vocabulary system for LUKHAS AGI.
Each vocabulary provides consistent emoji/symbol mappings for human-readable
state representation and cross-module communication.

Created: 2025-07-25
Status: ACTIVE
Priority: HIGH
"""

# Import existing vocabularies
try:
    from .bio_vocabulary import BIO_SYMBOLS, EMOTION_SYMBOLS, DEVICE_SYMBOLS
except ImportError:
    BIO_SYMBOLS = {}
    EMOTION_SYMBOLS = {}
    DEVICE_SYMBOLS = {}

try:
    from .dream_vocabulary import (
        DREAM_PHASE_SYMBOLS,
        DREAM_TYPE_SYMBOLS,
        DREAM_STATE_SYMBOLS,
        PATTERN_SYMBOLS,
        MEMORY_SYMBOLS
    )
except ImportError:
    DREAM_PHASE_SYMBOLS = {}
    DREAM_TYPE_SYMBOLS = {}
    DREAM_STATE_SYMBOLS = {}
    PATTERN_SYMBOLS = {}
    MEMORY_SYMBOLS = {}

try:
    from .identity_vocabulary import IDENTITY_SYMBOLIC_VOCABULARY
except ImportError:
    IDENTITY_SYMBOLIC_VOCABULARY = {}

try:
    from .voice_vocabulary # import VOICE  # External dependency_SYMBOLIC_VOCABULARY
except ImportError:
    VOICE_SYMBOLIC_VOCABULARY = {}

try:
    from .vision_vocabulary import VISION_SYMBOLIC_VOCABULARY
except ImportError:
    VISION_SYMBOLIC_VOCABULARY = {}

# Convenience function to get any symbol
def get_symbol(vocabulary_name: str, key: str, default: str = "❓") -> str:
    """
    Get a symbol from any vocabulary.
    
    Args:
        vocabulary_name: Name of the vocabulary (e.g., 'bio', 'dream')
        key: Key within the vocabulary
        default: Default symbol if not found
        
    Returns:
        The emoji symbol or default
    """
    vocabularies = {
        'bio': BIO_SYMBOLS,
        'emotion': EMOTION_SYMBOLS,
        'device': DEVICE_SYMBOLS,
        'dream_phase': DREAM_PHASE_SYMBOLS,
        'dream_type': DREAM_TYPE_SYMBOLS,
        'dream_state': DREAM_STATE_SYMBOLS,
        'pattern': PATTERN_SYMBOLS,
        'memory': MEMORY_SYMBOLS,
        'identity': IDENTITY_SYMBOLIC_VOCABULARY,
        'voice': VOICE_SYMBOLIC_VOCABULARY,
        'vision': VISION_SYMBOLIC_VOCABULARY
    }
    
    vocab = vocabularies.get(vocabulary_name, {})
    if isinstance(vocab, dict) and key in vocab:
        entry = vocab[key]
        if isinstance(entry, dict) and 'emoji' in entry:
            return entry['emoji']
        elif isinstance(entry, str):
            return entry
    return default

# Export all symbols
__all__ = [
    # Bio module
    'BIO_SYMBOLS',
    'EMOTION_SYMBOLS',
    'DEVICE_SYMBOLS',
    # Dream module
    'DREAM_PHASE_SYMBOLS',
    'DREAM_TYPE_SYMBOLS',
    'DREAM_STATE_SYMBOLS',
    'PATTERN_SYMBOLS',
    'MEMORY_SYMBOLS',
    # Identity module
    'IDENTITY_SYMBOLIC_VOCABULARY',
    # Voice module
    'VOICE_SYMBOLIC_VOCABULARY',
    # Vision module
    'VISION_SYMBOLIC_VOCABULARY',
    # Helper function
    'get_symbol'
]