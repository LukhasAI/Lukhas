"""
VIVOX.QREADY - Quantum Synchronization Events
Multi-agent quantum coherence and synchronization
"""

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import numpy as np

from candidate.core.common import get_logger

logger = get_logger(__name__)


class SyncType(Enum):
    """Types of quantum synchronization"""

    ENTANGLEMENT = "entanglement"  # Direct quantum entanglement
    RESONANCE = "resonance"  # Resonance coupling
    PHASE_LOCK = "phase_lock"  # Phase synchronization
    CORRELATION = "correlation"  # Classical correlation
    EMERGENT = "emergent"  # Spontaneous synchronization
    CONSENSUS = "consensus"  # Multi-agent consensus sync


@dataclass
class QSyncEvent:
    """Quantum synchronization event between agents"""

    event_id: str
    agent_ids: list[str]
    sync_type: SyncType
    correlation_strength: float  # 0-1 synchronization strength
    timestamp: datetime
    qi_states: dict[str, np.ndarray] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_strong_sync(self) -> bool:
        """Check if synchronization is strong enough for consensus"""
        return self.correlation_strength > 0.7

    def get_sync_quality(self) -> str:
        """Categorize synchronization quality"""
        if self.correlation_strength > 0.9:
            return "perfect"
        elif self.correlation_strength > 0.7:
            return "strong"
        elif self.correlation_strength > 0.5:
            return "moderate"
        elif self.correlation_strength > 0.3:
            return "weak"
        else:
            return "minimal"


