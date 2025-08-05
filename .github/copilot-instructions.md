# 🤖 Copilot Instructions for LUKHAS AGI Codebase

Welcome, AI agent! This guide will help you be productive in the LUKHAS AGI codebase. Focus on these project-specific conventions, workflows, and architectural patterns:

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

- Respect the Trinity Framework (⚛️🧠🛡️) in all new logic
- Use symbolic glyphs where possible (see `meta_dashboard/templates/symbolic_map.html`)
- Check `integration_config.yaml` for global thresholds
- Log all interventions to `data/` or `memory/`
- Update `data/meta_metrics.json` if adding monitoring features

### If Unsure:

- Consult `README_NEXT_GEN.md` or individual domain README files
- Ask whether a module is production or experimental
- Use `tests/` to validate any new logic

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