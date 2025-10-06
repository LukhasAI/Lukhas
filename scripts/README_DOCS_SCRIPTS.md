# Documentation Automation Scripts

**Purpose**: T4-level documentation governance for LUKHAS AI's 1233+ document ecosystem.

---

## Quick Start

```bash
# 1. Build inventory
python3 scripts/docs_inventory.py

# 2. Detect duplicates
python3 scripts/docs_dedupe.py

# 3. Generate site map and indices
python3 scripts/docs_generate.py

# 4. Validate quality (CI-ready)
python3 scripts/docs_lint.py
make docs-lint
```

---

## Scripts

### `docs_inventory.py`
Scans all `.md` files, extracts metadata (title, status, type, owner, module), computes hashes for duplicate detection.

**Output**: `docs/_inventory/docs_manifest.json`

**Metrics**:
- Total documents
- Missing front-matter count
- Exact duplicate groups
- Breakdown by status/type/module

---

### `docs_dedupe.py`
Detects exact duplicates (SHA256) and near-duplicates (title similarity), selects canonicals, generates redirect plan.

**Output**:
- `docs/_inventory/dedupe_plan.json`
- `docs/_generated/REDIRECTS.md`

**Canonical Selection**:
1. Taxonomy path match
2. Referenced by index
3. Front-matter richness
4. Newest timestamp

---

### `docs_generate.py`
Generates hierarchical site map and refreshes auto-generated sections in canonical indices.

**Output**:
- `docs/_generated/SITE_MAP.md`
- Updates to `docs/reference/DOCUMENTATION_INDEX.md`
- Updates to `docs/INDEX.md`

**Features**:
- Status badges (🚧 WIP, ⚠️ Deprecated)
- Clickable relative links
- Non-destructive (preserves manual sections)

---

### `docs_rewrite_links.py`
Validates internal links, follows redirects, checks anchors, rewrites to canonical paths.

**Usage**:
```bash
python3 scripts/docs_rewrite_links.py           # Dry-run
python3 scripts/docs_rewrite_links.py --apply   # Apply rewrites
```

**Validation**:
- Relative path resolution
- Target existence check
- Anchor validation (`#heading`)
- Redirect map integration

---

### `docs_lint.py`
CI-ready linter for front-matter, manifest completeness, site map freshness, broken links.

**Exit Codes**:
- `0`: All critical checks passed
- `1`: Errors found (blocks CI)

**Checks**:
1. Front-matter required keys
2. All `.md` in manifest (orphan detection)
3. Generated files fresh
4. Internal link sample validation

---

## CI Integration

### Makefile
```bash
make docs-lint  # Runs docs_lint.py
```

### GitHub Actions
**Workflow**: `.github/workflows/docs-lint.yml`

**Triggers**:
- PRs touching `docs/**`
- Pushes to `main`

**Jobs**:
1. Run `docs_lint.py`
2. Check generated files freshness

---

## Front-Matter Standard

All `.md` files require:

```yaml
---
status: {wip|draft|stable|deprecated|archived}
type: {architecture|api|guide|report|adr|index|misc}
owner: {@handle|team|unknown}
module: {inferred-from-path}
redirect: false
moved_to: null
---
```

---

## Redirect Stub Pattern

When moving/consolidating files:

```markdown
---
redirect: true
moved_to: <relative/new/path.md>
type: documentation
---

This file was moved. Please follow the redirect above.
```

---

## Taxonomy

```
docs/
├── reference/          # Cross-references, indices
├── architecture/       # System design
├── guides/             # How-tos
├── api/                # API docs
├── reports/            # Audits, status
├── adr/                # Decision records
├── archive/            # Deprecated content
├── _generated/         # Machine-generated (read-only)
└── _inventory/         # Manifests (read-only)
```

---

## Workflow

### New Document
1. Create file in appropriate taxonomy path
2. Add front-matter block
3. Run `make docs-lint` to validate
4. Commit and create PR (CI will validate)

### Move/Rename Document
1. Move file to new location
2. Replace old path with redirect stub
3. Run `python3 scripts/docs_generate.py` to update indices
4. Run `make docs-lint` to validate
5. Commit and create PR

### Periodic Maintenance
```bash
# Monthly: Re-check for duplicates
python3 scripts/docs_dedupe.py

# Weekly: Check broken links
python3 scripts/docs_rewrite_links.py

# Daily: CI runs on every PR
```

---

## Dependencies

**Python 3.11+** (stdlib only, no external deps)

Required modules:
- `hashlib`, `json`, `os`, `re`, `subprocess`, `datetime`, `pathlib`, `typing`

---

## Performance

| Script | Runtime | Output Size |
|--------|---------|-------------|
| `docs_inventory.py` | ~15s | 250 KB |
| `docs_dedupe.py` | ~8s | 45 KB |
| `docs_generate.py` | ~3s | 80 KB |
| `docs_rewrite_links.py` | ~120s | N/A |
| `docs_lint.py` | ~12s | Exit code |

**Total CI overhead**: ~30s per PR

---

## Troubleshooting

### "Manifest not found"
Run `python3 scripts/docs_inventory.py` first.

### "Site map is stale"
Run `python3 scripts/docs_generate.py` to regenerate.

### "Front-matter errors"
Add missing keys (status, type, owner, module) to YAML block.

### "Broken links"
Run `python3 scripts/docs_rewrite_links.py` to see full report.

---

## References

- **Governance**: [docs/adr/ADR-0002-docs-governance.md](../docs/adr/ADR-0002-docs-governance.md)
- **Report**: [docs/reports/DOCS_GOVERNANCE_IMPLEMENTATION_REPORT.md](../docs/reports/DOCS_GOVERNANCE_IMPLEMENTATION_REPORT.md)
- **Site Map**: [docs/_generated/SITE_MAP.md](../docs/_generated/SITE_MAP.md)
- **Redirects**: [docs/_generated/REDIRECTS.md](../docs/_generated/REDIRECTS.md)

---

**Maintained by**: Docs Team (@agi_dev)
**Last Updated**: 2025-10-06
