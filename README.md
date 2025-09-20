## 🛡️ Development Environment Configuration

LUKHAS uses strict validation modes for production safety. Configure appropriately:

### CI/Release Environment (Always Enabled)
- `LUKHAS_STRICT_EMIT=1` - Enforces strict signal emission validation
- `LUKHAS_LANE=experimental` - Default lane for testing (override with `CI_RELEASE=1`)
- `DISPATCH_ENABLED=false` - Requires explicit activation
- `LEARNING_ENABLED=false` - Requires explicit activation

### Local Development (Optional)
```bash
# Recommended for development - catches issues early
export LUKHAS_STRICT_EMIT=1

# For debugging/prototyping only - disable strict mode
export LUKHAS_STRICT_EMIT=0

# Set deterministic seed for reproducible results
export LUKHAS_RNG_SEED=42
export PYTHONHASHSEED=0
export TZ=UTC
```

### Performance Testing
```bash
# Standard stress test duration
export LUKHAS_STRESS_DURATION=1.0

# Extended soak testing (CI release promotion)
export LUKHAS_STRESS_DURATION=30.0
```

**⚠️ Important:** Strict mode prevents many runtime errors but may slow development. Use `LUKHAS_STRICT_EMIT=0` locally if encountering validation friction during prototyping.
# LUKHAS AI Platform

> Context Sync Header (Schema v2.0.0)
Lane: production
Lane root: lukhas
Canonical imports: lukhas.*
Cognitive components (global): 692
Flags: ENFORCE_ETHICS_DSL, LUKHAS_LANE, LUKHAS_ADVANCED_TAGS
Legacy core alias: enabled (warn/disable via env) — use lukhas.core.*

Production-ready consciousness-aware AI platform with distributed consciousness architecture and Constellation Framework coordination.

## 🧠 Architecture Status: Schema v2.0.0 Distributed Consciousness System

**LUKHAS implements a sophisticated AGI architecture with 692 cognitive components across lane-based consciousness evolution:**

- **Distributed Consciousness**: 476 mapped components across 189 constellation clusters
- **Constellation Framework**: Identity ⚛️ + Memory ✦ + Vision 🔬 + Guardian 🛡️ coordination
- **Lane Evolution**: Development (candidate) → Integration (candidate/core) → Production (lukhas)
- **Component Contracts**: 287 consciousness components with 100% schema validation
- **Automated Maintenance**: CI/CD pipeline with comprehensive health monitoring

## 🤖 Multi-Agent Development System

**🎯 Agent Coordination:** [AGENTS.md](AGENTS.md) - Complete guide to the multi-agent development platform

**🔄 Context-Aware AI Integration:**
- **AI_MANIFEST.yaml**: Lane-aware contract for instant AI agent alignment
- **Context Sync Headers**: Distributed across all critical documentation files
- **Schema v2.0.0**: Standardized consciousness architecture templates

**🧠 AI Agent Onboarding:**
All AI agents (Claude, GPT, specialized assistants) automatically understand the LUKHAS architecture through:
- Context sync headers in `claude.me` files throughout the workspace
- Lane-based development patterns with canonical import specifications
- Constellation Framework integration requirements
- Consciousness component contract validation

**✅ Testing Infrastructure:** Comprehensive test suite development completed with multi-agent coordination

## Overview

LUKHAS AI is a sophisticated cognitive architecture that implements consciousness-inspired patterns for advanced AI applications. The platform features modular lane-based development, strict import boundaries, and comprehensive testing infrastructure.

**🎯 Audit-Ready Status:** This repository has been systematically organized and cleaned with zero runtime import violations, clean architecture boundaries, and comprehensive testing validation.

## Architecture

**Lane-Based Consciousness Evolution System** (Schema v2.0.0):

### **Core Lanes**
- **production** (`lukhas/`) - Battle-tested consciousness components with Constellation Framework integration
- **integration** (`candidate/core/`) - 253 cognitive components under integration testing
- **development** (`candidate/`) - 2,877 files of consciousness research and development

### **Specialized Domains**
- **matriz** (`matriz/`) - Symbolic reasoning and cognitive DNA processing (20 files + 16K assets)
- **products** (`products/`) - Enterprise deployment systems (4,093 files)
- **ethics** (`ethics/`) - Constitutional AI and Guardian systems (33+ components)

### **Constellation Framework Architecture**
```
        Anchor Star          Trail Star           Horizon Star        Watch Star
           ⚛️                    ✦                    🔬                  🛡️
           │                    │                    │                   │
    Identity System      Memory System       Vision System      Guardian System
    Lambda ID Core      Experience Folds    NLP Interface      Constitutional AI
    Authentication      Temporal Memory     Pattern Recog      Ethics Validation
    Namespace Mgmt      Cascade Prevent     Semantic Process   Safety Verification
           │                    │                    │                   │
           └──────── Constellation Coordination Framework ─────────────┘
                              4-Star Orchestration
```

