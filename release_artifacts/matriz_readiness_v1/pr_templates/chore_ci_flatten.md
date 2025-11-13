Title: chore(ci): prepare CI + pre-commit for flattening

Summary:
- Update `pyproject.toml` `tool.ruff.src` and `target-version` as needed.
- Add/update `.pre-commit-config.yaml` with Black and Ruff hooks.

Verification:
- CI run: ruff + black checks pass on branch
- pre-commit runs locally with no failures

Checklist:
- [ ] pyproject updated
- [ ] pre-commit config committed
- [ ] CI job triggered & green
