
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from aioresponses import aioresponses
from bridge.llm_wrappers.jules_wrapper import (
    JulesClient,
    JulesConfig,
    create_jules_session,
    monitor_jules_session,
)

BASE_URL = "https://jules.googleapis.com"

@pytest.fixture
def mock_aioresponse():
    """Fixture for mocking aiohttp responses."""
    with aioresponses() as m:
        yield m

@pytest.mark.asyncio
async def test_successful_session_creation(mock_aioresponse):
    """Tests the successful creation of a Jules session."""
    mock_aioresponse.post(f"{BASE_URL}/v1alpha/sessions", payload={"name": "sessions/123"})

    async with JulesClient(api_key="test_key") as client:
        session = await client.create_session(prompt="test prompt", source_id="sources/1")
        assert session["name"] == "sessions/123"

@pytest.mark.asyncio
async def test_api_key_handling():
    """Tests the different ways API keys can be provided."""
    # Direct
    client = JulesClient(api_key="direct_key")
    assert client.config.api_key == "direct_key"

    # Environment variable
    with patch('os.getenv', return_value='env_key'):
        client = JulesClient()
        assert client.config.api_key == "env_key"

    # Keychain
    with patch('bridge.llm_wrappers.jules_wrapper.KEYCHAIN_AVAILABLE', True), \
         patch('bridge.llm_wrappers.jules_wrapper.get_jules_api_key', return_value='keychain_key'):
        client = JulesClient()
        assert client.config.api_key == 'keychain_key'

    # No key found
    with patch('os.getenv', return_value=None), \
         patch('bridge.llm_wrappers.jules_wrapper.KEYCHAIN_AVAILABLE', False):
        with pytest.raises(ValueError):
            JulesClient()


@pytest.mark.asyncio
async def test_session_listing_and_retrieval(mock_aioresponse):
    """Tests listing and retrieving sessions."""
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sessions", payload={"sessions": [{"name": "sessions/123"}]})
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sessions/123", payload={"name": "sessions/123", "state": "ACTIVE"})

    async with JulesClient(api_key="test_key") as client:
        sessions = await client.list_sessions()
        assert len(sessions["sessions"]) == 1

        session = await client.get_session("sessions/123")
        assert session["state"] == "ACTIVE"

@pytest.mark.asyncio
async def test_plan_approval_and_messaging(mock_aioresponse):
    """Tests plan approval and sending messages."""
    mock_aioresponse.post(f"{BASE_URL}/v1alpha/sessions/123:approvePlan", status=200, payload={})
    mock_aioresponse.post(f"{BASE_URL}/v1alpha/sessions/123:sendMessage", payload={"name": "activities/456"})

    async with JulesClient(api_key="test_key") as client:
        await client.approve_plan("sessions/123")

        activity = await client.send_message("sessions/123", "test message")
        assert activity["name"] == "activities/456"

@pytest.mark.asyncio
async def test_activity_streaming(mock_aioresponse):
    """Tests the activity streaming functionality."""
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sessions/123/activities", payload={"activities": [{"name": "activities/1", "type": "PLAN", "originator": "AGENT"}]})
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sessions/123", payload={"name": "sessions/123", "state": "COMPLETED"})

    async with JulesClient(api_key="test_key") as client:
        activities = []
        async for activity in client.stream_activities("sessions/123", poll_interval=0.01):
            activities.append(activity)

        assert len(activities) == 1
        assert activities[0].name == "activities/1"

@pytest.mark.asyncio
async def test_source_listing_and_retrieval(mock_aioresponse):
    """Tests listing sources and retrieving a source by URL."""
    sources_payload = {
        "sources": [
            {"name": "sources/1", "repositoryUrl": "http://test.com/repo1"},
            {"name": "sources/2", "repositoryUrl": "http://test.com/repo2"}
        ]
    }
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sources", payload=sources_payload)

    async with JulesClient(api_key="test_key") as client:
        source = await client.get_source_by_url("http://test.com/repo2")
        assert source is not None
        assert source.name == "sources/2"

        non_existent_source = await client.get_source_by_url("http://test.com/nonexistent")
        assert non_existent_source is None


@pytest.mark.asyncio
async def test_api_error_handling_with_retry(mock_aioresponse):
    """Tests the client's handling of API errors with retries."""
    # First two calls fail, third succeeds
    mock_aioresponse.post(f"{BASE_URL}/v1alpha/sessions", status=500)
    mock_aioresponse.post(f"{BASE_URL}/v1alpha/sessions", status=500)
    mock_aioresponse.post(f"{BASE_URL}/v1alpha/sessions", status=200, payload={"name": "sessions/123"})

    config = JulesConfig(api_key="test_key", max_retries=3)

    async with JulesClient(config=config) as client:
        # We need to patch sleep to avoid waiting during tests
        with patch('asyncio.sleep', new_callable=AsyncMock):
             session = await client.create_session(prompt="prompt", source_id="sources/1")
             assert session['name'] == 'sessions/123'
             assert len(mock_aioresponse.requests) == 3


@pytest.mark.asyncio
async def test_create_session_with_repo_url(mock_aioresponse):
    """Test creating a session by providing a repository URL."""
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sources", payload={"sources": [{"name": "sources/1", "repositoryUrl": "http://a.com/b"}]})
    mock_aioresponse.post(f"{BASE_URL}/v1alpha/sessions", payload={"name": "sessions/1"})

    async with JulesClient(api_key="test") as client:
        session = await client.create_session(prompt="p", repository_url="http://a.com/b")
        assert session['name'] == 'sessions/1'

@pytest.mark.asyncio
async def test_create_session_no_source(mock_aioresponse):
    """Test ValueError when no source is found for a repo URL."""
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sources", payload={"sources": []})

    async with JulesClient(api_key="test") as client:
        with pytest.raises(ValueError, match="No source found"):
            await client.create_session(prompt="p", repository_url="http://a.com/b")

@pytest.mark.asyncio
async def test_convenience_functions(mock_aioresponse):
    """Test the convenience functions `create_jules_session` and `monitor_jules_session`."""
    # Mock for create_jules_session
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sources", payload={"sources": [{"name": "sources/1", "repositoryUrl": "http://a.com/b"}]})
    mock_aioresponse.post(f"{BASE_URL}/v1alpha/sessions", payload={"name": "sessions/1"})

    session = await create_jules_session(prompt="p", repository_url="http://a.com/b", api_key="test")
    assert session['name'] == 'sessions/1'

    # Mocks for monitor_jules_session
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sessions/1/activities", payload={"activities": [{"name": "activities/1", "type":"PLAN", "originator":"AGENT"}]})
    mock_aioresponse.get(f"{BASE_URL}/v1alpha/sessions/1", payload={"name": "sessions/1", "state": "COMPLETED"})

    activities = await monitor_jules_session("sessions/1", api_key="test", timeout=0.1)
    assert len(activities) > 0

@pytest.mark.asyncio
async def test_delete_session(mock_aioresponse):
    """Tests the deletion of a session."""
    mock_aioresponse.delete(f"{BASE_URL}/v1alpha/sessions/123", status=200, payload={})

    async with JulesClient(api_key="test_key") as client:
        response = await client.delete_session("sessions/123")
        assert response == {}

@pytest.mark.asyncio
async def test_client_without_context_manager():
    """Test that using the client without a context manager raises a RuntimeError."""
    client = JulesClient(api_key="test")
    with pytest.raises(RuntimeError, match="must be used as async context manager"):
        await client.list_sources()
