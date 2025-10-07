---
status: wip
type: documentation
owner: unknown
module: development
redirect: false
moved_to: null
---

# CANDIDATE Domain Deep Dive Analysis
## Primary AGI Development Hub (467MB, 2,877 Python files)

### 🧠 Module Dependency Graph

```
CANDIDATE Domain Architecture
═══════════════════════════════

    ┌─────────────────────────────────────────────────────────────┐
    │                    aka_qualia/                               │
    │                Consciousness Core                           │
    │  ┌─────────────────────────────────────────────────────┐    │
    │  │ core.py ←→ models.py ←→ memory.py ←→ metrics.py     │    │
    │  │    ↓           ↓           ↓           ↓            │    │
    │  │ pls.py ←→ teq_hook.py ←→ glyphs.py ←→ palette.py   │    │
    │  │    ↓           ↓           ↓           ↓            │    │
    │  │ router_client.py ←→ vivox_integration.py           │    │
    │  │    ↓           ↓                                   │    │
    │  │ regulation.py ←→ oneiric_hook.py                   │    │
    │  └─────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────┘
                              │
                              ↓
    ┌─────────────────────────────────────────────────────────────┐
    │                     core/ (193 dirs)                        │
    │            Massive Component Ecosystem                      │
    │                                                             │
    │  orchestration/ (266 files)  interfaces/ (190 files)      │
    │         │                           │                      │
    │         ├── agent_orchestrator.py   ├── adaptive_enhancements.py │
    │         ├── base.py                 ├── api/ (v1, v2, grpc)      │
    │         └── agents/                 └── README_interfaces.md     │
    │                                                             │
    │  symbolic/ (71 files)        identity/ (17 files)         │
    │         │                           │                      │
    │         ├── EthicalAuditor.py       ├── lambda_id_core.py  │
    │         ├── SymbolicReasoning.py    └── core/              │
    │         └── bio_hub.py                                     │
    │                                                             │
    │  consciousness/ (12 files)   memory/ governance/ (9 files)│
    │         │                           │                      │
    │         └── reasoning/              └── ethics/            │
    └─────────────────────────────────────────────────────────────┘
                              │
                              ↓
    ┌─────────────────────────────────────────────────────────────┐
    │               Constellation Framework Integration                  │
    │                                                             │
    │  consciousness/ ←→ memory/ ←→ identity/                    │
    │       │              │           │                         │
    │       │              │           └── governance/           │
    │       │              │                   │                 │
    │       │              └── emotional/      └── consent/      │
    │       │                                                    │
    │       └── states/ ←→ reasoning/ ←→ systems/               │
    └─────────────────────────────────────────────────────────────┘
```

### 🎯 Key Abstractions List

#### **1. AkaQualia Core (`aka_qualia/core.py`)**
- **Primary Class**: `AkaQualia` - Phenomenological control loop
- **Key Methods**: `step()`, `process_signals()`, `regulate_ethics()`
- **Dependencies**: PLS, TEQGuardian, GlyphMapper, RouterClient, Memory

#### **2. Consciousness Processing**
- **ProtoQualia**: Consciousness state representation
- **PhenomenalScene**: Environmental awareness container
- **PhenomenalGlyph**: Symbolic consciousness encoding
- **TEQGuardian**: Ethics regulation system
- **OneiricHook**: Dream state processing

#### **3. Memory Systems (`memory.py`, `memory_sql.py`)**
- **AkaqMemory**: Abstract memory interface
- **MemoryClient**: Concrete memory implementation
- **FoldSystem**: Memory organization structure
- **EmotionalMemory**: Affective memory storage

#### **4. Orchestration Layer (`core/orchestration/`)**
- **AgentOrchestrator**: Multi-agent coordination (24KB file)
- **Base**: Foundational orchestration patterns
- **APIs**: External service integration points

#### **5. Interface Systems (`core/interfaces/`)**
- **AdaptiveEnhancements**: Dynamic system improvements
- **API Versions**: v1, v2, gRPC protocol implementations
- **InterfaceTrace**: 224KB documentation of all interfaces

