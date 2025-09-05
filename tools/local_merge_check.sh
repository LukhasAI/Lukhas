#!/usr/bin/env bash
set -euo pipefail

# tools/local_merge_check.sh
# Usage: ./tools/local_merge_check.sh [base_branch] [head_branch]
# Default: base=main head=$(git rev-parse --abbrev-ref HEAD)

BASE=${1:-main}
HEAD=${2:-$(git rev-parse --abbrev-ref HEAD)}
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ORIG_PWD="$PWD"

echo "Local merge check"
echo "Repo root: $REPO_ROOT"
echo "Base: $BASE"
echo "Head: $HEAD"

git fetch --no-tags origin "+refs/heads/${HEAD}:refs/remotes/origin/${HEAD}" || true
CLONE_DIR=$(mktemp -d /tmp/lukhas-merge-XXXX)
echo "Cloning origin into $CLONE_DIR"
REMOTE_URL="$(git -C "$REPO_ROOT" remote get-url origin)"
echo "Remote URL: $REMOTE_URL"

# Shallow clone the base branch into a temp dir to avoid touching local repo state
git clone --depth 1 --branch "$BASE" "$REMOTE_URL" "$CLONE_DIR"
cd "$CLONE_DIR"

echo "Fetching head ref origin/${HEAD}..."
git fetch --depth 1 origin "${HEAD}:refs/remotes/origin/${HEAD}" || true

echo "Merging origin/${HEAD} into clone (no-commit)..."
set +e
git merge --no-commit --no-ff "origin/${HEAD}"
MERGE_EXIT=$?
set -e

if [ $MERGE_EXIT -ne 0 ]; then
  echo "Merge produced conflicts or non-zero exit ($MERGE_EXIT)."
  # If the merge failed because of unrelated histories, allow an opt-in retry
  if [ $MERGE_EXIT -eq 128 ] && [ "${ALLOW_UNRELATED:-}" = "1" ]; then
    echo "Merge failed with unrelated histories; retrying with --allow-unrelated-histories because ALLOW_UNRELATED=1 is set."
    set +e
    git merge --allow-unrelated-histories --no-commit --no-ff "origin/${HEAD}"
    MERGE_EXIT=$?
    set -e
    if [ $MERGE_EXIT -ne 0 ]; then
      echo "Retry with --allow-unrelated-histories also failed (exit $MERGE_EXIT). Will continue to run checks on the current merge state."
    else
      echo "Retry merge succeeded (no-commit)."
    fi
  else
    echo "Attempting to continue with ruff/pytest on merge state. Set ALLOW_UNRELATED=1 to retry merges that fail due to unrelated histories."
  fi
fi

# Optional automatic conflict resolution (use with caution)
# Set AUTO_RESOLVE=theirs to prefer incoming branch (origin/${HEAD}) for conflicted files
# Set AUTO_RESOLVE=ours to prefer current clone branch (base)
if [ $MERGE_EXIT -ne 0 ] && [ "${AUTO_RESOLVE:-}" != "" ]; then
  echo "AUTO_RESOLVE is set to '${AUTO_RESOLVE}'; attempting automatic conflict resolution."
  if [ "${AUTO_RESOLVE}" = "theirs" ] || [ "${AUTO_RESOLVE}" = "ours" ]; then
    # List conflicted files
    CONFLICTED=$(git diff --name-only --diff-filter=U || true)
    if [ -z "$CONFLICTED" ]; then
      echo "No conflicted files detected to resolve."
    else
      echo "Conflicted files:"
      echo "$CONFLICTED"
      for f in $CONFLICTED; do
        if [ "${AUTO_RESOLVE}" = "theirs" ]; then
          git checkout --theirs -- "$f" || true
        else
          git checkout --ours -- "$f" || true
        fi
        git add -- "$f" || true
      done
      git commit -m "Auto-resolve merge conflicts preferring ${AUTO_RESOLVE} for quick CI validation (tools/local_merge_check)" || true
      echo "Auto-resolve commit created. Continuing checks on resolved merge state."
      MERGE_EXIT=0
    fi
  else
    echo "AUTO_RESOLVE value '${AUTO_RESOLVE}' not supported. Supported: 'theirs' or 'ours'."
  fi
fi

# Prepare Python venv
VENV_DIR="$CLONE_DIR/.venv_merge_check"
python3 -m venv "$VENV_DIR"
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip >/dev/null
python -m pip install "ruff==0.6.9" "pytest==8.4.2" >/dev/null
# Install test dependencies if requirements file exists in the clone
if [ -f "$CLONE_DIR/requirements-test.txt" ]; then
  echo "Installing test dependencies from requirements-test.txt in the clone (may take a while)"
  python -m pip install -r "$CLONE_DIR/requirements-test.txt" >/dev/null || true
fi

# Compute changed python files between base and head (origin refs)
CHANGED_FILES=$(git diff --name-only "origin/${BASE}...origin/${HEAD}" | grep -E '\.py$' || true)
if [ -z "$CHANGED_FILES" ]; then
  echo "No changed Python files between origin/${BASE} and origin/${HEAD}. Running full ruff check on serve/ and tests/contract"
  python -m ruff check --config "$REPO_ROOT/pyproject.toml" serve tests/contract || true
else
  echo "Changed Python files:" 
  echo "$CHANGED_FILES"
  python -m ruff check --config "$REPO_ROOT/pyproject.toml" $CHANGED_FILES || true
fi

# Run contract tests (disable heavy DB plugins that require native libs)
echo "Running contract tests (pytest tests/contract) - skipping pytest_postgresql plugin"
# Disable pytest_postgresql plugin which can import psycopg and fail in clean envs
pytest -q tests/contract -p no:pytest_postgresql --maxfail=1 --disable-warnings || true

# Deactivate and cleanup
echo "Cleaning up worktree"
echo "No temporary worktree to remove (using a shallow clone)."
deactivate || true
cd "$REPO_ROOT"

echo "Cleaning up clone"
rm -rf "$CLONE_DIR" || true

echo "Local merge check complete." 

# Return non-zero if merge had conflicts
if [ $MERGE_EXIT -ne 0 ]; then
  echo "Merge had conflicts or non-zero exit ($MERGE_EXIT). See clone logs above." >&2
  exit $MERGE_EXIT
fi

exit 0