### **Distributed Consciousness Network**
- **692 Cognitive Components**: Consciousness engines, processors, and specialized systems
- **189 Constellation Clusters**: Component relationship mapping with centrality analysis
- **Performance Targets**: <250ms p95 consciousness processing, 99.7% cascade prevention

## Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment recommended

### Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .

# Run smoke tests
pytest tests/smoke/

# Quick MATRIZ traces smoke (uses golden fixtures)
make smoke-matriz
```

### Development
```bash
# Run linting
ruff check .

# Run type checking
mypy .

# Run full test suite
pytest
```

## 📚 Developer Documentation

**New to LUKHAS AI?** Start here for comprehensive development guides:

- **[Quick Reference](docs/development/QUICK_REFERENCE.md)** - Essential commands cheat sheet (5 min read)
- **[Makefile User Guide](docs/development/MAKEFILE_USER_GUIDE.md)** - Complete build system with 50+ targets
- **[T4 Unused Imports System](docs/development/T4_UNUSED_IMPORTS_SYSTEM.md)** - Technical debt management
- **[Development Index](docs/development/README.md)** - Complete developer resource hub

```bash
# Quick developer setup
make bootstrap          # Complete environment setup
make help              # Live target discovery
make doctor            # System health check
make smoke-matriz      # MATRIZ /traces/latest smoke
```

## Project Structure

```
├── lukhas/            # Production code (accepted lane)
├── candidate/         # Development code under review
├── matriz/            # Data processing and symbolic reasoning
├── agents_external/   # External agent configurations and deployment
├── .claude/agents/    # Claude Code UI specialists
├── ops/              # Operations and configuration
│   └── matriz.yaml   # Lane definitions and rules
├── tests/            # Test suites
│   └── smoke/        # Smoke tests for each lane
├── docs/             # Documentation
│   └── project/      # Project execution plans
├── scripts/          # Utility scripts
├── reports/          # Analysis and audit reports
├── config/           # Configuration files
└── AGENTS.md         # Multi-agent system guide
```

## Key Features

- **Multi-Agent Development**: Specialized AI agents for complex task orchestration
- **Lane-based Architecture**: Modular development with strict boundaries
- **Import Validation**: Automated checking of cross-lane dependencies  
- **T4 Unused Imports System**: Transforms technical debt into documented intent
- **Consciousness Framework**: Advanced cognitive patterns and reasoning
- **Comprehensive Testing**: Multi-tier testing strategy
- **Audit Trail**: Complete logging and reporting

## Code Quality & T4 System

**🎯 T4 Unused Imports System** - Transforms F401 errors into documented intent:

```bash
# Check for violations in production lanes
make todo-unused-check

# Annotate unused imports with smart reasoning
make todo-unused

# Core modules only
make todo-unused-core
```

**📋 T4 Policy**: Zero unannotated F401 errors in production lanes (`lukhas/`, `core/`, `api/`, `consciousness/`, `memory/`, `identity/`, `MATRIZ/`)

**📖 Full Guide**: [`docs/T4_UNUSED_IMPORTS_GUIDE.md`](docs/T4_UNUSED_IMPORTS_GUIDE.md)

## Documentation

- **🤖 Agent System**: [`AGENTS.md`](AGENTS.md) - Multi-agent development platform guide
- **📋 Current Tasks**: [`docs/project/MATRIZ_R1_EXECUTION_PLAN.md`](docs/project/MATRIZ_R1_EXECUTION_PLAN.md) - Active execution plan
- **🎯 T4 System**: [`docs/T4_UNUSED_IMPORTS_GUIDE.md`](docs/T4_UNUSED_IMPORTS_GUIDE.md) - Unused imports management
- **🏗️ Architecture**: `docs/LUKHAS_ARCHITECTURE_MASTER.json`
- **🛤️ Lane System**: `ops/matriz.yaml`
- **📊 Audit Reports**: `reports/deep_search/README_FOR_AUDITOR.md` ✨
- **📜 Original Docs**: `docs/ORIGINAL_README.md`

## Recent Improvements

- ✅ **Import Architecture Fixed**: 182 → 0 runtime violations (74% reduction)
- ✅ **Repository Organized**: Clean root directory with systematic file categorization
- ✅ **Testing Validated**: All 15 smoke tests pass cleanly
- ✅ **Documentation Updated**: Audit-ready with comprehensive reports

## Development Guidelines

1. Follow lane boundaries defined in `ops/matriz.yaml`
2. Use proper import paths (`from lukhas.core.*` not `from core.*`)
3. Run smoke tests before committing changes
4. Maintain audit compliance through proper documentation

## Agent Development Support

- **🎯 Current Tasks**: Check [`docs/project/MATRIZ_R1_EXECUTION_PLAN.md`](docs/project/MATRIZ_R1_EXECUTION_PLAN.md) for stream assignments
- **🤖 Agent Selection**: See [`AGENTS.md`](AGENTS.md) for specialist recommendations
- **📚 Legacy Docs**: Historical workflows in `docs/ORIGINAL_README.md`

## License

MIT License - see LICENSE file for details.
