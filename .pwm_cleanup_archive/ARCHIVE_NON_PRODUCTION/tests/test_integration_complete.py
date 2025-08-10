#!/usr/bin/env python3
"""
Comprehensive integration tests for all orchestration and plugin systems.
Tests the complete integration of Claude and Codex implementations.

ΛTAG: test_integration_complete
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from core.plugin_registry import Plugin, PluginType
from core.plugin_registry import PluginRegistry as CorePluginRegistry
from orchestration.agent_orchestrator import AgentOrchestrator
from orchestration.agents.base import OrchestrationAgent
from orchestration.agents.registry import AgentRegistry
from orchestration.agents.types import AgentCapability, AgentResponse
from orchestration.agents.types import AgentContext as CodexContext
from orchestration.interfaces.agent_interface import (
    AgentContext,
    AgentInterface,
    AgentMessage,
)
from orchestration.interfaces.orchestration_protocol import (
    OrchestrationProtocol,
    Priority,
)
from orchestration.interfaces.plugin_registry import (
    PluginInterface,
    PluginMetadata,
    PluginRegistry,
)


class TestOrchestrationIntegration:
    """Test our orchestration implementation."""

    @pytest.mark.asyncio
    async def test_agent_interface_implementation(self):
        """Test implementing the AgentInterface."""

        class TestAgent(AgentInterface):
            async def initialize(self, context: AgentContext) -> bool:
                return True

            async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": "processed", "task_id": task.get("id")}

            async def handle_message(self, message: AgentMessage) -> AgentMessage:
                return AgentMessage(
                    sender_id="test_agent",
                    recipient_id=message.sender_id,
                    content={"echo": message.content},
                )

            async def get_health_status(self) -> Dict[str, Any]:
                return {"status": "healthy", "uptime": 100}

            async def shutdown(self) -> None:
                pass

            def get_agent_id(self) -> str:
                return "test_agent"

            def get_capabilities(self) -> List[str]:
                return ["test", "echo"]

        agent = TestAgent()
        context = AgentContext(
            orchestrator_id="test_orchestrator", session_id="test_session"
        )

        assert await agent.initialize(context)
        result = await agent.process_task({"id": "123", "action": "test"})
        assert result["task_id"] == "123"

        msg = AgentMessage(
            sender_id="user", recipient_id="test_agent", content={"msg": "hello"}
        )
        response = await agent.handle_message(msg)
        assert response.content["echo"]["msg"] == "hello"

        health = await agent.get_health_status()
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_plugin_registry_integration(self):
        """Test our plugin registry implementation."""

        class TestPlugin(PluginInterface):
            def __init__(self, metadata=None):
                self.metadata = metadata or {}

            async def initialize(self, config: Dict[str, Any]) -> bool:
                return True

            async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
                return {"processed": data, "plugin": "test"}

            async def shutdown(self) -> None:
                pass

            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="test_plugin",
                    version="1.0.0",
                    description="Test plugin",
                    capabilities=["test"],
                )

        registry = PluginRegistry()

        # Use plugin factory to create a plugin instance dynamically
        async def test_plugin_factory(config=None):
            return TestPlugin(config)

        # Load plugin using the factory
        registry._plugin_factories["test_plugin"] = test_plugin_factory
        success = await registry.load_plugin("test_plugin", {})
        assert success

        # Get plugin
        plugin = registry.get_plugin("test_plugin")
        assert plugin is not None
        assert plugin.get_metadata().name == "test_plugin"

        # Process with plugin via broadcast
        result = await registry.broadcast_signal(
            {"plugin": "test_plugin", "data": "test"}
        )
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_orchestration_protocol(self):
        """Test the orchestration protocol."""
        from orchestration.interfaces.orchestration_protocol import (
            MessageType,
            OrchestrationMessage,
        )

        protocol = OrchestrationProtocol(node_id="test_node")

        # Create and send a message
        msg = OrchestrationMessage(
            message_type=MessageType.DATA,
            sender_id="agent1",
            recipient_id="agent2",
            payload={"action": "process"},
            priority=Priority.HIGH,
        )

        assert msg.sender_id == "agent1"
        assert msg.priority == Priority.HIGH

        # Test broadcast
        msg_id = await protocol.broadcast(
            MessageType.STATUS, {"status": "active"}, Priority.NORMAL
        )
        assert msg_id is not None

        # Test serialization
        serialized = msg.to_json()
        deserialized = OrchestrationMessage.from_json(serialized)

        assert deserialized.sender_id == msg.sender_id
        assert deserialized.payload == msg.payload

    @pytest.mark.asyncio
    async def test_agent_orchestrator(self):
        """Test the agent orchestrator."""
        orchestrator = AgentOrchestrator()

        class WorkerAgent(AgentInterface):
            def __init__(self, agent_id: str):
                self._id = agent_id

            async def initialize(self, context: AgentContext) -> bool:
                return True

            async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": f"processed by {self._id}"}

            async def handle_message(self, message: AgentMessage) -> AgentMessage:
                return None

            async def get_health_status(self) -> Dict[str, Any]:
                return {"status": "healthy"}

            async def shutdown(self) -> None:
                pass

            def get_agent_id(self) -> str:
                return self._id

            def get_capabilities(self) -> List[str]:
                return ["process"]

        # Register agents
        agent1 = WorkerAgent("worker1")
        agent2 = WorkerAgent("worker2")

        await orchestrator.register_agent(agent1)
        await orchestrator.register_agent(agent2)

        # Distribute task
        task = {"id": "task1", "type": "process"}
        results = await orchestrator.distribute_task(task, ["process"])

        assert len(results) == 2
        assert any("worker1" in str(r) for r in results)
        assert any("worker2" in str(r) for r in results)


class TestCodexIntegration:
    """Test Codex's agent implementation."""

    def test_orchestration_agent_implementation(self):
        """Test implementing Codex's OrchestrationAgent."""

        class TestCodexAgent(OrchestrationAgent):
            def get_agent_id(self) -> str:
                return "test_codex"

            def get_capabilities(self):
                return [AgentCapability.ORCHESTRATION]

            def process(self, context: CodexContext) -> AgentResponse:
                return AgentResponse(
                    success=True,
                    result={"processed": context.task_id},
                    metadata={"agent": "test_codex"},
                )

            def validate_context(self, context: CodexContext) -> bool:
                return context.task_id is not None

        agent = TestCodexAgent()
        context = CodexContext(task_id="test123", symbolic_state={"mode": "test"})

        assert agent.validate_context(context)
        response = agent.process(context)
        assert response.success
        assert response.result["processed"] == "test123"

    def test_agent_registry(self):
        """Test Codex's agent registry."""
        registry = AgentRegistry()

        class SymbolicAgent(OrchestrationAgent):
            def get_agent_id(self) -> str:
                return "symbolic"

            def get_capabilities(self):
                return [AgentCapability.SYMBOLIC_REASONING]

            def process(self, context: CodexContext) -> AgentResponse:
                return AgentResponse(success=True, result=None, metadata={})

            def validate_context(self, context: CodexContext) -> bool:
                return True

        agent = SymbolicAgent()
        registry.register(agent)

        # Lookup by ID
        retrieved = registry.get_agent("symbolic")
        assert retrieved is agent

        # Find by capability
        agents = registry.find_agents_by_capability(AgentCapability.SYMBOLIC_REASONING)
        assert agent in agents


