# Jules API Integration for LUKHAS AI

## Overview

Google Jules is an AI-powered coding agent that can understand codebases, create implementation plans, and execute changes autonomously. This integration allows LUKHAS agents to delegate complex coding tasks to Jules for execution.

**API Status**: Alpha (experimental)
**Documentation**: https://developers.google.com/jules/api

## Architecture Integration

```
LUKHAS Orchestration Layer
    ↓
Jules API Wrapper (bridge/llm_wrappers/jules_wrapper.py)
    ↓
Google Jules API (jules.googleapis.com)
    ↓
Connected GitHub Repositories
```

## Setup

### 1. Get Jules API Key

1. Visit [Jules Web App](https://jules.ai) and sign in
2. Navigate to **Settings** page
3. Generate an API key (maximum 3 keys per account)
4. **Keep your API key secure** - never commit it to version control

### 2. Configure Environment

Add to `.env` or export as environment variable:

```bash
# Jules API Configuration
JULES_API_KEY=your-api-key-here
JULES_AUTO_APPROVE_PLANS=false  # Set to true for automatic plan approval
```

### 3. Connect Repositories

Before using the API, connect your repositories through the Jules web app:
1. Go to Jules app
2. Navigate to **Sources** section
3. Connect your GitHub repositories
4. Grant necessary permissions

## Usage

### Basic Usage

```python
from bridge.llm_wrappers.jules_wrapper import JulesClient

async def run_coding_task():
    async with JulesClient() as jules:
        # List connected repositories
        sources = await jules.list_sources()
        print(f"Connected repos: {[s.display_name for s in sources]}")

        # Create a coding session
        session = await jules.create_session(
            prompt="Write comprehensive tests for core orchestration module",
            repository_url="https://github.com/LukhasAI/Lukhas",
            automation_mode="AUTO_CREATE_PR"  # Auto-create PR when done
        )

        print(f"Session created: {session['name']}")

        # Monitor progress
        async for activity in jules.stream_activities(session['name']):
            print(f"[{activity.type}] {activity.message}")
```

### Convenience Functions

```python
from bridge.llm_wrappers.jules_wrapper import (
    create_jules_session,
    monitor_jules_session
)

# Quick session creation
session = await create_jules_session(
    prompt="Fix all E402 import ordering violations",
    repository_url="https://github.com/LukhasAI/Lukhas",
    auto_create_pr=True
)

# Monitor until completion
activities = await monitor_jules_session(
    session_id=session['name'],
    timeout=3600  # 1 hour timeout
)
```

### Integration with LUKHAS Orchestration

```python
from labs.core.orchestration.agent_orchestrator import AgentOrchestrator
from bridge.llm_wrappers.jules_wrapper import JulesClient

async def delegate_to_jules(task: dict) -> dict:
    """
    Delegate a coding task to Jules agent.

    Args:
        task: Task specification with prompt and repository

    Returns:
        Task result with PR link and changes
    """
    async with JulesClient() as jules:
        # Create session
        session = await jules.create_session(
            prompt=task['prompt'],
            repository_url=task['repository_url'],
            automation_mode="AUTO_CREATE_PR"
        )

        # Collect activities
        pr_link = None
        changes = []

        async for activity in jules.stream_activities(
            session['name'],
            timeout=task.get('timeout', 1800)  # 30 min default
        ):
            if activity.type == "PULL_REQUEST_CREATED":
                pr_link = activity.artifacts.get('pullRequest', {}).get('url')
            elif activity.type == "CODE_CHANGE":
                changes.append(activity.artifacts)

        return {
            'session_id': session['name'],
            'pr_link': pr_link,
            'changes': changes,
            'status': 'completed'
        }
```

## API Reference

### JulesClient

Main client class for interacting with Jules API.

#### Methods

- **`list_sources()`** - List connected repositories
- **`create_session(prompt, source_id|repository_url, ...)`** - Create coding session
- **`approve_plan(session_id)`** - Approve generated plan
- **`send_message(session_id, message)`** - Send message to agent
- **`list_activities(session_id)`** - Get session activities
- **`stream_activities(session_id)`** - Stream activities in real-time

### Configuration

**JulesConfig** parameters:
- `api_key`: Jules API key (required)
- `base_url`: API endpoint (default: https://jules.googleapis.com)
- `timeout`: Request timeout in seconds (default: 300)
- `max_retries`: Maximum retry attempts (default: 3)
- `auto_approve_plans`: Auto-approve generated plans (default: False)

### Activity Types

- **PLAN** - Agent created an implementation plan
- **MESSAGE** - Agent or user message
- **CODE_CHANGE** - Code modification
- **PULL_REQUEST_CREATED** - PR was created
- **PROGRESS_UPDATE** - Task progress update

## Use Cases for LUKHAS

### 1. Test Coverage Improvement

```python
# Delegate test writing to Jules
session = await jules.create_session(
    prompt="""
    Write comprehensive tests for core orchestration module.

    Context: Read TEST_ASSIGNMENT_REPORT.md, find TEST-001,
    write tests for 20 orchestration files, target 75%+ coverage.
    """,
    repository_url="https://github.com/LukhasAI/Lukhas",
    automation_mode="AUTO_CREATE_PR"
)
```

### 2. Code Quality Fixes

```python
# Fix linting violations
session = await jules.create_session(
    prompt="Fix all E402 import ordering violations in the codebase",
    repository_url="https://github.com/LukhasAI/Lukhas",
    automation_mode="AUTO_CREATE_PR"
)
```

### 3. Feature Implementation

```python
# Implement new feature
session = await jules.create_session(
    prompt="""
    Implement Prometheus metrics endpoint for MATRIZ cognitive engine.

    Requirements:
    - Add /metrics endpoint to serve/main.py
    - Track MATRIZ processing latency
    - Track memory usage
    - Track consensus decisions
    """,
    repository_url="https://github.com/LukhasAI/Lukhas",
    require_plan_approval=True  # Review plan before execution
)

# Review and approve plan
activities = await jules.list_activities(session['name'])
plan_activity = next(a for a in activities['activities'] if a['type'] == 'PLAN')
print(f"Plan: {plan_activity['message']}")

# Approve if satisfactory
await jules.approve_plan(session['name'])
```

### 4. Documentation Generation

```python
# Generate API documentation
session = await jules.create_session(
    prompt="""
    Generate comprehensive API documentation for serve/main.py endpoints.

    Include:
    - OpenAPI specification
    - Request/response examples
    - Authentication requirements
    - Error codes and handling
    """,
    repository_url="https://github.com/LukhasAI/Lukhas"
)
```

## Best Practices

### 1. Security

- **Never commit API keys** to version control
- Use environment variables or secure secret management
- Rotate API keys regularly (max 3 keys per account)
- Limit repository access to necessary repos only

### 2. Task Scope

- Keep prompts clear and specific
- Break large tasks into smaller sessions
- Use `require_plan_approval=True` for complex changes
- Set appropriate timeouts for long-running tasks

### 3. Error Handling

```python
async with JulesClient() as jules:
    try:
        session = await jules.create_session(
            prompt=task_prompt,
            repository_url=repo_url
        )
    except ValueError as e:
        logger.error(f"Source not found: {e}")
        # Prompt user to connect repository
    except aiohttp.ClientError as e:
        logger.error(f"API request failed: {e}")
        # Retry with exponential backoff
```

### 4. Monitoring

```python
# Track all activities for debugging
all_activities = []

async for activity in jules.stream_activities(session['name']):
    all_activities.append(activity)

    # Log important events
    if activity.type == "ERROR":
        logger.error(f"Jules error: {activity.message}")
    elif activity.type == "PULL_REQUEST_CREATED":
        logger.info(f"PR created: {activity.artifacts['pullRequest']['url']}")
```

## Limitations

- **Alpha API**: Specifications may change
- **Rate Limits**: Check Jules documentation for current limits
- **Repository Access**: Repos must be connected through Jules app first
- **API Key Limit**: Maximum 3 keys per account
- **Async Only**: Requires async/await syntax

## Troubleshooting

### "No module named 'aiohttp'"

```bash
pip install aiohttp
```

### "No source found for repository"

Connect the repository in Jules web app first:
1. Visit https://jules.ai
2. Go to Sources
3. Connect your GitHub repository

### "API key authentication failed"

- Verify API key is correct
- Check key hasn't expired
- Ensure `JULES_API_KEY` environment variable is set

### Session timeout

Increase timeout for long-running tasks:

```python
async for activity in jules.stream_activities(
    session['name'],
    timeout=7200  # 2 hours
):
    ...
```

## Examples

See `bridge/llm_wrappers/jules_wrapper.py` for complete implementation examples.

## Support

- **Jules Documentation**: https://developers.google.com/jules/api
- **LUKHAS Issues**: https://github.com/LukhasAI/Lukhas/issues
- **API Status**: Alpha (experimental)

## License

This integration follows LUKHAS AI licensing. Jules API usage subject to Google's terms of service.
