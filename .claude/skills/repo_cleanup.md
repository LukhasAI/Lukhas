# Repository Cleanup Skill

Enforce repository hygiene and standard project layout for LUKHΛS. Scans the root and subdirectories (using lukhas_context.md files) and produces a safe, reversible plan to tidy the root, archive or relocate orphaned files, enforce naming conventions, and surface structural inconsistencies for human review.

## Reasoning

1. Discover authoritative context files (lukhas_context.md) across the repository to understand each directory's intended purpose and owner. This avoids blind deletions and preserves module intent.

2. Compare the actual file tree against declared structure in MODULE_INDEX.md and the contexts to find misplaced files (e.g., large scripts in project root; assets in source folders).

3. Apply conservative rules inspired by world-class engineering teams (Altman/Amodei/Hassabis/Jobs): keep root minimal, put libraries under src/ or module/, tests under tests/, docs under docs/, CI under .github/, and archives under /archive. Jobs-style design: reduce cognitive load at entry points (README + 1-liner to get started).

4. Produce explicit, reversible file-move/rename operations and a proposed PR template, not destructive deletions. Prepare an /archive/ folder for legacy artifacts with metadata preserved.

5. Provide automation (bash script + dry-run) and a checklist for maintainers, plus a final report that references each lukhas_context.md used so ownership stays visible.

## Actions

### High-level outputs produced by this skill:
- A dry-run report listing candidate moves/renames and the rationale for each.
- A safe `scripts/lukhas_repo_cleanup.sh` that can be executed with `--dry-run` and `--apply` flags.
- A recommended PR checklist and proposed MODULE_INDEX.md updates.

### Suggested `scripts/lukhas_repo_cleanup.sh` (safe by default; run with `--apply` to change files):

```bash
#!/usr/bin/env bash
set -euo pipefail
DRY_RUN=true
if [[ "${1-}" == "--apply" ]]; then DRY_RUN=false; fi
ROOT=$(git rev-parse --show-toplevel)
ARCHIVE_DIR="$ROOT/archive/$(date +%Y%m%d_%H%M%S)_cleanup"
mkdir -p "$ARCHIVE_DIR"

echo "Scanning repository for cleanup candidates..."
# 1) Files that should not live in root (examples)
CANDIDATES=()
while IFS= read -r -d '' f; do
  # rule: no .py files in root except manage.py or minimal scripts
  fn=$(basename "$f")
  if [[ "$f" =~ "/[^/]+\.py$" ]] && [[ "$f" != "$ROOT/manage.py" ]] && [[ "$f" != "$ROOT/setup.py" ]]; then
    CANDIDATES+=("$f")
  fi
done < <(find "$ROOT" -maxdepth 2 -type f -name '*.py' -print0)

echo "Candidates: ${CANDIDATES[*]:-<none>}"
for f in "${CANDIDATES[@]}"; do
  targ="$ROOT/src/$(basename "$f")"
  echo "Proposed: $f -> $targ"
  if [[ "$DRY_RUN" = false ]]; then
    mkdir -p "$(dirname "$targ")"
    git mv "$f" "$targ" || mv "$f" "$ARCHIVE_DIR/"
  fi
done

echo "Suggested manual checks:"
echo "- Review large binaries in repo root (move to /assets or /archive)."
echo "- Consolidate documentation under /docs/; ensure README is entry point."
echo "- Run 'scripts/context_coverage_bot.py' to ensure each module has a lukhas_context.md."

if [[ "$DRY_RUN" = true ]]; then
  echo "Dry-run complete. Re-run with --apply to perform moves (creates archive)."
else
  echo "Apply complete. Commit created by git mv operations; please review."
fi
```

### PR checklist (to include in `.github/PULL_REQUEST_TEMPLATE.md`):
- [ ] `lukhas_context.md` present/updated in modified directories.
- [ ] MODULE_INDEX.md updated if module moved/renamed.
- [ ] No large binaries >5MB added to repo root (if necessary, moved to /assets or /archive).
- [ ] All moved files referenced by README and tests updated.

### Notes on human review
Always run the dry-run report, then inspect proposed moves. The script only proposes moves and archives fallbacks; maintainers must verify ownership before destructive changes.

## Context References

- `/api/lukhas_context.md`
- `/consciousness/simulation/lukhas_context.md`
- `/MODULE_INDEX.md`
- `/docs/CONTEXT_FILES.md`
- `/scripts/generate_lukhas_context.sh`
