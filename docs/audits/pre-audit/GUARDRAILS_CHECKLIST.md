# Pre-Audit Guardrails Checklist
**Purpose**: Validate system health before GPT Pro research audit
**Created**: 2025-10-15 | **Owner**: Claude Code

---

## 🎯 Overview

This checklist ensures LUKHAS is in a pristine, well-documented state before conducting a comprehensive GPT Pro research audit. All guardrails must pass before audit initiation.

**Why These Guardrails Matter**:
- **Shadow-Diff**: Confirms OpenAI compatibility at envelope/header level
- **State Sweep**: Provides current system health baseline
- **Compat-Enforce**: Ensures no breaking OpenAPI changes
- **OpenAPI Validation**: Confirms spec correctness and header parity

---

## ✅ Guardrail 1: State Sweep (System Health Baseline)

**Status**: ⏳ NOT STARTED

### Execute

```bash
make state-sweep
```

### Expected Output

- State sweep JSON saved to: `docs/audits/live/<timestamp>/state_sweep.json`
- Metrics captured:
  - Total files analyzed
  - Syntax errors count
  - Import health statistics
  - Lane boundary violations
  - Test coverage percentage
  - Ruff violation counts by rule

### Acceptance Criteria

- [ ] Command completes without errors
- [ ] JSON file generated and parseable
- [ ] Syntax errors < 100 (trending down)
- [ ] Lane boundary violations = 0
- [ ] Test coverage ≥ 75%

### Output Location

```
docs/audits/live/20251015/
├── state_sweep.json
├── ruff_statistics.txt
└── summary.md
```

---

## ✅ Guardrail 2: Shadow-Diff Report (OpenAI Compatibility)

