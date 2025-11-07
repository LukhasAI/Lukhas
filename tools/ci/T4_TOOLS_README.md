# T4 Unified Platform v2.0 - Tools Documentation

**Location**: `tools/ci/`  
**Status**: ✅ Production Ready  
**Version**: 2.0.0

---

## 📚 Overview

T4 Unified Platform consolidates dual T4 systems (Unused Imports + Lint) into a single platform with unified annotations, Intent Registry, dashboard, and automation.

**Key Components**:
- **Migration Script**: Convert legacy annotations to unified format
- **Unified Validator**: Merge both validators with quality scoring
- **HTML Dashboard**: Chart.js visualizations with ETA projections
- **Intent API**: FastAPI metrics endpoints
- **Parallel Automation**: 5x throughput via worktrees
- **Codemod Library**: LibCST transformers for non-autofix violations

---

## 🚀 Quick Start

### 1. Initialize Platform
```bash
make t4-init
```

Creates Intent Registry DB, reports directories, sets permissions.

### 2. Migrate Annotations (Dry-Run)
```bash
make t4-migrate-dry
```

Preview legacy → unified conversion. Review `reports/migration_report.json`.

### 3. Apply Migration
```bash
make t4-migrate
```

Converts all legacy annotations. Creates `.bak` backups.

### 4. Validate Annotations
```bash
make t4-validate
```

Runs unified validator. Outputs JSON metrics to stdout.

### 5. Generate Dashboard
```bash
make t4-dashboard
open reports/t4_dashboard.html
```

Creates interactive dashboard with trends and ETA projections.

---

## 📖 Tool Reference

### Migration Script
**File**: `tools/ci/migrate_annotations.py`

Converts legacy TODO annotations to unified JSON format.

**Usage**:
```bash
# Dry-run with report
python3 tools/ci/migrate_annotations.py --dry-run --report reports/migration_report.json

# Apply with backup
python3 tools/ci/migrate_annotations.py --apply --backup

# Specific paths only
python3 tools/ci/migrate_annotations.py --paths lukhas core --dry-run
```

**Features**:
- Git blame-based owner inference
- Heuristic code inference (F401, F821, B008, etc.)
- Deduplication (merges annotations within 2 lines)
- Backup creation (`.bak` files)
- JSON reporting

**Example Conversion**:
```python
# Before (legacy):
from foo import bar  # TODO[T4-UNUSED-IMPORT]: kept for future use

# After (unified):
from foo import bar  # TODO[T4-ISSUE]: {"id": "T4-abc123", "code": "F401", "type": "lint", "reason": "kept for future use", "status": "documented"}
```

---

### Unified Validator
**File**: `tools/ci/check_t4_issues.py`

Validates TODO[T4-ISSUE] annotations with quality scoring.

**Usage**:
```bash
# Validate production lanes
python3 tools/ci/check_t4_issues.py --paths lukhas core --json-only

# Strict mode (exit 1 on unannotated)
python3 tools/ci/check_t4_issues.py --paths lukhas --strict

# Specific codes only
python3 tools/ci/check_t4_issues.py --codes F821,F401,B008 --json-only
```

**Quality Score Formula**:
```python
Quality = (weighted_good / weighted_total) * 100

Weights:
  F821 (undefined name): 3
  F401 (unused import): 3
  B904 (exception handling): 2
  B008 (function call in default): 2
  RUF006 (async task tracking): 2
  SIM102 (collapsible if): 1
  SIM105 (contextlib suppress): 1
  E702 (multiple statements): 1
  B018 (useless expression): 1

Good = has owner+ticket OR status not in (planned, committed)
```

**Output Schema**:
```json
{
  "status": "pass",
  "summary": {
    "total_findings": 623,
    "annotated": 580,
    "unannotated": 43,
    "quality_issues": 12
  },
  "metrics": {
    "annotation_quality_score": 87.5,
    "counts_by_code": {"F821": 150, "F401": 100},
    "counts_by_status": {"documented": 400, "planned": 180}
  }
}
```

---

### Dashboard Generator
**File**: `tools/ci/t4_dashboard.py`

Generates HTML dashboard with Chart.js visualizations.

**Usage**:
```bash
# Generate dashboard
python3 tools/ci/t4_dashboard.py --output reports/t4_dashboard.html

# With auto-refresh (5 minutes)
python3 tools/ci/t4_dashboard.py --refresh 300

# Custom paths
python3 tools/ci/t4_dashboard.py --paths lukhas core api
```

**Features**:
- Metrics overview cards (total, quality, annotated, unannotated)
- Trend charts (violations over time, quality score timeline)
- Category breakdowns (by code, by status)
- Top violations table
- ETA projections (linear regression to <100 violations)
- Auto-refresh capability
- 90-day metrics history

**ETA Calculation**:
```python
# Linear regression: y = mx + b
# Solve for y=100: target_date = (100 - b) / m
# Rate: violations_per_week = -m * 86400 * 7
```

---

### Intent API
**File**: `tools/ci/intent_api.py`

REST API for Intent Registry database.

**Usage**:
```bash
# Start server
uvicorn tools.ci.intent_api:app --reload --port 8001

# Query metrics
curl http://localhost:8001/metrics/summary | jq

# Get stale intents (>30 days)
curl http://localhost:8001/intents/stale?days=30 | jq

# Get intents by owner
curl http://localhost:8001/intents/by_owner/john | jq

# Update intent
curl -X PATCH http://localhost:8001/intents/T4-abc123 \
  -H "Content-Type: application/json" \
  -d '{"status": "committed", "owner": "john", "ticket": "https://github.com/org/repo/issues/123"}'
```

