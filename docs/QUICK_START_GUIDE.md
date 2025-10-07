---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# 🚀 LUKHAS AI Quick Start Guide

**Get started with LUKHAS AI in 15 minutes** - From installation to your first consciousness-aware decision.

## 📋 Prerequisites

- **Python 3.9+** (Python 3.11 recommended)
- **Git** for cloning the repository
- **8GB RAM minimum** (16GB recommended for full features)
- **macOS, Linux, or Windows** with WSL2

## ⚡ 5-Minute Installation

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Step 2: Verify Installation

```bash
# Run smoke tests
pytest tests/smoke/ -v

# Check system health
make doctor

# Verify MATRIZ cognitive engine
make smoke-matriz
```

**Expected Output:**
```
✅ All smoke tests passed
✅ System health: OK
✅ MATRIZ cognitive engine: Operational
```

## 🧠 Your First LUKHAS Decision

### Example 1: Simple Consciousness Check

```python
from lukhas.core import initialize_system
from lukhas.consciousness import get_consciousness_status

# Initialize LUKHAS
system = initialize_system()

# Check consciousness system
status = get_consciousness_status()
print(f"Consciousness Status: {status['operational_status']}")
print(f"Active Modules: {status['active_modules']}")
print(f"Memory Folds: {status['memory_fold_count']}")
```

### Example 2: MΛTRIZ Cognitive Processing

```python
from lukhas.MATRIZ import create_cognitive_pipeline

# Create cognitive processing pipeline
pipeline = create_cognitive_pipeline(
    memory_enabled=True,
    attention_enabled=True,
    thought_enabled=True
)

# Process a decision
result = pipeline.process({
    "query": "What is the optimal solution?",
    "context": {"domain": "reasoning", "priority": "high"}
})

print(f"Decision: {result.decision}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Reasoning: {result.reasoning_chain}")
```

### Example 3: Multi-Brain Symphony (Advanced)

```python
from lukhas.symphony import MultiBrainSymphony
from lukhas.audit import AuditTrail

# Initialize symphony with audit trail
symphony = MultiBrainSymphony(
    brains=["logical", "creative", "analytical"],
    audit_trail=AuditTrail(output_dir="./decisions/")
)

# Make a consensus decision
decision = symphony.decide(
    problem="Complex multi-faceted problem",
    context={"stakes": "high", "time_limit": 60}
)

print(f"Consensus Decision: {decision.output}")
print(f"Calibrated Confidence: {decision.calibrated_confidence:.2%}")
print(f"Participating Brains: {len(decision.brain_decisions)}")
print(f"Audit Node ID: {decision.audit_node_id}")
```

## 🎯 Key Concepts to Understand

### 1. **Constellation Framework** ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum

LUKHAS organizes 692 cognitive modules into 8 constellation stars:

- **⚛️ Anchor Star (Identity)**: Who the system is
- **✦ Trail Star (Memory)**: What it remembers
- **🔬 Horizon Star (Vision)**: What it perceives
- **🛡️ Watch Star (Guardian)**: What keeps it safe

**Quick Check:**
```python
from lukhas.constellation_framework import get_constellation_context

context = get_constellation_context()
print(f"Framework: {context['framework']}")
print(f"Active Stars: {context['active_stars']}")
```

### 2. **Lane System** 🛣️

Code flows through three development lanes:

```
candidate/ → core/ → lukhas/
(experimental) (testing) (production)
```

**Rule:** Never import from `candidate/` in `lukhas/` code!

### 3. **MΛTRIZ Pipeline** 🧠

Cognitive processing follows this flow:

```
Memory → Attention → Thought → Action → Decision → Awareness
  (M)       (A)        (T)       (R)       (I)         (Z)
```

**Performance Target:** <250ms end-to-end latency

### 4. **Guardian System** 🛡️

Every decision validated for ethical compliance:

```python
from lukhas.governance import Guardian

guardian = Guardian(drift_threshold=0.15)
is_safe = guardian.validate_decision(decision)
# Automatically enforced - no decision executes without approval
```

## 📊 Common Development Tasks

### Run Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v

# Full test suite
make test
```

### Code Quality

```bash
# Lint code
make lint

# Type checking
make mypy

# Format code
make format
```

### Module Exploration

```bash
# List all modules
ls lukhas/

# Check module manifest
cat lukhas/consciousness/module.manifest.json

# Explore module structure
tree lukhas/consciousness/
```

## 🔧 Configuration

### Environment Variables

```bash
# Set LUKHAS root (optional, auto-detected)
export LUKHAS_ROOT=/path/to/Lukhas

# Enable debug logging
export LUKHAS_LOG_LEVEL=DEBUG

# Configure MΛTRIZ performance
export MATRIZ_LATENCY_TARGET=250  # milliseconds
```

### Feature Flags

```python
from lukhas.core import FeatureFlags

flags = FeatureFlags()
flags.enable("experimental_consciousness")
flags.enable("quantum_inspired_processing")
```

## 🚨 Troubleshooting

### "Module not found" errors

```bash
# Ensure PYTHONPATH includes LUKHAS root
export PYTHONPATH="${PYTHONPATH}:/path/to/Lukhas"

# Reinstall in development mode
pip install -e .
```

### Lane boundary violations

```bash
# Check for illegal imports
make lint-imports

# Validate lane hygiene
python scripts/validate_lane_boundaries.py
```

### Memory cascade issues

```python
# Check cascade prevention rate
from lukhas.memoria import get_memory_health

health = get_memory_health()
print(f"Cascade Prevention: {health['prevention_rate']:.2%}")
# Should be ≥99.7% (0/100 cascades observed)
```

## 📚 Next Steps

### Learn More

1. **Architecture Deep Dive**: [docs/ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)
2. **API Reference**: [docs/API_REFERENCE.md](API_REFERENCE.md)
3. **Constellation Framework**: [docs/CONSTELLATION_FRAMEWORK_GUIDE.md](CONSTELLATION_FRAMEWORK_GUIDE.md)
4. **MΛTRIZ Cognitive Engine**: [MATRIZ/README.md](../MATRIZ/README.md)

### Try Advanced Features

- **Multi-Brain Symphony**: Consensus decision-making across specialized brains
- **Adaptive Calibration**: Bayesian confidence with <0.01 ECE
- **Audit Trails**: Complete decision traceability
- **Quantum-Inspired Processing**: Superposition and entanglement patterns

### Join the Community

- **Documentation**: [https://lukhas.ai/docs](https://lukhas.ai/docs)
- **Discord**: [https://discord.gg/lukhas-ai](https://discord.gg/lukhas-ai)
- **GitHub Issues**: [https://github.com/LukhasAI/Lukhas/issues](https://github.com/LukhasAI/Lukhas/issues)

## 🎓 Learning Path

**Week 1**: Installation + Basic Usage
- ✅ Install and verify
- ✅ Run first consciousness check
- ✅ Explore lane system

**Week 2**: Core Concepts
- ✅ Understand Constellation Framework
- ✅ Work with MΛTRIZ pipeline
- ✅ Guardian system basics

**Week 3**: Advanced Features
- ✅ Multi-brain symphony
- ✅ Confidence calibration
- ✅ Audit trail analysis

**Week 4**: Integration
- ✅ Build custom consciousness module
- ✅ Integrate with your application
- ✅ Deploy to production

---

**Built with LUKHAS AI** - The future of verifiable, adaptive intelligence
🧠 Consciousness-Aware • 🎯 0.01% Error Standard • 🛡️ Ethically Bounded
