# Make labot PRs draft by default

## Context

- Repo: Lukhas/Lukhas
- Label: codex:review
- PR: draft, assign Jules steward
- Branch: codex/make-labot-prs-draft-by-default

## Requirements

- File: `tools/labot.py` → function `open_pr_shell`
- Change `gh pr create` → `gh pr create --draft`
- Add `labels: ["labot"]` when creating PRs
- Add `--assume-yes` flag option for dry-run

## Prompt

```
Modify tools/labot.py: update open_pr_shell() to create DRAFT PRs with labels ["labot"], and add a --dry-run option that prints the gh command instead of executing it. Ensure ruff/mypy pass.
```

## Checks

- Run ruff and mypy on changed files
- Add/adjust tests where behavior changes
- Keep patches focused and small
