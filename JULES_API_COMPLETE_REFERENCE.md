# Jules API Complete Reference & Feature Discovery

**Last Updated**: 2025-11-06
**API Version**: v1alpha (experimental - subject to change)
**Official Docs**: https://developers.google.com/jules/api

---

## 🎯 Core Concepts

### 1. Source
Your connected GitHub repository. Jules can access code but NOT production databases.

### 2. Session
An asynchronous "project" or "task" - like a chat session where Jules plans, codes, and executes work.

### 3. Activity
Individual steps, events, and messages within a session. Every action is tracked as an activity.

---

## 📡 Complete API Endpoints

### Sources

#### `GET /v1alpha/sources`
List all connected GitHub repositories.

**Response**: Array of source objects with:
- `name`: Resource identifier (e.g., "sources/github/owner/repo")
- `displayName`: Human-readable name
- `repositoryUrl`: GitHub URL
- `createTime`: When connected

**Example**:
```bash
curl 'https://jules.googleapis.com/v1alpha/sources' \
  -H 'X-Goog-Api-Key: YOUR_API_KEY'
```

---

### Sessions

#### `POST /v1alpha/sessions`
Create a new coding session.

**Request Body**:
```json
{
  "prompt": "Task description",
  "title": "Session display name",
  "sourceContext": {
    "source": "sources/github/owner/repo",
    "githubRepoContext": {
      "startingBranch": "main"
    }
  },
  "automationMode": "AUTO_CREATE_PR",
  "requirePlanApproval": false
}
```

**Parameters**:
- `prompt` (required): Task instructions for Jules
- `title` (optional): Display name for session
- `sourceContext` (required):
  - `source`: Source identifier from sources API
  - `githubRepoContext.startingBranch`: Branch to work on
- `automationMode` (optional):
  - `"AUTO_CREATE_PR"`: Automatically create pull requests
  - Default: Manual PR creation
- `requirePlanApproval` (optional):
  - `true`: Requires explicit plan approval before execution
  - `false` (default for API): Plans auto-approved

**Response**: Session object with `name`, `state`, `createTime`

#### `GET /v1alpha/sessions`
List sessions with pagination.

**Query Parameters**:
- `pageSize`: Number of sessions per page (default: 50)
- `pageToken`: Token for next page

**Response**:
```json
{
  "sessions": [...],
  "nextPageToken": "..."
}
```

#### `GET /v1alpha/sessions/{SESSION_ID}`
Get details for a specific session.

**Response**: Full session object with state, prompt, activities count, etc.

---

### Session Actions

#### `POST /v1alpha/sessions/{SESSION_ID}:approvePlan`
Approve the latest plan in a session.

**Request Body**: `{}` (empty)

**Response**: `{}` (empty - plan is approved)

**Effect**: Session moves from `AWAITING_PLAN_APPROVAL` to `IN_PROGRESS`

**Example**:
```python
await jules.approve_plan("sessions/123")
```

#### `POST /v1alpha/sessions/{SESSION_ID}:sendMessage`
Send feedback or instructions to Jules.

**Request Body**:
```json
{
  "prompt": "Your message or feedback"
}
```

**Response**: `{}` (empty)

**Note**: Jules' response appears as next activity. Poll activities to see reply.

**Example**:
```python
await jules.send_message(
    "sessions/123",
    "Use lukhas.* imports instead of core.* imports"
)
```

---

### Activities

#### `GET /v1alpha/sessions/{SESSION_ID}/activities`
List all activities for a session.

**Query Parameters**:
- `pageSize`: Activities per page (default: 100)
- `pageToken`: Token for pagination

**Response**:
```json
{
  "activities": [
    {
      "name": "sessions/123/activities/456",
      "type": "PLAN",
      "createTime": "2025-11-06T12:00:00Z",
      "message": {...},
      "artifacts": [...]
    }
  ],
  "nextPageToken": "..."
}
```

**Activity Types**:
- `PLAN`: Jules generated a plan
- `MESSAGE`: User or agent message
- `BASH_OUTPUT`: Command execution result
- `CODE_CHANGE`: File modifications
- `SCREENSHOT`: Frontend verification
- `CODE_REVIEW`: Review comments
- `COMPLETION`: Session ended

