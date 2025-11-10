#!/usr/bin/env python3
"""Batch respond to Jules sessions with guidance."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


# Standard LUKHAS import guidance
LUKHAS_IMPORT_GUIDANCE = """
**LUKHAS Import System Guidance**

The project uses a **lane-based architecture** with strict import boundaries:

**Import Rules**:
- `lukhas/` (production) ← can import from `core/`, `matriz/`, `universal_language/`
- `candidate/` (development) ← can import from `core/`, `matriz/` ONLY (NO lukhas imports)
- `serve/` (API routes) ← can import from `lukhas/`, `core/`, `matriz/`, `bridge/`

**Common Import Patterns**:
```python
# Metrics (from candidate lane)
from candidate.monitoring.metrics_collector import get_metrics_collector

# OR for tests, mock it:
from unittest.mock import Mock, patch
@patch('serve.openai_routes.get_metrics_collector')
def test_something(mock_metrics):
    ...

# OpenAI service
from bridge.llm_wrappers.openai_modulated_service import OpenAIModulatedService

# Rate limiting
from core.rate_limiter import RateLimiter

# Authentication
from lukhas.api.auth_helpers import get_current_user, require_api_key
```

**For Tests**:
1. Run from project root: `pytest tests/unit/...`
2. Don't create symlinks - use proper imports
3. Mock unavailable modules if needed
4. Use `PYTHONPATH=.` if needed

**Key Files**:
- Metrics: `candidate/monitoring/metrics_collector.py`
- Auth: `lukhas/api/auth_helpers.py`
- Rate limiting: `core/rate_limiter.py`
- OpenAI service: `bridge/llm_wrappers/openai_modulated_service.py`

Continue with your implementation using these proper imports!
"""

SESSIONS_TO_RESPOND = [
    # Security hardening sessions (P0)
    {
        "id": "12640991174544438084",
        "message": f"""
{LUKHAS_IMPORT_GUIDANCE}

**For your specific case** (openai_routes.py security tests):

The `get_metrics_collector` import should be:
```python
from candidate.monitoring.metrics_collector import get_metrics_collector
```

OR in your tests, mock it:
```python
@patch('serve.openai_routes.get_metrics_collector', return_value=Mock())
def test_your_endpoint(mock_metrics):
    ...
```

The import error happens because Jules' environment doesn't have candidate/ in path. Just mock it in your tests and continue!
"""
    },
    {
        "id": "9632975312775752958",
        "message": f"""
{LUKHAS_IMPORT_GUIDANCE}

**For skipped tests implementation**:

The tests are in `tests/unit/api/test_dreams_api_security.py`. Same import issues - just mock the problematic imports:

```python
from unittest.mock import Mock, patch, MagicMock

@patch('serve.routes.get_metrics_collector', return_value=Mock())
@patch('lukhas.api.auth_helpers.get_current_user')
def test_simulate_success_with_auth(mock_user, mock_metrics):
    mock_user.return_value = {{"user_id": "test_123", "tier": "pro"}}
    # Your test implementation
    ...
```

Don't worry about import errors - mock them and focus on implementing the 24 security tests!
"""
    },
    {
        "id": "4881210246989891433",
        "message": f"""
{LUKHAS_IMPORT_GUIDANCE}

**For serve/routes.py security**:

The `AttributeError: module 'serve' has no attribute 'routes'` means the import path is wrong.

Correct imports:
```python
from serve.routes import router  # NOT serve.routes.router
from lukhas.api.auth_helpers import get_current_user, require_api_key
from core.rate_limiter import rate_limit
```

In your tests:
```python
from serve.routes import router
from fastapi.testclient import TestClient

client = TestClient(router)

@patch('serve.routes.get_current_user')
def test_endpoint_with_auth(mock_user):
    mock_user.return_value = {{"user_id": "test", "tier": "pro"}}
    response = client.post("/api/v1/dreams/simulate", ...)
    assert response.status_code == 200
```

Continue with your security tests!
"""
    },
    {
        "id": "8833127221412567236",
        "message": """
**Dream/consciousness isolation looks good!**

I see you've added `user_id` parameters to dream generation and consciousness engine. Perfect!

**For the tests**, make sure you're testing:
1. Success (200) - User can generate own dreams
2. Unauthorized (401) - Missing auth
3. Forbidden (403) - Insufficient permissions
4. Cross-user (403) - Cannot access other user's dreams
5. Rate limiting (429)
6. Validation (422)

Continue with the implementation - you're on the right track! 🎉
"""
    },
    {
        "id": "18029788532764900686",
        "message": """
**Memory user isolation progress looks great!**

You found the correct file: `labs/consciousness/reflection/unified_memory_manager.py`

**Key changes needed**:
1. Add `user_id: str` parameter to all memory methods
2. Filter all queries by user_id
3. Update database schema if needed (add user_id column)

**For tests** (`tests/unit/memory/test_user_isolation.py`):
```python
def test_memory_user_isolation():
    manager = UnifiedMemoryManager()

    # Store memory for user1
    manager.store_memory(user_id="user1", content="secret1")

    # User2 should not see user1's memory
    results = manager.get_memories(user_id="user2")
    assert "secret1" not in str(results)

    # User1 should see their own memory
    results = manager.get_memories(user_id="user1")
    assert "secret1" in str(results)
```

Keep going - you're almost done!
"""
    },
]


async def batch_respond():
    """Send responses to all sessions."""
    async with JulesClient() as jules:
        print(f"Sending responses to {len(SESSIONS_TO_RESPOND)} Jules sessions...\n")
        print("="*70)

        for idx, item in enumerate(SESSIONS_TO_RESPOND, 1):
            session_id = item["id"]
            message = item["message"]

            print(f"\n[{idx}/{len(SESSIONS_TO_RESPOND)}] Session {session_id}")
            print(f"URL: https://jules.google.com/session/{session_id}")

            try:
                result = await jules.send_message(f"sessions/{session_id}", message)
                print(f"  ✅ Message sent successfully!")
            except Exception as e:
                print(f"  ❌ Error: {e}")

        print("\n" + "="*70)
        print(f"✅ Sent responses to {len(SESSIONS_TO_RESPOND)} sessions!")
        print("\nJules will now continue implementing with proper guidance.")


if __name__ == "__main__":
    asyncio.run(batch_respond())
