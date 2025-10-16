coo# Task Assignments - Claude Code Coordination Role
**Created**: 2025-10-15 | **Branch**: `chore/claude/coordination-dashboard` | **Worktree**: `Lukhas-claude-coordinator`

---

## 🎯 Claude Code Role Definition

**Primary Responsibilities**:
- **Task Allocation & Coordination**: Assign tasks to Codex/Copilot, track progress
- **Review Gate Authority**: Review critical PRs (Guardian/Identity/Consciousness changes)
- **Verification & Integration**: Validate cross-system changes, ensure architectural alignment
- **Pre-Audit Guardrails**: Execute pre-GPT Pro research audit checks
- **Coordination Dashboard**: Maintain real-time progress tracking

**NOT Primary Owner**: Claude Code reviews but doesn't execute most code tasks (delegated to Codex/Copilot)

---

## 📋 Complete Task Assignment Table

### Top-5 "Do Now" Tasks (2–4 Hour Wins)

| # | Task | Owner | Risk | Time | Claude Role | Priority | Files |
|---|------|-------|------|------|-------------|----------|-------|
| **1** | Shadow-Diff Harness | **Codex** | LOW | 2-3h | Review PR | **HIGH** | `scripts/shadow_diff.py`, `Makefile` |
| **2** | Golden Token Kit + Fixtures | **Codex** + Copilot | LOW | 2h | Review fixtures | **HIGH** | `tests/fixtures/tokens.py`, `configs/guardian/policies.dev.yaml` |
| **3** | Streaming RL Headers (SSE) | **Codex** | LOW | 2-3h | Review PR | **MEDIUM** | `lukhas/adapters/openai/api.py`, `tests/smoke/` |
| **4** | Auto-Backoff Hints in 429 | **Codex** | LOW | 1-2h | Review PR | **MEDIUM** | `lukhas/adapters/openai/api.py`, `tests/smoke/` |
| **5** | RC Soak Sentinel | **Copilot** | LOW | 2-3h | Review workflow | **HIGH** | `.github/workflows/`, `scripts/rc_soak_sentinel.py` |

### High-Impact Quick Wins (Pick 4–6 in Parallel)

| # | Task | Owner | Risk | Time | Claude Role | Priority | Files |
|---|------|-------|------|------|-------------|----------|-------|
| **A** | Idempotency Redis E2E | **Codex** | LOW | 2h | Review tests | **MEDIUM** | `tests/e2e/test_idempotency_redis.py` |
| **B** | Circuit-Breaker to MATRIZ | **Codex** | MEDIUM | 3h | **CRITICAL REVIEW** | **HIGH** | `matriz/core/`, `lukhas/adapters/` |
| **C** | Log Redaction v2 | **Codex** | LOW | 2h | Review tests | **MEDIUM** | `tests/unit/test_log_redaction.py` |
| **D** | SDK Rate-Limit Snippets | **Copilot** | LOW | 1-2h | Review docs | **LOW** | `docs/examples/`, `sdk/` |
| **E** | PR Magic Comment Triage | **Copilot** | LOW | 2h | Review workflow | **LOW** | `.github/workflows/` |
| **F** | OpenAPI Drift Sentinel | **Codex** | LOW | 1h | Review CI | **MEDIUM** | `.github/workflows/`, `tests/contract/` |
| **G** | Tenant Sandbox Starter | **Copilot** | LOW | 2-3h | Review policies | **MEDIUM** | `configs/guardian/policies.sandbox.yaml` |
| **H** | RC Promotion Script | **Copilot** | LOW | 2h | Review script | **HIGH** | `scripts/promote_rc_to_ga.sh` |

### Hygiene Slices (≤20 Files per Slice)

| # | Task | Owner | Risk | Time | Claude Role | Priority | Files |
|---|------|-------|------|------|-------------|----------|-------|
| **E402-1** | E402 Batch 1 (≤20 files) | **Codex** | LOW | 30min | Review imports | **MEDIUM** | See `/tmp/e402_batch1.txt` |
| **Safe-1** | Safe Autofix (W293/F841/I001) | **Codex** | LOW | 15min | Review changes | **LOW** | `lukhas/adapters/openai/`, `lukhas/core/reliability/` |

---

## 🎯 Claude Code Execution Tasks (Direct Ownership)

These are tasks Claude Code should execute directly (not delegate):

### Task CC-1: Pre-Audit Guardrails Checklist ✅

**Priority**: **CRITICAL** (blocks GPT Pro research audit)
**Time**: 30 minutes
**Branch**: `chore/claude/coordination-dashboard` (current)

