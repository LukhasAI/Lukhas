# Monitoring Deployment Blocked — Guardian Metrics Signature Mismatch

**Date**: 2025-10-14
**Status**: 🟢 **RESOLVED** - Smoke tests passing
**Owner**: Codex (hot-path adapter lane)
**Blocker Type**: Guardian PDP policy normalization

---

## Resolution Summary

Codex successfully merged all four branches to `main`:
- ✅ PR #381 (hot-path Ruff gate)
- ✅ PR #386 (Guardian PDP YAML tolerance)
- ✅ PR #385 (soft-audit batch)
- ✅ Branch retirement docs

### Fix applied (2025-10-14)
- Normalized Guardian policy rule effects to be case-insensitive (`allow`/`deny` now load correctly).
- Translated `when.action.route` hints into resource patterns so targeted deny rules do not blanket-match.
- Added regression coverage for lowercase policy effects.
- Re-ran `python3 -m pytest tests/smoke/test_openai_facade.py -q` and Guardian PDP unit tests — all green.

Guardian metrics `record_decision()` call already matched the canonical signature; no further changes required.

---

## Previous Failure Details (for record)

### Error
```
TypeError: record_decision() got an unexpected keyword argument 'latency_ms'
```

### Location
`lukhas/adapters/openai/api.py:276` in `_dep` function (Guardian enforcement)

### Root Cause
Guardian PDP normalization loaded the `deny-sensitive-dreams` rule with default wildcards; combined with lowercase `effect: allow`, every request was denied (`default_deny`). This presented as smoke-test 403s that were originally mistaken for a metrics signature mismatch.

---

## Impact

### Immediate
- ✅ Smoke tests now **PASSING** (`tests/smoke/test_openai_facade.py`)
- ✅ API requests with Guardian enforcement **succeed**
- ✅ Monitoring deployment validation **unblocked**
- ✅ RC soak period can proceed

### Blocked Tasks
- None — Guardian metrics recording validated and PDP allows baseline traffic.

---

## Required Fix

### Owner
**Codex** (hot-path adapter lane)

### Follow-up
- Keep Guardian policy YAMLs using lowercase effects if preferred — loader now normalizes safely.
- If future `when` clauses add new keys, extend normalization so they translate into explicit rule constraints.

---

## Investigation Steps

### Historical commands (kept for traceability)
```bash
grep -A 10 "def record_decision" lukhas/observability/guardian_metrics.py
git log --oneline -10 -- lukhas/observability/guardian_metrics.py
git log --oneline -10 -- lukhas/adapters/openai/api.py
```

---

## Timeline Impact

### Current
- ✅ Guardian PDP + metrics validated (2025-10-14)
- 🔜 Claude to deploy monitoring, run system health audit, and kick off RC soak

---

## Coordination

### Lane Ownership
- **Codex**: Completed Guardian PDP normalization fix
- **Claude**: Ready to proceed with monitoring deployment

### Communication
- Issue filed: [TBD - create GitHub issue if needed]
- Documented in: `MONITORING_DEPLOYMENT_BLOCKED.md` (updated with resolution)
- Team status: Notify after deployment + RC soak kickoff

---

## Next Steps

### Immediate (Claude)
1. Pull latest `main`
2. Deploy Prometheus rules
3. Deploy Grafana dashboard
4. Run system health audit
5. Start RC soak baseline collection

---

## Status
🟢 **UNBLOCKED**
**Priority**: P0 addressed
**ETA**: Monitoring deployment can resume immediately

---

_Documented by: Claude (Observability/CI)_
_Date: 2025-10-14_

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
