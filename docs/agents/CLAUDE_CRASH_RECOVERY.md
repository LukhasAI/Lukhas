# Claude Code Crash Recovery & Prevention Guide

## ⚠️ IMPORTANT: Claude Code Crash Context
**Last Updated**: 2025-08-12
**Issue**: Claude Code crashes during plan execution (2nd occurrence)
**Environment**: macOS Darwin 25.0.0, Claude Code v1.0.77

## 🔴 Crash Symptoms
- Crashes during plan execution phase
- Node.js crypto/SSL layer errors (`node::PrincipalRealm::crypto_key_object_private_constructor`)
- Thread state dumps with memory addresses
- `claude sessions list` command timeouts

## 🛠️ Prevention Measures

### 1. Environment Setup (Run Before Starting Work)
```bash
# Activate virtual environment
source /Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/bin/activate

# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=8192"

# Clear Claude Code cache if needed
rm -rf ~/.claude/cache/*
```

### 2. Avoid These Operations
- ❌ Processing files larger than 10MB at once
- ❌ Running multiple intensive tasks simultaneously
- ❌ Complex multi-agent deployments without breaks
- ❌ Large-scale file searches without using Task tool
- ❌ Batch operations on 100+ files simultaneously

### 3. Safe Working Practices
- ✅ Use `Task` tool for complex searches
- ✅ Break large operations into smaller chunks
- ✅ Commit changes frequently to preserve work
- ✅ Use TodoWrite tool to track progress (enables recovery)
- ✅ Save work state before running intensive operations

## 📋 Session Recovery Steps

### If Claude Code Crashes:
1. **Resume the session**:
   ```bash
   claude --resume
   # or
   claude --continue --print
   ```

2. **Check last working state**:
   ```bash
   git status
   git diff
   git log --oneline -5
   ```

3. **Review pending work**:
   - Check `MODULE_STATUS_REPORT.md` for last status
   - Review modified files in git status
   - Check test results in `test_results/`

## 🔍 Current Project Context (LUKHAS AI)

### Active Work Areas (as of last crash):
- **Modified Files** (uncommitted):
  - `bridge/adapters/service_adapter_base.py`
  - `MODULE_STATUS_REPORT.md`
  - `governance/security/security_audit_engine.py`
  - `lukhas/branding.py`
  - `security/scanning/consciousness-security-rules.py`
  - `tests/canary/test_candidate_systems.py`
  - `universal_language/__init__.py.shim`
  - `CLAUDE_CRASH_RECOVERY.md` (this file)

### Pending Tasks from MODULE_STATUS_REPORT.md:
1. **Test Suite Enhancement**: Add pytest coverage for critical untested modules
2. **Documentation Sprint**: Add docstrings to 219 undocumented files  
3. **Cleanup Operation**: Remove obsolete and empty files
4. **Architecture Review**: Consolidate orphaned modules
5. **Trinity Compliance**: Ensure all modules follow ⚛️🧠🛡️ patterns

### Test Coverage Status:
- **Identity Module**: 73% coverage, 93/96 tests passing (97% pass rate)
- **Overall Test Ratio**: 5.7% (199 test files / 3,490 Python files)
- **Priority Untested Modules**: quantum_attention, identity_tag_resolver, memory_interface

### Recent Commits:
- `0b029a58` - feat: Complete Phase 4 candidate systems migration with feature flags
- `b85b2b62` - feat: Complete colony system infrastructure (Phase 3c)
- `4a092fd1` - feat: Complete memory module consolidation (Phase 3b)
- `43f74b30` - feat: Complete bio module consolidation (Phase 3a)
- `376bcfea` - feat: Implement 4-lane code maturity architecture

### Known Working Commands:
```bash
# Testing
make test
pytest tests/canary/test_candidate_systems.py -v

# Code quality
make fix
make lint

# System analysis
python tools/analysis/_FUNCTIONAL_ANALYSIS.py
python tools/analysis/_OPERATIONAL_SUMMARY.py

# Deployment
./CLAUDE_ARMY/deploy_claude_max_6_agents.sh
```

## 🚀 Quick Recovery Checklist

- [ ] Activate virtual environment
- [ ] Set NODE_OPTIONS for memory
- [ ] Check git status for pending changes
- [ ] Review MODULE_STATUS_REPORT.md
- [ ] Run tests to verify system state
- [ ] Continue with pending tasks

## 💡 Tips for Next Agent
1. This is the LUKHAS AI repository - uses Trinity Framework (⚛️🧠🛡️)
2. Always use "LUKHAS AI" (not "LUKHAS AGI" or "Lukhas ")
3. Check CLAUDE.md for full project guidelines
4. Current phase: Post-Phase 4 (candidate systems migration completed)
5. If you encounter similar crashes, try breaking the task into smaller pieces

## 🔧 Emergency Commands
```bash
# Kill stuck Claude processes
pkill -f claude

# Update Claude Code (if needed)
npm update -g claude-code

# Check system resources
df -h /
top -l 1 | head -10

# Quick project status
git status
make test
```

---
**Note**: This document should be updated after each crash incident to help future agents recover quickly.