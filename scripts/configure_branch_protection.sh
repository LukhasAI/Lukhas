#!/usr/bin/env bash
#
# Configure branch protection rules for main branch
#
# Ensures that:
# 1. Required status checks pass before merge
# 2. TEMP-STUB services cannot be promoted to production
# 3. PQC verification is enforced when available
# 4. Code owner approvals required for sensitive changes
#
set -euo pipefail

REPO="LukhasAI/Lukhas"
BRANCH="main"

echo "Configuring branch protection for ${REPO}:${BRANCH}"

# Required status checks (these must pass before merge)
REQUIRED_CHECKS=(
    "nodespec-validate"
    "registry-ci"
    "pqc-sign-verify"
)

echo "Setting required status checks:"
printf '  - %s\n' "${REQUIRED_CHECKS[@]}"

# Configure branch protection via GitHub API
# Note: Requires appropriate GitHub token with repo permissions
gh api --method PUT "/repos/${REPO}/branches/${BRANCH}/protection" \
    --field required_status_checks[strict]=true \
    --field required_status_checks[contexts][]="$(IFS=,; echo "${REQUIRED_CHECKS[*]}")" \
    --field enforce_admins=true \
    --field required_pull_request_reviews[dismiss_stale_reviews]=true \
    --field required_pull_request_reviews[require_code_owner_reviews]=true \
    --field required_pull_request_reviews[required_approving_review_count]=1 \
    --field restrictions=null \
    2>/dev/null || {
        echo "⚠️  Direct API call failed. Attempting via gh CLI protection commands..."

        # Fallback to gh CLI protection commands
        gh api --method PUT "/repos/${REPO}/branches/${BRANCH}/protection" \
            --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["nodespec-validate", "registry-ci", "pqc-sign-verify"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null
}
EOF
    }

echo "✓ Branch protection configured"

# Create CODEOWNERS file if not present
CODEOWNERS_PATH=".github/CODEOWNERS"
if [[ ! -f "$CODEOWNERS_PATH" ]]; then
    echo "Creating CODEOWNERS file..."
    mkdir -p .github
    cat > "$CODEOWNERS_PATH" <<EOF
# LUKHAS AI Code Ownership
#
# These owners will be requested for review when someone opens a
# pull request that modifies code in their area.

# Registry service (requires security review)
/services/registry/ @security-team

# Core consciousness systems
/lukhas/consciousness/ @consciousness-team
/matriz/ @consciousness-team

# Identity and authentication
/lukhas/identity/ @security-team

# Governance and Guardian systems
/lukhas/governance/ @security-team

# Infrastructure and ops
/scripts/ @ops-team
/.github/workflows/ @ops-team
/Makefile @ops-team

# Schemas and specifications
/docs/schemas/ @architecture-team

# Default owners
* @core-team
EOF
    echo "✓ CODEOWNERS file created"
else
    echo "✓ CODEOWNERS file already exists"
fi

echo ""
echo "Branch protection configuration complete!"
echo ""
echo "Configured protections:"
echo "  ✓ Required status checks: nodespec-validate, registry-ci, pqc-sign-verify"
echo "  ✓ Enforce admin restrictions: enabled"
echo "  ✓ Code owner reviews required: yes"
echo "  ✓ Stale review dismissal: enabled"
echo ""
echo "Note: PQC checks may show as 'pending' until PQC runner is provisioned (issue #492)"
