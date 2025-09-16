#!/bin/bash
# LUKHAS Context Files Synchronization System
# Automatically keeps claude.me and lukhas_context.md files synchronized
# Supports bidirectional sync and automatic updates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HEADER="# LUKHAS AI Context - Vendor-Neutral AI Guidance
*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*

---

"

echo "🔄 LUKHAS Context Files Synchronization System"
echo "=============================================="
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --claude-to-lukhas     Sync from claude.me to lukhas_context.md (default)"
    echo "  --lukhas-to-claude     Sync from lukhas_context.md to claude.me"
    echo "  --bidirectional        Sync based on modification time (newer wins)"
    echo "  --check-status         Check sync status without making changes"
    echo "  --add-missing          Create missing partner files"
    echo "  --dry-run              Show what would be done without making changes"
    echo "  --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Default: sync claude.me → lukhas_context.md"
    echo "  $0 --bidirectional     # Smart sync based on file modification times"
    echo "  $0 --check-status      # Check which files are out of sync"
    echo "  $0 --add-missing       # Create any missing partner files"
}

# Default options
SYNC_DIRECTION="claude-to-lukhas"
DRY_RUN=false
CHECK_STATUS=false
ADD_MISSING=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --claude-to-lukhas)
            SYNC_DIRECTION="claude-to-lukhas"
            shift
            ;;
        --lukhas-to-claude)
            SYNC_DIRECTION="lukhas-to-claude"
            shift
            ;;
        --bidirectional)
            SYNC_DIRECTION="bidirectional"
            shift
            ;;
        --check-status)
            CHECK_STATUS=true
            shift
            ;;
        --add-missing)
            ADD_MISSING=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Counters
checked=0
synced=0
created=0
skipped=0
errors=0

# Function to add header to lukhas_context.md
add_lukhas_header() {
    local file="$1"
    local temp_file=$(mktemp)

    if ! grep -q "LUKHAS AI Context - Vendor-Neutral AI Guidance" "$file" 2>/dev/null; then
        echo "$HEADER" > "$temp_file"
        if [ -f "$file" ]; then
            cat "$file" >> "$temp_file"
        fi
        if [ "$DRY_RUN" = false ]; then
            mv "$temp_file" "$file"
        else
            rm "$temp_file"
        fi
        return 0
    else
        rm -f "$temp_file"
        return 1
    fi
}

# Function to remove header from lukhas_context.md for claude.me
remove_lukhas_header() {
    local file="$1"
    local temp_file=$(mktemp)

    # Skip the header section (everything until the first line after "---")
    awk '
        BEGIN { skip = 1 }
        /^---$/ { skip = 0; next }
        !skip { print }
    ' "$file" > "$temp_file"

    cat "$temp_file"
    rm "$temp_file"
}

# Function to sync files
sync_files() {
    local source_file="$1"
    local target_file="$2"
    local direction="$3"

    if [ ! -f "$source_file" ]; then
        echo -e "${RED}Source file not found: $source_file${NC}"
        return 1
    fi

    local target_dir=$(dirname "$target_file")
    mkdir -p "$target_dir"

    if [ "$direction" = "claude-to-lukhas" ]; then
        if [ "$DRY_RUN" = false ]; then
            cp "$source_file" "$target_file"
            add_lukhas_header "$target_file"
        fi
        echo -e "${GREEN}Claude → LUKHAS: $source_file → $target_file${NC}"
    else
        if [ "$DRY_RUN" = false ]; then
            remove_lukhas_header "$source_file" > "$target_file"
        fi
        echo -e "${GREEN}LUKHAS → Claude: $source_file → $target_file${NC}"
    fi
}

# Function to check if files need sync
files_need_sync() {
    local file1="$1"
    local file2="$2"

    if [ ! -f "$file1" ] || [ ! -f "$file2" ]; then
        return 0  # Need sync if either file missing
    fi

    # Compare content (ignoring LUKHAS header)
    local temp1=$(mktemp)
    local temp2=$(mktemp)

    if [[ "$file1" == *"lukhas_context.md" ]]; then
        remove_lukhas_header "$file1" > "$temp1"
        cp "$file2" "$temp2"
    else
        cp "$file1" "$temp1"
        remove_lukhas_header "$file2" > "$temp2"
    fi

    if diff -q "$temp1" "$temp2" >/dev/null 2>&1; then
        rm "$temp1" "$temp2"
        return 1  # Files are in sync
    else
        rm "$temp1" "$temp2"
        return 0  # Files need sync
    fi
}

