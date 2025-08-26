#!/bin/bash

# ΛiD Authentication System Key Management Utilities
#
# This script provides utilities for managing RSA keys, JWKS rotation,
# and other cryptographic operations for the authentication system.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
KEYS_DIR="keys"
BACKUP_DIR="keys/backup"
LOG_FILE="keys/key-management.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Print usage information
usage() {
    echo -e "${BLUE}ΛiD Authentication System - Key Management Utilities${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  generate-jwt-keys    Generate new RSA key pair for JWT signing"
    echo "  rotate-keys         Rotate existing JWT keys (backup and generate new)"
    echo "  generate-totp       Generate new TOTP secret for break-glass access"
    echo "  validate-keys       Validate existing key pairs"
    echo "  backup-keys         Backup all keys to secure storage"
    echo "  restore-keys        Restore keys from backup"
    echo "  clean-old-keys      Remove old key backups (keeps last 3)"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -v, --verbose       Enable verbose output"
    echo "  --key-size SIZE     RSA key size (default: 2048)"
    echo "  --env-file FILE     Environment file to update (default: .env)"
    echo ""
    echo "Examples:"
    echo "  $0 generate-jwt-keys --key-size 4096"
    echo "  $0 rotate-keys --env-file .env.production"
    echo "  $0 generate-totp"
}

# Check dependencies
check_dependencies() {
    local deps=("openssl" "base64" "jq")

    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            echo -e "${RED}❌ Error: $dep is required but not installed.${NC}"
            exit 1
        fi
    done
}

# Create directories
setup_directories() {
    mkdir -p "$KEYS_DIR" "$BACKUP_DIR"
    touch "$LOG_FILE"
}

# Generate RSA key pair for JWT signing
generate_jwt_keys() {
    local key_size=${1:-2048}
    local key_id=${2:-"lukhas-auth-$(date +%Y-%m-%d)-$(openssl rand -hex 4)"}

    log "Generating RSA key pair (size: $key_size, id: $key_id)"

    local private_key_file="$KEYS_DIR/jwt-private-$key_id.pem"
    local public_key_file="$KEYS_DIR/jwt-public-$key_id.pem"

    # Generate private key
    openssl genpkey \
        -algorithm RSA \
        -out "$private_key_file" \
        -pkcs8 \
        -outform PEM \
        "$key_size"

    # Extract public key
    openssl rsa \
        -in "$private_key_file" \
        -pubout \
        -out "$public_key_file"

    # Set appropriate permissions
    chmod 600 "$private_key_file"
    chmod 644 "$public_key_file"

    # Base64 encode for environment variables
    local private_b64=$(base64 -w 0 < "$private_key_file")
    local public_b64=$(base64 -w 0 < "$public_key_file")

    echo -e "${GREEN}✅ JWT keys generated successfully:${NC}"
    echo "   Private key: $private_key_file"
    echo "   Public key:  $public_key_file"
    echo ""
    echo -e "${YELLOW}📋 Environment variables:${NC}"
    echo "JWT_PRIVATE_KEY=$private_b64"
    echo "JWT_PUBLIC_KEY=$public_b64"
    echo "JWT_KEY_ID=$key_id"

    log "JWT keys generated: $key_id"
}

# Rotate existing JWT keys
rotate_keys() {
    local env_file=${1:-.env}

    log "Starting key rotation process"

    # Backup existing keys
    if [[ -f "$env_file" ]]; then
        backup_env_keys "$env_file"
    fi

    # Generate new keys
    local new_key_id="lukhas-auth-$(date +%Y-%m-%d)-$(openssl rand -hex 4)"
    generate_jwt_keys 2048 "$new_key_id"

    # Update environment file if it exists
    if [[ -f "$env_file" ]]; then
        update_env_file "$env_file" "$new_key_id"
    fi

    echo -e "${GREEN}✅ Key rotation completed${NC}"
    echo -e "${YELLOW}⚠️  Update your production environment with the new keys${NC}"
    echo -e "${YELLOW}⚠️  Keep old keys active for 30 days for JWT validation${NC}"

    log "Key rotation completed: $new_key_id"
}

# Backup keys from environment file
backup_env_keys() {
    local env_file="$1"
    local backup_file="$BACKUP_DIR/env-keys-$(date +%Y%m%d-%H%M%S).env"

    grep -E "^(JWT_PRIVATE_KEY|JWT_PUBLIC_KEY|JWT_KEY_ID)=" "$env_file" > "$backup_file" 2>/dev/null || true

    if [[ -s "$backup_file" ]]; then
        chmod 600 "$backup_file"
        echo -e "${GREEN}🔐 Keys backed up to: $backup_file${NC}"
        log "Environment keys backed up to: $backup_file"
    fi
}

# Update environment file with new keys
update_env_file() {
    local env_file="$1"
    local key_id="$2"

    local private_key_file="$KEYS_DIR/jwt-private-$key_id.pem"
    local public_key_file="$KEYS_DIR/jwt-public-$key_id.pem"

    if [[ ! -f "$private_key_file" || ! -f "$public_key_file" ]]; then
        echo -e "${RED}❌ Key files not found for key ID: $key_id${NC}"
        return 1
    fi

    local private_b64=$(base64 -w 0 < "$private_key_file")
    local public_b64=$(base64 -w 0 < "$public_key_file")

    # Create temporary file with new values
    local temp_file=$(mktemp)

    # Copy existing file and update JWT keys
    while IFS= read -r line; do
        if [[ "$line" =~ ^JWT_PRIVATE_KEY= ]]; then
            echo "JWT_PRIVATE_KEY=$private_b64"
        elif [[ "$line" =~ ^JWT_PUBLIC_KEY= ]]; then
            echo "JWT_PUBLIC_KEY=$public_b64"
        elif [[ "$line" =~ ^JWT_KEY_ID= ]]; then
            echo "JWT_KEY_ID=$key_id"
        else
            echo "$line"
        fi
    done < "$env_file" > "$temp_file"

    # Replace original file
    mv "$temp_file" "$env_file"
    chmod 600 "$env_file"

    echo -e "${GREEN}✅ Environment file updated: $env_file${NC}"
    log "Environment file updated with new keys: $key_id"
}

