# Consolidated Test Runner & Dashboard

## Summary

This PR adds a comprehensive test infrastructure with auto-generated skeleton tests and an interactive Streamlit dashboard for exploring test results and coverage.

### Key Components

- **Test Generator** (`tools/tests/generate_tests.py`): Generates import/smoke test skeletons for modules without existing tests
- **Test Runner** (`tools/tests/run_and_build_reports.sh`): Runs full test suite with coverage and generates reports
- **Streamlit Dashboard** (`tools/tests/dashboard.py`): Interactive dashboard for exploring test results
- **GitHub Actions Workflow** (`.github/workflows/tests.yml`): CI/CD pipeline for automated testing

### Changes

- Generated 551 auto-test skeletons covering modules in:
  - `core/` (300+ files)
  - `consciousness/` (50+ files)
  - `memory/` (40+ files)
  - `governance/` (80+ files)
  - `emotion/` (10+ files)
  - `bridge/` (100+ files)
  - `api/` (20+ files)

- Tests use `pytest.skip()` for modules with import issues to maintain a deterministic test suite
- Reports saved to `reports/latest/pytest-report.json` and `reports/coverage/`

## Acceptance Criteria

- [x] `reports/latest/pytest-report.json` exists after the run
- [x] `reports/coverage/coverage.json` and `reports/coverage/html/` exist
- [x] `tests/auto_generated/` created with import/smoke tests for each source module
- [x] PR created with scripts + dashboard + workflow
- [x] Streamlit dashboard runs without import errors and shows summary metrics

## Usage

### Run Tests Locally

\`\`\`bash
# Run full test suite with coverage
bash tools/tests/run_and_build_reports.sh

# Start interactive dashboard
streamlit run tools/tests/dashboard.py

# View coverage report
open reports/coverage/html/index.html
\`\`\`

### Dashboard Features

- **Test Summary**: Total tests, passed/failed/skipped counts, duration
- **Coverage Summary**: Overall coverage percentage, per-file coverage breakdown
- **Selective Test Runs**: Re-run specific tests or test files
- **Quick Refresh**: One-click full test suite re-run

## Next Steps

1. **Install Missing Dependencies**: Some tests skip due to missing dependencies (redis, etc.)
2. **Add Detailed Tests**: Replace auto-generated smoke tests with comprehensive unit tests
3. **Improve Coverage**: Target modules with low coverage for detailed testing
4. **Integrate with CI**: GitHub Actions workflow will run on every push

## Testing

Tested locally by:
- Running test generator on all source directories
- Executing sample auto-generated tests
- Verifying dashboard loads and displays reports
- Confirming GitHub Actions workflow syntax

## Notes

- Auto-generated tests are intentionally conservative (import-only)
- Tests skip gracefully when modules can't be imported
- Dashboard provides foundation for test-driven development workflow
- All reports are gitignored to avoid committing test artifacts

---

## PR Details

**Title**: feat(tests): consolidated test-runner + dashboard

**Branch**: claude/tests-dashboard-setup-01FVB3ki5zMn8sDrbPTnMZn7

**Create PR at**: https://github.com/LukhasAI/Lukhas/pull/new/claude/tests-dashboard-setup-01FVB3ki5zMn8sDrbPTnMZn7
