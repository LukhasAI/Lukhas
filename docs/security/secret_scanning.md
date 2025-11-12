# Secret Scanning

This document describes the secret scanning process used in this repository.

## Gitleaks

We use [gitleaks](https://github.com/gitleaks/gitleaks) to scan for secrets in our codebase. Gitleaks is a SAST tool for detecting hardcoded secrets like passwords, API keys, and tokens in git repos.

## Workflow

The secret scanning workflow is defined in `.github/workflows/secret-scan.yml`. It runs on every pull request and on a nightly schedule.

The workflow will:
1.  Check out the code.
2.  Run the gitleaks action.
3.  Fail the build if any secrets are found.

The gitleaks configuration is defined in `.gitleaks.toml` in the root of the repository.
