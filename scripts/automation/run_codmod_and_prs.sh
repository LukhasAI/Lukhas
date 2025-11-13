#!/usr/bin/env bash
# supervised automation for labs→provider codemod batches.
#
# Responsibilities
#  - ingest pre-generated codemod patches and stage them in deterministic batches
#  - require an operator confirmation gate before each batch is validated/pushed
#  - stop immediately when a patch cannot be applied or when lane-guard fails
#  - push branches and open draft PRs (never merge) after validation succeeds
#  - archive validation artifacts for the supervising reviewer
#
# Safety defaults
#  - dry-run mode (`--dry-run`) prints intended actions without mutating git state
#  - human approval is required unless `--auto-approve` is explicitly supplied
#  - lane-guard validation must pass before any push occurs

set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --patch-dir <path>     Directory containing *.patch files (default: /tmp/codmod_patches)
  --batch-size <n>       Number of patches per batch (default: env BATCH_SIZE or 20)
  --base-branch <ref>    Base branch to branch from (default: env BASE_BRANCH or origin/main)
  --branch-prefix <str>  Prefix for created branches (default: env BRANCH_PREFIX or codemod/replace-labs-batch-)
  --batch-start <n>      Starting batch index (default: env BATCH_START or 2)
  --dry-run              Print actions without applying patches or creating commits/PRs
  --auto-approve         Skip interactive confirmation (not recommended)
  --skip-pr              Do not create PRs (implies no push)
  --help                 Show this help message

Environment overrides:
  GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL, GH_REPO, WORKTREE_BASE, PATCH_SORT
USAGE
}

DRY_RUN=${DRY_RUN:-0}
AUTO_APPROVE=${AUTO_APPROVE:-0}
SKIP_PR=${SKIP_PR:-0}
PATCH_DIR=${PATCH_DIR:-"/tmp/codmod_patches"}
BATCH_SIZE=${BATCH_SIZE:-20}
BASE_BRANCH=${BASE_BRANCH:-"origin/main"}
BRANCH_PREFIX=${BRANCH_PREFIX:-"codemod/replace-labs-batch-"}
BATCH_START=${BATCH_START:-2}
PR_TARGET=${PR_TARGET:-"main"}
WORKTREE_BASE=${WORKTREE_BASE:-"/tmp/lukhas_wt"}
PATCH_SORT=${PATCH_SORT:-"name"}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --patch-dir)
      PATCH_DIR="$2"; shift 2 ;;
    --batch-size)
      BATCH_SIZE="$2"; shift 2 ;;
    --base-branch)
      BASE_BRANCH="$2"; shift 2 ;;
    --branch-prefix)
      BRANCH_PREFIX="$2"; shift 2 ;;
    --batch-start)
      BATCH_START="$2"; shift 2 ;;
    --dry-run)
      DRY_RUN=1; shift ;;
    --auto-approve)
      AUTO_APPROVE=1; shift ;;
    --skip-pr)
      SKIP_PR=1; shift ;;
    --help|-h)
      usage; exit 0 ;;
    *)
      echo "[error] Unknown option: $1" >&2
      usage
      exit 1 ;;
  esac
done

if ! [[ "$BATCH_SIZE" =~ ^[0-9]+$ ]] || [ "$BATCH_SIZE" -le 0 ]; then
  echo "[error] batch size must be a positive integer" >&2
  exit 1
fi

if ! [[ "$BATCH_START" =~ ^[0-9]+$ ]] || [ "$BATCH_START" -le 0 ]; then
  echo "[error] batch start must be a positive integer" >&2
  exit 1
fi

if [ "$SKIP_PR" -eq 1 ]; then
  echo "[info] --skip-pr supplied; pushing to origin is disabled"
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

