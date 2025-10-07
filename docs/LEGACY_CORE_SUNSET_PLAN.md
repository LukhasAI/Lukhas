---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

# Legacy Core Import Sunset Plan

## Current State
- ✅ Robust alias system implemented with MetaPathFinder
- ✅ All import styles supported: `import core.X`, `from core import X`, `from core.X import Y`
- ✅ Invariant tests lock behavior against regressions
- ✅ Regression guard prevents new legacy imports
- ✅ Brownout and warning toggles available

## Timeline

### Phase 1: Now (Monitoring)
- **Status**: Alias ON, warnings OFF by default
- **Action**: Enable `LUKHAS_WARN_LEGACY_CORE=1` in canary environments only
- **Goal**: Baseline legacy usage patterns

### Phase 2: T+1 Week (Discovery)
- **Action**: Enable `LUKHAS_WARN_LEGACY_CORE=1` in production for 24h
- **Goal**: Surface remaining legacy import paths
- **Metric**: Track `legacy_core_import_total` in logs/metrics
- **Fix**: Update any discovered legacy imports to `lukhas.core`

### Phase 3: T+2 Weeks (Brownout Test)
- **Action**: 10-minute brownout with `LUKHAS_DISABLE_LEGACY_CORE=1` on 10% traffic
- **Goal**: Validate alias can be safely disabled
- **Rollback**: Immediate if any errors detected
- **Success criteria**: Zero errors during brownout window

### Phase 4: T+4 Weeks (Announcement)
- **Action**: Announce sunset date to engineering teams
- **Action**: Enable `LUKHAS_WARN_LEGACY_CORE=1` weekly for visibility
- **Goal**: Give teams time to migrate remaining usage

### Phase 5: Sunset (When Ready)
- **Trigger**: `legacy_core_import_total` stays at 0 for 7 consecutive days
- **Action**: Remove alias system from `core/__init__.py`
- **Verification**: All tests still pass without alias

## Environment Controls

### Warning Toggle
```bash
# Enable warnings (for monitoring)
export LUKHAS_WARN_LEGACY_CORE=1

# Disable warnings (default)
export LUKHAS_WARN_LEGACY_CORE=0
```

### Brownout Toggle
```bash
# Enable brownout (for testing)
export LUKHAS_DISABLE_LEGACY_CORE=1

# Disable brownout (default)
export LUKHAS_DISABLE_LEGACY_CORE=0
```

## Monitoring

### Metrics Collection
Route ImportWarning logs to metrics:
```promql
# Legacy import rate by service
sum(rate(legacy_core_import_total[5m])) by (service)

# Zero-detection for sunset readiness
legacy_core_import_total == 0
```

### Alerts
- Alert when `legacy_core_import_total > 0` for 2 consecutive intervals
- Dashboard showing legacy usage trends over time

## Ownership Matrix

- **Alias owner**: Platform team (merges, brownouts, rollback)
- **Test owner**: QA team (core alias tests + budget test maintenance)
- **Comms owner**: Engineering productivity (sunset announcements)
- **SRE owner**: Alert configuration and brownout monitoring

## Rollback Procedures

### Emergency Rollback
1. Set `LUKHAS_DISABLE_LEGACY_CORE=0` (disable brownout)
2. Set `LUKHAS_WARN_LEGACY_CORE=0` (disable warnings)
3. Alias returns to silent operation

### Permanent Rollback
If sunset fails:
1. Keep alias system indefinitely
2. Disable warning/brownout toggles
3. Document as permanent compatibility layer

## Success Criteria

### GO Criteria
- ✅ CI green with guard script active
- ✅ WARNs observed < 5/day after 24h monitoring
- ✅ Brownout recovers cleanly in canary
- ✅ Import budget p95 < 250ms
- ✅ No new legacy imports in latest diffs

### NO-GO Criteria
- Any production errors during brownout
- Legacy usage > 100 imports/day after announcement
- Import budget regression > 500ms
- Test failures after brownout

If NO-GO: Rollback to WARN-only mode, fix offenders, retry brownout.