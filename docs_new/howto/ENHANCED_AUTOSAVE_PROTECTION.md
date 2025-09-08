---
title: Enhanced Autosave Protection
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["consciousness", "testing", "monitoring", "howto"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "consciousness", "identity"]
  audience: ["dev"]
---

# 🛡️ LUKHAS Enhanced Autosave & Data Protection System

## Overview
This document outlines the comprehensive autosave and data protection enhancements implemented to prevent the data loss issues experienced with agent configurations and other critical files.

## 🔧 Enhanced Autosave Configuration

### VS Code Settings (`.vscode/settings.json`)
```json
// Enhanced Autosave Configuration - PREVENT DATA LOSS
"files.autoSave": "afterDelay",
"files.autoSaveDelay": 1000,           // Save every 1 second
"files.autoGuessEncoding": true,
"files.hotExit": "onExitAndWindowClose", // Preserve unsaved changes
"workbench.editor.restoreViewState": true,
"workbench.editor.enablePreview": false, // No preview mode

// Backup and Recovery Enhancement
"files.enableTrash": true,
"workbench.editor.closeOnFileDelete": false,
"workbench.localHistory.enabled": true,  // VS Code local history
"workbench.localHistory.maxFileSize": 262144,

// Session Recovery
"window.restoreWindows": "all",
"window.restoreFullscreen": true,

// Git Auto-Protection
"git.autoStash": true,
"git.autorefresh": true,
"git.timeline.enabled": true
```

## 🛡️ Multi-Layer Protection System

### 1. **VS Code Local History**
- Automatic file history tracking
- Recoverable from VS Code timeline
- Located in workspace `.vscode/` folder

### 2. **Git Pre-Commit Hook Enhancement**
- **Agent Protection**: Automatic backup before commits
- **Empty File Detection**: Blocks commits with empty agent files
- **JSON Validation**: Ensures agent configs have valid syntax
- **Recovery Commands**: Provides exact recovery instructions

### 3. **Automated Backup Script**
**Location**: `scripts/utilities/auto_backup_lukhas.sh`

**Features**:
- Timestamped backups in `.auto-backup/`
- Agent configurations backup
- Consciousness modules backup
- Configuration files backup
- Automatic cleanup (keeps last 10 backups)
- Backup manifest with git commit info

**Usage**:
```bash
# Manual backup
./scripts/utilities/auto_backup_lukhas.sh

# Set up automatic backup (every hour)
crontab -e
# Add: 0 * * * * cd /path/to/Lukhas && ./scripts/utilities/auto_backup_lukhas.sh
```

### 4. **Enhanced Workspace Configuration**
**File**: `lukhas--enhanced-autosave.code-workspace`

**Features**:
- Workspace-specific autosave settings
- Auto-backup task on folder open
- Session state preservation
- Recommended extensions

## 🚨 Data Recovery Procedures

### Agent Files Recovery

#### Method 1: Git Recovery
```bash
# Restore all agent files from last commit
git checkout HEAD -- agents/

# Restore specific agent file
git checkout HEAD -- agents/specific_agent_config.json
```

#### Method 2: Backup Recovery
```bash
# List available backups
ls -la .auto-backup/

# Restore from specific backup
cp -r .auto-backup/YYYYMMDD-HHMMSS/agents/ agents/

# Restore latest backup
LATEST_BACKUP=$(ls -1t .auto-backup/ | head -1)
cp -r ".auto-backup/$LATEST_BACKUP/agents/" agents/
```

#### Method 3: VS Code Timeline
1. Open affected file in VS Code
2. Right-click in editor → "Open Timeline"
3. Select previous version to restore

### Critical File Protection

**Protected Directories**:
- `agents/` - All agent configurations
- `consciousness/` - Consciousness modules
- `core/` - Core system files
- `identity/` - Identity management
- `.vscode/` - VS Code settings

**Protection Methods**:
- Automatic git stashing before risky operations
- Pre-commit validation and backup
- Local history tracking
- Timestamped backups
- JSON syntax validation

## 🔄 Continuous Protection

### Automatic Features
- **1-second autosave** in VS Code
- **Pre-commit agent backup** via Git hook
- **Session restoration** on VS Code restart
- **Timeline tracking** for all files
- **Git auto-refresh** and stashing

### Manual Safety Commands
```bash
# Create immediate backup
./scripts/utilities/auto_backup_lukhas.sh

# Check agent file integrity
find agents/ -name "*.json" -exec python3 -m json.tool {} \; > /dev/null

# Verify no empty agent files
find agents/ -name "*.json" -size 0

# Create git stash with current state
git add -A && git stash push -m "Safety checkpoint $(date)"
```

## 📊 Monitoring & Alerts

### Git Hook Validation
The enhanced pre-commit hook will:
- ❌ **Block commits** with empty agent files
- ❌ **Block commits** with invalid JSON syntax
- ✅ **Create automatic backups** for agent changes
- ✅ **Provide recovery commands** if issues detected

### Backup Monitoring
```bash
# Check backup status
ls -la .auto-backup/ | tail -5

# View backup log
tail .git-agent-backups/backup.log

# Backup storage usage
du -sh .auto-backup/ .git-agent-backups/
```

## 🚀 Future Enhancements

### Planned Features
1. **Real-time file monitoring** with inotify/fswatch
2. **Cloud backup integration** (GitHub, AWS S3)
3. **Automated integrity checks** via cron jobs
4. **File change notifications** via VS Code extension
5. **Remote backup synchronization**

### Integration Points
- **CI/CD Pipeline**: Backup validation in GitHub Actions
- **Development Workflow**: Pre-push hooks for additional safety
- **Team Collaboration**: Shared backup protocols
- **Production Deployment**: Release backup requirements

---

## 💡 Best Practices

1. **Always use the enhanced workspace**: `lukhas--enhanced-autosave.code-workspace`
2. **Run manual backups** before major changes
3. **Check git status** before complex operations
4. **Use git stash** for temporary safety checkpoints
5. **Monitor backup logs** regularly
6. **Test recovery procedures** periodically

This comprehensive protection system ensures that the agent configuration loss incident cannot happen again, providing multiple layers of safety and clear recovery procedures.
