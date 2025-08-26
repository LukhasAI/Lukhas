#!/bin/bash
# COMPREHENSIVE SAFE RECOVERY SCRIPT
# Automatically recovers all files with discoverable content from git history

echo "🚀 LUKHAS COMPREHENSIVE FILE RECOVERY"
echo "====================================="
echo "Timestamp: $(date)"
echo ""

# Create recovery log
RECOVERY_LOG="/tmp/lukhas_recovery_$(date +%Y%m%d_%H%M%S).log"
BACKUP_DIR="/tmp/lukhas_recovery_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

log() {
    echo "$1" | tee -a "$RECOVERY_LOG"
}

log "🔧 Starting comprehensive recovery process..."
log "📁 Backup directory: $BACKUP_DIR"
log "📝 Recovery log: $RECOVERY_LOG"
log ""

# Get all suspicious files from our previous analysis
SUSPICIOUS_FILES=(
    $(cat /tmp/lukhas_recovery_analysis/suspicious_md_files.txt)
    $(cat /tmp/lukhas_recovery_analysis/suspicious_py_files.txt)
    $(cat /tmp/lukhas_recovery_analysis/suspicious_script_files.txt)
    $(cat /tmp/lukhas_recovery_analysis/suspicious_json_files.txt)
)

log "📊 RECOVERY STATISTICS:"
log "Total files to check: ${#SUSPICIOUS_FILES[@]}"
log ""

RECOVERED_COUNT=0
SKIPPED_COUNT=0
ERROR_COUNT=0

for file in "${SUSPICIOUS_FILES[@]}"; do
    # Skip if file doesn't exist or starts with ./
    file=${file#./}  # Remove leading ./
    
    if [ ! -f "$file" ]; then
        log "⚠️  SKIP: $file (doesn't exist)"
        ((SKIPPED_COUNT++))
        continue
    fi
    
    # Skip if file already has content
    if [ -s "$file" ]; then
        log "✅ SKIP: $file (already has content: $(wc -c < "$file") bytes)"
        ((SKIPPED_COUNT++))
        continue
    fi
    
    log "🔍 Checking: $file"
    
    # Look for content in git history (last 30 commits)
    FOUND_CONTENT=false
    FOUND_COMMIT=""
    
    for i in {1..30}; do
        if git show HEAD~$i:"$file" >/dev/null 2>&1; then
            size=$(git show HEAD~$i:"$file" 2>/dev/null | wc -c)
            if [ "$size" -gt 0 ]; then
                FOUND_COMMIT="HEAD~$i"
                FOUND_CONTENT=true
                log "  ✅ Found content in $FOUND_COMMIT ($size bytes)"
                break
            fi
        fi
    done
    
    if [ "$FOUND_CONTENT" = true ]; then
        # Create backup of empty file
        cp "$file" "$BACKUP_DIR/$(basename "$file").empty.backup" 2>/dev/null
        
        # Restore content
        if git show "$FOUND_COMMIT":"$file" > "$file" 2>/dev/null; then
            new_size=$(wc -c < "$file")
            log "  🎉 RESTORED: $file ($new_size bytes from $FOUND_COMMIT)"
            ((RECOVERED_COUNT++))
        else
            log "  ❌ ERROR: Failed to restore $file from $FOUND_COMMIT"
            ((ERROR_COUNT++))
        fi
    else
        log "  ❌ NO CONTENT: $file (not found in git history)"
        ((SKIPPED_COUNT++))
    fi
done

log ""
log "📊 FINAL RECOVERY STATISTICS:"
log "================================"
log "✅ Successfully recovered: $RECOVERED_COUNT files"
log "⚠️  Skipped (no content found): $SKIPPED_COUNT files"
log "❌ Errors: $ERROR_COUNT files"
log "📁 Empty file backups saved to: $BACKUP_DIR"
log "📝 Full log: $RECOVERY_LOG"
log ""

if [ $RECOVERED_COUNT -gt 0 ]; then
    log "🎯 NEXT STEPS:"
    log "1. Review recovered files for correctness"
    log "2. Test that the repository still works"
    log "3. Commit recovered files: git add . && git commit -m 'recover: Restore $(RECOVERED_COUNT) files from git history'"
    log ""
    log "🔍 TO REVIEW RECOVERED FILES:"
    log "git status --porcelain | grep '^M'"
else
    log "😔 No files were recovered. This might indicate:"
    log "1. Files were always meant to be empty"
    log "2. Content exists in very old commits (>30 commits back)"
    log "3. Files were created empty and never had content"
fi

echo ""
echo "📋 Recovery complete! Check the log for details:"
echo "cat $RECOVERY_LOG"
