# Infrastructure: EQNOX/GLYPHs/Routing + Ops/Observability/CI Prompts

> **⚠️ DO NOT EXECUTE THESE PROMPTS DIRECTLY**
>
> This document contains micro-PR prompts for future task breakdown.
> Each item should be reviewed, prioritized, and added to MASTER_LOG.md before execution.

---

## Overview

This document contains **10 micro-PR prompts** for implementing EQNOX/GLYPHs routing and operational infrastructure.

**Priority**: Medium-High - System reliability and observability
**Estimated Total**: ~45 hours
**Value Lever**: Production readiness and operational excellence

---

## D) EQNOX / GLYPHs / Routing (5 prompts)

### D1 — Glyph integrity hash

**Branch**: `feat/glyph-hash`
**Scope**: `eqnox/glyphs/model.py`
**Edits**:
- canonical JSON → SHA256(Base64) `hash()` method
- ensures glyph immutability and verifiability
- enables glyph versioning and comparison

**Commit**: `feat(eqnox): glyph integrity hash`

---

### D2 — Glyph scalar export

**Branch**: `feat/glyph-export-scalar`
**Scope**: `eqnox/glyphs/metrics.py`
**Edits**:
- `export_scalar(g)->{attractor,repeller}` function
- converts glyph to numerical representation
- enables quantitative analysis and ML features

**Commit**: `feat(eqnox): export scalar metrics`

---

### D3 — Router log-only mode

**Branch**: `feat/eqnox-router-logonly`
**Scope**: `eqnox/router.py`
**Edits**:
- `LOG_ONLY` config short-circuits execution and logs routes
- safety mode for testing routing decisions
- dry-run capability

**Commit**: `feat(eqnox): router log-only safety mode`

---

### D4 — Resonance snapshot event

**Branch**: `feat/eqnox-resonance-snap`
**Scope**: `eqnox/router.py`
**Edits**:
- emit `ResonanceSnapshot` with glyph hashes and decision id
- enables replay and debugging of routing decisions
- audit trail for consciousness routing

**Commit**: `feat(eqnox): emit resonance snapshots`

---

### D5 — Tags crosswalk hormones↔emotion

**Branch**: `feat/tags-hormone-crosswalk`
**Scope**: `core/tags/registry.py`
**Edits**:
- define canonical mapping between hormone levels and emotion tags
- `explain_state(endocrine)->[tags]` function
- bidirectional translation

**Commit**: `feat(tags): hormone↔emotion crosswalk`

---

## E) Ops / Observability / CI (5 prompts)

### E1 — `/metrics` dream/feedback counters

**Branch**: `feat/metrics-dream-feedback`
**Scope**: `serve/metrics.py`
**Edits**:
- counters for dream totals, regret totals, rollbacks, feedback totals
- Prometheus-compatible format
- enables operational dashboards

**Metrics to add**:
```python
dream_total = Counter('lukhas_dream_total', 'Total dreams generated')
dream_regret_total = Counter('lukhas_dream_regret_total', 'Dreams with regret signal')
dream_rollback_total = Counter('lukhas_dream_rollback_total', 'Dream rollbacks')
feedback_total = Counter('lukhas_feedback_total', 'Total feedback records')
```

**Commit**: `feat(metrics): dream/rollback/feedback counters`

---

### E2 — Healthz includes guardian summary

**Branch**: `feat/healthz-guardian`
**Scope**: `serve/healthz.py`
**Edits**:
- include `guardian_enabled`, `last_veto_reason`, `last_veto_ts`
- surfaces Guardian state in health checks
- enables monitoring of safety system

**Response format**:
```json
{
  "status": "healthy",
  "guardian": {
    "enabled": true,
    "last_veto_reason": "unsafe_content",
    "last_veto_ts": "2025-11-11T10:30:00Z",
    "total_vetoes_24h": 3
  }
}
```

**Commit**: `feat(healthz): surface guardian state`

---

### E3 — Import-lane banner (CI)

**Branch**: `chore/lanes-banner`
**Scope**: `scripts/consolidation/block_labs_imports.sh`
**Edits**:
- red banner + explicit remediation steps on violation
- improves developer experience when lane boundaries are violated
- clear guidance on how to fix

**Banner format**:
```
╔════════════════════════════════════════════════════════════╗
║  ❌ LANE BOUNDARY VIOLATION DETECTED                      ║
╠════════════════════════════════════════════════════════════╣
║  File: lukhas/core/processor.py                           ║
║  Illegal import: from labs.experimental import Feature    ║
║                                                            ║
║  REMEDIATION:                                              ║
║  1. Move Feature to core/ or lukhas/                      ║
║  2. Use registry pattern for dynamic loading              ║
║  3. See docs/architecture/LANE_SYSTEM.md                  ║
╚════════════════════════════════════════════════════════════╝
```

**Commit**: `chore(ci): clearer lane-guard violation banner`

---

### E4 — JSONL rotation helper

**Branch**: `feat/log-rotation-helper`
**Scope**: `core/util/log_rotate.py`
**Edits**:
- date-based rotate+symlink `current.jsonl` for sinks
- automatic daily rotation
- symlink to current day's log file

