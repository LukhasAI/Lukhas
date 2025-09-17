# Dream System CI Badges

Add these badges to your main README.md to show CI status:

## EXPAND Phase CI

```markdown
<!-- EXPAND Nightly Bench (heavy; cron + manual) -->
[![Dream EXPAND Bench](https://github.com/ORG/REPO/actions/workflows/dream-expand-bench.yml/badge.svg?branch=main)](https://github.com/ORG/REPO/actions/workflows/dream-expand-bench.yml)

<!-- EXPAND Smoke (auto on path changes) -->
[![Dream EXPAND Smoke](https://github.com/ORG/REPO/actions/workflows/dream-expand-smoke.yml/badge.svg?branch=main)](https://github.com/ORG/REPO/actions/workflows/dream-expand-smoke.yml)
```

## Workflow Overview

### Smoke Tests (`dream-expand-smoke.yml`)
- **Trigger**: Automatic on PR/push to paths:
  - `candidate/consciousness/dream/expand/**`
  - `benchmarks/dream/**`
  - `tests/benchmarks/**`
  - `tests/unit/dream/**`
- **Duration**: ~15 minutes
- **Purpose**: Fast safety validation and determinism checks
- **Features**: All EXPAND features disabled (safe mode)

### Benchmark Suite (`dream-expand-bench.yml`)
- **Trigger**: Manual dispatch + nightly cron (02:00 UTC)
- **Duration**: ~60 minutes
- **Purpose**: Comprehensive analysis and deep benchmarks
- **Features**: Stability, calibration, taxonomy, configuration recommendations
- **Options**: Synthetic cases, parameter sweeps, dashboard generation

## Usage

**For Development:**
- Smoke tests run automatically on relevant changes
- Get early feedback without heavy resource usage

**For Analysis:**
- Manually trigger bench workflow for deep analysis
- Nightly runs provide regular health monitoring
- Download artifacts for detailed inspection

**Badge Integration:**
Replace `ORG/REPO` with your GitHub organization and repository name.