**Status**: ⏳ WAITING (depends on Task #1 completion)

### Execute

```bash
make shadow-diff
```

### Expected Output

- Shadow-diff report saved to: `docs/audits/shadow/<timestamp>/`
- Comparison results:
  - Envelope shape match (keys/types)
  - Status code parity
  - Header presence (both RL families)
  - Error envelope structure

### Acceptance Criteria

- [ ] Command completes without errors
- [ ] Report shows ✅/❌ table for each endpoint
- [ ] Critical endpoints (embeddings, chat/completions) show full parity
- [ ] Any ❌ items documented with rationale or mitigation plan

### Output Location

```
docs/audits/shadow/20251015/
├── shadow_diff.json
├── envelope_comparison.md
└── headers_comparison.md
```

**Note**: This guardrail requires Task #1 (Shadow-Diff Harness) to be completed first.

---

## ✅ Guardrail 3: Compat-Enforce (No Breaking OpenAPI Changes)

**Status**: ⏳ NOT STARTED

### Execute

```bash
make compat-enforce
```

### Expected Output

- OpenAPI compatibility check result
- 0 breaking changes detected
- Optional: warnings for non-breaking changes

### Acceptance Criteria

- [ ] Command exits with status 0 (success)
- [ ] Output shows "0 breaking changes"
- [ ] Any warnings are documented and reviewed

### Sample Output

```
✅ OpenAPI compatibility check passed
Breaking changes: 0
Warnings: 2 (optional fields added)
```

---

## ✅ Guardrail 4: OpenAPI Validation & Headers Guard

**Status**: ⏳ NOT STARTED

### Execute

```bash
make openapi-spec
make openapi-headers-guard
```

### Expected Output

- **openapi-spec**:
  - OpenAPI spec generated: `docs/openapi/lukhas-openapi.json`
  - Spec validates against OpenAPI 3.0/3.1 schema

- **openapi-headers-guard**:
  - Header presence confirmed for all endpoints
  - Both RL header families present
  - OpenAI envelope structure matches

### Acceptance Criteria

- [ ] `make openapi-spec` completes without errors
- [ ] Spec file generated and parseable
- [ ] `openapi-spec-validator docs/openapi/lukhas-openapi.json` passes
- [ ] `make openapi-headers-guard` shows all headers present
- [ ] Both RL header families confirmed (X-RateLimit-* and OpenAI aliases)

### Sample Output

```bash
$ make openapi-spec
📝 Generating OpenAPI spec for OpenAI façade...
✅ wrote docs/openapi/lukhas-openapi.json

$ openapi-spec-validator docs/openapi/lukhas-openapi.json
✅ OpenAPI spec is valid!

$ make openapi-headers-guard
🔍 Validating OpenAI header parity...
✅ X-RateLimit-Limit present
✅ X-RateLimit-Remaining present
✅ X-RateLimit-Reset present
✅ OpenAI aliases present
✅ All required headers found
```

---

## 📊 Pre-Audit Summary Template

After all guardrails pass, generate this summary for the audit team:

```markdown
# Pre-Audit Summary
**Date**: 2025-10-15
**RC Version**: v0.9.0-rc

## Guardrails Status

| Guardrail | Status | Details |
|-----------|--------|---------|
| State Sweep | ✅ PASS | `docs/audits/live/20251015/` |
| Shadow-Diff | ✅ PASS | `docs/audits/shadow/20251015/` |
| Compat-Enforce | ✅ PASS | 0 breaking changes |
| OpenAPI Validation | ✅ PASS | Spec valid, headers confirmed |

## System Health Snapshot

- **Syntax Errors**: 42 (down from 434 - 90% reduction)
- **Lane Boundaries**: 0 violations
- **Test Coverage**: 78%
- **Ruff Hot-Path**: 94 violations (under 120 gate)

## OpenAI Compatibility

- **Envelope Parity**: ✅ Full match on /v1/embeddings, /v1/chat/completions
- **Header Parity**: ✅ Both RL header families present
- **Error Envelopes**: ✅ OpenAI structure matches

## Artifacts for Audit

- State sweep: `docs/audits/live/20251015/state_sweep.json`
- Shadow-diff: `docs/audits/shadow/20251015/shadow_diff.json`
- OpenAPI spec: `docs/openapi/lukhas-openapi.json`
- Monitoring dashboards: http://localhost:3000 (Grafana)

## Ready for GPT Pro Audit

All guardrails passed. System is in pristine state for comprehensive audit.
```

---

## 🚀 Execution Workflow

### Step 1: Execute Guardrails 1, 3, 4 (Independent)

```bash
# Run in parallel (independent guardrails)
make state-sweep &
make compat-enforce &
make openapi-spec && make openapi-headers-guard &

# Wait for all to complete
wait
```

### Step 2: Wait for Task #1 Completion (Shadow-Diff Harness)

- Codex completes Task #1
- Claude Code reviews PR
- PR merges to main
- `make shadow-diff` becomes available

### Step 3: Execute Guardrail 2 (Shadow-Diff)

```bash
make shadow-diff
```

### Step 4: Generate Pre-Audit Summary

```bash
# Create summary document
cat > docs/audits/pre-audit/summary_20251015.md <<'MD'
# [Use template above]
MD

# Commit artifacts
git add docs/audits/
git commit -m "docs(audit): pre-GPT Pro audit guardrails complete

All 4 guardrails passed:
- State sweep: 78% coverage, 0 lane violations
- Shadow-diff: Full OpenAI parity on critical endpoints
- Compat-enforce: 0 breaking changes
- OpenAPI validation: Spec valid, headers confirmed

Ready for GPT Pro research audit.

Artifacts:
- docs/audits/live/20251015/
- docs/audits/shadow/20251015/
- docs/audits/pre-audit/summary_20251015.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 📝 Checklist Summary

### Pre-Requisites
- [ ] All critical PRs merged (Tasks #1-5)
- [ ] CI green on main branch
- [ ] RC soak running (48-72h minimum)

### Guardrail Execution
- [ ] **G1**: State Sweep executed and artifacts saved
- [ ] **G2**: Shadow-Diff executed (after Task #1 complete)
- [ ] **G3**: Compat-Enforce passed (0 breaking changes)
- [ ] **G4**: OpenAPI Validation passed (spec + headers)

### Post-Guardrail
- [ ] Pre-audit summary document created
- [ ] All artifacts committed to `docs/audits/`
- [ ] GPT Pro audit team notified with artifact URLs
- [ ] Monitoring dashboards accessible for audit reference

---

## 🔗 Related Documents

- **Task Assignments**: [TASK_ASSIGNMENTS_CLAUDE.md](../../plans/TASK_ASSIGNMENTS_CLAUDE.md)
- **Coordination Dashboard**: [COORDINATION_DASHBOARD.md](../../plans/COORDINATION_DASHBOARD.md)
- **Task #1 (Shadow-Diff)**: See coordination dashboard for PR link
- **Parallel Execution Plan**: [PARALLEL_AGENT_EXECUTION_PLAN.md](../../plans/PARALLEL_AGENT_EXECUTION_PLAN.md)

---

**All guardrails must pass before initiating GPT Pro research audit. No exceptions.**

*⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum*
