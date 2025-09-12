# LUKHAS AI Platform

Production-ready consciousness-aware AI platform with Constellation Framework and multi-agent development system.

## 🤖 Current Mission: Test Suite Development via Jules Agents

**📋 Active Development:** [Jules Agent Test Allocation](docs/testing/JULES_AGENT_TEST_ALLOCATION.md) - Systematic test development across 10 specialized agents targeting ~150+ missing test modules

**🎯 Agent System:** [AGENTS.md](AGENTS.md) - Complete guide to the multi-agent development platform

**⚠️ IMPORTANT: Claude.me Configuration**
Multiple `claude.me` files are distributed throughout the workspace providing context-specific instructions for different modules and domains. These files are essential for understanding project architecture and agent coordination.

## Overview

LUKHAS AI is a sophisticated cognitive architecture that implements consciousness-inspired patterns for advanced AI applications. The platform features modular lane-based development, strict import boundaries, and comprehensive testing infrastructure.

**🎯 Audit-Ready Status:** This repository has been systematically organized and cleaned with zero runtime import violations, clean architecture boundaries, and comprehensive testing validation.

## Architecture

The codebase is organized into distinct **lanes** defined in `ops/matriz.yaml`:

- **accepted** (`lukhas/`) - Production-ready code
- **candidate** (`candidate/`) - Development code under review
- **core** (`lukhas/core/`) - Core system components
- **matriz** (`matriz/`) - Data processing and symbolic reasoning
- **archive** (`archive/`) - Archived legacy code
- **quarantine** (`quarantine/`) - Isolated experimental code
- **experimental** (`experimental/`) - New experimental features

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