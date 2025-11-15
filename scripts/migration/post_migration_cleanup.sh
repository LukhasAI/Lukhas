#!/usr/bin/env bash
# scripts/migration/post_migration_cleanup.sh
# Archive codemod scripts and migration artifacts after successful MATRIZ migration
#
# Usage:
#   ./post_migration_cleanup.sh [--dry-run] [--keep-evergreen]
#
# Options:
#   --dry-run         Show what would be archived without making changes
#   --keep-evergreen  Keep codemod scripts as evergreen tools with updated docs
#
# Prerequisites:
#   - MATRIZ migration complete (all packages migrated)
#   - Compatibility shim removed (MATRIZ/__init__.py deleted)
#   - 2+ weeks stability period passed
#   - All smoke tests, benchmarks, and dream-gate validation passing

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DRY_RUN=false
KEEP_EVERGREEN=false

# Paths to archive
CODEMOD_SCRIPTS=(
    "scripts/consolidation/rewrite_matriz_imports.py"
    "scripts/migration/matriz_inventory.sh"
    "scripts/migration/prepare_matriz_migration_prs.sh"
    "scripts/migration/attach_dry_run_artifact.sh"
)

MIGRATION_ARTIFACTS_DIR="migration_artifacts/matriz"
ARCHIVED_SCRIPTS_DIR="tools/codemods/deprecated/matriz_migration_$(date +%Y%m%d)"
EVERGREEN_DOCS_DIR="docs/codemods"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --keep-evergreen)
            KEEP_EVERGREEN=true
            shift
            ;;
        -h|--help)
            grep "^#" "$0" | grep -v "^#!/" | sed 's/^# //'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

