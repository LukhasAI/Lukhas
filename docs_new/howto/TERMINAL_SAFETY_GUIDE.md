---
title: Terminal Safety Guide
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["howto"]
facets:
  layer: ["gateway"]
  domain: ["symbolic"]
  audience: ["dev"]
---

# 🛡️ LUKHAS Terminal Safety Guide

## Problem Solved
- **Issue**: Multi-line Copilot commands causing `dquote>` terminal hangs
- **Root Cause**: Smart quotes, wrapped commands, improper paste handling
- **Solution**: Bracketed paste magic + VS Code warnings + quote-safe patterns

## New Terminal Features

### 1. Bracketed Paste Magic (zsh)
```bash
# Added to ~/.zshrc
autoload -Uz bracketed-paste-magic
zle -N bracketed-paste bracketed-paste-magic
```

### 2. Smart Quote Cleaning
```bash
# Use Ctrl+V for quote-safe pasting (instead of Cmd+V)
function clean-paste() {
    LBUFFER+=$(pbpaste | perl -CS -pe 'tr/""''/""'\'''\''/');
    zle redisplay
}
```

### 3. VS Code Paste Warnings
```json
{
  "terminal.integrated.enableMultiLinePasteWarning": true,
  "terminal.integrated.bracketedPasteMode": true,
  "editor.copyWithSyntaxHighlighting": false,
  "files.eol": "\n"
}
```

## Usage Guidelines for Copilot

### ✅ DO - Quote-Safe Patterns
```bash
# Use heredocs for multi-line output
{
    printf 'Status: %s\n' "OPERATIONAL"
    printf 'Files recovered: %d\n' 11
} | tee recovery.log

# Use printf instead of echo for complex text
printf '%s\n' "Phase 1: Complete"

# Use tasks for complex operations
# Terminal → Run Task → T4: Terminal-Safe Recovery Status
```

### ❌ AVOID - Quote-Dangerous Patterns
```bash
# DON'T: Multi-line echo with quotes
echo "Phase 1: Complete
✅ Files: "recovered"
Status: Ready"

# DON'T: Inline double quotes
echo "✅ Restored config/PROVENANCE.yaml ($(wc -c < config/PROVENANCE.yaml) bytes)"
```

## Emergency Recovery
If you still hit `dquote>`:
1. **Ctrl+C** - Abort immediately
2. Type a single `"` then **Enter** - Close dangling quote
3. **`reset`** - If terminal gets visually corrupted

## New Tools Available
- **Script**: `./scripts/terminal_safety_demo.sh` - Quote-safe demo
- **Task**: "T4: Terminal-Safe Recovery Status" - VS Code task runner
- **Shortcut**: **Ctrl+V** - Quote-safe paste in terminal

---
*Implemented: August 26, 2025*
*Based on GPT-5 terminal safety recommendations*
