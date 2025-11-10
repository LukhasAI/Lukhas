# Steward Process

This document outlines the governance process for stewards of the LUKHAS repository.

## Two-Key Rule

All changes to protected branches must be approved by at least two stewards before merging. This ensures that no single steward can make a change without a review from another steward.

## Steward Rotation

Stewards are rotated on a weekly basis. The rotation is managed in the `STEWARD_ROTATION.md` file.

## Patch Sizes

Patches should be small and focused. Large changes should be broken down into smaller, more manageable patches. As a general rule, a patch should not exceed 40 lines of code and 2 files.

## Canary Checklist

Before deploying a change to production, a canary release should be performed. The following checklist should be used to ensure a safe canary release:

- [ ] The change has been deployed to a staging environment.
- [ ] The change has been tested in the staging environment.
- [ ] The change has been monitored in the staging environment for at least 24 hours.
- [ ] The change has been approved by at least two stewards.

## Rollback Automation

In the event of a failed deployment, an automated rollback process should be in place. The rollback process should be triggered automatically if the deployment fails to meet the defined health checks.
