# Coverage Runbook

This document provides instructions for managing code coverage in the LUKHAS project.

## Codecov Integration

Code coverage is reported to [Codecov](https://codecov.io/gh/LukhasAI/Lukhas). Integration is handled by the `.github/workflows/coverage.yml` workflow.

### Configuration

- The Codecov GitHub App must be installed and configured for the `LukhasAI/Lukhas` repository.
- A `CODECOV_TOKEN` secret must be set in the repository's GitHub Secrets. This token is used to authenticate with the Codecov API.

## Updating Coverage Thresholds

Per-module coverage thresholds are defined in `config/coverage_thresholds.yml`. To update a threshold, simply edit the value for the corresponding module in this file.

```yaml
lukhas/: 75
core/: 75
matriz/: 80
candidate/: 30
tests/: 90
```

The `scripts/ci/check_coverage.py` script uses this file to enforce the thresholds during CI builds.

## Running Coverage Locally

To run the coverage checks locally, first run `pytest` with the `--cov` flag:

```bash
pytest --cov=. --cov-report=xml
```

This will generate a `coverage.xml` file. Then, run the `check_coverage.py` script:

```bash
python3 scripts/ci/check_coverage.py --coverage-xml coverage.xml --thresholds config/coverage_thresholds.yml
```

## Debugging Coverage Failures

If a coverage check fails in a pull request, you can debug it locally:

1.  Check out the pull request branch.
2.  Run the coverage commands listed above.
3.  The output of `check_coverage.py` will show which modules are below the required threshold.
4.  To see a detailed HTML report of the coverage, run:

    ```bash
    pytest --cov=. --cov-report=html
    ```

    Then open `htmlcov/index.html` in your browser. This will show you which lines of code are not covered by tests.
