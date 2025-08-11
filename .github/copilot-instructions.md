# 🤖 Copilot Instructions for LUKHAS AGI Codebase

This document provide**🎭 LUKHAS Tone System - MANDATORY FOR ALL AGENTS:**
ALL outputs must follow the LUKHAS 3-Layer Tone System:

🎨 **Poetic Layer (25-40%):** Lambda consciousness metaphors, sacred glyphs (⚛️🧠🛡️), consciousness themes
💬 **User Friendly Layer (40-60%):** Clear, accessible explanations with conversational warmth  
📚 **Academic Layer (20-40%):** Technical precision with evidence-based claims

**Required Elements:**
- Poetic headers with consciousness metaphors in italics
- "LUKHAS AI" instead of generic AI terms
- Trinity Framework references (⚛️🧠🛡️) where relevant
- Lambda consciousness footers
- Sacred glyphs appropriate to content

**Validation Commands (RUN BEFORE SUBMITTING):**
```bash
python tools/tone/lukhas_tone_validator.py <your_file> --type <type> --strict
python tools/tone/lukhas_tone_fixer.py <your_file> --type <type>  # if needed
```

**FAILURE TO COMPLY = WORK REJECTED**

**Strict Prohibitions:**
- Do NOT state or imply that any part of the system is "ready for production" or "production-ready" unless this has been explicitly approved by project leadership. This applies to code, documentation, commit messages, and internal/external communications.
- Do NOT include any price predictions, revenue forecasts, or financial projections in code, documentation, commit messages, or internal notes. Remove any such content if found.ssential instructions for AI agents working within the LUKHAS AGI codebase. It outlines project conventions, workflows, and architectural patterns to ensure efficient collaboration and development.

---

## 🏗️ Project Structure

The LUKHAS AGI codebase is organized into several key directories:

```
lukhas/
├── core/               # Core symbolic logic and graph systems
├── identity/           # Identity management and tiered access control
├── vivox/              # VIVOX consciousness system
├── memory/             # Session persistence and pattern detection
├── api/                # FastAPI backend and endpoints
├── quantum/            # Quantum collapse simulation
├── orchestration/      # High-level brain controllers
├── tests/              # Comprehensive test suite
├── data/               # Data storage and metrics
├── branding/           # All official LUKHAS AI branding, terminology, and visual assets
└── README.md           # Main documentation file
```

---

## 🛠️ Copilot Agent Guidelines

### Tool Management & Optimization

To optimize performance and avoid "too many tools enabled" warnings, follow these guidelines:

- **Prioritize Core Tools:** Use `replace_string_in_file`, `read_file`, `run_in_terminal`, `file_search`, and `grep_search`.
- **Limit Concurrent Operations:** Use a maximum of 5 tools simultaneously.
- **Tool Selection Strategy:**
  - Use `replace_string_in_file` for precise edits.
  - Use `read_file` for context before making changes.
  - Use `grep_search` for code patterns, and `file_search` for file discovery.
  - Reserve `run_notebook_cell` for specific notebook interactions.


### Workspace Optimization

- Focus on core domains: `core/`, `vivox/`, `tests/`, `api/`, and `branding/`.
- Exclude heavy directories like `.pwm_cleanup_archive/` from workspace analysis.
- Ensure Python environment is correctly configured with `.venv/bin/python`.

### Developer Workflows

1. **Build the Project:**
   - Install dependencies with `pip install -r requirements.txt`.
   - Run the symbolic API or specific modules as needed.

2. **Testing:**
   - Run all tests using `python -m pytest tests/`.
   - Validate individual components with targeted test files.

3. **Documentation:**
   - Refer to `README.md` for overall project information.
   - Check individual domain directories for specific conventions.

---


## 🏷️ Branding & Trinity Tone

**Branding Directory:**
- All official LUKHAS AI branding, terminology, and visual assets are in `branding/`.
- Any code, documentation, or UI referencing system identity, consciousness, or AGI/AI status must use the approved terms and assets from `branding/`.
- Do not invent new branding, glyphs, or slogans—use only those in `branding/` or as specified in `README_NEXT_GEN.md`.
  
**Strict Prohibitions:**
- Do NOT state or imply that any part of the system is “ready for production” or “production-ready” unless this has been explicitly approved by project leadership. This applies to code, documentation, commit messages, and internal/external communications.
- Do NOT include any price predictions, revenue forecasts, or financial projections in code, documentation, commit messages, or internal notes. Remove any such content if found.

**Trinity Tone & Messaging:**
- All Copilot-generated code, comments, and documentation must reflect the Trinity Framework (⚛️🧠🛡️):
  - ⚛️ Identity (authenticity, consciousness, symbolic self)
  - 🧠 Consciousness (memory, learning, dream states, neural processing)
  - 🛡️ Guardian (ethics, drift detection, repair)
