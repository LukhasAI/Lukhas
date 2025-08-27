# /deep-search-prepare
You are operating in ~/Lukhas. Prepare the repo so an external GitHub-connected auditor (ChatGPT Pro) can run a one-shot deep search efficiently and produce high-signal artifacts. Do NOT perform risky refactors.

## Objectives
- Ensure the lane source of truth exists: ops/matriz.yaml.
- Create all directories and placeholder artifacts the auditor will expect.
- Generate light-weight indexes (no large compute).
- Add minimal smoke tests (1 per lane).
- Produce a short audit README that explains where everything is.

## Steps (don’t skip)
1) Ensure directory structure:
   - Create (if missing): reports/deep_search/, lanes/, ops/
2) Ensure MATRIZ file:
   - If ops/matriz.yaml is missing, create a minimal schema with 7 lanes:
     lane, owner, dirs[], deps[]
   - Validate that each listed dir exists; if not, create empty placeholder dirs and note them in reports/deep_search/missing_dirs.txt
3) Indexes for the auditor:
   - Write reports/deep_search/FILE_INDEX.txt with a recursive file list (paths only).
   - Write reports/deep_search/PY_INDEX.txt listing all *.py files.
   - Write reports/deep_search/IMPORT_SAMPLES.txt containing the first 3 lines of every *.py file that include “import ” or “from ” (one line per hit, prefixed by path:lineno).
4) Import sanity quick-pass:
   - Search for “from core.” and write all hits to reports/deep_search/WRONG_CORE_IMPORTS.txt
   - Search for “from candidate.” inside lukhas/** and write hits to reports/deep_search/CANDIDATE_USED_BY_LUKHAS.txt
5) Smoke tests (one per lane):
   - For each lane in ops/matriz.yaml, create tests/smoke/test_<lane>_smoke.py that does the lightest possible import from one lane module (or a shim if needed). Keep it tiny.
   - Execute: pytest -q tests/smoke (don’t fail the run; capture output into reports/deep_search/SMOKE_RESULTS.txt)
6) Documentation breadcrumbs:
   - Create reports/deep_search/README_FOR_AUDITOR.md that explains:
     - Where ops/matriz.yaml lives and what “lanes” mean here.
     - Where indexes and precomputed lists live (the files created above).
     - Any known hot spots (if WRONG_CORE_IMPORTS or CANDIDATE_USED_BY_LUKHAS are non-empty).
7) Output:
   - Render a short summary in chat with checkboxes:
     - [ ] ops/matriz.yaml present
     - [ ] directories created
     - [ ] indexes written
     - [ ] smoke tests created
     - [ ] smoke results captured
     - [ ] auditor README written
8) Ask before writing any non-trivial code; for placeholders and test skeletons, proceed.

## Tools allowed
Read, Glob, Grep, Write, Edit, Bash, Python, Sub-agents (one sub-agent per lane while creating smoke tests).

## Acceptance criteria
- No risky edits; no renames.
- All artifact files exist and are non-empty where applicable.
- Pytest smoke tests run and produce SMOKE_RESULTS.txt.
- A human (auditor) can open reports/deep_search/README_FOR_AUDITOR.md and understand the layout in under 60 seconds.
