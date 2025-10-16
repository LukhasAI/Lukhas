# Coordination Dashboard - Real-Time Progress
**Last Updated**: 2025-10-15 05:35 UTC | **Auto-Refresh**: `make coord-snapshot`

---

## 🎯 Executive Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Tasks Total** | 18 | 18 | ✅ |
| **Tasks In Progress** | 0 | 3-5 | ⏳ READY TO START |
| **Tasks Complete** | 0 | 18 | ⏳ 0% |
| **PRs Open** | 2 | <10 | ✅ |
| **PRs Blocked** | 0 | 0 | ✅ |
| **CI Failures** | 0 | 0 | ✅ |
| **Pre-Audit Guardrails** | 0/4 | 4/4 | ⏳ PENDING |

---

## 📋 Top-5 "Do Now" Tasks (2–4 Hour Wins)

### Task #1: Shadow-Diff Harness (Codex) 🔧
**Status**: ⏳ NOT STARTED
**Owner**: Codex
**Priority**: HIGH
**Estimated**: 2-3 hours
**Dependencies**: None
**Branch**: `feat/codex/shadow-diff-harness`

**Progress**:
- [ ] Create `scripts/shadow_diff.py`
- [ ] Add `Makefile` target `shadow-diff`
- [ ] Generate first report to `docs/audits/shadow/`
- [ ] Optional: Add CI job for PRs touching facade
- [ ] PR created and tagged for Claude review

**Blockers**: None

**Accept Criteria**:
- ✅ `make shadow-diff` produces ✅/❌ table
- ✅ Report compares envelope shape, status codes, headers
- ✅ CI optional job configured

---

### Task #2: Golden Token Kit + Policy Fixtures (Codex + Copilot) 🛡️
**Status**: ⏳ NOT STARTED
**Owner**: Codex (code), Copilot (docs)
**Priority**: HIGH
**Estimated**: 2 hours
**Dependencies**: None
**Branch**: `feat/codex/golden-token-kit`

**Progress**:
- [ ] Create `tests/fixtures/tokens.py`
- [ ] Create `configs/guardian/policies.dev.yaml`
- [ ] Update smoke tests to use `authz_headers(scope=...)`
- [ ] Create `docs/gonzo/dev/POLICY_FIXTURES.md`
- [ ] Test in both `permissive` and `strict` modes
- [ ] PR created and tagged for Claude **CRITICAL REVIEW**

**Blockers**: None

**Accept Criteria**:
- ✅ Smoke suite passes with `LUKHAS_POLICY_MODE=permissive`
- ✅ Smoke suite passes with `strict` + `policies.dev.yaml`
- ✅ No production secrets in fixtures
- ✅ Clear dev/prod separation documented

---

### Task #3: Streaming RL Headers (SSE) (Codex) 📡
**Status**: ⏳ NOT STARTED
**Owner**: Codex
**Priority**: MEDIUM
**Estimated**: 2-3 hours
**Dependencies**: None
**Branch**: `feat/codex/streaming-rl-headers`

**Progress**:
- [ ] Add `X-RateLimit-*` headers to SSE start
- [ ] Add OpenAI RL header aliases
- [ ] Optional: Trailer on close
- [ ] Create `tests/smoke/test_responses_stream_headers.py`
- [ ] Validate both header families present
- [ ] PR created and tagged for Claude review

**Blockers**: None

**Accept Criteria**:
- ✅ Test asserts RL headers on streaming responses (200)
- ✅ Test asserts RL headers on early error path
- ✅ Both header families present

---

### Task #4: Auto-Backoff Hints in 429 (Codex) ⏱️
**Status**: ⏳ NOT STARTED
**Owner**: Codex
**Priority**: MEDIUM
**Estimated**: 1-2 hours
**Dependencies**: None
**Branch**: `feat/codex/backoff-hints-429`

**Progress**:
- [ ] Add `Retry-After` header to 429 response
- [ ] Include `{ "retry_after": seconds }` in error envelope
- [ ] Update `tests/smoke/test_rate_limit_headers.py`
- [ ] Validate both RL header families + Retry-After
- [ ] PR created and tagged for Claude review

**Blockers**: None

**Accept Criteria**:
- ✅ 429 shows `Retry-After` header
- ✅ 429 shows both RL header families
- ✅ Error envelope includes retry info

---

