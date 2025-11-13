# Codemod Rollback Playbook

This playbook documents the manual recovery steps if any batch from the labs → provider import codemod needs to be reverted after automation.

## Trigger conditions

Initiate this rollback if any of the following occur:

- Lane-guard identifies irreversible lane boundary regressions that cannot be addressed with follow-up commits within the batch PR.
- Security, governance, or product reviewers reject the codemod approach for a subset of files after PR creation.
- Production smoke tests or canary deploys surface regressions directly attributable to a batch PR.

## Rollback workflow

1. **Freeze automation**
   - Stop the `run_codmod_and_prs.sh` workflow immediately.
   - Notify the supervising engineer and post the failing batch number in the project board (move card to **Blocked**).

2. **Collect evidence**
   - Download the corresponding `/tmp/<branch>_artifacts.tgz` bundle from the automation host.
   - Capture `git status`, `git log -1 --stat`, and relevant CI job URLs for the failing batch.

3. **Revert the branch**
   - Locally: `git checkout main && git pull --ff-only`.
   - For the failing branch `codemod/replace-labs-batch-XX`, run `git revert --no-edit <commit>` for each codemod commit, or delete the remote branch with `git push origin --delete` if the branch has not been merged.
   - Close the GitHub PR with a note referencing the observed failure.

4. **Restore lane health**
   - Re-run `make lane-guard` (or `scripts/run_lane_guard_worktree.sh`) on `main` to confirm the repository returns to a passing state.
   - If regressions remain, coordinate a manual patch or hotfix PR before resuming automation.

5. **Post-mortem + follow-up**
   - Update this document with any new failure modes encountered.
   - Log an incident in the Codex ops channel including: batch number, root cause, mitigation, time to detect, and verification evidence.
   - Once reviewers approve a remediation plan, re-queue the affected patches by placing them in a new patch directory (e.g., `/tmp/codmod_patches_retry`).

## Safeguards when resuming

- Require an explicit 👍 from security and core reviewers in the Batch Codemod project board before running the next batch.
- Run the automation script in `--dry-run` mode to verify the patch manifest prior to re-applying patches.
- Confirm that lane-guard, smoke tests, and targeted service tests pass locally before pushing.

Keeping this loop tight ensures that any regressions introduced by the codemod are reversible with minimal risk to production lanes.