class EntanglementBridge:
    """
    Manages quantum entanglement between multiple agents
    Enables non-communication synchronization
    """

    def __init__(self):
        self.entangled_pairs: dict[tuple[str, str], float] = {}
        self.entanglement_network: dict[str, set[str]] = defaultdict(set)
        self.bridge_states: dict[str, np.ndarray] = {}

        # Entanglement parameters
        self.min_entanglement_strength = 0.5
        self.decoherence_rate = 0.01
        self.max_distance = 5  # Maximum entanglement chain distance

        logger.info("EntanglementBridge initialized")

    def create_entanglement(
        self, agent1_id: str, agent2_id: str, strength: float = 1.0
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Create quantum entanglement between two agents

        Args:
            agent1_id: First agent identifier
            agent2_id: Second agent identifier
            strength: Entanglement strength (0-1)

        Returns:
            Tuple of entangled states for each agent
        """
        # Create Bell state with variable entanglement
        if strength >= 1.0:
            # Perfect Bell state |00⟩ + |11⟩
            state = np.zeros(4, dtype=complex)
            state[0] = 1.0 / np.sqrt(2)
            state[3] = 1.0 / np.sqrt(2)
        else:
            # Partially entangled state
            theta = strength * np.pi / 2
            state = np.zeros(4, dtype=complex)
            state[0] = np.cos(theta / 2)
            state[3] = np.sin(theta / 2)

        # Store entanglement
        pair_key = tuple(sorted([agent1_id, agent2_id]))
        self.entangled_pairs[pair_key] = strength

        # Update network
        self.entanglement_network[agent1_id].add(agent2_id)
        self.entanglement_network[agent2_id].add(agent1_id)

        # Create individual states (traced out from full state)
        # Note: These are not true individual states but correlation markers
        agent1_state = np.array([np.sqrt(0.5), 0, 0, np.sqrt(0.5)], dtype=complex)
        agent2_state = np.array([np.sqrt(0.5), 0, 0, np.sqrt(0.5)], dtype=complex)

        # Store bridge states
        self.bridge_states[f"{agent1_id}_{agent2_id}"] = state

        return agent1_state, agent2_state

    def measure_correlation(
        self,
        agent1_state: np.ndarray,
        agent2_state: np.ndarray,
        agent1_id: str,
        agent2_id: str,
    ) -> float:
        """
        Measure quantum correlation between agent states

        Args:
            agent1_state: Quantum state of agent 1
            agent2_state: Quantum state of agent 2
            agent1_id: Agent 1 identifier
            agent2_id: Agent 2 identifier

        Returns:
            Correlation strength (0-1)
        """
        # Check if agents are entangled
        pair_key = tuple(sorted([agent1_id, agent2_id]))
        if pair_key not in self.entangled_pairs:
            # No entanglement - check classical correlation
            return float(abs(np.vdot(agent1_state, agent2_state)) ** 2)

        # Get entanglement strength
        entanglement = self.entangled_pairs[pair_key]

        # For entangled states, correlation should be high
        # The entanglement strength directly represents the correlation
        # Classical correlation is added as a baseline
        classical_correlation = abs(np.vdot(agent1_state, agent2_state)) ** 2

        # Entangled states have enhanced correlation
        correlation = entanglement * 0.8 + classical_correlation * 0.2

        return float(np.clip(correlation, 0, 1))

    def propagate_entanglement(self, source_agent: str) -> dict[str, float]:
        """
        Propagate entanglement through network from source agent

        Args:
            source_agent: Starting agent for propagation

        Returns:
            Dictionary of reachable agents and correlation strengths
        """
        reachable = {source_agent: 1.0}
        visited = set()
        queue = [(source_agent, 1.0, 0)]  # (agent, strength, distance)

        while queue:
            current_agent, current_strength, distance = queue.pop(0)

            if current_agent in visited or distance >= self.max_distance:
                continue

            visited.add(current_agent)

            # Check all entangled partners
            for partner in self.entanglement_network[current_agent]:
                pair_key = tuple(sorted([current_agent, partner]))
                edge_strength = self.entangled_pairs.get(pair_key, 0)

                # Calculate propagated strength
                propagated_strength = (
                    current_strength
                    * edge_strength
                    * (1 - self.decoherence_rate * distance)
                )

                if propagated_strength > self.min_entanglement_strength:
                    if (
                        partner not in reachable
                        or propagated_strength > reachable[partner]
                    ):
                        reachable[partner] = propagated_strength
                        queue.append((partner, propagated_strength, distance + 1))

        return reachable

    def find_entanglement_clusters(self) -> list[set[str]]:
        """Find clusters of strongly entangled agents"""
        clusters = []
        visited = set()

        for agent in self.entanglement_network:
            if agent not in visited:
                # Find all agents reachable with strong entanglement
                cluster = set()
                queue = [agent]

                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue

                    visited.add(current)
                    cluster.add(current)

                    # Add strongly entangled partners
                    for partner in self.entanglement_network[current]:
                        pair_key = tuple(sorted([current, partner]))
                        if self.entangled_pairs.get(pair_key, 0) > 0.7:
                            if partner not in visited:
                                queue.append(partner)

                if len(cluster) > 1:
                    clusters.append(cluster)

        return clusters

    def apply_decoherence(self, time_step: float = 0.1):
        """Apply decoherence to all entanglements"""
        pairs_to_remove = []

        for pair_key, strength in self.entangled_pairs.items():
            # Exponential decay
            new_strength = strength * np.exp(-self.decoherence_rate * time_step)

            if new_strength < self.min_entanglement_strength:
                pairs_to_remove.append(pair_key)
            else:
                self.entangled_pairs[pair_key] = new_strength

        # Remove weak entanglements
        for pair_key in pairs_to_remove:
            del self.entangled_pairs[pair_key]
            agent1, agent2 = pair_key
            self.entanglement_network[agent1].discard(agent2)
            self.entanglement_network[agent2].discard(agent1)


class QISynchronizer:
    """
    Manages quantum synchronization events and multi-agent coherence
    """

    def __init__(self, entanglement_bridge: Optional[EntanglementBridge] = None):
        self.bridge = entanglement_bridge or EntanglementBridge()
        self.sync_events: list[QSyncEvent] = []
        self.agent_states: dict[str, np.ndarray] = {}
        self.phase_locks: dict[tuple[str, str], float] = {}

        # Synchronization parameters
        self.sync_threshold = 0.5
        self.phase_tolerance = np.pi / 4
        self.resonance_frequencies: dict[str, float] = {}

        logger.info("QISynchronizer initialized")

    def register_agent(
        self, agent_id: str, initial_state: np.ndarray, resonance_frequency: float = 1.0
    ):
        """Register an agent for quantum synchronization"""
        self.agent_states[agent_id] = initial_state
        self.resonance_frequencies[agent_id] = resonance_frequency
        logger.debug(
            f"Agent {agent_id} registered with resonance frequency {resonance_frequency}"
        )

    def create_sync_event(
        self, agent_ids: list[str], sync_type: SyncType = SyncType.EMERGENT
    ) -> Optional[QSyncEvent]:
        """
        Create a quantum synchronization event

        Args:
            agent_ids: List of participating agents
            sync_type: Type of synchronization

        Returns:
            QSyncEvent if successful, None otherwise
        """
        if len(agent_ids) < 2:
            return None

        # Get agent states
        states = {}
        for agent_id in agent_ids:
            if agent_id not in self.agent_states:
                logger.warning(f"Agent {agent_id} not registered")
                return None
            states[agent_id] = self.agent_states[agent_id]

        # Calculate synchronization based on type
        if sync_type == SyncType.ENTANGLEMENT:
            correlation = self._calculate_entanglement_sync(agent_ids, states)
        elif sync_type == SyncType.PHASE_LOCK:
            correlation = self._calculate_phase_sync(agent_ids, states)
        elif sync_type == SyncType.RESONANCE:
            correlation = self._calculate_resonance_sync(agent_ids)
        else:
            correlation = self._calculate_emergent_sync(states)

        if correlation < self.sync_threshold:
            return None

        # Create sync event
        event = QSyncEvent(
            event_id=self._generate_event_id(),
            agent_ids=agent_ids,
            sync_type=sync_type,
            correlation_strength=correlation,
            timestamp=datetime.now(),
            qi_states=states.copy(),
            metadata={
                "agent_count": len(agent_ids),
                "sync_quality": self._get_sync_quality(correlation),
            },
        )

        self.sync_events.append(event)
        return event

    def synchronize_agents(
        self,
        agent_ids: list[str],
        target_state: Optional[np.ndarray] = None,
        sync_strength: float = 0.5,
    ) -> dict[str, np.ndarray]:
        """
        Actively synchronize multiple agents

        Args:
            agent_ids: Agents to synchronize
            target_state: Target state for synchronization (optional)
            sync_strength: Strength of synchronization (0-1)

        Returns:
            Dictionary of synchronized states
        """
        if not agent_ids:
            return {}

        # Determine target state
        if target_state is None:
            # Use average state as target
            states = [
                self.agent_states[aid] for aid in agent_ids if aid in self.agent_states
            ]
            if not states:
                return {}
            target_state = np.mean(states, axis=0)
            target_state /= np.linalg.norm(target_state)

        # Synchronize each agent towards target
        synchronized_states = {}

        for agent_id in agent_ids:
            if agent_id not in self.agent_states:
                continue

            current_state = self.agent_states[agent_id]

            # Partial synchronization
            synchronized = (
                1 - sync_strength
            ) * current_state + sync_strength * target_state
            synchronized /= np.linalg.norm(synchronized)

            # Update state
            self.agent_states[agent_id] = synchronized
            synchronized_states[agent_id] = synchronized

        # Create sync event
        self.create_sync_event(agent_ids, SyncType.PHASE_LOCK)

        return synchronized_states

    def detect_emergent_synchronization(
        self, min_agents: int = 2, correlation_threshold: float = 0.6
    ) -> list[QSyncEvent]:
        """
        Detect spontaneous synchronization between agents

        Args:
            min_agents: Minimum agents for sync detection
            correlation_threshold: Minimum correlation for sync

        Returns:
            List of detected synchronization events
        """
        detected_events = []
        agent_ids = list(self.agent_states.keys())

        if len(agent_ids) < min_agents:
            return detected_events

        # Check all combinations of agents
        from itertools import combinations

        for r in range(min_agents, min(len(agent_ids) + 1, 6)):  # Limit to 5 agents
            for agent_combo in combinations(agent_ids, r):
                # Calculate average correlation
                states = {aid: self.agent_states[aid] for aid in agent_combo}
                correlation = self._calculate_emergent_sync(states)

                if correlation >= correlation_threshold:
                    event = QSyncEvent(
                        event_id=self._generate_event_id(),
                        agent_ids=list(agent_combo),
                        sync_type=SyncType.EMERGENT,
                        correlation_strength=correlation,
                        timestamp=datetime.now(),
                        qi_states=states,
                        metadata={
                            "spontaneous": True,
                            "detection_threshold": correlation_threshold,
                        },
                    )
                    detected_events.append(event)

        # Add to history
        self.sync_events.extend(detected_events)

        return detected_events

    def _calculate_entanglement_sync(
        self, agent_ids: list[str], states: dict[str, np.ndarray]
    ) -> float:
        """Calculate synchronization through entanglement"""
        if len(agent_ids) < 2:
            return 0.0

        total_correlation = 0.0
        pair_count = 0

        # Check pairwise entanglement
        for i in range(len(agent_ids)):
            for j in range(i + 1, len(agent_ids)):
                correlation = self.bridge.measure_correlation(
                    states[agent_ids[i]],
                    states[agent_ids[j]],
                    agent_ids[i],
                    agent_ids[j],
                )
                total_correlation += correlation
                pair_count += 1

        return total_correlation / pair_count if pair_count > 0 else 0.0

    def _calculate_phase_sync(
        self, agent_ids: list[str], states: dict[str, np.ndarray]
    ) -> float:
        """Calculate phase synchronization"""
        if len(agent_ids) < 2:
            return 0.0

        # Extract phases
        phases = []
        for agent_id in agent_ids:
            state = states[agent_id]
            # Use dominant component phase
            dominant_idx = np.argmax(np.abs(state))
            phase = np.angle(state[dominant_idx])
            phases.append(phase)

        # Calculate phase coherence
        np.mean(phases)
        phase_variance = np.var(phases)

        # Convert variance to synchronization strength
        max_variance = np.pi**2  # Maximum possible variance
        sync_strength = 1.0 - (phase_variance / max_variance)

        return float(np.clip(sync_strength, 0, 1))

    def _calculate_resonance_sync(self, agent_ids: list[str]) -> float:
        """Calculate resonance-based synchronization"""
        if len(agent_ids) < 2:
            return 0.0

        # Get resonance frequencies
        frequencies = [self.resonance_frequencies.get(aid, 1.0) for aid in agent_ids]

        # Calculate frequency coherence
        mean_freq = np.mean(frequencies)
        freq_variance = np.var(frequencies)

        # Resonance occurs when frequencies are close
        if mean_freq > 0:
            relative_variance = freq_variance / (mean_freq**2)
            sync_strength = np.exp(-relative_variance * 10)  # Exponential decay
        else:
            sync_strength = 0.0

        return float(np.clip(sync_strength, 0, 1))

    def _calculate_emergent_sync(self, states: dict[str, np.ndarray]) -> float:
        """Calculate emergent synchronization from state overlap"""
        if len(states) < 2:
            return 0.0

        state_list = list(states.values())

        # Calculate average pairwise overlap
        total_overlap = 0.0
        pair_count = 0

        for i in range(len(state_list)):
            for j in range(i + 1, len(state_list)):
                overlap = abs(np.vdot(state_list[i], state_list[j])) ** 2
                total_overlap += overlap
                pair_count += 1

        return total_overlap / pair_count if pair_count > 0 else 0.0

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().isoformat()
        random_bytes = np.random.bytes(8)
        return f"qsync_{hashlib.sha256(f'{timestamp}{random_bytes}'.encode()).hexdigest()[:16]}"

    def _get_sync_quality(self, correlation: float) -> str:
        """Get synchronization quality description"""
        if correlation > 0.9:
            return "perfect"
        elif correlation > 0.7:
            return "strong"
        elif correlation > 0.5:
            return "moderate"
        else:
            return "weak"

    def get_sync_statistics(self) -> dict[str, Any]:
        """Get synchronization statistics"""
        if not self.sync_events:
            return {"message": "No synchronization events recorded"}

        # Analyze sync events
        sync_types = defaultdict(int)
        quality_distribution = defaultdict(int)
        agent_participation = defaultdict(int)

        for event in self.sync_events:
            sync_types[event.sync_type.value] += 1
            quality_distribution[event.get_sync_quality()] += 1
            for agent_id in event.agent_ids:
                agent_participation[agent_id] += 1

        # Calculate average correlation by type
        avg_correlation_by_type = {}
        for sync_type in SyncType:
            events_of_type = [e for e in self.sync_events if e.sync_type == sync_type]
            if events_of_type:
                avg_correlation_by_type[sync_type.value] = np.mean(
                    [e.correlation_strength for e in events_of_type]
                )

        # Find entanglement clusters
        clusters = self.bridge.find_entanglement_clusters()

        return {
            "total_sync_events": len(self.sync_events),
            "sync_type_distribution": dict(sync_types),
            "quality_distribution": dict(quality_distribution),
            "average_correlation": np.mean(
                [e.correlation_strength for e in self.sync_events]
            ),
            "avg_correlation_by_type": avg_correlation_by_type,
            "agent_participation": dict(agent_participation),
            "active_agents": len(self.agent_states),
            "entanglement_clusters": [list(cluster) for cluster in clusters],
            "strong_sync_rate": len([e for e in self.sync_events if e.is_strong_sync()])
            / len(self.sync_events),
        }
