"""Swarm tag propagation and ethical convergence simulation.

This module stress tests symbolic tag propagation across many agents
using the existing communication fabric. It can simulate up to 10k agents
with optional trust filtering ("PaLM-like" bias) and logs collision cases.

ΛTAG: swarm_simulation, tag_propagation, consensus
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass, field

from lukhas.core.efficient_communication import (
    EfficientCommunicationFabric,
    MessagePriority,
)
from lukhas.core.symbolism.tags import TagScope


@dataclass
class SimAgent:
    """Lightweight agent for tag propagation tests."""

    agent_id: str
    network: SwarmNetwork
    tags: dict[str, str] = field(default_factory=dict)
    # ΛTAG: survival_score influences swarm trust
    survival_score: float = 1.0

    async def propagate_tag(self, tag: str, value: str, trust: float) -> None:
        weighted_trust = trust * self.survival_score
        if self.network.high_trust_filter and weighted_trust < 0.8:
            return
        await self.network.broadcast(self, tag, value, weighted_trust)

    async def receive_tag(
        self, source_id: str, tag: str, value: str, trust: float
    ) -> None:
        current = self.tags.get(tag)
        if current is not None and current != value:
            self.network.log_collision(tag, current, value)
        self.tags[tag] = value


class SwarmNetwork:
    """Central network coordinating tag propagation."""

    def __init__(
        self, high_trust_filter: bool = False, value_bias: float = 1.0
    ) -> None:
        self.fabric = EfficientCommunicationFabric("swarm-net")
        self.high_trust_filter = high_trust_filter
        self.value_bias = value_bias
        self.agents: dict[str, SimAgent] = {}
        self.collisions: list[tuple[str, str, str]] = []
        self.tag_counts: dict[str, dict[str, int]] = {}

    async def start(self) -> None:
        await self.fabric.start()

    async def stop(self) -> None:
        await self.fabric.stop()

    def register(self, agent: SimAgent) -> None:
        self.agents[agent.agent_id] = agent
        self.tag_counts.setdefault(agent.agent_id, {})

    async def broadcast(
        self, sender: SimAgent, tag: str, value: str, trust: float
    ) -> None:
        weighted_trust = trust * self.value_bias
        payload = {
            "tag": tag,
            "value": value,
            "trust": weighted_trust,
            "scope": TagScope.GLOBAL.value,
        }
        for agent_id, agent in self.agents.items():
            if agent_id == sender.agent_id:
                continue
            await self.fabric.send_message(
                agent_id,
                "tag_update",
                payload,
                MessagePriority.NORMAL,
            )
            await agent.receive_tag(sender.agent_id, tag, value, weighted_trust)
        self.tag_counts.setdefault(tag, {}).setdefault(value, 0)
        self.tag_counts[tag][value] += 1

    def log_collision(self, tag: str, old_value: str, new_value: str) -> None:
        self.collisions.append((tag, old_value, new_value))

    def consensus(self) -> dict[str, str]:
        result = {}
        for tag, values in self.tag_counts.items():
            total = sum(values.values())
            for val, count in values.items():
                if count > total / 2:
                    result[tag] = val
        return result


async def simulate_swarm(
    num_agents: int = 10000,
    rounds: int = 1,
    *,
    high_trust_filter: bool = False,
    value_bias: float = 1.0,
) -> dict[str, int]:
    """Run the swarm tag propagation simulation."""
    network = SwarmNetwork(high_trust_filter=high_trust_filter, value_bias=value_bias)
    await network.start()

    agents = [
        SimAgent(f"agent-{i}", network, survival_score=random.uniform(0.5, 1.0))
        for i in range(num_agents)
    ]
    for agent in agents:
        network.register(agent)

    for _ in range(rounds):
        tasks = []
        for agent in agents:
            tag = f"t{random.randint(0, 5)}"
            value = f"v{random.randint(0, 2)}"
            trust = random.random()
            tasks.append(agent.propagate_tag(tag, value, trust))
        if tasks:
            await asyncio.gather(*tasks)

    consensus = network.consensus()
    metrics = {
        "agents": len(agents),
        "collisions": len(network.collisions),
        "consensus_tags": len(consensus),
        "cached_messages": len(network.fabric.message_cache),
    }

    await network.stop()
    return metrics


__all__ = ["simulate_swarm", "SimAgent", "SwarmNetwork"]
