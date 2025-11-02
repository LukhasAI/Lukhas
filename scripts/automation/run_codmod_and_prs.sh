#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

PATCH_DIR=${PATCH_DIR:-/tmp/codmod_patches}
BATCH_SIZE=${BATCH_SIZE:-20}
BASE_BRANCH=${BASE_BRANCH:-origin/main}
PR_TARGET=${PR_TARGET:-main}
GH_REPO=${GH_REPO:-$(git remote get-url origin | sed -E 's#.*[:/](.+/[^/]+)(\.git)?$#\1#')}

python3 scripts/codemods/replace_labs_with_provider.py --outdir "$PATCH_DIR"

PATCHES=("$PATCH_DIR"/*.patch)
PATCH_COUNT=${#PATCHES[@]}
if [ "$PATCH_COUNT" -eq 0 ]; then
  echo "No patches."
  exit 0
fi

i=0
batch=1
for patch in "${PATCHES[@]}"; do
  if (( i % BATCH_SIZE == 0 )); then
    BRANCH="codemod/replace-labs-batch-${batch}"
    git fetch origin
    git checkout -B "$BRANCH" "$BASE_BRANCH"
  fi

  git apply --index "$patch"
  i=$((i+1))

  if (( i % BATCH_SIZE == 0 )) || [ "$i" -eq "$PATCH_COUNT" ]; then
    git commit -m "chore(codemod): replace labs imports (batch ${batch})" || true
    git push -u origin "$BRANCH"
    gh pr create --repo "$GH_REPO" --title "codemod: replace labs imports (batch ${batch})" --body "Auto-generated batch ${batch}. Please run CI and lane-guard."

    # Ephemeral worktree validation
    WT="/tmp/wt_${batch}"
    rm -rf "$WT" || true
    git worktree add "$WT" "origin/$BRANCH"
    pushd "$WT"
      python3 -m venv .venv
      . .venv/bin/activate
      pip install -r requirements.txt || true
      ./scripts/run_lane_guard_worktree.sh || true
      tar -czf "/tmp/codmod_batch_${batch}_artifacts.tgz" artifacts/reports || true
      gh pr comment --repo "$GH_REPO" --body "Lane-guard artifacts for batch ${batch} attached." "$(gh pr list --repo "$GH_REPO" --state open --head "$BRANCH" --json number --jq '.[0].number')"
    popd
    git worktree remove "$WT" --force || true
    batch=$((batch+1))
  fi
done

echo "Done. Inspect PRs and artifacts. Do not merge without human review."