echo "[info] checking working tree state"
if [ -n "$(git status --porcelain)" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[warn] working tree has uncommitted changes; continuing because DRY_RUN=1"
  else
    echo "[error] working tree has uncommitted changes; please clean up before running" >&2
    exit 1
  fi
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "[info] fetching latest base branch state"
  git fetch origin
else
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[warn] remote 'origin' not configured; continuing because DRY_RUN=1"
  else
    echo "[error] remote 'origin' is required for pushes" >&2
    exit 1
  fi
fi

if ! git rev-parse --verify "$BASE_BRANCH" >/dev/null 2>&1; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[warn] base branch '$BASE_BRANCH' not found; dry-run exiting"
    exit 0
  fi
  echo "[error] base branch '$BASE_BRANCH' not found after fetch" >&2
  exit 1
fi

declare -a PATCHES
if [ ! -d "$PATCH_DIR" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[info] patch directory '$PATCH_DIR' not found; dry-run exiting"
    exit 0
  fi
  echo "[error] patch directory '$PATCH_DIR' not found" >&2
  exit 1
fi

case "$PATCH_SORT" in
  name)
    mapfile -t PATCHES < <(find "$PATCH_DIR" -maxdepth 1 -type f -name '*.patch' | sort)
    ;;
  mtime)
    mapfile -t PATCHES < <(find "$PATCH_DIR" -maxdepth 1 -type f -name '*.patch' -print0 | xargs -0 ls -1t)
    ;;
  *)
    echo "[warn] unknown PATCH_SORT='$PATCH_SORT'; defaulting to lexical order"
    mapfile -t PATCHES < <(find "$PATCH_DIR" -maxdepth 1 -type f -name '*.patch' | sort)
    ;;
esac

PATCH_COUNT=${#PATCHES[@]}
if [ "$PATCH_COUNT" -eq 0 ]; then
  echo "[info] no patches discovered in $PATCH_DIR; exiting"
  exit 0
fi

echo "[info] discovered $PATCH_COUNT patch(es); batch size=$BATCH_SIZE (starting at batch $BATCH_START)"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[info] DRY_RUN=1 — no git mutations will be performed"
fi

if [ "$SKIP_PR" -eq 1 ] && [ "$DRY_RUN" -eq 0 ]; then
  echo "[info] skip-pr active; batches will remain local after validation"
fi

batches_processed=0
declare -a created_refs=()

apply_patch() {
  local patch_path="$1"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] would apply patch $patch_path"
  else
    git apply --index "$patch_path"
  fi
}

run_lane_guard() {
  local branch_name="$1"
  local batch_num="$2"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] would run lane-guard for $branch_name"
    return 0
  fi

  local worktree_path="${WORKTREE_BASE}_${batch_num}"
  git worktree remove "$worktree_path" --force >/dev/null 2>&1 || true
  git worktree add "$worktree_path" "$branch_name" >/dev/null
  trap "git worktree remove '$worktree_path' --force >/dev/null 2>&1 || true" RETURN

  pushd "$worktree_path" >/dev/null
  if [ ! -x "./scripts/run_lane_guard_worktree.sh" ]; then
    echo "[error] scripts/run_lane_guard_worktree.sh missing or not executable" >&2
    exit 1
  fi

  if [ ! -d .venv ]; then
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -r requirements.txt
  echo "[info] running lane-guard for $branch_name"
  if ! ./scripts/run_lane_guard_worktree.sh; then
    echo "[error] lane-guard failed for $branch_name" >&2
    exit 1
  fi
  tar -czf "/tmp/${branch_name//\//_}_artifacts.tgz" artifacts/reports >/dev/null 2>&1 || true
  deactivate >/dev/null 2>&1 || true
  popd >/dev/null

  git worktree remove "$worktree_path" --force >/dev/null 2>&1 || true
  trap - RETURN
}