**Implementation**:
```python
def rotate_if_needed(base_path: str) -> str:
    """
    Returns path to current day's log file.
    Creates YYYY-MM-DD.jsonl and symlinks current.jsonl -> YYYY-MM-DD.jsonl
    """
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"{base_path}/{today}.jsonl"
    symlink = f"{base_path}/current.jsonl"

    if not os.path.exists(log_file):
        open(log_file, 'a').close()

    if os.path.islink(symlink):
        os.unlink(symlink)
    os.symlink(log_file, symlink)

    return log_file
```

**Commit**: `feat(util): simple date-based JSONL rotation`

---

### E5 — Bench harness: drift baseline cache

**Branch**: `feat/bench-drift-baseline`
**Scope**: `bench/baseline_cache.py`
**Edits**:
- cache last N drift stats
- write `bench/baseline.json`
- enables regression detection

**Baseline format**:
```json
{
  "version": "1.0",
  "last_updated": "2025-11-11T10:00:00Z",
  "baseline_stats": {
    "mean_coherence": 0.85,
    "std_coherence": 0.05,
    "p95_latency_ms": 245,
    "mean_regret": 0.02
  },
  "samples": 100,
  "window_days": 7
}
```

**Commit**: `feat(bench): baseline drift cache`

---

## Implementation Notes

### EQNOX/GLYPHs (D1-D5)

**Dependencies**:
- D1 (integrity hash) should be done first - foundational
- D2 (scalar export) depends on D1 (hash for versioning)
- D3 (log-only mode) can be done independently
- D4 (resonance snapshot) depends on D1 (glyph hash)
- D5 (tags crosswalk) can be done independently

**Testing Strategy**:
- Unit tests for D1 (hash stability)
- Property-based tests for D2 (scalar export consistency)
- Integration tests for D3 (log-only routing)
- E2E tests for D4 (full resonance flow)
- Validation tests for D5 (bidirectional mapping)

**Performance Considerations**:
- D1: Hash computation must be <1ms per glyph
- D2: Scalar export should be deterministic and fast
- D3: Log-only mode should have minimal overhead
- D4: Snapshot emission should be async

### Ops/Observability (E1-E5)

**Dependencies**:
- E1 (metrics) should be done early - enables monitoring
- E2 (healthz) can be done independently
- E3 (lane banner) is cosmetic, low priority
- E4 (log rotation) should be done before other logging features
- E5 (baseline cache) depends on benchmark infrastructure

**Operational Requirements**:
- E1: Metrics must be Prometheus-compatible
- E2: Healthz must respond <100ms
- E4: Log rotation must not lose data
- E5: Baseline cache must be atomic writes

**Monitoring Integration**:
- E1: Integrate with existing Grafana dashboards
- E2: Add to uptime monitoring (Pingdom, etc.)
- E5: Alert on significant drift from baseline

### Rollout Strategy

**Phase 1 (Week 1)**: Foundation
- D1 (glyph hash) - enables all glyph features
- E1 (metrics) - enables monitoring
- E4 (log rotation) - prevents disk issues

**Phase 2 (Week 2)**: Observability
- D2 (scalar export)
- D4 (resonance snapshots)
- E2 (healthz guardian)
- E5 (baseline cache)

**Phase 3 (Week 3)**: DX Improvements
- D3 (log-only mode) - testing tool
- D5 (tags crosswalk) - interpretability
- E3 (lane banner) - better errors

---

## Cross-System Integration

### EQNOX ↔ Consciousness
- D1 (integrity hash) enables glyph versioning in consciousness snapshots
- D4 (resonance snapshots) provides audit trail for consciousness routing
- D5 (hormone↔emotion crosswalk) bridges endocrine and cognitive systems

### Metrics ↔ Feedback
- E1 (dream/feedback counters) surfaces feedback system activity
- E2 (healthz guardian) exposes safety system state
- E5 (baseline cache) enables feedback-driven adaptation

### CI ↔ Lane System
- E3 (lane banner) improves developer experience
- Integrates with existing lane-guard checks
- Provides clear remediation guidance

---

## Production Readiness Checklist

### Before enabling in production:

**D1-D5 (EQNOX)**:
- [ ] Glyph hash collision testing (D1)
- [ ] Scalar export validation against known glyphs (D2)
- [ ] Log-only mode tested in staging (D3)
- [ ] Resonance snapshot storage capacity planned (D4)
- [ ] Hormone↔emotion crosswalk validated by psychology expert (D5)

**E1-E5 (Ops)**:
- [ ] Metrics dashboard created in Grafana (E1)
- [ ] Healthz endpoint added to uptime monitoring (E2)
- [ ] Lane banner tested on all violation types (E3)
- [ ] Log rotation tested across midnight (E4)
- [ ] Baseline cache tested with missing/corrupt files (E5)

---

## Security Considerations

### EQNOX (D1-D5)
- **D1**: Hash function must be cryptographically secure (use SHA-256)
- **D3**: Log-only mode should still enforce auth
- **D4**: Resonance snapshots may contain sensitive routing decisions - encrypt at rest

### Ops (E1-E5)
- **E1**: Metrics endpoint should require authentication
- **E2**: Healthz should not leak sensitive Guardian veto reasons
- **E5**: Baseline cache should be read-only in production

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
**Status**: Ready for task breakdown
