---
status: wip
type: documentation
---
# LAB BRIEFING — MATRIZ Rollout

**Objective:** Assign lanes module-by-module; nightly soak + chaos; safe canary.
**Focus now:** Guardian, Orchestrator, Memory, Consciousness, Identity.

## Required Gates (all must pass)
1) E2E perf budgets: tick<100ms, reflect<10ms, decide<50ms, E2E<250ms (CI95% bootstrap)
2) Schema drift guard (golden snapshot; breaking change detector)
3) Chaos fail-closed (guardian + kill-switch; rollback ≤30s)
4) Telemetry contracts (promtool tests; no dynamic label IDs)
5) Import hygiene (lane boundaries)

## Canary Policy
Start 5% → 25% in 12h if burn-rate clean (4×/1h, 2×/6h), SLO deltas ≤10%; rollback ≤30s.

## Operator Quick Commands
```bash
python3 scripts/matriz/check_readiness.py --modules guardian orchestrator memory consciousness identity \
  --out artifacts/matriz_readiness_report.json
python3 scripts/matriz/promote.py --module lukhas.consciousness --from candidate --to integration \
  --evidence-out artifacts/consciousness_promo.json --sign
```
