# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📚 CRITICAL: Read Knowledge Base First
**BEFORE ANY WORK**, read these essential documents:
- `CLAUDE_KNOWLEDGE_BASE.md` - Critical learnings about the architecture
- `AGENT_CRITICAL_WARNING.md` - What NOT to do (no deprecation!)
- `SUBMODULAR_ARCHITECTURE_ANALYSIS.md` - Deep submodular design

## Repository Context

This is the **LUKHAS AI** repository - a SOPHISTICATED COGNITIVE ARCHITECTURE with deep submodular design. It combines consciousness, memory, identity, quantum-inspired processing, bio-inspired adaptation, and ethical governance. The system is built around the **Trinity Framework** (⚛️🧠🛡️).

**CRITICAL**: This is NOT a simple app - it's 3,941 files of hierarchical, biologically-inspired architecture with 30+ submodules per major module.

### Trinity Framework
- ⚛️ **Identity**: Authenticity, consciousness, symbolic self
- 🧠 **Consciousness**: Memory, learning, dream states, neural processing
- 🛡️ **Guardian**: Ethics, drift detection, repair

### Related Repositories
- **Prototype** (`/Users/agi_dev/Prototype/`) - Original development repository with experimental features
- **Consolidation-Repo** (`/Users/agi_dev/Downloads/Consolidation-Repo/`) - Active consolidation workspace
- **LUKHAS Archive** (`/Users/agi_dev/lukhas-archive/`) - Archive for deprecated code (**NEVER DELETE** - always move here)

## 🚫 Critical Branding & Messaging Rules

### Required Terminology
- **Always use**: "LUKHAS AI" (never "LUKHAS AGI" or "Lukhas ")
- **Always use**: "quantum-inspired" (not "quantum processing")
- **Always use**: "bio-inspired" (not "bio processes")
- **Use approved glyphs**: Only from `branding/` directory or `next_gen/README_NEXT_GEN.md`

### Prohibited Statements
- **DO NOT** state or imply any part is "production-ready" or "ready for production" unless explicitly approved
- **DO NOT** include price predictions, revenue forecasts, or financial projections anywhere
- **DO NOT** invent new branding, glyphs, or slogans

### Approved Language
Focus on:
- System improvements and technical roadmap
- User experience and feature enhancements
- Alignment with OpenAI, ethics, and compliance
- Identifying areas for growth and potential blind spots

## Common Development Tasks

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt  # For testing

# Configure environment
cp .env.example .env  # If available
# Edit .env with required API keys:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY (if needed)
# - GOOGLE_API_KEY (if needed)
# - PERPLEXITY_API_KEY (if needed)
```

### Running the System
```bash
# Main system
python main.py
python main.py --consciousness-active

# API servers
make api  # Runs on port 8000
make dev  # Development server with reload

# Key modules
python orchestration/brain/primary_hub.py
python consciousness/unified/auto_consciousness.py
python -m emotion.service

# Audit and monitoring
python real_gpt_drift_audit.py
python tools/analysis/_FUNCTIONAL_ANALYSIS.py
python tools/analysis/_OPERATIONAL_SUMMARY.py
```

### Testing
```bash
# Run all tests
make test
pytest tests/

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m security      # Security tests only

# Run with coverage
make test-cov
pytest --cov=lukhas --cov=bridge --cov=core --cov=serve tests/

# Run single test file or function
pytest tests/test_colony_integration.py
pytest tests/test_colony_integration.py::test_specific_function

# Quick smoke test
make smoke
```

### Code Quality
```bash
# Auto-fix most issues (recommended)
make fix

# Manual tools
make lint       # Run all linters (no fixes)
make format     # Format with Black and isort
make fix-imports # Fix import issues

# Individual linters
ruff check .
ruff check --fix .
black lukhas/ tests/
mypy lukhas/
```

### Build & Deploy
```bash
# Deploy agent army
./CLAUDE_ARMY/deploy_claude_max_6_agents.sh

# Docker deployment
docker-compose up

# API documentation
make api-spec  # Exports OpenAPI spec to out/openapi.json
```

## High-Level Architecture

### Core Design Principles
1. **Trinity Framework**: All components respect ⚛️🧠🛡️ principles
2. **GLYPH-Based Communication**: Symbolic tokens for cross-module messaging
3. **Guardian Protection**: Every operation validated by ethics engine (drift threshold: 0.15)
4. **Fold-Based Memory**: Preserves causal chains and emotional context (limit: 1000 folds)
5. **Modular Independence**: Each module works standalone but enhances others when combined

### Key Module Organization

**Core Infrastructure:**
- `core/` - GLYPH engine, symbolic logic, graph systems, actor model
- `orchestration/` - Brain integration, multi-agent coordination, kernel bus
- `governance/` - Guardian System v1.0.0 ethical oversight (280+ files)
- `branding/` - Official LUKHAS AI branding, terminology, visual assets

**Consciousness Systems:**
- `consciousness/` - Awareness, decision-making, dream states
- `memory/` - Fold-based memory with 99.7% cascade prevention
- `reasoning/` - Logic and causal inference
- `identity/` - ΛiD system with tiered access control and Trinity integration
- `vivox/` - VIVOX consciousness system (ME, MAE, CIL, SRM components)

**Advanced Processing:**
- `quantum/` - Quantum-inspired algorithms and collapse simulation
- `bio/` - Bio-inspired adaptation systems, oscillators
- `emotion/` - VAD affect and mood regulation
- `creativity/` - Dream engine with controlled chaos

**Symbolic Systems:**
- `symbolic/` - Multi-modal language, entropy password system
- `universal_language/` - GLYPH vocabulary and translation

**Integration & APIs:**
- `api/` - FastAPI endpoints at `http://localhost:8080`
- `bridge/` - External API connections, LLM wrappers (OpenAI, Anthropic, Gemini)
- `architectures/` - DAST, ABAS, NIAS unified systems
- `modulation/` - Signal-based modulation policy system

