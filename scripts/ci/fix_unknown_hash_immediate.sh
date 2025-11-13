#!/usr/bin/env bash
# fix_unknown_hash_immediate.sh
# CRITICAL: Fix workflows using unknown hash c14a0b9e72d31fbb7b7f3466e2a4f96c6498a1b0
# This hash does not exist in actions/download-artifact repository - security concern

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== CRITICAL SECURITY FIX: Unknown download-artifact Hash ==="
echo "Hash c14a0b9e72d31fbb7b7f3466e2a4f96c6498a1b0 NOT FOUND in actions/download-artifact"
echo "Updating to verified safe version: v4.1.8"
echo ""

# The two workflows using this unknown hash
WORKFLOWS=(
  ".github/workflows/matriz-clearance.yml"
  ".github/workflows/matriz-nightly-soak.yml"
)

UNKNOWN_HASH="c14a0b9e72d31fbb7b7f3466e2a4f96c6498a1b0"
SAFE_VERSION="v4.1.8"

# Check if workflows exist
for workflow in "${WORKFLOWS[@]}"; do
  if [ ! -f "$workflow" ]; then
    echo "ERROR: Workflow not found: $workflow"
    exit 1
  fi
done

# Create backups
BACKUP_DIR=".github/workflows_backup_$(date +%Y%m%d_%H%M%S)_security_fix"
mkdir -p "$BACKUP_DIR"
echo "Creating backups in $BACKUP_DIR..."
for workflow in "${WORKFLOWS[@]}"; do
  cp "$workflow" "$BACKUP_DIR/$(basename "$workflow")"
done
echo "✅ Backups created"
echo ""

# Apply fix
echo "Applying security fix..."
for workflow in "${WORKFLOWS[@]}"; do
  echo "Processing: $workflow"

  # Check if file contains the unknown hash
  if grep -q "$UNKNOWN_HASH" "$workflow"; then
    # Replace unknown hash with safe version
    sed -i'.tmp' "s|actions/download-artifact@${UNKNOWN_HASH}.*|actions/download-artifact@${SAFE_VERSION}  # Security: fixed unknown hash (was c14a0b9e)|g" "$workflow"

    # Validate YAML
    if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
      echo "  ✅ Updated and validated"

      # Show the change
      echo "  📝 Change applied:"
      diff "$BACKUP_DIR/$(basename "$workflow")" "$workflow" | grep -A2 -B2 "download-artifact" || true
    else
      echo "  ❌ YAML validation failed - reverting"
      cp "$BACKUP_DIR/$(basename "$workflow")" "$workflow"
      exit 1
    fi

    # Cleanup temp file
    rm -f "${workflow}.tmp"
  else
    echo "  ℹ️  Unknown hash not found (may have been fixed already)"
  fi
  echo ""
done

echo "=== Fix Complete ==="
echo ""
echo "Backups saved in: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff .github/workflows/matriz-clearance.yml .github/workflows/matriz-nightly-soak.yml"
echo "2. Run verification: bash scripts/ci/verify_download_artifact_hashes.sh"
echo "3. Commit: git add .github/workflows/matriz-{clearance,nightly-soak}.yml"
echo "4. Push: git commit -m 'security(ci): fix unknown download-artifact hash in MATRIZ workflows'"
echo ""
echo "Critical security fix applied successfully! ✅"
