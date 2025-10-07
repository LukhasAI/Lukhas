---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

# AI Tools Integration Guide

**Configuring Any AI Development Tool for LUKHAS Platform**

## 🎯 Overview

LUKHAS AI platform provides **vendor-neutral context files** that work with any AI development tool. Our dual-format strategy ensures compatibility with Claude Desktop while supporting all other AI coding assistants.

## 📁 Context File System

### Dual Format Architecture
```
directory/
├── lukhas_context.md    # Vendor-neutral (recommended)
├── claude.me           # Claude Desktop optimized
└── [project files...]
```

**Both files contain identical information** - choose based on your AI tool:
- **Most AI Tools**: Use `lukhas_context.md`
- **Claude Desktop**: Use `claude.me` (optimized)

## 🛠️ Tool-Specific Configurations

### Codex Integration
Location: `.codex/config.toml`
```toml
[context]
context_files = ["lukhas_context.md", "README.md"]
context_patterns = ["**/lukhas_context.md", "**/claude.me"]
preferred_context_format = "lukhas_context.md"
```

### Cursor IDE
Create `.cursor/settings.json`:
```json
{
  "ai.contextFiles": [
    "**/lukhas_context.md",
    ".github/copilot-instructions.md"
  ],
  "ai.instructions": "Read lukhas_context.md in each directory for domain-specific guidance"
}
```

### GitHub Copilot
Already configured via `.github/copilot-instructions.md`
- Automatically detects context files
- Prioritizes lukhas_context.md format
- Falls back to claude.me for compatibility

### Tabnine
Create `.tabnine/config.json`:
```json
{
  "context_sources": [
    "lukhas_context.md",
    "claude.me"
  ],
  "project_context": true,
  "local_context_files": ["**/lukhas_context.md"]
}
```

### Universal Configuration
Use `.ai-tools.yaml` for tools that support YAML config:
```yaml
context_files:
  preferred_format: "lukhas_context.md"
  master_overview: "lukhas_context.md"
  development_hub: "candidate/lukhas_context.md"
```

## 🔄 Synchronization

### Keep Context Files Updated
```bash
# Check sync status
./scripts/sync_context_files.sh --check-status

# Sync all files (bidirectional)
./scripts/sync_context_files.sh --bidirectional

# Interactive maintenance
./scripts/maintain_context_files.sh
```

### VS Code Tasks
- **🔄 Sync Context Files**: Bidirectional sync
- **🔍 Check Context File Sync Status**: Status check
- **🛠️ Context Files Maintenance**: Interactive menu

## 📋 AI Tool Setup Checklist

### 1. Configure Context File Discovery
- [ ] Point your AI tool to read `lukhas_context.md` files
- [ ] Set fallback to `claude.me` for compatibility
- [ ] Enable recursive directory scanning

### 2. Essential Context Files
- [ ] Root: `lukhas_context.md` (master overview)
- [ ] Development: `candidate/lukhas_context.md`
- [ ] Integration: `lukhas/lukhas_context.md`
- [ ] Cognitive Engine: `matriz/lukhas_context.md`

### 3. Workflow Integration
- [ ] Read context file before editing in any directory
- [ ] Understand Constellation Framework (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum) alignment
- [ ] Follow lane isolation rules (ops/matriz.yaml)
- [ ] Apply consciousness-aware patterns

### 4. Tool-Specific Settings
- [ ] Set project root to `/Users/agi_dev/LOCAL-REPOS/Lukhas`
- [ ] Configure trust level (if supported)
- [ ] Enable project-wide context scanning
- [ ] Set up automatic context refresh

## 🎯 Best Practices

### Context File Usage
1. **Always read relevant `lukhas_context.md` first**
2. **Understand domain architecture** before making changes
3. **Check Constellation Framework alignment** (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum)
4. **Follow lane isolation rules** (candidate/ vs lukhas/ vs core/)

### Development Workflow
1. **Read context**: `lukhas_context.md` in target directory
2. **Understand domain**: Architecture and integration patterns
3. **Check dependencies**: Lane isolation and import boundaries
4. **Apply patterns**: Consciousness-aware development
5. **Sync context**: Keep both file formats updated

### Naming Conventions
- **Adapters**: `*_adapter.py`
- **Hubs**: `*_hub.py`
- **Tests**: `test_*.py`
- **Demos**: `demo_*.py`

## 🚀 Advanced Integration

### Custom Context Processors
For advanced AI tools, create custom processors:

```python
# Example: context_processor.py
def load_lukhas_context(directory):
    context_file = os.path.join(directory, 'lukhas_context.md')
    if os.path.exists(context_file):
        return parse_lukhas_context(context_file)
    return parse_claude_context(os.path.join(directory, 'claude.me'))
```

### API Integration
For tools with API access:
```python
# Point to context file locations
CONTEXT_PATTERNS = [
    "**/lukhas_context.md",
    "**/claude.me",
    ".github/copilot-instructions.md"
]
```

## 🔧 Troubleshooting

### Context Files Not Loading
1. Check file paths are absolute
2. Verify tool has read permissions
3. Ensure recursive scanning is enabled
4. Check `.gitignore` doesn't exclude context files

### Sync Issues
```bash
# Force resync all files
./scripts/sync_context_files.sh --bidirectional

# Check for conflicts
./scripts/sync_context_files.sh --check-status

# Interactive troubleshooting
./scripts/maintain_context_files.sh
```

### Tool-Specific Issues
- **Codex**: Check `.codex/config.toml` paths
- **Cursor**: Verify `.cursor/settings.json` exists
- **Copilot**: Review `.github/copilot-instructions.md`
- **Others**: Use `.ai-tools.yaml` universal config

## 📚 Documentation

- **Context System**: `docs/CONTEXT_FILES.md`
- **Agent Coordination**: `AGENTS.md`
- **Copilot Instructions**: `.github/copilot-instructions.md`
- **Architecture Overview**: `lukhas_context.md` (root)

---

**Professional Implementation**: This setup ensures any AI development tool can leverage the full architectural context of the LUKHAS platform while maintaining optimal Claude Desktop integration.
