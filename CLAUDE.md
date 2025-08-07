# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Context

This is part of the LUKHAS AI multi-repository ecosystem:

### **PRIMARY REPOSITORIES:**
- **Prototype** (`/Users/agi_dev/Prototype/`) - Original development repository
  - Contains ALL LUKHAS AI creations: production-ready to visionary ideas, apps, websites
  - Safe and recommended source for LUKHAS AI knowledge and logic
  - Note: Paths, names, and vision may slightly diverge from PWM
  
- **Consolidation-Repo** (`/Users/agi_dev/Downloads/Consolidation-Repo/`) - Active consolidation workspace
  - Integration and consolidation of LUKHAS components
  
- **PWM Repository** (`/Users/agi_dev/Lukhas_PWM/`) - **THIS REPOSITORY**
  - Pack-What-Matters production workspace
  - Distilled, lean, functional components only

- **LUKHAS Archive** (`/Users/agi_dev/lukhas-archive/`) - **IMPORTANT: Archive Repository**
  - All removed, deprecated, or refactored code goes here
  - **NEVER DELETE** - Always move to archive
  - Preserves all LUKHAS innovations and prototypes
  - Organized by date and source module
  - Used for: backups, deprecations, major refactors, experimental code

All repositories have local and GitHub remote versions (except archive which is local-only with cloud backup).

## Overview

LUKHAS PWM (Pack-What-Matters) is a lean, production-ready AGI system that distills essential LUKHAS components into working, functional modules. It combines consciousness, memory, identity, quantum processing, biological adaptation, and ethical governance to create a sophisticated AI research platform. The codebase achieves 99.9% system connectivity with comprehensive Guardian System protection.

## Common Development Tasks

### Environment Setup

```bash
# Activate existing virtual environment (.venv)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or create new virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt  # For testing

# Set up environment
cp .env.example .env
# Edit .env with OpenAI API key and other settings
```

### Building and Running

```bash
# Run main orchestrator (if available)
python orchestration/brain/primary_hub.py

# Run specific modules
python consciousness/unified/auto_consciousness.py

# Run standalone module example
python -m emotion.service

# Run integrated system
python main.py
```

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/governance/test_governance.py              # Basic governance tests
pytest tests/governance/test_enhanced_governance.py     # Enhanced governance tests
pytest tests/governance/test_comprehensive_governance.py # Full Guardian Reflector suite

# Run with coverage
pytest --cov=lukhas tests/

# Run functional analysis tools
python tools/analysis/PWM_FUNCTIONAL_ANALYSIS.py
python tools/analysis/PWM_OPERATIONAL_SUMMARY.py
python tools/analysis/PWM_WORKSPACE_STATUS_ANALYSIS.py
python tools/analysis/PWM_SECURITY_COMPLIANCE_GAP_ANALYSIS.py

# Run single test
pytest tests/governance/test_governance.py::test_specific_function

# Test markers available
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m security      # Security tests only
```

### Code Quality

```bash
# Format code
black lukhas/ tests/

# Linting
flake8 lukhas/
ruff lukhas/        # Fast alternative linter

# Type checking
mypy lukhas/
```

### Linting and Type Checking

```bash
# Run linting (using ruff for speed)
ruff check .

# Run type checking
mypy lukhas/

