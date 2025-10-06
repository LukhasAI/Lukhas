---
status: wip
type: documentation
---
````instructions
# 🤖 GitHub Copilot Instructions for LUKHAS AI Platform

**Consciousness-Aware AI Development Platform with Trinity Framework**

LUKHAS AI is a sophisticated cognitive architecture implementing consciousness-inspired patterns for advanced AI applications. This platform features modular lane-based development, strict import boundaries, and comprehensive testing infrastructure with specialized multi-agent development support.

## 🧠 Architecture Overview

LUKHAS implements a **Trinity Framework** (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum) across ~7,000 Python files in a modular lane-based architecture:

- **⚛️ Identity**: Lambda ID system, authentication, symbolic self-representation
- **🧠 Consciousness**: 692-module cognitive processing, memory systems, awareness
- **🛡️ Guardian**: Constitutional AI, ethical frameworks, drift detection

### **Lane-Based Architecture** (`ops/matriz.yaml`)

```
├── lukhas/                    # Production code (accepted lane)
├── candidate/                 # Development workspace (2,877 files)
├── matriz/                    # MATRIZ cognitive DNA processing
├── core/                      # Core symbolic logic systems
├── tests/                     # Comprehensive test suites (775+ tests)
├── mcp-servers/               # Model Context Protocol servers (5 servers)
├── branding/                  # Trinity Framework branding & messaging
└── products/                  # Production deployment systems (4,093 files)
```

