#!/bin/bash
# LUKHAS AI - Google Drive Sync Script
# Syncs code to Google Drive (excludes .git, build artifacts, caches)

set -e

SOURCE="/Users/agi_dev/LOCAL-REPOS/Lukhas"
DEST="/Users/agi_dev/Library/CloudStorage/GoogleDrive-gonzo.dominguez@gmail.com/My Drive/Lukhas-Code-Backup"

echo "🔄 LUKHAS AI → Google Drive Sync"
echo "================================="
echo ""
echo "📁 Source: $SOURCE"
echo "☁️  Destination: $DEST"
echo ""

# Create destination if it doesn't exist
mkdir -p "$DEST"

echo "📊 Analyzing changes..."
rsync -av --dry-run \
  --exclude='.git/' \
  --exclude='.venv/' \
  --exclude='.venv*/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache/' \
  --exclude='.mypy_cache/' \
  --exclude='.ruff_cache/' \
  --exclude='node_modules/' \
  --exclude='*.log' \
  --exclude='.DS_Store' \
  --exclude='build/' \
  --exclude='dist/' \
  --exclude='*.egg-info/' \
  --exclude='release_artifacts/' \
  --exclude='.coverage' \
  --exclude='htmlcov/' \
  "$SOURCE/" "$DEST/" | tail -20

echo ""
read -p "Proceed with sync? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo ""
  echo "🚀 Syncing to Google Drive..."
  rsync -av --progress \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='.venv*/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache/' \
    --exclude='.mypy_cache/' \
    --exclude='.ruff_cache/' \
    --exclude='node_modules/' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    --exclude='build/' \
    --exclude='dist/' \
    --exclude='*.egg-info/' \
    --exclude='release_artifacts/' \
    --exclude='.coverage' \
    --exclude='htmlcov/' \
    "$SOURCE/" "$DEST/"
  
  echo ""
  echo "✅ Sync completed!"
  echo ""
  echo "📊 Synced folder:"
  du -sh "$DEST"
  find "$DEST" -type f | wc -l | xargs echo "  Files:"
  echo ""
  echo "☁️  Your code is now in Google Drive:"
  echo "   My Drive → Lukhas-Code-Backup"
  echo ""
  echo "💡 To sync again, run: ~/LOCAL-REPOS/sync_lukhas_to_gdrive.sh"
else
  echo "Cancelled."
fi