**Artifacts**:
- Git patches with change sets
- Bash output with exit codes
- Images/screenshots
- PR details (URL, description)

---

## 🚀 Advanced Features

### 1. Memory System (2025 Update)
Jules now maintains:
- **Interaction history**: Remembers past sessions
- **User preferences**: Learns coding style, patterns
- **Corrections**: Applies learned nudges to future tasks

**Status**: Automatic - no API configuration needed

### 2. Image Upload
Upload screenshots or mockups for Jules to implement.

**Status**: Web UI feature (API support unclear)

### 3. PR Comment Reading
Jules can read and respond to PR review comments.

**Status**: Automatic during PR workflows

### 4. Stacked Diff Viewer
Enhanced code review with better diff visualization.

**Status**: Web UI enhancement

### 5. Batch Processing
Create multiple sessions that run in parallel on spare capacity.

**Capacity**: 15 daily tasks on free tier (Gemini 2.5-pro)
**Duration**: Tasks can run 1-2 hours each
**Throttling**: Async processing on spare capacity (slower than sync)

---

## ⚙️ Configuration Options

### Session States
- `ACTIVE`: Jules is working
- `IN_PROGRESS`: Executing approved plan
- `AWAITING_PLAN_APPROVAL`: Needs plan approval
- `AWAITING_USER_FEEDBACK`: Needs user response
- `COMPLETED`: Successfully finished
- `FAILED`: Encountered errors
- `CANCELLED`: User cancelled

### Automation Modes
- `AUTO_CREATE_PR`: Jules creates PRs automatically
- Default (no automation): Manual PR creation

### Plan Approval
- **API Default**: Plans auto-approved
- **Web UI**: Can require approval
- **Override**: Set `requirePlanApproval: true` in session creation

---

## 🔒 Authentication

**Method**: API Key via header

**Header**: `X-Goog-Api-Key: YOUR_API_KEY`

**Get API Key**: https://jules.google.com/settings#api

**Security**: Store in macOS Keychain or secure secrets manager

---

## 🎯 Best Practices

### 1. Session Management
```python
# Good: Auto-approve plans for batch jobs
session = await jules.create_session(
    prompt="Write tests for module X",
    source_id="sources/github/owner/repo",
    automation_mode="AUTO_CREATE_PR",
    require_plan_approval=False  # Auto-approve
)

# Good: Require approval for critical changes
session = await jules.create_session(
    prompt="Refactor authentication system",
    source_id="sources/github/owner/repo",
    require_plan_approval=True  # Manual approval
)
```

### 2. Activity Polling
```python
# Poll for completion
while True:
    session = await jules.get_session(session_id)
    if session['state'] in ['COMPLETED', 'FAILED']:
        break
    await asyncio.sleep(10)
```

### 3. Streaming Activities
```python
# Real-time activity stream
async for activity in jules.stream_activities(session_id):
    if activity.type == 'PLAN':
        print("Plan created - awaiting approval")
    elif activity.type == 'MESSAGE':
        print(f"Message: {activity.message}")
```

### 4. Error Handling
```python
try:
    session = await jules.create_session(...)
except ClientResponseError as e:
    if e.status == 400:
        # Check payload format
    elif e.status == 401:
        # Check API key
    elif e.status == 429:
        # Rate limited - back off
```

---

## 🚧 Known Limitations

### Cannot Do via API (yet):
- ❌ Publish PRs directly (must use web UI)
- ❌ Push branches programmatically
- ❌ Cancel running sessions (API support unclear)
- ❌ Update session mid-execution (send messages instead)
- ❌ Access production databases (by design)

### Observability Issues:
- Limited real-time progress updates
- File states only visible at checkpoints
- Mid-task corrections difficult

### Performance:
- Async processing on spare capacity (can be slow)
- Tasks may take 1-2 hours
- Free tier: 15 tasks/day

---

## 💡 Undocumented/Experimental Features

### Potential Endpoints (unconfirmed):
Based on API patterns, these MAY exist but are undocumented:

