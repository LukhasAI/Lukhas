Title: refactor(e741-tests): disambiguate single-letter identifiers in tests

Summary:
- Fixes E741 in the tests subsystem after moves.
- Renames contextual single-letter identifiers.

Verification:
- `ruff check --select E741 tests/`
- `pytest tests -q`

Checklist:
- [ ] E741 fixed or justified with # noqa
- [ ] tests pass locally & CI
- [ ] fixtures preserved or compatibility shim added
