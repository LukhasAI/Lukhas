# LUKHAS Agent Coordination System
**Status**: Active | **Updated**: 2025-10-15 | **Schema**: 3.0 (Generic - Matriz & Navigation Focus)

---

## Overview

The LUKHAS Agent Coordination System provides **AI agent navigation guidance** for working with the LUKHAS codebase, with special emphasis on **MATRIZ cognitive engine** integration and **repository structure understanding**.

**Core Principles**:
- **Context first**: Always read domain `claude.me` files before editing
- **Lane discipline**: Respect import boundaries (candidate → core → lukhas)
- **MATRIZ integration**: Understand symbolic reasoning & node-based processing
- **Verification**: Test changes, validate against architectural contracts
- **Minimal noise**: Clean commits, evidence-based claims

---

## Repository Navigation

### 🗺️ Context File System (42+ Distributed)

**Every major directory has domain-specific context files** providing architecture, patterns, and integration guidance.

#### **Primary Navigation Entry Point**
- **Master Context**: [`claude.me`](./claude.me) - Complete system architecture overview
  - 7,000+ Python files across 133 root directories
  - Constellation Framework (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum)
  - Lane-based evolution (candidate → core → lukhas → products)

#### **Core Development Lanes**

**CANDIDATE Lane** (Development & Research - 2,877 files)
- [`candidate/claude.me`](./candidate/claude.me) - Development workspace overview
- [`candidate/consciousness/claude.me`](./candidate/consciousness/claude.me) - Consciousness systems (52+ components)
- [`candidate/core/claude.me`](./candidate/core/claude.me) - Core prototypes (193 subdirectories)
- [`candidate/governance/claude.me`](./candidate/governance/claude.me) - Guardian & ethics development
- [`candidate/memory/claude.me`](./candidate/memory/claude.me) - Memory systems & fold architecture
- [`candidate/identity/claude.me`](./candidate/identity/claude.me) - ΛiD authentication development

**LUKHAS Lane** (Integration & Coordination - 692 components)
- [`lukhas/claude.me`](./lukhas/claude.me) - Constellation Framework integration hub
- [`lukhas/consciousness/claude.me`](./lukhas/consciousness/claude.me) - Consciousness integration
- [`lukhas/memory/claude.me`](./lukhas/memory/claude.me) - Memory integration & fold systems
- [`lukhas/identity/claude.me`](./lukhas/identity/claude.me) - Identity integration & auth services
- [`lukhas/governance/claude.me`](./lukhas/governance/claude.me) - Governance integration
- [`lukhas/core/claude.me`](./lukhas/core/claude.me) - Core integration systems

**PRODUCTS Lane** (Production Deployment - 4,093 files)
- [`products/claude.me`](./products/claude.me) - Production deployment hub
- [`products/enterprise/claude.me`](./products/enterprise/claude.me) - Enterprise systems
- [`products/intelligence/claude.me`](./products/intelligence/claude.me) - Intelligence & analytics
- [`products/experience/claude.me`](./products/experience/claude.me) - User experience systems

#### **Foundation Systems**

**MATRIZ Cognitive Engine** (20 Python files + 16K assets)
- [`matriz/claude.me`](./matriz/claude.me) - **CRITICAL**: Symbolic reasoning & node orchestration
- [`matriz/core/claude.me`](./matriz/core/claude.me) - Node orchestration, memory systems, interfaces
- [`matriz/visualization/claude.me`](./matriz/visualization/claude.me) - Graph visualization & interactive demos

**Research & Ethics**
- [`consciousness/claude.me`](./consciousness/claude.me) - Consciousness research foundations
- [`memory/claude.me`](./memory/claude.me) - Memory protection & sanctum vault
- [`identity/claude.me`](./identity/claude.me) - Lambda ID foundation
- [`ethics/claude.me`](./ethics/claude.me) - Ethics framework (33+ components)
- [`ethics/guardian/claude.me`](./ethics/guardian/claude.me) - Guardian systems & constitutional AI

---

## 🧬 MATRIZ Cognitive Engine - Agent Guide

### Architecture Overview

**MATRIZ implements "Cognitive DNA"** - every thought becomes a traceable, governed, evolvable node.

```
Every Operation → MATRIZ Node → Reasoning Chain → Provenance Tracking
      │               │              │                │
  User Input    → Node Creation → Causal Links → Decision Audit
  Processing    → Memory Storage → Temporal Link → Learning Loop
  Decision      → Node Network  → Semantic Link → Evolution
```

### Core Components

**Node System** (`matriz/core/`)
- **CognitiveOrchestrator**: Main processing coordinator with NodeRegistry and QueryProcessor
- **BaseNode**: Abstract foundation for all cognitive processing
- **CognitiveMemory**: Persistent thought storage with temporal/causal links

**Specialized Nodes** (`matriz/nodes/`)
- **MathNode**: Arithmetic operations with reasoning traces
- **FactNode**: Knowledge base with semantic linking
- **ValidatorNode**: Rule-based validation with reasoning explanation

