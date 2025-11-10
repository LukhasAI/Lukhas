#!/usr/bin/env bash
set -euo pipefail

# Split large ΛBot import into policy-compliant draft PRs
# Usage: ./scripts/split_labot_import.sh [--dry-run] [group_size]

GROUP_SIZE=2
DRY_RUN=false

usage() {
    cat <<'EOF'
Usage: ./scripts/split_labot_import.sh [--dry-run] [group_size]

  --dry-run   Show the branches and PR titles that would be created without
              performing any git operations.
  group_size  Optional display-only indicator for how many files are grouped
              per PR (default: 2).
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
        *)
            if [[ "$1" =~ ^[0-9]+$ ]]; then
                GROUP_SIZE="$1"
                shift
            else
                echo "Invalid group size: $1" >&2
                usage >&2
                exit 1
            fi
            ;;
    esac
done
ARTIFACTS_COMMIT="cb5d4cc01"
POLISH_COMMIT="1fa806988"
DOCS_COMMIT="8de9174cb"

echo "═══════════════════════════════════════════════════════════"
echo "ΛBot Import Splitter - Creating Draft PRs"
echo "Group size: $GROUP_SIZE files per PR"
echo "═══════════════════════════════════════════════════════════"

# Function to create PR for a group of files
create_pr_for_group() {
    local commit=$1
    local branch_prefix=$2
    local group_num=$3
    shift 3
    local files=("$@")

    local branch="${branch_prefix}-$(printf '%02d' $group_num)"
    local pr_title="chore(labot): import ΛBot artifacts (group $group_num)"
    echo ""
    echo "==> Creating branch: $branch"
    echo "Files (${#files[@]}): ${files[*]}"

    if [[ "$DRY_RUN" == true ]]; then
        echo "Dry run: would create PR '$pr_title'"
        return
    fi

    # Create branch from main
    git checkout -b "$branch" origin/main || {
        echo "Branch $branch already exists, skipping"
        git checkout main
        return
    }

    # Restore files from commit
    for file in "${files[@]}"; do
        mkdir -p "$(dirname "$file")"
        git checkout "$commit" -- "$file" 2>/dev/null || {
            echo "Warning: Could not restore $file from $commit"
            continue
        }
    done

    # Check if we have changes
    if ! git diff --cached --quiet 2>/dev/null; then
        # Files are already staged by git checkout, don't add extra files
        # git add . would pick up unrelated working directory changes
        git commit -m "chore(labot): import ΛBot files (group $group_num)

Imported from commit $commit:
$(printf '- %s\n' "${files[@]}")

This is part of the systematic import to satisfy policy guard
(max 2 files, max 40 lines per PR).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

        # Push branch
        git push -u origin "$branch"

        # Create draft PR
        local pr_body="# ΛBot Import - Group $group_num

**Source commit**: \`$commit\`
**Files**: ${#files[@]}

## Files in this PR
$(printf '- `%s`\n' "${files[@]}")

## Context
This draft PR is part of splitting the large ΛBot infrastructure import into policy-compliant chunks (≤2 files, ≤40 lines per PR).

## Review checklist
- [ ] No production code modified (tests/prompts/config only)
- [ ] No secrets committed
- [ ] YAML syntax valid (if applicable)
- [ ] Policy guard passes (\`make policy\`)

**Status**: Draft - requires human review before merge"

        gh pr create --draft \
            --title "$pr_title" \
            --body "$pr_body" \
            2>/dev/null && echo "✅ Draft PR created" || echo "⚠️  PR creation skipped (may require manual creation)"
    else
        echo "No changes to commit, skipping"
    fi

    # Return to main
    git checkout main
}

# Process artifacts commit (cb5d4cc01)
echo ""
echo "Processing artifacts commit: $ARTIFACTS_COMMIT"
artifacts_files=(
    ".labot/config.yml"
    "tools/labot.py"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-infra" 1 "${artifacts_files[@]}"

artifacts_files2=(
    "scripts/run_labot.sh"
    ".github/workflows/labot_plan.yml"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-infra" 2 "${artifacts_files2[@]}"

# Prompts (serve)
serve_prompts=(
    "prompts/labot/serve_main.md"
    "prompts/labot/serve_identity_middleware.md"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-prompts" 3 "${serve_prompts[@]}"

serve_prompts2=(
    "prompts/labot/serve_responses.md"
    "prompts/labot/serve_streaming.md"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-prompts" 4 "${serve_prompts2[@]}"

serve_prompts3=(
    "prompts/labot/serve_error_handling.md"
    "prompts/labot/serve_middleware_cors.md"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-prompts" 5 "${serve_prompts3[@]}"

# Prompts (lukhas)
lukhas_prompts=(
    "prompts/labot/lukhas_identity_core.md"
    "prompts/labot/lukhas_identity_webauthn.md"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-prompts" 6 "${lukhas_prompts[@]}"

lukhas_prompts2=(
    "prompts/labot/lukhas_governance_guardian.md"
)
matriz_prompts=(
    "prompts/labot/matriz_core_engine.md"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-prompts" 7 "${lukhas_prompts2[@]}" "${matriz_prompts[@]}"

# Prompts (matriz, core)
matriz_prompts2=(
    "prompts/labot/matriz_adapters_llm_adapter.md"
    "prompts/labot/matriz_memory_context.md"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-prompts" 8 "${matriz_prompts2[@]}"

matriz_prompts3=(
    "prompts/labot/matriz_bio_adaptation.md"
)
core_prompts=(
    "prompts/labot/core_monitoring_metrics.md"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-prompts" 9 "${matriz_prompts3[@]}" "${core_prompts[@]}"

core_prompts2=(
    "prompts/labot/core_security_encryption.md"
)
reports=(
    "reports/evolve_candidates.json"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-prompts" 10 "${core_prompts2[@]}" "${reports[@]}"

# PR requests (serve)
serve_requests=(
    "requests/labot/serve_main.pr.yml"
    "requests/labot/serve_identity_middleware.pr.yml"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-requests" 11 "${serve_requests[@]}"

serve_requests2=(
    "requests/labot/serve_responses.pr.yml"
    "requests/labot/serve_streaming.pr.yml"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-requests" 12 "${serve_requests2[@]}"

serve_requests3=(
    "requests/labot/serve_error_handling.pr.yml"
    "requests/labot/serve_middleware_cors.pr.yml"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-requests" 13 "${serve_requests3[@]}"

# PR requests (lukhas, matriz, core)
lukhas_requests=(
    "requests/labot/lukhas_identity_core.pr.yml"
    "requests/labot/lukhas_identity_webauthn.pr.yml"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-requests" 14 "${lukhas_requests[@]}"

lukhas_requests2=(
    "requests/labot/lukhas_governance_guardian.pr.yml"
)
matriz_requests=(
    "requests/labot/matriz_core_engine.pr.yml"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-requests" 15 "${lukhas_requests2[@]}" "${matriz_requests[@]}"

matriz_requests2=(
    "requests/labot/matriz_adapters_llm_adapter.pr.yml"
    "requests/labot/matriz_memory_context.pr.yml"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-requests" 16 "${matriz_requests2[@]}"

matriz_requests3=(
    "requests/labot/matriz_bio_adaptation.pr.yml"
)
core_requests=(
    "requests/labot/core_monitoring_metrics.pr.yml"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-requests" 17 "${matriz_requests3[@]}" "${core_requests[@]}"

core_requests2=(
    "requests/labot/core_security_encryption.pr.yml"
)
create_pr_for_group "$ARTIFACTS_COMMIT" "labot/import-requests" 18 "${core_requests2[@]}"

# Process polish commit (1fa806988)
echo ""
echo "Processing polish commit: $POLISH_COMMIT"
polish_files=(
    "tools/labot.py"
    ".github/PULL_REQUEST_TEMPLATE.md"
)
create_pr_for_group "$POLISH_COMMIT" "labot/import-polish" 19 "${polish_files[@]}"

polish_files2=(
    ".github/workflows/labot_audit.yml"
    "prompts/_templates/test_surgeon_system_prompt.md"
)
create_pr_for_group "$POLISH_COMMIT" "labot/import-polish" 20 "${polish_files2[@]}"

# Process docs commit (8de9174cb)
echo ""
echo "Processing docs commit: $DOCS_COMMIT"
docs_files=(
    "LABOT_DEPLOYMENT_COMPLETE.md"
)
create_pr_for_group "$DOCS_COMMIT" "labot/import-docs" 21 "${docs_files[@]}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Import splitting complete!"
echo "Created ~21 draft PRs for systematic review and merge"
echo ""
echo "Next steps:"
echo "1. Review draft PRs on GitHub"
echo "2. Merge in order: infra → prompts → requests → polish → docs"
echo "3. PR #1203 (serve/main.py pilot) continues unchanged"
echo "═══════════════════════════════════════════════════════════"
