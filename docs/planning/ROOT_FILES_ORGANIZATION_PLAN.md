---
status: wip
type: documentation
---
# Root Files Organization Plan

## Analysis Date: 2025-08-10

This document analyzes all files currently in the root directory and recommends their proper organization.

## Files That MUST Stay in Root

### Core Configuration (✅ KEEP IN ROOT)
- `.gitignore` - Git configuration
- `.env` - Environment variables (local)
- `.env.example` - Environment template
- `LICENSE` - Legal requirement
- `README.md` - Primary documentation
- `Makefile` - Build automation
- `pyproject.toml` - Python project config
- `requirements.txt` - Python dependencies
- `setup.py` - Package installation
- `package.json` - Node.js dependencies
- `package-lock.json` - Node.js lock file
- `pytest.ini` - Test configuration
- `pyrightconfig.json` - Type checking config
- `docker-compose.yml` - Docker orchestration
- `Dockerfile` - Container definition

### Project Files (✅ KEEP IN ROOT)
- `main.py` - Main entry point
- `lukhas_config.yaml` - Core LUKHAS config
- `modulation_policy.yaml` - Core policy config

### Development Tools (✅ KEEP IN ROOT)
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.flake8` - Linting configuration
- `pip-constraints.txt` - Dependency constraints

### IDE Configuration (✅ KEEP IN ROOT)
- `Lukhas.code-workspace` - VS Code workspace
- `claude_desktop_config.json` - Claude Desktop config

## Files to Move to `/docs/`

### Project Documentation (→ `/docs/`)
- `AI_COLLABORATION_ACKNOWLEDGMENT.md` → `/docs/collaboration/`
- `AI_INTEGRATION_SETUP.md` → `/docs/setup/`
- `AI_SETUP_CURRENT.md` → `/docs/setup/`
- `AUTHORS.md` → `/docs/`
- `CLAUDE.md` → Root (special - AI assistant instructions)
- `INFO_README.md` → `/docs/`
- `QUICK_START.md` → `/docs/`
- `README_NEXT_GEN.md` → `/docs/architecture/`
- `README_TRINITY.md` → `/docs/architecture/`
- `PROVENANCE.yaml` → `/docs/`

### Executive & Business Documents (→ `/docs/executive/`)
- `CEO_EXECUTIVE_REVIEW_AUGUST_2025.md`
- `INVESTOR_OVERVIEW.md`
- `PROFESSIONAL_DEVELOPMENT_ROADMAP.md`

### Vision & Roadmap Documents (→ `/docs/roadmap/`)
- `LUKHAS_UNIVERSAL_LANGUAGE_ROADMAP.md`
- `OPENAI_LUKHAS_2026-2030_COLLABORATION_VISION.md`
- `OPENAI_LUKHAS_2030_COLLABORATION_VISION.md`
- `ROADMAP_OPENAI_ALIGNMENT.md`
- `UNIVERSAL_SYMBOL_COMMUNICATION_BLUEPRINT.md`
- `UNIVERSAL_SYMBOL_TRINITY_BLUEPRINT.md`

### Planning Documents (→ `/docs/planning/`)
- `LUKHAS_ACTION_PLANS.md`
- `HIDDEN_POWER_ACTION_PLAN.md`
- `IMMEDIATE_ACTIONS.md`
- `IMMEDIATE_NEXT_STEPS.md`
- `TASKS_OPENAI_ALIGNMENT.md`
- `CLAUDE_CODE_TASKS.md`
- `.copilot_tasks.md`

### Reports & Analysis (→ `/docs/reports/`)
- `COMPREHENSIVE_STRESS_TEST_RESULTS_AUG_7_2025.md`
- `CRITICAL_FIX_NEEDED_model_communication_engine.md`
- `CRITICAL_GAPS_IMPROVEMENT_PLAN.md`
- `ETHICAL_ALIGNMENT_BREAKTHROUGH_ANALYSIS.md`
- `VALIDATION_REPORT.md`

### Integration & API Documents (→ `/docs/integration/`)
- `LUKHAS_DREAM_API_COLLABORATION.md`
- `LUKHAS_AI_QUICK_REFERENCE.md`
- `openapi.json` → `/docs/api/` or `/out/`

### Sprint & Release Documents (→ `/docs/releases/`)
- `PR1_COMPLETE.md`
- `PR2_COMPLETE.md`
- `SPRINT_COMPLETE.md`

### OpenAI Integration (→ `/docs/openai/`)
- `FINAL_OPENAI_STATUS.md`
- `INTEGRATION_TEST_CHECKLIST.md`
- `OPENAI_INPUT_OUTPUT_REPORT.md`
- `PRODUCTION_TEST_REPORT.md`
- `TOOL_EXECUTOR_IMPLEMENTATION.md`
- `TOOL_INTEGRATION_COMPLETE.md`
- `GPT5_AUDITS_LUKHAS.md`
- `IMPLEMENTATION_SUMMARY.md`

## Files to Move to `/scripts/`

### Python Scripts (→ `/scripts/`)
- `IMMEDIATE_CONFIG_ANALYSIS.py`
- `launch_readiness_check.py`
- `live_integration_test.py`
- `live_openai_smoke_test.py`
- `mock_integration_demo.py`
- `production_test_mock.py`
- `production_test_suite.py`
- `smoke_check.py`
- `demo_tool_gating.py`
- `demo_tool_governance.py`
- `governance_extended.py`

### Shell Scripts (→ `/scripts/`)
- `format_code.sh`
- `setup_test_environment.sh`
- `vs_code_reset_commands.sh`

## Files to Move to `/tests/`

### Test Files (→ `/tests/integration/`)
- `test_complete_openai_flow.py`
- `test_final_integration.py`
- `test_lukhas_ai_setup.py`
- `test_openai_connection.py`
- `test_openai_responses.py`
- `test_tool_analytics.py`
- `test_tool_executor.py`
- `test_tool_integration.py`
- `test_tool_integration_complete.py`

## Files to Move to Other Locations

### Temporary/Cache Files (→ Delete or `.gitignore`)
- `.coverage` → Delete (generated file)
- `.DS_Store` → Delete (macOS file)
- `claude_context.txt` → `/tmp/` or delete

### Backup Files (→ `/backups/` or delete)
- `intelligence_engine.py.bkup`

## Recommended Directory Structure

```
LUKHAS/
├── 📄 Root Configuration Files (keep minimal)
│   ├── .env, .gitignore, LICENSE, README.md
│   ├── Makefile, requirements.txt, setup.py
│   ├── pyproject.toml, pytest.ini
│   └── main.py, lukhas_config.yaml
│
├── 📁 docs/
│   ├── 📁 setup/
│   ├── 📁 architecture/
│   ├── 📁 roadmap/
│   ├── 📁 planning/
│   ├── 📁 reports/
│   ├── 📁 integration/
│   ├── 📁 openai/
│   ├── 📁 executive/
│   ├── 📁 releases/
│   └── 📁 api/
│
├── 📁 scripts/
│   ├── 📁 integration/
│   ├── 📁 testing/
│   └── 📁 utilities/
│
├── 📁 tests/
│   ├── 📁 integration/
│   └── 📁 tools/
│
└── 📁 perf/
    └── k6_smoke.js
