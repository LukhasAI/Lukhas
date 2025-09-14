This directory is reserved for known flaky tests.

Policy:
- Use `@pytest.mark.flaky` on tests placed here only.
- New flaky tests are not allowed elsewhere; CI will fail if detected.
- Track ownership and SLA in the test docstring or a linked issue.
