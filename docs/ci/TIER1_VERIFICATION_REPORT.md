# Tier 1 CI Workflow Verification Report

**Date:** 2025-11-12
**Author:** Jules

## 1. Summary

This report verifies the status of required Tier 1 CI workflows as defined in task T20251112040. The verification was performed by analyzing the GitHub Actions workflow configurations located in the `.github/workflows/` directory.

## 2. Workflow Verification Status

The following table summarizes the findings for each required Tier 1 workflow.

| Workflow | Status | Implementation Details |
|---|---|---|
| `lint-static` | ✅ **Active** | Implemented as the `lint` job in `ci.yml`. It runs `ruff`, `mypy`, `black`, and `isort` for static analysis and linting. |
| `unit-fast` | ✅ **Active** | Implemented as the `test` job in `ci.yml`. It runs the full unit test suite using `pytest`. A specific `-fast` variant was not found, but this job serves the purpose of unit testing. |
| `smoke-fast` | ✅ **Active** | Implemented as the `matrix-v3-sandbox` job in `ci.yml`. This job includes a step named "Matrix v3 smoke tests" which runs `pytest tests/test_provenance_smoke.py`. |
| `qrg-check` | ❌ **Not Found** | No workflow, job, or script matching `qrg-check` was found in the codebase or CI configurations. |
| `pre-commit` | ✅ **Active** | Implemented as the `pre-commit` job in `ci.yml`. It uses `pre-commit` to run checks on changed files. |
| `import-lanes` | ✅ **Active** | Implemented as the `lane-guard` job in `ci.yml`. This job's purpose is to "Enforce no candidate imports in lukhas," which aligns with the concept of import lane enforcement. |
| `pr-size` | ❌ **Not Found** | No workflow or action for checking Pull Request size was found in the CI configurations. |

## 3. Concurrency and Retention Settings

### Concurrency

- **`coverage-gates.yml`**: This workflow defines a concurrency group (`coverage-${{ github.ref }}-${{ github.workflow }}`) that cancels in-progress jobs on the same branch when a new run is triggered. This prevents redundant checks on the same PR.
- **Other Workflows**: No other workflows (`ci.yml`, `codeql-analysis.yml`, etc.) have explicit concurrency controls defined. They will use the GitHub Actions default behavior, which is to run concurrently without cancellation.

### Retention Policy

- **`coverage-gates.yml`**: The `upload-artifact` step in this workflow specifies a `retention-days` of **30**.
- **Other Workflows**: No other workflows specify artifact retention policies. They will use the default retention period for the repository, which is typically 90 days for public repositories and configurable for private ones.

## 4. Recommendations

- **Implement Missing Checks**: Consider adding the `qrg-check` and `pr-size` workflows to the CI pipeline to improve code quality and review efficiency.
- **Explicit Concurrency**: To optimize resource usage, consider adding `concurrency` groups with `cancel-in-progress: true` to the main `ci.yml` workflow for pull request triggers.
