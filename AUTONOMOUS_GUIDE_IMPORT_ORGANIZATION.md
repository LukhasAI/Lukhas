# Autonomous Guide: Fix Import Organization (E402 Violations)

**Goal:** Fix 1,978 "module import not at top of file" violations
**Priority:** Medium
**Estimated Time:** 6-8 hours
**Compatible With:** Claude Code, Codex, Copilot + ruff --fix

---

## Quick Start

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Check current E402 count
python3 -m ruff check . --select E402 --statistics

# Auto-fix what's safe
python3 -m ruff check . --select E402,I001 --fix

# Verify smoke tests
make smoke  # Must be 10/10 PASS
```

---

## Execution Strategy

### Phase 1: Auto-fix Safe Cases (2 hours)
```bash
# Start with production lane only
python3 -m ruff check lukhas/ --select E402,I001 --fix
python3 -m ruff check core/ --select E402,I001 --fix
python3 -m ruff check serve/ --select E402,I001 --fix

make smoke  # Validate after each
```

### Phase 2: Manual Fix Complex Cases (4-6 hours)
Focus on files where imports depend on runtime configuration:
- Files with `sys.path` modifications
- Files with conditional imports
- Files with import-time side effects

**Pattern to Fix:**
```python
# Before (E402 violation)
import sys
sys.path.append("...")  # Runtime modification
import mymodule  # E402: import not at top

# After (Compliant)
import sys
import mymodule  # Move before sys.path if possible
# OR add # noqa: E402 if runtime dependency is required
```

### Phase 3: Add noqa for Legitimate Cases
```bash
# Files that MUST have imports mid-file (rare)
# Add: # noqa: E402
# Document WHY in adjacent comment
```

---

## Success Criteria
- ✅ E402 count <100 (95% reduction)
- ✅ Smoke tests 10/10 PASS
- ✅ All auto-fixes committed
- ✅ Manual fixes documented

**Timeline:** 1-2 weeks (incremental sessions)
**Risk:** Low (ruff --fix is safe)
