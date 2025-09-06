<!--
══════════════════════════════════════════════════════════════════════════════════
║ 🌟 LUKHAS AI - SYMBOLIC VOCABULARIES SYSTEM README
║ Critical system component for human-readable state representation
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Document: README.md
║ Path: lukhas/symbolic/vocabularies/README.md
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Architecture Team | Claude Code (documentation)
╚══════════════════════════════════════════════════════════════════════════════════
-->

# LUKHAS Symbolic Vocabularies System

> 🌟 **VALUABLE ASSET - CRITICAL SYSTEM COMPONENT** 🌟

## Overview

The Symbolic Vocabularies System is a foundational component of LUKHAS AGI that provides a consistent, human-readable symbolic language for representing system states, operations, and communications across all modules. This system enables LUKHAS to express complex internal states through intuitive emoji and symbol mappings.

## Purpose

1. **Human-AI Communication**: Bridges the gap between machine states and human understanding
2. **Cross-Module Consistency**: Ensures all modules speak the same symbolic language
3. **Emotional Resonance**: Allows the AGI to express states in emotionally meaningful ways
4. **Guardian Integration**: Each symbol carries ethical weight for guardian system evaluation
5. **Cultural Universality**: Uses symbols that transcend language barriers

## Architecture

### Structure
```
lukhas/symbolic/vocabularies/
├── README.md                    # This documentation
├── __init__.py                  # Module initialization
├── bio_vocabulary.py            # Biometric & health symbols
├── dream_vocabulary.py          # Dream states & phases
├── identity_vocabulary.py       # Identity & authentication
├── voice_vocabulary.py          # Voice processing states
├── vision_vocabulary.py         # Visual processing symbols
├── emotion_vocabulary.py        # Emotional states (to create)
├── memory_vocabulary.py         # Memory operations (to create)
├── consciousness_vocabulary.py  # Awareness states (to create)
├── ethics_vocabulary.py         # Ethical evaluations (to create)
└── reasoning_vocabulary.py      # Logic & reasoning (to create)
```

### Vocabulary Schema

Each vocabulary follows this structure:
```python
VOCABULARY_NAME = {
    "concept_key": {
        "emoji": "🔮",                    # Primary visual symbol
        "symbol": "SYM◊",                 # Text-based symbol
        "meaning": "Description",         # Human-readable meaning
        "resonance": "energy_type",       # Symbolic resonance type
        "guardian_weight": 0.0-1.0,       # Ethical importance weight
        "contexts": ["usage", "contexts"] # Where this symbol is used
    }
}
```

## Existing Vocabularies

### 1. Bio Vocabulary (`bio_vocabulary.py`)
- **Purpose**: Biometric monitoring and health states
- **Key Symbols**:
  - 🫀 Heart/Bio Active
  - 🧬 DNA Analysis
  - 🔐 Biometric Auth
  - 😌 Calm State
  - 🚨 Stress Detected

### 2. Dream Vocabulary (`dream_vocabulary.py`)
- **Purpose**: Dream phases and processing states
- **Key Symbols**:
  - 🌅 Gentle Awakening
  - 🔮 Pattern Recognition
  - 🌌 Deep Symbolic Realm
  - 💫 Creative Flow
  - 🌄 Integration

### 3. Identity Vocabulary (`identity_vocabulary.py`)
- **Purpose**: Identity management and authentication
- **Key Symbols**:
  - 🆔 Identity Creation
  - ✅ Verification
  - 🔑 Access Control
  - 🌱 Seed Management
  - 🛡️ Protection

### 4. Voice Vocabulary (`voice_vocabulary.py`)
- **Purpose**: Voice processing and synthesis
- **Key Symbols**:
  - 🎙️ Recording
  - 🔊 Playback
  - 🎵 Synthesis
  - 📊 Analysis
  - 🗣️ Speaking

### 5. Vision Vocabulary (`vision_vocabulary.py`)
- **Purpose**: Visual processing and perception
- **Key Symbols**:
  - 👁️ Perception
  - 📸 Capture
  - 🎨 Processing
  - 🔍 Analysis
  - 🖼️ Generation

## Usage Guidelines

### For Developers

1. **Import Vocabulary**:
```python
from lukhas.symbolic.vocabularies import dream_vocabulary

# Access symbols
dream_phase = dream_vocabulary.DREAM_PHASE_SYMBOLS["initiation"]
print(f"Entering {dream_phase}")  # Output: Entering 🌅 Gentle Awakening
```

