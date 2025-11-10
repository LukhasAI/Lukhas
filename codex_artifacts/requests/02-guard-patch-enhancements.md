# Guard_patch enhancements

## Context

- Repo: Lukhas/Lukhas
- Label: codex:review
- PR: draft, assign Jules steward
- Branch: codex/guard-patch-enhancements

## Requirements

- Add YAML/OPA policy integration (optional): create `.policy/rules.rego` and a `tools/check_policy.py` to evaluate.
- Add a `--allow-large-imports` toggle for a whitelist during controlled imports.

## Prompt

```
Extend tools/guard_patch.py to accept a --whitelist-file path; if present, files listed there are exempt from max-files/max-lines checks. Add tests for the new behavior.
```

## Checks

- Run ruff and mypy on changed files
- Add/adjust tests where behavior changes
- Keep patches focused and small
