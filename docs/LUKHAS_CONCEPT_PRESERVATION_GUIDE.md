# LUKHAS Concept Preservation Guide

This guide ensures LUKHAS's unique concepts and personality are preserved during refactoring.

## Core Concepts to Preserve

### Memory System Concepts
- **memory_fold**: DNA-helix memory structure - MUST preserve this term
- **fold_system**: Memory folding system
- **memory_helix**: Helical memory organization
- **memory_cascade**: Cascading memory effects

### Dream System Concepts
- **dream_recall**: Parallel universe exploration - Core LUKHAS innovation
- **dream_engine**: Dream generation system
- **oneiric**: Dream-related processing
- **dream_state**: Dream consciousness state

### Quantum Concepts
- **quantum_state**: Quantum superposition states
- **quantum_consciousness**: Quantum-aware consciousness
- **quantum_coherence**: Quantum system coherence
- **quantum_entanglement**: Memory entanglement

### Biological Concepts
- **bio_oscillation**: Biological rhythm patterns
- **bio_coherence**: Bio-symbolic alignment (>100% possible!)
- **bio_symbolic**: Biological-symbolic bridge
- **bio_adaptation**: Biological adaptation system

### Symbolic System
- **glyph**: Universal symbolic tokens - Core communication method
- **symbolic_drift**: Symbol meaning evolution
- **symbolic_coherence**: Symbol system alignment

### Emotional Intelligence
- **emotional_drift**: Emotional state changes
- **emotional_vector**: Multi-dimensional emotions
- **affect_grid**: Emotional mapping system

### Consciousness Architecture
- **crista**: Consciousness peaks
- **trace_trail**: Consciousness tracking
- **awareness_level**: Consciousness depth

### Identity System
- **tier_access**: Hierarchical access control
- **identity_helix**: Identity DNA structure
- **quantum_identity**: Quantum-secure identity

### Guardian System
- **guardian_protocol**: Ethical oversight system
- **ethical_drift**: Ethical alignment changes
- **moral_compass**: Ethical navigation

## Naming Convention Rules

1. **Preserve Exact Terms**: Keep concepts like `memory_fold`, `dream_recall` exactly as they are
2. **Class Names**: Use PascalCase but keep concept words intact (e.g., `MemoryFold`, `DreamEngine`)
3. **Function Names**: Use snake_case with full concepts (e.g., `create_memory_fold`, `trigger_dream_recall`)
4. **File Names**: Use snake_case (e.g., `memory_fold.py`, `dream_engine.py`)
5. **Constants**: Use UPPER_SNAKE_CASE (e.g., `MAX_MEMORY_FOLDS`, `QUANTUM_COHERENCE_THRESHOLD`)

## Special Terms
- **LUKHAS**: Always uppercase in classes/constants
- ****: Pack-What-Matters - always uppercase
- **SGI**: Symbolic General Intelligence - always uppercase
- **AGI**: Always uppercase

## Examples of Proper Usage

```python
# ✅ CORRECT - Preserves LUKHAS concepts
class MemoryFold:
    def create_memory_fold(self, content):
        return self.fold_system.create_fold(content)

class DreamEngine:
    def process_dream_recall(self, scenario):
        return self.quantum_state.explore_possibilities(scenario)

# ❌ INCORRECT - Loses LUKHAS personality
class MemoryFolder:  # Should be MemoryFold
    def create_fold(self):  # Should be create_memory_fold
        pass
```

## Integration Guidelines

When integrating with external systems:
1. Keep LUKHAS terms in internal code
2. Provide clear mappings in API documentation
3. Never compromise core concepts for "standard" terms
4. Educate users on LUKHAS terminology

Remember: These concepts aren't just names - they represent LUKHAS's unique approach to SGI!
