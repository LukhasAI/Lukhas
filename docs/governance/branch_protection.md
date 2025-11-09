# Branch Protection Configuration Guide

This document provides comprehensive guidance on configuring branch protection rules for the Lukhas AI repository using the GitHub CLI (`gh`).

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Branch Protection Rules](#branch-protection-rules)
- [Required Status Checks](#required-status-checks)
- [Code Owner Review Requirements](#code-owner-review-requirements)
- [Benefits](#benefits)
- [Troubleshooting](#troubleshooting)

## Overview

Branch protection rules enforce code quality standards, ensure proper review processes, and protect critical branches from accidental or unauthorized changes. This guide uses the `gh` CLI tool to configure these rules programmatically.

## Prerequisites

Before configuring branch protection rules, ensure you have:

1. GitHub CLI installed and authenticated:
   ```bash
   gh --version
   gh auth status
   ```

2. Admin or maintain permissions on the repository

3. The repository name and organization/user:
   ```bash
   REPO_OWNER="your-org-or-username"
   REPO_NAME="Lukhas"
   ```

## Branch Protection Rules

### Protecting the Main Branch

Configure comprehensive protection for the `main` branch:

```bash
# Enable branch protection on main with core rules
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":[]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"dismissal_restrictions":{},"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":2}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

### Breaking Down the Protection Settings

#### 1. Require Pull Request Reviews

```bash
# Require 2 approving reviews with code owner approval
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_pull_request_reviews \
  --method PATCH \
  --field dismiss_stale_reviews=true \
  --field require_code_owner_reviews=true \
  --field required_approving_review_count=2 \
  --field require_last_push_approval=false
```

**Settings explained:**
- `dismiss_stale_reviews`: Automatically dismiss approvals when new commits are pushed
- `require_code_owner_reviews`: Require approval from code owners (defined in CODEOWNERS)
- `required_approving_review_count`: Minimum number of approving reviews (2 recommended)
- `require_last_push_approval`: Whether the most recent push must be approved

#### 2. Prevent Force Pushes and Deletions

```bash
# Disable force pushes
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/enforce_admins \
  --method PUT

# Prevent branch deletion
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/allow_deletions \
  --method DELETE
```

#### 3. Require Linear History (Optional)

```bash
# Enforce linear history (no merge commits)
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_linear_history \
  --method PUT
```

### Protecting Development Branches

Apply lighter protection to development branches:

```bash
# Protect develop branch with lighter rules
gh api repos/$REPO_OWNER/$REPO_NAME/branches/develop/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["ci-tests"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

### Pattern-Based Protection

Protect all release branches with a single rule:

```bash
# This requires using the GitHub API directly as gh CLI doesn't fully support pattern matching
curl -X POST \
  -H "Authorization: token $(gh auth token)" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/branches/release-*/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["ci-tests", "security-scan"]
    },
    "enforce_admins": true,
    "required_pull_request_reviews": {
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": true,
      "required_approving_review_count": 1
    },
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false
  }'
```

## Required Status Checks

### Adding Status Checks

Configure required status checks that must pass before merging:

```bash
# Add required status checks to main branch
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_status_checks \
  --method PATCH \
  --field strict=true \
  --field contexts[]="ci-tests" \
  --field contexts[]="security-scan" \
  --field contexts[]="code-quality" \
  --field contexts[]="vocabulary-lint" \
  --field contexts[]="front-matter-lint" \
  --field contexts[]="evidence-validation"
```

### Common Status Checks

Here are recommended status checks for different aspects:

#### Code Quality Checks
```bash
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_status_checks/contexts \
  --method POST \
  --field contexts[]="ruff-lint" \
  --field contexts[]="mypy-type-check" \
  --field contexts[]="black-format"
```

#### Security Checks
```bash
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_status_checks/contexts \
  --method POST \
  --field contexts[]="gitleaks-scan" \
  --field contexts[]="dependency-audit" \
  --field contexts[]="semgrep-security"
```

#### Test Coverage
```bash
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_status_checks/contexts \
  --method POST \
  --field contexts[]="pytest-unit-tests" \
  --field contexts[]="pytest-integration-tests" \
  --field contexts[]="codecov/project" \
  --field contexts[]="codecov/patch"
```

### Strict Status Checks

When `strict` is `true`, branches must be up to date with the base branch before merging:

```bash
# Enable strict status checks
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_status_checks \
  --method PATCH \
  --field strict=true
```

### Viewing Current Status Checks

```bash
# List all required status checks for main
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_status_checks \
  --jq '.contexts[]'
```

## Code Owner Review Requirements

### Setting Up Code Owner Reviews

Enable code owner review requirements:

```bash
# Require code owner reviews on main
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_pull_request_reviews \
  --method PATCH \
  --field require_code_owner_reviews=true
```

### Code Owner Configuration

Ensure your `.github/CODEOWNERS` file is properly configured (see `.github/CODEOWNERS`). The system will automatically request reviews from the appropriate team members based on files changed.

#### Example CODEOWNERS Integration

When a PR modifies files owned by specific teams:

1. **Core Systems** (`/lukhas/**`) → `@lukhas-core-team` review required
2. **Security** (`/security/**`) → `@security-team` review required
3. **Infrastructure** (`/deployment/**`) → `@devops-team` and `@platform-team` review required

### Review Dismissal Settings

```bash
# Configure review dismissal when new commits are pushed
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_pull_request_reviews \
  --method PATCH \
  --field dismiss_stale_reviews=true \
  --field dismissal_restrictions='{"users":[],"teams":[]}'
```

### Minimum Review Count

```bash
# Require at least 2 approving reviews
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_pull_request_reviews \
  --method PATCH \
  --field required_approving_review_count=2
```

## Benefits

### Code Quality Benefits

1. **Consistent Review Process**: All code changes undergo review by domain experts
2. **Reduced Bugs**: Multiple reviewers catch issues before they reach production
3. **Knowledge Sharing**: Reviews spread knowledge across the team
4. **Documentation**: Review comments serve as historical context

### Security Benefits

1. **Security Validation**: Security-critical paths require security team approval
2. **Audit Trail**: All changes are tracked with reviewer approval
3. **Reduced Attack Surface**: Unauthorized changes are prevented
4. **Compliance**: Meets regulatory requirements for code review

### Operational Benefits

1. **Protected Critical Branches**: Main/production branches can't be accidentally damaged
2. **Automated Checks**: CI/CD validates changes before human review
3. **Team Coordination**: CODEOWNERS ensures right people review changes
4. **Reduced Incidents**: Fewer production issues from inadequate review

### Development Workflow Benefits

1. **Clear Ownership**: Developers know who to ask for review
2. **Faster Reviews**: Automatic reviewer assignment speeds up process
3. **Better Code**: Review requirements encourage higher quality initial submissions
4. **Learning Opportunity**: Junior developers learn from senior reviewer feedback

## Troubleshooting

### Common Issues

#### Cannot Push to Protected Branch

**Problem**: Direct pushes to main are blocked

**Solution**: Create a feature branch and submit a PR:
```bash
git checkout -b feature/my-changes
git push origin feature/my-changes
gh pr create --base main --head feature/my-changes
```

#### Status Checks Not Running

**Problem**: Required status checks don't appear on PR

**Solution**: Ensure GitHub Actions workflows are configured:
```bash
# List all workflows
gh workflow list

# View specific workflow runs
gh run list --workflow=ci-tests
```

#### Code Owner Review Not Required

**Problem**: PR can be merged without code owner approval

**Solution**: Verify CODEOWNERS file and branch protection settings:
```bash
# Check current protection settings
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection | jq '.required_pull_request_reviews'

# Ensure code owner reviews are enabled
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_pull_request_reviews \
  --method PATCH \
  --field require_code_owner_reviews=true
```

#### Admin Override Needed

**Problem**: Need to merge urgent fix without full review

**Solution**: Admins can temporarily disable enforcement:
```bash
# Disable admin enforcement (use with caution)
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/enforce_admins \
  --method DELETE

# Re-enable after emergency merge
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/enforce_admins \
  --method PUT
```

**Note**: Always document the reason for override in PR comments and re-enable enforcement immediately after.

### Viewing Current Protection Rules

```bash
# Get complete branch protection configuration
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection | jq '.'

# Get just required reviews
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_pull_request_reviews | jq '.'

# Get just status checks
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection/required_status_checks | jq '.'
```

### Removing Branch Protection

If you need to remove protection (use with extreme caution):

```bash
# Remove all branch protection from main (DANGEROUS)
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection --method DELETE
```

## Quick Reference

### Complete Setup Script

Here's a complete script to set up branch protection for a new repository:

```bash
#!/bin/bash
# Branch Protection Setup Script

REPO_OWNER="your-org"
REPO_NAME="Lukhas"

# Main branch protection
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["ci-tests","security-scan","code-quality"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":2}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false

echo "Branch protection configured successfully!"
```

### Verification Checklist

- [ ] Branch protection enabled on `main`
- [ ] Required status checks configured
- [ ] Code owner reviews required
- [ ] Stale review dismissal enabled
- [ ] Force pushes disabled
- [ ] Branch deletion disabled
- [ ] `.github/CODEOWNERS` file exists and is valid
- [ ] Team members added to appropriate GitHub teams
- [ ] CI/CD workflows configured to run required checks

## Additional Resources

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub CODEOWNERS Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- Internal: `.github/CODEOWNERS` - Team ownership definitions
- Internal: `.github/workflows/` - CI/CD workflow configurations

## Maintenance

This configuration should be reviewed and updated:

- **Quarterly**: Review team assignments in CODEOWNERS
- **After major releases**: Update required status checks
- **When teams change**: Update team membership in GitHub
- **After incidents**: Evaluate if additional protection is needed

---

**Last Updated**: 2025-11-09
**Maintained By**: @security-team, @devops-team
**Document Owner**: Platform & Security Teams
