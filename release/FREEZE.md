# Release Freeze Checklist

- [ ] CI green on main (all workflows)
- [ ] Manifests 100% generated; critical modules have context
- [ ] Guardian/North policy review signed
- [ ] Perf smoke: p95 targets recorded & met on T1 paths
- [ ] Observability: spans/metrics/logging present for T1/T2
- [ ] Rollback plan + checkpoints documented
- [ ] Contracts versioned; breaking changes flagged
- [ ] Linkcheck clean; docs updated (Top & star pages)
