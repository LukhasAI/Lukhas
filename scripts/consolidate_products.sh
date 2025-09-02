#!/usr/bin/env bash
# Consolidate product bundles into top-level products/ dir.
# Usage:
#   ./scripts/consolidate_products.sh        # dry-run only
#   ./scripts/consolidate_products.sh --apply  # perform git mv operations

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$REPO_ROOT/products/manifest.txt"
if [ ! -f "$MANIFEST" ]; then
  MANIFEST="$REPO_ROOT/products/MANIFEST.md"
fi
DRY_RUN=true

if [ "${1-}" = "--apply" ]; then
  DRY_RUN=false
fi

echo "Products consolidation script"
echo "Repo root: $REPO_ROOT"
echo "Manifest: $MANIFEST"
echo "Dry run: $DRY_RUN"

if [ ! -f "$MANIFEST" ]; then
  echo "Manifest not found at $MANIFEST" >&2
  exit 2
fi

mkdir -p "$REPO_ROOT/products"

parse_manifest() {
  # parse lines like 'canonical -> relative/path'
  grep -E "^[[:alnum:]_\-]+[[:space:]]*->" "$MANIFEST" | sed -E 's/[[:space:]]*->[[:space:]]*/->/'
}

TO_MOVE=()
DELIM=$'\x1f'
while read -r line; do
  # split on '->'
  IFS='->' read -r key val <<< "$line" || continue
  canonical=$(echo "$key" | xargs)
  src=$(echo "$val" | xargs | sed -E 's/^[^[:alnum:]\/]*//; s/[^[:alnum:]\/_\-\.]*$//')
  if [ -z "$canonical" ] || [ -z "$src" ]; then
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

echo "Applying moves..."
for entry in "${TO_MOVE[@]}"; do
  IFS="$DELIM" read -r src dest <<< "$entry"
  if [ ! -e "$REPO_ROOT/$src" ]; then
    echo "Source $src does not exist; skipping." >&2
    continue
  fi
  if [ -e "$dest" ]; then
    echo "Destination $dest already exists; merging content." >&2
    # merge: create a temporary dir and move contents
    tmpdir=$(mktemp -d)
    git mv "$REPO_ROOT/$src" "$tmpdir/" || true
    mkdir -p "$dest"
    mv "$tmpdir/$(basename "$src")"/* "$dest/" || true
    rmdir "$tmpdir/$(basename "$src")" || true
    rmdir "$tmpdir" || true
  else
    mkdir -p "$(dirname "$dest")"
    git mv "$REPO_ROOT/$src" "$dest"
  fi
done

echo "Moves applied. Please run tests/CI and inspect changes, then commit and push."
