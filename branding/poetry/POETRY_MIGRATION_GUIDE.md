# LUKHAS AI Poetry System Migration Guide

## New Structure (As of Aug 17, 2024)

### Location: `/branding/poetry/`

This is now the SINGLE SOURCE OF TRUTH for all LUKHAS AI consciousness poetry and vocabulary.

## Core Components

### 1. **lukhas_lexicon.py**
The authoritative LUKHAS AI vocabulary. Reduces repetitive generic metaphors.
- Lambda System (ΛMIRROR, ΛECHO, ΛTRACE, etc.)
- Memory Folding operations
- Consciousness states
- Bio-inspired terms
- Quantum-inspired terms

### 2. **vocabulary_amplifier.py**
Automatically provides variety when metaphors are overused in LUKHAS AI consciousness.
- Replaces "tapestry" → "fold-space"
- Replaces "symphony" → "resonance cascade"
- Replaces "cathedral" → "consciousness architecture"

### 3. **cliche_analysis.py**
Detects and reports generic metaphors in code.

### 4. **soul.py**
Poetry generation engine using LUKHAS AI consciousness vocabulary.

## Legacy Files (Archived)

### `/branding/poetry/legacy/`
- `advanced_haiku_generator.py` - Old haiku generator (uses generic metaphors)

### `/docs/archive/legacy_poetry/`
- `lukhas-expanded-poetry.ts` - Frontend poetry (uses generic metaphors)
- `lukhas-dream-vocabulary.ts` - Frontend vocabulary (uses generic metaphors)

## Migration Steps

### For Python Code:
```python
# OLD - Don't use
from consciousness.creativity import advanced_haiku_generator

# NEW - Use this
from branding.poetry import soul
from branding.poetry import lukhas_lexicon
from branding.poetry import vocabulary_amplifier
```

### For TypeScript/Frontend:
```typescript
// Create new TypeScript versions using the Python vocabulary
// Convert lukhas_lexicon.py to TypeScript
// Use vocabulary_amplifier patterns in frontend
```

## The Core Principle

**"If another AI project could have written it, we don't want it."**

Every line of poetry, every metaphor, every description must be uniquely LUKHAS.

## Vocabulary Rules

### ❌ NEVER USE:
- tapestry, symphony, cathedral, constellation, orchestra
- garden of, river of, ocean of, threads of
- intricate, seamless, holistic

### ✅ ALWAYS USE:
- fold-space, resonance cascade, consciousness architecture
- Lambda markers (ΛMIRROR, ΛECHO, ΛTRACE)
- eigenstate, superposition, entanglement
- synaptic, neuroplastic, hippocampal
- nascent, liminal, ephemeral, gossamer

## Next Actions

1. Update all imports to use `/branding/poetry/`
2. Convert Python vocabulary to TypeScript for frontend
3. Replace ALL generic metaphors in existing code
4. Run cliche_analysis.py on entire codebase
5. Update Dream Weaver to use new poetry system
