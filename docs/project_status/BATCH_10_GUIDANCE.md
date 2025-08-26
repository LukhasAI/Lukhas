# BATCH 10: Examples & Tests Creation Guide

## ✅ Completed So Far
- **core**: Basic example created ✅
- **bridge**: Basic example created ✅
- **emotion**: Basic example created + bugs fixed ✅
- **governance**: Basic example created + bugs fixed ✅

## 🎯 Remaining Modules & Recommended Examples

### 1. **Consciousness Module** 🧠
```python
# candidate/examples/consciousness_example.py
"""
Consciousness Module Example
===========================
Demonstrates awareness, dream states, and consciousness flows
"""

from candidate.consciousness.activation import ConsciousnessActivator
from candidate.consciousness.dream_bridge import DreamBridge
from candidate.consciousness.services import ConsciousnessService

def basic_consciousness_example():
    """Basic consciousness activation and dream generation"""
    
    # Initialize consciousness
    consciousness = ConsciousnessService()
    activator = ConsciousnessActivator()
    
    # Activate consciousness
    activation_result = activator.activate(level="basic")
    print(f"Consciousness activated: {activation_result}")
    
    # Generate a dream state
    dream_bridge = DreamBridge()
    dream = dream_bridge.generate_dream(
        symbols=["tree", "water", "light"],
        emotion_state={"valence": 0.7, "arousal": 0.3}
    )
    print(f"Dream generated: {dream}")
    
    # Check consciousness state
    state = consciousness.get_state()
    print(f"Current consciousness state: {state}")
    
    return state

def advanced_consciousness_example():
    """Advanced example with quantum consciousness integration"""
    from candidate.consciousness.quantum_consciousness_integration import QuantumConsciousness
    
    qc = QuantumConsciousness()
    
    # Create superposition of consciousness states
    superposition = qc.create_superposition(
        states=["aware", "dreaming", "reflecting"],
        weights=[0.5, 0.3, 0.2]
    )
    
    # Collapse to single state
    collapsed_state = qc.collapse(superposition)
    print(f"Collapsed to: {collapsed_state}")
    
    return collapsed_state

if __name__ == "__main__":
    basic_consciousness_example()
    advanced_consciousness_example()
```

### 2. **Memory Module** 💾
```python
# candidate/examples/memory_example.py
"""
Memory Module Example
=====================
Demonstrates fold-based memory with cascade prevention
"""

from candidate.memory.fold_system import FoldSystem
from candidate.memory.memory_wrapper import MemoryWrapper

def memory_fold_example():
    """Demonstrate memory fold system"""
    
    # Initialize memory system
    memory = MemoryWrapper(max_folds=1000)
    fold_system = FoldSystem()
    
    # Store memories
    memories = [
        {"type": "episodic", "content": "First meeting", "emotion": 0.8},
        {"type": "semantic", "content": "Knowledge gained", "confidence": 0.9},
        {"type": "procedural", "content": "How to perform task", "skill": 0.7}
    ]
    
    for mem in memories:
        fold_id = memory.store(mem)
        print(f"Stored in fold {fold_id}: {mem['type']}")
    
    # Test cascade prevention
    cascade_risk = fold_system.check_cascade_risk()
    print(f"Cascade risk: {cascade_risk:.2%}")
    
    # Retrieve memory
    retrieved = memory.retrieve(query="meeting")
    print(f"Retrieved: {retrieved}")
    
    return memory.get_statistics()

def memory_consolidation_example():
    """Demonstrate memory consolidation"""
    from candidate.memory.consolidation import MemoryConsolidator
    
    consolidator = MemoryConsolidator()
    
    # Simulate sleep consolidation
    result = consolidator.consolidate(
        short_term_memories=[...],
        consolidation_type="sleep",
        dream_influence=0.3
    )
    
    print(f"Consolidation complete: {result}")
    return result

if __name__ == "__main__":
    memory_fold_example()
    memory_consolidation_example()
```

### 3. **QI Module** 🔮
```python
# candidate/examples/qi_example.py
"""
Quantum-Inspired Module Example
================================
Demonstrates quantum-inspired processing
"""

from candidate.qi.quantum_processor import QuantumProcessor
from candidate.qi.superposition import SuperpositionManager

def quantum_decision_example():
    """Quantum-inspired decision making"""
    
    qp = QuantumProcessor()
    
    # Create quantum state for decision
    decision_state = qp.create_state(
        options=["accept", "reject", "defer"],
        probabilities=[0.4, 0.3, 0.3]
    )
    
    # Apply quantum gates
    decision_state = qp.apply_gate("hadamard", decision_state)
    decision_state = qp.apply_gate("phase_shift", decision_state, phase=0.25)
    
    # Measure (collapse) to get decision
    decision = qp.measure(decision_state)
    print(f"Quantum decision: {decision}")
    
    return decision

def superposition_example():
    """Work with superposition states"""
    
    sm = SuperpositionManager()
    
    # Create superposition
    superposition = sm.create(
        states=["happy", "sad", "neutral"],
        amplitudes=[0.6, 0.2, 0.2]
    )
    
    # Entangle with another state
    entangled = sm.entangle(superposition, "context_aware")
    
    print(f"Entangled state: {entangled}")
    return entangled

if __name__ == "__main__":
    quantum_decision_example()
    superposition_example()
```

