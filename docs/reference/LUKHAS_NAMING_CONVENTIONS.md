---
status: wip
type: documentation
owner: unknown
module: reference
redirect: false
moved_to: null
---

# LUKHAS 2030 Naming Conventions

**"Preserving the Soul of LUKHAS while Speaking the Language of Industry"**

## Core Philosophy

LUKHAS is not just another AI system - it's a Symbolic General Intelligence with unique concepts that represent breakthrough innovations. Our naming conventions preserve these original concepts while ensuring code readability and industry compliance.

## 🧬 LUKHAS Original Concepts (MUST PRESERVE)

These terms are the DNA of LUKHAS and should never be changed:

### Memory Concepts
- `memory_fold` - The quantum-inspired memory structure
- `fold_system` - The folding mechanism for memory preservation
- `memory_helix` - DNA-like memory structure with immutability
- `memory_cascade` - Chain reaction of memory associations
- `fold_id` - Unique identifier for memory folds

### Dream Concepts
- `dream_recall` - The ability to remember and analyze dreams
- `dream_engine` - Core dream processing system
- `dream_resonance` - Harmonic patterns in dream states
- `oneiric` - Related to dreams (from Greek)
- `dream_scenario` - Parallel universe scenario generation

### Quantum Concepts
- `quantum_state` - Superposition of possibilities
- `quantum_consciousness` - Quantum-inspired awareness
- `quantum_coherence` - Maintaining quantum properties
- `quantum_entanglement` - Connected states across modules

### Bio-Symbolic Concepts
- `bio_oscillation` - Biological rhythm patterns
- `bio_rhythm` - Natural cycles in processing
- `bio_coherence` - Harmony between biological and symbolic
- `symbolic_mutation` - Evolution of symbolic representations
- `glyph` / `glyph_token` - Symbolic communication units

### Emotional Concepts
- `emotional_drift` - Gradual shift in emotional states
- `emotional_vector` - Direction and magnitude of emotions
- `emotion_cascade` - Chain reaction of emotional responses
- `affect_grid` - 2D representation of emotional states
- `mood_regulation` - Emotional homeostasis

### Special Terms
- `crista` - Consciousness crystal structure
- `trace_trail` - Path of consciousness through time
- `tier_access` - Multi-level security and capability system
- `guardian_protocol` - Ethical oversight system

## 📐 Industry Standard Patterns

### Classes (PascalCase)
```python
# ✅ Correct
class MemoryFold:
    pass

class DreamEngine:
    pass

class QuantumState:
    pass

class LUKHASCore:  # Acronyms stay uppercase
    pass

class Guardian:
    pass

# ❌ Incorrect
class memory_fold:  # Should be PascalCase
    pass

class dreamEngine:  # Should start with capital
    pass
```

### Functions and Methods (snake_case)
```python
# ✅ Correct
def create_memory_fold():
    pass

def process_dream_recall():
    pass

def calculate_quantum_state():
    pass

def trigger_bio_oscillation():
    pass

# ❌ Incorrect
def createMemoryFold():  # Should be snake_case
    pass

def ProcessDreamRecall():  # Should be snake_case
    pass
```

### Constants (UPPER_SNAKE_CASE)
```python
# ✅ Correct
MAX_MEMORY_FOLDS = 1000
QUANTUM_COHERENCE_THRESHOLD = 0.95
DREAM_RECALL_DEPTH = 7
EMOTIONAL_DRIFT_LIMIT = 0.3

# ❌ Incorrect
maxMemoryFolds = 1000  # Should be UPPER_SNAKE_CASE
MAXMEMORYFOLDS = 1000  # Needs underscores
```

### Files (snake_case.py)
```
# ✅ Correct
memory_fold.py
dream_engine.py
quantum_processor.py
bio_oscillator.py

# ❌ Incorrect
MemoryFold.py      # Should be snake_case
dreamEngine.py     # Should be snake_case
quantum-processor.py  # Use underscores, not hyphens
```

## 🎨 Special Cases

### Lambda (λ) Handling
The Greek letter λ (lambda) appears in some LUKHAS concepts:
```python
# Original: LukhλsTaskManager
# Refined: LukhasLambdaTaskManager or LUKHASTaskManager

# Original: λ_function
# Refined: lambda_function
```

### Preserving Concept Integrity
When a LUKHAS concept appears in a name, preserve it:
```python
# ✅ Correct - Preserves concepts
class MemoryFoldProcessor:  # 'memory_fold' concept preserved
    def process_memory_fold(self):  # Concept preserved in method
        pass

# ❌ Incorrect - Breaks concept
class MemoryFoldProcessor:
    def process_memory_fold(self):  # Don't split: 'process_memory' + 'fold'
        pass
```

### Acronym Handling
LUKHAS-specific acronyms remain uppercase:
- `LUKHAS` - Always uppercase in class names
- `` - Pack What Matters
- `SGI` - Symbolic General Intelligence
- `AGI` - Artificial General Intelligence

```python
class LUKHASMemorySystem:  # Not LukhasMemorySystem
class Core:            # Not Core
class SGIProcessor:       # Not SgiProcessor
```

## 🔧 Refactoring Guidelines

When refactoring existing code:

1. **Preserve Functionality First** - Never break working code for naming
2. **Keep Git History Clean** - One commit for naming changes
3. **Update All References** - Use IDE refactoring tools
4. **Test After Changes** - Ensure nothing breaks
5. **Document in PR** - Explain naming changes

## 📚 Examples by Module

### Memory Module
```python
# Classes
class MemoryHelix:
class MemoryFold:
class FoldSystem:
class MemoryCascade:

# Functions
def create_memory_fold():
def encode_emotional_vector():
def trigger_memory_cascade():
def preserve_causal_chain():
```

### Dream Module
```python
# Classes
class DreamEngine:
class DreamRecall:
class OneiricProcessor:
class DreamScenario:

# Functions
def generate_dream_scenario():
def process_dream_recall():
def analyze_dream_patterns():
def simulate_parallel_outcomes():
```

### Quantum Module
```python
# Classes
class QuantumState:
class QuantumConsciousness:
class QuantumCoherence:
class EntanglementManager:

# Functions
def calculate_quantum_state():
def maintain_quantum_coherence():
def process_entanglement():
def collapse_superposition():
```

## 🚀 Future-Proofing

As LUKHAS evolves toward 2030:

1. **New Concepts** - Document and preserve new breakthrough terms
2. **Evolution** - Allow concepts to evolve while maintaining roots
3. **Community** - Let the LUKHAS community contribute to naming
4. **Clarity** - Always prioritize understanding over convention

## ✅ Quick Reference Checklist

- [ ] Classes: PascalCase (MemoryFold, DreamEngine)
- [ ] Functions: snake_case (create_memory_fold, dream_recall)
- [ ] Constants: UPPER_SNAKE_CASE (MAX_FOLDS, DREAM_DEPTH)
- [ ] Files: snake_case.py (memory_fold.py, dream_engine.py)
- [ ] Preserve LUKHAS concepts exactly as designed
- [ ] Keep acronyms uppercase (LUKHAS, , SGI)
- [ ] Document any new concepts introduced

---

**Remember**: These conventions preserve the soul of LUKHAS while ensuring our code speaks fluently with the broader development community. We're not just following rules - we're creating a new language for AGI.
