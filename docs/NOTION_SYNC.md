---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Notion Sync - T4/0.01% External Visibility

Complete system for syncing LUKHAS enriched manifests to Notion with full provenance tracking and controlled vocabulary.

## Architecture

```
Enriched Manifests → Schema Validation → Vocab Gates → Notion API
         ↓                                                  ↓
   Provenance SHA                                    Database Pages
         ↓                                                  ↓
   Ledger Track                                      Multi-select Options
```

## Components

### 1. Notion Backfill (`scripts/notion_backfill.py`)

Ensures Notion database has multi-select options for all canonical features and tags.

**Purpose**: Pre-populate Notion database with controlled vocabulary before syncing manifests.

**Features**:
- Dry-run by default
- Stable color assignment via hash
- Append-only (no deletions unless `--prune`)
- Rate-limited API calls
- Ledger tracking

**Usage**:
```bash
# Dry-run: see what would be added
python scripts/notion_backfill.py --features --tags

# Apply changes
python scripts/notion_backfill.py --features --tags --apply

# Dangerous: remove options not in vocab
python scripts/notion_backfill.py --features --prune --apply
```

**Environment Variables**:
```bash
export NOTION_TOKEN="secret_..."
export NOTION_DATABASE_ID="..."
export NOTION_RATE_LIMIT=3  # ops/sec (optional, default 3)
```

### 2. Notion Sync (`scripts/notion_sync.py`)

Syncs enriched manifests to Notion database with SHA-based idempotency.

**Purpose**: One-way sync of manifest data to Notion for external visibility.

**Features**:
- SHA-based skip logic (no-op if unchanged)
- Full provenance tracking
- Schema + vocab validation before sync
- Dry-run with diff preview
- Append-only ledger
- Markdown reports for PRs

**Usage**:
```bash
# Dry-run all manifests
python scripts/notion_sync.py --all --dry-run

# Sync single module
python scripts/notion_sync.py --module consciousness

# Sync with PR report
python scripts/notion_sync.py --all --report-md
```

**Environment Variables**:
```bash
export NOTION_TOKEN="secret_..."
export NOTION_DATABASE_ID="..."
export NOTION_RATE_LIMIT=3  # ops/sec (optional, default 3)
```

## Notion Database Setup

### Required Properties

Create a Notion database with these exact property names:

1. **Module** (Title) - Module name
2. **Description** (Rich text) - Module description
3. **Features** (Multi-select) - Canonical features
4. **APIs** (Rich text) - Formatted API list
5. **SLA p95** (Number) - Performance target (ms)
6. **Coverage** (Number) - Test coverage percentage
7. **Provenance SHA** (Rich text) - Content hash for idempotency
8. **Updated At** (Date) - Last sync timestamp

### Optional Property

- **Tags** (Multi-select) - Module tags

### Integration Setup

1. Create an internal integration at https://www.notion.so/my-integrations
2. Copy the integration token (starts with `secret_`)
3. Share your database with the integration
4. Copy the database ID from the URL: `https://notion.so/{workspace}/{database_id}?v=...`

## Workflow

### Initial Setup

```bash
# 1. Backfill vocabulary options (dry-run first)
python scripts/notion_backfill.py --features --tags

# 2. Apply backfill
python scripts/notion_backfill.py --features --tags --apply

# 3. Sync manifests (dry-run first)
python scripts/notion_sync.py --all --dry-run

# 4. Apply sync
python scripts/notion_sync.py --all
```

### Ongoing Sync

```bash
# After enriching manifests or updating vocab
python scripts/notion_backfill.py --features --tags --apply
python scripts/notion_sync.py --all
```

### CI Integration

**.github/workflows/notion-sync.yml** (example):

```yaml
name: Notion Sync Preview

on:
  pull_request:
    paths:
      - 'vocab/features.json'
      - 'vocab/tags.json'
      - '**/module.manifest.json'

jobs:
  notion-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install requests jsonschema

      - name: Notion Backfill (dry-run)
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
        run: |
          python scripts/notion_backfill.py --features --tags

      - name: Notion Sync (dry-run with report)
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
        run: |
          python scripts/notion_sync.py --all --dry-run --report-md

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: notion-sync-report
          path: reports/notion_sync_report.md
```

