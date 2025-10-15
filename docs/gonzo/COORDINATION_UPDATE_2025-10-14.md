# Coordination Update — 2025-10-14

**RC Status**: v0.9.0-rc live
**This Update**: Post-RC operationalization + lane coordination

---

## Completed (Zero-Risk Merges)

### ✅ PR #382 (GA Guard Pack) - MERGED
- **Owner**: Claude
- **Scope**: Observability/CI only
- **Contents**:
  - PR Health Badge workflow
  - Prometheus recording rules (`lukhas/observability/rules/guardian-rl.rules.yml`)
  - Grafana dashboard (`lukhas/observability/grafana/guardian-rl-dashboard.json`)
  - Health artifacts wiring (Guardian + RL sections)
- **Status**: ✅ Merged to `main`

### ✅ PR #383 (DX Polish Pack) - MERGED
- **Owner**: Copilot
- **Scope**: Docs/examples only
- **Contents**:
  - README quickstart enhancements
  - Cookbooks (`docs/gonzo/dx/COOKBOOK_*.md`)
  - Postman collection updates
  - Examples smoke CI (no runtime)
- **Status**: ✅ Merged to `main`

### ✅ PR #385 (Soft-audit batch) - AUTO-MERGE ENABLED
- **Owner**: Codex
- **Scope**: Code hygiene (rebased)
- **Status**: 🟢 Ready, auto-merge enabled

### ✅ PR #386 (ruffA) - AUTO-MERGE ENABLED
- **Owner**: Codex
- **Scope**: Ruff A-tier fixes (rebased onto new Guardian YAML)
- **Status**: 🟢 Ready, auto-merge enabled

---

## PR #381 Status Change: Draft + Scoped B-Slices

### Why Draft?
- Original PR had comprehensive formatting across 57 modules
- Safer to land in ≤20-file increments
- Keep hot-path Ruff gate ≤120 diagnostics per slice

### Follow-Up Issues Created
- **#388**: E402/E70x slice 1 — adapters subset (≤20 files)
- **#389**: E402/E70x slice 2 — reliability subset (≤20 files)
- **#390**: Guardian Policy YAML format mismatch (P0 blocker)

### Acceptance Criteria (per slice)
- ✅ Hot-path Ruff stays ≤120
- ✅ Smoke tests green
- ✅ No topology changes
- ✅ Use lazy imports + `TYPE_CHECKING` where needed
- ✅ Keep public API stable

---

## Critical Blocker: Guardian YAML Format (#390)

### Symptom
```
WARNING lukhas.adapters.openai.api:api.py:317 Failed to initialize Guardian PDP:
__init__() missing 4 required positional arguments: 'subjects', 'actions', 'resources', and 'obligations'
```

### Impact
- ✅ Guardian PDP **never initializes** (falls back to permissive mode)
- ✅ Smoke tests expecting auth **fail with 401**
- ✅ Prometheus recording rules **can't be tested**
- ✅ Grafana dashboard **shows empty panels**
- ✅ Health artifacts **missing Guardian section**

### Root Cause
Policy YAML (`configs/policy/guardian_policies.yaml`) uses old `when/unless/subject` format.
Rule dataclass expects `subjects/actions/resources/conditions/obligations`.

### Fix Strategy
**Update YAML to explicit schema** (recommended over complex normalization logic).

See full analysis: `docs/gonzo/issues/GUARDIAN_POLICY_YAML_FORMAT_MISMATCH.md`

### Owner
**Codex** (hot-path adapter lane)

### Priority
**P0** - Unblocks:
- Claude: Prometheus rules deployment
- Claude: Grafana dashboard validation
- Claude: Health artifacts completion
- Claude: RC soak monitoring

---

## Monitoring Deployment (Pending #390 Fix)

### Artifacts Ready
- ✅ Prometheus rules: `lukhas/observability/rules/guardian-rl.rules.yml`
- ✅ Grafana dashboard: `lukhas/observability/grafana/guardian-rl-dashboard.json`
- ✅ Deployment checklist: `docs/audits/MONITORING_DEPLOYMENT_CHECKLIST.md`

