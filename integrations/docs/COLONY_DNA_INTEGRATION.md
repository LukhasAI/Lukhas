---
module: integrations
title: Colony ↔ DNA Helix Integration (Test Harness)
---

# Colony ↔ DNA Helix Integration (Test Harness)

- Goal: Prove consensus decisions persist correctly to DNA memory with strength,
  versioning, and privacy options.
- Adapter: `persist_consensus_to_dna()` maps decisions → DNA writes.
- Versioning: Higher `version` wins; older writes do not overwrite.
- Strength: Function of quorum and confidence (clamped to safe bounds).
- Privacy: `FLAG_DNA_ENCRYPT_PERSONAL` masks `_personal` payloads.

## Run

```bash
pytest -q tests/test_colony_dna_integration.py
make colony-dna-smoke
```

## Flags

- `FLAG_DNA_ENCRYPT_PERSONAL` (default false)
  - When true, consensus values marked with `{"_personal": true}` are stored as
    encrypted placeholders: `{"_enc": true, "blob": "[ENCRYPTED]"}`.
- `FLAG_DNA_DUAL_WRITE` (caller-side)
  - Use during migration to write both legacy and DNA stores.
