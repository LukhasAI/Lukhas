# Dream Validation Gate

This document outlines the "Dream Validation" GitHub Actions workflow, which serves as a PR gate to ensure the stability of the system's dream synthesis capabilities.

## Workflow Overview

The workflow is defined in `.github/workflows/dream-validate.yml` and is triggered on every pull request targeting the `main` or `develop` branches.

### Purpose

The primary purpose of this gate is to prevent regressions in the dream generation logic. It does this by running a validation script that measures the "drift" between the generated dreams and a set of baseline prompts.

### Key Details

- **Timeout:** The job has a 10-minute timeout.
- **Concurrency:** The workflow uses a concurrency group to cancel any in-progress runs on the same branch when a new commit is pushed. This saves resources by ensuring only the latest code is being tested.
- **Validation Script:** The core of the workflow is the `scripts/dream_validate_pr.py` script.
- **Drift Threshold:** The workflow will fail if the measured drift exceeds a threshold of `0.15`. This indicates a significant and potentially undesirable change in the dream synthesis output.

## How it Works

1.  The workflow checks out the PR code.
2.  It installs the necessary Python dependencies.
3.  It runs the `dream_validate_pr.py` script, passing in the baseline prompts and the maximum allowed drift.
4.  The script runs the dream validation and outputs the calculated drift.
5.  If the drift is above the threshold, the script exits with an error code, causing the workflow to fail and block the PR from being merged.
