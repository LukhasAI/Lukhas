#!/bin/bash

# LUKHAS PWM Restore Script
# Restores audit logs, feedback data, and configuration from backup

set -euo pipefail

# Configuration
BACKUP_DIR="${LUKHAS_BACKUP_DIR:-./backups}"
S3_BUCKET="${LUKHAS_S3_BUCKET:-}"
RESTORE_DIR="${LUKHAS_RESTORE_DIR:-.}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] <backup_file_or_s3_key>

Restore LUKHAS backup from local file or S3

Options:
    -d, --dir DIR       Restore to directory (default: current directory)
    -f, --force         Overwrite existing files without prompting
    -s, --s3            Download from S3 (provide S3 key instead of file)
    -l, --list          List available backups
    -v, --verify        Verify backup integrity only (no restore)
    -h, --help          Show this help message

Examples:
    # Restore from local file
    $0 backups/lukhas_backup_20240101_120000.tar.gz

    # Restore from S3
    $0 -s lukhas-backups/lukhas_backup_20240101_120000.tar.gz

    # List available backups
    $0 -l

    # Verify backup without restoring
    $0 -v backups/lukhas_backup_20240101_120000.tar.gz
EOF
}

# Parse arguments
FORCE=false
FROM_S3=false
LIST_ONLY=false
VERIFY_ONLY=false
BACKUP_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dir)
            RESTORE_DIR="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -s|--s3)
            FROM_S3=true
            shift
            ;;
        -l|--list)
            LIST_ONLY=true
            shift
            ;;
        -v|--verify)
            VERIFY_ONLY=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            BACKUP_FILE="$1"
            shift
            ;;
    esac
done

# List backups if requested
if [ "$LIST_ONLY" = true ]; then
    log_info "Available local backups:"
    if [ -d "$BACKUP_DIR" ]; then
        ls -lht "$BACKUP_DIR"/lukhas_backup_*.tar.gz 2>/dev/null || log_warn "No local backups found"
    else
        log_warn "Backup directory not found: $BACKUP_DIR"
    fi
    
    if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
        echo ""
        log_info "Available S3 backups:"
        aws s3 ls "s3://$S3_BUCKET/lukhas-backups/" --recursive | grep ".tar.gz" | tail -10
    fi
    exit 0
fi

# Check if backup file specified
if [ -z "$BACKUP_FILE" ]; then
    log_error "No backup file specified"
    show_usage
    exit 1
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Download from S3 if needed
if [ "$FROM_S3" = true ]; then
    if [ -z "$S3_BUCKET" ]; then
        log_error "S3_BUCKET not configured"
        exit 1
    fi
    
    log_info "Downloading from S3: s3://$S3_BUCKET/$BACKUP_FILE"
    LOCAL_FILE="$TEMP_DIR/$(basename "$BACKUP_FILE")"
    
    aws s3 cp "s3://$S3_BUCKET/$BACKUP_FILE" "$LOCAL_FILE" || {
        log_error "Failed to download from S3"
        exit 1
    }
    
    # Also download checksum if available
    aws s3 cp "s3://$S3_BUCKET/${BACKUP_FILE%.tar.gz}.sha256" "$LOCAL_FILE.sha256" 2>/dev/null || true
    
    BACKUP_FILE="$LOCAL_FILE"
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Verify checksum if available
CHECKSUM_FILE="${BACKUP_FILE%.tar.gz}.sha256"
if [ -f "$CHECKSUM_FILE" ]; then
    log_info "Verifying backup integrity..."
    EXPECTED=$(cut -d' ' -f1 "$CHECKSUM_FILE")
    ACTUAL=$(sha256sum "$BACKUP_FILE" | cut -d' ' -f1)
    
    if [ "$EXPECTED" = "$ACTUAL" ]; then
        log_info "  Checksum verified: OK"
    else
        log_error "  Checksum mismatch!"
        log_error "  Expected: $EXPECTED"
        log_error "  Actual:   $ACTUAL"
        exit 1
    fi
else
    log_warn "No checksum file found - skipping verification"
fi

# If verify only, stop here
if [ "$VERIFY_ONLY" = true ]; then
    log_info "Backup verification complete"
    
    # Show contents
    log_info "Backup contents:"
    tar -tzf "$BACKUP_FILE" | head -20
    echo "..."
    
    exit 0
fi

