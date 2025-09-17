## 🧪 Jules Agent Execution Protocol

Each Jules agent MUST follow this standardized workflow for every assigned module:

1. **Read Assignment**  
   - Open your allocation in [`docs/testing/JULES_AGENT_TEST_ALLOCATION.md`](docs/testing/JULES_AGENT_TEST_ALLOCATION.md).  
   - Check your `.yaml` spec file in `tests/specs/`.

2. **Setup Environment**  
   ```bash
   git fetch origin
   git checkout -b feat/tests/Jules-0X-<module>
   make bootstrap
   ```

3. **Create Tests**  
   - Place tests under `tests/unit/` or `tests/integration/` following spec.
   - Use T4 markers (`tier1`, `tier2`, etc).
   - Annotate edge cases and goldens.

4. **Local Validation**
   ```bash
   pytest -m tier1 --tb=short
   pytest --cov=lukhas --cov-report=term-missing
   ```

## 🛡️ Strict Mode Environment Variables

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

5. **Commit with Branding**  
   - Follow [`commit_standard_format.yaml`](commit_standard_format.yaml).  
   - Example:  
     ```
     test(identity): add MFA login + token expiry tests (tier1)
     ```

6. **PR Creation**  
   - Title: `test(Jules-0X): <module summary>`  
   - Body: include acceptance checklist + coverage diff.  
   - Add label: `tests-only`.

7. **Cross-Validation**
   - Before requesting a merge, run integration tests that exercise at least one other Jules agent's module, validating compatibility and identifying cross-agent issues.
   - Attach cross-validation notes and results to the PR body.

---

## 📋 Jules Agent Prompt Template

Use this when directing an AI agent (Claude/GPT/Codex) for Jules work:

```
Hello, you are Jules-0X, responsible for creating tests in the LUKHAS AI platform.

📂 Your module allocation is documented in docs/testing/JULES_AGENT_TEST_ALLOCATION.md and detailed in tests/specs/JULES-0X-<MODULE>.yaml.

📂 Assigned Modules:
Find your allocation in `docs/testing/JULES_AGENT_TEST_ALLOCATION.md`.

📑 Specification:
Check your `.yaml` spec in `tests/specs/JULES-0X-<MODULE>.yaml`.

🎯 Task:
- Write new pytest tests according to the spec.
- Place files under tests/unit/ or tests/integration/.
- Use @pytest.mark.<tier> markers from pytest.ini.
- Ensure ≥80% coverage, deterministic runs, and T4 compliance.
- Add edge cases, negative cases, and golden files where applicable.

✅ Acceptance Criteria:
- Tests pass locally and in CI
- Coverage ≥80% per module
- No fake tests (assert True/False, empty tests, blanket excepts)
- PR uses commit_standard_format.yaml conventions
 - Cross-validation completed with another Jules agent (attach notes in PR body)
 - Contract invariants validated against CONTRACT.md
 - Golden files produced and validated where required
- No new linting/type errors
- Follow LUKHAS coding standards
```
# LUKHAS AI Platform

Production-ready consciousness-aware AI platform with Constellation Framework and multi-agent development system.

## 🤖 Current Mission: Test Suite Development via Jules Agents

**📋 Active Development:** [Jules Agent Test Allocation](docs/testing/JULES_AGENT_TEST_ALLOCATION.md) - Systematic test development across 10 specialized agents targeting ~150+ missing test modules

> ⚠️ NOTE — Jules tasks are currently happening: Do NOT delete or remove any Jules-related sections or files while this work is in progress. Preserve all Jules assignments, configs, and docs until the Jules program is explicitly closed.

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
