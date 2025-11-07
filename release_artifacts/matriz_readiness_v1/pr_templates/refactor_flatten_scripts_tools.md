Title: refactor(flatten-scripts-tools): move scripts/tools to flattened modules

Summary:
- Move selected scripts/tools modules to flattened top-level modules
- Use AST rewrite to update imports

Verification:
- `python3 -m compileall .`
- `ruff check --select E,F --statistics .`
- `pytest -q -k "smoke or tools"`

Checklist:
- [ ] compile & ruff OK
- [ ] smoke tests OK
- [ ] PR limited in scope (< 15 files)
