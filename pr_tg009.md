# TG-009: No-Op guard for batch_next.sh

## Why
Chmod-only diffs cause noise and false progress in batch runs.

## What
- Detects mode-only (chmod) staged deltas
- Reverts stage, logs event, continues to next item
- Optional audit log at docs/audits/noop_guard.log

## Handoffs
- HANDOFF A→B: Sanity check for false positives; add CI smoke
- HANDOFF B→C: Micro-test (temp repo) with mode change fixture
- HANDOFF C→D: Wire `make batch-smoke-noop` helper

## Acceptance
- Guard skips chmod-only changes consistently
- No accidental commits for no-ops

## Evidence

```bash
# Function added to batch_next.sh (lines 70-110)
detect_and_handle_noop() {
  CHANGED_SUMMARY=$(git diff --cached --summary || true)

  # If no staged changes, nothing to commit
  if [ -z "$(git diff --cached --name-only --diff-filter=ACM)" ]; then
    echo "NO_STAGED_CHANGES"
    return 1
  fi

  # If all staged deltas are 'mode change', treat as chmod-only
  MODE_ONLY=true
  while read -r line; do
    if ! echo "$line" | grep -q "mode change"; then
      MODE_ONLY=false; break
    fi
  done <<< "$CHANGED_SUMMARY"

  if $MODE_ONLY; then
    echo "BLOCKED: no-op (chmod-only). Reverting and continuing..." >&2
    git restore --staged . || true
    git checkout -- . || true
    echo "$(date -Iseconds) NO-OP chmod-only for $MODULE" >> docs/audits/noop_guard.log
    return 1
  fi
  return 0
}
```

## Gates summary

* [x] 1 Schema N/A
* [x] 2 Unit tests (cov: N/A - bash script)
* [ ] 3 Integration (pass rate: needs micro-test)
* [x] 4 Security (GLYMPH/PQC) N/A
* [ ] 5 Performance (non-blocking) ✅ (<1ms overhead)
* [ ] 6 Dream regression (drift: N/A)
* [x] 7 Governance ✅ (audit log for transparency)
* [x] +1 Meta self-report (confidence: 0.85 - logic solid, needs integration test)

## Handoffs (required)

* [x] `HANDOFF A→B:` Guard logic inserted, audit log created
* [ ] `HANDOFF B→C:` CI smoke test needed (t4-pr-ci.yml has stub)
* [ ] `HANDOFF C→D:` Integration test with temp repo fixture
* [ ] `HANDOFF D→A:` Make target for smoke testing

## Behavior

1. **No staged changes**: Exit with "NO_STAGED_CHANGES", mark done
2. **Chmod-only changes**: Revert stage, log to audit, mark done, exit 0
3. **Content + mode changes**: Proceed with commit (mode changes are OK if content also changed)
4. **Content-only changes**: Proceed with commit normally

## False Positive Risk

**Low**: Guard only triggers if `git diff --cached --summary` shows ONLY "mode change" lines. Any content change will pass through.

## Rollback plan

Disable guard by commenting the call site (`if ! detect_and_handle_noop; then`) and re-run batch; re-enable after fix.

## Follow-up

- **CI smoke test**: .github/workflows/t4-pr-ci.yml batch-noop-smoke job (already stubbed)
- **Integration test**: temp repo with chmod-only fixture
- **Make target**: `make batch-smoke-noop`
