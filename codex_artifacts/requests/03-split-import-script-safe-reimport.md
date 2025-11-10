# Split import script & safe reimport

## Context

- Repo: Lukhas/Lukhas
- Label: codex:review
- PR: draft, assign Jules steward
- Branch: codex/split-import-script-safe-reimport

## Requirements

- Add `scripts/split_labot_import.sh` as earlier provided.
- Add a `--dry-run` that shows PR titles & branch names.

## Checks

- Run ruff and mypy on changed files
- Add/adjust tests where behavior changes
- Keep patches focused and small
