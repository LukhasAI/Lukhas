#!/usr/bin/env bash
set -euo pipefail

# Block new direct imports of labs.* in production lanes (core/, lukhas/, serve/).
# Allows existing violations to be migrated by codemod, but prevents new ones.

changed_files=$(git diff --cached --name-only --diff-filter=ACM | tr '\n' ' ')

if [ -z "$changed_files" ]; then
  exit 0
fi

bad=$(echo "$changed_files" | xargs -n1 -I{} bash -lc '
  f="{}";
  case "$f" in
    core/*|lukhas/*|serve/*)
      if [ -f "$f" ] && echo "$f" | grep -E "\.py$" >/dev/null; then
        if rg -n "^\s*from\s+labs\.|^\s*import\s+labs\b" "$f" >/dev/null 2>&1; then
          echo "$f";
        fi
      fi
    ;;
  esac
')

if [ -n "$bad" ]; then
  echo "❌ Blocked: direct imports of labs.* found in production lanes:" >&2
  echo "$bad" | sed 's/^/  - /' >&2
  echo >&2
  echo "Use ProviderRegistry or lazy importlib-based access in functions." >&2
  echo "Docs: CLAUDE_CODEX_TODO.md (Provider/Lazy patterns)." >&2
  exit 1
fi

exit 0

