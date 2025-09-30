# Module Sitemap (Draft v3)

## Purpose
Explain that this sitemap is the authoritative, human-readable index of all Lukhas modules after consolidation. It helps ensure discoverability, metadata consistency, and MATRIZ readiness.

## Global Rules
- Each module lives at `Lukhas/<module>/`
- Each module must contain:
  - `module.json` (renamed from directory_index.json)
  - `schema/` (with `module_schema.json` describing config + contracts)
  - `docs/` (markdown docs, design notes, READMEs)
  - `tests/` (unit + MATRIZ validation tests)
  - `config/` (OPA policies, YAML configs, metadata)
  - `__init__.py` or equivalent entrypoints
- Metadata in `module.json` must include:
  - name, description, version
  - lane assignment (L0–L5)
  - MATRIZ contract reference
  - owner/maintainer
  - tags (identity, core, orchestration, etc.)

## Example Structure
```
Lukhas/core/
  module.json
  schema/module_schema.json
  docs/README.md
  tests/test_core_contracts.py
  config/policy.rego
  __init__.py
```

## Upgrade Notes
- All existing `directory_index.json` files must be renamed to `module.json`
- Populate new fields (`lane`, `matriz_contract`, `tags`)
- `module_schema.json` will be colocated inside each module’s `schema/` dir
- Missing docs/tests/config dirs should be stubbed with placeholder files
- Promotion conveyor ensures files are moved and validated incrementally

## Next Steps
- Run `tools/module_sitemap_sync.py` (to be created) to check compliance
- Add validation hook in `make validate-matrix-all`
- Update artifacts/module_inventory.json automatically on sync