- `DELETE /v1alpha/sessions/{SESSION_ID}` - Cancel session?
- `PATCH /v1alpha/sessions/{SESSION_ID}` - Update session?
- `POST /v1alpha/sessions/{SESSION_ID}:pause` - Pause execution?
- `POST /v1alpha/sessions/{SESSION_ID}:resume` - Resume paused?
- Webhooks for session events?
- Filtering sessions by state?

**Status**: UNCONFIRMED - API is alpha and evolving

---

## 🔮 Integration Patterns

### 1. CI/CD Integration
```python
# Trigger Jules on test failures
if test_coverage < 75:
    await jules.create_session(
        prompt=f"Increase test coverage to 75%+ for {module}",
        automation_mode="AUTO_CREATE_PR"
    )
```

### 2. Bug Tracker Integration
```python
# Auto-assign bugs to Jules
@app.route('/webhook/bug-filed')
async def on_bug_filed(bug):
    await jules.create_session(
        prompt=f"Fix bug: {bug.title}\n\n{bug.description}",
        automation_mode="AUTO_CREATE_PR"
    )
```

### 3. Batch Test Creation
```python
# Create tests for multiple modules
for module in untested_modules:
    await jules.create_session(
        prompt=f"Write tests for {module}, target 75%+ coverage",
        automation_mode="AUTO_CREATE_PR"
    )
```

### 4. MCP Server Integration
Connect Jules to VS Code via Model Context Protocol for enhanced workflows.

---

## 📊 Rate Limits & Quotas

**Free Tier**:
- 15 sessions/day
- Gemini 2.5-pro model
- Counted by session, not tokens
- ~15+ hours theoretical capacity

**Unknown**:
- Concurrent session limits?
- API request rate limits?
- Activity polling limits?

---

## 🛠️ Tools & Libraries

### LUKHAS Integration
```python
from bridge.llm_wrappers.jules_wrapper import JulesClient

async with JulesClient() as jules:
    # API key from macOS Keychain
    session = await jules.create_session(...)
    await jules.approve_plan(session_id)
    await jules.send_message(session_id, "Use pattern X")
```

### Official Jules CLI
Google provides command-line tools for Jules management.

**Status**: Available but separate from API

---

## 📝 Example Workflows

### Complete Session Workflow
```python
async def run_jules_task():
    async with JulesClient() as jules:
        # 1. Create session
        session = await jules.create_session(
            prompt="Write smoke tests for critical paths",
            source_id="sources/github/owner/repo",
            title="TEST-014: Smoke Tests",
            automation_mode="AUTO_CREATE_PR"
        )

        session_id = session['name']

        # 2. Monitor until plan created
        while True:
            s = await jules.get_session(session_id)
            if s['state'] == 'AWAITING_PLAN_APPROVAL':
                break
            await asyncio.sleep(5)

        # 3. Approve plan
        await jules.approve_plan(session_id)

        # 4. Monitor until completion
        while True:
            s = await jules.get_session(session_id)
            if s['state'] in ['COMPLETED', 'FAILED']:
                break
            await asyncio.sleep(10)

        # 5. Check activities for results
        activities = await jules.list_activities(session_id)
        for activity in activities['activities']:
            if 'PR' in str(activity):
                print(f"PR created: {activity}")
```

---

## 🎓 Key Learnings

1. **Always use official payload format** - `sourceContext` not `sources`
2. **Plans auto-approve by default in API** - Override with `requirePlanApproval`
3. **Jules is async** - Design for 30min-2hr task completion
4. **Free tier is generous** - 15 sessions/day = lots of automation
5. **Memory is automatic** - Jules learns from corrections
6. **API is alpha** - Expect changes and new features

---

## 🔗 Resources

- **Official API Docs**: https://developers.google.com/jules/api
- **Jules Web UI**: https://jules.google.com
- **API Key Setup**: https://jules.google.com/settings#api
- **LUKHAS Wrapper**: `bridge/llm_wrappers/jules_wrapper.py`

---

**Status**: API is actively evolving. Check official docs for latest features.
