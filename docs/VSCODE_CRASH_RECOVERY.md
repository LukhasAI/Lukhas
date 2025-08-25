# VS Code Crash Recovery Guide

## Issue Summary
**Date**: 2025-08-24
**Problem**: VS Code (Electron) crashed with EXC_BREAKPOINT (SIGTRAP) exception
**Session Duration**: ~3 days (since Aug 21)
**Crash Time**: 21:09:34

## Root Causes Identified

1. **Memory Pressure**
   - Long-running session (3+ days)
   - Multiple AI assistants running simultaneously (Claude + GitHub Copilot)
   - Large file optimizations disabled
   - Aggressive auto-save (1000ms intervals)

2. **Extension Conflicts**
   - Both Claude and GitHub Copilot extensions active
   - Multiple Python analysis tools running concurrently
   - No memory limits set for extensions

## Changes Implemented

### 1. VS Code Settings Optimizations

#### Performance Improvements
- **Auto-save delay**: Increased from 1000ms to 3000ms (reduces disk I/O)
- **Large file optimizations**: Enabled (was disabled)
- **Editor tab limit**: Set to 10 open tabs maximum
- **Terminal scrollback**: Limited to 1000 lines
- **Search results**: Limited to 10,000 matches

#### Memory Management
- **Large files memory limit**: Set to 2048MB
- **TypeScript server memory**: Limited to 2048MB
- **Extension affinity**: Configured to isolate Python extensions
- **Tokenization line length**: Limited to 20,000 characters

#### Extension Management
- **GitHub Copilot**: Temporarily disabled to reduce conflicts
- **Auto-update**: Disabled for extensions
- **Update mode**: Set to manual

### 2. Recovery Script Created

Location: `scripts/vscode_recovery.sh`

**Features**:
- Clears VS Code cache directories
- Resets problematic extensions
- Checks system resources
- Creates settings backups
- Provides interactive recovery options

**Usage**:
```bash
./scripts/vscode_recovery.sh
```

## Prevention Strategies

### Daily Practices
1. **Restart VS Code** at least once every 2-3 days
2. **Monitor memory usage** using Activity Monitor
3. **Keep open tabs** to 10 or fewer
4. **Close unused terminals** and output panels

### Weekly Maintenance
1. **Clear cache** using the recovery script
2. **Review extensions** and disable unused ones
3. **Check for updates** manually
4. **Backup settings** regularly

### When Issues Occur

#### Quick Recovery
```bash
# Run quick recovery (clears cache, checks resources)
./scripts/vscode_recovery.sh
# Select option 1
```

#### Full Recovery
```bash
# Run full recovery (all optimizations)
./scripts/vscode_recovery.sh
# Select option 2
```

#### Manual Steps
1. Force quit VS Code if frozen
2. Clear Electron processes: `killall Electron`
3. Run recovery script
4. Restart VS Code

## Configuration Backups

Settings are automatically backed up to:
- `.vscode/settings.json.backup-[timestamp]`
- `.vscode/settings.json.recovery-backup-[date]`

To restore a backup:
```bash
cp .vscode/settings.json.backup-20250824-210955 .vscode/settings.json
```

## Monitoring Commands

### Check Memory Usage (macOS)
```bash
# View memory pressure
vm_stat | grep "Pages free"

# Check Electron processes
ps aux | grep -i electron | grep -v grep
```

### Check VS Code Extensions
```bash
# List all extensions
code --list-extensions

# Disable problematic extension
code --disable-extension [extension-id]
```

## Re-enabling GitHub Copilot

Once stability is confirmed, re-enable GitHub Copilot:

1. Edit `.vscode/settings.json`
2. Change these settings back to `true`:
   - `"github.copilot.enable"`
   - `"github.copilot.inlineSuggest.enable"`
   - `"github.copilot.enableCompletions"`
   - `"github.copilot.enablePanel"`
   - `"github.copilot.enableStatusBar"`
   - `"github.copilot.enableSuggestions"`

## Additional Resources

- [VS Code Performance Issues](https://code.visualstudio.com/docs/supporting/troubleshoot-terminal-issues)
- [Electron Memory Management](https://www.electronjs.org/docs/latest/tutorial/performance)
- Recovery script: `scripts/vscode_recovery.sh`
- Original crash report: `Crash_report.csv`

## Support

If crashes persist after applying these fixes:

1. Run full recovery: `./scripts/vscode_recovery.sh` (option 2)
2. Check system logs: `~/Library/Application Support/Code/logs/`
3. Consider reinstalling VS Code
4. Report issue to: https://github.com/microsoft/vscode/issues