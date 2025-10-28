#!/usr/bin/env bash
# scripts/run_lane_guard_worktree.sh
# Purpose: run import-health and lane-guard in isolated worktree + venv,
# apply minimal local fix to .importlinter if needed, capture artifacts,
# revert any local changes, and cleanup. DO NOT commit/push.

set -euo pipefail
IFS=$'\n\t'

REPO_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
WORKTREE="/Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/sync-origin-main"
ARTDIR="artifacts"
REPORTDIR="$ARTDIR/reports"
VENV=".venv_temp"
SYMLINK=".venv"

mkdir -p "$REPORTDIR"

echo "[run] Repo root: $REPO_ROOT"
cd "$REPO_ROOT"

echo "[run] Fetching origin"
git fetch origin --prune

if [ ! -d "$WORKTREE" ] || [ ! -f "$WORKTREE/.git" ]; then
  echo "[run] Creating worktree at $WORKTREE (origin/main)"
  git worktree add "$WORKTREE" origin/main
else
  echo "[run] Worktree already exists: $WORKTREE"
fi

cd "$WORKTREE"
echo "[run] In worktree: $(pwd)"

# create artifacts dir within worktree
mkdir -p "$WORKTREE/$ARTDIR"
mkdir -p "$REPORTDIR"

# Setup venv
echo "[run] Creating venv at $WORKTREE/$VENV"
python3 -m venv "$VENV"
echo "[run] Upgrading pip and installing import-linter (logs -> venv_install.log)"
"$VENV/bin/python" -m pip install --upgrade pip > "$REPORTDIR/venv_install.log" 2>&1 || true
"$VENV/bin/python" -m pip install import-linter >> "$REPORTDIR/venv_install.log" 2>&1 || true

# Conservative install: install minimal deps if requirements-dev exists, but capture logs
if [ -f "$REPO_ROOT/requirements-dev.txt" ]; then
  echo "[run] Installing requirements-dev (this might be large; logs -> venv_install.log)"
  "$VENV/bin/python" -m pip install -r "$REPO_ROOT/requirements-dev.txt" >> "$REPORTDIR/venv_install.log" 2>&1 || true
else
  echo "[run] No requirements-dev.txt found at repo root. Skipping."
fi

# Symlink .venv -> .venv_temp so Makefile picks up .venv/bin/lint-imports
ln -sfn "$VENV" "$SYMLINK"
echo "[run] Created symlink $SYMLINK -> $VENV"

# Ensure artifacts dir exists and capture environment info
echo "run_id: $(uuidgen)" > "$REPORTDIR/run_meta.txt"
echo "worktree: $WORKTREE" >> "$REPORTDIR/run_meta.txt"
echo "git_head: $(git rev-parse --short HEAD)" >> "$REPORTDIR/run_meta.txt"

# Run import-health
echo "[run] Running import-health..."
PYTHONPATH=. "$VENV/bin/python" "$WORKTREE/scripts/consolidation/check_import_health.py" --verbose 2>&1 | tee "$REPORTDIR/import_health_worktree.log" || true

# Inspect import_health log for common ImportError hints
if grep -q "ImportError\|ModuleNotFoundError" "$REPORTDIR/import_health_worktree.log" 2>/dev/null || true; then
  echo "[run] import-health reported missing modules; extracting hints..."
  grep -nE "ImportError|ModuleNotFoundError" "$REPORTDIR/import_health_worktree.log" | sed -n '1,100p' > "$REPORTDIR/import_health_errors_snippet.txt" || true
  echo "[run] Installing minimal runtime deps (pydantic, streamlit) as common fixes..."
  "$VENV/bin/python" -m pip install pydantic streamlit >> "$REPORTDIR/venv_install.log" 2>&1 || true
  echo "[run] Re-running import-health..."
  PYTHONPATH=. "$VENV/bin/python" "$WORKTREE/scripts/consolidation/check_import_health.py" --verbose 2>&1 | tee -a "$REPORTDIR/import_health_worktree.log" || true
fi

# Check final import-health PASS
if grep -q "PASS" "$REPORTDIR/import_health_worktree.log" 2>/dev/null || true; then
  echo "[run] import-health indicates PASS or likely passed (check $REPORTDIR/import_health_worktree.log)"
else
  echo "[run] import-health did not clearly PASS. Please check $REPORTDIR/import_health_worktree.log"
fi

# Run lane-guard via Makefile
echo "[run] Running make lane-guard (as CI)..."
set +e
make lane-guard 2>&1 | tee "$REPORTDIR/lane_guard_make_original.log"
MAKE_EXIT=$?
set -e

if [ $MAKE_EXIT -eq 0 ]; then
  echo "[run] make lane-guard completed successfully (no local fixes necessary)."
