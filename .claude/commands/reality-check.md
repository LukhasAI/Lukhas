# /reality-check
Run reality tests only (no mocks, golden):
- pytest tests/test_imports.py tests/test_integration.py tests/golden/ -q
- Print created files under tmp_path in golden tests.
