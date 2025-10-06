---
status: wip
type: documentation
---
You are acting as a lane promotion engineer for the Lukhas repo.
PROMPT NAME: T4-LanePromotion (candidate → lukhas, single module)

GOAL
Promote exactly one module from candidate/core/<module> to lukhas/core/<module>, with smoke tests before/after, import path updates inside promoted files only, and a temporary shim IF other code still imports the candidate path. Never bulk copy. Never delete candidate code.

INPUTS (fill these before running):
- MODULE = <orchestration|glyph|integration|api|neural|interfaces|monitoring|symbolic>
- OWNER  = <Jules01..Jules07 or leave blank to skip>

RULES
- One module per PR.
- No structural moves beyond candidate/core/<MODULE> → lukhas/core/<MODULE>.
- Do not rename packages.
- Update imports inside promoted files:
  - from core.X → from lukhas.core.X
  - import core.X → import lukhas.core.X
- If any import still uses candidate.core.MODULE elsewhere, add a TEMP SHIM:
  lukhas/core/<MODULE>_shim.py that re-exports from candidate.core.<MODULE>.
- Add/refresh two smoke tests:
  - tests/smoke/test_<MODULE>_candidate_smoke.py (imports candidate path)
  - tests/smoke/test_<MODULE>_lukhas_smoke.py   (imports lukhas path)
- Update artifacts:
  - ops/matriz.yaml: ensure the lane and dirs are listed
  - lanes/<MODULE>/README.md: Scope, Non-goals, Interfaces, Risks, Test plan
  - MATRIZ_PLAN.md Promotion Decisions: mark <MODULE> promoted, date, owner, shim Y/N
- CI must pass the “reality” tests first (no-mock import/integration/golden) before merging.

PROCEDURE
1) Validate existence of candidate/core/<MODULE>.
2) Generate candidate smoke test; run: pytest -q tests/smoke/test_<MODULE>_candidate_smoke.py
   - If fail: stop and print exact errors; propose smallest import fixes inside candidate module (ASK before editing).
3) Copy tree (no delete): candidate/core/<MODULE> → lukhas/core/<MODULE>.
4) Update imports in promoted files only: core. → lukhas.core.
5) Scan for repo imports of candidate.core.<MODULE>. If any found:
   - Create lukhas/core/<MODULE>_shim.py that re-exports candidate.core.<MODULE>.
6) Generate lukhas smoke test; run: pytest -q tests/smoke/test_<MODULE>_lukhas_smoke.py
   - If fail: print errors; propose minimal fixes (ASK before editing).
7) Update ops/matriz.yaml lanes & deps; create/refresh lanes/<MODULE>/README.md.
8) Append MATRIZ_PLAN.md Promotion Decisions with this promotion details.
9) Create a new branch: chore/promo-core-<MODULE>
10) Commit with message:
    chore(promotion): promote core/<MODULE> from candidate → lukhas
    - Imports updated inside promoted files
    - TEMP shim added: <Y/N>
    - Smoke passed: candidate + lukhas (see reports)
    - MATRIZ + lane docs updated
11) Open PR with title:
    “Promote core/<MODULE> (candidate → lukhas) — smoke-tested, shim=<Y/N>”
    Include a checklist:
      [ ] Candidate smoke green
      [ ] Lukhas smoke green
      [ ] Shim present only if needed
      [ ] ops/matriz.yaml updated
      [ ] lanes/<MODULE>/README.md updated
      [ ] MATRIZ_PLAN.md updated
      [ ] No bulk moves; no deletes under candidate/
12) Print a compact summary table in chat:
    | Module | Owner | Shim | Candidate Smoke | Lukhas Smoke | Next Dep |
    | ------ | ----- | ---- | --------------- | ------------ | -------- |

OUTPUT
- One PR touching only: lukhas/core/<MODULE>/**, tests/smoke/*<MODULE>*.py, ops/matriz.yaml, lanes/<MODULE>/README.md, MATRIZ_PLAN.md, and optional lukhas/core/<MODULE>_shim.py
- All changes justified in PR description with the checklist above.

STOP CONDITIONS
- Candidate smoke fails and user declines the proposed minimal fix.
- Import update would affect non-promoted files.
- User denies adding a TEMP shim when downstream still imports candidate.

SECURITY / SAFETY
- Do not edit tests to “make them pass” except the two smoke files explicitly listed.
- Never delete candidate sources.
- Never mass-search-replace beyond promoted files.