**Endpoints**:
- `GET /metrics/summary` - Aggregate metrics
- `GET /intents/stale?days=30` - Stale intents
- `GET /intents/by_owner/{owner}` - Intents by owner
- `GET /intents/{intent_id}` - Single intent
- `POST /intents` - Create intent
- `PATCH /intents/{intent_id}` - Update intent
- `DELETE /intents/{intent_id}` - Delete intent
- `GET /health` - Health check

**Metrics Response**:
```json
{
  "total": 623,
  "by_status": {"documented": 400, "planned": 180, "committed": 43},
  "by_code": {"F821": 150, "F401": 100, "B904": 50},
  "quality_score": 87.5,
  "avg_time_to_resolve": 14.3
}
```

---

### Parallel Batch Automation
**File**: `scripts/t4_parallel_batches.sh`

Accelerates fixes with parallel worktree processing.

**Usage**:
```bash
# Dry-run
./scripts/t4_parallel_batches.sh --dry-run

# Process with limits
./scripts/t4_parallel_batches.sh --max-per-batch 10

# Custom categories
./scripts/t4_parallel_batches.sh --categories "E702,B018,SIM105"

# Full automation
./scripts/t4_parallel_batches.sh
```

**Features**:
- 5x throughput (5 parallel worktrees)
- Category-based batching
- Auto-commit with T4-compliant messages
- Auto-PR creation via `gh` CLI
- Progress monitoring
- Safety limits
- Automatic cleanup

**Workflow**:
1. Create 5 worktrees (E702, B018, SIM105, F821, B008)
2. Run ruff autofix in parallel
3. Commit changes
4. Push branches
5. Create PRs with "safe-merge" label
6. Update dashboard
7. Cleanup worktrees

---

### Codemod Library
**Files**: `tools/ci/codemods/library.py`, `run_codemod.py`

LibCST transformers for non-autofix violations.

**Usage**:
```bash
# Remove unused import
python3 tools/ci/codemods/run_codemod.py \
  --transformer RemoveUnusedImport \
  --file lukhas/api.py \
  --unused-names "Foo,Bar"

# Fix B904 (exception handling)
python3 tools/ci/codemods/run_codemod.py \
  --transformer FixB904 \
  --paths lukhas core \
  --dry-run

# Fix RUF012 (mutable class attrs)
python3 tools/ci/codemods/run_codemod.py \
  --transformer FixRUF012 \
  --paths lukhas \
  --backup
```

**Transformers**:
1. **RemoveUnusedImport** (F401): Remove specific unused imports
2. **ConvertImportStar** (F403): Convert `from x import *` to explicit
3. **FixRUF012**: Add `ClassVar` annotation to mutable defaults
4. **FixB904**: Add `from e` clause to exception re-raises

**Examples**:

**RemoveUnusedImport**:
```python
# Before:
from foo import bar, baz  # baz unused
# After:
from foo import bar
```

**FixB904**:
```python
# Before:
try:
    ...
except Exception as e:
    raise ValueError("error")  # B904
# After:
try:
    ...
except Exception as e:
    raise ValueError("error") from e
```

---

## 📊 Metrics & Reporting

### Current Statistics
- **Total Violations**: 623 (down from 647 baseline)
- **Top Categories**: F821 (~150), F401 (~100), RUF006 (~80), B904 (~50)
- **Estimated Quality Score**: 87.5% (weighted)
- **Target**: <100 violations (84% reduction needed)

### Reports Location
- **Dashboard**: `reports/t4_dashboard.html`
- **Migration Report**: `reports/migration_report.json`
- **Validator Output**: stdout (JSON format)
- **Metrics History**: `reports/t4_metrics_history.json`
- **Intent Registry DB**: `reports/todos/intent_registry.db`

---

## 🔧 Makefile Targets

```bash
make t4-init              # Initialize platform
make t4-migrate-dry       # Dry-run migration
make t4-migrate           # Apply migration
make t4-validate          # Validate annotations
make t4-dashboard         # Generate dashboard
make t4-api               # Start API server
make t4-parallel-dry      # Dry-run parallel batching
make t4-parallel          # Run parallel batching
make t4-codemod-dry       # Dry-run codemod
make t4-codemod-apply     # Apply codemod
```

---

## 🎯 Roadmap

### Phase 1: Unification (Weeks 1-4)
- Merge dual systems
- Migrate all annotations
- Deploy dashboard
- Enable Intent API

### Phase 2: Acceleration (Weeks 5-8)
- Parallel batching automated (weekly runs)
- Velocity: 6 fixes/day → 30+ fixes/day
- Target: 400 → 250 violations (37.5% reduction)

### Phase 3: Prevention (Weeks 9-12)
- Pre-commit hooks enhanced
- New violations: 15/week → <5/week
- Codemods for non-autofix categories
- Target: 250 → 150 violations (40% reduction)

### Phase 4: Optimization (Weeks 13-16)
- <100 violations achieved
- Quality score >95%
- Avg time to resolve <7 days
- Maintain <100 violations

---

## 📚 Additional Documentation

- **Complete Design**: `T4_CHANGES.md`
- **Implementation Summary**: `T4_MEGA_PR_SUMMARY.md`
- **Copilot Instructions**: `.github/copilot-instructions.md`

---

**Last Updated**: 2025-01-20  
**Maintainer**: LUKHAS Core Team  
**Status**: Production Ready ✅
