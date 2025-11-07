#!/usr/bin/env bash
set -euo pipefail
REPO="LukhasAI/Lukhas"
MAIN_BRANCH="main"

cat > .github/CODEOWNERS <<'EOF'
/tools/ci/ @platform-team
/tools/ci/codemods/ @platform-team
/docs/gonzo/ @architecture-team
/tools/t4/ @platform-team
EOF

git add .github/CODEOWNERS
git commit -m "chore(t4): add CODEOWNERS for T4"
git push

gh api --method PUT /repos/$REPO/branches/$MAIN_BRANCH/protection -f required_status_checks='{"strict":true,"contexts":["t4-validator","t4-intent-api-health","ci/tests"]}' -f enforce_admins=true
echo "Branch protection set. CODEOWNERS added."
