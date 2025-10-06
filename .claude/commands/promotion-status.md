---
status: wip
type: documentation
---
# /promotion-status
Summarize promotion progress for modules queued in `ops/promotion_queue.yaml`.

## What it does
- Reads `ops/promotion_queue.yaml` → ordered list of modules and owners
- Checks for marker files in `ops/.promotion_history/<module>.done`
- Optionally inspects `reports/deep_search/SMOKE_<module>_*.txt` for pass/fail
- Prints a compact status table + next actionable module

## Steps (do not skip)
1) Ensure `ops/promotion_queue.yaml` exists; if missing, print a clear error and suggest creating it from the template.
2) Ensure `ops/.promotion_history/` exists; create it if missing (no-op for read-only).
3) For each item in `order`:
   - `status = DONE` if `ops/.promotion_history/<module>.done` exists, else `PENDING`.
   - Try to read these (optional):
     - `reports/deep_search/SMOKE_<module>_candidate.txt`
     - `reports/deep_search/SMOKE_<module>_lukhas.txt`
     Summarize last line containing `passed`/`failed` or total counts.
   - Determine `next_pending` as the first PENDING module.
4) Print a table:

   | #   | Module        | Owner   | Status       | Candidate Smoke | Lukhas Smoke | Marker                                    |
   | --- | ------------- | ------- | ------------ | --------------- | ------------ | ----------------------------------------- |
   | 1   | orchestration | Jules01 | DONE/PENDING | pass/fail       | pass/fail    | ops/.promotion_history/orchestration.done |

5) If there is a `next_pending`, print the exact command to continue:
   - `/promote-module module=<next_pending> owner=<owner>`

## Output
- A concise table in chat
- A single-line summary: `Next: <module> (owner <owner>)` or `All modules promoted.`

## Acceptance Criteria
- Handles empty/missing files gracefully
- No file mutations other than creating `ops/.promotion_history/` if missing
