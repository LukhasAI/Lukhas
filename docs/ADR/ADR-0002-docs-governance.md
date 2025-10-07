---
status: stable
type: adr
owner: docs-team
module: docs
redirect: false
moved_to: null
---

![Status: Stable](https://img.shields.io/badge/status-stable-green)
![Owner: docs-team](https://img.shields.io/badge/owner-docs-team-lightblue)

# ADR-0002: Documentation Governance Framework

**Date**: 2025-10-06
**Status**: Accepted
**Context**: LUKHAS AI documentation system governance

## Problem

The LUKHAS documentation ecosystem had grown to 1233+ documents across 60+ subdirectories without a unified governance framework. This led to:

- **Orphaned documentation**: Files not referenced by any index
- **Duplicate content**: 32 exact duplicates, 46+ near-duplicates
- **Inconsistent metadata**: 87% of docs missing standardized front-matter
- **Broken links**: Numerous internal links pointing to moved/renamed files
- **No CI validation**: Documentation quality not enforced in PR reviews
- **Stale generated content**: Site maps and indices manually maintained

## Decision

Implement a **T4-level documentation governance framework** with:

### 1. Standardized Front-Matter

All `.md` files must include YAML front-matter:

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

### 2. Taxonomy Structure

Documents organized into canonical paths:

```
docs/
├── reference/          # Cross-references, indices
├── architecture/       # System design, components
├── guides/             # How-tos, tutorials
├── api/                # API contracts, schemas
├── reports/            # Audits, status snapshots
├── adr/                # Architecture Decision Records
├── archive/            # Deprecated/duplicate content
├── _generated/         # Machine-generated (read-only)
└── _inventory/         # Machine-readable manifests
```

### 3. Redirect Stub Pattern

When moving/consolidating files, replace with redirect stub:

```markdown
---
redirect: true
moved_to: <relative/new/path.md>
type: documentation
---

This file was moved. Please follow the redirect above.
```

### 4. Automation Scripts

Four core Python scripts in `scripts/`:

- **`docs_inventory.py`**: Scan all docs, generate `docs/_inventory/docs_manifest.json`
- **`docs_dedupe.py`**: Detect duplicates, generate `docs/_generated/REDIRECTS.md`
- **`docs_generate.py`**: Rebuild `SITE_MAP.md` and refresh canonical indices
- **`docs_lint.py`**: CI-ready validation (front-matter, links, freshness)

### 5. CI Guardrails

GitHub Actions workflow (`.github/workflows/docs-lint.yml`):

```yaml
- Validates front-matter on all docs
- Checks generated files are fresh
- Detects broken internal links
- Blocks merge if critical checks fail
```

Makefile integration:

```bash
make docs-lint  # Run full linter
```

### 6. Deduplication Policy

**Exact Duplicates**:
- Canonical selection: prefer taxonomy path > index reference > front-matter richness > newest
- Non-canonical files → redirect stub or archive

**Near-Duplicates** (≥70% title similarity):
- Archive non-canonical with note referencing canonical alternative

### 7. Link Rewriting

`docs_rewrite_links.py` updates internal links:
- Follows redirect map from dedupe plan
- Validates anchors exist in target documents
- Reports broken links for manual review

## Consequences

### Positive

- **Zero orphan docs**: All files reachable from `docs/INDEX.md` or `docs/reference/DOCUMENTATION_INDEX.md`
- **Automated consistency**: CI enforces front-matter and link integrity
- **Developer ergonomics**: Stable paths, clear taxonomy, fast navigation
- **Single source of truth**: `docs_manifest.json` as canonical inventory
- **Audit trail**: Redirect table tracks all moves/consolidations

### Negative

- **Initial migration burden**: 1067 docs need front-matter added (automated via script)
- **CI overhead**: ~30s added to PR checks
- **Learning curve**: Contributors must follow front-matter standard

### Neutral

- **Read-only generated files**: Developers cannot manually edit `_generated/` or `_inventory/`
- **Redirect stubs**: Adds clutter but preserves external link stability

## Implementation

### Phase 1: Inventory (Completed)
- ✅ Created `docs_inventory.py`
- ✅ Generated `docs/_inventory/docs_manifest.json`
- ✅ Metrics: 1233 docs, 32 exact dupes, 13 with full front-matter

### Phase 2: Deduplication (Completed)
- ✅ Created `docs_dedupe.py`
- ✅ Generated `docs/_generated/REDIRECTS.md`
- ✅ Identified 50 redirects, 57 archive candidates

### Phase 3: Generation (Completed)
- ✅ Created `docs_generate.py`
- ✅ Generated `docs/_generated/SITE_MAP.md`
- ✅ Updated `docs/reference/DOCUMENTATION_INDEX.md` and `docs/INDEX.md`

### Phase 4: Link Rewriting (Completed)
- ✅ Created `docs_rewrite_links.py` with dry-run validation
- ⚠️ Apply mode requires manual review and approval

### Phase 5: CI Integration (Completed)
- ✅ Created `docs_lint.py`
- ✅ Updated `Makefile` target `docs-lint`
- ✅ Created `.github/workflows/docs-lint.yml`

### Phase 6: Governance (This Document)
- ✅ ADR-0002 captures framework and policies

### Phase 7: Rollout (Pending)
- 🔲 Run front-matter normalization on all 1067 docs
- 🔲 Apply dedupe plan (move to archive, create redirect stubs)
- 🔲 Apply link rewrites
- 🔲 Enable CI enforcement (merge blocking)

## Maintenance

### Daily
- CI runs on every PR touching `docs/**`

### Weekly
- Review broken link report from `docs_rewrite_links.py`

### Monthly
- Re-run `docs_dedupe.py` to catch new duplicates
- Audit archive for candidates to delete permanently

### Quarterly
- Review taxonomy effectiveness
- Update front-matter schema if needed

## Rollback Plan

If governance proves too restrictive:

1. Disable CI enforcement (remove merge blocking)
2. Revert to advisory-only linting
3. Keep automation scripts for optional use

Front-matter and redirect stubs remain backward-compatible.

## References

- [T4 Commit Standards](../T4_INFRASTRUCTURE_SUMMARY.md)
- [Documentation Index](../reference/DOCUMENTATION_INDEX.md)
- [Site Map](../_generated/SITE_MAP.md)
- [Redirects Table](../_generated/REDIRECTS.md)

## Alternatives Considered

### 1. Manual Governance (Rejected)
- **Pros**: No tooling overhead
- **Cons**: Unsustainable at 1233+ docs, human error prone

### 2. Full MkDocs Migration (Rejected)
- **Pros**: Rich tooling, built-in search
- **Cons**: Major migration cost, overkill for internal docs

### 3. Wiki/Notion External Tool (Rejected)
- **Pros**: User-friendly UI
- **Cons**: Loss of version control, docs separated from code

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Docs Lead | @agi_dev | 2025-10-06 | Approved |
| Tech Lead | TBD | TBD | Pending |

---

**Next Steps**:
1. Socialize this ADR with the team
2. Run Phase 7 rollout scripts
3. Enable CI merge blocking after 1-week grace period
