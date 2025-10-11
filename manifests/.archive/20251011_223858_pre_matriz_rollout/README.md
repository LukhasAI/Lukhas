# Archived Manifests - Pre-MATRIZ Rollout

**Archived**: 2025-10-11 22:38:58
**Reason**: Cleanup before MATRIZ discipline pack mass manifest generation

## Contents

### `.ledger/` (152 items)
Legacy manifest ledger system - replaced by MATRIZ module compliance schema v1.1.0

### `review_queue.json` (1.2MB)
Legacy review queue - replaced by new manifest generation pipeline

## Context

These artifacts were archived during the MATRIZ prep rollout to ensure clean state before generating 780 module manifests with the new schema v1.1.0 (🔮 Oracle constellation, Flow star, colony field, events/security blocks).

**Related commits:**
- `359ac64f6` - Initial MATRIZ discipline pack (31 files)
- `6efc20ef0` - Pre-flight patches (canon sync, CI workflow)

**Next steps:** Generate 780 manifests from normalized inventory after 20-module sample validation.

## Restoration

If needed, restore with:
```bash
cp -r .archive/20251011_223858_pre_matriz_rollout/.ledger manifests/
cp .archive/20251011_223858_pre_matriz_rollout/review_queue.json manifests/
```

## See Also

- `/Users/agi_dev/LOCAL-REPOS/Lukhas/docs/gonzo/matriz_prep/` - MATRIZ preparation documentation
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/schemas/matriz_module_compliance.schema.json` - v1.1.0 schema
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/scripts/star_canon.json` - Constellation Framework canonical stars
