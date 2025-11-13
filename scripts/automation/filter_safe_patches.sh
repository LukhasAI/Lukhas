#!/usr/bin/env bash
# Conservative filter for codmod patches.
# Classifies patches as safe (import reshapes) or flagged for manual review.

set -euo pipefail

PATCH_DIR=""
OUT_DIR=""
MAX_NON_IMPORT_DELETIONS=2

usage() {
  cat <<'USAGE'
Usage: filter_safe_patches.sh --patch-dir DIR --out-dir DIR [--max-non-import-deletions N]

Scans codmod patches and copies the safe subset to the output directory while
printing a summary of flagged patches with reasons.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --patch-dir)
      PATCH_DIR=${2-}
      shift 2
      ;;
    --out-dir)
      OUT_DIR=${2-}
      shift 2
      ;;
    --max-non-import-deletions)
      MAX_NON_IMPORT_DELETIONS=${2-}
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[error] Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$PATCH_DIR" || -z "$OUT_DIR" ]]; then
  echo "[error] --patch-dir and --out-dir are required" >&2
  usage >&2
  exit 1
fi

if [[ ! -d "$PATCH_DIR" ]]; then
  echo "[error] Patch directory $PATCH_DIR does not exist" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
FLAGGED_REPORT=${FLAGGED_REPORT:-"${OUT_DIR}/../flagged_patches.tsv"}
mkdir -p "$(dirname "$FLAGGED_REPORT")"
: > "$FLAGGED_REPORT"

echo -e "patch\treason" >> "$FLAGGED_REPORT"

mapfile -t RESULTS < <(python3 - "$PATCH_DIR" "$MAX_NON_IMPORT_DELETIONS" <<'PY'
import sys
from pathlib import Path

patch_dir = Path(sys.argv[1])
max_non_import = int(sys.argv[2])

for patch_path in sorted(patch_dir.glob('*.patch')):
    text = patch_path.read_text()
    lines = text.splitlines()

    contains_importlib = any(('importlib' in line or '_importlib' in line) for line in lines)
    contains_getattr_mod = any('getattr' in line and '_mod' in line for line in lines)

    status = 'safe'
    reason = ''

    if not contains_importlib:
        status = 'flagged'
        reason = 'missing importlib'
    elif not contains_getattr_mod:
        status = 'flagged'
        reason = 'missing getattr(_mod, ...)'
    else:
        for line in lines:
            if line.startswith('-'):
                continue
            if 'from labs' in line:
                status = 'flagged'
                reason = 'contains from labs'
                break

    if status == 'safe':
        total_deletions = 0
        non_import_deletions = 0
        for line in lines:
            if not line.startswith('-') or line.startswith('---'):
                continue
            total_deletions += 1
            stripped = line[1:].strip()
            if stripped.startswith('def '):
                status = 'flagged'
                reason = 'deleted function'
                break
            if stripped.startswith('class '):
                status = 'flagged'
                reason = 'deleted class'
                break
            if stripped:
                lowered = stripped.lstrip()
                if not (lowered.startswith('import ') or lowered.startswith('from ')):
                    non_import_deletions += 1
        else:
            if total_deletions > 10:
                status = 'flagged'
                reason = '>10 deletions'
            elif non_import_deletions > max_non_import:
                status = 'flagged'
                reason = '>max non-import deletions'

    print('\t'.join((patch_path.name, status, reason)))
PY
)

SAFE_COUNT=0
FLAGGED_COUNT=0
TOTAL=0

for entry in "${RESULTS[@]}"; do
  TOTAL=$((TOTAL + 1))
  IFS=$'\t' read -r name status reason <<<"$entry"
  if [[ "$status" == "safe" ]]; then
    cp "$PATCH_DIR/$name" "$OUT_DIR/"
    SAFE_COUNT=$((SAFE_COUNT + 1))
  else
    printf "%s\t%s\n" "$name" "$reason" >> "$FLAGGED_REPORT"
    FLAGGED_COUNT=$((FLAGGED_COUNT + 1))
  fi
done

cat <<SUMMARY
=== FILTER SUMMARY ===
Total patches scanned: $TOTAL
Safe patches: $SAFE_COUNT (copied to $OUT_DIR)
Flagged patches: $FLAGGED_COUNT
SUMMARY

if (( FLAGGED_COUNT > 0 )); then
  echo "[info] Flagged patch reasons recorded at $FLAGGED_REPORT"
fi

exit 0
