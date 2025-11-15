# Dependency Management

This document outlines the strategy for managing dependencies in the Lukhas project.

## Automated Dependency Updates

We use Dependabot to keep our dependencies up-to-date. The configuration is located in `.github/dependabot.yml`.

- **Pip dependencies**: Checked weekly for updates.
- **GitHub Actions**: Checked monthly for updates.

Dependabot automatically creates pull requests for any outdated dependencies. These pull requests are then reviewed and merged by the development team.

## Dependency Vulnerability Scanning

We use `pip-audit` to scan our Python dependencies for known vulnerabilities. This is performed by the `dependency-check.yml` workflow in `.github/workflows`.

The workflow is configured to:
- Run on every pull request against the `main` and `develop` branches.
- Block pull requests that contain dependencies with critical vulnerabilities.
- Timeout after 15 minutes.

This proactive approach helps us to identify and mitigate security risks before they are introduced into the codebase.
