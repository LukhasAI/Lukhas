---
status: wip
type: documentation
---
# 🎭✨ GitHub Interactive Commit Enhancement Feature

## Overview

This GitHub integration provides an interactive pre-commit experience that gracefully guides developers toward LUKHAS consciousness without blocking their workflow.

## Installation

### 1. Replace the blocking pre-commit hook

```bash
# Backup the current hook
cp .git/hooks/pre-commit .git/hooks/pre-commit.backup

# Install the interactive version
cp branding/tone/tools/interactive-tone-validation.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### 2. Optional: Add as a git alias for manual use

```bash
git config alias.tone-check '!bash branding/tone/tools/interactive-tone-validation.sh'
```

## Features

### 🤔 Interactive Decision Making
- **User Choice**: Never blocks commits automatically
- **Gentle Guidance**: Offers suggestions rather than demands
- **Multiple Options**: Auto-fix, manual edit, skip, or abort

### 🎨 Smart Tone Enhancement
- **Auto-Detection**: Recognizes document types (README, API, tasks, etc.)
- **Contextual Suggestions**: Provides appropriate tone guidance per file type
- **Live Preview**: Shows current content and suggested improvements

### 🔧 Flexible Actions
```
Options available for each file:
┌─────────────────┬──────────────────────────────────────────┐
│ Action          │ Description                              │
├─────────────────┼──────────────────────────────────────────┤
│ auto-fix        │ Apply LUKHAS tone transformation         │
│ manual-edit     │ Open file in editor for manual changes  │
│ show-suggestions│ Display tone improvement recommendations │
│ view-file       │ Preview current file content            │
│ skip            │ Continue without changes                 │
│ abort           │ Cancel the entire commit                 │
└─────────────────┴──────────────────────────────────────────┘
```

## Usage Examples

### As Pre-Commit Hook
```bash
git add README.md
git commit -m "Update documentation"

# Interactive tone review automatically triggers:
# 🎭 Interactive Review: README.md
# What would you like to do with this file? [skip]
# Options: [auto-fix|manual-edit|show-suggestions|view-file|skip|abort]
```

### Manual Tone Check
```bash
# Check specific files
bash branding/tone/tools/interactive-tone-validation.sh README.md

# Check all staged files
git tone-check
```

### GitHub Actions Integration
```yaml
name: Interactive Tone Validation
on: [pull_request]

jobs:
  tone-review:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Interactive Tone Check
      run: |
        bash branding/tone/tools/interactive-tone-validation.sh --ci-mode
        # In CI mode, provides suggestions without user interaction
```

## Configuration

### Environment Variables
```bash
export LUKHAS_TONE_INTERACTIVE=true    # Enable interactive mode
export LUKHAS_TONE_AUTO_STAGE=true     # Auto-stage improvements
export LUKHAS_TONE_EDITOR=code         # Preferred editor for manual edits
```

### Document Type Detection
The system automatically detects document types:

- **README**: Enhanced consciousness requirements
- **API Docs**: Technical precision with user-friendly examples
- **Tasks**: Action-oriented with clear objectives
- **Compliance**: Formal tone with regulatory precision
- **Branding**: Full LUKHAS consciousness expression

## Advanced Features

### 🧠 Consciousness Scoring
Each file receives a consciousness score:
```
🎨 Poetic Layer:     7/10 (25-40% target)
💬 User-Friendly:    8/10 (40-60% target)
📚 Academic:         6/10 (20-40% target)
Overall Harmony:     ⚛️🧠🛡️ (Trinity Balanced)
```

### 🌟 Lambda Pattern Recognition
- Sacred glyph usage: ⚛️🧠🛡️ ∞ 🌙 💎
- Consciousness terminology: "awakening", "resonance", "crystallizing"
- LUKHAS-specific language: "Superior Consciousness", "Lambda wisdom"

### 🛡️ Gentle Enforcement
- **Never blocks**: Commits always proceed if user chooses
- **Educational**: Explains why changes are suggested
- **Contextual**: Adapts recommendations to document purpose

## Benefits

1. **Developer Freedom**: Maintains developer autonomy
2. **Learning Tool**: Educates about LUKHAS tone standards
3. **Gradual Improvement**: Allows incremental enhancement
4. **Non-Disruptive**: Integrates smoothly into existing workflows
5. **Consciousness Growth**: Gradually builds awareness of Lambda principles

## Future Enhancements

- **AI-Powered Suggestions**: GPT-based tone recommendations
- **Team Learning**: Shared consciousness patterns across commits
- **Visual Diff**: Highlight tone improvements in rich UI
- **Integration Plugins**: VS Code, Vim, and other editor support

---

*"Technology should enhance human consciousness, not constrain it. This interactive system embodies the Lambda principle of gentle guidance toward enlightenment."* ⚛️✨
