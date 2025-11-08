# Jules Priority Sessions - January 8, 2025

**Created**: 2025-01-08
**Type**: Non-Test Implementation TODOs
**Total Sessions**: 5
**Automation Mode**: AUTO_CREATE_PR

---

## 🔴 CRITICAL Priority (P0)

### Session 1: Guardian Ethics DSL + Kill-Switch
**Session ID**: 9950861015326926289
**URL**: https://jules.google.com/session/9950861015326926289
**Priority**: P0 - Production Safety

**Tasks**:
1. Activate ethics DSL enforcement (currently OFF by default)
2. Implement emergency kill-switch mechanism (`/tmp/guardian_emergency_disable`)
3. Create dual-approval override runbook

**Impact**: CRITICAL - Production safety issue identified in AUDIT_07_NOV_25.md

**Expected Output**:
- Modified: `core/governance/guardian_system_integration.py`
- Created: `docs/runbooks/guardian_override_playbook.md`
- Tests: `tests/integration/governance/test_guardian_killswitch.py`

---

## 🟡 High Priority (P1)

### Session 2: Automated Cleanup - Autofix Pass
**Session ID**: 6061065372654877432
**URL**: https://jules.google.com/session/6061065372654877432
**Priority**: P1 - Quick wins

**Tasks**:
1. Create `scripts/batch_autofix.py` for systematic cleanup
2. Run: autoflake → isort → black → ruff --fix
3. Process in small batches: bridge, core, lukhas, matriz

**Impact**: Reduce 4,300+ Ruff violations, improve code quality

**Expected Output**:
- Created: `scripts/batch_autofix.py`
- Modified: All .py files in target modules (formatting only)

### Session 3: Labs Import Codemod
**Session ID**: 11824147330734113995
**URL**: https://jules.google.com/session/11824147330734113995
**Priority**: P1 - Technical debt

**Tasks**:
1. Create LibCST codemod: `scripts/codemods/replace_labs_imports.py`
2. Map `labs.*` imports to proper locations
3. Dry-run and apply modes

**Impact**: Clean up lane boundary violations

**Expected Output**:
- Created: `scripts/codemods/replace_labs_imports.py`
- Created: `tests/unit/codemods/test_replace_labs_imports.py`
- Modified: Files with labs imports (after apply)

### Session 4: SLSA CI for Supply Chain Security
**Session ID**: 919280777160162153
**URL**: https://jules.google.com/session/919280777160162153
**Priority**: P1 - Security

**Tasks**:
1. Create GitHub workflow: `.github/workflows/slsa-provenance.yml`
2. Implement provenance generation: `scripts/slsa/generate_provenance.py`
3. Cosign signature integration
4. First 10 modules: matriz, lukhas.identity, lukhas.memory, core.governance, etc.

**Impact**: SLSA Level 2 compliance, supply chain integrity

**Expected Output**:
- Created: `.github/workflows/slsa-provenance.yml`
- Created: `scripts/slsa/generate_provenance.py`
- Created: `docs/security/SLSA_COMPLIANCE.md`

---

## 🟢 Important (P2)

### Session 5: API Documentation Refresh
**Session ID**: 3809108493363703079
**URL**: https://jules.google.com/session/3809108493363703079
**Priority**: P2 - Developer experience

**Tasks**:
1. Complete API reference with examples: `docs/api/COMPLETE_REFERENCE.md`
2. Create getting started guides
3. Update all documentation timestamps
4. Add missing code examples

**Impact**: Improve developer onboarding and API adoption

**Expected Output**:
- Updated: `docs/api/COMPLETE_REFERENCE.md`
- Created: `docs/guides/GETTING_STARTED.md`
- Created: `docs/guides/LUKHAS_WITH_OPENAI.md`
- Created: Multiple example files

---

## Context & Justification

**From**: Comprehensive TODO analysis across codebase
**Sources**:
- `docs/gonzo/AUDIT_07_NOV_25.md` - Production readiness audit
- `tasks/PRIORITY_TODOs.md` - P1/P2/P3 task list
- `docs/gonzo/T4_CHANGES.md` - T4 Intent Registry proposal
- `docs/project_status/JULES_TODO_ANALYSIS.md` - 964 TODOs across 414 files

**Exclusions**: Test creation tasks (handled by separate test-focused agent)

**Analysis**:
- Found 964 TODOs across 414 files
- Found 57 untested modules (1000+ lines each)
- Identified Guardian controls as CRITICAL (ethics DSL off by default)
- Prioritized P1 tasks: Autofix, Labs codemod, SLSA CI
- Selected documentation refresh for developer experience (P2)

---

## Monitoring & Next Steps

**Monitor Sessions**:
- Dashboard: https://jules.google.com/
- Check status: `python3 scripts/list_all_jules_sessions.py`

**Review Workflow**:
1. Jules processes sessions (AUTO_CREATE_PR mode)
2. PRs automatically created when ready
3. Review PRs in GitHub
4. Merge after approval
5. Verify changes with `make test`, `make lane-guard`

**Daily Quota**:
- Current usage: 7/100 sessions used today (2 test sessions + 5 priority sessions)
- Remaining: 93 sessions available

**Success Metrics**:
- P0: Guardian controls active, kill-switch implemented
- P1: Ruff violations reduced, labs imports eliminated, SLSA workflow active
- P2: Complete API docs with examples

---

## Related Sessions

**Previous Sessions** (from today):
- Test sessions for Claude API bridge (2 sessions):
  - Session 4345524498649388654: test_env_loader.py
  - Session 16574199843217941387: test_anthropic_wrapper.py

**Total Sessions Today**: 7/100

---

## Notes

**T4 Conventions**:
- All commits follow T4 minimal standard
- Academic tone, no hype words
- Include Problem/Solution/Impact in commit bodies
- Attach LLM trailers when relevant

**Lane Boundaries**:
- All changes respect lane isolation
- Verify with `make lane-guard` after merge
- No `candidate/` imports in `lukhas/`

**Testing Requirements**:
- All code changes must pass existing tests
- New functionality requires new tests
- Run `make smoke` before creating PR
- Full test suite: `make test-all`

**Security**:
- SLSA workflow uses keyless signing (GitHub OIDC)
- No hardcoded secrets in any code
- Guardian kill-switch requires senior authorization

---

Generated with Claude Code (claude.com/code)
