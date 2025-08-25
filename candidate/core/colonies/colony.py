"""
Enhanced Colony with Signal Bus Integration
===========================================
Connects the colony architecture with our endocrine signal system.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from candidate.orchestration.signals.homeostasis import HomeostasisController

# Import our signal system
from candidate.orchestration.signals.signal_bus import Signal, SignalBus, SignalType

# Import base colony
try:
    from candidate.core.colonies.base_colony import BaseColony
except ImportError:
    # Simplified base colony for now

    class BaseColony:

        def __init__(self, colony_id: str, capabilities: list[str]):
            self.colony_id = colony_id
            self.capabilities = capabilities
            self.agents = {}
            self.is_running = False

        async def start(self):
            self.is_running = True

        async def stop(self):
            self.is_running = False


logger = logging.getLogger(__name__)


@dataclass
class ConsensusResult:
    """Result of a colony consensus operation"""

    consensus_reached: bool
    decision: Any
    confidence: float
    votes: dict[str, Any]
    participation_rate: float
    dissent_reasons: list[str] = field(default_factory=list)
    signal_emissions: list[Signal] = field(default_factory=list)


class ColonySignalIntegration:
    """Mixin for integrating colonies with the signal bus"""

    def __init__(self):
        self.signal_bus = SignalBus()
        self.homeostasis = HomeostasisController()
        self.signal_history = []

    async def emit_hormone(
        self,
        signal_type: SignalType,
        level: float,
        metadata: Optional[dict] = None,
    ):
        """Emit a hormone signal from the colony"""
        signal = Signal(
            name=signal_type,
            source=f"colony_{getattr(self, 'colony_id', 'unknown')}",
            level=level,
            metadata=metadata or {},
        )

        # Publish to signal bus
        success = self.signal_bus.publish(signal)

        # Track in history
        self.signal_history.append(
            {"timestamp": time.time(), "signal": signal, "success": success}
        )

        # Check homeostasis
        if success:
            active_signals = self.signal_bus.get_active_signals()
            self.homeostasis.process_signals(active_signals)

            # Check for emergency conditions
            state = self.homeostasis.get_system_state()
            if state.get("emergency_mode"):
                await self._handle_emergency_mode(state)

        return success

    async def _handle_emergency_mode(self, state: dict[str, Any]):
        """Handle emergency mode triggered by homeostasis"""
        logger.warning(f"Colony entering emergency mode: {state}")

        # Emit stress signal
        await self.emit_hormone(
            SignalType.STRESS,
            0.9,
            {"reason": "emergency_mode", "state": state},
        )

        # Trigger colony reorganization
        if hasattr(self, "reorganize_for_emergency"):
            await self.reorganize_for_emergency()

    def subscribe_to_signals(self, signal_types: list[SignalType]):
        """Subscribe to specific signal types"""
        for signal_type in signal_types:
            self.signal_bus.subscribe(signal_type, self._handle_signal)

    def _handle_signal(self, signal: Signal):
        """Handle incoming signals"""
        logger.info(f"Colony received signal: {signal.name} at level {signal.level}")

        # Adjust colony behavior based on signal
        if signal.name == SignalType.URGENCY and signal.level > 0.7:
            self._increase_processing_speed()
        elif signal.name == SignalType.STRESS and signal.level > 0.8:
            self._activate_resilience_mode()

    def _increase_processing_speed(self):
        """Increase colony processing speed for urgent tasks"""
        if hasattr(self, "processing_speed"):
            self.processing_speed *= 1.5
            logger.info("Colony processing speed increased due to urgency")

    def _activate_resilience_mode(self):
        """Activate resilience mode during high stress"""
        if hasattr(self, "resilience_mode"):
            self.resilience_mode = True
            logger.info("Colony resilience mode activated")


class EnhancedReasoningColony(ColonySignalIntegration):
    """Enhanced reasoning colony with signal integration"""

    def __init__(self, colony_id: str = None):
        super().__init__()
        self.colony_id = colony_id or str(uuid.uuid4())
        self.reasoning_agents = {}
        self.consensus_threshold = 0.7
        self.processing_speed = 1.0
        self.resilience_mode = False

        # Subscribe to relevant signals
        self.subscribe_to_signals(
            [SignalType.URGENCY, SignalType.STRESS, SignalType.AMBIGUITY]
        )

    async def process_query(
        self, query: str, context: dict[str, Any] = None
    ) -> ConsensusResult:
        """Process a query through the colony with signal awareness"""
        start_time = time.time()

        # Emit starting signal
        await self.emit_hormone(
            SignalType.NOVELTY,
            0.5,
            {
                "query": query[:100],  # First 100 chars
                "has_context": context is not None,
            },
        )

        # Collect votes from agents
        votes = {}
        for agent_id, agent in self.reasoning_agents.items():
            if hasattr(agent, "evaluate"):
                vote = await agent.evaluate(query, context)
                votes[agent_id] = vote

        # Calculate consensus
        consensus = self._calculate_consensus(votes)

        # Emit result signals based on consensus
        signal_emissions = []
        if consensus["confidence"] > 0.8:
            signal = Signal(
                name=SignalType.TRUST,
                source=f"colony_{self.colony_id}",
                level=consensus["confidence"],
            )
            self.signal_bus.publish(signal)
            signal_emissions.append(signal)
        elif consensus["confidence"] < 0.3:
            signal = Signal(
                name=SignalType.AMBIGUITY,
                source=f"colony_{self.colony_id}",
                level=1.0 - consensus["confidence"],
            )
            self.signal_bus.publish(signal)
            signal_emissions.append(signal)

        # Create result
        result = ConsensusResult(
            consensus_reached=consensus["reached"],
            decision=consensus["decision"],
            confidence=consensus["confidence"],
            votes=votes,
            participation_rate=len(votes) / max(1, len(self.reasoning_agents)),
            dissent_reasons=consensus.get("dissent_reasons", []),
            signal_emissions=signal_emissions,
        )

        # Log processing time
        processing_time = time.time() - start_time
        logger.info(
            f"Colony processed query in {processing_time:.2f}s with confidence {result.confidence:.2f}"
        )

        return result

    def _calculate_consensus(self, votes: dict[str, Any]) -> dict[str, Any]:
        """Calculate consensus from votes"""
        if not votes:
            return {
                "reached": False,
                "decision": None,
                "confidence": 0.0,
                "dissent_reasons": ["No votes received"],
            }

        # Simple majority voting for demo
        decisions = {}
        for vote in votes.values():
            decision = str(vote.get("decision", "unknown"))
            decisions[decision] = decisions.get(decision, 0) + 1

        # Find majority decision
        total_votes = len(votes)
        majority_decision = max(decisions.items(), key=lambda x: x[1])
        confidence = majority_decision[1] / total_votes

        return {
            "reached": confidence >= self.consensus_threshold,
            "decision": majority_decision[0],
            "confidence": confidence,
            "dissent_reasons": [
                f"Agent voted for {d}" for d in decisions if d != majority_decision[0]
            ],
        }

    async def reorganize_for_emergency(self):
        """Reorganize colony structure during emergency"""
        logger.warning(f"Colony {self.colony_id} reorganizing for emergency")

        # In emergency, bypass slow agents
        fast_agents = {
            aid: agent
            for aid, agent in self.reasoning_agents.items()
            if hasattr(agent, "response_time") and agent.response_time < 1.0
        }

        if fast_agents:
            self.reasoning_agents = fast_agents
            logger.info(
                f"Colony reduced to {len(fast_agents)} fast agents for emergency"
            )

        # Lower consensus threshold for faster decisions
        self.consensus_threshold = 0.5

        # Emit reorganization signal
        await self.emit_hormone(
            SignalType.STRESS,
            0.7,
            {
                "action": "emergency_reorganization",
                "agent_count": len(self.reasoning_agents),
            },
        )


class SwarmSignalNetwork:
    """Swarm network integrated with signal bus"""

    def __init__(self, signal_bus: SignalBus):
        self.signal_bus = signal_bus
        self.agents = {}
        self.tag_propagation = {}
        self.oscillation_threshold = 5
        self.oscillation_history = []

    async def propagate_signal_as_tag(self, signal: Signal):
        """Convert signal to tag and propagate through swarm"""
        tag = f"signal_{signal.name.value}"
        value = str(signal.level)

        # Track propagation
        if tag not in self.tag_propagation:
            self.tag_propagation[tag] = []

        self.tag_propagation[tag].append(
            {"timestamp": time.time(), "value": value, "source": signal.source}
        )

        # Detect oscillations
        if self._detect_oscillation(tag):
            # Emit stress signal if oscillating
            stress_signal = Signal(
                name=SignalType.STRESS,
                source="swarm_oscillation_detector",
                level=0.8,
                metadata={"oscillating_tag": tag},
            )
            self.signal_bus.publish(stress_signal)
            logger.warning(f"Oscillation detected in tag {tag}")

        # Propagate to all agents
        propagation_tasks = []
        for _agent_id, agent in self.agents.items():
            if hasattr(agent, "receive_tag"):
                propagation_tasks.append(
                    agent.receive_tag(signal.source, tag, value, signal.level)
                )

        if propagation_tasks:
            await asyncio.gather(*propagation_tasks, return_exceptions=True)

    def _detect_oscillation(self, tag: str) -> bool:
        """Detect if a tag is oscillating"""
        if tag not in self.tag_propagation:
            return False

        recent = self.tag_propagation[tag][-10:]  # Last 10 propagations
        if len(recent) < 10:
            return False

        # Check for value flipping
        values = [p["value"] for p in recent]
        changes = sum(1 for i in range(1, len(values)) if values[i] != values[i - 1])

        return changes > self.oscillation_threshold

    def get_swarm_consensus(self) -> dict[str, Any]:
        """Get current swarm consensus on all tags"""
        consensus = {}

        for tag, propagations in self.tag_propagation.items():
            if not propagations:
                continue

            # Get most recent values
            recent_values = [p["value"] for p in propagations[-100:]]

            # Find most common value
            value_counts = {}
            for v in recent_values:
                value_counts[v] = value_counts.get(v, 0) + 1

            if value_counts:
                consensus[tag] = max(value_counts.items(), key=lambda x: x[1])[0]

        return consensus


# Example usage


async def demo_enhanced_colony():
    """Demonstrate enhanced colony with signal integration"""

    # Create colony
    colony = EnhancedReasoningColony("reasoning-alpha")

    # Process a query
    result = await colony.process_query(
        "Should we increase system resources?",
        {"current_load": 0.85, "memory_usage": 0.72},
    )

    print(f"Consensus reached: {result.consensus_reached}")
    print(f"Decision: {result.decision}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Signals emitted: {len(result.signal_emissions)}")

    # Check homeostasis
    state = colony.homeostasis.get_system_state()
    print(f"System state: {state}")

    # Create swarm
    swarm = SwarmSignalNetwork(colony.signal_bus)

    # Propagate a signal through swarm
    test_signal = Signal(name=SignalType.URGENCY, source="test", level=0.7)
    await swarm.propagate_signal_as_tag(test_signal)

    # Get swarm consensus
    consensus = swarm.get_swarm_consensus()
    print(f"Swarm consensus: {consensus}")


if __name__ == "__main__":
    asyncio.run(demo_enhanced_colony())