### Task #5: RC Soak Sentinel (Copilot) 🔬
**Status**: ⏳ NOT STARTED
**Owner**: Copilot
**Priority**: HIGH
**Estimated**: 2-3 hours
**Dependencies**: Prometheus running
**Branch**: `ops/copilot/rc-soak-sentinel`

**Progress**:
- [ ] Create `scripts/rc_soak_sentinel.py`
- [ ] Query Prom for: denial-rate, PDP p95, 5xx error-rate
- [ ] Open GH issue on threshold breach with panel links
- [ ] Create `.github/workflows/rc-soak-sentinel.yml`
- [ ] Document SLOs in `docs/audits/ops/RC_SOAK_SLO.md`
- [ ] PR created and tagged for Claude review

**Blockers**: None

**Accept Criteria**:
- ✅ Manual run creates issue on breach
- ✅ No-op when SLOs met
- ✅ Issue includes last-hour panel links

---

## 🚀 High-Impact Quick Wins (4–6 in Parallel)

### Task A: Idempotency Redis E2E (Codex) 💾
**Status**: ⏳ NOT STARTED | **Priority**: MEDIUM | **Est**: 2h
**Progress**: 0/5 steps
**Branch**: `feat/codex/idempotency-redis`

### Task B: Circuit-Breaker to MATRIZ (Codex) ⚡
**Status**: ⏳ NOT STARTED | **Priority**: HIGH | **Est**: 3h
**Progress**: 0/6 steps | **⚠️ CRITICAL REVIEW REQUIRED**
**Branch**: `feat/codex/matriz-circuit-breaker`

### Task C: Log Redaction v2 (Codex) 🔒
**Status**: ⏳ NOT STARTED | **Priority**: MEDIUM | **Est**: 2h
**Progress**: 0/4 steps
**Branch**: `feat/codex/log-redaction-v2`

### Task D: SDK Rate-Limit Snippets (Copilot) 📚
**Status**: ⏳ NOT STARTED | **Priority**: LOW | **Est**: 1-2h
**Progress**: 0/3 steps
**Branch**: `docs/copilot/sdk-rl-snippets`

### Task E: PR Magic Comment Triage (Copilot) 🤖
**Status**: ⏳ NOT STARTED | **Priority**: LOW | **Est**: 2h
**Progress**: 0/4 steps
**Branch**: `ci/copilot/pr-magic-triage`

### Task F: OpenAPI Drift Sentinel (Codex) 🔍
**Status**: ⏳ NOT STARTED | **Priority**: MEDIUM | **Est**: 1h
**Progress**: 0/3 steps
**Branch**: `ci/codex/openapi-drift-sentinel`

### Task G: Tenant Sandbox Starter (Copilot) 🏗️
**Status**: ⏳ NOT STARTED | **Priority**: MEDIUM | **Est**: 2-3h
**Progress**: 0/4 steps
**Branch**: `docs/copilot/tenant-sandbox`

### Task H: RC Promotion Script (Copilot) 🚀
**Status**: ⏳ NOT STARTED | **Priority**: HIGH | **Est**: 2h
**Progress**: 0/5 steps
**Branch**: `ops/copilot/rc-promotion-script`

---

## 🧹 Hygiene Slices (≤20 Files per Slice)

### E402 Batch 1 (Codex) 🧹
**Status**: ⏳ NOT STARTED | **Priority**: MEDIUM | **Est**: 30min
**Files**: 20 (from `/tmp/e402_batch1.txt`)
**Branch**: `fix/codex/E402-batch1` (already planned in previous docs)

### Safe Autofix (Codex) 🧹
**Status**: ⏳ NOT STARTED | **Priority**: LOW | **Est**: 15min
**Rules**: W293, F841, I001
**Branch**: `fix/codex/ruff-autofix-safe` (already planned in previous docs)

---

## 🎯 Claude Code Direct Tasks (Owner: Claude)

### CC-1: Pre-Audit Guardrails Checklist ✅
**Status**: ⏳ NOT STARTED
**Priority**: CRITICAL (blocks GPT Pro audit)
**Estimated**: 30 minutes

