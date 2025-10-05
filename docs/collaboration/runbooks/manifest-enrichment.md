---
module: docs.collaboration.runbooks
type: runbook
title: Manifest Enrichment Runbook
status: stable
tags: [t4, governance, enrichment, runbook]
lane: L2
---

# Manifest Enrichment Runbook

**Purpose**: Step-by-step procedures for enriching LUKHAS module manifests with controlled vocabulary extraction and validation.

**Audience**: DevOps, Release Engineers, Documentation Teams

**SLA**: Manual enrichment: 15 min/module | Bulk enrichment: <5 min for 100 modules

---

## 1. Normal Operations

### 1.1 Enrich All Manifests

**When**: After adding new modules or updating existing code

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
make enrich
```

**Expected Output**:
```
✅ Enriched 148/148 manifests
📝 Generated 4,120 unmapped phrases in review queue
💾 Ledger entries: 146 modules
```

**Success Criteria**:
- All manifests processed without errors
- Ledger entries appended to `artifacts/enrichment_ledger.jsonl`
- Review queue updated at `artifacts/review_queue.jsonl`

### 1.2 Generate Registry and Reports

**When**: After enrichment, before PR submission

```bash
make registry    # Generate MODULE_REGISTRY.json
make slo-report  # Generate SLO dashboard
```

**Expected Output**:
- `docs/_generated/MODULE_REGISTRY.json` created/updated
- `docs/_generated/SLO_DASHBOARD.md` created/updated

### 1.3 Run Quality Gates

**When**: Before committing changes

```bash
make quality
```

**Expected Output**:
```
✅ Schema validation passed
✅ Vocabulary compliance passed
✅ Review queue valid
✅ Registry matches filesystem
✅ No SLO violations
```

---

## 2. Troubleshooting

### 2.1 Schema Validation Failures

**Symptom**: `make validate-schema` fails

**Diagnosis**:
```bash
python3 scripts/ci/validate_schema.py
```

**Common Causes**:
1. **Empty strings in required fields**: Check `matrix.contract`, `matrix.bus_api`, `matrix.adapters`
2. **Invalid patterns**: Check `dependencies.apis[]` paths (no leading `/` or drive letters)
3. **Missing required fields**: Check `name`, `version`, `tags`, `performance.sla_targets`

**Fix**:
```bash
# Find problematic manifests
find . -name "module.manifest.json" -type f | while read f; do
  python3 -c "
import json, sys
data = json.load(open('$f'))
# Check for empty strings
if data.get('matrix', {}).get('contract') == '':
    print('$f: Empty matrix.contract')
" 2>/dev/null
done

# Fix empty strings (example)
jq '.matrix.contract = "N/A"' module.manifest.json > tmp && mv tmp module.manifest.json
```

### 2.2 Vocabulary Compliance Failures

**Symptom**: `make validate-vocab` fails with unmapped terms

**Diagnosis**:
```bash
python3 scripts/ci/vocab_guard.py
```

**Common Causes**:
- New terms extracted that aren't in `schemas/controlled_vocabulary.json`
- Review queue has high-frequency terms that should be promoted

**Fix**:
```bash
# Promote high-frequency terms from review queue
python3 scripts/bulk_promote_vocab.py \
  --queue artifacts/review_queue.jsonl \
  --threshold 5 \
  --output schemas/controlled_vocabulary.json

# Re-run enrichment
make enrich

# Re-validate
make validate-vocab
```

### 2.3 SLO Violations

**Symptom**: `make validate-slo` fails with performance regressions

**Diagnosis**:
```bash
python3 scripts/ci/slo_gate.py
```

**Output Example**:
```
❌ SLO violations (2 modules):
  consciousness: p95: 320.0ms > 250.0ms target (observed 2025-10-03)
  identity: p95: 150.0ms > 100.0ms target (observed 2025-10-03)
```

**Fix Options**:

**Option A: Optimize Performance**
```bash
# Profile the module
cd lukhas/consciousness
pytest tests/ --profile

# Fix performance bottleneck
# ... (module-specific optimization)

# Re-benchmark
python3 scripts/benchmark_module.py consciousness
# Update manifest with new observed_p95
```

**Option B: Adjust SLA Target** (requires justification)
```bash
# Edit manifest
vim lukhas/consciousness/module.manifest.json
# Update performance.sla_targets.p95_latency with justification

# Document in PR
git commit -m "perf(consciousness): adjust SLA target due to <reason>"
```

**Option C: Mark Data as Stale** (temporary bypass)
```bash
# Remove observed timestamp to mark as stale
jq '.performance.observed.observed_at = null' module.manifest.json > tmp && mv tmp module.manifest.json

# SLO gate will skip stale data
make validate-slo  # Should pass
```

### 2.4 Registry vs Filesystem Mismatch

**Symptom**: `make validate-registry` fails

**Diagnosis**:
```bash
python3 scripts/ci/registry_vs_fs.py
```

**Output Example**:
```
❌ Registry validation failed (3 errors):
  consciousness: Registry claims docs/architecture.md but file missing
  identity: Filesystem has tests/test_auth.py but not in registry