# Auto-fix linting issues
ruff check --fix .
```

## High-Level Architecture

### System Organization

The codebase follows a modular architecture with 41 root systems organized into functional domains (reduced from 53 through consolidation):

**Core Infrastructure:**
- `core/` - GLYPH engine, symbolic processing, system foundations (396 files)
- `orchestration/` - Brain integration, multi-agent coordination (349 files)
- `governance/` - Guardian System v1.0.0 ethical oversight

**Cognitive Systems:**
- `consciousness/` - Awareness, reflection, decision-making (55 files, 70.9% functional)
- `memory/` - Fold-based memory with causal chains (222 files, 72.1% functional)
- `reasoning/` - Logic, causal inference, goal processing (117 files)
- `identity/` - Quantum-resistant auth, tier access (147 files, 66.0% functional)

**Advanced Processing:**
- `quantum/` - Quantum-inspired algorithms (93 files, 82.8% functional)
- `bio/` - Biological adaptation systems (49 files, 65.3% functional)
- `emotion/` - VAD affect, mood regulation (26 files, 64.7% functional)
- `creativity/` - Dream engine with 40+ modules (89 files)

**Integration:**
- `api/` - FastAPI endpoints (core and commercial APIs)
- `architectures/` - DAST, ABAS, NIAS unified architecture systems
- `bridge/` - External API connections (98 files)
- `ethics/` - Multi-tiered policy engines (17 files)

### Key Design Patterns

1. **Symbolic Communication**: All modules use GLYPH tokens for cross-module messaging
2. **Guardian Protection**: Every operation validated by ethics engine
3. **Fold-Based Memory**: Preserves causal chains and emotional context
4. **Dream-Driven Innovation**: Creative solutions from controlled chaos
5. **Bio-Symbolic Coherence**: 102.22% coherence between biological and symbolic systems
6. **Multi-Stage Pipelines**: Quantum and bio modules use transformation pipelines
7. **Orchestrator Pattern**: Cross-domain coordination via hub modules

### Module Communication

Critical dependencies:
- All modules depend on `core/` for GLYPH processing
- `orchestration/brain/` coordinates cross-module actions
- `governance/` validates all operations
- `memory/` provides persistence across modules
- Circular dependencies strictly avoided
- Integration modules named as `*_adapter.py` or `*_hub.py`

## Guardian System Integration

The Guardian System v1.0.0 provides comprehensive ethical oversight:

### Protection Features
- **Remediator Agent**: Symbolic immune system for threat detection
- **Reflection Layer**: Ethical reasoning for all operations
- **Symbolic Firewall**: Multi-layered security protection
- **Drift Detection**: Monitors for ethical and behavioral drift (threshold: 0.15)
- **Decision Justification**: Philosophical reasoning engine

### Testing with Guardian Reflector
- Multi-framework moral reasoning (virtue ethics, deontological, consequentialist)
- SEEDRA-v3 model for deep ethical analysis
- Real-time consciousness protection
- Comprehensive enterprise-grade validation

## Development Guidelines

### Adding Features

1. **Choose Module**: Select appropriate module based on functionality
2. **Use GLYPHs**: Always use symbolic tokens for cross-module communication
3. **Ethics First**: All features must pass Guardian System validation
4. **Memory Integration**: Significant actions create memory folds
5. **Test Coverage**: Aim for 98%+ coverage (like dream engine)

### Working with Specific Modules

**Memory System (`memory/`)**
- Use fold-based architecture
- Preserve emotional context
- 99.7% cascade prevention rate
- Close memory folds after use
- Fold limit: 1000 (configurable)

**Quantum Processing (`quantum/`)**
- 82.8% functional - most reliable module
- Post-quantum cryptography ready
- Multi-stage transformation pipelines
- Encryption level: 256-bit default

**API Module (`api/`)**
- Only 33.3% functional - needs improvement
- FastAPI-based endpoints
- Focus on stability over features
- Base URL: `http://localhost:8080`

**Orchestration (`orchestration/`)**
- 60.5% functional - refactoring needed
- Brain hub coordinates all modules
- Avoid tight coupling
- Check `AGENT.md` for integration status

### Security Considerations

- All inputs validated through `bridge/`
- Identity module handles authentication
- Ethics engine cannot be bypassed
- Complete audit trail with causality chains
- Quantum-resistant cryptography throughout
- Multi-tier authentication enabled
- Biometric support available

## Common Pitfalls

