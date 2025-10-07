---
status: stable
type: runbook
owner: unknown
module: docs.collaboration.runbooks
redirect: false
moved_to: null
---

# Notion Sync Runbook

**Purpose**: Operational procedures for synchronizing LUKHAS module manifests with Notion database.

**Audience**: DevOps, Product Teams, Documentation Teams

**SLA**: Sync 100 modules: <2 min | Single module: <5 sec | Error recovery: <5 min

---

## 1. Normal Operations

### 1.1 Full Sync (All Modules)

**When**: After bulk enrichment, weekly maintenance, or initial setup

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Pre-flight check (validates options are hydrated)
python3 scripts/notion/notion_sync.py --pre-flight

# Full sync
python3 scripts/notion/notion_sync.py --sync-all
```

**Expected Output**:
```
🔍 Pre-flight: Checking option hydration...
✅ All manifests have notion_database_options hydrated

📊 Syncing 148 modules to Notion...
✅ 148/148 synced successfully
⏱️  Duration: 1m 23s
```

**Success Criteria**:
- All modules synced without errors
- Notion database updated with latest manifest data
- Response times <5 sec per module

### 1.2 Single Module Sync

**When**: After updating a specific module manifest

```bash
# Sync specific module
python3 scripts/notion/notion_sync.py --module consciousness

# Verify in Notion
python3 scripts/notion/notion_verify.py --module consciousness
```

**Expected Output**:
```
✅ consciousness synced to Notion (page_id: 12abc...)
📋 Status: Active | Lane: L2 | MQI: 92.3
```

### 1.3 Dry Run (Validation Only)

**When**: Testing changes before actual sync

```bash
# Dry run (no Notion writes)
python3 scripts/notion/notion_sync.py --sync-all --dry-run

# Review what would change
cat artifacts/notion_sync_plan.json | jq '.changes[] | select(.action == "update")'
```

---

## 2. Pre-flight Checks

### 2.1 Option Hydration Validation

**Purpose**: Ensure all manifests have `notion_database_options` populated before sync

**Check**:
```bash
python3 scripts/notion/notion_sync.py --pre-flight
```

**Expected Output**:
```
✅ All manifests have notion_database_options hydrated
```

**Failure Output**:
```
❌ 12 manifests missing notion_database_options:
  - consciousness/module.manifest.json
  - identity/module.manifest.json
  ...

Run: make enrich
```

**Auto-fix**:
```bash
# Backfill missing options
python3 scripts/notion/notion_sync.py --auto-backfill

# Or use enrichment pipeline
make enrich
```

### 2.2 Notion API Connectivity

**Check**:
```bash
# Test Notion API connection
python3 scripts/notion/notion_health.py

# Expected output
✅ Notion API: Reachable
✅ Database ID: Valid (12abc...)
✅ API Token: Valid (expires 2026-01-01)
✅ Rate Limit: 95/100 requests available
```

**Troubleshooting**:
- **API Token Invalid**: Check `NOTION_API_TOKEN` environment variable
- **Database Not Found**: Verify `NOTION_DATABASE_ID` in `.env`
- **Rate Limit**: Wait 60 seconds and retry

---

## 3. Troubleshooting

### 3.1 Rate Limiting (429 Errors)

**Symptom**: Sync fails with `429 Too Many Requests`

**Diagnosis**:
```bash
python3 scripts/notion/notion_sync.py --sync-all 2>&1 | grep "429"
```

**Output**:
```
❌ Rate limited: 429 Too Many Requests (retry after 60s)
```

**Fix** (Automatic Retry):
```bash
# Sync with auto-retry on rate limit
python3 scripts/notion/notion_sync.py \
  --sync-all \
  --retry-on-rate-limit \
  --max-retries 3 \
  --backoff 60
```

**Fix** (Manual Batching):
```bash
# Sync in batches of 20 modules with 10s delay
python3 scripts/notion/notion_sync.py \
  --sync-all \
  --batch-size 20 \
  --batch-delay 10
```

**Prevention**:
- Use `--batch-size` for large syncs
- Schedule syncs outside peak hours
- Monitor rate limit with `notion_health.py`

### 3.2 Schema Mismatch

**Symptom**: Sync fails with Notion validation errors

**Diagnosis**:
```bash
python3 scripts/notion/notion_sync.py --sync-all 2>&1 | grep "validation_error"
```

**Output Example**:
```
❌ consciousness: Notion validation error
   Field 'MQI' expects number, got string "92.3"