**Steps**:
- [ ] Run `make state-sweep` → save to `docs/audits/live/<timestamp>/`
- [ ] Run shadow-diff (after Task #1) → save to `docs/audits/shadow/<timestamp>/`
- [ ] Confirm `compat-enforce` green
- [ ] Validate OpenAPI: `make openapi-spec && make openapi-headers-guard`
- [ ] Create `docs/audits/pre-audit/GUARDRAILS_CHECKLIST.md`

---

### CC-2: Coordination Dashboard (THIS DOCUMENT) 📊
**Status**: 🔄 IN PROGRESS
**Priority**: HIGH
**Estimated**: 1 hour

**Steps**:
- [x] Create `COORDINATION_DASHBOARD.md` (this file)
- [ ] Create `task_status.json`
- [ ] Create `scripts/coordination/daily_snapshot.sh`
- [ ] Add `coord-snapshot` target to Makefile
- [ ] Test snapshot command

---

### CC-3: Critical Review - Circuit-Breaker (Review PR) 🔍
**Status**: ⏳ WAITING (depends on Task B completion)
**Priority**: CRITICAL
**Estimated**: 1 hour

**Checklist**: See [TASK_ASSIGNMENTS_CLAUDE.md](./TASK_ASSIGNMENTS_CLAUDE.md#task-cc-3)

---

### CC-4: Guardian Policy Fixtures Review (Review PR) 🛡️
**Status**: ⏳ WAITING (depends on Task #2 completion)
**Priority**: HIGH
**Estimated**: 30 minutes

**Checklist**: See [TASK_ASSIGNMENTS_CLAUDE.md](./TASK_ASSIGNMENTS_CLAUDE.md#task-cc-4)

---

### CC-5: OpenAPI Parity Validation ✅
**Status**: ⏳ WAITING (depends on Tasks #1, #3, #4 completion)
**Priority**: HIGH
**Estimated**: 20 minutes

**Steps**: See [TASK_ASSIGNMENTS_CLAUDE.md](./TASK_ASSIGNMENTS_CLAUDE.md#task-cc-5)

---

### CC-6: Integration Test Suite Validation 🧪
**Status**: ⏳ WAITING (after major PRs merge)
**Priority**: MEDIUM
**Estimated**: 30 minutes

**Steps**: See [TASK_ASSIGNMENTS_CLAUDE.md](./TASK_ASSIGNMENTS_CLAUDE.md#task-cc-6)

---

## 📊 Progress Metrics

### Overall Completion
```
████░░░░░░░░░░░░░░░░ 0% (0/18 tasks complete)
```

### By Owner
- **Codex**: 0/9 tasks (0%)
- **Copilot**: 0/6 tasks (0%)
- **Claude Code**: 0/6 tasks (0%)

### By Priority
- **CRITICAL**: 0/3 tasks (0%)
- **HIGH**: 0/6 tasks (0%)
- **MEDIUM**: 0/7 tasks (0%)
- **LOW**: 0/2 tasks (0%)

### Time Estimates
- **Total Estimated**: ~32 hours
- **Time Spent**: 0 hours
- **Remaining**: ~32 hours

---

## 🚨 Blockers & Risks

### Active Blockers
*None currently*

### Potential Risks
1. **Circuit-Breaker (Task B)**: MATRIZ integration complexity - needs careful review
2. **Guardian Fixtures (Task #2)**: Security implications - critical review required
3. **Parallel Execution**: Merge conflicts if worktrees not used properly

### Mitigation
- Use separate worktrees for all parallel work
- Lock files in `.dev/locks/` to coordinate
- Critical reviews by Claude Code before merge

---

## 🔄 Daily Snapshot History

### 2025-10-15 05:35 UTC (Initial)
- Dashboard created
- Task assignments documented
- All tasks in "NOT STARTED" state
- Ready for parallel execution

---

## 📝 Quick Commands

```bash
# Update dashboard
make coord-snapshot

# Check all PRs
gh pr list --state open --json number,title,state,statusCheckRollup

# Check CI status
gh pr checks {PR_NUMBER}

# Find PRs ready for review
python scripts/coordination/review_ready.py

# Generate daily report
python scripts/coordination/generate_report.py --output docs/audits/daily/$(date +%Y%m%d).md
```

---

## 🎯 Next Actions (Immediate)

1. ✅ **Execute CC-1**: Pre-Audit Guardrails (Claude Code - 30min)
2. ✅ **Complete CC-2**: Finish coordination scripts (Claude Code - 30min)
3. 🚀 **Launch Task #5**: RC Soak Sentinel (Copilot - unblocks monitoring)
4. 🚀 **Launch Task #1**: Shadow-Diff Harness (Codex - unblocks alignment checks)
5. 🚀 **Launch Task #2**: Golden Token Kit (Codex - unblocks test stability)

---

**Real-time coordination dashboard maintained by Claude Code. Auto-refresh: `make coord-snapshot`**

*⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum*