1. **Never bypass Guardian System** - All operations must be validated
2. **Always use GLYPHs** - Direct module communication breaks symbolic unity
3. **Monitor drift scores** - Respond to behavioral changes (threshold: 0.15)
4. **Close memory folds** - Prevent memory leaks
5. **Check functional status** - Some modules only partially operational
6. **Verify integration status** - Many files in transition, check `AGENT.md`

## Debugging Tips

1. **Check Trace Logs**: `trace/` directory for system-wide debugging
2. **Monitor Drift**: Watch `drift_score` in governance metrics
3. **Memory Visualization**: Use fold visualizers for memory debugging
4. **Ethics Violations**: Check Guardian System logs
5. **GLYPH Translation**: Use symbolic parser for token debugging
6. **Functional Analysis**: Run `tools/analysis/PWM_FUNCTIONAL_ANALYSIS.py` for module status
7. **Audit Trail**: Check `data/drift_audit_summary.json` for system behavior

## Production Deployment

The system includes 3 microservice deployments:
- Consciousness Platform (`deployments/consciousness_platform/`)
- Dream Commerce (`deployments/dream_commerce/`)
- Memory Services (`deployments/memory_services/`)

Each service is Docker-containerized with FastAPI endpoints.

### Docker Support

```bash
# Build and run with Docker Compose (where available)
docker-compose up

# Individual service deployment
cd deployments/consciousness_platform
docker build -t lukhas-consciousness .
docker run -p 8080:8080 lukhas-consciousness
```

## Configuration

Main configuration file: `lukhas_pwm_config.yaml`

Key environment variables (set in `.env`):
- `OPENAI_API_KEY`: Required for AI capabilities
- `DATABASE_URL`: PostgreSQL connection string
- `LUKHAS_ID_SECRET`: Security key (min 32 chars)
- `ETHICS_ENFORCEMENT_LEVEL`: strict/moderate/lenient
- `DREAM_SIMULATION_ENABLED`: true/false
- `QUANTUM_PROCESSING_ENABLED`: true/false
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR

## File Organization Guidelines

**IMPORTANT**: When creating new files, follow the proper directory structure to maintain a clean root directory.

### Directory Structure (ORGANIZED - August 2025)

```
🧠 LUKHAS_PWM/
├── 📄 Root Files (ONLY these belong in root)
│   ├── CLAUDE.md                    # This file
│   ├── README.md                    # Primary documentation (UPDATED)
│   ├── LICENSE                      # Legal
│   ├── requirements.txt             # Core dependencies (UPDATED)
│   ├── main.py                      # Main entry point (FIXED imports)
│   ├── package.json                 # Node.js dependencies
│   ├── lukhas_pwm_config.yaml       # Core configuration
│   ├── pytest.ini                   # Test configuration
│   └── .gitignore, .env.example     # Environment files
│
├── 📁 docs/                         # All documentation (ORGANIZED)
│   ├── 📁 reports/                  # Analysis reports
│   │   ├── 📁 status/               # Status reports (all *_COMPLETE.md moved here)
│   │   └── 📁 analysis/             # Analysis results (all JSON reports moved here)
│   ├── 📁 planning/                 # Planning documents
│   │   └── 📁 completed/            # All PHASE_* files moved here
│   └── All documentation files      # Moved from root
│
├── 📁 tools/                        # Analysis & utility tools
│   ├── 📁 analysis/                 # Analysis scripts (PWM_*.py)
│   ├── 📁 scripts/                  # All utility scripts moved here
│   └── 📁 documentation_suite/      # Documentation generators
│
├── 📁 tests/                        # Test suites (ORGANIZED)
│   ├── 📁 stress/                   # Stress tests (all STRESS_TEST_*.py moved here)
│   ├── 📁 governance/               # Governance tests
│   └── All test files               # Moved from root
│
├── 📁 test_results/                 # Test outputs (ORGANIZED)
│   └── All test results             # JSON and report files
│
└── 📁 [Module Directories]          # Core LUKHAS modules
```

### File Placement Rules

