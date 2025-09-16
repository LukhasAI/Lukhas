import pytest

pytest.importorskip("mcp")
from unittest.mock import MagicMock, patch

from ai_orchestration.lukhas_mcp_server import LUKHASConsciousnessMCP


@pytest.fixture
def mcp_server():
    """Fixture for LUKHASConsciousnessMCP server."""
    with patch("ai_orchestration.lukhas_mcp_server.Server"):
        server = LUKHASConsciousnessMCP()
        server.operational_support = MagicMock()
        server.metrics_history = []
        return server


@pytest.mark.mcp_operational
@pytest.mark.asyncio
async def test_analyze_mcp_performance_tool(mcp_server):
    # Mock the analysis result
    mcp_server.operational_support.analyze_operational_patterns.return_value.findings = ["High CPU usage detected."]

    arguments = {}
    result = await mcp_server._analyze_mcp_performance(arguments)

    assert len(result) == 1
    assert "High CPU usage detected" in result[0].text


@pytest.mark.mcp_operational
@pytest.mark.asyncio
async def test_trigger_mcp_support_workflow_tool(mcp_server):
    # Mock the workflow result
    mcp_server.operational_support.automate_support_workflows.return_value.success = True
    mcp_server.operational_support.automate_support_workflows.return_value.message = "Workflow triggered."
    mcp_server.operational_support.automate_support_workflows.return_value.incident_id = "INC-001"

    arguments = {"incident_id": "INC-001", "description": "Test incident"}
    result = await mcp_server._trigger_mcp_support_workflow(arguments)

    assert len(result) == 1
    assert "Workflow Result for Incident INC-001" in result[0].text
    assert "Success: True" in result[0].text
    assert "Message: Workflow triggered" in result[0].text
