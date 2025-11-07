Title: refactor(flatten-benchmarks): physical flatten small benchmark set

Summary:
- Moved 3 small benchmark modules to top-level flattened modules.
- Updated imports across repo using AST-based rewrite (scripts/rewrite_imports_libcst.py).
- Verified compile and bench tests.

Verification:
- `python3 -m compileall .`
- `ruff check --select E,F --statistics`
- `pytest -q -k "benchmark or matriz"`

Checklist:
- [ ] ruff E/F no failures
- [ ] compile OK
- [ ] benchmark tests pass
- [ ] PR diff < 10 files
