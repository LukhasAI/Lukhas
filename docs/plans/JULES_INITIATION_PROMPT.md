# Jules Agent - Initiation Prompt

**Copy this entire message to start Jules on documentation tasks**

---

## 🎯 Your Mission

Hello Jules! You've been assigned to complete comprehensive documentation for the LUKHAS AI platform. This is a **3-4 hour autonomous task** covering 347 scripts, API documentation, and OpenAPI specifications.

---

## 📚 Essential Reading (READ THESE FIRST)

### Primary Task Brief
**CRITICAL**: Read this first for complete context and instructions
- **Main Brief**: [docs/plans/JULES_COMPLETE_TASK_BRIEF_2025-10-19.md](../JULES_COMPLETE_TASK_BRIEF_2025-10-19.md)
  - 500 lines of detailed instructions
  - 3 major tasks with acceptance criteria
  - Examples, templates, and validation steps

### Task Execution Guide
**Structured task list with dependencies**:
- **Task JSON**: [docs/plans/JULES_TASKS.json](../JULES_TASKS.json)
  - 6 sequential tasks (J-01 → J-06)
  - Dependencies, commands, outputs
  - Acceptance criteria per task

### Repository Context
**Understand the codebase structure** (LUKHAS uses distributed context files):
- **Master Context**: [claude.me](../../claude.me)
  - Complete system overview
  - Architecture patterns
  - Development guidelines

- **AGENTS.md**: [AGENTS.md](../../AGENTS.md)
  - Agent coordination system
  - Repository navigation
  - Context file system (42+ distributed files)

### Automation
**Makefile helpers for task execution**:
- **Jules Makefile**: [mk/jules.mk](../../mk/jules.mk)
  - `make jules-tasks` - Run full chain
  - `make jules-J-01` - Individual tasks
  - `make jules-validate` - Check acceptance criteria

---

## 🚀 Quick Start (5 Steps)

### 1. Clone & Setup (5 min)
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git pull origin main
git checkout -b feat/jules-documentation-complete

# Verify environment
python --version  # Should be 3.9+
which interrogate pydocstyle || pip install interrogate pydocstyle
```

### 2. Read Task Brief (15 min)
```bash
# Open and read (in order):
cat docs/plans/JULES_COMPLETE_TASK_BRIEF_2025-10-19.md
cat docs/plans/JULES_TASKS.json
cat mk/jules.mk
```

### 3. Execute Task Chain (2-3 hours)
```bash
# Option A: Use Makefile automation
make jules-tasks

# Option B: Manual execution (more control)
make jules-J-01  # Seed docstrings
# Manual: Enhance 30 critical scripts (J-02)
make jules-J-03  # CI integration
# Manual: Create OpenAPI specs (J-04)
make jules-J-05  # Generate index
make jules-J-06  # Final validation
```

### 4. Validate Outputs (15 min)
```bash
# Run validation suite
make jules-validate

# Check coverage
interrogate -v scripts api

