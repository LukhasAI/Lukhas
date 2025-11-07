# Jules API Options Tree - Complete Reference

**Current Quota**: 86/100 sessions used (14 available now, 100 after reset)
**Quota Reset**: In a few hours (~24h cycle)
**Last Updated**: 2025-11-06 20:55 UTC

---

## 📊 Quota & Limits

### Check Current Quota
```python
async with JulesClient() as jules:
    sessions = await jules.list_sessions(page_size=100)
    total = len(sessions.get('sessions', []))
    print(f"Active: {total}, Available: {100 - total}")
```

**Limits**:
- **Daily Quota**: 100 sessions/day (paid tier)
- **Resets**: Every 24 hours
- **Rollover**: No - use them or lose them!
- **Recommendation**: Create 20-30 sessions daily for optimal ROI

---

## 🔧 JulesClient Methods

### 1. **list_sources()** - List Connected Repositories

**Purpose**: Get all repositories connected to Jules
**Parameters**: None
**Returns**: List of JulesSource objects

```python
sources = await jules.list_sources()
# Returns: [JulesSource(name, display_name, repository_url, create_time)]
```

**Fields in Response**:
- `name`: Resource ID (e.g., "sources/123456789")
- `display_name`: Human-readable name
- `repository_url`: GitHub URL
- `create_time`: When connected

---

### 2. **get_source_by_url(repository_url)** - Find Source by URL

**Purpose**: Lookup source ID by repository URL
**Parameters**:
- `repository_url` (str): GitHub repo URL

```python
source = await jules.get_source_by_url("https://github.com/LukhasAI/Lukhas")
# Returns: JulesSource or None
```

---

### 3. **create_session()** - Create New Coding Session

**Purpose**: Start a new Jules task/session
**This is the main method you'll use most!**

#### Required Parameters
- `prompt` (str): Task description for Jules

#### Source Identification (pick ONE)
- `source_id` (str): Resource name like "sources/123456789"
  *OR*
- `repository_url` (str): GitHub URL (will auto-lookup source)

#### Optional Parameters
- `display_name` (str): Session title/name for organization
- `automation_mode` (str): Automation level
  - `"AUTO_CREATE_PR"` - Automatically create PR when done (RECOMMENDED)
  - `None` - Manual PR creation
- `require_plan_approval` (bool): Whether to wait for plan approval
  - `False` - Auto-approve plans (RECOMMENDED for speed)
  - `True` - Wait for manual approval via `approve_plan()`

#### Full Example
```python
session = await jules.create_session(
    prompt="Write comprehensive tests for labs/core/identity/",
    source_id="sources/github/LukhasAI/Lukhas",  # or use repository_url
    display_name="TEST-044: Identity Module Tests",
    automation_mode="AUTO_CREATE_PR",
    require_plan_approval=False
)
```

#### Response Fields
- `id`: Session ID (numeric string)
- `name`: Full resource name "sessions/{id}"
- `state`: Current state (see Session States below)
- `title`/`displayName`: Session name
- `createTime`: Creation timestamp
- `prompt`: Original task prompt

---

### 4. **list_sessions()** - List All Sessions

**Purpose**: Get paginated list of sessions
**Parameters**:
- `page_size` (int): Sessions per page (default: 50, max: 100)
- `page_token` (str): For pagination (from previous response)

```python
result = await jules.list_sessions(page_size=50)
sessions = result.get('sessions', [])
next_page = result.get('nextPageToken')
```

**Pagination Example**:
```python
all_sessions = []
page_token = None

while True:
    result = await jules.list_sessions(page_size=50, page_token=page_token)
    all_sessions.extend(result.get('sessions', []))
    page_token = result.get('nextPageToken')
    if not page_token:
        break
```

---

### 5. **get_session(session_id)** - Get Session Details

**Purpose**: Fetch specific session information
**Parameters**:
- `session_id` (str): Session resource name "sessions/123"

```python
session = await jules.get_session("sessions/123456789")
state = session.get('state')
```

---

### 6. **approve_plan(session_id)** - Approve Generated Plan

**Purpose**: Manually approve Jules' execution plan
**When to Use**: Only if `require_plan_approval=True` was set
**Parameters**:
- `session_id` (str): Session resource name

```python
await jules.approve_plan("sessions/123456789")
```

