# /promote-batch
Batch driver for lane promotions from `candidate/core/*` to `lukhas/core/*`, one PR at a time, in this order:
orchestration → glyph → integration → api → neural → interfaces → monitoring → symbolic

## Inputs
- Optional: `queue=ops/promotion_queue.yaml` (default) — provides module order & owners.
- Optional: `dry_run=true|false` (default false) — if true, only prints the plan.
- Optional: `start_after=<module>` — skip modules up to and including this name.

## Queue file format (YAML)
# ops/promotion_queue.yaml
order:
  - module: orchestration
    owner: Jules01
  - module: glyph
    owner: Jules02
  - module: integration
    owner: Jules03
  - module: api
    owner: Jules04
  - module: neural
    owner: Jules05
  - module: interfaces
    owner: Jules06
  - module: monitoring
    owner: Jules07
  - module: symbolic
    owner: Jules03

## Policy
- Execute **one module per invocation** of `/promote-module`; open **one PR**; then stop and await user review.
- No bulk copies. No deletions under `candidate/`.
- Use shims only if downstream still imports `candidate.core.<module>`.
- Always run smoke tests before/after as defined by `/promote-module`.

## Steps
1) Read the queue file (`ops/promotion_queue.yaml`). If missing, create it from the template above and STOP (ask user to review owners).
2) If `start_after` is set, skip all entries up to and including that module.
3) For the **first pending** module in `order`:
   - Print a summary plan: module, owner, candidate path, lukhas target, presence of existing lukhas module, dependent imports detected.
   - Ask for approval to continue.
4) Invoke the single-module flow:
   - Run: `/promote-module module=<module> owner=<owner>`
   - On success, create a lightweight marker at `ops/.promotion_history/<module>.done` with timestamp + smoke results path.
5) STOP and print:
   - “Batch paused after <module>. Review the PR and merge before running /promote-batch again to continue with the next module.”

## Output
- A concise table of remaining modules in the queue with status: PENDING / DONE.
- Pointer to the newly opened PR from `/promote-module`.

## Acceptance Criteria
- Exactly one promotion PR opened.
- No file deletions under `candidate/`.
- Smoke results captured as per `/promote-module`.