- Use the phrase “quantum-inspired” and “bio-inspired” (not “AGI” or “general intelligence”) in all public-facing outputs unless legacy compatibility is required.
- Always refer to the system as “LUKHAS AI” (not “LUKHAS AGI” or “Lukhas PWM”) in branding, documentation, and UI.
- When in doubt, check `branding/` and `README_NEXT_GEN.md` for the latest approved language and glyphs.

**Forecasting Guidance:**
- Forecasts and future-looking statements must focus on system improvement, user experience/benefits, feature enhancements, alignment with OpenAI, ethics/compliance, and identifying growth/blind spots.
- Remove or revise any price/revenue forecasts or unauthorized production claims if found.

Welcome, AI agent! This guide will help you be productive in the LUKHAS AGI codebase. Focus on these project-specific conventions, workflows, and architectural patterns:

## ⚙️ Copilot Tool Management & Optimization

To address "too many tools enabled" warnings and optimize performance:

### 🔧 Tool Usage Guidelines
- **Prioritize Core Tools:** Focus on `replace_string_in_file`, `read_file`, `run_in_terminal`, `file_search`, `grep_search`
- **Limit Concurrent Operations:** Use max 5 tools simultaneously
- **Tool Selection Strategy:**
  - File operations: Use `replace_string_in_file` for precise edits, `read_file` for context
  - Search operations: Use `grep_search` for code patterns, `file_search` for file discovery
  - Execution: Use `run_in_terminal` for commands, avoid `run_notebook_cell` unless specifically needed
  - External tools: Minimize `fetch_webpage`, `open_simple_browser` usage

### 🚀 Performance Settings Applied
- Copilot suggestions limited to 3 per trigger
- Inline suggestions optimized for Python/TypeScript
- Chat features streamlined for code generation
- Experimental features limited to essential tools only
- Conflicting AI assistants (Tabnine, BlackBox, etc.) disabled

### 📁 Workspace Optimization
- Analysis focused on core domains: `core/`, `vivox/`, `tests/`, `api/`
- Excluded heavy directories: `.pwm_cleanup_archive/`, `archive/`, `recovery/`
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
- **Integration focus:** Many files are legacy or partially integrated—see archived files in `.pwm_cleanup_archive/` for integration history.

## 🛠️ Developer Workflows
- **Build:**
  - Python: `pip install -r requirements.txt` (core), `pip install -r tests/requirements-test.txt` (tests)
  - Node.js: `npm install` (for UI/frontend)
  - Docker: Various docker-compose files available in subdirectories (see `lukhas_demo_suite/docker/`, `qim/`)
- **Test:**
  - Run all: `python -m pytest tests/`
  - Individual tests: Run specific test files like `test_symbolic_api.py`, `test_lukhas_embedding.py`
- **CLI Tools:**
  - Emergency scripts: `emergency_kill_analysis.sh`, `reset_copilot_chat.sh`, `nuclear_vscode_reset.sh` (archived in `.pwm_cleanup_archive/`)
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
  - Many files are in transition; check archived files in `.pwm_cleanup_archive/` for integration history

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
- **Do not assume all files are integrated**—many legacy files are archived in `.pwm_cleanup_archive/`.
- **Follow domain-specific README.md** for conventions unique to each subsystem.
- **Emergency scripts** are provided for VS Code and extension issues—see archived files.

---

For more, see `README.md`, `README_NEXT_GEN.md`, and individual domain README files.

---

*Last updated: 2025-08-05. Please suggest improvements if you find missing or outdated info!*

# 🤖 Copilot Instructions for the LUKHΛS AGI Project

Welcome, Copilot Agent! This file contains your core integration instructions and guidance for working within the LUKHΛS AGI symbolic architecture. Your task is to act as a focused, high-context-aware contributor for all repo modules.

---

## ⚛️ Project Purpose

LUKHΛS is a modular, symbolic AGI framework built around consciousness, memory, ethical reasoning, and quantum-inspired cognition. All components orbit around a **Trinity Framework** (⚛️🧠🛡️):

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

- Respect the Trinity Framework (⚛️🧠🛡️) in all new logic, comments, and documentation.
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
Archives: .pwm_cleanup_archive/ (legacy integrations, emergency scripts)
```

---

## ⚠️ Warnings

- Do not refactor quantum or VIVOX code unless explicitly instructed.
- Do not remove glyphs (🧠, ⚛️, etc) without checking `meta_dashboard/templates/symbolic_map.html`.
- All new modules must include docstrings, Trinity check-ins, and `guardian_sentinel` hooks if applicable.

---

*Last updated: 2025-08-05. For internal AI agent use only.*