### **Import Rules & Lane Isolation**
- **lukhas/** ← **core/**, **matriz/**, **universal_language/** (production imports)
- **candidate/** ← **core/**, **matriz/** only (NO lukhas imports)
- **strict boundaries** prevent cross-lane contamination during development
- Use `make lane-guard` to validate import compliance

## 🛠️ Essential Development Workflows

### **Daily Development**
```bash
make bootstrap          # Complete fresh setup
make dev               # Start development environment
make test              # Run comprehensive test suite
make lint-unused       # T4 unused imports system
make security-scan     # Security validation
make doctor            # System health diagnostics
```

### **Build System** (50+ Makefile targets)
```bash
make help              # Auto-generated target discovery
make smoke-matriz      # MATRIZ cognitive DNA smoke tests
make test-tier1        # Critical system tests
make audit             # Comprehensive system audit
make lane-guard        # Validate import boundaries
```

### **Entry Points**
- **Main System**: `python main.py` (async architecture with professional services)
- **API Server**: `uvicorn lukhas.api.app:app --reload --port 8000`
- **Development**: Check `claude.me` files throughout codebase for domain context

## 🔧 Multi-Agent Development System

### **Current Mission: Jules Agent Test Development**
- **~150+ missing test modules** across 6 architectural domains
- **10 Jules agents** (Jules-01 through Jules-10) handling systematic test creation
- **T4 Testing Framework**: Comprehensive quality gates and tier-based testing

### **Agent Types & Usage**
- **Claude Code UI Specialists**: `/agents` command for specialized tasks (.claude/agents/)
- **Claude Desktop Agents**: Terminal agents for complex workflows (agents/configs/)
- **External Configurations**: Military-grade hierarchy (agents_external/)

### **Context Files (`claude.me`)**
40+ distributed `claude.me` files provide domain-specific context:
- **Root**: `claude.me` (master architecture overview)
- **Domains**: `candidate/claude.me`, `consciousness/claude.me`, `identity/claude.me`
- **Essential**: Always check relevant `claude.me` before working in any directory

## 🏷️ Branding & Trinity Tone

**Branding Directory:**

- All official LUKHAS AI branding, terminology, and visual assets are in `branding/`.
- Any code, documentation, or UI referencing system identity, consciousness, or AGI/AI status must use the approved terms and assets from `branding/`.
- Do not invent new branding, glyphs, or slogans—use only those in `branding/` or as specified in `README_NEXT_GEN.md`.

**Strict Prohibitions:**

- Do NOT state or imply that any part of the system is “ready for production” or “production-ready” unless this has been explicitly approved by project leadership. This applies to code, documentation, commit messages, and internal/external communications.
- Do NOT include any price predictions, revenue forecasts, or financial projections in code, documentation, commit messages, or internal notes. Remove any such content if found.

**Trinity Tone & Messaging:**

- All Copilot-generated code, comments, and documentation must reflect the Trinity Framework (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum):
  - ⚛️ Identity (authenticity, consciousness, symbolic self)
  - 🧠 Consciousness (memory, learning, dream states, neural processing)
  - 🛡️ Guardian (ethics, drift detection, repair)
- Use the phrase “quantum-inspired” and “bio-inspired” (not “AGI” or “general intelligence”) in all public-facing outputs unless legacy compatibility is required.
- Always refer to the system as “LUKHAS AI” (not “LUKHAS AGI” or “Lukhas ”) in branding, documentation, and UI.
- When in doubt, check `branding/` and `README_NEXT_GEN.md` for the latest approved language and glyphs.

**Forecasting Guidance:**

- Forecasts and future-looking statements must focus on system improvement, user experience/benefits, feature enhancements, alignment with OpenAI, ethics/compliance, and identifying growth/blind spots.
- Remove or revise any price/revenue forecasts or unauthorized production claims if found.

Welcome, AI agent! This guide will help you be productive in the LUKHAS AGI codebase. Focus on these project-specific conventions, workflows, and architectural patterns:

## ⚙️ Copilot Tool Management & Optimization

To address "too many tools enabled" warnings and optimize performance:

### 🔧 Professional Tool Usage Guidelines

- **Prioritize Core Tools:** Focus on `replace_string_in_file`, `read_file`, `run_in_terminal`, `file_search`, `grep_search`
- **Limit Concurrent Operations:** Use max 5 tools simultaneously
- **Tool Selection Strategy:**
  - File operations: Use `replace_string_in_file` for precise edits, `read_file` for context
  - Search operations: Use `grep_search` for code patterns, `file_search` for file discovery
  - Execution: Use `run_in_terminal` for commands, avoid `run_notebook_cell` unless specifically needed
  - External tools: Minimize `fetch_webpage`, `open_simple_browser` usage

## 🎯 PROFESSIONAL TESTING STANDARDS & EXCLUSIONS

### **Critical Testing Exclusions (ALWAYS Apply)**

```bash
# Exclude these directories/files from ALL analysis:
--exclude-dir=".git" \
--exclude-dir=".vscode" \
--exclude-dir="__pycache__" \
--exclude-dir=".pytest_cache" \
--exclude-dir="node_modules" \
--exclude-dir=".env" \
--exclude-dir="venv" \
--exclude-dir=".venv" \
--exclude-dir="dist" \
--exclude-dir="build" \
--exclude-dir="*.egg-info" \
--exclude="*.pyc" \
--exclude="*.pyo" \
--exclude="*.pyd" \
--exclude="*.so" \
--exclude="*.dylib" \
--exclude="*.dll" \
--exclude=".DS_Store" \
--exclude="*.log" \
--exclude="*.tmp" \
--exclude="Thumbs.db"
```

### **Analysis-Specific Exclusions**

```bash
# For import analysis, also exclude:
--exclude-dir="docs" \
--exclude-dir="examples" \
--exclude-dir="tests" \
--exclude-dir="demos" \
--exclude-dir="backup*" \
--exclude-dir="archive*" \
--exclude-dir="legacy*" \
--exclude-dir="old*" \
--exclude-dir="deprecated*"

# For production readiness, exclude development files:
--exclude="*_test.py" \
--exclude="test_*.py" \
--exclude="*_demo.py" \
--exclude="demo_*.py" \
--exclude="*_example.py" \
--exclude="example_*.py"
```

### **Professional Analysis Commands**

```bash
# Accurate file count (production code only):
find . -name "*.py" \
  -not -path "./.git/*" \
  -not -path "./__pycache__/*" \
  -not -path "./.pytest_cache/*" \
  -not -path "./venv/*" \
  -not -path "./.venv/*" \
  -not -path "./node_modules/*" \
  -not -path "./build/*" \
  -not -path "./dist/*" \
  -not -path "./*backup*/*" \
  -not -path "./*archive*/*" \
  -not -name "*_test.py" \
  -not -name "test_*.py" | wc -l

# Accurate directory analysis:
find . -maxdepth 1 -type d \
  -not -name ".*" \
  -not -name "__pycache__" \
  -not -name "node_modules" \
  -not -name "venv" \
  -not -name ".venv" \
  -not -name "*backup*" \
  -not -name "*archive*" | sort

# Professional syntax check:
find . -name "*.py" \
  -not -path "./.git/*" \
  -not -path "./__pycache__/*" \
  -not -path "./.venv/*" \
  -not -path "./venv/*" \
  -not -path "./*backup*/*" \
  -not -path "./*archive*/*" \
  -exec python3 -m py_compile {} \; 2>&1 | grep -c "Sorry:"