#### **6. Symbolic Processing (`core/symbolic/`)**
- **EthicalAuditor**: Moral reasoning validation (20KB)
- **SymbolicReasoning**: Abstract concept processing
- **BioHub**: Biological pattern integration

### 🔗 Integration Points Map

#### **Constellation Framework Connections**
```
candidate/consciousness/ ┌──────────────────────────────────┐
                        │  OpenAI Consciousness Adapter    │
                        │  Advanced Consciousness Engine   │
                        │  Dream-Emotion Bridge            │
                        └──────────────────────────────────┘
                                         │
                                         ↓
candidate/memory/       ┌──────────────────────────────────┐
                        │  Multimodal Memory Integration   │
                        │  OpenAI Memory Adapter           │
                        │  Base Manager                    │
                        └──────────────────────────────────┘
                                         │
                                         ↓
candidate/identity/     ┌──────────────────────────────────┐
                        │  Lambda ID Core                  │
                        │  Tier-Aware Swarm Hub            │
                        │  Identity Event Publisher        │
                        └──────────────────────────────────┘
```

#### **External System Bridges**
- **RouterClient**: External AI model orchestration
- **VivoxIntegration**: Real-time communication systems
- **PrometheusExporter**: Monitoring and observability
- **LukhasMetrics**: Performance measurement

#### **Data Flow Patterns**
```
Input Signals → AkaQualia.step() → ProtoQualia Generation →
Ethics Validation → Memory Storage → Glyph Mapping →
Router Orchestration → Output Actions
```

### 🏗️ Context Boundaries

#### **Tier 1 Boundaries** (Critical Systems)
```
candidate/aka_qualia/.claude.md
  Purpose: Consciousness core development
  Context: Phenomenological processing, qualia generation
  
candidate/core/orchestration/.claude.md  
  Purpose: Multi-agent coordination
  Context: Workflow management, service orchestration

candidate/core/interfaces/.claude.md
  Purpose: System integration points
  Context: API definitions, protocol implementations
```

#### **Tier 2 Boundaries** (Domain Boundaries)
```
candidate/consciousness/.claude.md
  Purpose: Consciousness architecture development
  Context: Awareness systems, decision-making processes

candidate/memory/.claude.md
  Purpose: Memory system development  
  Context: Storage, retrieval, emotional memory

candidate/identity/.claude.md
  Purpose: Identity management systems
  Context: Authentication, authorization, governance
```

#### **Tier 3 Boundaries** (Specialized Systems)
```
candidate/core/symbolic/.claude.md
  Purpose: Symbolic reasoning development
  Context: Abstract processing, ethical auditing

candidate/governance/.claude.md
  Purpose: Ethics and compliance systems
  Context: Policy enforcement, regulation validation
```

### 📊 Architecture Insights

#### **1. Consciousness-Centric Design**
- `aka_qualia/` serves as the phenomenological processing core
- 43KB `core.py` indicates sophisticated consciousness modeling
- Integration with ethics (TEQ), memory, and routing systems

#### **2. Massive Component Ecosystem**
- `core/` contains 193 subdirectories with 1,029+ Python files
- Orchestration and interfaces dominate with 456 files combined
- Suggests enterprise-scale, production-ready architecture

#### **3. Constellation Framework Implementation**
- Consciousness/Memory/Identity triad implemented across multiple modules
- Cross-references show tight integration between domains
- Dream-emotion bridging indicates advanced affective processing

#### **4. Production Readiness**
- Monitoring (Prometheus), observability, metrics collection
- Router client for external AI orchestration
- Regulation and ethics validation systems

#### **5. Symbolic-Biological Fusion**
- `symbolic/` and `bio/` integration points
- Bio-hub connecting biological patterns to symbolic processing
- Quantum-bio consciousness components

### 🎯 Development Priorities

1. **Consciousness Core**: aka_qualia/ phenomenological processing
2. **Orchestration**: Multi-agent coordination and workflow management  
3. **Interfaces**: API definitions and external integrations
4. **Symbolic**: Abstract reasoning and ethical auditing systems
5. **Constellation Integration**: Consciousness-Memory-Identity coordination

*Analysis Date: 2025-09-12*
*Files Analyzed: 2,877 Python files across 193+ subdirectories*