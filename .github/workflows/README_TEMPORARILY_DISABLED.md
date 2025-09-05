# Workflow Archive Policy

Most workflows in `.github/workflows-disabled/` are parked/archived to prevent CI drift and noise. To re-enable a workflow:

1. Move the file from `.github/workflows-disabled/` to `.github/workflows/`.
2. Ensure the workflow has correct path filters and triggers (see active lane-local workflows for examples).
3. Prefix archived files with `zzz-` for clarity if desired.

Active workflows:
- PR: `ci.yml`, `python-lint.yml`, `logging-tag-guard.yml` (lane-local, robust)
- Scheduled: `security-scan.yml`, `dependency-audit.yml` (weekly)

All others remain disabled until explicitly needed for ops, DR, or hygiene.
