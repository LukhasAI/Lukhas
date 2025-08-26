#!/bin/bash

# LUKHAS Auto-Backup Script
# Prevents data loss by creating automatic backups

echo "🛡️ LUKHAS Agent Protection - Auto-Backup Started"
echo "=============================================="

# Create backup directory with timestamp OUTSIDE workspace
BACKUP_DIR="$HOME/LOCAL-REPOS/LUKHAS_BACKUPS/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup critical agent configurations
echo "📁 Backing up Agent Configurations..."
cp -r agents/ "$BACKUP_DIR/agents/" 2>/dev/null
echo "  ✓ Supreme Army configs backed up"

# Backup consciousness modules
echo "🧠 Backing up Consciousness Modules..."
cp -r consciousness/ "$BACKUP_DIR/consciousness/" 2>/dev/null
cp -r core/ "$BACKUP_DIR/core/" 2>/dev/null
cp -r identity/ "$BACKUP_DIR/identity/" 2>/dev/null
echo "  ✓ Consciousness modules backed up"

# Backup configuration files
echo "⚙️ Backing up Configuration Files..."
cp *.yaml "$BACKUP_DIR/" 2>/dev/null
cp *.json "$BACKUP_DIR/" 2>/dev/null
cp -r .vscode/ "$BACKUP_DIR/.vscode/" 2>/dev/null
echo "  ✓ Configuration files backed up"

# Create backup manifest
echo "📋 Creating Backup Manifest..."
cat > "$BACKUP_DIR/BACKUP_MANIFEST.txt" << EOF
LUKHAS Auto-Backup
=====================
Timestamp: $(date)
Agent Configs: $(find agents/ -name "*.json" -o -name "*.yaml" | wc -l) files
Consciousness Modules: $(find consciousness/ core/ identity/ -name "*.py" 2>/dev/null | wc -l) files
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "Not in git repo")
Git Branch: $(git branch --show-current 2>/dev/null || echo "Unknown")

Files backed up:
$(find "$BACKUP_DIR" -type f | sort)
EOF

# Clean old backups (keep last 10) OUTSIDE workspace
echo "🧹 Cleaning old backups..."
ls -1dt "$HOME/LOCAL-REPOS/LUKHAS_BACKUPS"/*/ 2>/dev/null | tail -n +11 | xargs rm -rf
KEPT_BACKUPS=$(ls -1d "$HOME/LOCAL-REPOS/LUKHAS_BACKUPS"/*/ 2>/dev/null | wc -l)
echo "  ✓ Kept $KEPT_BACKUPS recent backups"

echo ""
echo "✅ Auto-Backup Complete!"
echo "📍 Backup Location: $BACKUP_DIR"
echo "🕒 Next backup: Run this script or set up cron job"
echo ""
echo "💡 To restore: cp -r $BACKUP_DIR/* ."
echo "📁 Backup location: $BACKUP_DIR"