```

**Common Causes**:
1. **Type mismatch**: Manifest has string, Notion expects number
2. **Missing required fields**: Notion database schema changed
3. **Invalid enum values**: Status/Lane values not in Notion select options

**Fix**:
```bash
# Check Notion schema
python3 scripts/notion/notion_schema_dump.py \
  --output artifacts/notion_schema.json

# Compare with manifest schema
diff <(jq '.properties' artifacts/notion_schema.json) \
     <(jq '.notion_database_options' consciousness/module.manifest.json)

# Update manifest to match Notion schema
# OR update Notion database schema to match manifest
```

### 3.3 Page Not Found (404 Errors)

**Symptom**: Sync fails with `404 Page not found`

**Diagnosis**:
```bash
python3 scripts/notion/notion_sync.py --module consciousness
```

**Output**:
```
❌ consciousness: Page not found (page_id: 12abc...)
```

**Causes**:
1. **Page deleted in Notion**: Manual deletion or archive
2. **Invalid page_id**: Manifest has stale page_id
3. **Permission issue**: API token lacks page access

**Fix** (Create New Page):
```bash
# Remove stale page_id from manifest
jq 'del(.notion_page_id)' consciousness/module.manifest.json > tmp && mv tmp consciousness/module.manifest.json

# Re-sync (will create new page)
python3 scripts/notion/notion_sync.py --module consciousness --create-if-missing

# Update manifest with new page_id
python3 scripts/notion/notion_sync.py --module consciousness --update-manifest
```

### 3.4 Missing Options in Manifest

**Symptom**: Pre-flight check fails

**Diagnosis**:
```bash
python3 scripts/notion/notion_sync.py --pre-flight
```

**Output**:
```
❌ 5 manifests missing notion_database_options
```

**Fix** (Auto-backfill):
```bash
# Extract options from enriched manifests
python3 scripts/notion/notion_sync.py --auto-backfill

# Expected output
✅ Backfilled notion_database_options for 5 modules
📝 Updated manifests:
  - consciousness/module.manifest.json
  - identity/module.manifest.json
  ...

# Re-run pre-flight
python3 scripts/notion/notion_sync.py --pre-flight  # Should pass
```

**Fix** (Manual Enrichment):
```bash
# Re-run full enrichment
make enrich

# Enrichment will populate notion_database_options
# Re-run pre-flight
python3 scripts/notion/notion_sync.py --pre-flight  # Should pass
```

---

## 4. Incident Response

### 4.1 Emergency Rollback (Notion Data Corrupted)

**Scenario**: Sync introduced incorrect data to Notion database

**Procedure**:
```bash
# Step 1: Identify last good sync
tail -10 artifacts/notion_sync_ledger.jsonl | jq -r '.timestamp, .sha'

# Step 2: Restore Notion from backup
python3 scripts/notion/notion_restore.py \
  --ledger artifacts/notion_sync_ledger.jsonl \
  --sha <LAST_GOOD_SHA> \
  --confirm

# Step 3: Verify restoration
python3 scripts/notion/notion_verify.py --all

# Step 4: Document incident
echo "Rollback completed at $(date)" >> incidents/notion_rollback.log
```

**Expected Duration**: <10 minutes

### 4.2 Bulk Delete Recovery

**Scenario**: Accidentally deleted pages in Notion

**Procedure**:
```bash
# Step 1: Check Notion trash
# (Manual: Open Notion → Trash → Restore pages)

# Step 2: Re-sync from manifests
python3 scripts/notion/notion_sync.py \
  --sync-all \
  --create-if-missing \
  --update-manifest

# Step 3: Verify all pages restored
python3 scripts/notion/notion_verify.py --all --verbose
```

### 4.3 API Token Leak

**Scenario**: Notion API token exposed in logs or code

**Immediate Actions**:
```bash
# Step 1: Revoke token in Notion
# (Manual: Notion Settings → Integrations → Revoke token)

# Step 2: Generate new token
# (Manual: Notion Settings → Integrations → New integration)

# Step 3: Update environment variable
echo "NOTION_API_TOKEN=new_token_here" > .env.local

# Step 4: Rotate secrets in CI/CD
# (Update GitHub Secrets, etc.)

# Step 5: Test connectivity
python3 scripts/notion/notion_health.py
```

**Follow-up**:
- Audit all systems that had access to old token
- Review logs for unauthorized access
- Document in security incident report

---

## 5. Maintenance

### 5.1 Weekly Sync

**Schedule**: Every Monday 9:00 AM UTC

**Procedure**:
```bash
# Full sync with validation
make notion-sync-weekly

