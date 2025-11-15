
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lukhas.orchestrator.health import (
    check_database_connection,
    check_external_apis,
    check_matriz_nodes,
    check_memory_system,
    get_health_status,
)

pytestmark = pytest.mark.asyncio

@patch("lukhas.orchestrator.health.ExternalAPIManager")
@patch("lukhas.orchestrator.health.MatrizManager")
@patch("lukhas.orchestrator.health.MemoryManager")
@patch("lukhas.orchestrator.health.DatabaseManager")
async def test_get_health_status_all_ok(
    mock_db_manager, mock_memory_manager, mock_matriz_manager, mock_external_api_manager
):
    """
    Tests that the health check returns 'ok' when all components are healthy.
    """
    # Mocks for healthy components
    db_instance_mock = mock_db_manager.return_value
    db_instance_mock.connect = AsyncMock()
    db_instance_mock.ping = AsyncMock()
    db_instance_mock.close = AsyncMock()

    mock_memory_manager.return_value.check_status = AsyncMock()

    healthy_node = MagicMock()
    healthy_node.is_healthy.return_value = True
    mock_matriz_manager.return_value.get_nodes = AsyncMock(return_value=[healthy_node])

    mock_external_api_manager.return_value.check_apis = AsyncMock()

    health_status = await get_health_status()

    assert health_status["status"] == "ok"
    assert health_status["components"]["database"]["status"] == "ok"
    assert health_status["components"]["memory_system"]["status"] == "ok"
    assert health_status["components"]["matriz_nodes"]["status"] == "ok"
    assert health_status["components"]["external_apis"]["status"] == "ok"

@patch("lukhas.orchestrator.health.DatabaseManager")
async def test_check_database_connection_error(mock_db_manager):
    """
    Tests that the database check returns 'error' when the connection fails.
    """
    db_instance_mock = mock_db_manager.return_value
    db_instance_mock.connect = AsyncMock()
    db_instance_mock.ping = AsyncMock(side_effect=Exception("Connection timed out"))

    status = await check_database_connection()

    assert status["status"] == "error"
    assert "Connection timed out" in status["details"]

@patch("lukhas.orchestrator.health.MemoryManager")
async def test_check_memory_system_error(mock_memory_manager):
    """
    Tests that the memory system check returns 'error' when it fails.
    """
    mock_memory_manager.return_value.check_status = AsyncMock(side_effect=Exception("Cache unavailable"))

    status = await check_memory_system()

    assert status["status"] == "error"
    assert "Cache unavailable" in status["details"]

@patch("lukhas.orchestrator.health.MatrizManager")
async def test_check_matriz_nodes_error(mock_matriz_manager):
    """
    Tests that the MATRIZ nodes check returns 'error' when a node is unhealthy.
    """
    unhealthy_node = MagicMock()
    unhealthy_node.name = "unhealthy_node"
    unhealthy_node.is_healthy.return_value = False
    mock_matriz_manager.return_value.get_nodes = AsyncMock(return_value=[unhealthy_node])

    status = await check_matriz_nodes()

    assert status["status"] == "error"
    assert "unhealthy_node" in status["details"]

@patch("lukhas.orchestrator.health.ExternalAPIManager")
async def test_check_external_apis_error(mock_external_api_manager):
    """
    Tests that the external APIs check returns 'error' when an API is down.
    """
    mock_external_api_manager.return_value.check_apis = AsyncMock(side_effect=Exception("API timeout"))

    status = await check_external_apis()

    assert status["status"] == "error"
    assert "API timeout" in status["details"]

@patch("lukhas.orchestrator.health.ExternalAPIManager")
@patch("lukhas.orchestrator.health.MatrizManager")
@patch("lukhas.orchestrator.health.MemoryManager")
@patch("lukhas.orchestrator.health.DatabaseManager")
async def test_get_health_status_multiple_errors(
    mock_db_manager, mock_memory_manager, mock_matriz_manager, mock_external_api_manager
):
    """
    Tests that the health check returns 'error' when multiple components are unhealthy.
    """
    # Mocks for unhealthy components
    db_instance_mock = mock_db_manager.return_value
    db_instance_mock.connect = AsyncMock(side_effect=Exception("Connection timed out"))

    mock_memory_manager.return_value.check_status = AsyncMock()  # Healthy

    mock_matriz_manager.return_value.get_nodes = AsyncMock(side_effect=Exception("Manager failed"))

    mock_external_api_manager.return_value.check_apis = AsyncMock()  # Healthy

    health_status = await get_health_status()

    assert health_status["status"] == "error"
    assert health_status["components"]["database"]["status"] == "error"
    assert health_status["components"]["memory_system"]["status"] == "ok"
    assert health_status["components"]["matriz_nodes"]["status"] == "error"
    assert health_status["components"]["external_apis"]["status"] == "ok"