**Note**: Not needed if `require_plan_approval=False` (auto-approves)

---

### 7. **send_message(session_id, message)** - Send Feedback to Jules

**Purpose**: Give Jules instructions, corrections, or feedback
**Parameters**:
- `session_id` (str): Session resource name
- `message` (str): Your message/instructions

```python
await jules.send_message(
    "sessions/123456789",
    "Use lukhas.* imports instead of core.* imports"
)
```

**When to Use**:
- Session is in AWAITING_FEEDBACK state
- You want to correct Jules' approach
- You want to provide additional context

---

### 8. **delete_session(session_id)** - Delete Session

**Purpose**: Remove completed session to free quota
**Parameters**:
- `session_id` (str): Session resource name

```python
await jules.delete_session("sessions/123456789")
```

**Best Practice**: Delete completed sessions whose PRs are merged to free quota slots

---

### 9. **list_activities(session_id)** - Get Session Activities

**Purpose**: Fetch session activity log (messages, plans, code changes)
**Parameters**:
- `session_id` (str): Session resource name
- `page_size` (int): Activities per page (default: 100)
- `page_token` (str): Pagination token

```python
result = await jules.list_activities("sessions/123456789", page_size=100)
activities = result.get('activities', [])
```

**Activity Types**:
- `PLAN` - Jules created an execution plan
- `MESSAGE` - Text message (from you or Jules)
- `CODE_CHANGE` - Code modifications
- `SYSTEM` - System events

---

### 10. **stream_activities(session_id)** - Real-time Activity Stream

**Purpose**: Monitor session progress in real-time
**Parameters**:
- `session_id` (str): Session resource name
- `poll_interval` (float): Seconds between polls (default: 2.0)
- `timeout` (float): Max time to monitor (default: None = forever)

```python
async for activity in jules.stream_activities("sessions/123", poll_interval=2.0):
    if activity.type == "MESSAGE":
        print(f"Jules: {activity.message}")
    elif activity.type == "PLAN":
        print("Plan created!")
```

**Use Case**: Real-time monitoring of long-running sessions

---

## 📋 Session States

### State Machine
```
PLANNING → IN_PROGRESS → COMPLETED
    ↓           ↓            ↓
AWAITING_    AWAITING_   FAILED
 PLAN_      FEEDBACK
 APPROVAL
```

### State Descriptions

| State | Meaning | Action Needed |
|-------|---------|---------------|
| **PLANNING** | Jules is creating execution plan | None (auto-approves if configured) |
| **AWAITING_PLAN_APPROVAL** | Plan ready, needs approval | Call `approve_plan()` |
| **IN_PROGRESS** | Jules is writing code | Wait for completion |
| **AWAITING_FEEDBACK** | Jules needs your input | Call `send_message()` with instructions |
| **COMPLETED** | Task finished successfully | Review PR, delete session |
| **FAILED** | Task failed | Review error, retry or delete |
| **CANCELLED** | You cancelled the session | Delete session |

---

## 🎯 Common Workflows

### Workflow 1: Batch Create Sessions (Recommended)

```python
async with JulesClient() as jules:
    sessions = [
        {
            "title": "TEST-044: Identity Tests",
            "prompt": "Write tests for labs/core/identity/",
        },
        {
            "title": "TEST-045: Memory Tests",
            "prompt": "Write tests for labs/memory/",
        },
    ]

    for config in sessions:
        session = await jules.create_session(
            prompt=config['prompt'],
            display_name=config['title'],
            source_id="sources/github/LukhasAI/Lukhas",
            automation_mode="AUTO_CREATE_PR",
            require_plan_approval=False
        )
        print(f"✅ Created: {session.get('id')}")
```

---

### Workflow 2: Check Session Status

```python
async with JulesClient() as jules:
    # Get all sessions
    result = await jules.list_sessions(page_size=100)

    # Group by state
    by_state = {}
    for session in result.get('sessions', []):
        state = session.get('state')
        by_state.setdefault(state, []).append(session)

    # Show summary
    for state, sessions in by_state.items():
        print(f"{state}: {len(sessions)} sessions")
```

---

### Workflow 3: Respond to Waiting Sessions

