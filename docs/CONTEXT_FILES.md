# LUKHAS Context Files System

**Dual-format AI guidance with vendor neutrality and Claude Desktop compatibility**

## 📖 Overview

The LUKHAS project uses a sophisticated context file system to provide AI development tools with domain-specific architectural guidance. We maintain **42 distributed context files** in dual format to ensure compatibility with any AI tool while optimizing for Claude Desktop.

## 📁 File Format

### Dual Format Strategy
- **`claude.me`**: Claude Desktop optimized format with built-in tool recognition
- **`lukhas_context.md`**: Vendor-neutral format for any AI development tool
- **Content**: Identical architectural information in both files

### File Structure
```
directory/
├── claude.me                 # Claude Desktop format
├── lukhas_context.md         # Vendor-neutral format
└── [other files...]
```

## 🛠️ Management Tools

### Quick Commands
```bash
# Check sync status
./scripts/sync_context_files.sh --check-status

# Sync all files (bidirectional based on modification time)
./scripts/sync_context_files.sh --bidirectional

# Interactive maintenance menu
./scripts/maintain_context_files.sh
```

### VS Code Tasks
- **🔄 Sync Context Files**: Bidirectional sync
- **🔍 Check Context File Sync Status**: Status check
- **🛠️ Context Files Maintenance**: Interactive menu

## 📋 Usage Guide

### For Claude Desktop Users
- Continue using `claude.me` files (zero disruption)
- Built-in recognition and optimization
- Full Trinity Framework integration

### For Other AI Tools
- Configure tools to read `lukhas_context.md` files
- Vendor-neutral format with clear LUKHAS branding
- Identical architectural information as claude.me

### For Content Updates
1. **Edit either file** (claude.me or lukhas_context.md)
2. **Run sync script** to update the partner file
3. **Commit both files** to maintain consistency

## 🔄 Synchronization System

### Automatic Options
- **VS Code Tasks**: Built-in tasks for sync operations
- **Git Wrapper**: `./scripts/git_with_sync.sh` for automatic checks
- **Maintenance Script**: Interactive menu for all operations

### Sync Modes
- **Bidirectional**: Smart sync based on modification time (recommended)
- **Claude → LUKHAS**: Force sync from claude.me to lukhas_context.md
- **LUKHAS → Claude**: Force sync from lukhas_context.md to claude.me
- **Add Missing**: Create missing partner files

### Examples
```bash
# Smart sync (newer file wins)
./scripts/sync_context_files.sh --bidirectional

# Force direction
./scripts/sync_context_files.sh --claude-to-lukhas

# Preview changes
./scripts/sync_context_files.sh --bidirectional --dry-run

# Check what needs sync
./scripts/sync_context_files.sh --check-status
```

## 📊 Benefits

### ✅ Achieved
- **🔧 Claude Compatibility**: All existing Claude Desktop integration preserved
- **🎯 Vendor Neutrality**: Any AI tool can use lukhas_context.md files
- **🏷️ Clear Branding**: LUKHAS identity prominently featured
- **🚀 Future-Proof**: No vendor lock-in concerns
- **📚 Consistency**: Identical information in both formats
- **⚡ Professional**: Enterprise-quality automation and validation

### 🎯 Use Cases
- **Multi-AI Development**: Teams using different AI tools
- **Future Migration**: Easy transition to new AI platforms
- **Claude Desktop**: Optimized experience with claude.me files
- **Enterprise**: Vendor-neutral documentation strategy

## 🗂️ File Locations

### Key Context Files
```
claude.me / lukhas_context.md              # Master architecture overview
candidate/claude.me / lukhas_context.md    # Primary workspace (2,877 files)
lukhas/claude.me / lukhas_context.md       # Integration layer (148 files)
matriz/claude.me / lukhas_context.md       # Cognitive DNA processing
```

### Trinity Framework
- **⚛️ Identity**: identity/, candidate/core/identity/, lukhas/identity/
- **🧠 Consciousness**: consciousness/, candidate/consciousness/, lukhas/consciousness/
- **🛡️ Guardian**: ethics/, governance/, ethics/guardian/

### Specialized Domains
- **Memory**: memory/, candidate/memory/, lukhas/memory/
- **Bio/Quantum**: bio/, quantum/
- **Products**: products/, products/enterprise/, products/experience/
- **Tools**: tools/

## 🔧 Maintenance

### Regular Tasks
1. **Check sync status** before major commits
2. **Run bidirectional sync** after content updates
3. **Use maintenance script** for comprehensive operations
4. **Review git status** for context file changes

### Troubleshooting
```bash
# Files out of sync?
./scripts/sync_context_files.sh --check-status

# Force complete resync
./scripts/sync_context_files.sh --bidirectional

# Missing partner files?
./scripts/sync_context_files.sh --add-missing

# Interactive help
./scripts/maintain_context_files.sh
```

---

**Professional Implementation**: This dual-format strategy provides enterprise-grade vendor neutrality while maintaining optimal Claude Desktop integration. The 42 distributed context files ensure any AI development tool has comprehensive architectural guidance for the LUKHAS AGI platform.