# Check for existing data
if [ "$FORCE" != true ]; then
    EXISTING_DIRS=""
    [ -d "$RESTORE_DIR/.lukhas_audit" ] && EXISTING_DIRS="$EXISTING_DIRS .lukhas_audit"
    [ -d "$RESTORE_DIR/.lukhas_feedback" ] && EXISTING_DIRS="$EXISTING_DIRS .lukhas_feedback"
    
    if [ -n "$EXISTING_DIRS" ]; then
        log_warn "Found existing data directories:$EXISTING_DIRS"
        read -p "Overwrite existing data? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Restore cancelled"
            exit 0
        fi
    fi
fi

# Extract backup
log_info "Extracting backup to: $RESTORE_DIR"
mkdir -p "$RESTORE_DIR"

# Extract to temp first
cd "$TEMP_DIR"
tar -xzf "$BACKUP_FILE"

# Show metadata if present
if [ -f "metadata.json" ]; then
    log_info "Backup metadata:"
    jq -r '
        "  Created: " + .timestamp,
        "  Audit entries: " + (.audit_entries | tostring),
        "  Feedback entries: " + (.feedback_entries | tostring),
        "  Version: " + .lukhas_version
    ' metadata.json 2>/dev/null || cat metadata.json
fi

# Restore each component
cd - > /dev/null

# Restore audit logs
if [ -d "$TEMP_DIR/audit" ]; then
    log_info "Restoring audit logs..."
    mkdir -p "$RESTORE_DIR/.lukhas_audit"
    cp -r "$TEMP_DIR/audit"/* "$RESTORE_DIR/.lukhas_audit/" 2>/dev/null || true
    AUDIT_COUNT=$(find "$RESTORE_DIR/.lukhas_audit" -name "*.jsonl" -exec wc -l {} + 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo 0)
    log_info "  Restored $AUDIT_COUNT audit entries"
fi

# Restore feedback data
if [ -d "$TEMP_DIR/feedback" ]; then
    log_info "Restoring feedback data..."
    mkdir -p "$RESTORE_DIR/.lukhas_feedback"
    cp -r "$TEMP_DIR/feedback"/* "$RESTORE_DIR/.lukhas_feedback/" 2>/dev/null || true
    FEEDBACK_COUNT=$(find "$RESTORE_DIR/.lukhas_feedback" -name "*.jsonl" -exec wc -l {} + 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo 0)
    log_info "  Restored $FEEDBACK_COUNT feedback entries"
fi

# Restore configuration (with prompts)
if [ -d "$TEMP_DIR/config" ]; then
    log_info "Restoring configuration files..."
    for config_file in "$TEMP_DIR/config"/*; do
        if [ -f "$config_file" ]; then
            basename=$(basename "$config_file")
            target="$RESTORE_DIR/$basename"
            
            # Special handling for .env (never overwrite without prompt)
            if [ "$basename" = ".env" ] && [ -f "$target" ] && [ "$FORCE" != true ]; then
                log_warn "  .env exists - skipping (use --force to overwrite)"
                continue
            fi
            
            if [ -f "$target" ] && [ "$FORCE" != true ]; then
                read -p "  Overwrite $basename? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    continue
                fi
            fi
            
            cp "$config_file" "$target"
            log_info "  Restored: $basename"
        fi
    done
fi

# Restore analytics if present
if [ -d "$TEMP_DIR/analytics" ]; then
    log_info "Restoring analytics data..."
    mkdir -p "$RESTORE_DIR/.lukhas_analytics"
    cp -r "$TEMP_DIR/analytics"/* "$RESTORE_DIR/.lukhas_analytics/" 2>/dev/null || true
fi

# Create restore record
mkdir -p "$RESTORE_DIR/.lukhas_backup"
cat > "$RESTORE_DIR/.lukhas_backup/last_restore.json" <<EOF
{
    "restored_from": "$BACKUP_FILE",
    "restored_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "audit_entries": $AUDIT_COUNT,
    "feedback_entries": $FEEDBACK_COUNT
}
EOF

log_info "Restore completed successfully!"
log_info "Restored to: $RESTORE_DIR"

# Show summary
echo ""
log_info "Summary:"
[ -d "$RESTORE_DIR/.lukhas_audit" ] && log_info "  ✓ Audit logs restored"
[ -d "$RESTORE_DIR/.lukhas_feedback" ] && log_info "  ✓ Feedback data restored"
[ -d "$RESTORE_DIR/.lukhas_analytics" ] && log_info "  ✓ Analytics data restored"

# Remind about restarting services
echo ""
log_warn "Remember to restart LUKHAS services for changes to take effect:"
log_warn "  systemctl restart lukhas  # or"
log_warn "  python -m lukhas.api.app"

exit 0