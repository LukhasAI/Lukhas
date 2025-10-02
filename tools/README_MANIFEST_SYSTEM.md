# LUKHAS Manifest System Tools

Production-grade Python tools for validating, hydrating, indexing, and diffing LUKHAS module manifests.

## Overview

The manifest system provides a living, self-enforcing registry for all LUKHAS modules. It consists of 4 core tools that work together to ensure manifest quality and track changes over time.

## Tools

### 1. manifest_validate.py
**Purpose:** Validate manifest files against the JSON schema

**Features:**
- Validates against `schemas/module.manifest.schema.json` using Draft202012Validator
- Performs semantic checks (module name matches directory, paths exist, etc.)
- Skips `.venv/` and `artifacts/` directories
- Exits with code 1 if any validation fails

**Usage:**
```bash
# Validate a single manifest
python3 tools/manifest_validate.py path/to/module.manifest.json

# Validate all manifests in repository
python3 tools/manifest_validate.py --all

# Validate all manifests in a specific directory
python3 tools/manifest_validate.py path/to/directory --all
```

**Output:**
- ✅ for valid files
- ❌ for invalid files with detailed error messages
- Summary with pass/fail counts

### 2. manifest_lock_hydrator.py
**Purpose:** Generate lockfiles with resolved paths and content hashes

**Features:**
- Generates `module.manifest.lock.json` for each manifest
- Computes SHA256 hashes of manifest + all `.py/.json/.yaml` files
- Includes git commit SHA and timestamp
- Normalizes entrypoints, lanes, status, owner, SLOs
- Idempotent: sorted keys, deterministic output
- Skips `.venv/` and `artifacts/` directories

**Usage:**
```bash
# Generate lockfile for a specific module
python3 tools/manifest_lock_hydrator.py path/to/module/

# Generate lockfiles for all manifests
python3 tools/manifest_lock_hydrator.py --all

# Dry run (show what would be generated)
python3 tools/manifest_lock_hydrator.py --all --dry-run
```

**Output:**
- Lockfile path: `module.manifest.lock.json` (next to manifest)
- Hash count and success/failure status

**Lockfile Structure:**
```json
{
  "module": "core",
  "module_path": "lukhas/core",
  "schema_version": "1.0.0",
  "status": "stable",
  "owner": {
    "team": "Core",
    "codeowners": ["@lukhas-core"]
  },
  "runtime": {
    "language": "python",
    "entrypoints": ["main.py"]
  },
  "matrix": {
    "lane": "L2",
    "gates_profile": "standard"
  },
  "slos": {
    "availability": 99.9,
    "latency_p95_ms": 100,
    "latency_p99_ms": 250
  },
  "hashes": {
    "module.manifest.json": "abc123...",
    "__init__.py": "def456...",
    "main.py": "ghi789..."
  },
  "git_commit": "abc123...",
  "generated_at": "2025-10-02T15:00:00Z"
}
```

### 3. manifest_indexer.py
**Purpose:** Generate a unified registry from all lockfiles

**Features:**
- Reads all `module.manifest.lock.json` files
- Generates `artifacts/module.registry.json` with all modules
- Detects duplicate module names
- Writes `artifacts/registry_errors.json` if duplicates found
- Exits with code 1 on duplicates or load errors
- Creates `artifacts/` directory if needed

**Usage:**
```bash
# Generate registry from all lockfiles
python3 tools/manifest_indexer.py

# Dry run (show what would be generated)
python3 tools/manifest_indexer.py --dry-run

# Custom output path
python3 tools/manifest_indexer.py --output path/to/registry.json
```

**Output:**
- Registry: `artifacts/module.registry.json`
- Error details: `artifacts/registry_errors.json` (if duplicates)

**Registry Structure:**
```json
{
  "version": "1.0.0",
  "generated_at": "2025-10-02T15:00:00Z",
  "total_modules": 42,
  "modules": [
    {
      "_source_lockfile": "lukhas/core/module.manifest.lock.json",
      "module": "core",
      "module_path": "lukhas/core",
      "hashes": {...},
      ...
    }
  ]
}
```

### 4. registry_diff.py
**Purpose:** Compare registries to detect breaking changes

