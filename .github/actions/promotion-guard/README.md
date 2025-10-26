# MATRIZ-007 Promotion Guard

## Overview
Automated GitHub Action that prevents production promotion until MATRIZ-007 PQC migration is complete.

## How It Works

1. **Triggers**: Runs on all PRs to main branch
2. **Checks**:
   - Issue #490 (MATRIZ-007) state (must be CLOSED)
   - Week 6 checklist completion (all items must be checked)
3. **Fails**: If issue is OPEN or Week 6 has unchecked items
4. **Passes**: Only when MATRIZ-007 is CLOSED and Week 6 complete

## Workflow File

`.github/workflows/matriz-007-guard.yml`

## Script

`check_matriz_007.py` - Python script that:
- Fetches issue #490 via GitHub API
- Parses Week 6 checklist from issue body
- Validates all checklist items are marked complete
- Produces clear error messages with blocking items

## Configuration

Environment variables in workflow:
- `ISSUE_NUMBER`: "490" (MATRIZ-007 tracking issue)
- `WEEK_SECTION_HEADING`: "Week 6" (checklist section to validate)

## Example Output

### When Blocked

```
================================================================================
MATRIZ Issue #490: MATRIZ-007 PQC migration - 6-week plan
State: OPEN
================================================================================

BLOCKERS preventing promotion:
 * Issue is OPEN. Promotion blocked until MATRIZ-007 is CLOSED (completed).
 * Week 6 checklist has 3 unchecked item(s):
  - Line 142: Implement key rotation procedure and dual-sign transition
  - Line 143: Complete red-team results with no high severity findings
  - Line 144: Performance benchmarking and sign/verify latency validated

REMEDIATION:
 - Close the issue #490 after confirming Week 6 completion. Use the issue checklist to mark items done.
 - Ensure the Week 6 checklist in the issue body contains items such as: 'Dilithium2 sign/verify passed', 'Key rotation implemented', 'Red-team sign-off', 'Performance validated', etc.
 - After closing and verifying, re-run CI to allow promotion.
================================================================================

Promotion guard: BLOCKED
```

### When Passing

```
================================================================================
MATRIZ Issue #490: MATRIZ-007 PQC migration - 6-week plan
State: CLOSED
================================================================================

No blockers found: Issue appears CLOSED and Week 6 checklist (if present) has all items checked.

Promotion guard: PASS — MATRIZ-007 appears completed for Week 6.
```

## Adding as Required Status Check

### Via GitHub UI
1. Go to Settings → Branches → main
2. Edit branch protection rule
3. Add "MATRIZ-007 Completion Check" to required status checks
4. Save changes

### Via CLI
```bash
# Add to required status checks
gh api --method PUT /repos/LukhasAI/Lukhas/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["nodespec-validate","registry-ci","pqc-sign-verify","MATRIZ-007 Completion Check"]}' \
  -f enforce_admins=true
```

### Via Script
```bash
# Update configure_branch_protection.sh to include:
REQUIRED_CHECKS=(
    "nodespec-validate"
    "registry-ci"
    "pqc-sign-verify"
    "MATRIZ-007 Completion Check"
)
```

## Week 6 Checklist Format

The guard expects a checklist in issue #490 under a "Week 6" heading:

```markdown
### Week 6: Production Readiness

- [ ] Performance benchmarking at scale
- [ ] Load testing (50+ ops/sec target)
- [ ] Remove TEMP-STUB markers
- [ ] Final security sign-off
- [ ] Dilithium2 signing operational (no fallbacks)
- [ ] Red-team security review passed
- [ ] Key rotation implemented and tested
```

The script is flexible with heading formats:
- "Week 6"
- "Week 6: Production Readiness"
- "### Week 6 — Validation"

Case-insensitive matching.

## Testing Locally

```bash
# Set up environment
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPOSITORY="LukhasAI/Lukhas"
export ISSUE_NUMBER="490"
export WEEK_SECTION_HEADING="Week 6"

# Run the script
python3 .github/actions/promotion-guard/check_matriz_007.py
```

Expected exit codes:
- `0` = Pass (promotion allowed)
- `1` = Blocked (promotion prevented)

## Integration with TEMP-STUB Guard

This guard complements the existing `temp-stub-guard.yml`:

| Guard | Purpose | Trigger |
|-------|---------|---------|
| temp-stub-guard | Blocks if TEMP-STUB markers present | Production lane file modifications |
| matriz-007-guard | Blocks if MATRIZ-007 not complete | All PRs to main |

Both must pass for production promotion.

## Dependencies

- Python 3.11+
- `requests` library (for GitHub API)
- GitHub token with `issues: read` permission

## Troubleshooting

### Issue fetch fails
```
ERROR: failed to fetch issue #490 (HTTP 404)
```
**Solution**: Verify ISSUE_NUMBER is correct and issue exists.

### No checklist found
```
BLOCKERS preventing promotion:
 * No Week 6 checklist section found
```
**Solution**: Add Week 6 checklist to issue #490 body.

### False positive (guard blocks when shouldn't)
**Debug**:
1. Check issue #490 state: `gh issue view 490`
2. Verify all Week 6 checkboxes are marked: `[x]` not `[ ]`
3. Ensure issue is CLOSED

### Guard not running on PR
**Check**:
1. Workflow file syntax: `gh workflow view "MATRIZ-007 Promotion Guard"`
2. PR target branch is `main`
3. Script exists and is executable: `ls -la .github/actions/promotion-guard/`

## Security Notes

- Uses `pull_request_target` to access GITHUB_TOKEN safely
- Only reads issue data (no write permissions)
- Script validates input and fails safely on errors
- No secrets or sensitive data in output

## Future Enhancements

Potential additions:
- Check PQC CI artifact presence (verify pqc-sign-verify passed)
- Validate test coverage thresholds
- Check for required security approvals
- Verify performance benchmark results

## Related Documentation

- [MATRIZ-007 Timeline](../../../docs/ops/POST_MERGE_ACTIONS.md#matriz-007-pqc-migration-timeline)
- [Post-Merge Actions](../../../docs/ops/POST_MERGE_ACTIONS.md)
- [T4 Execution Summary](../../../docs/ops/T4_EXECUTION_SUMMARY.md)

## Maintenance

**Owner**: Security Team
**Review Schedule**: After MATRIZ-007 completion
**Deprecation**: Can be removed once MATRIZ-007 is closed and guard has passed consistently

## Change Log

- **2025-10-24**: Initial implementation
- Guards MATRIZ-007 Week 6 completion
- Blocks production promotion until PQC migration complete
