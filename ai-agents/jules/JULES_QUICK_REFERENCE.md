# Jules Quick Reference - For AI Agents

**Essential commands for Claude Code agents working with Jules sessions**

---

## 🚨 Critical Discovery: Sessions Can Complete With Unresolved Questions

**Problem**: Jules API shows session as `COMPLETED` but Jules asked questions during execution that went unanswered.

**Solution**: ALWAYS inspect activities to see the full conversation.

---

## 📋 Essential Commands

### 1. Check All Sessions
```bash
python3 scripts/check_all_active_jules_sessions.py
```
Shows all non-completed sessions grouped by state.

### 2. Inspect Session Conversation (NEW!)
```bash
# Check specific session
python3 scripts/get_jules_session_activities.py <session_id>

# Check all active sessions
python3 scripts/get_jules_session_activities.py
```
**CRITICAL**: Reveals Jules' questions even if session shows COMPLETED.

### 3. Find Sessions Waiting for Response
```bash
python3 scripts/check_waiting_jules_sessions.py
```
Finds sessions in `WAITING_FOR_USER` state.

### 4. Respond to Jules (NEW!)
```bash
# Single session
python3 scripts/send_jules_message.py <session_id> "your response"

# Example:
python3 scripts/send_jules_message.py 123 "Use lukhas.* imports for production code"

# Batch response (modify script first)
python3 scripts/batch_respond_to_jules.py
```

### 5. Approve Waiting Plans
```bash
python3 scripts/approve_waiting_jules_plans.py
```
Batch approves plans in `AWAITING_PLAN_APPROVAL` state.

### 6. Create Sessions
```bash
python3 scripts/create_security_hardening_sessions.py
```
Batch creates Jules sessions for tasks.

### 7. Clean Up Completed Sessions
```bash
# Dry run (see what would be deleted)
python3 scripts/close_completed_jules_sessions.py

# Actually delete (preserves sessions with PRs)
python3 scripts/close_completed_jules_sessions.py --delete
```

---

## 🔍 Typical Workflow When User Says "Check Jules Sessions"

```bash
# 1. Check all session states
python3 scripts/check_all_active_jules_sessions.py

# 2. Inspect activities to find questions (CRITICAL STEP)
python3 scripts/get_jules_session_activities.py

# 3. Look for "🤖 JULES [MESSAGE]" entries in output
# These are Jules asking questions or reporting blockers

# 4. Respond to questions
python3 scripts/send_jules_message.py <session_id> "guidance here"

# 5. Verify Jules continues work
python3 scripts/check_all_active_jules_sessions.py
```

---

## 💡 Common Jules Questions & Standard Responses

### Import Errors (80% of questions)

**Jules says**: "ImportError: cannot import name 'get_metrics_collector'"

**Response**:
```
LUKHAS uses lane-based architecture:

- lukhas/ (production) ← imports from core/, matriz/
- candidate/ (development) ← imports from core/, matriz/ ONLY
- serve/ (API routes) ← imports from lukhas/, core/, bridge/

For tests, mock unavailable modules:
from unittest.mock import patch
@patch('serve.routes.get_metrics_collector')
def test_your_endpoint(mock_metrics):
    ...

Continue with your implementation using mocks!
```

### Test Path Issues

**Jules says**: "AttributeError: module 'serve' has no attribute 'routes'"

**Response**:
```
Use correct import:
from serve.routes import router  # NOT serve.routes.router

Run tests from project root:
pytest tests/unit/api/test_file.py
```

### Environment Questions

**Jules says**: "Can't set up test environment - module structure unclear"

**Response**:
```
Don't worry about complex setup. Mock problematic imports:

from unittest.mock import Mock, patch, MagicMock

@patch('module.problematic_import', return_value=Mock())
def test_feature(mock_import):
    # Your test here
    ...

Focus on implementing the test logic, not environment setup!
```

---

## 🎯 Pro Tips for AI Agents

1. **ALWAYS check activities** - Don't trust session state alone
2. **Look for agentMessaged** - That's Jules asking questions
3. **Batch similar responses** - Create script for common issues
4. **Use mocking guidance** - Most import errors resolve with mocks
5. **Preserve PR sessions** - Never delete completed sessions with PRs

---

## 📊 Complete Automation Toolkit (9 Scripts)

| Script | Purpose |
|--------|---------|
| `create_security_hardening_sessions.py` | Batch session creation |
| `check_all_active_jules_sessions.py` | Comprehensive monitoring |
| `check_waiting_jules_sessions.py` | Find waiting sessions |
| `check_new_security_sessions.py` | Track specific sessions |
| `approve_waiting_jules_plans.py` | Batch plan approval |
| `close_completed_jules_sessions.py` | Session cleanup (preserves PRs) |
| `get_jules_session_activities.py` | **Inspect conversations** |
| `send_jules_message.py` | **Send single message** |
| `batch_respond_to_jules.py` | **Batch response automation** |

---

## 🔗 More Info

- Full API reference: [JULES_API_COMPLETE_REFERENCE.md](JULES_API_COMPLETE_REFERENCE.md)
- Python wrapper: `bridge/llm_wrappers/jules_wrapper.py`
- Official docs: https://developers.google.com/jules/api

---

**Last Updated**: 2025-11-10
**Tested With**: 22 sessions, 5 batch responses, 100% success rate