class TestCorePluginIntegration:
    """Test core plugin system from Codex."""

    def test_core_plugin_registry(self):
        """Test the core plugin registry."""
        registry = CorePluginRegistry()

        class SymbolicPlugin(Plugin):
            def get_plugin_type(self) -> PluginType:
                return PluginType.SYMBOLIC_PROCESSOR

            def get_plugin_name(self) -> str:
                return "symbolic_test"

            def get_version(self) -> str:
                return "1.0.0"

        plugin = SymbolicPlugin()
        registry.register_plugin(plugin)

        # Retrieve plugin
        retrieved = registry.get_plugin(PluginType.SYMBOLIC_PROCESSOR, "symbolic_test")
        assert retrieved is plugin

        # List plugins
        plugins = registry.list_plugins(PluginType.SYMBOLIC_PROCESSOR)
        assert plugin in plugins


class TestCombinedIntegration:
    """Test how both systems work together."""

    @pytest.mark.asyncio
    async def test_unified_architecture(self):
        """Test that both architectures can coexist."""

        # Our comprehensive interface
        our_registry = PluginRegistry()

        # Codex's simpler registry
        codex_registry = AgentRegistry()

        # Core plugin system
        core_plugins = CorePluginRegistry()

        # All can operate independently
        assert our_registry is not None
        assert codex_registry is not None
        assert core_plugins is not None

        # Test creating an adapter
        class UnifiedAgent(AgentInterface, OrchestrationAgent):
            """Agent that implements both interfaces."""

            # Our interface methods
            async def initialize(self, context: AgentContext) -> bool:
                return True

            async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
                # Adapt to Codex context
                codex_context = CodexContext(
                    task_id=task.get("id", "unknown"), symbolic_state=task
                )
                response = self.process(codex_context)
                return {"success": response.success, "result": response.result}

            async def handle_message(self, message: AgentMessage) -> AgentMessage:
                return None

            async def get_health_status(self) -> Dict[str, Any]:
                return {"status": "healthy"}

            async def shutdown(self) -> None:
                pass

            # Codex interface methods
            def get_agent_id(self) -> str:
                return "unified"

            def get_capabilities(self):
                return [AgentCapability.ORCHESTRATION]

            def process(self, context: CodexContext) -> AgentResponse:
                return AgentResponse(
                    success=True, result={"unified": True}, metadata={}
                )

            def validate_context(self, context: CodexContext) -> bool:
                return True

        agent = UnifiedAgent()

        # Can be used with our system
        result = await agent.process_task({"id": "test"})
        assert result["success"]

        # Can be used with Codex system
        codex_registry.register(agent)
        assert codex_registry.get_agent("unified") is agent


