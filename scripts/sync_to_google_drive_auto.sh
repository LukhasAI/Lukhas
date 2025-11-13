#!/bin/bash
# Auto-sync version (no prompts) - runs every 10 minutes via LaunchAgent

SOURCE="/Users/agi_dev/LOCAL-REPOS/Lukhas"
DEST="/Users/agi_dev/Library/CloudStorage/GoogleDrive-gonzo.dominguez@gmail.com/My Drive/Lukhas-Code-Backup"
LOGFILE="/Users/agi_dev/Library/Logs/lukhas-gdrive-sync.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting auto-sync..." >> "$LOGFILE"

# Sync silently
rsync -a \
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
  "$SOURCE/" "$DEST/" >> "$LOGFILE" 2>&1

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') - Sync completed successfully" >> "$LOGFILE"
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') - Sync failed with exit code $EXIT_CODE" >> "$LOGFILE"
fi