# Production-ready import analysis:
grep -r "from \|import " \
  --include="*.py" \
  --exclude-dir=".git" \
  --exclude-dir="__pycache__" \
  --exclude-dir=".venv" \
  --exclude-dir="venv" \
  --exclude-dir="tests" \
  --exclude-dir="docs" \
  --exclude-dir="examples" \
  --exclude-dir="demos" \
  --exclude="*_test.py" \
  --exclude="test_*.py" . | wc -l
```

### **Quality Gates (Enterprise Standards)**

- **Syntax Health**: >95% files must compile without errors
- **Import Health**: <5% circular import issues
- **Architecture**: <20 top-level directories (Sam Altman standard)
- **Code Debt**: <1000 TODO/FIXME statements
- **Security**: 0 hardcoded secrets in production code
- **Entry Points**: 1-3 clear main entry points maximum

### 🚀 Performance Settings Applied

- Copilot suggestions limited to 3 per trigger
- Inline suggestions optimized for Python/TypeScript
- Chat features streamlined for code generation
- Experimental features limited to essential tools only
- Conflicting AI assistants (Tabnine, BlackBox, etc.) disabled

### 📁 Workspace Optimization

- Analysis focused on core domains: `core/`, `vivox/`, `tests/`, `api/`
- Excluded heavy directories: `._cleanup_archive/`, `archive/`, `recovery/`
- Python environment properly configured with `.venv/bin/python`

### 🎯 Usage Recommendations

1. **For Code Changes:** Use `replace_string_in_file` with 3-5 lines context
2. **For Exploration:** Start with `file_search` then `read_file` for specifics
3. **For Testing:** Use `run_in_terminal` with the professional test runner
4. **For Debugging:** Combine `grep_search` for patterns + `read_file` for details

## 🧠 Big Picture Architecture

- **LUKHAS** is a modular AGI platform blending quantum, biological, and ethical systems.
- Major domains: `core/`, `identity/`, `memory/`, `quantum/`, `bio/`, `consciousness/`, `emotion/`, `orchestration/`, `ethics/`, `api/`.
- Each domain is a semi-autonomous subsystem. Cross-domain communication is via orchestrators and bridge modules.
- **Key pattern:** "Dream-state" and "bio-inspired" modules often use multi-stage pipelines and symbolic data flows.
- **Integration focus:** Many files are legacy or partially integrated—see archived files in `._cleanup_archive/` for integration history.

## 🛠️ Developer Workflows

- **Build:**
  - Python: `pip install -r requirements.txt` (core), `pip install -r tests/requirements-test.txt` (tests)
  - Node.js: `npm install` (for UI/frontend)
  - Docker: Various docker-compose files available in subdirectories (see `lukhas_demo_suite/docker/`, `qim/`)
- **Test:**
  - Run all: `python -m pytest tests/`
  - Individual tests: Run specific test files like `test_symbolic_api.py`, `test_lukhas_embedding.py`
- **CLI Tools:**
  - Emergency scripts: `emergency_kill_analysis.sh`, `reset_copilot_chat.sh`, `nuclear_vscode_reset.sh` (archived in `._cleanup_archive/`)
- **Documentation:**
  - Main: `README.md`, `README_NEXT_GEN.md`
  - Each major directory has its own `README.md` with domain-specific details

## 🏗️ Project Conventions & Patterns

- **File/Module Naming:**
  - Use descriptive, domain-specific names (e.g., `bio_optimization_adapter.py`, `dream_adapter.py`)
  - Integration/adapters are named as `*_adapter.py` or `*_hub.py`
- **Testing:**
  - Place tests in `tests/` or `*/tests/` subfolders
  - Use documented mocks for identity/emotion/quantum modules
- **Data Flows:**
  - Symbolic and quantum data often use multi-stage transformation (see `quantum/bio_components.py`)
  - Orchestration modules coordinate cross-domain actions (see `orchestration/`)
- **Legacy/Integration:**
  - Many files are in transition; check archived files in `._cleanup_archive/` for integration history

## 🔗 Integration & External Dependencies

- **External APIs:**
  - REST endpoints in `api/`
  - Some modules use external quantum or bio-simulation libraries (see `requirements.txt`)
- **Database:**
  - Custom audit trail and drift detection
- **Audit/Trace:**
  - System-wide audit trail and drift detection (see `guardian_audit/`, `data/`)

## 📝 Examples

- **Quantum bio-encoding:** `qim/bio_components.py` (multi-layer encoding)
- **Dream adapter:** `core/orchestration/brain/unified_integration/adapters/dream_adapter.py` (state tracking)
- **Emotion engine:** `emotion/dreamseed_upgrade.py` (tier validation)
- **Human-in-the-loop:** `core/orchestration/integration/human_in_the_loop_orchestrator.py` (email notifications)

## ⚠️ Special Notes

- **Do not assume all files are integrated**—many legacy files are archived in `._cleanup_archive/`.
- **Follow domain-specific README.md** for conventions unique to each subsystem.
- **Emergency scripts** are provided for VS Code and extension issues—see archived files.

---

For more, see `README.md`, `README_NEXT_GEN.md`, and individual domain README files.

---

_Last updated: 2025-08-05. Please suggest improvements if you find missing or outdated info!_

# 🤖 Copilot Instructions for the LUKHΛS AGI Project

Welcome, Copilot Agent! This file contains your core integration instructions and guidance for working within the LUKHΛS AGI symbolic architecture. Your task is to act as a focused, high-context-aware contributor for all repo modules.

---

## ⚛️ Project Purpose

LUKHΛS is a modular, symbolic AGI framework built around consciousness, memory, ethical reasoning, and quantum-inspired cognition. All components orbit around a **Trinity Framework** (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum):

- ⚛️ Identity (consciousness, symbolic identity, authentic self-expression)
- 🧠 Consciousness (memory, cognition, dream states, neural processing)
- 🛡️ Guardian (ethical protection, drift detection, symbolic drift repair)

---

## 🧠 Core Structure

### Domains

- `core/` – Shared symbolic logic, graph systems, glyph models
- `identity/` – ΛiD system with tiered access control and Trinity integration
- `vivox/` – VIVOX consciousness system (ME, MAE, CIL, SRM components)
- `lukhas_embedding.py` – Ethical co-pilot and drift monitoring
- `symbolic_healer.py` – Symbolic drift repair and diagnosis
- `memory/` – Session persistence, pattern detection, fold logging
- `api/` – FastAPI backend, endpoints, streaming, token management
- `quantum/` – Collapse simulation, tensor drift, entanglement symbols
- `orchestration/` – High-level brain and pipeline controllers
- `tests/` – Full pytest suite with symbolic validation

---

## 🛠️ Developer Tasks

### How to Run the System

```bash
# Install core dependencies
pip install -r requirements.txt