# Equivalent to:
python3 scripts/notion/notion_sync.py --pre-flight
python3 scripts/notion/notion_sync.py --sync-all --batch-size 50
python3 scripts/notion/notion_verify.py --all
```

**Success Criteria**:
- All modules synced without errors
- No validation failures
- Sync duration <5 minutes

### 5.2 Monthly Audit

**Schedule**: First Monday of each month

**Procedure**:
```bash
# Step 1: Compare Notion vs Manifests
python3 scripts/notion/notion_audit.py \
  --output artifacts/notion_audit_$(date +%Y%m).json

# Step 2: Review discrepancies
cat artifacts/notion_audit_*.json | jq '.discrepancies'

# Step 3: Fix discrepancies
# (Manual review and correction)

# Step 4: Document findings
echo "Audit completed: $(date)" >> docs/audit_log.md
```

### 5.3 Schema Evolution

**When**: Adding new fields to manifests or Notion database

**Procedure**:
```bash
# Step 1: Update Notion database schema (manual in Notion UI)

# Step 2: Update manifest schema
vim schemas/module.manifest.schema.json

# Step 3: Update enrichment extractor
vim scripts/enrich/claude_extractor.py

# Step 4: Backfill existing manifests
make enrich

# Step 5: Sync to Notion
python3 scripts/notion/notion_sync.py --sync-all

# Step 6: Update feature flags if needed
vim schemas/flags.json
```

---

## 6. Automation Integration

### 6.1 CI Pipeline Integration

**GitHub Actions** (.github/workflows/notion-sync.yml):
```yaml
name: Notion Sync
on:
  push:
    branches: [main]
    paths:
      - '**/module.manifest.json'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Pre-flight check
        env:
          NOTION_API_TOKEN: ${{ secrets.NOTION_API_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
        run: |
          python3 scripts/notion/notion_sync.py --pre-flight

      - name: Sync to Notion
        env:
          NOTION_API_TOKEN: ${{ secrets.NOTION_API_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
        run: |
          python3 scripts/notion/notion_sync.py \
            --sync-all \
            --batch-size 50 \
            --retry-on-rate-limit

      - name: Verify sync
        env:
          NOTION_API_TOKEN: ${{ secrets.NOTION_API_TOKEN }}
        run: |
          python3 scripts/notion/notion_verify.py --all
```

### 6.2 Post-commit Hook

**Install**:
```bash
cp scripts/hooks/post-commit-notion .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

**Hook Content** (.git/hooks/post-commit):
```bash
#!/bin/bash

# Only sync if module manifests changed
changed_files=$(git diff-tree -r --name-only --no-commit-id HEAD)

if echo "$changed_files" | grep -q "module.manifest.json"; then
  echo "📊 Module manifests changed, syncing to Notion..."
  python3 scripts/notion/notion_sync.py --sync-changed --async
  echo "✅ Notion sync queued (background)"
fi
```

---

## 7. Monitoring and Alerts

### 7.1 Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Sync success rate | 100% | <98% |
| Sync duration (100 modules) | <2 min | >5 min |
| API error rate | <1% | >5% |
| Rate limit hits | 0/day | >3/day |
| Schema validation failures | 0 | >1 |

### 7.2 Alert Channels

- **Slack**: `#lukhas-notion-sync`
- **PagerDuty**: P2 for sync failures, P1 for API token issues
- **Email**: DevOps team distribution list

### 7.3 Healthcheck Endpoint

```bash
# Run healthcheck
python3 scripts/notion/notion_health.py --json

# Expected output
{
  "status": "healthy",
  "api_reachable": true,
  "database_accessible": true,
  "token_valid": true,
  "rate_limit_remaining": 95,
  "last_sync_success": "2025-10-05T12:34:56Z",
  "last_sync_duration_sec": 83
}
```

---

## 8. Security

### 8.1 API Token Management

- **Storage**: Environment variable `NOTION_API_TOKEN` (never commit to git)
- **Rotation**: Every 90 days
- **Access**: Read-only in production, read-write in CI/CD only
- **Auditing**: All API calls logged to `artifacts/notion_api_audit.log`

### 8.2 Data Privacy

- **PII**: No personally identifiable information in manifests
- **Encryption**: All API calls over HTTPS
- **Compliance**: GDPR-compliant (data retention <30 days)

---

## 9. Contacts

**Primary**: Documentation Team
**Escalation**: Platform Engineering
**Notion Admin**: Product Team
**Issue Tracker**: GitHub Issues with `notion-sync` label

---

## 10. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-05 | Initial runbook creation | Claude |

---

**Next Review**: 2025-11-05 (Monthly)
