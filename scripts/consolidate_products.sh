#!/usr/bin/env bash
# Consolidate product bundles into top-level products/ dir.
# Usage (safe defaults):
#   ./scripts/consolidate_products.sh                # dry-run only (default)
#   ./scripts/consolidate_products.sh --apply --confirm  # actually perform git mv operations
#
# Notes:
# - This script is conservative by default and will only print planned moves.
# - To apply changes you must pass both --apply and --confirm to avoid accidental modifications.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$REPO_ROOT/products/manifest.txt"
if [ ! -f "$MANIFEST" ]; then
  MANIFEST="$REPO_ROOT/products/MANIFEST.md"
fi
DRY_RUN=true
CONFIRM=false

if [ "${1-}" = "--apply" ]; then
  DRY_RUN=false
fi

if [ "${1-}" = "--confirm" ] || [ "${2-}" = "--confirm" ]; then
  CONFIRM=true
fi

echo "Products consolidation script - dry-run by default"
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
  echo "Dry run complete. Re-run with --apply --confirm to perform git mv operations."
  exit 0
fi

if [ "$CONFIRM" != true ]; then
  echo "Apply requested but --confirm not provided. Aborting to avoid accidental moves." >&2
  exit 3
fi

echo "Applying moves..."
for entry in "${TO_MOVE[@]}"; do
  IFS="$DELIM" read -r src dest <<< "$entry"
  if [ ! -e "$REPO_ROOT/$src" ]; then
    echo "Source $src does not exist; skipping." >&2
    continue
  fi
  if [ -e "$dest" ]; then
    echo "Destination $dest already exists; merging content safely." >&2
    # merge contents into destination using rsync to avoid partial git mv behavior
    mkdir -p "$dest"
    rsync -a --remove-source-files "$REPO_ROOT/$src/" "$dest/"
    # remove empty source directory
    find "$REPO_ROOT/$src" -type f -maxdepth 1 -print -quit | grep -q . || rmdir "$REPO_ROOT/$src" || true
  else
    mkdir -p "$(dirname "$dest")"
    git mv "$REPO_ROOT/$src" "$dest"
  fi
done

echo "Moves applied. Please run tests/CI and inspect changes, then commit and push."
