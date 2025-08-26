# /promote-module
Promote a single module from candidate → lukhas using the lane process.
USAGE: `/promote-module module=orchestration owner=Jules01`

## Inputs
- `module` (required): subdir under `candidate/core/` to promote (e.g., `orchestration`, `glyph`)
- `owner`  (optional): lane owner (e.g., `Jules01`). If omitted, read from ops/matriz.yaml.

## Principles
- Promote **one** module per run.
- No structural reshuffles.
- Write minimal **shims** only when downstream still imports candidate path.
- Run smoke tests **before and after**.
- Ask before writing nontrivial edits.

## Steps (do not skip)
1) **Sanity checks**
   - Verify `candidate/core/<module>` exists.
   - Refuse if `lukhas/core/<module>` already exists unless user confirms “update/overwrite?”.
   - Parse `ops/matriz.yaml` → lanes, owner mapping. If `owner` provided, use it.

2) **Pre-promotion smoke test (candidate)**
   - Create (or refresh) `tests/smoke/test_<module>_candidate_smoke.py`:
     ```python
     def test_<module>_import_candidate():
         import candidate.core.<module> as m
         assert hasattr(m, "__file__")
     ```
   - Run: `pytest -q tests/smoke/test_<module>_candidate_smoke.py | tee reports/deep_search/SMOKE_<module>_candidate.txt`
   - If import fails, STOP and summarize blockers.

3) **Copy (no delete)**
   - Copy tree: `candidate/core/<module>` → `lukhas/core/<module>`
   - In copied files, update **internal imports** that referred to core modules:
     - Replace `from core.` → `from lukhas.core.`
     - Replace `import core.` → `import lukhas.core.`
   - Do **not** change third-party imports.

4) **Temporary shim (only if needed)**
   - If scans show that other code still imports `candidate.core.<module>`, create a shim at:
     `lukhas/core/<module>_shim.py` with:
     ```python
     # TEMP SHIM — remove post-promotion
     from candidate.core.<module> import *  # noqa: F401,F403
     ```
   - Do not mass-rewrite downstream yet; the shim keeps them functional during phased promotion.

5) **Post-promotion smoke test (lukhas)**
   - Generate `tests/smoke/test_<module>_lukhas_smoke.py`:
     ```python
     def test_<module>_import_lukhas():
         import lukhas.core.<module> as m
         assert hasattr(m, "__file__")
     ```
   - Run: `pytest -q tests/smoke/test_<module>_lukhas_smoke.py | tee reports/deep_search/SMOKE_<module>_lukhas.txt`
   - If fail, show precise diffs and import errors; ask before applying minimal path fixes.

6) **Ops + docs updates**
   - Append/ensure lane entry in `ops/matriz.yaml` for this module’s paths.
   - Update / create `lanes/<module>/README.md` with:
     - Scope, Non-goals, Interfaces, Risks, Test plan (1-2 smoke tests listed).
   - Update `MATRIZ_PLAN.md` (Promotion Decisions section) with:
     - `<module>: promoted`, date, owner, shim present? (Y/N)

7) **Commit plan (ask to confirm)**
   - If approved, stage files and commit:
     ```
     chore(promotion): promote core/<module> from candidate → lukhas

     - Created lukhas/core/<module>/*
     - Updated imports: core.* → lukhas.core.*
     - Added shim (temporary): lukhas/core/<module>_shim.py  (if present)
     - Smoke: candidate + lukhas passed (see reports/deep_search/SMOKE_<module>_*.txt)
     - MATRIZ + lane docs updated
     ```
   - Do **not** delete `candidate/core/<module>`.

8) **Summary output**
   - Print a compact table:
     | Module   | Owner   | Shim | Candidate Smoke | Lukhas Smoke | Next Step                |
     | -------- | ------- | ---- | --------------- | ------------ | ------------------------ |
     | <module> | <owner> | Y/N  | pass/fail       | pass/fail    | promote next dep: <name> |

## Tools allowed
Read, Glob, Grep, Write, Edit, Bash, Python, Sub-agents (isolated context for tests)

## Acceptance criteria
- Both smoke tests pass.
- Imports updated only within promoted files.
- ops/matriz.yaml + lane README updated.
- No deletion under candidate/.
- Clear summary & reversible commit.
