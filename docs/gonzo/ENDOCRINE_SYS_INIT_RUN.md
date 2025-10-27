# LUKHAS Endocrine System — Initialization & Operational Runbook

**Date**: 2025-08-02
**Session**: Professional Architecture + Endocrine System Implementation
**Status**: ✅ Completed (documentation refined)

---

## 🚨 MATRIZ Migration Update

**Team Announcement (Ready to Share):**

We've completed MATRIZ case standardization for all production code and integration tests!

**Completed:**
✅ serve/ (2 imports)
✅ core/ (2 imports)  
✅ tests/integration/ (20 imports)

**Status:** 3 PRs in CI validation

**Next:** tests/unit + tests/smoke (23 imports) - will migrate after current PRs pass CI

**CI Mode:** Warning (logs occurrences, doesn't block)
**Timeline:** Flip to blocking mode after critical tests are migrated and stable (~48 hours)

**Action Required:** Avoid large MATRIZ-related changes until migrations merge. Use uppercase `from MATRIZ import X` for new code.

Questions? See MATRIZ_MIGRATION_GUIDE.md

---

## Purpose
Initialize the endocrine subsystem and verify correct modulatory integration into MATRIZ: attention bias, arbitration tone, and neuroplasticity modulation, while ensuring operational safety and verifiability.

**Owner:** `@owner_ops`
**Safety lead:** `@guardian_owner`

---

## Preconditions (must verify before run)
- [ ] System health >= 90% for `lukhas_memory`, `lukhas_consciousness`, and `event_bus`.
- [ ] Compatibility shim & migration PRs merged (if needed).
- [ ] Backup: WaveC pre-snapshot created and stored with SHA.
- [ ] Rollback scripts and last-good snapshot available.
- [ ] Ethics/privacy approval for any human-derived data.

---

## Calibration & Baseline
1. Run calibration stimuli (N=50) to establish baseline hormone medians and stdevs.
2. Compute `alert_threshold = median + 3*std` for each hormone; persist with metadata.

---

## Initialization Steps (operator)

**ENV:**
```bash
export RUN_ID=$(uuidgen)
```

**Step 1 — Start endocrine service**
```bash
python3 core/endocrine/start_engine.py --run-id $RUN_ID
```

**Step 2 — Inject controlled stimuli**
- Stress pulse: cortisol +0.2 for 30s
- Reward pulse: dopamine +0.3 for 5s

```python
core.endocrine.set_pulse('cortisol', delta=0.2, duration=30, run_id=RUN_ID)
```

**Step 3 — Observe and record**
- Monitor attention bias, arbitration tone, and neuroplasticity metrics.
- Log to `artifacts/endocrine/$RUN_ID/` with signed metadata.

**Step 4 — Acceptance checks**
- No hormone exceeds saturation bounds.
- Decision shift within expected envelope (±20%) unless intended.
- No unexpected Guardian vetoes.

---

## Safety & Stop Conditions
**Automatic stop if**:
- hormone_level > MAX_SAFE
- memory_coherence drops by > DRIFT_CRITICAL (e.g., 0.3)
- Guardian issues a kill event

**Emergency stop command:**
```bash
python3 core/endocrine/emergency_stop.py --run-id $RUN_ID
python3 scripts/restore_wavec_snapshot.py --snapshot last_good
```

---

## Validation & Acceptance Criteria
- Endocrine update loop runs without exception for 30 minutes.
- Neuroplasticity and mood follow predicted curves within ±20%.
- All artifacts and signed snapshots stored in `lukhas.store`.

---

## Post-run Tasks
- Persist artifacts and logs under `artifacts/endocrine/$RUN_ID/`.
- Run regression tests across memory, dream and decision flows.
- Safety lead reviews and signs off before staging roll.

---

## Emergency & Audit
- All runs are auditable: store `run_id`, operator, timestamp, git SHA, snapshot IDs and signed hashes.
- Use `docs/gonzo/INCIDENT_REPORT_TEMPLATE.md` for reports.

---

## Next Steps
1. Define endocrine-to-MATRIZ contract (events, rate limits, safety bounds).
2. Implement endocrine calibration suite and chaos tests.
3. Integrate endocrine telemetry into the system dashboard.