**Features:**
- Compares current registry vs baseline
- Detects modules added, modified, or removed
- Enforces deprecation/alias workflow for removals
- Exits with code 1 on unplanned removals
- Supports bypass via flag or environment variable

**Usage:**
```bash
# Create baseline from current registry
python3 tools/registry_diff.py --create-baseline

# Compare current vs baseline
python3 tools/registry_diff.py

# Allow removals (bypass enforcement)
python3 tools/registry_diff.py --allow-removals

# Or set environment variable
LUKHAS_ALLOW_MODULE_REMOVALS=1 python3 tools/registry_diff.py

# Custom paths
python3 tools/registry_diff.py --baseline path/to/baseline.json --current path/to/current.json
```

**Output:**
- Added modules (✨)
- Modified modules (🔄)
- Removed modules (🗑️)
  - ✅ if has deprecation/alias entry
  - ❌ if missing proper workflow

**Violation Handling:**
If a module is removed without deprecation/alias:
1. Exit code 1
2. Clear error message with fix instructions
3. Can bypass with `--allow-removals` or env var (not recommended)

## Workflow Integration

### CI/CD Pipeline
```yaml
# .github/workflows/manifest-validation.yml
- name: Validate Manifests
  run: python3 tools/manifest_validate.py --all

- name: Generate Lockfiles
  run: python3 tools/manifest_lock_hydrator.py --all

- name: Generate Registry
  run: python3 tools/manifest_indexer.py

- name: Check Registry Diff
  run: python3 tools/registry_diff.py
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Only run if manifest changed
if git diff --cached --name-only | grep -q "module.manifest.json"; then
    python3 tools/manifest_validate.py --all || exit 1
fi
```

### Local Development
```bash
# 1. Edit manifest
vim lukhas/core/module.manifest.json

# 2. Validate
python3 tools/manifest_validate.py lukhas/core/module.manifest.json

# 3. Generate lockfile
python3 tools/manifest_lock_hydrator.py lukhas/core/

# 4. Regenerate registry
python3 tools/manifest_indexer.py

# 5. Check for breaking changes
python3 tools/registry_diff.py
```

## Error Codes

All tools use consistent exit codes:
- **0**: Success
- **1**: Validation/enforcement failure
- **2**: Missing dependencies or configuration

## Requirements

- Python 3.11+
- `jsonschema` package (for validation only)
- Git (for commit SHA extraction)

## File Locations

```
tools/
├── manifest_validate.py      # Step 1: Validate manifests
├── manifest_lock_hydrator.py  # Step 2: Generate lockfiles
├── manifest_indexer.py        # Step 3: Generate registry
└── registry_diff.py           # Step 4: Detect changes

artifacts/
├── module.registry.json          # Current registry
├── module.registry.json.baseline # Baseline for comparison
└── registry_errors.json          # Duplicate/error details

**/
└── module.manifest.lock.json  # Generated next to each manifest
```

## Design Principles

1. **Idempotent**: Running twice produces identical results
2. **Deterministic**: Sorted keys, stable hashing
3. **Fast**: Minimal I/O, efficient algorithms
4. **Clear errors**: Actionable messages with file paths
5. **Zero config**: Works out of the box with sensible defaults

## Troubleshooting

### Validation Errors
```bash
# Check schema compliance
python3 tools/manifest_validate.py path/to/manifest.json

# Common issues:
# - Module name doesn't match directory
# - Layout paths don't exist
# - Missing required fields
```

### Duplicate Modules
```bash
# Check for duplicates
python3 tools/manifest_indexer.py

# If duplicates found, check:
cat artifacts/registry_errors.json
```

### Registry Diff Failures
```bash
# Check what changed
python3 tools/registry_diff.py

# If module removed, either:
# 1. Add deprecation entry to replacement module
# 2. Add alias entry if renamed
# 3. Use --allow-removals (not recommended)
```

## Future Enhancements

- [ ] Parallel lockfile generation for large repos
- [ ] Incremental registry updates (only changed modules)
- [ ] JSON Schema draft version detection
- [ ] Manifest migration tools (schema upgrades)
- [ ] Integration with LUKHAS governance system
- [ ] Web UI for registry exploration
- [ ] Prometheus metrics export

## License

Part of the LUKHAS AI project. Internal use only.