def run_integration_tests():
    """Run all integration tests."""
    print("Running comprehensive integration tests...")
    print("=" * 60)

    # Test our orchestration
    print("\n1. Testing our orchestration implementation...")
    asyncio.run(TestOrchestrationIntegration().test_agent_interface_implementation())
    asyncio.run(TestOrchestrationIntegration().test_plugin_registry_integration())
    asyncio.run(TestOrchestrationIntegration().test_orchestration_protocol())
    asyncio.run(TestOrchestrationIntegration().test_agent_orchestrator())
    print("â Our orchestration tests passed")

    # Test Codex integration
    print("\n2. Testing Codex agent implementation...")
    TestCodexIntegration().test_orchestration_agent_implementation()
    TestCodexIntegration().test_agent_registry()
    print("â Codex integration tests passed")

    # Test core plugins
    print("\n3. Testing core plugin system...")
    TestCorePluginIntegration().test_core_plugin_registry()
    print("â Core plugin tests passed")

    # Test combined
    print("\n4. Testing unified architecture...")
    asyncio.run(TestCombinedIntegration().test_unified_architecture())
    print("â Unified architecture tests passed")

    print("\n" + "=" * 60)
    print("â All integration tests passed successfully!")
    print("\nSystems integrated:")
    print("- Our comprehensive orchestration interfaces")
    print("- Codex's concrete agent implementations")
    print("- Core plugin registry with entry points")
    print("- Unified adapters for cross-compatibility")


if __name__ == "__main__":
    run_integration_tests()
