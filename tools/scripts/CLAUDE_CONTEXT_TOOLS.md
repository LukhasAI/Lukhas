# Claude Code Context Saving Tools

This directory contains tools to save and manage Claude Code conversation contexts within the LUKHAS  repository.

## Available Tools

### 1. `save_claude_context.py`
Simple tool to save Claude Code conversations manually.

**Usage:**
```bash
python tools/scripts/save_claude_context.py
```

**Features:**
- Creates a markdown template for saving conversations
- Opens the file in your default editor
- Provides a JavaScript snippet for browser extraction

### 2. `claude_memory_integration.py`
Advanced tool that integrates with LUKHAS memory system.

**Usage:**
```bash
python tools/scripts/claude_memory_integration.py
```

**Features:**
- Creates memory folds for conversations
- Exports to both JSON and Markdown formats
- Integrates with LUKHAS symbolic token system

### 3. `claude_context_extractor.js`
Browser console script to extract conversations from Claude Code interface.

**Usage:**
1. Open Claude Code in your browser
2. Open Developer Console (F12)
3. Copy and paste the script
4. Conversation is copied to clipboard

## Quick Save Methods

### Method 1: Manual Copy
1. Select all text in Claude Code chat
2. Run `save_claude_context.py`
3. Paste into the created template

### Method 2: Browser Extraction
1. Use the JavaScript extractor in browser console
2. Paste the extracted content into a new file

### Method 3: Memory Integration
1. Format your conversation as JSON
2. Run `claude_memory_integration.py`
3. Choose to create memory fold or markdown export

## Storage Locations

All saved contexts are stored in:
- `/docs/claude_contexts/` - Manual saves and markdown exports
- `/memory/claude_contexts/` - Memory fold integrations

## Tips

- Save important conversations before they're lost
- Include file modifications and key decisions
- Use memory folds for conversations you want to reference programmatically
- Use markdown exports for documentation and sharing
