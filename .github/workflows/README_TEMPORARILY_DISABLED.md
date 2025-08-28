# 🚫 GitHub Actions Temporarily Disabled

**Date**: August 28, 2025
**Reason**: Cost optimization - preventing excessive GitHub Actions usage

## Status

All GitHub Actions workflows have been temporarily moved to `workflows-disabled/` directory to stop automatic execution and reduce costs.

**Disabled Workflows**: 35 workflow files
**Location**: `.github/workflows-disabled/`

## Re-enabling Instructions

When ready to re-enable GitHub Actions:

```bash
# Move all workflows back to active directory
mv .github/workflows-disabled/*.yml .github/workflows/
mv .github/workflows-disabled/.env.secrets .github/workflows/

# Remove this disable directory
rmdir .github/workflows-disabled/
```

## Disabled Workflows Include

- CI/CD pipelines (ci.yml, ci-enhanced.yml)
- Security audits and validation
- Quality checks and linting
- Identity and authentication tests
- LUKHAS validation pipeline
- Dependency audits
- Release workflows
- And many more automated checks

## Cost Impact

This temporary disabling prevents:
- Automatic runs on every push/pull request
- Scheduled workflow executions
- Workflow dispatches and triggers
- Associated compute costs

## Re-activation

Remove this file and move workflows back when ready to resume automated actions.

---

*Temporary measure for cost control*
*All workflows preserved and ready for re-activation*
