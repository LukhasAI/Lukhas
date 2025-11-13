# DAST / EQNOX wiring tasks

## Context

- Repo: Lukhas/Lukhas
- Label: codex:review
- PR: draft, assign Jules steward
- Branch: codex/dast-eqnox-wiring-tasks

## Requirements

- Add small adapter modules that standardize messaging between `dast.or.py` orchestrator and MATRIZ. Create a `lukhas/adapters/dast_adapter.py` with typed interfaces and tests.
- Add integration tests that use dependency overrides to simulate the orchestrator.

## Prompt

```
Create lukhas/adapters/dast_adapter.py implementing a simple typed interface: send_task(task: dict) -> dict. Add unit tests with mocked responses. Add an ADR describing the interface.
```

## Checks

- Run ruff and mypy on changed files
- Add/adjust tests where behavior changes
- Keep patches focused and small
