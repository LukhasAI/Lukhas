#!/usr/bin/env bash
# Daily Coordination Snapshot
# Captures current state of all tasks, PRs, and CI status

set -euo pipefail

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
SNAPSHOT_DIR="docs/audits/coordination/${DATE}"
mkdir -p "${SNAPSHOT_DIR}"

echo "📸 Capturing coordination snapshot: ${DATE} ${TIME}"

# ============================================================================
# 1. Update task_status.json with current timestamp
# ============================================================================
echo "🔄 Updating task status timestamp..."
TMP_JSON=$(mktemp)
jq --arg timestamp "${DATE}T${TIME}Z" '.last_updated = $timestamp' \
  docs/plans/task_status.json > "$TMP_JSON"
mv "$TMP_JSON" docs/plans/task_status.json

# ============================================================================
# 2. Capture PR status
# ============================================================================
echo "📋 Capturing PR status..."
gh pr list --state open --json number,title,state,statusCheckRollup,headRefName \
  > "${SNAPSHOT_DIR}/pr_status_${TIMESTAMP}.json" || echo "[]" > "${SNAPSHOT_DIR}/pr_status_${TIMESTAMP}.json"

# Count PRs
PR_COUNT=$(jq 'length' "${SNAPSHOT_DIR}/pr_status_${TIMESTAMP}.json")
echo "  → ${PR_COUNT} open PRs"

# ============================================================================
# 3. Check CI status
# ============================================================================
echo "🔧 Checking CI status..."
CI_FAILURES=0

# Check if there are any PRs with failing checks
if [ "$PR_COUNT" -gt 0 ]; then
  CI_FAILURES=$(jq '[.[] | select(.statusCheckRollup != null and .statusCheckRollup != []) | select(.statusCheckRollup[] | .conclusion == "FAILURE")] | length' \
    "${SNAPSHOT_DIR}/pr_status_${TIMESTAMP}.json" || echo "0")
fi

echo "  → ${CI_FAILURES} PRs with CI failures"

# ============================================================================
# 4. Check worktree status
# ============================================================================
echo "🌳 Checking worktree status..."
git worktree list > "${SNAPSHOT_DIR}/worktrees_${TIMESTAMP}.txt"
WORKTREE_COUNT=$(git worktree list | wc -l | tr -d ' ')
echo "  → ${WORKTREE_COUNT} active worktrees"

# ============================================================================
# 5. Generate metrics snapshot
# ============================================================================
echo "📊 Generating metrics..."
cat > "${SNAPSHOT_DIR}/metrics_${TIMESTAMP}.json" <<JSON
{
  "timestamp": "${DATE}T${TIME}Z",
  "snapshot_id": "${TIMESTAMP}",
  "prs": {
    "open": ${PR_COUNT},
    "ci_failures": ${CI_FAILURES}
  },
  "worktrees": {
    "count": ${WORKTREE_COUNT}
  },
  "tasks": {
    "total": $(jq '.summary.total_tasks' docs/plans/task_status.json),
    "in_progress": $(jq '.summary.in_progress' docs/plans/task_status.json),
    "completed": $(jq '.summary.completed' docs/plans/task_status.json),
    "not_started": $(jq '.summary.not_started' docs/plans/task_status.json),
    "blocked": $(jq '.summary.blocked' docs/plans/task_status.json)
  }
}
JSON

# ============================================================================
# 6. Generate Markdown summary
# ============================================================================
echo "📝 Generating Markdown summary..."
cat > "${SNAPSHOT_DIR}/summary_${TIMESTAMP}.md" <<MD
# Coordination Snapshot
**Date**: ${DATE} ${TIME}
**Snapshot ID**: ${TIMESTAMP}

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | $(jq '.summary.total_tasks' docs/plans/task_status.json) |
| **In Progress** | $(jq '.summary.in_progress' docs/plans/task_status.json) |
| **Completed** | $(jq '.summary.completed' docs/plans/task_status.json) |
| **Not Started** | $(jq '.summary.not_started' docs/plans/task_status.json) |
| **Blocked** | $(jq '.summary.blocked' docs/plans/task_status.json) |
| **Completion %** | $(jq '.summary.completion_percentage' docs/plans/task_status.json)% |

## PRs

| Metric | Value |
|--------|-------|
| **Open PRs** | ${PR_COUNT} |
| **CI Failures** | ${CI_FAILURES} |

## Worktrees

| Metric | Value |
|--------|-------|
| **Active Worktrees** | ${WORKTREE_COUNT} |

## Files Generated

- \`pr_status_${TIMESTAMP}.json\` - PR status from GitHub
- \`worktrees_${TIMESTAMP}.txt\` - Active worktrees
- \`metrics_${TIMESTAMP}.json\` - Aggregate metrics
- \`summary_${TIMESTAMP}.md\` - This summary

## Next Actions

- Review open PRs for merge readiness
- Check CI failures and address blockers
- Update task status for completed work

MD

# ============================================================================
# 7. Create symlink to latest snapshot
# ============================================================================
echo "🔗 Creating symlink to latest..."
ln -sf "${SNAPSHOT_DIR}/summary_${TIMESTAMP}.md" "${SNAPSHOT_DIR}/latest.md"
ln -sf "${SNAPSHOT_DIR}/metrics_${TIMESTAMP}.json" "${SNAPSHOT_DIR}/latest.json"

# ============================================================================
# Done
# ============================================================================
echo "✅ Snapshot complete: ${SNAPSHOT_DIR}/"
echo ""
echo "View summary:"
echo "  cat ${SNAPSHOT_DIR}/latest.md"
echo ""
echo "View metrics:"
echo "  jq . ${SNAPSHOT_DIR}/latest.json"