**NEVER create these in root:**
- Analysis scripts (PWM_*.py) → Place in `tools/analysis/`
- Test files (test_*.py) → Place in appropriate `tests/` subdirectory
- Reports (*.json, *_REPORT.md) → Place in `docs/reports/`
- Planning documents → Place in `docs/planning/`
- Temporary or working files → Use appropriate module directory

**Examples:**
- ❌ `/PWM_FUNCTIONAL_ANALYSIS.py` 
- ✅ `/tools/analysis/PWM_FUNCTIONAL_ANALYSIS.py`

- ❌ `/test_governance.py`
- ✅ `/tests/governance/test_governance.py`

- ❌ `/PWM_OPERATIONAL_STATUS_REPORT.md`
- ✅ `/docs/reports/status/PWM_OPERATIONAL_STATUS_REPORT.md`

### When Creating New Components

1. **Analysis Tools**: Always place in `tools/analysis/` or `tools/scripts/`
2. **Documentation**: Use `docs/` with appropriate subdirectory
3. **Tests**: Place in `tests/` with module-specific subdirectory
4. **Module Code**: Use the appropriate module directory
5. **Configuration**: Only core configs belong in root

### Automated Organization

A pre-commit hook and GitHub Action help maintain organization:
- Files created in wrong locations will be flagged
- Suggestions provided for correct placement
- Automatic organization can be triggered

Remember: A clean root directory makes the project more professional and easier to navigate!

## Cross-Repository Development

When working with LUKHAS AI components:

### Source Repository Guidelines
- **Prototype Repository**: Primary source for innovative features and experimental code
  - Check `/Users/agi_dev/Prototype/` for original implementations
  - Safe to copy logic and patterns (created by LUKHAS AI founder)
  - Be aware of naming/path differences when adapting code

### Integration Workflow
1. **Research in Prototype**: Look for relevant implementations and patterns
2. **Adapt for PWM**: Modify to fit Pack-What-Matters philosophy
3. **Test Integration**: Ensure compatibility with existing PWM systems
4. **Document Origins**: Note source files when bringing in new components

### Key Differences to Note
- **Prototype**: Includes experimental and visionary components
- **PWM**: Only production-ready, essential components
- **Paths**: May differ between repositories
- **Dependencies**: PWM uses minimal dependencies

When in doubt about a component's implementation, check the Prototype repository for the original LUKHAS AI vision and adapt it to PWM's lean requirements.

## External Integration Examples

### Anthropic Claude Integration
```python
from lukhas.emotion import EmotionEnhancer
from lukhas.dream import DreamInjector

# Add emotional intelligence to Claude
enhancer = EmotionEnhancer()
response = anthropic.complete(
    enhancer.add_emotional_context(prompt)
)
```

### OpenAI GPT Integration
```python
from lukhas.identity import SafetyWrapper
from lukhas.trace import AuditLogger

# Wrap GPT with LUKHAS safety
safe_gpt = SafetyWrapper(openai.ChatCompletion)
traced_gpt = AuditLogger(safe_gpt)
```

## Important Resources

- **Main Documentation**: `README.md` - Complete system overview
- **Trinity Documentation**: `README_TRINITY.md` - Guardian system and symbolic AI overview
- **Copilot Instructions**: `.github/copilot-instructions.md` - Additional AI agent guidance
- **Module Manifests**: `*/MODULE_MANIFEST.json` - Module-specific metadata
- **Test Configuration**: `pytest.ini` - Testing setup and markers
- **Analysis Tools**: `tools/analysis/` - System analysis scripts

## Session Context Archives

Important development sessions are documented for reference:

### Finalization Session (August 5, 2025)
- **Location**: `/docs/context/session_20250805_finalization.md`
- **Summary**: System stabilization from 87.8% to 100% functionality
- **Key Work**: Identity system implementation, API endpoints completion, dashboard enhancements
- **Outcome**: Full production readiness for OpenAI review

This session archive contains detailed technical context about fixes, implementations, and architectural decisions made during the final stabilization phase.