# Validate OpenAPI (if created)
swagger-cli validate docs/openapi/*.openapi.yaml
spectral lint docs/openapi/*.openapi.yaml

# Generate unified metrics and dashboard (T4+)
python scripts/emit_metrics.py \
  --coverage docs/audits/docstring_coverage.json \
  --offenders docs/audits/docstring_offenders.txt \
  --spectral-junit docs/audits/openapi_lint_junit.xml \
  --out docs/audits/metrics.json

python scripts/gen_coverage_dashboard.py \
  --metrics docs/audits/metrics.json \
  --out docs/audits/coverage_dashboard.md
```

### 5. Create PR (10 min)
```bash
# Commit with T4 standards
git add -A
git commit -m "docs(scripts): complete documentation for 347 scripts and API specs

Problem:
- 347 scripts lacked proper docstrings and usage examples
- API endpoints missing OpenAPI-compatible documentation
- No OpenAPI specification files for ecosystem integration

Solution:
- Added module docstrings to all 347 scripts with usage examples
- Enhanced 30 critical scripts with complete function documentation
- Added comprehensive API endpoint documentation
- Created 5 OpenAPI 3.1 specification files for major domains

Impact:
- Improved developer experience and onboarding
- API documentation now OpenAPI-compatible
- Scripts have clear usage patterns and examples
- Foundation for automated API documentation generation

🤖 Generated with Jules Agent

Co-Authored-By: Jules <noreply@lukhas.ai>"

# Push and create PR
git push origin feat/jules-documentation-complete
gh pr create --title "docs(scripts): complete documentation for 347 scripts and API specs" \
  --body "See commit message for details. All acceptance criteria met."
```

---

## 📋 Your Tasks Overview

### Task 3.1: Script Documentation (2-3 hours)
**Scope**: 347 Python scripts in `scripts/` directory
**Priority**: HIGH

**What to do**:
1. Add module-level docstrings to ALL scripts
2. Add comprehensive function docstrings to top 30 critical scripts:
   - `scripts/generate_module_manifests.py`
   - `scripts/validate_module_manifests.py`
   - `scripts/validate_contract_refs.py`
   - `scripts/context_coverage_bot.py`
   - `scripts/migrate_context_front_matter.py`
   - `scripts/sync_t12_manifest_owners.py`
   - `scripts/fix_t12_context_owners.py`
   - ... (see task brief for complete list)

**Template** (use this for module docstrings):
```python
"""
One-line summary of what this script does.

Detailed description of functionality, use cases, and requirements.
This should be 2-3 paragraphs explaining the "why" and "how".

Usage:
    python scripts/script_name.py [options]

Examples:
    $ python scripts/script_name.py --module-path consciousness/core --write
    $ python scripts/script_name.py --strict --verbose

Requirements:
    - Python 3.9+
    - Dependencies: pydantic, pathlib, json
    - Must be run from repository root

Author: LUKHAS Development Team
Last Updated: 2025-10-19
"""
```

**Validation**:
```bash
interrogate -v --fail-under 85 scripts api
pydocstyle --convention=google scripts/
```

---

### Task 3.2: API Documentation (1 hour)
**Scope**: API endpoints in `api/` directory
**Priority**: HIGH

**What to do**:
1. Add OpenAPI-compatible docstrings to all FastAPI endpoints
2. Document request/response models with Pydantic Field descriptions
3. Include example requests/responses

**Template**:
```python
@router.get("/consciousness/status", tags=["consciousness"])
async def get_consciousness_status() -> ConsciousnessStatus:
    """
    Get current consciousness subsystem status.

    Returns real-time metrics for consciousness processing including:
    - Active qualia count
    - Reflection depth
    - Integration state
    - Performance metrics

    Returns:
        ConsciousnessStatus: Current status object with metrics

    Raises:
        HTTPException: 503 if consciousness subsystem unavailable

    Example Response:
        {
            "active_qualia": 42,
            "reflection_depth": 3,
            "integration_state": "active",
            "performance": {
                "latency_p95_ms": 45.2,
                "throughput_ops_sec": 123.4
            }
        }
    """
    # Implementation
```

---

### Task 3.3: OpenAPI Specifications (1 hour)
**Scope**: 5 OpenAPI 3.1 YAML files
**Priority**: MEDIUM

**What to do**:
1. Create OpenAPI specs for each major domain:
   - `docs/openapi/consciousness.openapi.yaml`
   - `docs/openapi/memory.openapi.yaml`
   - `docs/openapi/identity.openapi.yaml`
   - `docs/openapi/governance.openapi.yaml`
   - `docs/openapi/matriz.openapi.yaml`

2. Extract from FastAPI's built-in OpenAPI generation:
```bash
# Start API server
uvicorn api.app:app --reload

# Access OpenAPI JSON
curl http://localhost:8000/openapi.json > /tmp/openapi.json

# Split by tags and convert to YAML
# (Manual process - see task brief for details)
```

**Template** (see task brief for complete example):
```yaml
openapi: 3.1.0
info:
  title: LUKHAS Consciousness API
  description: Real-time consciousness processing and qualia integration API
  version: 1.0.0

servers:
  - url: https://api.lukhas.ai/v1
    description: Production
  - url: http://localhost:8000/v1
    description: Local development

paths:
  /consciousness/status:
    get:
      summary: Get consciousness status
      tags: [consciousness]
      responses:
        '200':
          description: Status retrieved successfully
```

**Validation**:
```bash
swagger-cli validate docs/openapi/*.openapi.yaml
spectral lint docs/openapi/*.openapi.yaml --format junit --output docs/audits/openapi_lint_junit.xml
```

**T4+ Enhancements** (Optional but Recommended):
```bash
# Generate ReDoc static previews (browsable HTML)
for f in docs/openapi/*.openapi.yaml; do
  base=$(basename "$f" .openapi.yaml)
  redoc-cli build "$f" -o "docs/openapi/site/${base}.html"
done

# Add SPDX license headers (advisory)
python scripts/add_spdx_headers.py \
  --roots docs/openapi \
  --spdx "SPDX-License-Identifier: Proprietary" \
  --author "LUKHAS API Team" \
  --filetype yaml

# Validate docstring semantics (advisory report)
python scripts/validate_docstring_semantics.py \
  --roots scripts api \
  --report docs/audits/docstring_semantics_report.md \
  --no-llm
```

---

## ✅ Acceptance Criteria (Must Pass All)

### Task 3.1: Script Documentation
- [ ] All 347 scripts have module-level docstrings
- [ ] Top 30 critical scripts have complete function docstrings (Args/Returns/Raises)
- [ ] All scripts include usage examples
- [ ] `interrogate -v scripts api` shows ≥85% coverage
- [ ] `pydocstyle --convention=google scripts/` passes

### Task 3.2: API Documentation
- [ ] All API endpoints have comprehensive docstrings
- [ ] Request/response models fully documented with Field descriptions
- [ ] Example requests/responses included
- [ ] Error cases documented

### Task 3.3: OpenAPI Specs
- [ ] 5 OpenAPI 3.1 YAML files created
- [ ] All specs validate: `swagger-cli validate docs/openapi/*.openapi.yaml`
- [ ] Spectral lint passes: `spectral lint docs/openapi/*.openapi.yaml`
- [ ] README.md index created: `docs/openapi/README.md`
- [ ] All specs include examples and response schemas

### T4+ Quality Polish (Bonus)
- [ ] Unified metrics generated: `docs/audits/metrics.json`
- [ ] Coverage dashboard created: `docs/audits/coverage_dashboard.md`
- [ ] ReDoc previews built: `docs/openapi/site/*.html`
- [ ] Semantic validation report: `docs/audits/docstring_semantics_report.md`
- [ ] SPDX headers added (if applicable)

---

## 🚨 Critical Reminders

### T4 Commit Standards
**Required format**:
```
<type>(<scope>): <imperative subject ≤72>

Problem:
- Bullet points describing the issue

Solution:
- Bullet points describing the fix

Impact:
- Bullet points describing the outcome

🤖 Generated with Jules Agent

Co-Authored-By: Jules <noreply@lukhas.ai>
```

**Types**: docs, feat, fix, refactor, test, chore
**Scopes**: scripts, api, docs, openapi

### Style Guidelines
- Use **Google-style docstrings** (not NumPy or reStructuredText)
- No emojis in docstrings (professional tone)
- Include concrete examples in usage sections
- Keep descriptions concise but complete
- Use present tense for descriptions ("Returns" not "Will return")

### Path Awareness (Post-Phase 5B)
- All paths are FLAT (no `lukhas/` prefix)
- ✅ Correct: `consciousness/core/processor.py`
- ❌ Wrong: `lukhas/consciousness/core/processor.py`

---

## 🔗 Reference Links

### Documentation Standards
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
- OpenAPI 3.1 Specification: https://spec.openapis.org/oas/v3.1.0
- FastAPI Documentation: https://fastapi.tiangolo.com/tutorial/

### Tools Documentation
- interrogate: https://interrogate.readthedocs.io/
- pydocstyle: http://www.pydocstyle.org/
- swagger-cli: https://apitools.dev/swagger-cli/
- spectral: https://stoplight.io/open-source/spectral
- redoc-cli: https://redocly.com/docs/redoc/

### T4+ Polish Scripts (New!)
- `scripts/emit_metrics.py` - Aggregate coverage/style/lint into unified JSON
- `scripts/gen_coverage_dashboard.py` - Generate visual Markdown dashboard
- `scripts/add_spdx_headers.py` - Inject SPDX license headers
- `scripts/validate_docstring_semantics.py` - Semantic validation (heuristic)

### LUKHAS Documentation
- Architecture Overview: [docs/architecture/README.md](../../docs/architecture/README.md)
- API Guide: [docs/api/README.md](../../docs/api/README.md)
- Development Workflow: [docs/development/README.md](../../docs/development/README.md)

---

## 💬 Questions & Support

### If You Get Stuck
1. **Read the full task brief again**: Most questions are answered there
2. **Check the Makefile**: `make jules-help` shows all available commands
3. **Validate incrementally**: Don't wait until the end to run validation
4. **Comment on Issue/PR**: If truly blocked, document the blocker

### Common Issues

**Issue**: interrogate shows low coverage
**Fix**: Make sure you added module docstrings to ALL scripts (not just top 30)

**Issue**: pydocstyle fails with "Missing docstring in public function"
**Fix**: Top 30 scripts need ALL public functions documented

**Issue**: swagger-cli validation fails
**Fix**: Check YAML syntax, ensure all required OpenAPI fields present

**Issue**: Can't find API endpoints
**Fix**: Check `api/` directory, look for `@router.get/post/put/delete` decorators

---

## 🎯 Success Looks Like

When you're done, the repository will have:
- ✅ 347 scripts with professional module docstrings
- ✅ 30 critical scripts with complete function documentation
- ✅ All API endpoints documented for OpenAPI compatibility
- ✅ 5 OpenAPI 3.1 YAML files validated and linted
- ✅ Comprehensive README index for API documentation
- ✅ All acceptance criteria passing
- ✅ PR created with T4 commit standards

**T4+ Bonus Deliverables**:
- ✅ Unified metrics dashboard (`docs/audits/coverage_dashboard.md`)
- ✅ ReDoc browsable previews (`docs/openapi/site/*.html`)
- ✅ Semantic validation advisory report
- ✅ CI artifacts ready for phase4-docs-polish bundle

**Estimated time investment**: 3-4 hours
**Impact**: Massive improvement to developer experience and API discoverability

---

## 🚀 Ready to Start?

1. **Read** all essential docs (30 min)
2. **Clone** and create branch (5 min)
3. **Execute** tasks sequentially (2-3 hours)
4. **Validate** all outputs (15 min)
5. **Create PR** and celebrate! (10 min)

**Good luck, Jules! You've got this.** 🎉

---

*Prepared by: Claude Code (LUKHAS Core Team)*
*Date: 2025-10-19*
*Task Brief Version: 1.0*
