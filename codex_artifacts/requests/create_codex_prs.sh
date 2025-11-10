#!/usr/bin/env bash
set -euo pipefail
BASE=main
echo 'Creating branches and draft PRs for Codex tasks...'
# Ensure label exists (idempotent)
gh label create 'codex:review' -d 'Codex task review' -c '#5319e7' >/dev/null 2>&1 || true
echo '--- codex/make-labot-prs-draft-by-default ---'
git checkout -B codex/make-labot-prs-draft-by-default $BASE
# Rebase on remote if exists to avoid push rejection; autostash local changes
git pull --rebase --autostash origin codex/make-labot-prs-draft-by-default || true
mkdir -p codex_artifacts/branch_markers
printf '%s
' 'Codex scaffold marker for Make labot PRs draft by default' 'Branch: codex/make-labot-prs-draft-by-default' 'Request: codex_artifacts/requests/01-make-labot-prs-draft-by-default.md' > codex_artifacts/branch_markers/01-make-labot-prs-draft-by-default.txt
git add codex_artifacts/branch_markers/01-make-labot-prs-draft-by-default.txt
git commit -m 'codex: scaffold 01-make-labot-prs-draft-by-default' || true
git push -u origin codex/make-labot-prs-draft-by-default
# Create draft PR
gh pr create --draft --title 'codex: Make labot PRs draft by default' --body 'Automated Codex task: see `codex_artifacts/requests/01-make-labot-prs-draft-by-default.md`.\n\nBranch: `codex/make-labot-prs-draft-by-default`. This PR is a DRAFT labeled `codex:review`.' --label codex:review --base $BASE --head codex/make-labot-prs-draft-by-default || gh pr create --draft --title 'codex: Make labot PRs draft by default' --body 'Automated Codex task: see `codex_artifacts/requests/01-make-labot-prs-draft-by-default.md`.\n\nBranch: `codex/make-labot-prs-draft-by-default`. This PR is a DRAFT labeled `codex:review`.' --base $BASE --head codex/make-labot-prs-draft-by-default
echo '--- codex/guard-patch-enhancements ---'
git checkout -B codex/guard-patch-enhancements $BASE
# Rebase on remote if exists to avoid push rejection; autostash local changes
git pull --rebase --autostash origin codex/guard-patch-enhancements || true
mkdir -p codex_artifacts/branch_markers
printf '%s
' 'Codex scaffold marker for Guard_patch enhancements' 'Branch: codex/guard-patch-enhancements' 'Request: codex_artifacts/requests/02-guard-patch-enhancements.md' > codex_artifacts/branch_markers/02-guard-patch-enhancements.txt
git add codex_artifacts/branch_markers/02-guard-patch-enhancements.txt
git commit -m 'codex: scaffold 02-guard-patch-enhancements' || true
git push -u origin codex/guard-patch-enhancements
# Create draft PR
gh pr create --draft --title 'codex: Guard_patch enhancements' --body 'Automated Codex task: see `codex_artifacts/requests/02-guard-patch-enhancements.md`.\n\nBranch: `codex/guard-patch-enhancements`. This PR is a DRAFT labeled `codex:review`.' --label codex:review --base $BASE --head codex/guard-patch-enhancements || gh pr create --draft --title 'codex: Guard_patch enhancements' --body 'Automated Codex task: see `codex_artifacts/requests/02-guard-patch-enhancements.md`.\n\nBranch: `codex/guard-patch-enhancements`. This PR is a DRAFT labeled `codex:review`.' --base $BASE --head codex/guard-patch-enhancements
echo '--- codex/split-import-script-safe-reimport ---'
git checkout -B codex/split-import-script-safe-reimport $BASE
# Rebase on remote if exists to avoid push rejection; autostash local changes
git pull --rebase --autostash origin codex/split-import-script-safe-reimport || true
mkdir -p codex_artifacts/branch_markers
printf '%s
' 'Codex scaffold marker for Split import script & safe reimport' 'Branch: codex/split-import-script-safe-reimport' 'Request: codex_artifacts/requests/03-split-import-script-safe-reimport.md' > codex_artifacts/branch_markers/03-split-import-script-safe-reimport.txt
git add codex_artifacts/branch_markers/03-split-import-script-safe-reimport.txt
git commit -m 'codex: scaffold 03-split-import-script-safe-reimport' || true
git push -u origin codex/split-import-script-safe-reimport
# Create draft PR
gh pr create --draft --title 'codex: Split import script & safe reimport' --body 'Automated Codex task: see `codex_artifacts/requests/03-split-import-script-safe-reimport.md`.\n\nBranch: `codex/split-import-script-safe-reimport`. This PR is a DRAFT labeled `codex:review`.' --label codex:review --base $BASE --head codex/split-import-script-safe-reimport || gh pr create --draft --title 'codex: Split import script & safe reimport' --body 'Automated Codex task: see `codex_artifacts/requests/03-split-import-script-safe-reimport.md`.\n\nBranch: `codex/split-import-script-safe-reimport`. This PR is a DRAFT labeled `codex:review`.' --base $BASE --head codex/split-import-script-safe-reimport
echo '--- codex/opa-policy-ci-integration ---'
git checkout -B codex/opa-policy-ci-integration $BASE
# Rebase on remote if exists to avoid push rejection; autostash local changes
git pull --rebase --autostash origin codex/opa-policy-ci-integration || true
mkdir -p codex_artifacts/branch_markers
printf '%s
' 'Codex scaffold marker for OPA policy + CI integration' 'Branch: codex/opa-policy-ci-integration' 'Request: codex_artifacts/requests/04-opa-policy-ci-integration.md' > codex_artifacts/branch_markers/04-opa-policy-ci-integration.txt
git add codex_artifacts/branch_markers/04-opa-policy-ci-integration.txt
git commit -m 'codex: scaffold 04-opa-policy-ci-integration' || true
git push -u origin codex/opa-policy-ci-integration
# Create draft PR
gh pr create --draft --title 'codex: OPA policy + CI integration' --body 'Automated Codex task: see `codex_artifacts/requests/04-opa-policy-ci-integration.md`.\n\nBranch: `codex/opa-policy-ci-integration`. This PR is a DRAFT labeled `codex:review`.' --label codex:review --base $BASE --head codex/opa-policy-ci-integration || gh pr create --draft --title 'codex: OPA policy + CI integration' --body 'Automated Codex task: see `codex_artifacts/requests/04-opa-policy-ci-integration.md`.\n\nBranch: `codex/opa-policy-ci-integration`. This PR is a DRAFT labeled `codex:review`.' --base $BASE --head codex/opa-policy-ci-integration
echo '--- codex/dast-eqnox-wiring-tasks ---'
git checkout -B codex/dast-eqnox-wiring-tasks $BASE
# Rebase on remote if exists to avoid push rejection; autostash local changes
git pull --rebase --autostash origin codex/dast-eqnox-wiring-tasks || true
mkdir -p codex_artifacts/branch_markers
printf '%s
' 'Codex scaffold marker for DAST / EQNOX wiring tasks' 'Branch: codex/dast-eqnox-wiring-tasks' 'Request: codex_artifacts/requests/05-dast-eqnox-wiring-tasks.md' > codex_artifacts/branch_markers/05-dast-eqnox-wiring-tasks.txt
git add codex_artifacts/branch_markers/05-dast-eqnox-wiring-tasks.txt
git commit -m 'codex: scaffold 05-dast-eqnox-wiring-tasks' || true
git push -u origin codex/dast-eqnox-wiring-tasks
# Create draft PR
gh pr create --draft --title 'codex: DAST / EQNOX wiring tasks' --body 'Automated Codex task: see `codex_artifacts/requests/05-dast-eqnox-wiring-tasks.md`.\n\nBranch: `codex/dast-eqnox-wiring-tasks`. This PR is a DRAFT labeled `codex:review`.' --label codex:review --base $BASE --head codex/dast-eqnox-wiring-tasks || gh pr create --draft --title 'codex: DAST / EQNOX wiring tasks' --body 'Automated Codex task: see `codex_artifacts/requests/05-dast-eqnox-wiring-tasks.md`.\n\nBranch: `codex/dast-eqnox-wiring-tasks`. This PR is a DRAFT labeled `codex:review`.' --base $BASE --head codex/dast-eqnox-wiring-tasks
echo '--- codex/openapi-drift-deeper-check ---'
git checkout -B codex/openapi-drift-deeper-check $BASE
# Rebase on remote if exists to avoid push rejection; autostash local changes
git pull --rebase --autostash origin codex/openapi-drift-deeper-check || true
mkdir -p codex_artifacts/branch_markers
printf '%s
' 'Codex scaffold marker for OpenAPI drift deeper check' 'Branch: codex/openapi-drift-deeper-check' 'Request: codex_artifacts/requests/06-openapi-drift-deeper-check.md' > codex_artifacts/branch_markers/06-openapi-drift-deeper-check.txt
git add codex_artifacts/branch_markers/06-openapi-drift-deeper-check.txt
git commit -m 'codex: scaffold 06-openapi-drift-deeper-check' || true
git push -u origin codex/openapi-drift-deeper-check
# Create draft PR
gh pr create --draft --title 'codex: OpenAPI drift deeper check' --body 'Automated Codex task: see `codex_artifacts/requests/06-openapi-drift-deeper-check.md`.\n\nBranch: `codex/openapi-drift-deeper-check`. This PR is a DRAFT labeled `codex:review`.' --label codex:review --base $BASE --head codex/openapi-drift-deeper-check || gh pr create --draft --title 'codex: OpenAPI drift deeper check' --body 'Automated Codex task: see `codex_artifacts/requests/06-openapi-drift-deeper-check.md`.\n\nBranch: `codex/openapi-drift-deeper-check`. This PR is a DRAFT labeled `codex:review`.' --base $BASE --head codex/openapi-drift-deeper-check
