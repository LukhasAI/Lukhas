---
status: wip
type: documentation
owner: unknown
module: runbooks
redirect: false
moved_to: null
---

# 🚀 BATCH COCKPIT BRIEF - Claude Code Command Pack

## TL;DR - One Command Conveyor

```bash
# Execute next promotion batch (50 files, full validation, auto-PR)
python3 tools/batch_cockpit.py

# Or with custom settings
python3 tools/batch_cockpit.py --batch-size 75 --modules core --skip-pr
```

## What It Does (T4/0.01% Surgical)

**6-Step Automated Conveyor**:
1. **Plan Generation**: `promotion_selector.py` → `promotion_batch.plan.jsonl`
2. **Move Execution**: `promote_from_candidate.py` → git mv operations
3. **Validation Suite**: MATRIZ + coverage + import health checks
4. **Artifact Updates**: `promotion_log.md` + `import_failures.json`
5. **Git Operations**: Commit with structured message + trailers
6. **PR Creation**: Auto-generated with validation status + test plan

## Guardrails Built-In

- ✅ **No Regressions**: Pre-commit + CI block candidate/ additions
- ✅ **MATRIZ Gates**: Every batch validated against consciousness contracts
- ✅ **Coverage Ratchet**: Baseline maintained or explicit bypass required
- ✅ **Import Health**: Continuous monitoring via import_failures.json
- ✅ **History Preservation**: All moves via `git mv` (no history loss)

## Usage Patterns

### Daily Drain (Mon-Thu)
```bash
# Standard 50-file batch
python3 tools/batch_cockpit.py
```

### Friday Stabilization
```bash
# Dry run to see plan
python3 tools/batch_cockpit.py --dry-run

# Manual validation if needed
make validate-matrix-all
make authz-run
```

### Endgame Sprint (candidate/ < 100 files)
```bash
# Larger batches for final drain
python3 tools/batch_cockpit.py --batch-size 75
```

## Outputs Generated

### Automatic Artifacts
- `artifacts/promotion_batch.plan.jsonl` - Move plan
- `artifacts/promotion_log.md` - Updated with batch results
- `artifacts/import_failures.json` - Health status
- Git commit with structured message + Claude trailers
- GitHub PR with validation summary + test checklist

### Validation Reports
- MATRIZ contract compliance status
- Coverage baseline comparison
- Import health verification
- File count impact metrics

## Error Handling

- **MATRIZ Failures**: Batch stops, manual intervention required
- **Coverage Drops**: Blocked unless `allow:coverage-drop` label added
- **Import Errors**: Logged to artifacts, PR includes recovery plan
- **Git Conflicts**: Manual resolution with history preservation

## Integration Points

- **Pre-commit**: Rejects new candidate/ files automatically
- **CI Workflow**: `promotion-guard.yml` validates every PR
- **Coverage Tools**: `compare_coverage.py` baseline enforcement
- **MATRIZ System**: Full consciousness contract validation

---

## Quick Start

```bash
# First time setup (if needed)
pip install -r requirements.txt

# Execute batch conveyor
python3 tools/batch_cockpit.py

# Check results
git log -1 --oneline
cat artifacts/promotion_log.md | tail -20
```

**Status**: Ready for production deployment
**Safety**: T4/0.01% bulletproof with full rollback capability
**Pace**: Sustainable 50 files/day → candidate/ drain complete in ~45 days

---

## 💥 BURST MODE - Weekend Sprint Conveyor

### TL;DR - Accelerated Drain
```bash
# Weekend burst: 200 files in 4x50 batches with checkpoints
python3 tools/burst_cockpit.py --target 200

# Sprint mode: 400 files in 8x50 batches (max safe burst)
python3 tools/burst_cockpit.py --target 400 --max-batches 8

# Custom burst: 300 files in 6x50 batches
python3 tools/burst_cockpit.py --target 300 --batch-size 50
```

### What Burst Mode Does
**Multi-Batch Orchestration**:
- Executes 4-8 consecutive promotion batches automatically
- Validation checkpoints every 2 batches (MATRIZ + imports + coverage)
- Auto-halt on any validation failure (bulletproof safety)
- Single summary PR for entire burst session
- Checkpoint artifacts for audit trail

### Safety Features
- **Validation Gates**: MATRIZ + import health checked every 100 files
- **Auto-Halt**: Stops immediately on any validation failure
- **Rollback Ready**: Each batch preserves git history via git mv
- **Checkpoint Artifacts**: Full session logs in `artifacts/burst_checkpoint.json`
- **Max Batch Limit**: Hard cap prevents runaway execution

### Recommended Schedule
- **Mon-Thu**: Daily 50-file batches (`batch_cockpit.py`)
- **Friday**: Stabilization + validation review
- **Weekend**: Burst sessions 200-400 files (`burst_cockpit.py`)

### Timeline Impact
- **Baseline**: 50/day × 4 days = 200 files/week → 45 weeks
- **Hybrid**: 200/weekday + 300/weekend = 500 files/week → **18 weeks**
- **Sprint**: 200/weekday + 400/weekend = 600 files/week → **15 weeks**

🎯 **Next Action**: Choose your velocity and run the conveyor!