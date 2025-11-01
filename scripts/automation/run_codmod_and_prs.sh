#!/usr/bin/env bash
# Supervised orchestration for the labs→provider codemod.
# - Runs the codemod in dry-run to produce patches.
# - Applies patches in small batches onto a feature branch using a worktree.
# - Optionally creates PRs (disabled by default via DRY_RUN=1).

set -euo pipefail

CODMOD=${CODMOD:-"scripts/codemods/replace_labs_with_provider.py"}
PATCH_DIR=${PATCH_DIR:-"/tmp/codmod_patches"}
BATCH_SIZE=${BATCH_SIZE:-20}
DRY_RUN=${DRY_RUN:-1}
BASE_BRANCH=${BASE_BRANCH:-"origin/main"}
PR_TARGET=${PR_TARGET:-"main"}
WORKTREE_BASE=${WORKTREE_BASE:-"/tmp/lukhas_wt"}

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

echo "[info] Running codemod dry-run to produce patches..."
python3 "$CODMOD" --outdir "$PATCH_DIR"

PATCH_COUNT=$(ls -1 "$PATCH_DIR"/*.patch 2>/dev/null | wc -l | tr -d ' ')
PATCH_COUNT=${PATCH_COUNT:-0}
echo "[info] Found ${PATCH_COUNT} patch(es) in $PATCH_DIR"

if [ "$PATCH_COUNT" -eq 0 ]; then
  echo "[info] No patches to apply; exiting."
  exit 0
fi

i=0
batch=1
branch_prefix=${BRANCH_PREFIX:-"codemod/replace-labs-batch-"}

for patch in "$PATCH_DIR"/*.patch; do
  if (( i % BATCH_SIZE == 0 )); then
    BRANCH="${branch_prefix}${batch}"
    echo "[info] Starting batch $batch on branch $BRANCH"
    git fetch origin --quiet || true
    git checkout -B "$BRANCH" "$BASE_BRANCH"
  fi

  echo "[info] Applying patch $patch"
  git apply --index "$patch"
  i=$((i+1))

  if (( i % BATCH_SIZE == 0 )) || [ "$i" -eq "$PATCH_COUNT" ]; then
    git commit -m "chore(codemod): replace labs imports (batch ${batch})" || true

    if [ "$DRY_RUN" -eq 0 ]; then
      echo "[info] Pushing branch $BRANCH (DRY_RUN=0)"
      git push -u origin "$BRANCH"
      if command -v gh >/dev/null 2>&1; then
        GH_REPO=${GH_REPO:-$(git remote get-url origin | sed -E 's#.*[:/](.+/[^/]+)(\.git)?$#\1#')}
        gh pr create --repo "$GH_REPO" \
          --title "codemod: replace labs imports (batch ${batch})" \
          --base "$PR_TARGET" \
          --head "$BRANCH" \
          --body "Auto-generated codemod batch ${batch}. Please run CI and lane-guard." || true
      fi
    else
      echo "[info] DRY_RUN=1; skipping push/PR for $BRANCH"
    fi

    # Ephemeral worktree validation (lane-guard) – optional, best-effort
    WT="${WORKTREE_BASE}_${batch}"
    rm -rf "$WT" || true
    git worktree add "$WT" "$BRANCH"
    pushd "$WT" >/dev/null
      if [ -f "scripts/run_lane_guard_worktree.sh" ]; then
        echo "[info] Running lane-guard worktree script (best-effort)"
        if [ ! -d .venv ]; then
          python3 -m venv .venv || true
        fi
        # shellcheck disable=SC1091
        . .venv/bin/activate || true
        pip install -r requirements.txt || true
        ./scripts/run_lane_guard_worktree.sh || true
        tar -czf "/tmp/${BRANCH}_artifacts.tgz" artifacts/reports || true
      else
        echo "[warn] scripts/run_lane_guard_worktree.sh not found; skipping lane-guard"
      fi
    popd >/dev/null
    git worktree remove "$WT" --force || true

    batch=$((batch+1))
  fi
done

echo "[info] All batches processed. DRY_RUN=$DRY_RUN"