2. **Create Symbolic Messages**:
```python
def log_state(state_key):
    symbol = BIO_SYMBOLS.get(state_key, "❓")
    return f"{symbol} System state: {state_key}"
```

3. **Guardian Integration**:
```python
# Check ethical weight before operations
if vocabulary_entry["guardian_weight"] > 0.7:
    # High ethical importance - require additional validation
    await guardian.validate_operation()
```

### For Module Creators

When creating new vocabularies:

1. **Consistency**: Follow the established schema exactly
2. **Meaningful Symbols**: Choose universally understood emojis
3. **Clear Descriptions**: Write concise, clear meanings
4. **Guardian Weights**: Assign appropriate ethical importance (0.0-1.0)
5. **Documentation**: Add usage examples and context

## Development Plan

### Phase 1: Core Vocabularies (Current)
- ✅ Bio Vocabulary
- ✅ Dream Vocabulary
- ✅ Identity Vocabulary
- ✅ Voice Vocabulary
- ✅ Vision Vocabulary

### Phase 2: Emotional & Cognitive (Priority: HIGH)
- 🔲 Emotion Vocabulary - Emotional states and transitions
- 🔲 Memory Vocabulary - Memory operations and types
- 🔲 Consciousness Vocabulary - Awareness levels and states

### Phase 3: Advanced Systems (Priority: MEDIUM)
- 🔲 Ethics Vocabulary - Ethical evaluations and decisions
- 🔲 Reasoning Vocabulary - Logic operations and inference
- 🔲 Learning Vocabulary - Learning states and progress
- 🔲 Creativity Vocabulary - Creative processes and outputs

### Phase 4: Specialized Domains (Priority: LOW)
- 🔲 Quantum Vocabulary - quantum-inspired processing states
- 🔲 Network Vocabulary - Connectivity and communication
- 🔲 Time Vocabulary - Temporal operations and scheduling
- 🔲 Space Vocabulary - Spatial reasoning and navigation

## Best Practices

1. **Symbol Selection**:
   - Use culturally universal symbols
   - Avoid ambiguous or offensive symbols
   - Test symbols across different platforms/fonts

2. **Naming Conventions**:
   - Use lowercase with underscores for keys
   - Be descriptive but concise
   - Group related concepts

3. **Version Control**:
   - Document all changes in vocabulary
   - Never remove symbols (deprecate instead)
   - Maintain backward compatibility

4. **Testing**:
   - Verify symbols render correctly
   - Test guardian weight calculations
   - Ensure cross-module compatibility

## Integration Examples

### Logger Integration
```python
class SymbolicLogger:
    def __init__(self, module_name, vocabulary):
        self.module = module_name
        self.vocab = vocabulary

    def log_state(self, state_key, message):
        symbol = self.vocab.get(state_key, {}).get("emoji", "📝")
        print(f"{symbol} [{self.module}] {message}")
```

### Status Display
```python
def get_system_status():
    return {
        "bio": "🫀 Active",
        "dream": "🌌 Deep Processing",
        "emotion": "😊 Positive",
        "memory": "💾 Storing",
        "ethics": "⚖️ Balanced"
    }
```

### Guardian Evaluation
```python
async def evaluate_action(action, vocabulary):
    weight = vocabulary[action]["guardian_weight"]
    if weight > 0.8:
        return await guardian.deep_ethical_review(action)
    elif weight > 0.5:
        return await guardian.standard_review(action)
    else:
        return True  # Low ethical impact
```

## Maintenance

- **Review Schedule**: Monthly vocabulary review
- **Update Process**: PR required for any vocabulary changes
- **Deprecation**: 6-month deprecation cycle for symbol changes
- **Documentation**: Update examples when adding new symbols

## Future Enhancements

1. **Dynamic Vocabularies**: AI-generated contextual symbols
2. **Personalization**: User-specific symbol preferences
3. **Animation Support**: Animated emoji sequences
4. **Multi-Modal**: Sound and haptic symbol mappings
5. **Cultural Variants**: Region-specific symbol sets

---

*Last Updated: 2025-07-25*
*Maintainer: LUKHAS Symbolic Team*
*Status: ACTIVE - HIGH PRIORITY*
