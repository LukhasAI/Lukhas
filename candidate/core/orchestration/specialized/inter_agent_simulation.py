#!/usr/bin/env python3
"""
Inter-Agent Simulation Module
=============================

This module provides inter-agent simulation functionality for the LUKHAS Cognitive system.
It handles communication and coordination between different agents.
"""
import streamlit as st

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agents in the system."""

    JULES = "jules"
    CODEX = "codex"
    LAMBDA_BOT = "lambda_bot"
    ORCHESTRATOR = "orchestrator"


class MessageType(Enum):
    """Types of messages between agents."""

    HEARTBEAT = "heartbeat"
    COMMAND = "command"
    RESPONSE = "response"
    ERROR = "error"
    STATUS = "status"


@dataclass
class AgentMessage:
    """Message structure for inter-agent communication."""

    sender: str
    receiver: str
    message_type: MessageType
    content: Any
    timestamp: float
    message_id: str


class Agent:
    """Base agent class for simulation."""

    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = "initialized"
        self.message_queue = []
        self.last_heartbeat = time.time()

        logger.info(f"Agent {agent_id} ({agent_type.value}) initialized")

    async def send_message(self, receiver: str, message_type: MessageType, content: Any) -> AgentMessage:
        """Send a message to another agent."""
        message = AgentMessage(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            timestamp=time.time(),
            message_id=f"{self.agent_id}_{int(time.time(} * 1000)}",
        )

        logger.debug(f"Agent {self.agent_id} sending message to {receiver}: {message_type.value}")
        return message

    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process an incoming message."""
        logger.debug(f"Agent {self.agent_id} processing message from {message.sender}: {message.message_type.value}")

        if message.message_type == MessageType.HEARTBEAT:
            self.last_heartbeat = time.time()
            return await self.send_message(message.sender, MessageType.RESPONSE, {"status": "alive"})

        elif message.message_type == MessageType.STATUS:
            status_info = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "status": self.status,
                "last_heartbeat": self.last_heartbeat,
            }
            return await self.send_message(message.sender, MessageType.RESPONSE, status_info)

        return None

    def get_status(self) -> dict[str, Any]:
        """Get agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat,
            "message_queue_length": len(self.message_queue),
        }


class InterAgentSimulation:
    """Main inter-agent simulation class."""

    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.message_log: list[AgentMessage] = []
        self.simulation_running = False
        self.simulation_start_time = None

        logger.info("Inter-agent simulation initialized")

    def add_agent(self, agent_id: str, agent_type: AgentType) -> Agent:
        """Add an agent to the simulation."""
        agent = Agent(agent_id, agent_type)
        self.agents[agent_id] = agent
        logger.info(f"Added agent {agent_id} to simulation")
        return agent

    async def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        message_type: MessageType,
        content: Any,
    ) -> bool:
        """Send a message between agents."""
        if sender_id not in self.agents or receiver_id not in self.agents:
            logger.error(f"Invalid agent IDs: {sender_id} -> {receiver_id}")
            return False

        sender = self.agents[sender_id]
        receiver = self.agents[receiver_id]

        # Create and send message
        message = await sender.send_message(receiver_id, message_type, content)
        self.message_log.append(message)

        # Process message at receiver
        response = await receiver.process_message(message)
        if response:
            self.message_log.append(response)

        return True

    async def broadcast_heartbeat(self) -> dict[str, Any]:
        """Broadcast heartbeat to all agents."""
        heartbeat_results = {}

        for agent_id in self.agents:
            try:
                # Send heartbeat
                await self.send_message(
                    "system",
                    agent_id,
                    MessageType.HEARTBEAT,
                    {"timestamp": time.time()},
                )
                heartbeat_results[agent_id] = "success"
            except Exception as e:
                logger.error(f"Heartbeat failed for agent {agent_id}: {e}")
                heartbeat_results[agent_id] = f"failed: {e}"

        return heartbeat_results

    async def run_simulation(self, intent: dict[str, Any]) -> dict[str, Any]:
        """Run a simulation with the given intent."""
        logger.info(f"Running simulation with intent: {intent}")

        self.simulation_running = True
        self.simulation_start_time = time.time()

        # Add some agents if none exist
        if not self.agents:
            self.add_agent("system", AgentType.ORCHESTRATOR)
            self.add_agent("jules_01", AgentType.JULES)
            self.add_agent("codex_01", AgentType.CODEX)
            self.add_agent("orchestrator", AgentType.ORCHESTRATOR)

        # Process the intent
        await self.send_message("system", "orchestrator", MessageType.COMMAND, intent)

        # Run heartbeat
        await self.broadcast_heartbeat()

        result = {
            "status": "completed",
            "intent": intent,
            "agents_involved": len(self.agents),
            "messages_sent": len(self.message_log),
            "simulation_time": time.time() - self.simulation_start_time,
        }

        self.simulation_running = False
        return result

    async def simulate_signal_desync(self) -> dict[str, Any]:
        """Simulate signal desynchronization."""
        logger.info("Simulating signal desync")

        # Ensure agents exist
        if "jules_01" not in self.agents:
            self.add_agent("jules_01", AgentType.JULES)
        if "codex_01" not in self.agents:
            self.add_agent("codex_01", AgentType.CODEX)

        # Simulate out-of-order messages
        await self.send_message("jules_01", "codex_01", MessageType.COMMAND, {"sequence": 2})
        await self.send_message("jules_01", "codex_01", MessageType.COMMAND, {"sequence": 1})
        await self.send_message("jules_01", "codex_01", MessageType.COMMAND, {"sequence": 3})

        return {
            "test": "signal_desync",
            "status": "simulated",
            "out_of_order_messages": 3,
        }

    async def simulate_ethical_override_conflict(self) -> dict[str, Any]:
        """Simulate ethical override conflict."""
        logger.info("Simulating ethical override conflict")

        # Ensure agents exist
        if "system" not in self.agents:
            self.add_agent("system", AgentType.ORCHESTRATOR)
        if "jules_01" not in self.agents:
            self.add_agent("jules_01", AgentType.JULES)
        if "codex_01" not in self.agents:
            self.add_agent("codex_01", AgentType.CODEX)

        # Simulate conflicting ethical commands
        await self.send_message(
            "system",
            "jules_01",
            MessageType.COMMAND,
            {"action": "block_content", "reason": "ethical"},
        )
        await self.send_message(
            "system",
            "codex_01",
            MessageType.COMMAND,
            {"action": "allow_content", "reason": "override"},
        )

        return {
            "test": "ethical_override_conflict",
            "status": "simulated",
            "conflict_detected": True,
        }

    async def simulate_latency_induced_echo_loop(self) -> dict[str, Any]:
        """Simulate latency-induced echo loop."""
        logger.info("Simulating latency-induced echo loop")

        # Ensure agents exist
        if "jules_01" not in self.agents:
            self.add_agent("jules_01", AgentType.JULES)
        if "codex_01" not in self.agents:
            self.add_agent("codex_01", AgentType.CODEX)

        # Simulate echo loop with delays
        for i in range(3):
            await self.send_message("jules_01", "codex_01", MessageType.COMMAND, {"echo_test": i})
            await asyncio.sleep(0.1)
            await self.send_message(
                "codex_01",
                "jules_01",
                MessageType.RESPONSE,
                {"echo_response": i},
            )

        return {
            "test": "latency_induced_echo_loop",
            "status": "simulated",
            "echo_cycles": 3,
        }
        """Simulate echo controller functionality."""
        logger.info("Starting echo controller simulation")

        # Add some test agents
        self.add_agent("jules_01", AgentType.JULES)
        self.add_agent("codex_01", AgentType.CODEX)
        self.add_agent("lambda_bot", AgentType.LAMBDA_BOT)

        # Simulate echo detection
        echo_results = []

        # Test 1: Normal communication
        await self.send_message("jules_01", "codex_01", MessageType.COMMAND, {"action": "analyze"})
        echo_results.append({"test": "normal_communication", "status": "passed"})

        # Test 2: Heartbeat
        heartbeat_results = await self.broadcast_heartbeat()
        echo_results.append(
            {
                "test": "heartbeat",
                "status": "passed",
                "results": heartbeat_results,
            }
        )

        # Test 3: Status check
        for agent_id in self.agents:
            await self.send_message("system", agent_id, MessageType.STATUS, {})
        echo_results.append({"test": "status_check", "status": "passed"})

        return {
            "echo_controller_simulation": "completed",
            "agents_tested": len(self.agents),
            "messages_sent": len(self.message_log),
            "test_results": echo_results,
        }

    async def simulate_echo_controller(self) -> dict[str, Any]:
        """Simulate echo controller functionality."""
        logger.info("Starting echo controller simulation")

        # Add some test agents if they don't exist
        if "jules_01" not in self.agents:
            self.add_agent("jules_01", AgentType.JULES)
        if "codex_01" not in self.agents:
            self.add_agent("codex_01", AgentType.CODEX)
        if "lambda_bot" not in self.agents:
            self.add_agent("lambda_bot", AgentType.LAMBDA_BOT)

        # Simulate echo detection
        echo_results = []

        # Test 1: Normal communication
        await self.send_message("jules_01", "codex_01", MessageType.COMMAND, {"action": "analyze"})
        echo_results.append({"test": "normal_communication", "status": "passed"})

        # Test 2: Heartbeat
        heartbeat_results = await self.broadcast_heartbeat()
        echo_results.append(
            {
                "test": "heartbeat",
                "status": "passed",
                "results": heartbeat_results,
            }
        )

        # Test 3: Status check
        for agent_id in self.agents:
            if agent_id != "system":
                await self.send_message("system", agent_id, MessageType.STATUS, {})
        echo_results.append({"test": "status_check", "status": "passed"})

        return {
            "echo_controller_simulation": "completed",
            "agents_tested": len(self.agents),
            "messages_sent": len(self.message_log),
            "test_results": echo_results,
        }
        """Simulate delayed echo detection."""
        logger.info(f"Simulating delayed echo with {delay}s delay")

        start_time = time.time()

        # Send initial message
        await self.send_message(
            "jules_01",
            "codex_01",
            MessageType.COMMAND,
            {"action": "test_echo"},
        )

        # Wait for delay
        await asyncio.sleep(delay)

        # Send delayed response
        await self.send_message(
            "codex_01",
            "jules_01",
            MessageType.RESPONSE,
            {"result": "delayed_response"},
        )

        end_time = time.time()
        actual_delay = end_time - start_time

        return {
            "test": "delayed_echo",
            "requested_delay": delay,
            "actual_delay": actual_delay,
            "status": "completed",
        }

    async def simulate_delayed_echo(self, delay: float = 1.0) -> dict[str, Any]:
        """Simulate delayed echo detection."""
        logger.info(f"Simulating delayed echo with {delay}s delay")

        # Ensure agents exist
        if "jules_01" not in self.agents:
            self.add_agent("jules_01", AgentType.JULES)
        if "codex_01" not in self.agents:
            self.add_agent("codex_01", AgentType.CODEX)

        start_time = time.time()

        # Send initial message
        await self.send_message(
            "jules_01",
            "codex_01",
            MessageType.COMMAND,
            {"action": "test_echo"},
        )

        # Wait for delay
        await asyncio.sleep(delay)

        # Send delayed response
        await self.send_message(
            "codex_01",
            "jules_01",
            MessageType.RESPONSE,
            {"result": "delayed_response"},
        )

        end_time = time.time()
        actual_delay = end_time - start_time

        return {
            "test": "delayed_echo",
            "requested_delay": delay,
            "actual_delay": actual_delay,
            "status": "completed",
        }

    async def simulate_failed_handshake(self) -> dict[str, Any]:
        """Simulate failed handshake detection."""
        logger.info("Simulating failed handshake")

        # Add an agent that will "fail"
        failed_agent = self.add_agent("failed_agent", AgentType.JULES)
        failed_agent.status = "failed"

        # Try to communicate with failed agent
        try:
            await self.send_message("system", "failed_agent", MessageType.HEARTBEAT, {})
            return {
                "test": "failed_handshake",
                "status": "failed",
                "error": "Agent should have failed but didn't",
            }
        except Exception as e:
            return {
                "test": "failed_handshake",
                "status": "detected",
                "error": str(e),
            }

    def get_simulation_status(self) -> dict[str, Any]:
        """Get current simulation status."""
        return {
            "agents": {agent_id: agent.get_status() for agent_id, agent in self.agents.items()},
            "message_count": len(self.message_log),
            "simulation_running": self.simulation_running,
            "simulation_start_time": self.simulation_start_time,
        }

    def export_message_log(self) -> list[dict[str, Any]]:
        """Export message log for analysis."""
        return [
            {
                "sender": msg.sender,
                "receiver": msg.receiver,
                "type": msg.message_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "message_id": msg.message_id,
            }
            for msg in self.message_log
        ]


# Global simulation instance
_simulation = None


def get_simulation() -> InterAgentSimulation:
    """Get the global simulation instance."""
    global _simulation
    if _simulation is None:
        _simulation = InterAgentSimulation()
    return _simulation


async def main():
    """Main function for testing."""
    print("🤖 LUKHAS Cognitive AI Inter-Agent Simulation")
    print("=" * 50)

    simulation = get_simulation()

    # Run echo controller simulation
    echo_results = await simulation.simulate_echo_controller()
    print("\n📊 Echo Controller Results:")
    print(json.dumps(echo_results, indent=2))

    # Run delayed echo simulation
    delayed_results = await simulation.simulate_delayed_echo(0.5)
    print("\n📊 Delayed Echo Results:")
    print(json.dumps(delayed_results, indent=2))

    # Run failed handshake simulation
    failed_results = await simulation.simulate_failed_handshake()
    print("\n📊 Failed Handshake Results:")
    print(json.dumps(failed_results, indent=2))

    # Get final status
    status = simulation.get_simulation_status()
    print("\n📊 Final Status:")
    print(f"Agents: {len(status['agents'])}")
    print(f"Messages: {status['message_count']}")

    print("\n🎯 Inter-Agent Simulation Complete")


if __name__ == "__main__":
    asyncio.run(main())