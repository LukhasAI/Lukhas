# OPA policy + CI integration

## Context

- Repo: Lukhas/Lukhas
- Label: codex:review
- PR: draft, assign Jules steward
- Branch: codex/opa-policy-ci-integration

## Requirements

- Add `.policy/rules.rego` enforcing:
- forbid `except:` with no exception types
- forbids test deletion
- forbids removing invariants
- Add `opa eval` step to `labot_audit.yml`

## Prompt

```
Add .policy/rules.rego with rules forbidding broad except and test deletion. Modify .github/workflows/labot_audit.yml to run 'opa eval' and fail if rules violated.
```

## Checks

- Run ruff and mypy on changed files
- Add/adjust tests where behavior changes
- Keep patches focused and small
