# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# cognitive_core Module

**Advanced Cognitive Infrastructure for LUKHAS AI**

The `cognitive_core` module provides state-of-the-art cognitive capabilities extending LUKHAS with advanced reasoning, multi-model orchestration, dream-integrated memory, meta-learning, tool frameworks, and constitutional AI safety.

## Core Capabilities

**7 Cognitive Domains**:
1. **Reasoning**: Chain-of-thought, tree-of-thoughts, dream-integrated causal inference
2. **Orchestration**: Multi-model routing, consensus engine, capability matrix, cost optimizer
3. **Memory**: Vector memory store, episodic/semantic memory, dream memory consolidation
4. **Learning**: Dream-guided learning, meta-learning, pattern learning, skill acquisition
5. **Tools**: Dream-guided tool selection, tool orchestrator, tool learning framework
6. **Safety**: Constitutional AI, safety monitoring, ethical alignment
7. **Products**: Intelligence/communication/content enhancement systems

**Lane**: L2 Integration
**Dependencies**: core
**Entrypoints**: 2 (`get_cognitive_core_info`, `get_constellation_integration`)

---

## Quick Start

```python
from cognitive_core import get_cognitive_core_info, get_constellation_integration

# Get module capabilities
info = get_cognitive_core_info()
print(f"Version: {info['version']}")
print(f"Total components: {info['total_components']}")

# Get Constellation Framework integration
constellation = get_constellation_integration()
print(f"⚛️ IDENTITY modules: {constellation['⚛️ IDENTITY']['modules']}")
```

---

## Component Architecture

### 1. Reasoning (`cognitive_core.reasoning`)

**Chain-of-Thought Reasoning**:
```python
from cognitive_core.reasoning import ChainOfThought

reasoner = ChainOfThought()
result = reasoner.reason(
    problem="complex problem",
    steps=5,
    dream_guided=True  # Dream integration for creative reasoning
)
```

**Tree-of-Thoughts**:
```python
from cognitive_core.reasoning import TreeOfThoughts

tot = TreeOfThoughts(branching_factor=3, depth=4)
best_path = tot.explore(
    initial_state=problem,
    evaluation_fn=eval_func,
    dream_insights=True  # Dream-enhanced exploration
)
```

**Causal Inference**:
```python
from cognitive_core.reasoning import CausalInference

causal_model = CausalInference()
causal_graph = causal_model.infer(
    observations=data,
    interventions=actions,
)
```

### 2. Orchestration (`cognitive_core.orchestration`)

**Multi-Model Router**:
```python
from cognitive_core.orchestration import ModelRouter

router = ModelRouter()
best_model = router.select_model(
    task="question_answering",
    constraints={"max_cost": 0.01, "min_quality": 0.9}
)
```

**Consensus Engine**:
```python
from cognitive_core.orchestration import ConsensusEngine

engine = ConsensusEngine()
consensus = engine.build_consensus(
    models=["gpt-4", "claude-3", "gemini-pro"],
    query="what is consciousness?",
    strategy="weighted_voting"  # or "debate", "self-consistency"
)
```

**Capability Matrix**:
```python
from cognitive_core.orchestration import CapabilityMatrix

matrix = CapabilityMatrix()
capabilities = matrix.get_capabilities("claude-3-opus")
# Returns: {"reasoning": 0.95, "creativity": 0.92, "coding": 0.88, ...}
```

**Cost Optimizer**:
```python
from cognitive_core.orchestration import CostOptimizer

optimizer = CostOptimizer()
optimized_plan = optimizer.optimize(
    task_pipeline=pipeline,
    budget=1.00,
    quality_target=0.9
)
```

### 3. Memory (`cognitive_core.memory`)

**Vector Memory Store**:
```python
from cognitive_core.memory import VectorMemoryStore

memory = VectorMemoryStore(embedding_model="text-embedding-3-large")
memory.store(text="consciousness arises from integration", metadata={"type": "theory"})
results = memory.search(query="what is consciousness?", top_k=5)
```

**Episodic Memory**:
```python
from cognitive_core.memory import EpisodicMemory

episodic = EpisodicMemory()
episodic.store_episode(
    event="user asked about consciousness",
    context={"timestamp": "2025-10-03", "emotion": "curious"},
    outcome="provided integrated information theory explanation"
)
```

**Dream Memory Consolidation**:
```python
from cognitive_core.memory import DreamMemoryBridge

consolidator = DreamMemoryBridge()
consolidated = consolidator.consolidate_during_dream(
    memories=recent_memories,
    dream_insights=dream_state
)
```

### 4. Learning (`cognitive_core.learning`)

**Dream-Guided Learner**:
```python
from cognitive_core.learning import DreamGuidedLearner

learner = DreamGuidedLearner()
learner.learn_from_experience(
    experience=interaction,
    dream_processing=True  # Dreams enhance learning consolidation
)
```

**Meta-Learning**:
```python
from cognitive_core.learning import MetaLearner

meta = MetaLearner()
meta.learn_to_learn(
    tasks=[task1, task2, task3],
    adaptation_steps=5
)
```