else
  echo "[run] make lane-guard failed. Inspecting for root-package mismatch..."
  # Heuristics: compare top-level dirs vs .importlinter entries
  # Portable listing of top-level directories (macOS-compatible)
  TOP_PKGS=$(for d in ./*/; do
    [ -d "$d" ] || continue
    basename "$d"
  done | egrep -v '^\.' | egrep -v '^(venv|.venv|.git|node_modules)$' | tr '\n' ' ' | sed 's/ $//')
  echo "[run] top-level packages: $TOP_PKGS" > "$REPORTDIR/top_level_packages.txt"
  # Read root packages from .importlinter and pyproject.toml
  if [ -f .importlinter ]; then
    echo "[run] Found .importlinter - extracting root_packages..." 
    grep -n 'root_package\|root_packages' .importlinter > "$REPORTDIR/importlinter_roots.txt" || true
    sed -n '1,200p' .importlinter > "$REPORTDIR/importlinter_raw.txt"
  fi
  if [ -f pyproject.toml ]; then
    grep -n 'root_package\|root_packages' pyproject.toml > "$REPORTDIR/pyproject_roots.txt" || true
    sed -n '1,200p' pyproject.toml > "$REPORTDIR/pyproject_raw.txt"
  fi

  # If .importlinter mentions a package name that's not in top-level packages, attempt minimal local fix
  # Look for 'matriz' vs 'MATRIZ' mismatch as common case
  if grep -q -i 'matriz' .importlinter 2>/dev/null || grep -q -i 'matriz' pyproject.toml 2>/dev/null; then
    # detect actual case-sensitive folder
    if [ -d "MATRIZ" ] && ! grep -q 'MATRIZ' .importlinter 2>/dev/null; then
      echo "[run] Detected matrix case mismatch: .importlinter references lowercase 'matriz' but 'MATRIZ' exists."
      echo "[run] Backing up and patching .importlinter locally..."
      cp .importlinter .importlinter.bak
      # Use perl or sed to replace word boundaries for 'matriz' -> 'MATRIZ'
      perl -i -pe 's/\bmatriz\b/MATRIZ/g' .importlinter
      echo "[run] Running make lane-guard with local .importlinter patch..."
      set +e
      make lane-guard 2>&1 | tee "$REPORTDIR/lane_guard_run_localfix.log"
      LG_EXIT=$?
      set -e
      # Revert changes
      echo "[run] Reverting .importlinter to HEAD copy..."
      git restore --source=HEAD -- .importlinter || true
      rm -f .importlinter.bak || true
      if [ $LG_EXIT -ne 0 ]; then
        echo "[run] lane-guard still failed after local patch. See $REPORTDIR/lane_guard_run_localfix.log"
      else
        echo "[run] lane-guard passed after local patch. See $REPORTDIR/lane_guard_run_localfix.log"
      fi
    else
      echo "[run] No obvious MATRIZ case discrepancy detected. Consider creating override config to run import-linter."
      # create an override skeleton pointing to first top-level package
      FIRST_PKG=$(echo "$TOP_PKGS" | awk '{print $1}')
      if [ -n "$FIRST_PKG" ]; then
        echo "[run] Creating importlinter override for root_package = $FIRST_PKG"
        cat > "$REPORTDIR/importlinter_override.toml" <<EOF
[importlinter]
root_packages = ["$FIRST_PKG"]
EOF
        "$VENV/bin/lint-imports" --config "$REPORTDIR/importlinter_override.toml" --verbose 2>&1 | tee "$REPORTDIR/import_lint_override.log" || true
        echo "[run] Ran lint-imports with override. See $REPORTDIR/import_lint_override.log"
      fi
    fi
  else
    echo "[run] .importlinter does not mention 'matriz'. Manual triage required. See $REPORTDIR/importlinter_raw.txt and $REPORTDIR/pyproject_raw.txt"
  fi
fi

# Final checks: ensure no uncommitted changes in worktree
CHANGED=$(git status --porcelain)
if [ -n "$CHANGED" ]; then
  echo "[run] Warning: Uncommitted changes detected in the worktree:"
  git status --porcelain
  # Attempt to restore .importlinter from HEAD if it exists
  if git show HEAD:.importlinter >/dev/null 2>&1; then
    git restore --source=HEAD -- .importlinter || true
    echo "[run] Reverted .importlinter to HEAD."
  fi
else
  echo "[run] No uncommitted changes found in worktree."
fi

# Optional cleanup: remove venv and symlink
echo "[run] Cleaning up venv and symlink..."
rm -rf "$SYMLINK" "$VENV" || true

echo "[run] Done. Artifacts under $REPORTDIR"
echo "Please review the logs in: $REPORTDIR"
