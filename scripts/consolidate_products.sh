#!/usr/bin/env bash
# Consolidate product bundles into top-level products/ dir.
# Usage:
#   ./scripts/consolidate_products.sh              # dry-run (default)
#   ./scripts/consolidate_products.sh --apply      # perform git mv operations
#   ./scripts/consolidate_products.sh -n|--dry-run # explicit dry-run
#   ./scripts/consolidate_products.sh -h|--help    # show this help

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$REPO_ROOT/products/manifest.txt"
if [ ! -f "$MANIFEST" ]; then
  MANIFEST="$REPO_ROOT/products/MANIFEST.md"
fi

# Defaults
DRY_RUN=true
VERBOSE=false

show_help() {
  cat <<'EOF'
Usage: consolidate_products.sh [OPTIONS]

Options:
  --apply           Actually perform moves using `git mv`. Default is dry-run.
  -n, --dry-run     Dry run (default).
  -v, --verbose     Print verbose logs.
  -h, --help        Show this help and exit.

Manifest format (lines):
  canonical_name -> relative/path/to/source
  Lines starting with '#' or blank lines are ignored.

This script is conservative: it checks that you're in a git repo and
warns if there are uncommitted changes. It will attempt `git mv` and
fall back to moving files with preservation of content if necessary.
EOF
}

# Simple logging
info() { [ "$VERBOSE" = true ] && printf "[INFO] %s\n" "$*" || true; }
warn() { printf "[WARN] %s\n" "$*" >&2; }
err() { printf "[ERROR] %s\n" "$*" >&2; }

# Option parsing
while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply)
      DRY_RUN=false; shift;;
    -n|--dry-run)
      DRY_RUN=true; shift;;
    -v|--verbose)
      VERBOSE=true; shift;;
    -h|--help)
      show_help; exit 0;;
    *)
      err "Unknown option: $1"; show_help; exit 2;;
  esac
done

echo "Products consolidation script"
echo "Repo root: $REPO_ROOT"
echo "Manifest: $MANIFEST"
echo "Dry run: $DRY_RUN"

if [ ! -f "$MANIFEST" ]; then
  err "Manifest not found at $MANIFEST"
  exit 2
fi

mkdir -p "$REPO_ROOT/products"

check_git_safety() {
  if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    warn "Not a git repository: $REPO_ROOT. Script will still operate but git mv won't be available."
    return
  fi

  # Warn if uncommitted changes exist to avoid surprising moves
  if [ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]; then
    warn "Working tree has uncommitted changes. It's recommended to commit or stash before running with --apply."
  fi
}

parse_manifest() {
  # robust manifest parsing: ignore comments and blank lines, split on first '->'
  awk '/^[[:space:]]*#/ { next } /^[[:space:]]*$/ { next } /->/ { print }' "$MANIFEST" |
    sed -E 's/\r$//'
}

# Build move plan
TO_MOVE=()
DELIM=$'\x1f'
TMPDIRS=()

while IFS= read -r line; do
  # normalize spacing around arrow, keep everything else (paths may contain dots, dashes, spaces)
  line=$(printf '%s' "$line" | sed -E 's/[[:space:]]*->[[:space:]]*/->/')
  # split on first occurrence of '->'
  if [[ "$line" != *'->'* ]]; then
    continue
  fi
  key=${line%%->*}
  val=${line#*->}
  canonical=$(printf '%s' "$key" | xargs)
  src_raw=$(printf '%s' "$val" | xargs)
  # Strip leading ./ from source for consistency
  src=${src_raw#./}
  if [ -z "$canonical" ] || [ -z "$src" ]; then
    warn "Skipping invalid manifest line: $line"
    continue
  fi
  dest="$REPO_ROOT/products/$canonical"
  TO_MOVE+=("$src${DELIM}$dest")
done < <(parse_manifest)

echo "Planned moves:" 
for entry in "${TO_MOVE[@]}"; do
  IFS="$DELIM" read -r src dest <<< "$entry"
  echo "  src='$src' dest='$dest'"
done

if [ "$DRY_RUN" = true ]; then
  echo "Dry run complete. Re-run with --apply to perform git mv operations."
  exit 0
fi

check_git_safety

cleanup() {
  info "Cleaning up temporary directories..."
  for d in "${TMPDIRS[@]:-}"; do
    [ -n "$d" ] && [ -d "$d" ] && rm -rf -- "$d" || true
  done
}
trap cleanup EXIT

echo "Applying moves..."
for entry in "${TO_MOVE[@]}"; do
  IFS="$DELIM" read -r src dest <<< "$entry"
  abs_src="$REPO_ROOT/$src"
  if [ ! -e "$abs_src" ]; then
    warn "Source $abs_src does not exist; skipping."
    continue
  fi

  if [ -e "$dest" ]; then
    warn "Destination $dest already exists; merging content."
    # Try to move children into the destination. Prefer git mv per-item to preserve history.
    if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      # Move contents of source into dest using git when possible
      shopt -s nullglob
      for item in "$abs_src"/* "$abs_src"/.*; do
        [ "$item" = "$abs_src/." ] || [ "$item" = "$abs_src/.." ] && continue
        item_base=$(basename -- "$item")
        target="$dest/$item_base"
        if [ -e "$target" ]; then
          warn "Target $target exists; skipping that entry to avoid overwrite."
          continue
        fi
        git mv -f -- "$item" "$target" || (mkdir -p "$(dirname -- "$target")" && mv -- "$item" "$target" && git add -- "$target")
      done
      shopt -u nullglob
      # Remove the now-empty source if possible
      rmdir -- "$abs_src" 2>/dev/null || true
    else
      # Non-git fallback: move filesystem contents
      mkdir -p -- "$dest"
      mv -- "$abs_src"/* "$dest/" 2>/dev/null || true
      rm -rf -- "$abs_src" || true
    fi
  else
    mkdir -p -- "$(dirname -- "$dest")"
    if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      git mv -- "$abs_src" "$dest"
    else
      mv -- "$abs_src" "$dest"
    fi
  fi
done

echo "Moves applied. Please run tests/CI and inspect changes, then commit and push."
