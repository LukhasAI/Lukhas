---
status: wip
type: documentation
---


# Promotion Queue & Batch Driver

This repo promotes modules from `candidate/core/*` → `lukhas/core/*` one PR at a time.

## How to run (Claude Code)
1) Review owners in `ops/promotion_queue.yaml`.
2) Run `/promote-batch`:
   - Optionally: `/promote-batch start_after=<module>`
   - Optionally: `/promote-batch dry_run=true` (prints plan only)
3) Approve when asked. The command calls `/promote-module` for the first pending item, opens a PR, and stops.
4) After merge, run `/promote-batch` again to continue with the next item.

## Status tracking
Each completed module creates `ops/.promotion_history/<module>.done` with timestamp and smoke result pointers.

## Safety rules
- One module per PR.
- No deletions under `candidate/`.
- Shims allowed only if other code still imports `candidate.core.<module>`.
- Smoke tests must pass before/after.