**Reasoning Chains** (`matriz/traces_router.py`)
- **TraceRouter**: Complete reasoning path capture (11KB)
- **ProvenanceTracker**: Decision origin tracking
- **ReasoningPath**: Step-by-step thought reconstruction

**Visualization** (`matriz/visualization/`)
- **NetworkRenderer**: Real-time node visualization
- **Interactive Demo**: 4.8MB HTML with embedded cognitive visualizations
- **16,042 frontend assets**: Complete JavaScript framework for rich interactions

### Integration Patterns

**LUKHAS Memory Bridge**
```
LUKHAS Memory ↔ MATRIZ Nodes ↔ Symbolic Reasoning
       │              │                │
  Fold System   → Node Memory    → Reasoning Chains
  Consciousness → Node Network   → Causal Processing
  Integration   → Provenance     → Decision Tracking
```

**CANDIDATE Symbolic Bridge**
```
CANDIDATE Symbolic → MATRIZ Processing → Integrated Reasoning
        │                  │                    │
  EthicalAuditor    → ValidationNode    → Ethics Reasoning
  SymbolicReasoning → MathNode/FactNode → Logical Processing
  BioHub           → CustomNodes       → Biological Patterns
```

### Development Workflow

**Custom Node Creation**
1. Inherit `BaseNode` from `matriz/core/node_interface.py`
2. Define capabilities, constraints, and interfaces
3. Implement processing logic with provenance tracking
4. Register dynamically via `CognitiveOrchestrator`
5. Test integration with LUKHAS and CANDIDATE

**Reasoning Chain Development**
1. Analyze query requirements
2. Select appropriate nodes via `QueryProcessor`
3. Coordinate multi-node processing
4. Integrate results with conflict resolution
5. Track provenance via `TraceRouter`
6. Optimize chain performance

---

## Lane-Based Import Rules

### Critical Boundaries

**LUKHAS Lane** (Production)
- ✅ Can import: `core/`, `matriz/`, `universal_language/`
- ❌ Cannot import: `candidate/` (strict isolation)
- **Validate**: `make lane-guard`

**CANDIDATE Lane** (Development)
- ✅ Can import: `core/`, `matriz/` ONLY
- ❌ Cannot import: `lukhas/` (no production deps)
- **Purpose**: Research & prototyping isolation

**CORE Lane** (Integration - 253 files)
- ✅ Shared components for candidate/lukhas integration
- **Purpose**: Battle-tested integration layer

### Lane Promotion Workflow

```
CANDIDATE (research) → CORE (integration) → LUKHAS (production) → PRODUCTS (deployment)
     │                      │                     │                      │
Prototyping  →        Testing &        →    Constellation    →    Enterprise
Iteration    →        Validation       →    Integration      →    Scaling
Innovation   →        Coordination     →    Monitoring       →    Compliance
```

**Promotion Criteria**:
- 75%+ test coverage
- No circular import issues
- Guardian alignment validated
- Lane boundary compliance
- Performance benchmarks met

---

## Development Commands

### Navigation & Discovery

```bash
# Find context files
find . -name "claude.me" | head -20

# Search for specific patterns
make grep PATTERN="CognitiveOrchestrator"
make glob PATTERN="**/matriz/**/*.py"

# Lane boundary validation
make lane-guard
make imports-guard
```

### MATRIZ Development

```bash
# MATRIZ smoke tests (deterministic golden fixture)
make smoke-matriz

# Interactive visualization
cd matriz/visualization
python graph_viewer.py

# API server (RESTful node access)
uvicorn matriz.interfaces.api_server:app --reload --port 8001
```

### System Health

```bash
# Quick health check
make doctor              # Comprehensive diagnostics
make smoke              # Basic smoke tests (15 tests)
make smoke-matriz       # MATRIZ traces smoke test

# Comprehensive testing
make test-tier1         # Critical system tests
make test-all           # Full test suite (775+ tests)
pytest tests/smoke/     # Smoke test suite
pytest tests/unit/      # Component tests
```

### Code Quality

```bash
# Linting & formatting
make lint              # Run linting and type checking
make lint-unused       # T4 unused imports system
make format            # Format code with Black
make fix               # Fix auto-fixable issues

# Security & validation
make security-scan     # Security validation
make audit             # Comprehensive system audit
```

### Development Workflows

```bash
# Fresh setup
make bootstrap         # Complete environment setup
make dev               # Start development server
make api               # Start API server (port 8000)

# OpenAPI façade
make openapi-spec      # Generate OpenAPI spec
make openapi-validate  # Validate spec
make facade-smoke      # Run OpenAI façade smoke tests
```

---

## Agent Workflow Patterns

### Before Starting Work

1. **Read Master Context**: Start with [`claude.me`](./claude.me)
2. **Read Domain Context**: Navigate to specific `{domain}/claude.me`
3. **Check Lane Boundaries**: Understand import restrictions
4. **Review MATRIZ Integration**: If cognitive processing involved, read [`matriz/claude.me`](./matriz/claude.me)
5. **Run System Health**: `make doctor && make smoke`

