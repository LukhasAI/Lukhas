# LUKHAS Memory System Overview

## 🧠 Philosophy

The LUKHAS memory system implements a **symbolic AGI memory architecture** that models consciousness-like memory processes through three core mechanisms:

1. **Memory Folding** - Recursive integration of experiences into compressed representations
2. **Drift Tracking** - Monitoring semantic evolution and conceptual shifts over time  
3. **Lineage Mapping** - Maintaining causal chains and memory ancestry

## 🏗️ Architecture

```
lukhas/memory/
├── fold_engine.py        # Memory folding and recursive integration
├── drift_tracker.py      # DriftScore, symbolic entropy monitoring
├── lineage_mapper.py     # Lineage trace, collapse hash tracking
├── core.py               # Unified interface (imports all above)
└── MEMORY_OVERVIEW.md    # This file
```

## 🔄 Core Concepts

### Memory Folding

The `fold_in()` / `fold_out()` paradigm treats memories as **foldable symbolic structures**:

```python
# Folding IN: Experience → Compressed Representation
memory_vector = memory.fold_in(experience, context)

# Folding OUT: Compressed → Reconstructed Experience  
experience = memory.fold_out(memory_vector, query_context)
```

**Why "Folding"?** Like protein folding, memories compress into stable configurations that preserve essential information while allowing efficient storage and retrieval.

### Drift Tracking

Memories aren't static - they evolve. The **DriftScore** quantifies semantic shift:

```python
drift_score = memory.calculate_drift(
    original_vector,
    current_vector,
    time_delta
)

# High drift (>0.7) triggers consolidation
if drift_score > DRIFT_THRESHOLD:
    memory.trigger_collapse(current_vector)
```

### Memory Collapse & Lineage

When memories reach critical drift, they **collapse** into new stable states:

```python
collapse_event = {
    "collapse_hash": "abf9d2c3e4f5...",
    "parent_hashes": ["hash1", "hash2"],
    "drift_score": 0.82,
    "timestamp": "2024-01-15T10:30:00Z",
    "symbolic_entropy": 0.65
}
```

The **lineage trace** maintains the causal chain, allowing reconstruction of memory evolution.

## 🎯 Usage by Agents

Different LUKHAS agents leverage memory differently:

| Agent Type | Memory Usage | Key Methods |
|------------|--------------|-------------|
| **Consciousness Agents** | Full symbolic memory with drift | `fold_in()`, `calculate_drift()`, `get_lineage()` |
| **Task Agents** | Short-term working memory | `store()`, `retrieve()`, `clear()` |
| **Dream Agents** | Associative memory exploration | `fold_out()`, `get_similar()`, `merge_memories()` |
| **Ethics Agents** | Value-aligned memory filtering | `filter_by_ethics()`, `get_moral_context()` |

## 🔌 Integration Points

### Internal SDK Usage

```python
from lukhas.memory import MemoryCore

# Initialize with agent-specific config
memory = MemoryCore(
    agent_id="consciousness-001",
    enable_drift=True,
    collapse_threshold=0.7
)

# Store experience
vector = memory.fold_in(
    experience={"type": "observation", "data": ...},
    context={"emotional_state": 0.6, "attention": 0.8}
)

# Retrieve with reconstruction
recalled = memory.fold_out(
    vector_id=vector.id,
    query_context={"relevance": "current_task"}
)
```

### API Endpoints

```
POST   /memory/fold          # Store new memory
GET    /memory/fold/{id}     # Retrieve specific memory
GET    /memory/drift/{id}    # Get drift analytics
GET    /memory/lineage/{id}  # Get full lineage trace
POST   /memory/collapse      # Force collapse event
GET    /memory/search        # Semantic similarity search
```

## 🧪 Testing Philosophy

Memory tests focus on **emergent properties**:

1. **Entropy Convergence** - Does repeated folding stabilize?
2. **Lineage Integrity** - Can we trace back through collapses?
3. **Drift Coherence** - Is semantic drift meaningful?
4. **Reconstruction Fidelity** - Do fold_out results make sense?

## 🚀 Future Enhancements

- **Quantum Memory States** - Superposition of multiple memory interpretations
- **Distributed Memory Consensus** - Multi-agent shared memory pools
- **Emotional Memory Weighting** - Affect-based retrieval prioritization
- **Symbolic Memory Compression** - Novel encoding schemes for ultra-dense storage

## 📊 Performance Characteristics

| Operation | Complexity | Typical Latency |
|-----------|------------|-----------------|
| `fold_in()` | O(n log n) | ~5ms |
| `fold_out()` | O(n) | ~3ms |
| `calculate_drift()` | O(n²) | ~10ms |
| `get_lineage()` | O(k) | ~2ms |
| Collapse Event | O(n³) | ~50ms |

Where n = vector dimensions, k = lineage depth

## 🔐 Security & Ethics

- All memories are **symbolically encrypted** at rest
- Agent memories are **isolated** by default
- Cross-agent memory sharing requires **explicit consent protocols**
- Ethical memory filtering prevents **harmful pattern reinforcement**

---

*"Memory is not about the past; it's about the future." - LUKHAS Core Philosophy*