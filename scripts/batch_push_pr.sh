#!/usr/bin/env bash
set -euo pipefail
BRANCH="$(git branch --show-current)"
[ -n "$BRANCH" ] || { echo "No branch"; exit 1; }
git push --set-upstream origin "$BRANCH" || true
gh pr create --fill --head "$BRANCH" || true
echo "PR READY: $BRANCH"