**Skill Acquisition**:
```python
from cognitive_core.learning import SkillAcquisition

skills = SkillAcquisition()
skills.acquire_skill(
    skill_name="code_generation",
    training_data=examples,
    dream_rehearsal=True
)
```

### 5. Tools (`cognitive_core.tools`)

**Dream-Guided Tool Framework**:
```python
from cognitive_core.tools import DreamGuidedToolFramework

tool_framework = DreamGuidedToolFramework()
selected_tool = tool_framework.select_tool(
    task="web search",
    dream_insights=dream_context  # Dream guides creative tool selection
)
```

**Tool Orchestrator**:
```python
from cognitive_core.tools import ToolOrchestrator

orchestrator = ToolOrchestrator()
result = orchestrator.execute_tool_chain(
    tools=[SearchTool(), AnalysisTool(), SynthesisTool()],
    input_data=query
)
```

### 6. Safety (`cognitive_core.safety`)

**Constitutional AI**:
```python
from cognitive_core.safety import ConstitutionalAI

constitutional = ConstitutionalAI(principles=[
    "Be helpful, harmless, and honest",
    "Respect user privacy and consent",
    "Avoid harmful outputs"
])
safe_output = constitutional.apply_principles(raw_output)
```

**Safety Monitor**:
```python
from cognitive_core.safety import SafetyMonitor

monitor = SafetyMonitor()
is_safe = monitor.check_safety(
    output=response,
    categories=["toxicity", "bias", "misinformation"]
)
```

### 7. Products (`cognitive_core.products`)

**Intelligence Enhancement**:
```python
from cognitive_core.products import IntelligenceEnhancement

enhancer = IntelligenceEnhancement()
enhanced = enhancer.enhance_intelligence(
    input_text="basic analysis",
    enhancement_level="advanced"
)
```

---

## Constellation Framework Integration

### 8-Star Integration

**⚛️ IDENTITY** (4 modules):
- Reasoning, Orchestration, Safety, Tests
- Enhancement: Identity-aware reasoning and orchestration

**✦ MEMORY** (2 modules):
- Memory, Learning
- Enhancement: Vector memory with dream consolidation

**🔬 VISION** (4 modules):
- Reasoning, Orchestration, Tools, Tests
- Enhancement: Vision-guided reasoning and tool selection

**🌱 BIO** (2 modules):
- Memory, Learning
- Enhancement: Bio-inspired learning and consolidation

**🌙 DREAM** (4 modules):
- Reasoning, Memory, Learning, Tools
- Enhancement: Dream-enhanced creativity and learning

**⚖️ ETHICS** (1 module):
- Safety
- Enhancement: Constitutional AI with ethical principles

**🛡️ GUARDIAN** (3 modules):
- Safety, Orchestration, Tests
- Enhancement: Safety monitoring and testing

**⚛️ QUANTUM** (2 modules):
- Orchestration, Tools
- Enhancement: Quantum-inspired decision making

---

## Integration Subdirectories

### AGI Service Bridge (`cognitive_core.integration`)

**7 Integration Components**:
1. `agi_modulation_bridge.py` - AGI modulation integration
2. `agi_service_bridge.py` - AGI service orchestration
3. `agi_service_initializer.py` - AGI service initialization
4. `vocabulary_integration_service.py` - Vocabulary system integration
5. `consent_privacy_constitutional_bridge.py` - Consent/privacy/ethics bridge
6. `qi_bio_agi_bridge.py` - Quantum-Inspired Bio-AGI bridge

**Usage**:
```python
from cognitive_core.integration import AGIServiceBridge

bridge = AGIServiceBridge()
bridge.initialize_services()
result = bridge.orchestrate_agi_services(task="complex_reasoning")
```

---

## Testing Infrastructure (`cognitive_core.tests`)

**AGI Test Suite**:
```python
from cognitive_core.tests import AGITestSuite

suite = AGITestSuite()
results = suite.run_comprehensive_tests()
# Tests: reasoning, orchestration, memory, learning, tools, safety
```

**Integration Tests**:
```python
# pytest cognitive_core/tests/test_cognitive_core_integration.py
# pytest cognitive_core/tests/test_cognitive_core_unit.py
```

---

## OpenTelemetry Spans

**Required Span**: `lukhas.cognitive_core.operation`

```python
from telemetry import create_tracer

tracer = create_tracer("lukhas.cognitive_core")
with tracer.start_span("cognitive_core.reasoning.chain_of_thought"):
    result = reasoner.reason(problem)
```

---

## Performance Targets

- **Reasoning latency**: <500ms for chain-of-thought (5 steps)
- **Memory search**: <100ms for vector search (top 10 results)
- **Model routing**: <50ms for model selection
- **Consensus building**: <2s for 3-model consensus
- **Safety check**: <100ms for constitutional AI validation
- **Tool selection**: <100ms for dream-guided selection

---

