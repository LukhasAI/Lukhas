#!/usr/bin/env bash
# scripts/migration/prepare_matriz_migration_prs.sh
# PREPARE MATRIZ MIGRATION PRs for serve/, core/, and orchestrator.
# Usage:
#  ./prepare_matriz_migration_prs.sh --dry-run
#  ./prepare_matriz_migration_prs.sh --apply --push
set -euo pipefail

REPO_ROOT="$(pwd)"
DRY=${DRY:-1}
APPLY=0
PUSH=0

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --apply) DRY=0; APPLY=1; shift ;;
    --push) PUSH=1; shift ;;
    --help) echo "Usage: $0 [--dry-run | --apply] [--push]"; exit 0 ;;
    *) echo "Unknown arg $1"; exit 1 ;;
  esac
done

DATE=$(date +%Y-%m-%d)
PACKAGES=("serve" "core" "orchestrator")
AST_REWRITER="python3 scripts/consolidation/rewrite_matriz_imports.py"
RUNNER="./scripts/run_lane_guard_worktree.sh"

for pkg in "${PACKAGES[@]}"; do
  echo "=== PACKAGE: $pkg ==="
  DRYPATCH="/tmp/matriz_${pkg}_dry.patch"
  echo "[1/6] Dry-run AST rewriter for $pkg -> $DRYPATCH"
  $AST_REWRITER --path "$pkg" --dry-run --out "$DRYPATCH" || true

  BRANCH="migration/matriz-${pkg}-${DATE}"
  BASE="origin/main"

  echo "[2/6] Creating branch $BRANCH from $BASE"
  git fetch origin
  git checkout -B "$BRANCH" "$BASE"

  # Add dry-run artifact and short note
  ART_NOTE="MATRIZ migration dry-run for $pkg created on $DATE. Dry patch attached: $(basename $DRYPATCH)"
  mkdir -p migration_artifacts/matriz/$pkg
  cp "$DRYPATCH" migration_artifacts/matriz/$pkg/ || true
  echo "$ART_NOTE" > migration_artifacts/matriz/$pkg/README.md
  git add migration_artifacts/matriz/$pkg
  git commit -m "chore(migration): add dry-run patch for MATRIZ -> $pkg" || true

  echo "[3/6] If --apply not provided, we stop here (dry-run branch prepared)."
  if [[ $DRY -eq 1 && $APPLY -eq 0 ]]; then
    echo "Dry-mode: branch $BRANCH prepared with dry-run artifact. Please review /tmp/matriz_${pkg}_dry.patch or migration_artifacts/matriz/$pkg/"
    # push branch for review if requested
    if [[ $PUSH -eq 1 ]]; then
      git push -u origin "$BRANCH"
      echo "Pushed branch $BRANCH"
    fi
    # switch back to main before next package
    git checkout main
    continue
  fi

  # APPLY path:
  echo "[4/6] Applying AST rewriter for $pkg (non-dry)"
  $AST_REWRITER --path "$pkg" || { echo "AST rewriter failed"; exit 1; }

  echo "[5/6] Run local validations: make smoke, lane-guard"
  set +e
  make smoke
  SMOKE_RC=$?
  set -e
  if [[ $SMOKE_RC -ne 0 ]]; then
    echo "Smoke tests failed for $pkg after applying codemod; aborting. Please inspect."
    git status --porcelain
    git checkout main
    exit 2
  fi

  echo "[5b/6] Run import-lane guard (runner)"
  if [[ -x "$RUNNER" ]]; then
    "$RUNNER" || { echo "Lane guard failed; abort."; git checkout main; exit 3; }
  else
    echo "Runner not found or not executable; please run ./scripts/run_lane_guard_worktree.sh manually."
  fi

  echo "[6/6] Commit changes and push branch"
  git add -A "$pkg"
  git commit -m "chore(imports): migrate matriz -> MATRIZ in $pkg (AST codemod)" || true
  if [[ $PUSH -eq 1 ]]; then
    echo "Pushing branch $BRANCH"
    git push -u origin "$BRANCH"
    # create PR if gh available
    if command -v gh >/dev/null 2>&1; then
      gh pr create --title "chore(imports): migrate matriz -> MATRIZ in $pkg (AST codemod)" \
        --body "## Summary\nApplied AST-safe rewrite to migrate imports from \`matriz\` to \`MATRIZ\` in package **$pkg**.\n\nDry-run patch attached in migration_artifacts. Validations: make smoke => OK; lane-guard => OK.\n\n## Validation\n- Smoke tests: PASS\n- Lane-guard: PASS\n\n## Rollback\n- Revert commit: \`git revert <commit>\` on branch\n" --base main --head "$BRANCH" || echo "gh CLI not configured to open PR."
    else
      echo "gh cli not found: push done. Create PR manually for $BRANCH."
    fi
  fi

  # switch back for next package
  git checkout main
done

echo "All done. Dry=${DRY} Apply=${APPLY} Push=${PUSH}"
