"""
Tests for Agent Interface
========================

ΛTAG: test, agent, interface
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

import pytest

from orchestration.interfaces.agent_interface import (
    AgentCapability,
    AgentContext,
    AgentInterface,
    AgentMessage,
    AgentMetadata,
    AgentStatus,
    SimpleAgent,
)


class TestAgentMetadata:
    """Test AgentMetadata dataclass"""

    def test_default_creation(self):
        """Test creating metadata with defaults"""
        metadata = AgentMetadata()

        assert metadata.agent_id != ""
        assert metadata.name == ""
        assert metadata.version == "1.0.0"
        assert metadata.author == "LUKHAS Team"
        assert isinstance(metadata.created_at, datetime)
        assert len(metadata.capabilities) == 0
        assert len(metadata.dependencies) == 0

    def test_custom_creation(self):
        """Test creating metadata with custom values"""
        metadata = AgentMetadata(
            name="TestAgent",
            version="2.0.0",
            description="A test agent",
            capabilities={AgentCapability.TASK_PROCESSING, AgentCapability.LEARNING},
        )

        assert metadata.name == "TestAgent"
        assert metadata.version == "2.0.0"
        assert AgentCapability.TASK_PROCESSING in metadata.capabilities
        assert AgentCapability.LEARNING in metadata.capabilities


class TestAgentMessage:
    """Test AgentMessage dataclass"""

    def test_message_creation(self):
        """Test creating agent messages"""
        message = AgentMessage(
            sender_id="agent1",
            recipient_id="agent2",
            message_type="test",
            content={"data": "test"},
            priority=5,
        )

        assert message.sender_id == "agent1"
        assert message.recipient_id == "agent2"
        assert message.message_type == "test"
        assert message.content["data"] == "test"
        assert message.priority == 5
        assert isinstance(message.timestamp, datetime)

    def test_broadcast_message(self):
        """Test creating broadcast message"""
        message = AgentMessage(
            sender_id="agent1",
            recipient_id=None,  # Broadcast
            message_type="announcement",
            content="Hello all agents",
        )

        assert message.recipient_id is None
        assert message.requires_response is False


class TestAgentContext:
    """Test AgentContext dataclass"""

    def test_context_creation(self):
        """Test creating agent context"""
        context = AgentContext(orchestrator_id="orch1", session_id="session1")

        assert context.orchestrator_id == "orch1"
        assert context.session_id == "session1"
        assert context.memory_access is False
        assert isinstance(context.message_queue, asyncio.Queue)


class TestAgentInterface:
    """Test the abstract AgentInterface"""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing"""

        class MockAgent(AgentInterface):
            def __init__(self):
                metadata = AgentMetadata(name="MockAgent", version="1.0.0")
                super().__init__(metadata)
                self.initialized = False
                self.tasks_processed = 0
                self.messages_handled = 0

            async def initialize(self, context: AgentContext) -> bool:
                self.initialized = True
                self.context = context
                self.update_status(AgentStatus.READY)
                return True

            async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
                self.tasks_processed += 1
                return {"status": "completed", "task_id": task.get("task_id")}

            async def handle_message(
                self, message: AgentMessage
            ) -> Optional[AgentMessage]:
                self.messages_handled += 1
                if message.requires_response:
                    return AgentMessage(
                        sender_id=self.metadata.agent_id,
                        recipient_id=message.sender_id,
                        message_type="response",
                        content={"acknowledged": True},
                    )
                return None

            async def get_health_status(self) -> Dict[str, Any]:
                return {
                    "healthy": True,
                    "status": self.status.name,
                    "tasks_processed": self.tasks_processed,
                }

            async def shutdown(self) -> None:
                self.update_status(AgentStatus.TERMINATED)

        return MockAgent()

    def test_agent_creation(self, mock_agent):
        """Test agent creation and initial state"""
        assert mock_agent.metadata.name == "MockAgent"
        assert mock_agent.status == AgentStatus.INITIALIZING
        assert mock_agent.context is None
        assert len(mock_agent._message_handlers) == 0

    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_agent):
        """Test agent initialization"""
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")

        success = await mock_agent.initialize(context)

        assert success is True
        assert mock_agent.initialized is True
        assert mock_agent.context == context
        assert mock_agent.status == AgentStatus.READY

    def test_capability_registration(self, mock_agent):
        """Test capability registration"""
        # Register enum capability
        mock_agent.register_capability(AgentCapability.LEARNING)
        assert AgentCapability.LEARNING in mock_agent.metadata.capabilities

        # Register custom capability
        mock_agent.register_capability("custom_capability")
        assert "capability:custom_capability" in mock_agent.metadata.tags

    def test_has_capability(self, mock_agent):
        """Test capability checking"""
        mock_agent.register_capability(AgentCapability.LEARNING)
        mock_agent.register_capability("custom_capability")

        assert mock_agent.has_capability(AgentCapability.LEARNING)
        assert mock_agent.has_capability("custom_capability")
        assert not mock_agent.has_capability(AgentCapability.QUANTUM_PROCESSING)
        assert not mock_agent.has_capability("unknown_capability")

    def test_message_handler_registration(self, mock_agent):
        """Test message handler registration"""

        def test_handler(message):
            return {"handled": True}

        mock_agent.register_message_handler("test_type", test_handler)

        assert "test_type" in mock_agent._message_handlers
        assert mock_agent._message_handlers["test_type"] == test_handler

    def test_lifecycle_hooks(self, mock_agent):
        """Test lifecycle hook registration"""
        hook_called = False

        def test_hook(agent):
            nonlocal hook_called
            hook_called = True

        mock_agent.add_lifecycle_hook("pre_init", test_hook)

        assert len(mock_agent._lifecycle_hooks["pre_init"]) == 1

        # Test invalid hook phase
        with pytest.raises(ValueError, match="Unknown lifecycle phase"):
            mock_agent.add_lifecycle_hook("invalid_phase", test_hook)

    @pytest.mark.asyncio
    async def test_lifecycle_hook_execution(self, mock_agent):
        """Test lifecycle hook execution"""
        hook_results = []

        async def async_hook(agent):
            hook_results.append("async_hook")

        def sync_hook(agent):
            hook_results.append("sync_hook")

        mock_agent.add_lifecycle_hook("pre_init", async_hook)
        mock_agent.add_lifecycle_hook("pre_init", sync_hook)

        await mock_agent.execute_lifecycle_hooks("pre_init")

        assert "async_hook" in hook_results
        assert "sync_hook" in hook_results

    def test_status_updates(self, mock_agent):
        """Test status update functionality"""
        assert mock_agent.status == AgentStatus.INITIALIZING

        mock_agent.update_status(AgentStatus.READY)
        assert mock_agent.status == AgentStatus.READY

        mock_agent.update_status(AgentStatus.PROCESSING)
        assert mock_agent.status == AgentStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_send_message(self, mock_agent):
        """Test message sending"""
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")
        await mock_agent.initialize(context)

        # Send direct message
        message_id = await mock_agent.send_message(
            "recipient_agent", {"data": "test"}, message_type="test", priority=5
        )

        assert message_id is not None

        # Check message in queue
        message = await context.message_queue.get()
        assert message.sender_id == mock_agent.metadata.agent_id
        assert message.recipient_id == "recipient_agent"
        assert message.content["data"] == "test"
        assert message.priority == 5

    @pytest.mark.asyncio
    async def test_broadcast_message(self, mock_agent):
        """Test broadcast message"""
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")
        await mock_agent.initialize(context)

        # Broadcast message
        message_id = await mock_agent.broadcast(
            {"announcement": "Hello all"}, message_type="announcement"
        )

        assert message_id is not None

        # Check message in queue
        message = await context.message_queue.get()
        assert message.recipient_id is None  # Broadcast
        assert message.content["announcement"] == "Hello all"

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_agent):
        """Test error handling"""
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")
        await mock_agent.initialize(context)

        # Simulate error
        test_error = Exception("Test error")
        await mock_agent.handle_error(test_error, "test_context")

        # Check status changed to error
        assert mock_agent.status == AgentStatus.ERROR

        # Check error message sent
        message = await context.message_queue.get()
        assert message.message_type == "error"
        assert message.priority == 10
        assert "Test error" in message.content["error"]

    def test_metadata_dict(self, mock_agent):
        """Test metadata dictionary conversion"""
        metadata_dict = mock_agent.get_metadata_dict()

        assert metadata_dict["name"] == "MockAgent"
        assert metadata_dict["version"] == "1.0.0"
        assert metadata_dict["agent_id"] == mock_agent.metadata.agent_id
        assert metadata_dict["status"] == mock_agent.status.name