## Guarantees (T4/0.01%)

### Provenance
✅ Every synced page carries `Provenance SHA` from manifest content
✅ Ledger tracks all sync attempts with timestamps and status
✅ Full audit trail in `manifests/.ledger/notion_sync.ndjson`

### Idempotency
✅ SHA comparison before every write
✅ No-op if page content unchanged
✅ Deterministic color assignment for options
✅ Safe to re-run multiple times

### Safety
✅ Schema validation before sync (hard fail on violations)
✅ Vocab validation before sync (hard fail on unknown features/tags)
✅ Rate limiting (default 3 ops/sec, configurable)
✅ Dry-run default for destructive operations
✅ Append-only ledger (no silent failures)

### Controlled Entropy
✅ Only canonical features/tags synced
✅ Notion multi-select options = controlled vocabulary
✅ No free-text pollution
✅ Backfill ensures options exist before sync

## Ledger Format

**Location**: `manifests/.ledger/notion_sync.ndjson`

**Record Types**:

```json
{
  "ts": "2025-10-03T12:34:56.789012+00:00",
  "action": "notion-backfill-apply",
  "properties": ["Features", "Tags"],
  "status": "success",
  "total_options": 24
}
```

```json
{
  "ts": "2025-10-03T12:35:01.234567+00:00",
  "module": "consciousness",
  "page_id": "abc123...",
  "sha": "a4c1d2...",
  "action": "create",
  "status": "success"
}
```

```json
{
  "ts": "2025-10-03T12:35:02.345678+00:00",
  "module": "memory",
  "page_id": "def456...",
  "sha": "e8f9a0...",
  "action": "skip",
  "status": "sha_match"
}
```

## Reports

### Markdown Reports

**Location**: `reports/notion_sync_report.md`

Generated with `--report-md` flag:

```markdown
# 🔄 Notion Sync Report
_Generated 2025-10-03T12:35:10.123456+00:00_

## Summary
- **Created**: 12
- **Updated**: 34
- **Skipped**: 102

## Details
- `consciousness` → create (sha:a4c1d2ef)
- `memory` → update (sha:e8f9a0b1)
- `identity` → skip(sha-match) (sha:c2d3e4f5)
...
```

## Troubleshooting

### "Notion properties missing"

**Error**: `Property 'Features' not found in database`

**Fix**: Ensure all required properties exist in Notion database with exact names (case-sensitive).

### "Multi-select option not found"

**Error**: `Option 'consciousness.theory' does not exist`

**Fix**: Run backfill first:
```bash
python scripts/notion_backfill.py --features --tags --apply
```

### "Rate limit exceeded"

**Error**: `429 Too Many Requests`

**Fix**: Reduce rate limit:
```bash
export NOTION_RATE_LIMIT=2
```

### "Schema validation failed"

**Error**: `Schema validation failed: ...`

**Fix**: Ensure manifests are enriched and valid:
```bash
python scripts/ci/validate_schema.py
python scripts/enrich_manifests.py
```

## Best Practices

1. **Always backfill before syncing** - Ensure Notion has all multi-select options
2. **Dry-run first** - Preview changes before applying
3. **Use reports in PRs** - Generate Markdown reports for visibility
4. **Monitor ledger** - Check `notion_sync.ndjson` for errors
5. **Rate limit in CI** - Set conservative limits to avoid 429s
6. **Schema first** - Validate manifests before attempting sync

## Next Steps

1. **Backfill vocabulary** → `notion_backfill.py --features --tags --apply`
2. **Sync manifests** → `notion_sync.py --all`
3. **Setup CI preview** → Add dry-run workflow to GitHub Actions
4. **Monitor ledger** → Check for errors in `notion_sync.ndjson`

---

**Status**: ✅ Complete T4/0.01% external visibility system
**Quality Level**: Provable, auditable, falsifiable