### During Development

1. **Atomic Changes**: Small, focused commits with clear intent
2. **Test First**: Write/update tests before implementation
3. **Validate Continuously**: Run `make lint && make test-fast`
4. **Respect Boundaries**: Never cross lane import barriers
5. **Document Decisions**: Update relevant context files

### After Changes

1. **Run Full Tests**: `make test-tier1` or `make test-all`
2. **Check Coverage**: Maintain 75%+ for production promotion
3. **Validate Imports**: `make lane-guard && make imports-guard`
4. **Update Context**: Reflect architectural changes in `claude.me` files
5. **Clean Commit**: Follow T4 commit message standards

---

## Commit Message Standards (T4)

### Format

```
<type>(<scope>): <imperative subject ≤72>

<optional body with Problem/Solution/Impact bullets>

<optional trailers: Closes, Security-Impact, LLM>
```

### Types & Scopes

**Types**: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|security

**Scopes**: core|matriz|identity|memory|glyph|api|orchestration|governance|consciousness|interfaces|monitoring|tools|ops|serve|lanes|hygiene|docs

### Examples

✅ **Good**:
- `fix(matriz): resolve node registration race condition in CognitiveOrchestrator`
- `feat(consciousness): add Dream EXPAND++ resonance field module`
- `docs(agents): update MATRIZ navigation guide with node development patterns`

❌ **Bad**:
- `BREAKTHROUGH: AMAZING MATRIZ UPGRADE!!!` (hype, punctuation spam)
- `fix stuff.` (vague, ends with period)
- `Update files` (not imperative, no scope)

---

## Quick Reference

### Key Directories

```
/Users/agi_dev/LOCAL-REPOS/Lukhas/
├── matriz/                 # Cognitive DNA engine (20 files + 16K assets)
├── candidate/              # Development lane (2,877 files)
├── lukhas/                 # Production lane (692 components)
├── core/                   # Integration components (253 files)
├── products/               # Production deployment (4,093 files)
├── tests/                  # Test suites (775+ tests)
├── docs/                   # Documentation
├── scripts/                # Automation scripts
└── tools/                  # Development tools
```

### Essential Make Targets

```bash
make help              # Auto-generated target discovery (50+ targets)
make doctor            # System health diagnostics
make smoke             # Quick smoke tests
make smoke-matriz      # MATRIZ traces smoke test
make lane-guard        # Validate import boundaries
make test-tier1        # Critical system tests
make lint              # Linting & type checking
make format            # Code formatting
make audit             # Comprehensive audit
```

### Context Navigation

- **New to LUKHAS?** → Start with [`claude.me`](./claude.me)
- **MATRIZ work?** → Read [`matriz/claude.me`](./matriz/claude.me)
- **Consciousness?** → Check [`candidate/consciousness/claude.me`](./candidate/consciousness/claude.me)
- **Production deploy?** → See [`products/claude.me`](./products/claude.me)
- **Research docs?** → Review [`docs/THE_VAULT_RESEARCH_INTELLIGENCE.md`](./docs/THE_VAULT_RESEARCH_INTELLIGENCE.md)

---

## Success Criteria

### Code Quality

- ✅ All files compile without syntax errors
- ✅ Test coverage ≥75% for production promotion
- ✅ Lane boundaries respected (validated via `make lane-guard`)
- ✅ Import health: <5% circular issues
- ✅ Security: 0 hardcoded secrets in production code

### MATRIZ Integration

- ✅ Custom nodes inherit from `BaseNode`
- ✅ Reasoning chains tracked via `TraceRouter`
- ✅ Provenance logging for all cognitive operations
- ✅ Integration tests with LUKHAS memory adapter
- ✅ Visualization assets updated for new node types

### Documentation

- ✅ Domain `claude.me` files updated for architectural changes
- ✅ Inline docstrings for all public APIs
- ✅ Integration patterns documented
- ✅ Breaking changes highlighted in commit messages

---

## Emergency Commands

```bash
# In LUKHAS directory
make clean              # Clean build artifacts
make deep-clean         # Deep clean including caches
make emergency-bypass   # Emergency reset (use with caution)

# Health diagnostics
make doctor-strict      # Strict health check with failures
make doctor-json        # Machine-readable health report
```

---

## Links & Resources

- **Master Architecture**: [claude.me](./claude.me) - Complete system overview
- **MATRIZ Engine**: [matriz/claude.me](./matriz/claude.me) - Cognitive DNA architecture
- **Development Guide**: [docs/development/](./docs/development/) - Developer workflows
- **Research Intelligence**: [docs/THE_VAULT_RESEARCH_INTELLIGENCE.md](./docs/THE_VAULT_RESEARCH_INTELLIGENCE.md) - 604 research documents
- **Constellation Framework**: [branding/constellation/](./branding/constellation/) - Framework branding

---

**The LUKHAS Agent Coordination System provides navigation guidance for AI agents working with MATRIZ cognitive engine integration, lane-based development, and Constellation Framework architecture.**

*⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum*