echo -e "${BLUE}Mode: $SYNC_DIRECTION${NC}"
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}DRY RUN MODE: No files will be modified${NC}"
fi
echo ""

# Find all claude.me files
claude_files=$(find . -name "claude.me" -type f | sort)

if [ "$CHECK_STATUS" = true ]; then
    echo -e "${BLUE}Checking synchronization status...${NC}"
    echo ""
fi

while IFS= read -r claude_file; do
    if [ -z "$claude_file" ]; then
        continue
    fi

    checked=$((checked + 1))
    dir=$(dirname "$claude_file")
    lukhas_file="$dir/lukhas_context.md"

    if [ "$CHECK_STATUS" = true ]; then
        echo -n "[$checked] $dir: "
        if [ -f "$lukhas_file" ]; then
            if files_need_sync "$claude_file" "$lukhas_file"; then
                echo -e "${YELLOW}OUT OF SYNC${NC}"
            else
                echo -e "${GREEN}IN SYNC${NC}"
            fi
        else
            echo -e "${RED}MISSING lukhas_context.md${NC}"
        fi
        continue
    fi

    # Add missing files if requested
    if [ "$ADD_MISSING" = true ]; then
        if [ ! -f "$lukhas_file" ]; then
            echo -n "Creating missing: $lukhas_file ... "
            if [ "$DRY_RUN" = false ]; then
                sync_files "$claude_file" "$lukhas_file" "claude-to-lukhas"
                created=$((created + 1))
            else
                echo -e "${GREEN}WOULD CREATE${NC}"
            fi
            continue
        fi
    fi

    # Skip if partner file doesn't exist and we're not adding missing
    if [ ! -f "$lukhas_file" ] && [ "$ADD_MISSING" = false ]; then
        echo -e "${YELLOW}Skipping $claude_file (no partner file)${NC}"
        skipped=$((skipped + 1))
        continue
    fi

    # Determine sync direction
    actual_direction="$SYNC_DIRECTION"
    if [ "$SYNC_DIRECTION" = "bidirectional" ]; then
        if [ -f "$lukhas_file" ]; then
            if [ "$claude_file" -nt "$lukhas_file" ]; then
                actual_direction="claude-to-lukhas"
            else
                actual_direction="lukhas-to-claude"
            fi
        else
            actual_direction="claude-to-lukhas"
        fi
    fi

    # Check if sync is needed
    if files_need_sync "$claude_file" "$lukhas_file"; then
        echo -n "[$checked] Syncing: "
        if [ "$actual_direction" = "claude-to-lukhas" ]; then
            sync_files "$claude_file" "$lukhas_file" "claude-to-lukhas"
        else
            sync_files "$lukhas_file" "$claude_file" "lukhas-to-claude"
        fi
        synced=$((synced + 1))
    else
        echo -e "${GREEN}[$checked] Already in sync: $dir${NC}"
        skipped=$((skipped + 1))
    fi

done <<< "$claude_files"

echo ""
echo -e "${BLUE}Synchronization Summary:${NC}"
echo "Files checked: $checked"
if [ "$CHECK_STATUS" = false ]; then
    echo "Files synchronized: $synced"
    echo "Files created: $created"
    echo "Files skipped: $skipped"
    echo "Errors: $errors"

    if [ "$DRY_RUN" = false ] && [ $synced -gt 0 -o $created -gt 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Synchronization completed successfully!${NC}"
        echo ""
        echo "Next steps:"
        echo "• Review changes with: git diff"
        echo "• Commit changes: git add . && git commit -m 'sync: Update context files'"
        echo "• Set up automatic sync with git hooks (optional)"
    elif [ "$DRY_RUN" = true ]; then
        echo ""
        echo -e "${YELLOW}DRY RUN completed. Run without --dry-run to apply changes.${NC}"
    fi
fi
