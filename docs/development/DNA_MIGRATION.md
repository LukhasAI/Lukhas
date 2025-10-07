---
status: wip
type: documentation
owner: unknown
module: development
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# DNA Migration Plan (Phased)

## Phases
1) Dual-write (`FLAG_DNA_DUAL_WRITE=true`): new writes to legacy + DNA.
2) Read shadow (`FLAG_DNA_READ_SHADOW=true`): reads from legacy, compare with DNA, log drift.
3) Cutover (`FLAG_DNA_CUTOVER_READ_FROM=dna`): primary reads from DNA; keep shadow for a week.
4) Decommission: turn off legacy writes; archive legacy data.

## Backfill
```bash
python scripts/migrate_memory_to_dna.py      # resume-safe, checkpointed
cat .lukhas_migration/checkpoint.json
```

## Rollback
- Flip `FLAG_DNA_CUTOVER_READ_FROM=legacy`
- Keep dual-write enabled until stability confirmed
- Investigate drift via `/dna/compare?key=...`

---

## Acceptance criteria
- No behavioral change until flags are toggled
- `write_memory_dual` writes legacy only by default; writes both when `FLAG_DNA_DUAL_WRITE=true`
- Backfill script runs, creates `.lukhas_migration/checkpoint.json`, and resumes
- `read_memory` honors `DNA_CUTOVER_READ_FROM` and logs drift when `DNA_READ_SHADOW=true`
- `/dna/health` returns counts; `/dna/compare?key=...` shows both sides
- Tests pass in CI
