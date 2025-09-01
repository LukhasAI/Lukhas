# 🚀 AGENT QUICK START GUIDE

**Immediate Action Protocol for LUKHAS AI Agent Army**
*Version: Trinity Framework v3.0*

---

## 🎯 QUICK START (2 Minutes)

### 1. Check Your Assignment
```bash
# View your assigned tasks
python track_mypy_progress.py | grep "YOUR_AGENT_NAME"
```

### 2. Get Task Details
```bash
# Read the coordination hub
cat AGENT_ARMY_COORDINATION.md | grep -A 20 "YOUR_AGENT_NAME"
```

### 3. Access Error Database
```bash
# Your specific errors
python -c "
import json
with open('mypy_errors_enumeration.json') as f:
    data = json.load(f)
    for task in data['tasks']:
        if task['assigned_agent'] == 'YOUR_AGENT_NAME':
            print(f'Task: {task[\"task_id\"]}')
            print(f'Files: {task[\"files\"]}')
            print(f'Errors: {len(task[\"errors\"])}')
            break
"
```

---

## 🛠️ IMMEDIATE EXECUTION PROTOCOL

### For Each Assigned File:

1. **Run mypy on your file**:
```bash
python -m mypy YOUR_FILE.py --show-error-codes --pretty
```

2. **Fix errors systematically**:
   - Start with import errors
   - Fix type annotation issues
   - Add type: ignore for unavoidable cases
   - Test functionality preservation

3. **Validate fixes**:
```bash
python -m mypy YOUR_FILE.py --show-error-codes
```

4. **Update progress**:
```bash
python track_mypy_progress.py
```

---

## 📋 AGENT-SPECIFIC QUICK REFERENCES

### Agent Jules (WebAuthn Security)
**Files**: `lukhas/identity/webauthn.py`
**Priority**: CRITICAL
**Errors**: 12

**Quick Commands**:
```bash
# Check your errors
python -m mypy lukhas/identity/webauthn.py --show-error-codes --pretty

# Common fixes needed:
# 1. Add type annotations to cache dictionaries
# 2. Fix Optional[str] conflicts
# 3. Add type: ignore for dynamic access
```

### Agent Consciousness (Lambda ID)
**Files**: `lukhas/identity/lambda_id.py`
**Priority**: CRITICAL
**Errors**: 10

**Quick Commands**:
```bash
python -m mypy lukhas/identity/lambda_id.py --show-error-codes --pretty
```

### Agent Core (Distributed Systems)
**Files**: `lukhas/core/distributed_tracing.py`, `lukhas/core/supervisor_agent.py`
**Priority**: CRITICAL
**Errors**: 17

**Quick Commands**:
```bash
python -m mypy lukhas/core/distributed_tracing.py --show-error-codes --pretty
python -m mypy lukhas/core/supervisor_agent.py --show-error-codes --pretty
```

---

## 🔧 COMMON FIX PATTERNS

### Type Annotation Fixes
```python
# Before
def process_data(data):
    pass

# After
def process_data(data: dict[str, Any]) -> dict[str, Any]:
    pass
```

### Dictionary Type Fixes
```python
# Before
cache = {}

# After
cache: dict[str, Any] = {}
```

### Optional Type Fixes
```python
# Before
def get_user(user_id: str) -> str:
    return None

# After
def get_user(user_id: str) -> str | None:
    return None
```

### Type Ignore (When Necessary)
```python
# Specific error code
result = dynamic_call()  # type: ignore[attr-defined]

# Multiple codes
result = complex_call()  # type: ignore[attr-defined,union-attr]
```

---

## ✅ VALIDATION CHECKLIST

- [ ] All import errors resolved
- [ ] Type annotations added to all functions
- [ ] Dictionary/object types properly annotated
- [ ] Optional types correctly used
- [ ] Type: ignore comments specific and justified
- [ ] Functionality preserved (run existing tests)
- [ ] Mypy passes with no errors on your files

---

## 🚨 EMERGENCY PROTOCOLS

### If You Encounter:
- **Complex Type Issues**: Document and ask for coordination
- **Functionality Breaking**: Revert and seek guidance
- **Unsure About Fix**: Check AGENT_ARMY_COORDINATION.md examples

### Communication:
- **Blockers**: Update this guide with issues found
- **Success**: Mark tasks complete in coordination hub
- **Questions**: Reference specific error codes and files

---

## 📊 PROGRESS TRACKING

### Daily Check-in:
```bash
# Your progress
python track_mypy_progress.py

# Overall project status
python -c "
import json
with open('mypy_errors_enumeration.json') as f:
    data = json.load(f)
    total_errors = sum(len(task['errors']) for task in data['tasks'])
    print(f'Total remaining errors: {total_errors}')
"
```

### Completion Criteria:
- ✅ Your assigned files pass mypy validation
- ✅ No functionality regressions
- ✅ All type annotations modernized
- ✅ Documentation updated if needed

---

## 🎯 SUCCESS METRICS

**Individual Agent Goals:**
- 100% of assigned errors resolved
- Code quality maintained or improved
- Timeline adherence
- Zero functionality breaking changes

**Team Success:**
- 80% overall error reduction
- Zero critical import/attribute errors
- Modern Python typing throughout
- Improved code maintainability

---

*Remember: Quality over speed. Fix it right the first time.*

**Quick Reference**: `AGENT_ARMY_COORDINATION.md` for full details
**Progress**: `track_mypy_progress.py` for real-time updates
**Errors**: `mypy_errors_enumeration.json` for task database