```python
async with JulesClient() as jules:
    result = await jules.list_sessions()

    for session in result.get('sessions', []):
        state = session.get('state')
        sid = session.get('name')

        if state == 'AWAITING_PLAN_APPROVAL':
            await jules.approve_plan(sid)
            print(f"✅ Approved: {sid}")

        elif state == 'AWAITING_FEEDBACK':
            await jules.send_message(sid, "Continue with your approach!")
            print(f"💬 Sent feedback: {sid}")
```

---

### Workflow 4: Cleanup Completed Sessions

```python
async with JulesClient() as jules:
    result = await jules.list_sessions()

    # Get open PRs
    open_prs = {1003, 1006, 1016}  # Example PR numbers

    for session in result.get('sessions', []):
        if session.get('state') == 'COMPLETED':
            title = session.get('displayName', '')
            sid = session.get('name')

            # Check if PR is still open
            has_open_pr = any(f"#{pr}" in title for pr in open_prs)

            if not has_open_pr:
                await jules.delete_session(sid)
                print(f"🗑️  Deleted: {title}")
```

---

## 💡 Best Practices

### 1. Session Creation
- ✅ Always use `automation_mode="AUTO_CREATE_PR"`
- ✅ Always set `require_plan_approval=False` for speed
- ✅ Use descriptive `display_name` for organization
- ✅ Batch create sessions (10-20 at once) for efficiency

### 2. Session Titles
Format: `{TYPE}-{NUMBER}: {Description}`

Examples:
- `TEST-044: Labs Identity Tests`
- `IMPL-007: Redis Caching Layer`
- `FIX-012: E402 Import Violations`
- `REFACTOR-003: Simplify Memory Manager`

### 3. Prompts
Write clear, specific prompts:

**Good Prompts**:
```
Write comprehensive tests for labs/core/identity/.

Focus on:
- identity_manager.py - Identity lifecycle
- lambda_id_core.py - ΛiD implementation
- Authentication flows

Requirements:
- Use pytest-asyncio
- Mock external services
- Achieve >85% coverage
```

**Bad Prompts**:
```
Add tests  # Too vague!
Fix the bugs  # No specificity!
```

### 4. Quota Management
- Create 20-30 sessions daily to maximize ROI
- Delete completed sessions promptly
- Sessions don't roll over - use or lose!

### 5. PR Management
- Let Jules create PRs automatically
- Review PRs as they come in
- Tag @codex for merge conflicts
- Keep PRs open until merged

---

## 🚨 Troubleshooting

### Error: "No source found for repository"
**Solution**: Repository not connected in Jules app
1. Go to https://jules.google.com/
2. Connect your GitHub repository
3. Use `list_sources()` to find source ID

### Error: "Sessions/123: approvePlan not found (404)"
**Cause**: Session already auto-approved
**Solution**: This is normal if `require_plan_approval=False`

### Session Stuck in AWAITING_FEEDBACK
**Solution**: Jules needs your input
```python
await jules.send_message(session_id, "Your instructions here")
```

### Too Many Active Sessions
**Solution**: Delete completed sessions
```python
await jules.delete_session("sessions/123")
```

---

## 📖 Quick Reference Card

### Create Session (Most Common)
```python
async with JulesClient() as jules:
    session = await jules.create_session(
        prompt="Your task here",
        source_id="sources/github/LukhasAI/Lukhas",
        display_name="TEST-044: Module Tests",
        automation_mode="AUTO_CREATE_PR",
        require_plan_approval=False
    )
```

### Check All Sessions
```python
result = await jules.list_sessions(page_size=100)
```

### Delete Session
```python
await jules.delete_session("sessions/123456789")
```

### Send Feedback
```python
await jules.send_message("sessions/123", "Use pattern X")
```

---

## 🔗 Related Documentation

- [Jules API Complete Reference](JULES_API_COMPLETE_REFERENCE.md)
- [Jules 15 Sessions Status](JULES_13_SESSIONS_STATUS_2025-11-06.md)
- [Create Jules Sessions Guide](CREATE_7_JULES_SESSIONS.md)

---

**Quota Status**: 86/100 sessions used
**Available Now**: 14 sessions
**After Reset**: 100 sessions (in a few hours)
**Recommendation**: Use remaining 14 sessions, then create 20-30 more after reset

**Updated**: 2025-11-06 20:55 UTC

**Note**: Quota shown on Jules web UI may differ from API count. Trust web UI numbers.
