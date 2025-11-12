# OpenAPI drift deeper check

## Context

- Repo: Lukhas/Lukhas
- Label: codex:review
- PR: draft, assign Jules steward
- Branch: codex/openapi-drift-deeper-check

## Requirements

- Replace the stub `tools/check_openapi_drift.py` with a deep-differ that reports path/method/response schema differences and an optional `--autofix` to update saved `openapi.json` after steward confirmation.

## Prompt

```
Improve tools/check_openapi_drift.py to perform deep JSON Schema diff for paths and responses, and output a machine-readable summary. Add tests for the diffing logic.
```

## Checks

- Run ruff and mypy on changed files
- Add/adjust tests where behavior changes
- Keep patches focused and small

## Status

- ❗️ PR #1375 is being used for a different task (issue #1249: DAST/EQNOX wiring).
- ✅ OpenAPI drift detection (issue #1250) will proceed on branch `codex/openapi-drift-deeper-check` with a new PR to be filed.
- ⏳ No Codex PR number yet; the next update will include the draft link once it is created.
