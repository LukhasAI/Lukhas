#!/bin/bash
# LUKHAS AI - Google Drive Incremental Sync
# Syncs only changed files since last sync to reduce upload time

set -e

REPO_DIR="/Users/agi_dev/LOCAL-REPOS/Lukhas"
GDRIVE_DIR="/Users/agi_dev/Google Drive/Lukhas"  # Adjust path
SYNC_STATE_FILE="$REPO_DIR/.sync_state"
TEMP_DIR="/tmp/lukhas_sync_$$"

echo "🔄 Starting LUKHAS incremental sync to Google Drive..."

# Create Google Drive directory if it doesn't exist
mkdir -p "$GDRIVE_DIR"

# Get last sync timestamp
if [ -f "$SYNC_STATE_FILE" ]; then
    LAST_SYNC=$(cat "$SYNC_STATE_FILE")
    echo "📅 Last sync: $(date -r $LAST_SYNC)"
else
    LAST_SYNC=0
    echo "📅 First sync - will copy all files"
fi

# Find changed files since last sync
echo "🔍 Finding changed files..."
mkdir -p "$TEMP_DIR"

# Get list of changed files
find "$REPO_DIR" -type f -newer "$SYNC_STATE_FILE" 2>/dev/null > "$TEMP_DIR/changed_files.txt" || true

# Always include key files even if not changed
cat >> "$TEMP_DIR/changed_files.txt" << EOF
$REPO_DIR/README.md
$REPO_DIR/package.json
$REPO_DIR/MATRIZ_CONSCIOUSNESS_ARCHITECTURE.md
EOF

# Exclude patterns
EXCLUDE_PATTERNS=(
    "*.git*"
    "*node_modules*"
    "*.venv*"
    "*__pycache__*"
    "*.pyc"
    "*test_results*"
    "*trace*"
    "*.log"
    "*temp*"
    "*tmp*"
)

# Filter and copy changed files
COPIED_COUNT=0
while IFS= read -r file; do
    # Skip if file doesn't exist
    [ ! -f "$file" ] && continue
    
    # Check exclude patterns
    SKIP=false
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            SKIP=true
            break
        fi
    done
    
    if [ "$SKIP" = false ]; then
        # Calculate relative path
        REL_PATH="${file#$REPO_DIR/}"
        DEST_FILE="$GDRIVE_DIR/$REL_PATH"
        
        # Create destination directory
        mkdir -p "$(dirname "$DEST_FILE")"
        
        # Copy file
        cp "$file" "$DEST_FILE"
        echo "📄 Copied: $REL_PATH"
        ((COPIED_COUNT++))
    fi
done < "$TEMP_DIR/changed_files.txt"

# Update sync timestamp
date +%s > "$SYNC_STATE_FILE"

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Sync complete! Copied $COPIED_COUNT files"
echo "📁 Google Drive location: $GDRIVE_DIR"