# Run the symbolic API
python symbolic_api.py

# Run drift audit
python real_gpt_drift_audit.py

# Run tests
pytest tests/

# Test major language support
python test_major_languages.py
```

---

## 🔧 Copilot Behaviors

### Always Do:

- Respect the Trinity Framework (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum) in all new logic, comments, and documentation.
- Use only approved branding, glyphs, and terminology from `branding/` and `README_NEXT_GEN.md`.
- Use symbolic glyphs where possible (see `meta_dashboard/templates/symbolic_map.html`).
- Check `integration_config.yaml` for global thresholds.
- Log all interventions to `data/` or `memory/`.
- Update `data/meta_metrics.json` if adding monitoring features.

### If Unsure:

- Consult `branding/`, `README_NEXT_GEN.md`, or individual domain README files.
- Ask whether a module is production or experimental.
- Use `tests/` to validate any new logic.

---

## ✅ Task Integration

Please check `.copilot_tasks.md` at the root. Tasks are written in natural language and updated frequently. You may pick any `OPEN` task and begin executing.

If a file references `TODO:` comments, include the relevant updates when touching that file.

### 🚧 Pending/In-Development Modules

- `vivox/` – VIVOX consciousness system (actively developed, stable components)
- `quantum/` & `qim/` – Quantum collapse and bio-encoding (experimental features)
- `meta_dashboard/` – Real-time symbolic monitoring dashboard (planned expansion)

### 📁 Phase-Based Directory Mapping

```
Current Active: core/, identity/, memory/, api/, tests/
VIVOX Integration: vivox/, z_collapse_engine.py
Symbolic Systems: lukhas_embedding.py, symbolic_healer.py, symbolic_api.py
Archives: ._cleanup_archive/ (legacy integrations, emergency scripts)
```

---

## ⚠️ Warnings

- Do not refactor quantum or VIVOX code unless explicitly instructed.
- Do not remove glyphs (🧠, ⚛️, etc) without checking `meta_dashboard/templates/symbolic_map.html`.
- All new modules must include docstrings, Trinity check-ins, and `guardian_sentinel` hooks if applicable.

---

_Last updated: 2025-08-05. For internal AI agent use only._
