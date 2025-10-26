#!/usr/bin/env bash
# Auto-pick smallest remaining batch and run next item
set -euo pipefail

BATCH_MATRIZ="${BATCH_MATRIZ:-/tmp/batch_matriz.tsv}"
BATCH_CORE="${BATCH_CORE:-/tmp/batch_core.tsv}"
BATCH_SERVE="${BATCH_SERVE:-/tmp/batch_serve.tsv}"

count_remaining() {
    local batch="$1"
    local done_file="${batch}.done"
    local total=0
    local done_count=0

    [[ -f "$batch" ]] || return 0
    total=$(wc -l < "$batch")

    [[ -f "$done_file" ]] && done_count=$(wc -l < "$done_file") || done_count=0

    echo $((total - done_count))
}

# Find batch with smallest remaining
min_remaining=999999
pick=""

for batch in "$BATCH_MATRIZ" "$BATCH_CORE" "$BATCH_SERVE"; do
    remaining=$(count_remaining "$batch")
    if [[ $remaining -gt 0 ]] && [[ $remaining -lt $min_remaining ]]; then
        min_remaining=$remaining
        pick="$batch"
    fi
done

if [[ -z "$pick" ]]; then
    echo "✅ All batches complete!"
    exit 0
fi

echo "→ Running next from $(basename "$pick") ($min_remaining remaining)"
BATCH_FILE="$pick" exec "$(dirname "${BASH_SOURCE[0]}")/batch_next.sh"
