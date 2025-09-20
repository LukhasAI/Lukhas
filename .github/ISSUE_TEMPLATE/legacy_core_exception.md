---
name: Legacy Core Import Exception
about: Request exception for legacy 'core' import usage during sunset
title: "[LEGACY-CORE] Exception request: "
labels: ["legacy-core", "sunset-exception", "platform"]
assignees: []
---

## Exception Request Details

**Service/Component**:
**Team**:
**Priority**: [ ] P0-Critical [ ] P1-High [ ] P2-Medium [ ] P3-Low

## Legacy Import Context

**Current legacy import patterns** (attach grep output):
```
# Run: grep -r "from core\|import core" . --include="*.py" | head -20
```

**Estimated volume**:
- Number of files:
- Number of import statements:
- Complexity (simple/complex):

## Migration Barriers

**Why can't codemod fix this automatically?**
[ ] Dynamic imports
[ ] String-based imports
[ ] Complex metaprogramming
[ ] External dependency conflicts
[ ] Other (explain below)

**Details**:


## Exception Duration

**Requested sunset delay**:
- [ ] 1 week (simple refactor)
- [ ] 2 weeks (moderate complexity)
- [ ] 4 weeks (complex dependencies)
- [ ] 8+ weeks (architectural changes needed)

**Migration plan**:
1.
2.
3.

## Business Impact

**What breaks if we proceed with sunset now?**


**Customer impact if delayed**:


## Platform Team Review

- [ ] Exception approved by Platform Team lead
- [ ] Sunset timeline updated in docs/LEGACY_CORE_SUNSET_PLAN.md
- [ ] Monitoring alerts configured for this component
- [ ] Regular check-ins scheduled

**Approval signature**: @platform-team-lead

## Tracking

**Metrics to track during exception period**:
- [ ] `legacy_core_import_total{service="YOUR_SERVICE"}`
- [ ] Migration progress (files converted/week)
- [ ] Blockers resolved

**Check-in schedule**:
- [ ] Weekly status updates
- [ ] Bi-weekly platform team review
- [ ] Exception expiry review 2 weeks before deadline

---

**For Platform Team Use**

**Exception ID**: LEGACY-{{ date }}-{{ component }}
**Status**: [ ] Approved [ ] Rejected [ ] Under Review
**Expiry Date**:
**Extension Count**: 0

*This template ensures controlled exceptions during legacy core sunset with clear accountability and timeline tracking.*