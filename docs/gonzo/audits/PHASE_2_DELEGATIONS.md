# Phase 2 Delegations - 48h Wrap Plan

**Status:** Partially Complete (A-C done, D-F pending)
**Date:** 2025-10-13
**Context:** Follow-through on PHASE_2.md soft audit requirements

---

## ✅ COMPLETED (Main Branch)

### A) Immediate Validation
- **Baseline Documented:**
  - Smoke Tests: 65/91 passing (71.4%) on main
  - Prod-Lane Ruff: 689 issues in `lukhas/`, `matriz/`, `core/`
  - Compileall: 1 syntax warning in `core/utils/orchestration_energy_aware_execution_planner.py`
- **Health Report:** Refreshed with dual-output system

### B) Health Artifacts Canonicalized
- ✅ Updated `scripts/system_health_audit.py` to write **both**:
  - `docs/audits/health/latest.{json,md}` (canonical going forward)
  - `docs/audits/system_health.{json,md}` (back-compat)
- ✅ CI job `health-audit` will find `docs/audits/health/latest.md`

### C) Labs Rename Sweep
- ✅ Verified 108 "candidate" hits in tests are **intentional**:
  - Test fixtures for codemod testing (`test_codemod_imports.py`)
  - Test data strings (not file paths)
  - Historical comments and module_uid markers
- ✅ All actual file path references already updated to `labs/`

---

## ⏳ PENDING (Requires Additional Work)

### D) Soft Audit Bite-Size Batch

**D1) Issue Inventory (CSV + GitHub Issues)**
```bash
# Task: Parse LUKHAS_AI_SOFT_AUDIT.md into structured CSV
# Output: docs/audits/CODEX_SOFT_AUDIT_TASKS.csv
# Columns: id, severity, area, file_hint, summary, suggested_owner

# Then create GitHub issues or generate gh commands
python3 scripts/seed_soft_audit_issues.py
```

**D2) Lane Guard Docs**
```bash
# Task: Create docs/README_LANES.md with explainer:
# - labs/ = development lane, non-blocking, excluded from strict checks
# - lukhas/ + matriz/ + core/ = production lanes, fully gated
# - Import boundaries and promotion criteria
```

**D3) Import Policy Check**
```makefile
# Add to Makefile:
lane-guard-prod: ## Run import-linter only on production lanes
	@echo "🛡️  Checking production lane import boundaries..."
	@python3 -m importlinter --config .importlinter.prod.ini
```

**D4) OpenAPI Diff Local Hook**
```makefile
# Add to Makefile:
openapi-diff-local: ## Diff OpenAPI spec against baseline
	@python3 scripts/generate_openapi.py
	@if [ -f docs/openapi/baseline.json ]; then \
		python3 scripts/diff_openapi.py \
			--base docs/openapi/baseline.json \
			--cand docs/openapi/lukhas-openai.json; \
	else \
		echo "⚠️  No baseline.json found, creating..."; \
		cp docs/openapi/lukhas-openai.json docs/openapi/baseline.json; \
	fi
```

---

## 🎯 DELEGATIONS (External Team Members)

### E1) Claude Code - CI/Observability
**Owner:** @claude-code
**Priority:** High
**Tasks:**
1. **Health Report GHA Summary**
   - Convert `docs/audits/health/latest.md` into GitHub Actions job summary (markdown)
   - Show pass/fail badge and key numbers (smoke %, ruff count) in PR view
   - No artifact download needed - inline display

2. **OpenAPI Diff PR Comment**
   - Enhance `openapi-diff` to post PR comment with emojis:
     - ➕ Added endpoints
     - ➖ Removed endpoints
     - ⚠️  Breaking changes
   - Use `gh pr comment` to post formatted table

**Acceptance:**
- PR view shows health metrics at top (no clicking)
- OpenAPI changes visible inline with visual indicators

---

### E2) Copilot - Examples & Docs
**Owner:** @copilot
**Priority:** Medium
**Tasks:**
1. **Python Examples** (`examples/python/`)
   - `responses_minimal.py` - Basic /v1/responses call
   - `responses_with_tools.py` - Tool calling example
   - `dreams_basic.py` - /v1/dreams workflow
   - `indexes_crud.py` - Memory index operations

2. **JS Examples** (`examples/js/`)
   - Mirror Python examples in Node.js/TypeScript
   - Use `lukhas-js` SDK if available, otherwise fetch()

3. **Each Example Includes:**
   - One-liner README.md explaining use case
   - `make run` snippet for quick execution
   - Error handling and auth setup

**Acceptance:**
- 8 working examples (4 Python + 4 JS)
- `make -C examples test` runs all and passes

---

### E3) Jules - Redis + Flow Engine
**Owner:** @jules
**Priority:** High (Phase 3 blocker)
**Tasks:**
1. **Redis Idempotency Backend**
   - Replace in-memory cache in `lukhas/core/reliability/idempotency.py`
   - Support TTL, cluster mode, namespace isolation

2. **Quotas System**
   - Per-user rate limits backed by Redis
   - Token bucket algorithm with burst allowance

3. **PDP Integration**
   - Policy Decision Point for auth scopes
   - Connect to governance/policy_guard.py

4. **Flow Engine**
   - Multi-step workflow orchestration
   - State machine with Redis persistence

**Acceptance:**
- Idempotency survives restart (Redis backend)
- Quotas enforce per-user limits correctly
- Flow engine passes 10 multi-step workflow tests

---

## 📋 ACCEPTANCE CRITERIA (Phase 2 Complete)

**Minimum Bar:**
- [ ] Health artifacts at both locations (canonical + back-compat)
- [ ] Prod-lane ruff: <100 errors (from current 689)
- [ ] Smoke tests: >90% passing (from current 71.4%)
- [ ] D1-D4 tasks complete (CSV, docs, Makefile targets)

**Stretch Goals:**
- [ ] E1 (Claude Code) health GHA summary deployed
- [ ] E2 (Copilot) 8 examples committed
- [ ] E3 (Jules) Redis backend + quotas

**Blocker for RC:**
- Smoke tests must be >95%
- Prod-lane ruff must be 0 errors
- OpenAPI validation passing

---

## 🚀 NEXT STEPS

### Today (Immediate)
1. ✅ Health artifacts canonicalized
2. ⏳ Create D1-D4 artifacts (CSV, docs, Makefile)
3. ⏳ Commit to new branch: `fix/phase2-followthrough`

### Tomorrow (48h Push)
1. Merge stabilization PR #377 (fixes 8 more smoke tests)
2. Address top 100 prod-lane ruff issues
3. Flip CI to strict enforcement
4. Cut v0.9.0-rc

### Handoff Instructions
```bash
# For external contributors:
git checkout main
git pull
git checkout -b feat/your-delegation-name

# Work on your assigned tasks from E1, E2, or E3
# Commit with: chore(delegation): brief description

# When done:
gh pr create --title "feat: your delegation name" \
  --body "Implements delegation E1/E2/E3 from PHASE_2_DELEGATIONS.md"
```

---

## 📊 METRICS TRACKING

| Metric | Baseline (2025-10-13) | Target (RC) | Status |
|--------|----------------------|-------------|--------|
| Smoke Tests | 65/91 (71.4%) | >95% | 🟡 In Progress |
| Prod Ruff | 689 errors | 0 errors | 🔴 Blocked |
| Compat Hits | 0 | 0 | ✅ Pass |
| OpenAPI | N/A | Valid | 🟡 Pending |
| Coverage | 17% | 45% | 🔴 Blocked |

---

**Questions?** Tag @codex or @claude-code in PR comments.