# Generate TOTP secret for break-glass access
generate_totp() {
    local totp_secret=$(openssl rand -base64 32)
    local totp_file="$KEYS_DIR/break-glass-totp-$(date +%Y%m%d-%H%M%S).secret"

    echo "$totp_secret" > "$totp_file"
    chmod 600 "$totp_file"

    echo -e "${GREEN}✅ TOTP secret generated:${NC}"
    echo "   File: $totp_file"
    echo "   Secret: $totp_secret"
    echo ""
    echo -e "${YELLOW}📱 QR Code for authenticator app:${NC}"
    echo "   Manual entry: $totp_secret"
    echo ""
    echo -e "${YELLOW}📋 Environment variable:${NC}"
    echo "BREAK_GLASS_TOTP_SECRET=$totp_secret"

    log "TOTP secret generated for break-glass access"
}

# Validate existing key pairs
validate_keys() {
    local valid=0
    local invalid=0

    echo -e "${BLUE}🔍 Validating JWT key pairs...${NC}"

    for private_key in "$KEYS_DIR"/jwt-private-*.pem; do
        if [[ ! -f "$private_key" ]]; then
            continue
        fi

        local key_id=$(basename "$private_key" .pem | sed 's/jwt-private-//')
        local public_key="$KEYS_DIR/jwt-public-$key_id.pem"

        if [[ ! -f "$public_key" ]]; then
            echo -e "${RED}❌ Missing public key for: $key_id${NC}"
            ((invalid++))
            continue
        fi

        # Test key pair by signing and verifying
        local test_data="test-signature-$(date +%s)"
        local signature_file=$(mktemp)

        if echo "$test_data" | openssl dgst -sha256 -sign "$private_key" -out "$signature_file" && \
           echo "$test_data" | openssl dgst -sha256 -verify "$public_key" -signature "$signature_file" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Valid key pair: $key_id${NC}"
            ((valid++))
        else
            echo -e "${RED}❌ Invalid key pair: $key_id${NC}"
            ((invalid++))
        fi

        rm -f "$signature_file"
    done

    echo ""
    echo -e "${BLUE}📊 Validation Summary:${NC}"
    echo "   Valid pairs: $valid"
    echo "   Invalid pairs: $invalid"

    if [[ $invalid -gt 0 ]]; then
        log "Key validation completed with $invalid invalid pairs"
        return 1
    else
        log "All $valid key pairs validated successfully"
        return 0
    fi
}

# Backup all keys
backup_keys() {
    local backup_archive="$BACKUP_DIR/keys-backup-$(date +%Y%m%d-%H%M%S).tar.gz"

    echo -e "${BLUE}💾 Creating key backup...${NC}"

    tar -czf "$backup_archive" \
        -C "$KEYS_DIR" \
        --exclude="backup" \
        . 2>/dev/null || true

    if [[ -f "$backup_archive" ]]; then
        chmod 600 "$backup_archive"
        echo -e "${GREEN}✅ Keys backed up to: $backup_archive${NC}"
        log "Keys backed up to: $backup_archive"
    else
        echo -e "${RED}❌ Failed to create backup${NC}"
        log "Failed to create key backup"
        return 1
    fi
}

# Clean old key backups
clean_old_keys() {
    local keep_count=3

    echo -e "${BLUE}🧹 Cleaning old key backups (keeping last $keep_count)...${NC}"

    # Remove old backup archives
    ls -t "$BACKUP_DIR"/keys-backup-*.tar.gz 2>/dev/null | tail -n +$((keep_count + 1)) | xargs rm -f || true

    # Remove old environment backups
    ls -t "$BACKUP_DIR"/env-keys-*.env 2>/dev/null | tail -n +$((keep_count + 1)) | xargs rm -f || true

    echo -e "${GREEN}✅ Cleanup completed${NC}"
    log "Old key backups cleaned up"
}

# Main function
main() {
    local command=""
    local key_size=2048
    local env_file=".env"
    local verbose=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            generate-jwt-keys|rotate-keys|generate-totp|validate-keys|backup-keys|restore-keys|clean-old-keys)
                command="$1"
                shift
                ;;
            --key-size)
                key_size="$2"
                shift 2
                ;;
            --env-file)
                env_file="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Unknown option: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done

    if [[ -z "$command" ]]; then
        echo -e "${RED}❌ No command specified${NC}"
        usage
        exit 1
    fi

    # Setup
    check_dependencies
    setup_directories

    # Execute command
    case "$command" in
        generate-jwt-keys)
            generate_jwt_keys "$key_size"
            ;;
        rotate-keys)
            rotate_keys "$env_file"
            ;;
        generate-totp)
            generate_totp
            ;;
        validate-keys)
            validate_keys
            ;;
        backup-keys)
            backup_keys
            ;;
        clean-old-keys)
            clean_old_keys
            ;;
        *)
            echo -e "${RED}❌ Command not implemented: $command${NC}"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