confirm_batch() {
  local branch_name="$1"
  local batch_num="$2"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] would request approval for batch $batch_num"
    return 0
  fi
  if [ "$AUTO_APPROVE" -eq 1 ]; then
    echo "[info] auto-approve enabled; proceeding with batch $batch_num"
    return 0
  fi

  echo "[prompt] Ready to validate/push batch $batch_num ($branch_name)."
  read -r -p "Proceed? [y/N] " response
  case "${response,,}" in
    y|yes)
      return 0
      ;;
    *)
      echo "[info] operator declined to proceed; halting remaining batches"
      exit 0
      ;;
  esac
}

create_pr() {
  local branch_name="$1"
  local batch_num="$2"
  if [ "$DRY_RUN" -eq 1 ] || [ "$SKIP_PR" -eq 1 ]; then
    echo "[info] skipping PR creation for $branch_name (dry-run or skip-pr)"
    return
  fi

  local repo=${GH_REPO:-$(git remote get-url origin | sed -E 's#.*[:/](.+/[^/]+)(\\.git)?$#\\1#')}
  local title="codemod: replace labs imports (batch ${batch_num})"
  local body="Automated codemod batch ${batch_num}. Lane-guard artifacts: /tmp/${branch_name//\//_}_artifacts.tgz. Human approval required before merge."
  if command -v gh >/dev/null 2>&1; then
    gh pr create --repo "$repo" --base "$PR_TARGET" --head "$branch_name" --title "$title" --body "$body" --draft
  else
    echo "[warn] gh CLI not available; push completed without PR"
  fi
}

push_branch() {
  local branch_name="$1"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] would push $branch_name to origin"
    return
  fi
  if [ "$SKIP_PR" -eq 1 ]; then
    echo "[info] skip-pr enabled; not pushing $branch_name"
    return
  fi
  echo "[info] pushing $branch_name"
  git push -u origin "$branch_name"
}

for ((idx=0; idx<PATCH_COUNT; idx++)); do
  patch_path="${PATCHES[$idx]}"
  batch_offset=$((idx / BATCH_SIZE))
  position_in_batch=$((idx % BATCH_SIZE))
  batch_number=$((BATCH_START + batch_offset))
  branch_name="${BRANCH_PREFIX}$(printf '%02d' "$batch_number")"

  if [ $position_in_batch -eq 0 ]; then
    echo "[info] starting batch $batch_number on branch $branch_name"
    if [ "$DRY_RUN" -eq 0 ]; then
      git checkout -B "$branch_name" "$BASE_BRANCH"
      git config user.name "${GIT_AUTHOR_NAME:-codex-bot}"
      git config user.email "${GIT_AUTHOR_EMAIL:-codex-bot@example.com}"
    else
      echo "[dry-run] would checkout branch $branch_name from $BASE_BRANCH"
    fi
  fi

  echo "[info] staging patch $(basename "$patch_path") into batch $batch_number"
  apply_patch "$patch_path"

  if [ $position_in_batch -eq $((BATCH_SIZE - 1)) ] || [ $idx -eq $((PATCH_COUNT - 1)) ]; then
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "[dry-run] would commit batch $batch_number"
    else
      git commit -m "chore(codemod): replace labs imports (batch ${batch_number})" || true
    fi

    if [ "$DRY_RUN" -eq 0 ]; then
      echo "[info] batch $batch_number summary:"
      git status --short
    fi

    confirm_batch "$branch_name" "$batch_number"

    run_lane_guard "$branch_name" "$batch_number"

    push_branch "$branch_name"
    create_pr "$branch_name" "$batch_number"

    batches_processed=$((batches_processed + 1))
    created_refs+=("$branch_name")

    if [ "$DRY_RUN" -eq 0 ]; then
      git checkout "$BASE_BRANCH" >/dev/null 2>&1 || true
    fi
  fi
done

echo "[info] completed $batches_processed batch(es)"
if [ ${#created_refs[@]} -gt 0 ]; then
  printf '[info] branches prepared: %s\n' "${created_refs[*]}"
  echo "[info] no auto-merge actions were performed; manual review required"
fi

echo "[info] script finished successfully"
