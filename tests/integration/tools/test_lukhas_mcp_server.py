# owner: Jules-10
# tier: tier4
# module_uid: mcp_servers.lukhas_mcp_server
# criticality: P2

import pytest
import json
from pathlib import Path
from mcp_servers.lukhas_mcp_server import LUKHASMCPServer


class FakeMCPServer:
    """A test double for the MCP Server to allow for offline unit testing."""

    def __init__(self, name: str):
        self.name = name
        self._list_tools_handler = None
        self._call_tool_handler = None

    def list_tools(self):
        def decorator(func):
            self._list_tools_handler = func
            return func

        return decorator

    def call_tool(self):
        def decorator(func):
            self._call_tool_handler = func
            return func

        return decorator

    async def simulate_call_tool(self, name: str, arguments: dict):
        """Simulates a client calling a tool, invoking the registered handler."""
        if not self._call_tool_handler:
            raise RuntimeError("No call_tool handler registered")
        # In the real MCP, the result is a list of content parts.
        # We simulate that here.
        results = await self._call_tool_handler(name, arguments)
        # The test will get the text content and parse it.
        return [part.text for part in results]


# Mock the 'types' class that is expected by the server code
class MockTypes:
    class Tool:
        def __init__(self, name, description, inputSchema):
            pass

    class TextContent:
        def __init__(self, type, text):
            self.type = type
            self.text = text


@pytest.fixture
def mock_mcp_types(monkeypatch):
    """Fixture to mock the mcp.types module."""
    monkeypatch.setattr("mcp_servers.lukhas_mcp_server.types", MockTypes)


@pytest.fixture
def mcp_server(tmp_path: Path, mock_mcp_types) -> LUKHASMCPServer:
    """Provides an instance of LUKHASMCPServer with a fake client factory."""
    workspace_root = tmp_path / "LUKHAS_WORKSPACE"
    workspace_root.mkdir()

    def fake_client_factory():
        return FakeMCPServer("lukhas-mcp-fake")

    server = LUKHASMCPServer(str(workspace_root), client_factory=fake_client_factory)
    # Manually register the tools, as this would happen on server start
    server._register_tools()
    return server


@pytest.mark.tier4
@pytest.mark.integration
class TestLUKHASMCPServerWithFakeClient:
    """Test suite for LUKHAS MCP Server functionality using a fake client."""

    @pytest.mark.asyncio
    async def test_get_patterns_tool(self, mcp_server: LUKHASMCPServer):
        """Tests the 'get_lukhas_patterns' tool via the fake server."""
        # Arrange
        tool_name = "get_lukhas_patterns"
        args = {"category": "naming", "examples": True}

        # Act
        results = await mcp_server.server.simulate_call_tool(tool_name, args)
        result_json = json.loads(results[0])

        # Assert
        assert result_json["category"] == "naming"
        assert len(result_json["patterns"]) > 0
        assert "example" in result_json["patterns"][0]

    @pytest.mark.asyncio
    async def test_explain_concept_tool(self, mcp_server: LUKHASMCPServer):
        """Tests the 'explain_lukhas_concept' tool."""
        # Arrange
        tool_name = "explain_lukhas_concept"
        args = {"concept": "memory_fold"}

        # Act
        results = await mcp_server.server.simulate_call_tool(tool_name, args)
        explanation = results[0]

        # Assert
        assert "memory_fold" in explanation.lower()
        assert "consciousness storage mechanism" in explanation
        assert "🎭" in explanation

    @pytest.mark.asyncio
    async def test_suggest_naming_tool(self, mcp_server: LUKHASMCPServer):
        """Tests the 'suggest_lukhas_naming' tool."""
        # Arrange
        tool_name = "suggest_lukhas_naming"
        args = {"purpose": "activate awareness", "element_type": "function", "domain": "consciousness"}

        # Act
        results = await mcp_server.server.simulate_call_tool(tool_name, args)
        result_json = json.loads(results[0])

        # Assert
        assert "suggestions" in result_json
        assert len(result_json["suggestions"]) > 0
        assert any("activate_awareness" in s for s in result_json["suggestions"])

    @pytest.mark.asyncio
    async def test_generate_trinity_docs_tool(self, mcp_server: LUKHASMCPServer):
        """Tests the 'generate_trinity_documentation' tool."""
        # Arrange
        tool_name = "generate_trinity_documentation"
        args = {"element_type": "class", "element_name": "ConsciousnessEngine", "context": "Manages core awareness"}

        # Act
        results = await mcp_server.server.simulate_call_tool(tool_name, args)
        docstring = results[0]

        # Assert
        assert "🎭" in docstring
        assert "🌈" in docstring
        assert "🎓" in docstring
        assert "ConsciousnessEngine" in docstring

    @pytest.mark.asyncio
    async def test_review_code_tool_compliant(self, mcp_server: LUKHASMCPServer):
        """Tests the 'lukhas_code_review' tool with compliant code."""
        # Arrange
        tool_name = "lukhas_code_review"
        compliant_code = '''
"""
🎭 Poetic. 🌈 Human. 🎓 Technical.
"""
def my_conscious_function(): pass
'''
        args = {"code": compliant_code}

        # Act
        results = await mcp_server.server.simulate_call_tool(tool_name, args)
        result_json = json.loads(results[0])

        # Assert
        assert result_json["compliance_score"] > 80

    @pytest.mark.asyncio
    async def test_review_code_tool_non_compliant(self, mcp_server: LUKHASMCPServer):
        """Tests the 'lukhas_code_review' tool with non-compliant code."""
        # Arrange
        tool_name = "lukhas_code_review"
        non_compliant_code = "def my_function(): print('hello')"
        args = {"code": non_compliant_code}

        # Act
        results = await mcp_server.server.simulate_call_tool(tool_name, args)
        result_json = json.loads(results[0])

        # Assert
        assert result_json["compliance_score"] < 80
        assert "Missing Trinity Framework documentation" in result_json["issues"][0]
