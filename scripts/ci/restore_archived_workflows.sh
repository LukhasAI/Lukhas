#!/bin/bash
# Restores archived GitHub workflows from .github/workflows.archived to .github/workflows

set -euo pipefail

ARCHIVE_DIR=".github/workflows.archived"
TARGET_DIR=".github/workflows"
DRY_RUN=false

usage() {
  echo "Usage: $0 [--dry-run]"
  echo "  --dry-run: List changes without moving files."
  exit 1
}

if [ "${1:-}" == "--dry-run" ]; then
  DRY_RUN=true
fi

if [ ! -d "$ARCHIVE_DIR" ]; then
  echo "Archive directory not found: $ARCHIVE_DIR"
  exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
  echo "Target directory not found: $TARGET_DIR. Creating it..."
  mkdir -p "$TARGET_DIR"
fi

echo "Checking for workflows to restore..."
for workflow in "$ARCHIVE_DIR"/*.yml; do
  if [ -f "$workflow" ]; then
    filename=$(basename "$workflow")
    if [ "$DRY_RUN" == "true" ]; then
      echo "[Dry Run] Would move $filename to $TARGET_DIR"
    else
      echo "Restoring $filename..."
      mv "$workflow" "$TARGET_DIR/"
    fi
  fi
done

echo "Done."
