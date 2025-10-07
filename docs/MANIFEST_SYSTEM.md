---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

# LUKHAS Module Manifest System

## Overview

The manifest system transforms scattered JSON files into a living, self-enforcing registry with provenance, drift detection, and executable contracts.

## Architecture

### Components

1. **Manifests** (`module.manifest.json`) - Human-authored intent
2. **Lockfiles** (`module.manifest.lock.json`) - Generated provenance with hashes
3. **Registry** (`artifacts/module.registry.json`) - Single source of truth
4. **Conformance Tests** - Executable contracts verifying entrypoints work

### Data Flow

```
module.manifest.json (authored)
  ↓ [validate]
  ↓ [hydrate_lock]
module.manifest.lock.json (generated)
  ↓ [index]
artifacts/module.registry.json (canonical)
  ↓ [diff] → fail on unplanned changes
  ↓ [generate_conformance]
tests/conformance/test_contracts.py (generated)
  ↓ [pytest]
✅ or ❌
```

## Tools

### tools/manifest_validate.py
Validates all manifests against JSON schema.

**Usage:** `make manifests-validate` or `python3 tools/manifest_validate.py`

### tools/manifest_lock_hydrator.py
Generates deterministic lockfiles with hashes and metadata.

**Usage:** `make manifest-lock` or `python3 tools/manifest_lock_hydrator.py`

### tools/manifest_indexer.py
Builds single registry from all lockfiles.

**Usage:** `make manifest-index` or `python3 tools/manifest_indexer.py`

### tools/registry_diff.py
Detects silent module removals/renames.

**Usage:** `make manifest-diff` or `python3 tools/registry_diff.py`

### tools/generate_conformance_tests.py
Creates pytest tests from registry.

**Usage:** `make conformance-generate` or `python3 tools/generate_conformance_tests.py`

## Workflows

### Adding a New Module

1. Create `module.manifest.json` in module root
2. Run `make manifests-validate` - ensure valid
3. Run `make manifest-lock` - generate lockfile
4. Run `make manifest-index` - update registry
5. Commit manifest + lockfile (registry is generated in CI)

### Renaming a Module

1. Add `deprecations` entry to old module manifest:
   ```json
   "deprecations": [{
     "old_name": "lukhas.old.module",
     "until": "2026-03-31",
     "replace_with": "lukhas.new.module",
     "migration_guide": "docs/migrations/old-to-new.md"
   }]
   ```
2. Create new module manifest
3. Run manifest system pipeline
4. Update imports gradually
5. Remove old module after deprecation period

### Using Aliases

1. Add `aliases` array to module manifest:
   ```json
   "aliases": ["lukhas.legacy.name", "old.module.path"]
   ```
2. Run manifest system pipeline
3. Import resolution will work with any alias
4. Eventually consolidate to canonical name

## Anti-Patterns

❌ **Don't** edit lockfiles manually (they're generated)
❌ **Don't** edit conformance tests (they're generated)
❌ **Don't** remove modules without deprecation period
❌ **Don't** skip manifest validation

✅ **Do** edit manifests directly
✅ **Do** regenerate lockfiles after manifest changes
✅ **Do** add deprecation notices before removal
✅ **Do** run full pipeline before committing

## Troubleshooting

**"Duplicate module names"**
- Check `artifacts/registry_errors.json`
- Rename one module or add alias

**"Conformance test failing"**
- Entrypoint declared but doesn't exist
- Fix code or update manifest

**"Registry diff failed"**
- Module removed without deprecation
- Add deprecation entry or use `allow:module-removal` label

## Future Enhancements

- Real signing (replace checksums with GPG/cosign)
- OpenTelemetry span verification in conformance tests
- SLO runtime validation
- Automatic docs catalog generation
