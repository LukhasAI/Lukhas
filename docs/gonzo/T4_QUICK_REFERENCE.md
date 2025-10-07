---
status: wip
type: documentation
owner: unknown
module: gonzo
redirect: false
moved_to: null
---

# 🎯 T4 AutoFix Quick Reference

**LUKHAS AI Agent Army - Cursor-Aware QuickFix System**

## 🎮 Keyboard Shortcuts

| Shortcut | Action             | Description                        |
| -------- | ------------------ | ---------------------------------- |
| **⌘⇧Q**  | Generate LLM Patch | Generate fix for TODO under cursor |
| **⌘⇧W**  | Apply Patch        | Apply patch with reality checks    |
| **⌘⇧T**  | List TODOs         | Show all TODOs in Problems panel   |
| **⌘⇧Y**  | Open Summary       | Open nightly summary report        |

## ⚡ Command Line Quick Actions

```bash
# Cursor-aware fix (most common)
tools/dev/t4_quickfix.py --cursor-line 42 src/file.py

# Generate and open in VS Code
tools/dev/t4_quickfix.py --open src/file.py

# Safe validation only
tools/dev/t4_quickfix.py --safe-only src/file.py

# Custom LLM model
T4_LLM_MODEL=codellama tools/dev/t4_quickfix.py src/file.py

# Comprehensive local fixes
tools/ci/run_autofix.sh
```

## 🔧 Essential Files

| File                       | Purpose       | Quick Edit             |
| -------------------------- | ------------- | ---------------------- |
| `.t4autofix.toml`          | Policy config | `code .t4autofix.toml` |
| `tools/dev/t4_quickfix.py` | Main script   | Core LLM integration   |
| `tools/ci/debt_ratchet.py` | Lint debt control | Prevent regression |
| `tools/reports/weekly_hygiene.py` | Dashboard | Weekly metrics |
| `.vscode/tasks.json`       | VS Code tasks | Task definitions       |
| `.vscode/keybindings.json` | Shortcuts     | Keyboard bindings      |

## 🛡️ Safety Checklist

- [ ] **Policy Check**: File matches allow patterns in `.t4autofix.toml`
- [ ] **Single File**: Patch affects only one file
- [ ] **Reality Tests**: Import/integration tests pass
- [ ] **Staged Aware**: Works with local git changes
- [ ] **Auto Revert**: Failures automatically roll back

## 🧹 Hygiene Features (NEW)

```bash
# Test debt ratchet (prevent lint regression)
python tools/ci/debt_ratchet.py

# Check ownership routing for files
python -c "from tools.ci.owners_from_codeowners import map_files_to_owners; print(map_files_to_owners(['src/file.py']))"

# Generate weekly dashboard
python tools/reports/weekly_hygiene.py

# Check coverage gaps
python tools/ci/needs_golden.py
```

## 🚨 Emergency Commands

```bash
# Check LLM connectivity
echo "def test(): pass" | ollama run deepseek-coder

# Validate configuration
python -c "import tomli; print('✅ Config OK')"

# Clear temp patches
rm -f /tmp/t4_patch_*

# Reset to safe defaults
cp .t4autofix.toml.example .t4autofix.toml

# Manual revert
git checkout -- src/file.py
```

## 📋 Common Workflows

### 🎯 Interactive Fix (Primary)
1. Cursor on TODO[T4-AUTOFIX] line
2. **⌘⇧Q** → Generate patch
3. Review patch in VS Code
4. **⌘⇧W** → Apply with checks

### 🔄 Batch Processing
1. `tools/ci/mark_todos.py --scan src/`
2. `tools/ci/run_autofix.sh`
3. Review changes in git diff
4. Commit or adjust policy

### 🔍 Troubleshooting
1. **T4_DEBUG=1** for verbose output
2. Check **VS Code Output panel**
3. Verify **Ollama status**: `ollama list`
4. Test **policy patterns** in config

## ⚙️ Configuration Quick Edits

### Allow New File Patterns
```toml
[scope]
allow_patterns = ["src/**", "lib/**", "new_module/**"]
```

### Enable New Transformations
```toml
[transformations.safe]
your_new_rule = true
```

### Adjust LLM Settings
```toml
[llm]
model = "codellama"           # or "deepseek-coder"
timeout_seconds = 60          # for complex fixes
max_context_lines = 150       # more context
```

## 📊 Status Indicators

| Symbol | Meaning          | Action               |
| ------ | ---------------- | -------------------- |
| 🤖      | LLM processing   | Wait for completion  |
| ⏱️      | Timeout fallback | Review stub patch    |
| ✅      | Success          | Apply or commit      |
| ❌      | Failed tests     | Check errors, revert |
| 🛡️      | Policy blocked   | Update configuration |
| 📝      | Patch generated  | Review in VS Code    |
| 🧹      | Hygiene check    | Debt ratchet active  |
| 📈      | Coverage gap     | needs-golden label   |
| ▁▂▃▄▅▆▇█ | Sparklines      | Weekly trend data    |

## 🔗 Resources

- **Full Manual**: `docs/gonzo/T4_AUTOFIX_USER_MANUAL.md`
- **System Status**: `docs/gonzo/T4-QUICKFIX-SYSTEM-COMPLETE.md`
- **Configuration**: `.t4autofix.toml` (policy rules)
- **Agent Coordination**: `CLAUDE.md`

## 🆘 Help & Support

```bash
# Get help
tools/dev/t4_quickfix.py --help

# System info
tools/dev/t4_quickfix.py --version

# Debug mode
T4_DEBUG=1 tools/dev/t4_quickfix.py src/file.py

# VS Code tasks
⌘⇧P → "Tasks: Run Task" → T4 operations
```

---

**Quick Start**: Cursor on TODO → **⌘⇧Q** → Review → **⌘⇧W**
**Emergency**: `rm -f /tmp/t4_patch_*` and `git checkout -- file.py`
**Status**: ✅ OPERATIONAL | **Authority**: Deputy Assistant GitHub Copilot

*Constellation Framework (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum) - LUKHAS AI Agent Army*
