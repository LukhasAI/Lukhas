# Brief: Lane-Guard Sync (import-health + import-linter) — origin/main

## Purpose
Run import-health and the repo lane-guard (import-linter) against `origin/main` in an isolated git worktree and venv, fix root/package mismatch if needed (local-only), capture artifacts and logs, revert local edits, and produce a short report. **Do not push or commit changes.**

## Environment
- Repo root (original): `/Users/agi_dev/LOCAL-REPOS/Lukhas`
- Worktree path: `/Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/sync-origin-main`
- Venv (worktree-local): `.venv_temp` (symlinked to `.venv` for Makefile)
- Make target: `make lane-guard` (invokes `.venv/bin/lint-imports --config .importlinter`)
- Import health script: `scripts/consolidation/check_import_health.py`

## Safety & Rules
- Only operate in the isolated worktree (do not change the main checkout).
- Do not commit/push any changes. All edits are local only and must be reverted before exit.
- Prefer minimal installs for missing dependencies (pydantic, streamlit, etc.) before trying `pip install -e .`.
- Revert `.importlinter` to HEAD copy after local edits.

## Steps (ordered)
1. `git fetch origin --prune`
2. `git worktree add /Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/sync-origin-main origin/main` (create if missing)
3. `cd /Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/sync-origin-main`
4. Create venv: `python3 -m venv .venv_temp`
5. `.venv_temp/bin/python -m pip install --upgrade pip`
6. `.venv_temp/bin/python -m pip install import-linter`
7. If `requirements-dev.txt` exists: `.venv_temp/bin/python -m pip install -r /Users/agi_dev/LOCAL-REPOS/Lukhas/requirements-dev.txt` (or conservative installs of pydantic & streamlit as needed)
8. Symlink: `ln -sfn .venv_temp .venv`
9. Run import-health:
```
PYTHONPATH=. .venv_temp/bin/python scripts/consolidation/check_import_health.py --verbose 2>&1 | tee artifacts/import_health_worktree.log
```
If ImportError: install missing packages into `.venv_temp` and re-run.
10. Run lane-guard via Makefile:
```
make lane-guard 2>&1 | tee artifacts/lane_guard_make_original.log
```
11. If the linter fails due to root/package mismatch:
 - Preferred local edit path:
   - `cp .importlinter .importlinter.bak`
   - Edit `.importlinter` to align `root_packages` with actual top-level module names (e.g., change `matriz` → `MATRIZ` if needed)
   - `make lane-guard 2>&1 | tee artifacts/lane_guard_run_localfix.log`
   - Revert: `git restore --source=HEAD -- .importlinter` and `rm -f .importlinter.bak`
 - Alternative: create `artifacts/importlinter_override.toml` and run:
```
.venv_temp/bin/lint-imports --config artifacts/importlinter_override.toml --verbose 2>&1 | tee artifacts/import_lint_override.log
```
12. Collect artifacts:
 - `artifacts/import_health_worktree.log`
 - `artifacts/venv_install.log` (pip install logs)
 - `artifacts/lane_guard_run_localfix.log`
 - optionally `artifacts/import_lint_override.log`
13. Cleanup and revert:
 - `git restore --source=HEAD -- .importlinter`
 - `rm -rf .venv .venv_temp`
 - Remove generated override files
14. Report: Summarize `git log HEAD..origin/main --oneline` and include lane-guard status: `Contracts: X kept, Y broken` and failing chains.

## Expected outputs (artifacts)
- artifacts/import_health_worktree.log
- artifacts/venv_install.log
- artifacts/lane_guard_run_localfix.log
- artifacts/import_lint_override.log (if used)
- Short summary report (text)

## Notes
- If `pip install -e .` is required, warn that it may install large deps; prefer targeted installs first.
- If multiple root packages exist, ensure they are importable or use the override config.
- Do not create PRs or push any changes without explicit permission.

END
