---
status: stable
type: runbook
owner: unknown
module: docs.collaboration.runbooks
redirect: false
moved_to: null
---

![Status: Stable](https://img.shields.io/badge/status-stable-green)

# Documentation Migration Runbook

**Purpose**: Procedures for migrating documentation from scattered locations to standardized module `docs/` directories with validated frontmatter.

**Audience**: Documentation Teams, Migration Agents, DevOps

**SLA**: Single module migration: <10 min | Bulk migration (100 modules): <2 hours

---

## 1. Normal Operations

### 1.1 Pre-migration Validation

**When**: Before starting any migration

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Validate doc frontmatter schema
python3 scripts/ci/doc_frontmatter_guard.py --validate-schema

# Check current documentation state
python3 scripts/docs/doc_audit.py --output artifacts/doc_audit.json
```

**Expected Output**:
```
✅ Frontmatter schema valid
📊 Documentation Audit:
  - Total docs: 678
  - With valid frontmatter: 342 (50.4%)
  - Missing frontmatter: 336 (49.6%)
  - Invalid frontmatter: 0
```

### 1.2 Single Module Migration

**When**: Migrating documentation for one module

```bash
# Migrate specific module
python3 scripts/docs/migrate_module_docs.py \
  --module consciousness \
  --target lukhas/consciousness/docs \
  --validate

# Expected output
✅ consciousness documentation migrated
📁 Files moved: 12
  - README.md → lukhas/consciousness/docs/README.md
  - architecture.md → lukhas/consciousness/docs/architecture.md
  - api.md → lukhas/consciousness/docs/api.md
  ...
📝 Frontmatter added/validated: 12/12
🔗 Updated links: 34 references
```

**Validation**:
```bash
# Verify frontmatter compliance
python3 scripts/ci/doc_frontmatter_guard.py \
  --path lukhas/consciousness/docs \
  --strict

# Expected output
✅ All 12 docs have valid frontmatter
```

### 1.3 Bulk Migration

**When**: Migrating all documentation across multiple modules

```bash
# Generate migration plan
python3 scripts/docs/plan_bulk_migration.py \
  --output artifacts/doc_migration_plan.json

# Review plan
cat artifacts/doc_migration_plan.json | jq '.summary'

# Execute migration
python3 scripts/docs/execute_migration.py \
  --plan artifacts/doc_migration_plan.json \
  --batch-size 10 \
  --validate
```

**Expected Output**:
```
📊 Migration Plan Summary:
  - Modules to migrate: 148
  - Total docs: 678
  - Estimated duration: 1h 45m

🚀 Executing migration...
✅ Batch 1/15 complete (10 modules, 67 docs)
✅ Batch 2/15 complete (10 modules, 54 docs)
...
✅ Migration complete: 678/678 docs migrated
⏱️  Duration: 1h 32m
```

---

## 2. Documentation Standards

### 2.1 Frontmatter Schema Contract

**Required Fields** (from `schemas/doc.frontmatter.schema.json`):
- `module`: Module name (pattern: `^[a-zA-Z_][\w.]+$`)
- `type`: One of: `api`, `architecture`, `examples`, `runbook`, `guide`, `reference`, `tutorial`
- `title`: Document title (3-120 chars)
- `status`: One of: `draft`, `wip`, `stable`, `deprecated`

**Optional Fields**:
- `tags`: Array of tags
- `lane`: Lane designation (`L0`, `L1`, `L2`, `L3`)
- `authors`: List of authors
- `last_updated`: ISO 8601 timestamp
- `related_docs`: List of related document paths

**Example**:
```yaml
---
module: lukhas.consciousness
type: architecture
title: Consciousness Layer Architecture
status: stable
tags: [consciousness, architecture, core]
lane: L2
authors: [DevTeam]
last_updated: 2025-10-05T12:00:00Z
related_docs:
  - lukhas/consciousness/docs/api.md
  - lukhas/memory/docs/integration.md
---
```

### 2.2 Directory Structure

**Standard Layout**:
```
lukhas/<module>/docs/
├── README.md           # Module overview (required)
├── architecture.md     # Architecture details (recommended)
├── api.md             # API reference (if module has API)
├── examples/          # Code examples
│   ├── basic.md
│   └── advanced.md
└── runbooks/          # Operational runbooks
    ├── deployment.md
    └── troubleshooting.md
```

### 2.3 Link Resolution

**Internal Links** (relative paths):
- Within module: `[API Reference](api.md)`
- Cross-module: `[Memory Integration](../../memory/docs/integration.md)`
- Root docs: `[Architecture Guide](/docs/architecture/overview.md)`

**External Links** (absolute URLs):
- GitHub: `[Source](https://github.com/LukhasAI/Lukhas)`
- External docs: `[Python Docs](https://docs.python.org/3/)`

---

## 3. Migration Procedures

### 3.1 Discover Documentation

**Find all docs for a module**:
```bash
# Search by module name
python3 scripts/docs/find_module_docs.py \
  --module consciousness \
  --output artifacts/consciousness_docs.json

# Expected output
{
  "module": "consciousness",
  "found_docs": [
    {
      "path": "docs/architecture/consciousness.md",
      "type": "architecture",
      "status": "orphaned"  # Not in module docs/
    },
    {
      "path": "lukhas/consciousness/README.md",
      "type": "api",
      "status": "in_module"  # Already in module
    },
    ...
  ],
  "total": 12,
  "orphaned": 8,
  "in_module": 4
}
```

### 3.2 Migrate Single Document

**Procedure**:
```bash
# Migrate single doc with frontmatter injection
python3 scripts/docs/migrate_doc.py \
  --source docs/architecture/consciousness.md \
  --target lukhas/consciousness/docs/architecture.md \
  --module consciousness \
  --type architecture \
  --status stable \
  --add-frontmatter \
  --update-links

# Verify frontmatter
head -15 lukhas/consciousness/docs/architecture.md
```

**Expected Output**:
```yaml
---
module: lukhas.consciousness
type: architecture
title: Consciousness Layer Architecture
status: stable
migrated_from: docs/architecture/consciousness.md
migrated_at: 2025-10-05T12:34:56Z
---

# Consciousness Layer Architecture
...
```

### 3.3 Update Cross-references

**After migration, update links**:
```bash
# Find broken links
python3 scripts/docs/check_links.py \
  --path lukhas/consciousness/docs \
  --output artifacts/broken_links.json

# Auto-fix relative links
python3 scripts/docs/fix_links.py \
  --broken-links artifacts/broken_links.json \
  --auto-fix

# Verify
python3 scripts/docs/check_links.py --path lukhas/consciousness/docs
# Expected: ✅ All links valid
```

### 3.4 Update Module Registry

**After migration**:
```bash
# Regenerate registry to reflect new doc locations
make registry

# Verify docs listed
jq '.modules[] | select(.name == "consciousness") | .docs' \
  docs/_generated/MODULE_REGISTRY.json
```

---

## 4. Troubleshooting

### 4.1 Invalid Frontmatter

**Symptom**: Frontmatter validation fails

**Diagnosis**:
```bash
python3 scripts/ci/doc_frontmatter_guard.py \
  --path lukhas/consciousness/docs/architecture.md \
  --verbose
```

**Output Example**:
```
❌ lukhas/consciousness/docs/architecture.md:
  - Missing required field: 'status'
  - Invalid type: 'tutorial' (expected one of: api, architecture, ...)
  - Invalid module: 'consciousness' (expected pattern: ^[a-zA-Z_][\w.]+$)
```

**Fix**:
```bash
# Fix frontmatter manually
vim lukhas/consciousness/docs/architecture.md

# Or use auto-fix utility
python3 scripts/docs/fix_frontmatter.py \
  --path lukhas/consciousness/docs/architecture.md \
  --module lukhas.consciousness \
  --type architecture \
  --status stable
```

### 4.2 Duplicate Documentation

**Symptom**: Same content in multiple locations

**Diagnosis**:
```bash
# Find duplicates by content hash
python3 scripts/docs/find_duplicates.py \
  --output artifacts/duplicate_docs.json

# Expected output
{
  "duplicates": [
    {
      "hash": "abc123...",
      "files": [
        "docs/architecture/consciousness.md",
        "lukhas/consciousness/docs/architecture.md"
      ],
      "similarity": 0.98
    }
  ]
}
```

**Fix**:
```bash
# Keep module version, archive old version
mv docs/architecture/consciousness.md \
   docs/archive/consciousness_$(date +%Y%m%d).md

# Update any references
python3 scripts/docs/update_references.py \
  --old docs/architecture/consciousness.md \
  --new lukhas/consciousness/docs/architecture.md
```

### 4.3 Broken Links After Migration

**Symptom**: Links pointing to old locations

**Diagnosis**:
```bash
# Check all links
python3 scripts/docs/check_links.py --all
```

**Output Example**:
```
❌ 34 broken links found:
  - lukhas/identity/docs/README.md:42 → ../../../docs/architecture/consciousness.md (404)
  - lukhas/memory/docs/integration.md:18 → ../../consciousness/README.md (404)
  ...
```

**Fix** (Auto-update):
```bash
# Map old paths to new paths
cat > artifacts/link_map.json <<EOF
{
  "docs/architecture/consciousness.md": "lukhas/consciousness/docs/architecture.md",
  "lukhas/consciousness/README.md": "lukhas/consciousness/docs/README.md"
}
EOF

# Update all references
python3 scripts/docs/bulk_update_links.py \
  --link-map artifacts/link_map.json \
  --verify
```

### 4.4 Conflicting Frontmatter

**Symptom**: Existing frontmatter conflicts with migration

**Diagnosis**:
```bash
# Check existing frontmatter
python3 scripts/docs/extract_frontmatter.py \
  --path lukhas/consciousness/docs/architecture.md
```

**Output Example**:
```yaml
# Existing frontmatter
---
title: Old Title
author: Unknown
date: 2024-01-01
---
```

**Fix** (Merge):
```bash
# Merge existing with required schema
python3 scripts/docs/merge_frontmatter.py \
  --path lukhas/consciousness/docs/architecture.md \
  --module lukhas.consciousness \
  --type architecture \
  --status stable \
  --preserve-fields title,author,date

# Result
---
module: lukhas.consciousness
type: architecture
title: Old Title  # Preserved
status: stable
author: Unknown  # Preserved
date: 2024-01-01  # Preserved
migrated_at: 2025-10-05T12:34:56Z
---
```

---

## 5. Incident Response

### 5.1 Accidental Deletion

**Scenario**: Documentation deleted during migration

**Procedure**:
```bash
# Step 1: Check git history
git log --all --full-history -- "**/*.md" | head -50

# Step 2: Restore from git
git checkout HEAD~1 -- lukhas/consciousness/docs/architecture.md

# Step 3: Verify restoration
ls -la lukhas/consciousness/docs/architecture.md

# Step 4: Re-apply frontmatter if needed
python3 scripts/docs/fix_frontmatter.py \
  --path lukhas/consciousness/docs/architecture.md \
  --module lukhas.consciousness \
  --type architecture
```

**Expected Duration**: <2 minutes

### 5.2 Mass Link Breakage

**Scenario**: Bulk migration broke links across codebase

**Procedure**:
```bash
# Step 1: Revert migration
git revert HEAD

# Step 2: Generate comprehensive link map
python3 scripts/docs/build_link_map.py \
  --plan artifacts/doc_migration_plan.json \
  --output artifacts/comprehensive_link_map.json

# Step 3: Re-run migration with link map
python3 scripts/docs/execute_migration.py \
  --plan artifacts/doc_migration_plan.json \
  --link-map artifacts/comprehensive_link_map.json \
  --verify-links

# Step 4: Verify no broken links
python3 scripts/docs/check_links.py --all
```

### 5.3 Schema Change Mid-migration

**Scenario**: Frontmatter schema updated during migration

**Procedure**:
```bash
# Step 1: Identify docs with old schema
python3 scripts/docs/find_schema_mismatches.py \
  --output artifacts/schema_mismatches.json

# Step 2: Update to new schema
python3 scripts/docs/update_to_new_schema.py \
  --mismatches artifacts/schema_mismatches.json \
  --new-schema schemas/doc.frontmatter.schema.json

# Step 3: Validate
python3 scripts/ci/doc_frontmatter_guard.py --all
```

---

## 6. Automation Integration

### 6.1 CI Pipeline Integration

**GitHub Actions** (.github/workflows/doc-migration.yml):
```yaml
name: Documentation Migration
on:
  workflow_dispatch:
    inputs:
      module:
        description: 'Module to migrate (or "all")'
        required: true
        default: 'all'

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate frontmatter schema
        run: |
          python3 scripts/ci/doc_frontmatter_guard.py --validate-schema

      - name: Migrate docs
        run: |
          if [ "${{ github.event.inputs.module }}" = "all" ]; then
            python3 scripts/docs/execute_migration.py \
              --plan artifacts/doc_migration_plan.json
          else
            python3 scripts/docs/migrate_module_docs.py \
              --module "${{ github.event.inputs.module }}"
          fi

      - name: Validate migration
        run: |
          python3 scripts/ci/doc_frontmatter_guard.py --all
          python3 scripts/docs/check_links.py --all

      - name: Update registry
        run: make registry

      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "docs: migrate ${{ github.event.inputs.module }} documentation"
          git push
```

### 6.2 Pre-migration Hook

**Script** (scripts/hooks/pre-migrate-docs.sh):
```bash
#!/bin/bash
set -e

echo "🔍 Pre-migration validation..."

# Validate schema
python3 scripts/ci/doc_frontmatter_guard.py --validate-schema

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
  echo "❌ Uncommitted changes detected. Commit or stash first."
  exit 1
fi

# Generate migration plan
python3 scripts/docs/plan_bulk_migration.py \
  --output artifacts/doc_migration_plan.json

# Review plan
echo "📊 Migration Plan:"
cat artifacts/doc_migration_plan.json | jq '.summary'

echo "✅ Pre-migration validation passed"
```

---

## 7. Monitoring and Metrics

### 7.1 Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Docs with valid frontmatter | 100% | <95% |
| Broken links | 0 | >10 |
| Orphaned docs (outside modules) | <5% | >15% |
| Migration duration (100 modules) | <2 hours | >4 hours |
| Schema compliance | 100% | <98% |

### 7.2 Dashboard

**Generate migration dashboard**:
```bash
python3 scripts/docs/doc_migration_dashboard.py \
  --output docs/_generated/DOC_MIGRATION_DASHBOARD.md
```

**Example Output**:
```markdown
# Documentation Migration Dashboard

## Overall Progress
- ✅ Migrated: 678/678 (100%)
- ✅ Valid frontmatter: 678/678 (100%)
- ✅ Broken links: 0
- ✅ Orphaned docs: 0

## By Module
| Module | Docs | Migrated | Valid FM | Broken Links |
|--------|------|----------|----------|--------------|
| consciousness | 12 | ✅ 12 | ✅ 12 | 0 |
| identity | 8 | ✅ 8 | ✅ 8 | 0 |
...
```

---

## 8. Best Practices

### 8.1 Migration Checklist

**Before Migration**:
- [ ] Validate frontmatter schema
- [ ] Generate migration plan
- [ ] Review plan for conflicts
- [ ] Backup current documentation state (git commit)

**During Migration**:
- [ ] Migrate in small batches (10-20 modules)
- [ ] Validate each batch before proceeding
- [ ] Update links incrementally
- [ ] Monitor for errors

**After Migration**:
- [ ] Verify all frontmatter valid
- [ ] Check for broken links
- [ ] Update module registry
- [ ] Archive old documentation locations
- [ ] Document migration in changelog

### 8.2 Common Pitfalls

1. **Not updating cross-references**: Always run link checker after migration
2. **Skipping frontmatter validation**: Use strict validation before committing
3. **Large batch migrations without testing**: Test on 1-2 modules first
4. **Not archiving old locations**: Maintain history for reference
5. **Ignoring existing frontmatter**: Merge, don't replace

---

## 9. Contacts

**Primary**: Documentation Team
**Migration Agent**: @docs-migration-agent
**Escalation**: Platform Engineering
**Issue Tracker**: GitHub Issues with `docs-migration` label

---

## 10. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-05 | Initial runbook creation | Claude |

---

**Next Review**: 2025-11-05 (Monthly)