### Blocked Until Guardian Works
1. Deploy Prometheus rules to server
2. POST Grafana dashboard to Grafana API
3. Run `scripts/system_health_audit.py` (verify Guardian section)
4. Pin metrics comment on PR #382 (denial rate, PDP p95 latency)

---

## Lane Ownership (Current)

| Agent | Lane | Current Work |
|-------|------|--------------|
| **Claude** | Observability/CI | Monitoring deployment (blocked by #390) |
| **Codex** | Hot-path code | Fix Guardian YAML (#390) → B-slices (#388, #389) |
| **Copilot** | DX/docs | README "What's new in v0.9.0-rc" snippet (docs-only) |

### Coordination Rules
- **Claude**: Owns workflows, rules, dashboards, health scripts, docs
- **Codex**: Owns hot-path adapters, reliability, observability **code**
- **Copilot**: Owns README, examples, cookbooks, Postman

**No overlaps**: Each agent has exclusive areas to avoid conflicts.

---

## Next Steps (Priority Order)

### 1. Codex: Fix Guardian YAML (#390) - P0
- Update `configs/policy/guardian_policies.yaml` to explicit schema
- Add unit test for policy loading
- Verify smoke tests pass
- Commit as hot-path fix

### 2. Claude: Deploy Monitoring (after #390)
- Load Prometheus rules to server
- Deploy Grafana dashboard
- Run health audit validation
- Pin metrics comment on #382

### 3. Codex: B-Slice 1 (#388) - P1
- E402/E70x fixes in adapters subset (≤20 files)
- Lazy imports + TYPE_CHECKING
- Keep Ruff gate ≤120

### 4. Copilot: RC Release Notes Snippet
- "What's new in v0.9.0-rc" section for README
- Docs-only, no runtime changes

### 5. Codex: B-Slice 2 (#389) - P2
- E402/E70x fixes in reliability subset
- After slice 1 complete

---

## RC Soak Guardrails (48-72h After Monitoring Deploy)

### Observability Validation
- [ ] Guardian denial rate ≤15% (baseline)
- [ ] PDP p95 latency <10ms (SLO)
- [ ] Rate limit hit rate ≤5%
- [ ] PR Health Badge appears on next PR
- [ ] OpenAPI headers guard passes

### Alert Previews (No-Page Mode)
- [ ] Guardian Denial Rate High (warning only)
- [ ] Rate Limit Near-Exhaustion (warning only)

### Health Artifacts
- [ ] `/healthz` signals present with version stamp
- [ ] Guardian section in `docs/audits/health/latest.json`
- [ ] RL section in `docs/audits/health/latest.json`

---

## Communication Channel

**Lock Status**: Check `.dev/locks/ga-guard.lock` (Claude owns observability/CI)

**Issue References**:
- #382 - GA Guard Pack (merged)
- #383 - DX Polish Pack (merged)
- #385 - Soft-audit batch (auto-merge enabled)
- #386 - ruffA (auto-merge enabled)
- #381 - Phase-B lint (draft)
- #388 - E402/E70x slice 1
- #389 - E402/E70x slice 2
- #390 - Guardian YAML format (P0 blocker)

**Docs**:
- `docs/audits/TEAM_STATUS.md` - Worktree ownership
- `docs/audits/MONITORING_DEPLOYMENT_CHECKLIST.md` - Prometheus/Grafana deployment
- `docs/gonzo/issues/GUARDIAN_POLICY_YAML_FORMAT_MISMATCH.md` - Guardian YAML analysis

---

## Acceptance Checklist (Claude)

- [x] #382, #383 merged cleanly; CI green
- [x] #385, #386 auto-merge enabled
- [x] Prometheus rules + Grafana dashboard artifacts ready
- [x] PR #381 converted to Draft
- [x] Follow-up issues created (#388, #389, #390)
- [x] Team status + coordination docs updated
- [ ] Guardian YAML fixed (blocked on Codex)
- [ ] Monitoring deployed (blocked on Codex)
- [ ] Health artifacts validated (blocked on Codex)
- [ ] RC soak baseline collected (blocked on Codex)

---

**Current Status**: 🟡 Blocked on Guardian YAML fix (#390)
**Next Owner**: Codex (fix #390, then proceed with B-slices)
**Claude**: On standby for monitoring deployment after #390 resolved

---

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