class TestSimpleAgent:
    """Test the SimpleAgent implementation"""

    @pytest.fixture
    def simple_agent(self):
        """Create a SimpleAgent instance"""
        return SimpleAgent("TestSimpleAgent")

    def test_simple_agent_creation(self, simple_agent):
        """Test SimpleAgent creation"""
        assert simple_agent.metadata.name == "TestSimpleAgent"
        assert AgentCapability.TASK_PROCESSING in simple_agent.metadata.capabilities
        assert AgentCapability.INTER_AGENT_COMM in simple_agent.metadata.capabilities

    @pytest.mark.asyncio
    async def test_simple_agent_initialization(self, simple_agent):
        """Test SimpleAgent initialization"""
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")

        success = await simple_agent.initialize(context)

        assert success is True
        assert simple_agent.status == AgentStatus.READY
        assert simple_agent.context == context

    @pytest.mark.asyncio
    async def test_simple_agent_task_processing(self, simple_agent):
        """Test SimpleAgent task processing"""
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")
        await simple_agent.initialize(context)

        task = {
            "task_id": "test_task_123",
            "type": "test_task",
            "parameters": {"param1": "value1"},
        }

        result = await simple_agent.process_task(task)

        assert result["status"] == "completed"
        assert result["task_id"] == "test_task_123"
        assert "Processed test_task task" in result["result"]

    @pytest.mark.asyncio
    async def test_simple_agent_message_handling(self, simple_agent):
        """Test SimpleAgent message handling"""
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")
        await simple_agent.initialize(context)

        # Test message without response required
        message1 = AgentMessage(
            sender_id="sender1", message_type="info", content={"info": "test"}
        )

        response1 = await simple_agent.handle_message(message1)
        assert response1 is None

        # Test message with response required
        message2 = AgentMessage(
            sender_id="sender2",
            message_type="query",
            content={"query": "status"},
            requires_response=True,
        )

        response2 = await simple_agent.handle_message(message2)
        assert response2 is not None
        assert response2.recipient_id == "sender2"
        assert response2.content["acknowledged"] is True

    @pytest.mark.asyncio
    async def test_simple_agent_health_status(self, simple_agent):
        """Test SimpleAgent health status"""
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")
        await simple_agent.initialize(context)

        health = await simple_agent.get_health_status()

        assert health["status"] == "READY"
        assert health["healthy"] is True
        assert health["agent_id"] == simple_agent.metadata.agent_id
        assert "uptime" in health
        assert health["active_tasks"] == 0

    @pytest.mark.asyncio
    async def test_simple_agent_shutdown(self, simple_agent):
        """Test SimpleAgent shutdown"""
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")
        await simple_agent.initialize(context)

        # Add message to queue
        await context.message_queue.put(AgentMessage(sender_id="test"))

        await simple_agent.shutdown()

        assert simple_agent.status == AgentStatus.TERMINATED
        assert context.message_queue.empty()


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agent system"""

    @pytest.mark.asyncio
    async def test_agent_communication(self):
        """Test communication between agents"""
        # Create two agents
        agent1 = SimpleAgent("Agent1")
        agent2 = SimpleAgent("Agent2")

        # Initialize with shared context (simplified)
        context1 = AgentContext(orchestrator_id="test_orch", session_id="test_session")
        context2 = AgentContext(orchestrator_id="test_orch", session_id="test_session")

        await agent1.initialize(context1)
        await agent2.initialize(context2)

        # Agent1 sends message
        await agent1.send_message(
            agent2.metadata.agent_id,
            {"greeting": "Hello Agent2"},
            message_type="greeting",
        )

        # Get message from agent1's queue
        message = await context1.message_queue.get()

        # Agent2 handles message
        response = await agent2.handle_message(message)

        # Verify communication
        assert message.content["greeting"] == "Hello Agent2"
        assert message.sender_id == agent1.metadata.agent_id

    @pytest.mark.asyncio
    async def test_agent_task_error_handling(self):
        """Test agent error handling during task processing"""

        class ErrorAgent(AgentInterface):
            def __init__(self):
                metadata = AgentMetadata(name="ErrorAgent", version="1.0.0")
                super().__init__(metadata)

            async def initialize(self, context):
                self.context = context
                self.update_status(AgentStatus.READY)
                return True

            async def process_task(self, task):
                try:
                    if task.get("type") == "error_task":
                        raise Exception("Simulated task error")
                    return {"status": "completed", "task_id": task.get("task_id")}
                except Exception as e:
                    await self.handle_error(e, "task processing")
                    return {
                        "status": "error",
                        "error": str(e),
                        "task_id": task.get("task_id", "unknown"),
                    }

            async def handle_message(self, message):
                return None

            async def get_health_status(self):
                return {"healthy": self.status != AgentStatus.ERROR}

            async def shutdown(self):
                self.update_status(AgentStatus.TERMINATED)

        agent = ErrorAgent()
        context = AgentContext(orchestrator_id="test_orch", session_id="test_session")
        await agent.initialize(context)

        # Process error task
        error_task = {"task_id": "error_task_123", "type": "error_task"}

        result = await agent.process_task(error_task)

        assert result["status"] == "error"
        assert "Simulated task error" in result["error"]
        assert agent.status == AgentStatus.ERROR
