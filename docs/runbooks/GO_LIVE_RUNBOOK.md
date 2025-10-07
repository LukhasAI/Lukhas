---
status: wip
type: documentation
owner: unknown
module: runbooks
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Go-Live Runbook + Ops Playbook

## Day-0 (Go-Live) Checklist — 20-minute preflight

### Branch Policy Setup
- [ ] Ensure promotion PRs require ✅ MATRIZ + ✅ coverage + ✅ promotion guard green
- [ ] Enable `allow:coverage-drop` and `allow:candidate-additions` labels (emergency only)
- [ ] Confirm CI can push PR comments and upload artifacts
- [ ] Test dashboard bot: `python3 tools/dashboard_bot.py --mode update`

### Baseline Snapshots
- [ ] **candidate/ file count**: `find candidate/ -type f -name "*.py" | wc -l`
- [ ] **Coverage metrics**: Run coverage tool and save baseline
- [ ] **Quarantined AuthZ tests**: `grep -r '@authz_quarantine' tests/ | wc -l`
- [ ] **Artifacts inventory**: `ls -la artifacts/`

### Verification Commands
```bash
# Test daily cockpit
python3 tools/batch_cockpit.py --dry-run

# Test burst cockpit
python3 tools/burst_cockpit.py --target 100 --dry-run

# Test dashboard bot
python3 tools/dashboard_bot.py --mode update
python3 tools/dashboard_bot.py --mode exec-summary --output artifacts/executive_summary.md
```

---

## Daily Mode (Mon–Thu): 50 files/day (surgical)

### Operator Command
```bash
python3 tools/batch_cockpit.py
```

### Auto-execution Flow
1. **Plan**: Generate next 50 files via promotion_selector.py
2. **Move**: Execute git mv operations with history preservation
3. **Validate**: MATRIZ + coverage + import health checks
4. **Artifacts**: Update promotion_log.md + progress.json
5. **Commit**: Structured commit with Problem/Solution/Impact
6. **PR**: Draft PR with validation summary + dashboard comment

### Human Gates
- **Review PR checklist**: All artifacts green before merge
- **Stop conditions**: Any red in MATRIZ/import/coverage → investigate before re-run

---

## Burst Mode (Weekends): 200–400 files (sprint)

### Operator Commands
```bash
# Standard weekend burst
python3 tools/burst_cockpit.py --target 300

# Conservative burst
python3 tools/burst_cockpit.py --target 200

# Maximum safe burst
python3 tools/burst_cockpit.py --target 400 --max-batches 8
```

### Safety Features
- **Checkpoints every 100 files** with full validation suite
- **Auto-halt** on any validation failure
- **Max batch guard** prevents runaway execution
- **Single summary PR** with checkpoint table + dashboard metrics

---

## Ops Guardrails (live)

### Automated Blocks
- **No new candidate/ files**: Pre-commit + CI enforcement
- **Import drift**: import_failures.json must be empty
- **Coverage ratchet**: Equal or higher than baseline (bypass with label + justification)
- **MATRIZ gates**: Hard fail on invalid contracts/identity/OPA/telemetry

### Dashboard Monitoring
```bash
# Update metrics
python3 tools/dashboard_bot.py --mode update

# Generate executive summary
python3 tools/dashboard_bot.py --mode exec-summary --output artifacts/weekly_report.md

# Check current status
cat artifacts/progress.json | jq '.summary'
```

---

## On-Call Playbook (fast fixes)

### Symptom → Action

**MATRIZ validation fails**
```bash
# Identify failing contracts
make validate-matrix-all 2>&1 | grep "❌"

# Fix contract or policy
# Re-run batch
python3 tools/batch_cockpit.py
```

**Coverage regression**
```bash
# Inspect coverage report
cat tests/matrix_coverage_report.md

# Add targeted tests or reduce batch size
# Re-run with --batch-size 25
python3 tools/batch_cockpit.py --batch-size 25
```

**Import failures**
```bash
# Read failure details
cat artifacts/import_failures.json | jq '.failures'

# Add shim or fix import path
# Re-run validation
python3 tools/dashboard_bot.py --mode update
```

**CI timeout (burst mode)**
```bash
# Lower target and resume
python3 tools/burst_cockpit.py --target 200

# Check partial progress
cat artifacts/burst_checkpoint.json
```

