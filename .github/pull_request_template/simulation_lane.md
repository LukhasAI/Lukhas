# Simulation Lane PR

> Purpose: changes to `consciousness/simulation/*`, related tests, schemas, or Dream Inbox.

## Summary
- What changed and why?
- Any user-visible behavior?
- Risk level (L0–L5) and mitigations:

## Checklists

### Defensive Controls
- [ ] Feature flag respected (`SIMULATION_ENABLED`)  
- [ ] Ethics gate covers: consent, duress/shadow, unsafe goal keywords  
- [ ] Adapter isolation: **no imports** from `adapters/*` (import-linter clean)  
- [ ] MATADA node envelope validates (`schemas/matriz_node_v1.json`)  
- [ ] Deterministic scoring maintained (golden tests unaffected)

### Tests & CI
- [ ] Canary tests updated/passing (`make t4-sim-lane`)  
- [ ] Import contracts pass (`make imports-guard`)  
- [ ] Summary refreshed (`sim-lane: generate summary`)  
- [ ] Dream Inbox writes gated by `memory.inbox.dreams.write` scope

### Capabilities & Policy
- [ ] `consciousness.simulation.schedule` and `.collect` enforced  
- [ ] Any new scopes documented in `docs/consciousness/README.md`

### Artifacts
- [ ] `docs/consciousness/SIMULATION_SUMMARY.md` updated  
- [ ] MATADA schema changes (if any) reflected in `schemas/` + changelog

## Rollback
- [ ] Feature flag can disable at runtime  
- [ ] No data migrations required OR migration/rollback plan included

/label t4-sim-lane