# Universal Language Module

## Overview

The Universal Language module is a **unified, standalone language system** that consolidates all symbolic, grammatical, and multi-modal communication capabilities in LUKHAS. This module replaces and unifies the previously fragmented implementations scattered across `/symbolic/`, `/core/symbolic/`, `/bio_symbolic/`, and other directories.

## Key Features

### 🌐 Unified Language Core
- Single source of truth for all language operations
- Centralized symbol and concept management
- Domain-specific vocabularies (emotion, bio, dream, identity, vision, voice, etc.)
- Consistent cross-module communication

### 🔤 GLYPH System
- Visual symbolic representation using emojis and unicode
- 100+ pre-defined GLYPH mappings
- Entropy calculation for security applications
- Custom GLYPH registration

### 📝 Grammar Engine
- Syntax rules and validation
- Grammatical role detection
- Pattern-based parsing
- Auto-correction capabilities
- Support for multiple syntax types (statement, question, command, conditional)

### 📚 Unified Vocabulary
- Domain-specific vocabularies for all symbolic domains
- Symbol-to-concept mapping
- Alias support for flexible lookup
- Relationship tracking between symbols

### 🔄 Universal Translator
- Cross-modal translation (text ↔ GLYPH ↔ symbol ↔ concept)
- Cross-domain translation
- Private-to-universal concept translation
- Universal-to-private personalized rendering

### 🎨 Multimodal Processing
- Support for multiple input modalities:
  - Text, Emoji, Image, Sound, Gesture
  - Color, Pattern, Rhythm, Stroke
- Entropy-based security features
- Modality combination and analysis

### 🔒 Privacy-Preserving System
- Device-local private symbol vault
- End-to-end encryption
- Anonymous concept transmission
- Differential privacy for statistics
- No private data leaves device

## Architecture

```
universal_language/
├── __init__.py          # Module interface
├── core.py              # Core language system
├── glyph.py             # GLYPH token processing
├── grammar.py           # Grammar rules and parsing
├── vocabulary.py        # Unified vocabulary management
├── translator.py        # Cross-modal/domain translation
├── multimodal.py        # Multi-modal input processing
├── privacy.py           # Privacy-preserving symbols
└── README.md            # This file
```

## Quick Start

### Basic Usage

```python
from universal_language import (
    UniversalLanguageCore,
    Symbol,
    Concept,
    get_universal_language
)

# Get the singleton instance
language = get_universal_language()

# Create a symbol
symbol = Symbol(
    id="MY_SYMBOL",
    domain=SymbolicDomain.EMOTION,
    name="joy",
    value=1.0,
    glyph="😊"
)

# Register the symbol
language.register_symbol(symbol)

# Translate to concept
concepts = language.translate_symbols_to_concepts([symbol])
```

### GLYPH Processing

```python
from universal_language import get_glyph_engine

glyph_engine = get_glyph_engine()

# Parse string to extract GLYPHs
sequence = glyph_engine.parse_string("Hello 😊 World 🌍")

# Create GLYPH token
token = glyph_engine.create_token("🧠", "consciousness")

# Calculate entropy
entropy = glyph_engine.get_entropy(sequence)
```

### Grammar Validation

```python
from universal_language import get_grammar_engine

grammar = get_grammar_engine()

# Validate sequence
symbols = [subject_symbol, verb_symbol, object_symbol]
is_valid, violations = grammar.validate_sequence(symbols)

# Parse with auto-correction
parsed = grammar.parse_sequence(symbols, auto_correct=True)
```

### Multi-Modal Processing

```python
from universal_language import get_multimodal_processor, ModalityType

processor = get_multimodal_processor()

# Create multi-modal message
message = processor.create_message({
    ModalityType.TEXT: "Hello",
    ModalityType.EMOJI: "👋",
    ModalityType.COLOR: "#FFD700"
})

# Extract dominant modality
dominant = processor.extract_dominant_modality(message)
```

### Privacy-Preserving Translation

```python
from universal_language import get_private_vault

# Get user's private vault
vault = get_private_vault("user123")

# Bind private symbol
private_symbol = vault.bind_symbol(
    token="🦋",  # User's private emoji
    token_type="emoji",
    meaning_id="EMOTION.TRANSFORMATION"
)

# Translate private to universal (only IDs transmitted)
concept_ids = vault.translate_private_to_universal(["🦋", "✨"])

# Translate universal back to private (personalized)
private_tokens = vault.translate_universal_to_private(concept_ids)
```

## Key Improvements

### Consolidation Benefits
- **Single source of truth** - No more duplicate vocabularies
- **Consistent API** - Same interface for all language operations
- **Reduced complexity** - From 100+ scattered files to 8 core modules
- **Better performance** - Centralized caching and optimization
- **Maintainable** - Clear module boundaries and responsibilities

### New Capabilities
- **Grammar rules** - Previously missing LUKHAS Grammar now implemented
- **Cross-modal translation** - Seamless conversion between modalities
- **Privacy by design** - Built-in privacy preservation
- **Entropy calculation** - Security features for high-entropy passwords
- **Auto-correction** - Grammar correction for malformed sequences

## Migration Guide

### From Old Symbolic Systems

```python
# Old way (scattered implementations)
from symbolic.vocabularies import emotion_vocabulary
from core.symbolic import symbolic_language
from bio_symbolic import glyph_hash

# New way (unified)
from universal_language import get_unified_vocabulary
vocabulary = get_unified_vocabulary()
```

### From GLYPH Processing

```python
# Old way
from core.glyph.glyphs import GLYPH_MAP

# New way
from universal_language import get_glyph_engine
glyph_engine = get_glyph_engine()
```

## Testing

Run the test suite:

```bash
python -m pytest universal_language/tests/
```

Run the demo:

```bash
python universal_language/demo.py
```

## Performance

- **Symbol lookup**: O(1) with caching
- **Translation**: O(n) for n symbols
- **Grammar validation**: O(n*m) for n symbols and m rules
- **Memory usage**: ~10MB for full vocabulary
- **Entropy calculation**: O(n) for sequence length n

## Security Considerations

The Universal Language module implements **military-grade security** for private symbols with a zero-knowledge authentication system. Key features:

- Private symbols **never leave device** unencrypted
- Only universal concept IDs are transmitted
- Differential privacy applied to statistics
- Device-specific encryption keys
- Audit logging for all operations
- **150+ bits of entropy** for login (vs ~48 bits for traditional passwords)
- Zero-knowledge proof authentication
- Device-binding prevents vault theft

📔 **See [SECURITY.md](./SECURITY.md) for comprehensive security documentation**

## Future Enhancements

- [ ] Neural embedding generation for concepts
- [ ] Advanced grammar learning from usage
- [ ] Real-time cross-language translation
- [ ] Quantum-resistant encryption
- [ ] Federated learning for population priors
- [ ] AR/VR modality support

## License

Proprietary - LUKHAS AI Systems

## Support

For questions or issues, contact the LUKHAS development team.

---

*Universal Language Module v1.0.0*
*Unified from 5+ fragmented implementations*
*Ready for production use*