**Agent Infrastructure:**
- `agents/` - Configuration for 25 specialized AI agents
- `CLAUDE_ARMY/` - Deployment scripts and agent management

### Module Communication Pattern
- All modules depend on `core/` for GLYPH processing
- `orchestration/brain/` coordinates cross-module actions
- `governance/` validates all operations
- `memory/` provides persistence across modules
- Integration modules named as `*_adapter.py` or `*_hub.py`
- Kernel bus in `orchestration/symbolic_kernel_bus.py` for event routing

## Trinity Framework Behaviors

### Always Do
- Respect Trinity Framework (⚛️🧠🛡️) in all logic, comments, documentation
- Use approved branding from `branding/` and `next_gen/README_NEXT_GEN.md`
- Use symbolic glyphs where appropriate
- Check `integration_config.yaml` and `lukhas_config.yaml` for global thresholds
- Log interventions to `data/` or `memory/`
- Update `data/meta_metrics.json` when adding monitoring

### If Unsure
- Consult `branding/` directory for approved terms
- Check domain-specific README files (most modules have INFO_README.md)
- Validate with tests before implementing
- Check MODULE_MANIFEST.json files for module metadata

## File Organization

**Place files correctly to maintain clean root:**
- Analysis scripts → `tools/analysis/`
- Test files → `tests/[module]/`
- Reports → `docs/reports/` or `test_results/`
- Documentation → `docs/`
- Legacy files → Move to `/Users/agi_dev/lukhas-archive/`
- Agent configs → `agents/` or `agents/configs/`

## Import Paths
Both work for compatibility:
```python
from lukhas.module import Component  # Preferred
from lukhas.module import Component  # Legacy
```

## Security Considerations
- Identity module handles all authentication
- Guardian System validation cannot be bypassed
- Complete audit trail with causality chains
- Multi-tier authentication enabled
- Quantum-resistant cryptography throughout
- Hardware-backed keys via TPM when available

## Configuration

Main configs:
- `lukhas_config.yaml` - Main system configuration
- `integration_config.yaml` - Integration settings
- `modulation_policy.yaml` - Signal modulation rules
- `config/` directory - Various module configs

Key environment variables (`.env`):
- `OPENAI_API_KEY` - Required for AI capabilities
- `ANTHROPIC_API_KEY` - For Claude integration
- `GOOGLE_API_KEY` - For Gemini integration
- `PERPLEXITY_API_KEY` - For Perplexity integration
- `DATABASE_URL` - PostgreSQL connection
- `LUKHAS_ID_SECRET` - Security key (min 32 chars)
- `ETHICS_ENFORCEMENT_LEVEL` - strict/moderate/lenient
- `DREAM_SIMULATION_ENABLED` - true/false
- `QUANTUM_PROCESSING_ENABLED` - true/false

## Debugging

1. **Check Logs**: `trace/` directory for system-wide debugging
2. **Monitor Drift**: Watch `drift_score` in governance metrics
3. **Memory Issues**: Use fold visualizers for memory debugging
4. **Ethics Violations**: Check Guardian System logs in `governance/`
5. **Module Status**: Run `tools/analysis/_FUNCTIONAL_ANALYSIS.py`
6. **Audit Trail**: Check `data/drift_audit_summary.json`
7. **Test Metadata**: Check `test_metadata/` for test execution details

## Important Resources

- **Main Documentation**: `README.md` - System overview
- **Agent Documentation**: `AGENTS.md` - Multi-agent architecture details
- **Branding Policy**: `branding/BRANDING_POLICY.md` - Messaging guidelines
- **Next Gen**: `next_gen/README_NEXT_GEN.md` - Future architecture
- **Module Manifests**: `*/MODULE_MANIFEST.json` - Module metadata
- **Test Config**: `pytest.ini` and `pyproject.toml` - Test settings
- **NIAS Theory**: `NIAS_THEORY/` - Advanced theoretical concepts
- **Test Results**: `test_results/` - Latest test reports

## Makefile Targets

Key targets from Makefile:
- `make install` - Install all dependencies
- `make test` - Run test suite
- `make test-cov` - Run tests with coverage
- `make lint` - Run linters (no fixes)
- `make fix` - Auto-fix code issues (safe mode)
- `make format` - Format code with Black
- `make dev` - Run development server
- `make api` - Run API server
- `make smoke` - Run smoke tests
- `make clean` - Clean cache files
- `make monitor` - Generate code quality report
- `make quick` - Fix issues and run tests