---

## Rollback (single-move)

Each batch = one commit + one PR. **Rollback procedure**:

```bash
# Identify batch commit
git log --oneline --grep="promotion batch"

# Revert specific batch
git revert <batch-commit-sha>

# Verify compat layer maintains runtime stability
python3 -c "import lukhas.core.some_module"  # Should still work
```

---

## Weekly Rhythm (sustainable pace)

### Monday–Thursday
- **Morning**: `python3 tools/batch_cockpit.py`
- **Review**: Check PR dashboard comment + merge if green
- **Target**: 50 files/day = 200 files/week baseline

### Friday
- **Stabilization only**: No new promotions
- **AuthZ sweep**: Fix quarantined tests, remove @authz_quarantine markers
- **Coverage boost**: Add targeted tests to low-coverage modules
- **Metrics review**: Update weekly velocity tracking

### Weekend
- **Burst session**: `python3 tools/burst_cockpit.py --target 300`
- **Checkpoint review**: Validate all gates pass
- **PR ready**: Summary PR ready for Monday merge

---

## Executive Dashboard (signal, not noise)

### 6 Key Metrics (tracked daily)
1. **candidate/ files remaining**
2. **Files promoted this week** (target: 200–500)
3. **MATRIZ pass rate** (target: 100%)
4. **Coverage delta vs baseline** (≥ 0)
5. **Quarantined AuthZ tests** (goal: trending ↓ weekly)
6. **Import failures** (target: 0)

### Dashboard Commands
```bash
# Real-time status
python3 tools/dashboard_bot.py --mode update

# Weekly executive report
python3 tools/dashboard_bot.py --mode exec-summary --output artifacts/weekly_$(date +%Y%m%d).md
```

### Slack/PR Integration
Dashboard bot automatically posts metrics to every promotion PR as a comment.

---

## Claude Code Cockpit Prompts (ready to paste)

### Daily Mode (Batch PR)
```
Run batch_cockpit.py in T4 mode.
If any gate fails, halt and post a comment with the failing artifact excerpt and a minimal patch plan.
Otherwise open a Draft PR using promotion template; populate numbers from artifacts.
```

### Burst Mode (Weekend)
```
Run burst_cockpit.py --target 300 with checkpoints every 100.
If a checkpoint fails, stop and create a single PR with partial progress and the failure report.
If all pass, open one summary PR with the checkpoint table and cumulative coverage delta.
```

### Quarantine Sweep (Fridays)
```
Enumerate @authz_quarantine tests.
For each: link open issue, show minimal policy/contract diff to pass, and open a "Fix Friday" PR stack.
Remove markers only when green.
```

---

## Risk Register (honest + small)

### Known Risks & Mitigations
- **Hidden cross-module import** → Caught by import_failures.json; add shim or promote missing dep
- **Coverage drag from low-signal files** → Split future batches by "coverage impact score"
- **Quarantine creep** → Friday sweeps keep debt bounded; track count weekly
- **Burst validation failures** → Auto-halt prevents progression; checkpoints enable resume

### Risk Monitoring
```bash
# Daily risk check
python3 tools/dashboard_bot.py --mode update | grep "🟡\|❌"

# Weekly risk review
grep -E "(❌|🟡)" artifacts/weekly_*.md
```

---

## Definition of Done (migration complete)

### Phase 1: Drain Complete
- [ ] **candidate/ ≤ 10%** → Increase batch size to 100/day
- [ ] **MATRIZ 100% green** → All consciousness contracts valid
- [ ] **AuthZ quarantine = 0** → All authorization tests pass

### Phase 2: Legacy Sunset
- [ ] **No production imports via legacy** → All imports use flat-root
- [ ] **Schedule compat layer removal** → 2-week heads-up for final cleanup
- [ ] **Coverage ≥ pre-migration baseline** → Quality maintained throughout

### Success Criteria
- **Zero breaking changes** during migration
- **Complete audit trail** via promotion logs + git history
- **Faster CI/CD** due to simplified import structure
- **Developer velocity boost** from reduced cognitive overhead

---

**Status**: Ready for production deployment
**Confidence**: T4/0.01% bulletproof with enterprise-grade guardrails
**Timeline**: 15-18 weeks to completion with hybrid velocity