# Priority TODOs (T4 / 0.01%) — Agent-friendly

P1 (Critical - 2-4w)
1. Codemod: replace labs ImportFrom nodes (scripts/codemods/replace_labs_with_provider.py). Operator: Codex.
2. SLSA CI for first 10 modules (github workflow + cosign/in-toto). Owner: Security + Codex.
3. Autofix pass: autoflake/isort/black then ruff --fix (small batches). Owner: Claude Code + Codex.

P2 (Important - 1m)
4. Coverage: pytest-cov + codecov integration. Owner: Ops.
5. WaveC snapshot sign/verify + API. Owner: Core.

P3 (Enhancement - 3mo)
6. Decision explainability API (core/explainability). Owner: Research.
7. Endocrine contract + telemetry. Owner: Ops.

Agent task templates
- Each template includes: branch name, single-file change template, tests, run commands, PR template, lane-guard run artifact attach.
