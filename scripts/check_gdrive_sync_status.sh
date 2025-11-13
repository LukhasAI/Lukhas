#!/bin/bash
# Quick status check for Google Drive sync

GDRIVE="/Users/agi_dev/Library/CloudStorage/GoogleDrive-gonzo.dominguez@gmail.com/My Drive/Lukhas-Code-Backup"

echo "📊 Google Drive Sync Status"
echo "============================"
echo ""
echo "📁 Local Source: /Users/agi_dev/LOCAL-REPOS/Lukhas"
echo "☁️  Cloud Backup: My Drive/Lukhas-Code-Backup"
echo ""
echo "📈 Current Stats:"
du -sh "$GDRIVE" 2>/dev/null | awk '{print "  Size: " $1}'
find "$GDRIVE" -type f 2>/dev/null | wc -l | awk '{print "  Files: " $1}'
echo ""
echo "✅ Main AI Code Directories:"
for dir in core matriz consciousness governance memory bio; do
  if [ -d "$GDRIVE/$dir" ]; then
    count=$(find "$GDRIVE/$dir" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
    printf "  %-15s %3d Python files\n" "$dir:" "$count"
  fi
done
echo ""
echo "🔄 To update cloud backup:"
echo "  bash ~/LOCAL-REPOS/Lukhas/scripts/sync_to_google_drive.sh"
echo ""
