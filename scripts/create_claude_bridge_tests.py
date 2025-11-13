#!/usr/bin/env python3
"""
Create Jules sessions for Claude API bridge tests

Creates 2 critical test files via Jules API.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def create_test_sessions():
    """Create Jules sessions for missing bridge tests"""

    sessions = [
        {
            "title": "Create comprehensive tests for bridge/llm_wrappers/env_loader.py (keychain integration)",
            "prompt": """Create comprehensive pytest tests for bridge/llm_wrappers/env_loader.py.

**File Context:** Secure API key management with macOS Keychain fallback support. Python 3.9+ compatible.

**Key Functions to Test:**

1. `load_lukhas_env()` - Load .env from multiple locations
2. `get_from_keychain(service_name)` - Retrieve from macOS Keychain
3. `get_api_key(service)` - Priority: .env → Keychain → None
4. `get_openai_config()` - Complete OpenAI config dict
5. `get_azure_openai_config()` - Complete Azure config dict

**Critical Test Coverage:**

**Test load_lukhas_env:**
- Load from each priority location (.env, ../.env, ~/.lukhas/.env)
- Handle missing files gracefully
- Parse valid .env format (KEY=value)
- Ignore comments (#) and blank lines
- Handle malformed entries
- Set os.environ correctly

**Test get_from_keychain:**
- Mock subprocess.run for security command
- Test successful retrieval
- Test missing keychain entries (CalledProcessError)
- Test invalid service names
- Test FileNotFoundError (security not found)
- Test Exception handling with debug logging

**Test get_api_key (MOST IMPORTANT):**
- Test priority order: .env → Keychain → None
- Test with valid .env key (should use .env)
- Test with placeholder "sk-ant-REPLACE_WITH_YOUR_KEY" (should skip to keychain)
- Test keychain fallback when .env empty
- Test setting os.environ from keychain
- Test all service mappings: anthropic, openai, azure, gemini, perplexity
- Test keychain_mapping: anthropic → LUKHASAI.ANTHROPIC_API_KEY
- Test returning None when not found anywhere

**Test get_openai_config:**
- Test returns dict with api_key, org_id, project_id
- Test partial configuration

**Test get_azure_openai_config:**
- Test returns dict with api_key, endpoint, org_id, project_id

**Test Patterns Required:**
```python
import pytest
from unittest.mock import patch, mock_open, MagicMock
import os
import subprocess

@pytest.fixture
def mock_env_file(tmp_path):
    '''Create temp .env file for testing'''
    env_file = tmp_path / ".env"
    env_file.write_text("ANTHROPIC_API_KEY=sk-ant-test123")
    return env_file

@pytest.fixture
def clean_environ():
    '''Clean os.environ before tests'''
    original = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original)

def test_get_from_keychain_success(monkeypatch):
    '''Test successful keychain retrieval'''
    mock_run = MagicMock()
    mock_run.stdout.strip.return_value = "sk-ant-keychain-key"
    monkeypatch.setattr(subprocess, 'run', lambda *args, **kwargs: mock_run)
    # Test implementation

def test_get_api_key_priority_env_over_keychain(monkeypatch, tmp_path):
    '''Test .env takes priority over keychain'''
    # Set up .env with valid key
    # Set up mock keychain
    # Assert .env key is used
```

**Edge Cases:**
- Empty .env file
- Whitespace-only values
- Keys with special characters
- Very long keys
- Concurrent access

**Output File:** tests/unit/bridge/llm_wrappers/test_env_loader.py

**Requirements:**
- Use pytest framework
- Mock all subprocess calls
- Mock file I/O appropriately
- Use monkeypatch for os.environ
- Include docstrings
- Test both success and failure paths
- Achieve >90% code coverage

**LUKHAS Conventions:**
- Use LUKHAS terminology
- Follow existing test patterns from tests/unit/bridge/llm_wrappers/test_codex_wrapper.py
"""
        },
        {
            "title": "Create comprehensive tests for bridge/llm_wrappers/anthropic_wrapper.py (Claude API)",
            "prompt": """Create comprehensive pytest tests for bridge/llm_wrappers/anthropic_wrapper.py.

**File Context:** Wrapper for Anthropic Claude API with automatic API key management and LUKHAS terminology enforcement.

**Class to Test:** AnthropicWrapper

**Methods:**
1. `__init__()` - Initialize with API key from env_loader
2. `generate_response(prompt, model, **kwargs)` - Async Claude API call
3. `is_available()` - Check if client is initialized

**Critical Test Coverage:**

**Test __init__:**
- Test with valid API key from env_loader
- Test with None API key (should handle gracefully)
- Test API key logging (first 20 chars only for security)
- Test anthropic.AsyncAnthropic initialization success
- Test handling ImportError when anthropic package not installed
- Verify client is None when import fails

**Test generate_response (MOST IMPORTANT):**
- Test successful response with mocked API
- Test with different models: claude-3-opus-20240229, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022
- Test max_tokens parameter
- Test system guidance injection (quantum-inspired, bio-inspired, LUKHAS AI)
- Test normalize_output integration
- Test handling anthropic.APIError
- Test handling RateLimitError
- Test handling APITimeoutError
- Test handling empty responses
- Test response tuple format (text: str, model: str)
- Test error message formatting

**Test is_available:**
- Test returns True when async_client is initialized
- Test returns False when async_client is None
- Test after successful __init__
- Test after failed __init__ (no API key)

**Test Patterns Required:**
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

@pytest.fixture
def mock_env_loader():
    '''Mock env_loader.get_api_key'''
    with patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key') as mock:
        mock.return_value = 'sk-ant-test123'
        yield mock

@pytest.fixture
def mock_anthropic():
    '''Mock anthropic.AsyncAnthropic'''
    with patch('bridge.llm_wrappers.anthropic_wrapper.anthropic') as mock:
        mock_client = AsyncMock()
        mock.AsyncAnthropic.return_value = mock_client
        yield mock

@pytest.mark.asyncio
async def test_generate_response_success(mock_env_loader, mock_anthropic):
    '''Test successful Claude API response'''
    # Mock API response
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Test response")]
    mock_anthropic.AsyncAnthropic.return_value.messages.create.return_value = mock_response

    wrapper = AnthropicWrapper()
    text, model = await wrapper.generate_response("Test prompt")

    assert text == "Test response"
    assert model == "claude-3-sonnet-20240229"  # or whatever default

@pytest.mark.asyncio
async def test_generate_response_api_error(mock_env_loader, mock_anthropic):
    '''Test handling API errors'''
    # Set up mock to raise APIError
    # Assert error is handled gracefully
    # Assert returns error message tuple
```

**Integration with env_loader:**
- Mock get_api_key() for all tests
- Test when get_api_key returns None
- Test when get_api_key returns valid key

**Integration with branding.terminology:**
- Mock normalize_output() for consistent testing
- Test that normalize_output is called on responses

**Edge Cases:**
- Very long prompts
- Empty prompts
- Prompts with special characters
- Response with no content
- Malformed API responses
- Network timeouts
- Rate limiting

**Output File:** tests/unit/bridge/llm_wrappers/test_anthropic_wrapper.py

**Requirements:**
- Use pytest framework with pytest-asyncio
- Mock all external dependencies (anthropic, env_loader, normalize_output)
- Use AsyncMock for async methods
- Include comprehensive docstrings
- Test both success and failure paths
- Achieve >90% code coverage
- Follow patterns from existing tests

**LUKHAS Conventions:**
- Validate LUKHAS terminology in system prompts
- Use quantum-inspired and bio-inspired terminology
- Reference LUKHAS AI (not Lukhas AGI)
- Follow existing test structure from tests/unit/bridge/llm_wrappers/test_codex_wrapper.py
"""
        }
    ]

    print("\n🧪 Creating Jules Sessions for Claude API Bridge Tests")
    print("=" * 70)
    print(f"\nSessions to create: {len(sessions)}\n")

    for i, s in enumerate(sessions, 1):
        print(f"{i}. {s['title'][:65]}...")

    print("\n" + "=" * 70)

    created = []

    async with JulesClient() as jules:
        for i, session_config in enumerate(sessions, 1):
            print(f"\nCreating session {i}/{len(sessions)}...")
            print(f"  {session_config['title'][:60]}...")

            try:
                session = await jules.create_session(
                    prompt=session_config['prompt'],
                    source_id="sources/github/LukhasAI/Lukhas",
                    automation_mode="AUTO_CREATE_PR"
                )

                session_id = session['name'].split('/')[-1]
                print(f"  ✅ Created: {session_id}")
                print(f"     URL: https://jules.google.com/session/{session_id}")
                created.append(session)

            except Exception as e:
                print(f"  ❌ Failed: {e}")

            await asyncio.sleep(1)

    print("\n" + "=" * 70)
    print(f"✅ Created {len(created)}/{len(sessions)} sessions")
    print("=" * 70)

    if created:
        print("\n🔗 Monitor at:")
        for s in created:
            sid = s['name'].split('/')[-1]
            print(f"   https://jules.google.com/session/{sid}")

    print("\nNext steps:")
    print("  1. Jules will generate tests automatically")
    print("  2. PRs will be created when ready")
    print("  3. Review and merge PRs")
    print("  4. Run: pytest tests/unit/bridge/llm_wrappers/ -v")


if __name__ == "__main__":
    try:
        asyncio.run(create_test_sessions())
    except KeyboardInterrupt:
        print("\n⏸️  Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