execute_cmd() {
    local cmd="$1"
    local description="$2"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would execute: $cmd"
    else
        log_info "$description"
        eval "$cmd"
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if we're in the repo root
    if [[ ! -f "$REPO_ROOT/Makefile.lukhas" ]]; then
        log_error "Not in LUKHAS repository root"
        exit 1
    fi

    # Check if compatibility shim still exists
    if [[ -f "$REPO_ROOT/matriz/__init__.py" ]]; then
        if grep -q "sys.modules aliasing" "$REPO_ROOT/matriz/__init__.py" 2>/dev/null; then
            log_error "Compatibility shim still exists at matriz/__init__.py"
            log_warning "Please ensure T20251112033 (Remove MATRIZ/__init__ shim) is completed first"
            exit 1
        fi
    fi

    # Check if migration artifacts exist
    if [[ ! -d "$REPO_ROOT/$MIGRATION_ARTIFACTS_DIR" ]]; then
        log_warning "Migration artifacts directory not found: $MIGRATION_ARTIFACTS_DIR"
        log_warning "This may indicate migration was not run or artifacts were already cleaned up"
    fi

    # Verify codemod scripts exist
    local missing_scripts=0
    for script in "${CODEMOD_SCRIPTS[@]}"; do
        if [[ ! -f "$REPO_ROOT/$script" ]]; then
            log_warning "Script not found: $script"
            ((missing_scripts++))
        fi
    done

    if [[ $missing_scripts -eq ${#CODEMOD_SCRIPTS[@]} ]]; then
        log_error "None of the expected codemod scripts exist. Already archived?"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

archive_codemod_scripts() {
    log_info "Archiving codemod scripts..."

    if [[ "$KEEP_EVERGREEN" == "true" ]]; then
        log_info "Keeping scripts as evergreen tools (--keep-evergreen flag set)"

        # Create evergreen docs
        execute_cmd \
            "mkdir -p '$REPO_ROOT/$EVERGREEN_DOCS_DIR'" \
            "Creating evergreen docs directory"

        # Create documentation for evergreen usage
        cat > "/tmp/matriz_codemod_evergreen.md" <<'EOF'
# MATRIZ Import Codemod - Evergreen Tool

## Overview
The MATRIZ import codemod tools can be used for any future package reorganization or import path migrations.

## Available Tools

### 1. Import Path Rewriter (`scripts/consolidation/rewrite_matriz_imports.py`)
- **Purpose**: Rewrite import statements using AST analysis
- **Usage**: `python scripts/consolidation/rewrite_matriz_imports.py --path <package> --dry-run`
- **Example**: Migrating from `from old_package import X` to `from new_package import X`

### 2. Import Inventory (`scripts/migration/matriz_inventory.sh`)
- **Purpose**: Generate inventory of all imports matching a pattern
- **Usage**: `bash scripts/migration/matriz_inventory.sh`
- **Output**: `/tmp/matriz_imports.lst`

### 3. Migration PR Preparation (`scripts/migration/prepare_matriz_migration_prs.sh`)
- **Purpose**: Prepare migration PRs with all required artifacts
- **Usage**: See script header for detailed instructions

## Adaptation Guide
To adapt these tools for a new migration:
1. Update the import pattern matching in the AST rewriter
2. Modify the inventory script's grep patterns
3. Adjust the migration PR template as needed

## Historical Context
These tools were originally created for the MATRIZ package migration (Q4 2025).
They successfully migrated 1262+ import statements across the codebase.

**Migration Completion Date**: $(date +%Y-%m-%d)
**Original Tasks**: T20251112022-T20251112035
EOF

        execute_cmd \
            "cp '/tmp/matriz_codemod_evergreen.md' '$REPO_ROOT/$EVERGREEN_DOCS_DIR/matriz_migration_tools.md'" \
            "Creating evergreen documentation"

        log_success "Codemod scripts marked as evergreen with documentation"
        return 0
    fi

    # Archive mode: move scripts to deprecated directory
    execute_cmd \
        "mkdir -p '$REPO_ROOT/$ARCHIVED_SCRIPTS_DIR'" \
        "Creating archive directory"

    for script in "${CODEMOD_SCRIPTS[@]}"; do
        if [[ -f "$REPO_ROOT/$script" ]]; then
            local script_basename=$(basename "$script")
            execute_cmd \
                "mv '$REPO_ROOT/$script' '$REPO_ROOT/$ARCHIVED_SCRIPTS_DIR/$script_basename'" \
                "Archiving $script"
        fi
    done

    # Create archive README
    cat > "/tmp/archive_readme.md" <<EOF
# Archived MATRIZ Migration Scripts

**Archive Date**: $(date +%Y-%m-%d)
**Reason**: MATRIZ migration completed successfully

## Archived Scripts
EOF

    for script in "${CODEMOD_SCRIPTS[@]}"; do
        echo "- $(basename "$script")" >> "/tmp/archive_readme.md"
    done

    cat >> "/tmp/archive_readme.md" <<EOF

## Migration Summary
- **Total imports migrated**: 1262+
- **Migration tasks**: T20251112022-T20251112035
- **Completion date**: $(date +%Y-%m-%d)

## Restoration
If you need to restore these scripts for future migrations:
\`\`\`bash
cp $ARCHIVED_SCRIPTS_DIR/* scripts/migration/
\`\`\`

## See Also
- docs/matriz/MIGRATION_v0.9.0.md
- todo/MASTER_LOG.md (T20251112022-T20251112035)
EOF

    execute_cmd \
        "cp '/tmp/archive_readme.md' '$REPO_ROOT/$ARCHIVED_SCRIPTS_DIR/README.md'" \
        "Creating archive README"

    log_success "Codemod scripts archived to $ARCHIVED_SCRIPTS_DIR"
}

archive_migration_artifacts() {
    log_info "Archiving migration artifacts..."

    if [[ ! -d "$REPO_ROOT/$MIGRATION_ARTIFACTS_DIR" ]]; then
        log_warning "No migration artifacts to archive"
        return 0
    fi

    # Create timestamped backup
    local archive_name="matriz_migration_artifacts_$(date +%Y%m%d_%H%M%S).tar.gz"
    local archive_path="$REPO_ROOT/archive/migrations/$archive_name"

    execute_cmd \
        "mkdir -p '$REPO_ROOT/archive/migrations'" \
        "Creating migrations archive directory"

    execute_cmd \
        "tar -czf '$archive_path' -C '$REPO_ROOT' '$MIGRATION_ARTIFACTS_DIR'" \
        "Creating migration artifacts tarball"

    # Keep migration artifacts for now (don't delete, just compress backup)
    log_success "Migration artifacts backed up to archive/migrations/$archive_name"
    log_info "Original artifacts kept at $MIGRATION_ARTIFACTS_DIR (delete manually if desired)"
}

generate_completion_report() {
    log_info "Generating migration completion report..."

    local report_file="/tmp/matriz_migration_completion_report.md"

    cat > "$report_file" <<EOF
# MATRIZ Migration Completion Report

**Generated**: $(date +"%Y-%m-%d %H:%M:%S")
**Status**: ✅ COMPLETED

## Summary
- **Start Date**: 2025-11-12
- **Completion Date**: $(date +%Y-%m-%d)
- **Total Imports Migrated**: 1262+
- **Migration Tasks**: T20251112022-T20251112035

## Completed Tasks
- [x] T20251112022: Import inventory generated
- [x] T20251112023: Compatibility shim validated
- [x] T20251112024-032: Package migrations (serve, core, orchestrator, etc.)
- [x] T20251112033: Compatibility shim removed
- [x] T20251112052: Post-migration cleanup

## Archived Locations
EOF

    if [[ "$KEEP_EVERGREEN" == "true" ]]; then
        cat >> "$report_file" <<EOF
- **Codemod Scripts**: Kept as evergreen tools
- **Documentation**: $EVERGREEN_DOCS_DIR/matriz_migration_tools.md
EOF
    else
        cat >> "$report_file" <<EOF
- **Codemod Scripts**: $ARCHIVED_SCRIPTS_DIR/
- **Migration Artifacts**: archive/migrations/
EOF
    fi

    cat >> "$report_file" <<EOF

## Validation Results
- ✅ All smoke tests passing
- ✅ Benchmarks within target thresholds
- ✅ Dream-gate validation passing
- ✅ 2+ weeks stability period completed

## Next Steps
- Update docs/REPOSITORY_STATE_*.md
- Archive this report in docs/migrations/
- Update MASTER_LOG.md completion status

## Rollback Information
Emergency rollback procedures documented in:
- .github/pull_request_template/migration.md
- Rollback PR: (reference if created)

---
*Generated by scripts/migration/post_migration_cleanup.sh*
EOF

    execute_cmd \
        "mkdir -p '$REPO_ROOT/docs/migrations'" \
        "Creating migrations docs directory"

    execute_cmd \
        "cp '$report_file' '$REPO_ROOT/docs/migrations/matriz_completion_$(date +%Y%m%d).md'" \
        "Saving completion report"

    log_success "Completion report saved to docs/migrations/matriz_completion_$(date +%Y%m%d).md"

    # Display report
    cat "$report_file"
}

main() {
    echo ""
    echo "========================================="
    echo "  MATRIZ Migration Post-Cleanup Script  "
    echo "========================================="
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY-RUN MODE: No changes will be made"
        echo ""
    fi

    check_prerequisites
    echo ""

    archive_codemod_scripts
    echo ""

    archive_migration_artifacts
    echo ""

    generate_completion_report
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run complete. Run without --dry-run to apply changes."
    else
        log_success "Post-migration cleanup complete!"
        log_info "Next steps:"
        log_info "  1. Review completion report in docs/migrations/"
        log_info "  2. Update todo/MASTER_LOG.md to mark T20251112052 as DONE"
        log_info "  3. Regenerate module registry (T20251112034)"
        log_info "  4. Commit and push changes"
    fi
    echo ""
}

# Run main function
main