**Deliverables**:
1. Run `make state-sweep` and save to `docs/audits/live/<timestamp>/`
2. Generate shadow-diff report (depends on Task #1 completion)
3. Confirm `compat-enforce` is green
4. Validate OpenAPI spec: `make openapi-spec && make openapi-headers-guard`
5. Create pre-audit checklist document

**Files**:
- `docs/audits/pre-audit/GUARDRAILS_CHECKLIST.md`
- `docs/audits/live/<timestamp>/state_sweep.json`
- `docs/audits/shadow/<timestamp>/` (after Task #1)

**Accept**:
- ✅ All 4 guardrails pass
- ✅ Artifacts saved in `docs/audits/`
- ✅ Checklist document committed

---

### Task CC-2: Coordination Dashboard (Real-Time Progress) 📊

**Priority**: **HIGH**
**Time**: 1 hour
**Branch**: `chore/claude/coordination-dashboard` (current)

**Deliverables**:
1. `docs/plans/COORDINATION_DASHBOARD.md` - Real-time progress tracking
2. Task status JSON: `docs/plans/task_status.json`
3. Daily snapshot script: `scripts/coordination/daily_snapshot.sh`
4. Progress visualization (Markdown table + JSON for automation)

**Files**:
- `docs/plans/COORDINATION_DASHBOARD.md`
- `docs/plans/task_status.json`
- `scripts/coordination/daily_snapshot.sh`
- `Makefile` (add `coord-snapshot` target)

**Accept**:
- ✅ Dashboard shows all task statuses
- ✅ JSON parseable for automation
- ✅ Daily snapshot command works

---

### Task CC-3: Critical Review - Circuit-Breaker to MATRIZ 🔍

**Priority**: **CRITICAL** (after Task B completion by Codex)
**Time**: 1 hour
**Branch**: Review PR from Codex

**Review Checklist**:
1. MATRIZ integration preserves reasoning chain provenance
2. Breaker state exposed in healthz endpoint
3. Fallback mode documented and tested
4. No silent failures (all errors logged with context)
5. Metrics emitted: `matriz_breaker_state`, `matriz_breaker_trips`
6. Lane boundaries respected (no `candidate/` imports in `lukhas/`)

**Files to Review**:
- `matriz/core/orchestrator.py`
- `lukhas/adapters/matriz_adapter.py` (or equivalent)
- `tests/unit/test_circuit_breaker.py`
- `tests/integration/test_matriz_fallback.py`

**Accept**:
- ✅ All checklist items verified
- ✅ Tests cover breaker trip/reset scenarios
- ✅ Documentation updated

---

### Task CC-4: Guardian Policy Fixtures Review 🛡️

**Priority**: **HIGH** (after Task #2 completion by Codex)
**Time**: 30 minutes
**Branch**: Review PR from Codex

**Review Checklist**:
1. `policies.dev.yaml` clearly labeled "NOT for production"
2. Scopes align with OpenAPI operations
3. Token fixtures use deterministic generation (not hardcoded secrets)
4. Smoke tests work in both `permissive` and `strict` modes
5. Documentation warns about dev-only usage

**Files to Review**:
- `tests/fixtures/tokens.py`
- `configs/guardian/policies.dev.yaml`
- `docs/gonzo/dev/POLICY_FIXTURES.md`

**Accept**:
- ✅ No production secrets in fixtures
- ✅ Clear dev/prod separation documented
- ✅ Smoke tests pass in both modes

---

### Task CC-5: OpenAPI Parity Validation (Post-Tasks #1, #3, #4) ✅

**Priority**: **HIGH** (after facade changes)
**Time**: 20 minutes
**Branch**: Review combined changes

**Validation Steps**:
1. Regenerate OpenAPI spec: `make openapi-spec`
2. Validate spec: `openapi-spec-validator docs/openapi/lukhas-openapi.json`
3. Run facade smoke: `bash scripts/smoke_test_openai_facade.sh`
4. Check header parity (both RL header families present)
5. Verify streaming headers (SSE start + optional trailer)

**Files**:
- `docs/openapi/lukhas-openapi.json`
- `lukhas/adapters/openai/api.py`

**Accept**:
- ✅ Spec validates without errors
- ✅ Facade smoke tests pass
- ✅ Headers match OpenAI envelope structure

---

### Task CC-6: Integration Test Suite Validation 🧪

**Priority**: **MEDIUM** (after major tasks complete)
**Time**: 30 minutes
**Branch**: `main` (after PRs merge)

**Validation Steps**:
1. Run tier-1 tests: `make test-tier1`
2. Run smoke tests: `make smoke && make smoke-matriz`
3. Validate lane boundaries: `make lane-guard`
4. Check import health: `make imports-guard`
5. Generate coverage report: `pytest --cov=. --cov-report=html`

**Accept**:
- ✅ All tier-1 tests pass
- ✅ Lane boundaries respected
- ✅ Coverage ≥75% (or documented waivers)

---

## 🔄 Delegation & Review Flow

### Step 1: Task Assignment
```
Claude Code → Create Task Branch → Assign to Codex/Copilot → Update Dashboard
```

### Step 2: Execution
```
Codex/Copilot → Execute Task → Self-Verify → Create PR → Tag Claude for Review
```

### Step 3: Review Gate
```
Claude Code → Review PR → Run Validation → Approve/Request Changes → Merge
```

### Step 4: Integration
```
Claude Code → Pull Latest → Run Integration Tests → Update Dashboard → Mark Complete
```

---

## 📊 Task Prioritization Matrix

### Execute FIRST (Unblock Others)
1. **CC-1**: Pre-Audit Guardrails (enables GPT Pro audit)
2. **CC-2**: Coordination Dashboard (enables parallel tracking)
3. **Task #5**: RC Soak Sentinel (Copilot) - enables continuous monitoring

### Execute SECOND (High Value)
4. **Task #1**: Shadow-Diff Harness (Codex) - alignment verification
5. **Task #2**: Golden Token Kit (Codex) - unblocks test stability
6. **Task H**: RC Promotion Script (Copilot) - unblocks GA promotion

### Execute THIRD (Parallel Execution)
7. **Task #3**: Streaming RL Headers (Codex)
8. **Task #4**: Auto-Backoff Hints (Codex)
9. **Task B**: Circuit-Breaker (Codex) - **CRITICAL REVIEW by Claude**
10. **Task G**: Tenant Sandbox (Copilot)

### Execute FOURTH (Polish & Hygiene)
11. **E402-1**: Batch 1 cleanup (Codex)
12. **Task A**: Idempotency Redis (Codex)
13. **Task C**: Log Redaction v2 (Codex)
14. **Task D**: SDK Snippets (Copilot)

---

## 🚨 Critical Review Required (Claude Code Gate)

These tasks MUST be reviewed by Claude Code before merge:

1. **Task B**: Circuit-Breaker to MATRIZ (MATRIZ integration changes)
2. **Task #2**: Guardian Policy Fixtures (Guardian/security changes)
3. **Any PR touching**: `matriz/`, `lukhas/consciousness/`, `lukhas/identity/`, `lukhas/governance/`

---

## ⏱️ Time Estimates Summary

### Claude Code Direct Execution (Total: 3.5 hours)
- CC-1: Pre-Audit Guardrails → 30min
- CC-2: Coordination Dashboard → 1h
- CC-3: Circuit-Breaker Review → 1h
- CC-4: Guardian Fixtures Review → 30min
- CC-5: OpenAPI Validation → 20min
- CC-6: Integration Tests → 30min

### Review Gates (Total: 2 hours)
- Task #1 Review → 15min
- Task #3 Review → 15min
- Task #4 Review → 10min
- Task #5 Review → 20min
- Task H Review → 15min
- Hygiene Reviews → 30min

### Total Claude Code Involvement: ~5.5 hours

---

## 📝 Daily Coordination Checklist

```bash
# Morning (9am)
make coord-snapshot                    # Capture overnight progress
gh pr list --state open --json number,title,state,statusCheckRollup
python scripts/coordination/triage_blockers.py

# Midday (1pm)
make coord-snapshot                    # Capture morning progress
gh pr checks {open_prs}                # Check CI status
python scripts/coordination/review_ready.py  # Find PRs ready for review

# Evening (5pm)
make coord-snapshot                    # Capture daily progress
python scripts/coordination/generate_report.py --output docs/audits/daily/$(date +%Y%m%d).md
git add docs/audits/daily/ && git commit -m "chore(coord): daily snapshot $(date +%Y%m%d)"
```

---

## 🎯 Success Criteria

### Per Task
- ✅ Assigned to correct owner (Codex/Copilot/Claude)
- ✅ Execution time within estimate (±30min)
- ✅ Critical reviews completed within 24h
- ✅ Integration tests pass after merge

### Overall Coordination
- ✅ All tasks tracked in dashboard
- ✅ No merge conflicts (worktrees prevent)
- ✅ Daily snapshots generated
- ✅ Pre-audit guardrails pass before GPT Pro audit

---

## 🔗 Links & References

- **Coordination Dashboard**: [COORDINATION_DASHBOARD.md](./COORDINATION_DASHBOARD.md) (to be created)
- **Parallel Execution Plan**: [PARALLEL_AGENT_EXECUTION_PLAN.md](./PARALLEL_AGENT_EXECUTION_PLAN.md)
- **Quick Start Actions**: [QUICK_START_ACTIONS.md](./QUICK_START_ACTIONS.md)
- **Task Status JSON**: [task_status.json](./task_status.json) (to be created)

---

**Claude Code is the coordinator, verifier, and integration gatekeeper. Codex/Copilot are the primary executors.**

*⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum*