```

**Fix**:
```bash
# Regenerate registry from current filesystem
make registry

# Verify
make validate-registry  # Should pass
```

---

## 3. Incident Response

### 3.1 Rollback Bad Enrichment

**Scenario**: Enrichment introduced errors or incorrect vocabulary

**Procedure**:
```bash
# Find the ledger entry SHA from before enrichment
tail -5 artifacts/enrichment_ledger.jsonl

# Revert to previous state
make revert-last

# Alternative: Manual revert
python3 scripts/util/revert_from_ledger.py \
  --ledger artifacts/enrichment_ledger.jsonl \
  --sha <TARGET_SHA>

# Re-validate
make quality
```

**Expected Duration**: <2 minutes

### 3.2 Emergency Bypass (CI Blocked)

**Scenario**: CI quality gates blocking urgent hotfix

**Procedure** (requires approval):
```bash
# Set emergency flag
export LUKHAS_EMERGENCY_BYPASS=true

# Run tests only (skip quality gates)
make test

# Commit with bypass trailer
git commit -m "fix(critical): <description>

Emergency-Bypass: quality-gates
Approved-By: <APPROVER>
Reason: <JUSTIFICATION>
"

# Push
git push

# IMMEDIATELY after merge:
# 1. Remove bypass flag
unset LUKHAS_EMERGENCY_BYPASS

# 2. Fix quality issues
make quality  # Address all failures

# 3. Document in incident report
```

**Follow-up**: Create incident report within 24 hours

### 3.3 Corrupted Ledger Recovery

**Scenario**: `artifacts/enrichment_ledger.jsonl` corrupted or deleted

**Procedure**:
```bash
# Check git history
git log --all --full-history -- artifacts/enrichment_ledger.jsonl

# Restore from last commit
git checkout HEAD~1 -- artifacts/enrichment_ledger.jsonl

# If not in git, rebuild from manifests
python3 scripts/util/rebuild_ledger.py \
  --output artifacts/enrichment_ledger.jsonl

# Verify integrity
python3 scripts/ci/validate_ledger.py
```

---

## 4. Maintenance

### 4.1 Vocabulary Cleanup (Monthly)

**Goal**: Promote high-frequency terms, deprecate unused terms

```bash
# Review queue statistics
python3 scripts/report_vocab_stats.py \
  --queue artifacts/review_queue.jsonl \
  --top 100

# Bulk promote terms with frequency ≥5
python3 scripts/bulk_promote_vocab.py \
  --queue artifacts/review_queue.jsonl \
  --threshold 5

# Identify deprecated terms (unused in any manifest)
python3 scripts/find_unused_vocab.py \
  --output artifacts/deprecated_vocab.json

# Update controlled vocabulary
vim schemas/controlled_vocabulary.json
```

### 4.2 SLO Target Review (Quarterly)

**Goal**: Ensure SLA targets reflect current system capabilities

```bash
# Generate SLO trend report
python3 scripts/report_slo_trends.py \
  --since 3-months-ago \
  --output artifacts/slo_trends.md

# Review outliers
cat artifacts/slo_trends.md | grep "violation_rate > 10%"

# Adjust targets in manifests as needed
```

---

## 5. Automation Integration

### 5.1 CI Pipeline Integration

**GitHub Actions** (.github/workflows/quality.yml):
```yaml
name: T4 Quality Gates
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run quality gates
        run: |
          make quality
      - name: Upload artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: quality-reports
          path: |
            artifacts/enrichment_ledger.jsonl
            artifacts/review_queue.jsonl
            docs/_generated/SLO_DASHBOARD.md
```

### 5.2 Pre-commit Hook

**Install**:
```bash
cp scripts/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Hook Content** (.git/hooks/pre-commit):
```bash
#!/bin/bash
set -e

echo "Running T4 quality gates..."
make quality

if [ $? -ne 0 ]; then
  echo "❌ Quality gates failed. Fix issues or use --no-verify to bypass."
  exit 1
fi

echo "✅ Quality gates passed"
```

---

## 6. Metrics and Monitoring

### 6.1 Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Schema validation pass rate | 100% | <95% |
| Vocab compliance rate | 100% | <98% |
| SLO violation rate | <5% | >10% |
| Enrichment duration (100 modules) | <5 min | >10 min |
| Registry sync lag | 0 mismatches | >3 mismatches |

### 6.2 Dashboards

- **SLO Dashboard**: `docs/_generated/SLO_DASHBOARD.md`
- **Module Registry**: `docs/_generated/MODULE_REGISTRY.json`
- **Review Queue**: `artifacts/review_queue.jsonl` (view with `jq`)

---

## 7. Contacts

**Primary**: DevOps Team
**Escalation**: Platform Engineering
**Documentation**: This runbook
**Issue Tracker**: GitHub Issues with `t4-governance` label

---

## 8. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-05 | Initial runbook creation | Claude |

---

**Next Review**: 2025-11-05 (Monthly)