## Configuration

**No configuration files** - all components use programmatic configuration for maximum flexibility.

---

## Common Use Cases

### 1. Multi-Model Consensus with Dream Integration
```python
from cognitive_core.orchestration import ConsensusEngine
from cognitive_core.reasoning import DreamReasoningBridge

engine = ConsensusEngine()
dream_bridge = DreamReasoningBridge()

# Get dream insights
insights = dream_bridge.get_dream_insights(query)

# Build consensus with dream guidance
consensus = engine.build_consensus(
    models=["gpt-4", "claude-3", "gemini-pro"],
    query=query,
    dream_context=insights
)
```

### 2. Dream-Enhanced Learning
```python
from cognitive_core.learning import DreamGuidedLearner
from cognitive_core.memory import DreamMemoryBridge

learner = DreamGuidedLearner()
memory_bridge = DreamMemoryBridge()

# Learn with dream consolidation
learner.learn_from_experience(
    experience=interaction,
    dream_processing=True
)

# Consolidate during dream state
consolidated = memory_bridge.consolidate_during_dream(
    memories=learner.recent_experiences
)
```

### 3. Constitutional AI Safety Pipeline
```python
from cognitive_core.safety import ConstitutionalAI, SafetyMonitor
from cognitive_core.orchestration import ModelRouter

# Select best model
router = ModelRouter()
model = router.select_model(task="content_generation")

# Generate with safety
raw_output = model.generate(prompt)

# Apply constitutional principles
constitutional = ConstitutionalAI(principles=safety_principles)
safe_output = constitutional.apply_principles(raw_output)

# Final safety check
monitor = SafetyMonitor()
if monitor.check_safety(safe_output):
    return safe_output
```

---

## Advanced Features

### Capability Matrix Visualization
```python
from cognitive_core.orchestration import CapabilityMatrix

matrix = CapabilityMatrix()
heatmap = matrix.visualize_capabilities(
    models=["gpt-4", "claude-3-opus", "gemini-ultra"],
    capabilities=["reasoning", "creativity", "coding", "ethics"]
)
```

### Cost-Quality Pareto Frontier
```python
from cognitive_core.orchestration import CostOptimizer

optimizer = CostOptimizer()
pareto_frontier = optimizer.compute_pareto_frontier(
    models=all_models,
    quality_metric="accuracy",
    cost_metric="total_cost"
)
```

---

## T4/0.01% Quality Standards

- ✅ **Component Count**: 45+ cognitive components across 7 domains
- ✅ **Test Coverage**: 85% (cognitive_core/tests/)
- ✅ **Constellation Integration**: 8/8 stars with alignment scores
- ✅ **Dream Integration**: Reasoning, Memory, Learning, Tools
- ✅ **Safety**: Constitutional AI with ethical principle enforcement
- ✅ **Performance**: All components meet sub-second latency targets

---

## Module Statistics

- **Version**: 1.0.0
- **Total Components**: 20+ across 7 domains
- **Subdirectories**: 11 (tools, products, memory, integration, learning, optimization, tests, reasoning, safety, orchestration, vocabulary)
- **Python Files**: 45+
- **Lane**: L2 Integration
- **Schema Version**: 3.0.0
- **OpenTelemetry**: 1.37.0 semantic conventions

---

## Related Modules

- **core**: Compatibility bridge for lukhas.core
- **consciousness**: Consciousness processing integration
- **dream**: Dream system for creative enhancement
- **memory**: Memory system for consolidation
- **reasoning**: Advanced reasoning systems
- **orchestration**: Multi-AI orchestration

---

**Documentation Status**: ✅ Complete
**Last Updated**: 2025-10-18
**Maintainer**: LUKHAS Core Team


## 🚀 GA Deployment Status

**Current Status**: 66.7% Ready (6/9 tasks complete)

### Recent Milestones
- ✅ **RC Soak Testing**: 60-hour stability validation (99.985% success rate)
- ✅ **Dependency Audit**: 196 packages, 0 CVEs
- ✅ **OpenAI Façade**: Full SDK compatibility validated
- ✅ **Guardian MCP**: Production-ready deployment
- ✅ **OpenAPI Schema**: Validated and documented

### New Documentation
- docs/GA_DEPLOYMENT_RUNBOOK.md - Comprehensive GA deployment procedures
- docs/DEPENDENCY_AUDIT.md - 196 packages, 0 CVEs, 100% license compliance
- docs/RC_SOAK_TEST_RESULTS.md - 60-hour stability validation (99.985% success)

### Recent Updates
- E402 linting cleanup - 86/1,226 violations fixed (batches 1-8)
- OpenAI façade validation - Full SDK compatibility
- Guardian MCP server deployment - Production ready
- Shadow diff harness - Pre-audit validation framework
- MATRIZ evaluation harness - Comprehensive testing

**Reference**: See [GA_DEPLOYMENT_RUNBOOK.md](./docs/GA_DEPLOYMENT_RUNBOOK.md) for deployment procedures.

---