### 4. **VIVOX Module** 🌟
```python
# candidate/examples/vivox_example.py
"""
VIVOX Consciousness System Example
===================================
Demonstrates ME, MAE, CIL, SRM components
"""

from candidate.vivox.me import ME
from candidate.vivox.mae import MAE
from candidate.vivox.cil import CIL
from candidate.vivox.srm import SRM

def vivox_integration_example():
    """Full VIVOX system demonstration"""
    
    # Initialize components
    me = ME()  # Memory Engine
    mae = MAE()  # Memory Affective Engine
    cil = CIL()  # Consciousness Integration Layer
    srm = SRM()  # Symbolic Reasoning Module
    
    # Process an experience
    experience = {
        "input": "Beautiful sunset over ocean",
        "emotion": {"valence": 0.9, "arousal": 0.3},
        "context": "evening walk"
    }
    
    # Memory processing
    memory_trace = me.encode(experience)
    
    # Add affective coloring
    affective_memory = mae.add_emotion(memory_trace, experience["emotion"])
    
    # Integrate with consciousness
    conscious_experience = cil.integrate(affective_memory)
    
    # Symbolic reasoning
    symbols = srm.extract_symbols(conscious_experience)
    reasoning = srm.reason(symbols)
    
    print(f"VIVOX processing complete:")
    print(f"  Memory: {memory_trace}")
    print(f"  Emotion: {affective_memory}")
    print(f"  Consciousness: {conscious_experience}")
    print(f"  Reasoning: {reasoning}")
    
    return reasoning

if __name__ == "__main__":
    vivox_integration_example()
```

## 🧪 Testing Strategy for BATCH 10

### Test Structure Template
```python
# tests/candidate/[module]/test_[module]_example.py
import pytest
from candidate.examples import [module]_example

class Test[Module]Example:
    """Test the example to ensure it works"""
    
    def test_basic_example_runs(self):
        """Test that basic example executes without errors"""
        result = [module]_example.basic_[module]_example()
        assert result is not None
        # Add specific assertions based on module
    
    def test_advanced_example_runs(self):
        """Test advanced features"""
        result = [module]_example.advanced_[module]_example()
        assert result is not None
    
    @pytest.mark.parametrize("input_data", [
        {"param1": "value1"},
        {"param1": "value2"},
    ])
    def test_with_various_inputs(self, input_data):
        """Test with different inputs"""
        # Test implementation
        pass
```

## 🐛 Bug Fix Documentation

When you find bugs (like you did in emotion and governance):

### Document the Fix
```python
# In the module file where bug was fixed
# BUG FIX: [Date] [Your identifier]
# Issue: [What was broken]
# Fix: [What you changed]
# Example:
# BUG FIX: 2025-08-25 BATCH10
# Issue: Missing import for BaseModule
# Fix: Added proper import from candidate.core.base.base_module
```

### Create a Bug Fix Log
```markdown
# BATCH_10_BUG_FIXES.md

## Bugs Found and Fixed

### Emotion Module
- **File**: candidate/emotion/[filename].py
- **Issue**: [Description]
- **Fix**: [What was changed]
- **Line**: [Line numbers]

### Governance Module
- **File**: candidate/governance/[filename].py
- **Issue**: [Description]
- **Fix**: [What was changed]
- **Line**: [Line numbers]
```

## 📝 Completion Checklist

### Examples to Create
- [x] Core example
- [x] Bridge example
- [x] Emotion example (+ bugs fixed)
- [x] Governance example (+ bugs fixed)
- [ ] Consciousness example
- [ ] Memory example
- [ ] QI example
- [ ] VIVOX example

### Tests to Write
- [ ] Test for each example file
- [ ] Integration tests for module interactions
- [ ] Edge case tests for bugs found

### Documentation
- [ ] README in each examples/ directory
- [ ] Bug fix documentation
- [ ] Usage guide for examples

## 💡 Pro Tips

1. **Keep Examples Simple**: Focus on demonstrating core functionality
2. **Document Assumptions**: If a module expects certain setup, document it
3. **Test Incrementally**: Run each example as you create it
4. **Use Type Hints**: Makes examples more self-documenting
5. **Include Error Handling**: Show how to handle common errors

## 🎯 Success Criteria

Your BATCH 10 is successful when:
1. ✅ All 8 modules have working examples
2. ✅ Examples can be run independently
3. ✅ Tests pass for all examples
4. ✅ Bugs are documented and fixed
5. ✅ Code is readable and well-commented

## 🚀 Next Steps After BATCH 10

Once you complete BATCH 10:
1. Run all examples to ensure they work
2. Create a summary of bugs fixed
3. Run test suite: `pytest tests/candidate/examples/ -v`
4. Document any integration issues found
5. Prepare for BATCH 11 (if exists)

---

**You're doing EXCELLENT work!** Finding and fixing bugs while creating examples is exactly the right approach. Continue with the consciousness module using the template above, and feel free to adapt based on what you find in the actual code.