```

## Migration Script

```bash
#!/bin/bash
# organize_root_files.sh

# Create directories
mkdir -p docs/{setup,architecture,roadmap,planning,reports,integration,openai,executive,releases,api,collaboration}
mkdir -p scripts/{integration,testing,utilities}
mkdir -p tests/{integration,tools}

# Move documentation files
mv AI_COLLABORATION_ACKNOWLEDGMENT.md docs/collaboration/ 2>/dev/null
mv AI_INTEGRATION_SETUP.md AI_SETUP_CURRENT.md docs/setup/ 2>/dev/null
mv README_NEXT_GEN.md README_TRINITY.md docs/architecture/ 2>/dev/null
mv CEO_EXECUTIVE_REVIEW_AUGUST_2025.md INVESTOR_OVERVIEW.md PROFESSIONAL_DEVELOPMENT_ROADMAP.md docs/executive/ 2>/dev/null

# Move roadmap files
mv LUKHAS_UNIVERSAL_LANGUAGE_ROADMAP.md OPENAI_LUKHAS_*.md ROADMAP_OPENAI_ALIGNMENT.md docs/roadmap/ 2>/dev/null
mv UNIVERSAL_SYMBOL_*.md docs/roadmap/ 2>/dev/null

# Move planning files
mv LUKHAS_ACTION_PLANS.md HIDDEN_POWER_ACTION_PLAN.md IMMEDIATE_*.md docs/planning/ 2>/dev/null
mv TASKS_OPENAI_ALIGNMENT.md CLAUDE_CODE_TASKS.md .copilot_tasks.md docs/planning/ 2>/dev/null

# Move reports
mv COMPREHENSIVE_STRESS_TEST_*.md CRITICAL_*.md ETHICAL_*.md VALIDATION_REPORT.md docs/reports/ 2>/dev/null

# Move OpenAI docs
mv FINAL_OPENAI_STATUS.md INTEGRATION_TEST_CHECKLIST.md OPENAI_INPUT_OUTPUT_REPORT.md docs/openai/ 2>/dev/null
mv PRODUCTION_TEST_REPORT.md TOOL_*.md GPT5_*.md IMPLEMENTATION_SUMMARY.md docs/openai/ 2>/dev/null

# Move releases
mv PR*_COMPLETE.md SPRINT_COMPLETE.md docs/releases/ 2>/dev/null

# Move scripts
mv launch_readiness_check.py live_*.py mock_*.py production_test_*.py smoke_check.py scripts/testing/ 2>/dev/null
mv demo_*.py governance_extended.py scripts/integration/ 2>/dev/null
mv IMMEDIATE_CONFIG_ANALYSIS.py scripts/utilities/ 2>/dev/null
mv *.sh scripts/utilities/ 2>/dev/null

# Move tests
mv test_*.py tests/integration/ 2>/dev/null

# Move other files
mv openapi.json docs/api/ 2>/dev/null
mv AUTHORS.md INFO_README.md QUICK_START.md PROVENANCE.yaml docs/ 2>/dev/null
mv LUKHAS_DREAM_API_COLLABORATION.md LUKHAS_AI_QUICK_REFERENCE.md docs/integration/ 2>/dev/null

# Clean up
rm -f .DS_Store .coverage claude_context.txt *.bkup

echo "✅ Root directory organized!"
```

## Benefits of This Organization

1. **Cleaner Root**: Only essential config files remain
2. **Better Discovery**: Related documents grouped together
3. **Easier Navigation**: Clear hierarchy
4. **Professional Structure**: Standard Python project layout
5. **Git-Friendly**: Less clutter in root diffs
6. **IDE-Friendly**: Better project exploration

## Priority Actions

1. **High Priority**: Move all test files to `/tests/`
2. **High Priority**: Move all scripts to `/scripts/`
3. **Medium Priority**: Organize documentation in `/docs/`
4. **Low Priority**: Archive old sprint/release docs

## Files Requiring Special Attention

- `CLAUDE.md` - Should stay in root (AI assistant instructions)
- `main.py` - Must stay in root (entry point)
- `openapi.json` - Consider generating to `/out/` instead
- `.coverage` - Should be in `.gitignore`
