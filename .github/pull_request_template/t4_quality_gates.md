---
status: wip
type: documentation
---
# Pull Request - T4/0.01% Quality Gates

## What Changed

- [ ] Manifests (`**/module.manifest.json`)
- [ ] Documentation (`**/docs/*.md`)
- [ ] Tests (`**/tests/*.py`)
- [ ] Vocabulary (`vocab/features.json`, `vocab/tags.json`)
- [ ] Schema (`schemas/*.json`)
- [ ] Scripts/Tools (`scripts/`, `tools/`)
- [ ] CI/Governance (`.github/`, `Makefile`)

## Evidence (T4/0.01% Quality Gates)

- [ ] `make quality` passes (schema, vocab, MQI, registry, SLO)
- [ ] Review queue reduced or unchanged (`manifests/review_queue.json`)
- [ ] No SLO violations introduced (L2/L3 modules)
- [ ] Registry matches filesystem (`scripts/ci/registry_vs_fs.py`)
- [ ] Ledger appended (if manifests modified)

## For Manifest Changes

- [ ] Full provenance tracking (`_provenance` field present)
- [ ] Controlled vocabulary only (no free-text features/tags)
- [ ] MQI ≥ 90 for L2 modules, ≥ 95 for L3 modules
- [ ] SLA targets defined for L2/L3 modules

## For Vocabulary Changes

- [ ] `--validate-only` passed before applying
- [ ] Canonical keys follow naming convention (`domain.feature`)
- [ ] Synonyms mapped correctly
- [ ] Notion options backfilled (if Notion sync enabled)

## For Documentation Changes

- [ ] Frontmatter schema valid (`schemas/doc.frontmatter.schema.json`)
- [ ] Module field matches manifest
- [ ] Status is `stable` (not `draft` or `wip`)

## For Schema Changes

- [ ] Feature flag added for new required fields (`schemas/flags.json`)
- [ ] Backward compatibility maintained (2 release deprecation policy)
- [ ] All existing manifests still validate

## Backout Plan

If this PR breaks production:

```bash
# Revert last manifest changes from ledger
make revert:last

# Regenerate registry and reports
make registry slo-report

# Re-sync Notion (dry-run first)
make sync-notion-dry
```

## Labels

<!-- Add appropriate labels: -->
<!-- area:manifests, area:vocab, area:docs, area:tests, area:schema -->
<!-- sync:notion, migration:docs-tests, governance:policy -->
<!-- risk:low, risk:medium, risk:high -->

## Additional Context

<!-- Add any additional context, screenshots, or relevant information -->
