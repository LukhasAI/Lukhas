
import asyncio
import os
import sys
import aiohttp
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Mock missing modules before import
sys.modules['governance'] = MagicMock()
sys.modules['governance.guardian_system'] = MagicMock()

from ai_orchestration.lukhas_ai_orchestrator import LUKHASAIOrchestrator

@pytest.fixture
def orchestrator():
    # Mock os.getenv to avoid needing real API keys
    with patch('os.getenv', return_value='fake-key'):
        return LUKHASAIOrchestrator(workspace_root=".")

@pytest.mark.asyncio
@patch('ai_orchestration.lukhas_ai_orchestrator.aiohttp.ClientSession')
async def test_network_timeout(MockClientSession, orchestrator):
    """
    Simulates a network timeout and verifies the system handles it gracefully.
    """
    mock_session_cm = AsyncMock()
    mock_session = MagicMock()
    mock_session_cm.__aenter__.return_value = mock_session
    MockClientSession.return_value = mock_session_cm

    mock_post_cm = AsyncMock()
    mock_post_cm.__aenter__.side_effect = asyncio.TimeoutError("Simulated network timeout")
    mock_session.post.return_value = mock_post_cm

    with pytest.raises(asyncio.TimeoutError):
        await orchestrator._call_ollama("test prompt", {})

    mock_session.post.assert_called_once()

@pytest.mark.asyncio
@patch('ai_orchestration.lukhas_ai_orchestrator.aiohttp.ClientSession')
async def test_network_partition(MockClientSession, orchestrator):
    """
    Simulates a network partition and verifies the system handles it gracefully.
    """
    mock_session_cm = AsyncMock()
    mock_session = MagicMock()
    mock_session_cm.__aenter__.return_value = mock_session
    MockClientSession.return_value = mock_session_cm

    mock_post_cm = AsyncMock()
    os_error = OSError(111, "Connection refused")
    mock_post_cm.__aenter__.side_effect = aiohttp.ClientConnectorError(
        MagicMock(),
        os_error
    )
    mock_session.post.return_value = mock_post_cm

    with pytest.raises(aiohttp.ClientConnectorError):
        await orchestrator._call_ollama("test prompt", {})

    mock_session.post.assert_called_once()
