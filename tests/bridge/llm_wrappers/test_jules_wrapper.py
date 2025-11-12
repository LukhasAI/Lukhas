
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

@patch('bridge.llm_wrappers.jules_wrapper.os.getenv', return_value="test_api_key")
@patch('aiohttp.ClientSession')
def test_jules_client_initialization(MockClientSession, mock_os_getenv):
    """Tests that the JulesClient initializes correctly."""
    from bridge.llm_wrappers.jules_wrapper import JulesClient
    # Act
    client = JulesClient()

    # Assert
    assert client.config.api_key == "test_api_key"

@pytest.mark.asyncio
@patch('bridge.llm_wrappers.jules_wrapper.os.getenv', return_value="test_api_key")
async def test_create_session_success(mock_os_getenv):
    """Tests a successful session creation."""
    from bridge.llm_wrappers.jules_wrapper import JulesClient, JulesSource
    # Arrange
    async with JulesClient() as client:
        # Mock the _request method to avoid actual HTTP calls
        client._request = AsyncMock(return_value={"name": "sessions/123"})

        # Mock the list_sources method to return a mock source
        mock_source = JulesSource(name="sources/123", repository_url="https://github.com/test/repo")
        client.list_sources = AsyncMock(return_value=[mock_source])

        # Act
        session = await client.create_session(
            prompt="test prompt",
            repository_url="https://github.com/test/repo"
        )

        # Assert
        assert session["name"] == "sessions/123"
        client._request.assert_awaited_once()

@pytest.mark.asyncio
@patch('bridge.llm_wrappers.jules_wrapper.os.getenv', return_value="test_api_key")
async def test_list_activities_success(mock_os_getenv):
    """Tests listing activities successfully."""
    from bridge.llm_wrappers.jules_wrapper import JulesClient
    # Arrange
    async with JulesClient() as client:
        client._request = AsyncMock(return_value={"activities": [{"name": "activity/1"}]})

        # Act
        activities = await client.list_activities("sessions/123")

        # Assert
        assert len(activities["activities"]) == 1
        assert activities["activities"][0]["name"] == "activity/1"

@pytest.mark.asyncio
@patch('bridge.llm_wrappers.jules_wrapper.os.getenv', return_value="test_api_key")
async def test_stream_activities(mock_os_getenv):
    """Tests streaming activities."""
    from bridge.llm_wrappers.jules_wrapper import JulesClient
    # Arrange
    now = datetime.now().isoformat()
    mock_activity_1 = {"name": "activity/1", "type": "MESSAGE", "create_time": now, "originator": "AGENT"}
    mock_activity_2 = {"name": "activity/2", "type": "PLAN", "create_time": now, "originator": "AGENT"}

    async with JulesClient() as client:
        # Mock list_activities to return a page of activities, and get_session to terminate the stream
        client.list_activities = AsyncMock(side_effect=[
            {"activities": [mock_activity_1]},
            {"activities": [mock_activity_1, mock_activity_2]},
        ])
        client.get_session = AsyncMock(side_effect=[
            {"state": "ACTIVE"},
            {"state": "COMPLETED"}
        ])

        # Act
        streamed_activities = []
        async for activity in client.stream_activities("sessions/123", poll_interval=0.01):
            streamed_activities.append(activity)

        # Assert
        assert len(streamed_activities) == 2
        assert streamed_activities[0].name == "activity/1"
        assert streamed_activities[1].name == "activity/2"
