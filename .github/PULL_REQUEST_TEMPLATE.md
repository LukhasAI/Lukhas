## What/Why
Describe the change in one sentence. Why is this change necessary?

## Checklist (T4 guardrails)
- [ ] **Snapshot**: Recorded state snapshot for audit trail (attach ledger id or file)
- [ ] **Tests**: Unit/integration tests added/updated. All tests pass: `pytest -q`
- [ ] **Module Registry**: New/modified modules registered in `lukhas/core/module_registry.py`
- [ ] **Observability**: Metrics intact (`lukhas_guardian_decision_total` etc.)
- [ ] **Documentation**: Updated README, docs/guardian-enhancements.md
- [ ] **Zero-regression**: No behavior changes (explain test coverage)
- [ ] **Canary**: Rollback plan provided for risky changes
- [ ] **Audit**: Dual approval captured for governance/flag changes

## Implementation notes
Short implementation notes and reasoning. Link to discovery report if relevant.

## Testing instructions
How to run tests locally and manual verification steps.

## Snapshot metadata
Attach snapshot output or ledger transaction id:
```

---

**T4 BRIEF FOR COPILOT:**
```
- Consolidating guardian code with strict safety guardrails
- Discovery script shows exact duplicates and similarity scores
- Do NOT merge until discovery report reviewed by human
- Quick wins: PYTHONPATH/import fixes only, must pass pytest
- Any functional consolidation requires:
  * Module registration in module_registry.py
  * Unit tests covering preserved behavior
  * Audit snapshot with ledger id
  * Updated docs in guardian/ and docs/
  * Forwarding shims for old APIs (deprecate, don't break)
  * Canary/rollback plan
- Strategy driven by overlap %:
  * >50% overlap: merge
  * <10% overlap: modular API (Guardian pattern)
  * Forwarding: document and verify
```
