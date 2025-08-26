# /anti-fake-tests
1) pre-commit run --all-files
2) pytest tests/test_imports.py tests/test_integration.py -q
3) pytest tests/golden/ -q
4) tools/ci/verify_diff_coverage.sh
Exit non-zero on any failure.
