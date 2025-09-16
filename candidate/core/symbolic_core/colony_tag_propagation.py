"""GLYPH-aware colony tag propagation for symbolic consciousness meshes."""

from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional

try:  # pragma: no cover - exercised when networkx is available
    import networkx as nx
except ImportError:  # pragma: no cover - fallback path validated separately
    nx = None  # type: ignore

logger = logging.getLogger(__name__)


try:  # pragma: no cover - prefer real implementations when lanes are available
    from lukhas.core.colonies import BaseColony, ConsensusResult, TagScope
except ImportError:  # pragma: no cover - fallback executed in unit tests
    logger.warning("GLYPH colony import fallback active – using in-memory colony primitives")

    @dataclass
    class ConsensusResult:  # type: ignore[redefinition]
        consensus_reached: bool
        decision: Any
        confidence: float
        votes: dict[str, str]
        participation_rate: float

    class BaseColony:  # type: ignore[redefinition]
        def __init__(self, colony_id: str, capabilities: Optional[list[str]] = None):
            self.colony_id = colony_id
            self.capabilities = capabilities or []
            self.agents: dict[str, Any] = {}

    class TagScope:  # type: ignore[redefinition]
        GLOBAL = "global"
        LOCAL = "local"


try:
    from candidate.core.symbolic_core.vocabularies import SymbolicVocabulary
except ImportError:  # pragma: no cover - deterministic fallback for tests

    @dataclass
    class SymbolicVocabulary:  # type: ignore[redefinition]
        """Light-weight vocabulary for symbolic registration during testing."""

        _registry: Dict[str, Dict[str, Any]] = field(default_factory=dict)

        # ΛTAG: glyph_vocabulary
        def register(self, concept: str, value: Any, metadata: Optional[dict[str, Any]] = None) -> None:
            metadata = metadata or {}
            self._registry.setdefault(concept, {"values": set(), "metadata": []})
            self._registry[concept]["values"].add(value)
            self._registry[concept]["metadata"].append(metadata)

        def lookup(self, concept: str) -> dict[str, Any]:
            return self._registry.get(concept, {"values": set(), "metadata": []})

        def stats(self) -> dict[str, Any]:
            return {"concepts": len(self._registry)}


@dataclass
class Tag:
    """Structured tag exchanged between consciousness agents."""

    key: str
    value: Any
    scope: str
    confidence: float = 1.0

    # ΛTAG: glyph_tag_serialization
    def serialize(self) -> dict[str, Any]:
        return {"key": self.key, "value": self.value, "scope": self.scope, "confidence": self.confidence}


@dataclass
class ConsciousnessAgent:
    """Representation of a consciousness node inside the colony mesh."""

    id: str
    resonance: float = 0.6
    driftScore: float = 0.0
    affect_delta: float = 0.0
    neighbors: set[str] = field(default_factory=set)

    def activate(self, signal: float) -> float:
        """Update resonance based on propagated signal and track metrics."""

        previous_resonance = self.resonance
        self.resonance = max(0.0, min(1.0, (self.resonance + signal) / 2))
        self.affect_delta = self.resonance - previous_resonance
        self.driftScore = max(0.0, 1.0 - abs(self.affect_delta))
        return self.resonance


class SymbolicReasoningColony(BaseColony):
    """Colony for symbolic reasoning and belief propagation."""

    def __init__(self, colony_id: str, agent_count: int = 4):
        super().__init__(colony_id, capabilities=["symbolic_reasoning"])
        self.vocabulary = SymbolicVocabulary()
        self.belief_network = nx.DiGraph() if nx else None
        self.propagation_history: list[dict[str, Any]] = []
        self.agents: dict[str, ConsciousnessAgent] = self._initialize_consciousness_mesh(agent_count)

    # ΛTAG: mesh_initialization
    def _initialize_consciousness_mesh(self, agent_count: int) -> dict[str, ConsciousnessAgent]:
        agents: dict[str, ConsciousnessAgent] = {}
        for idx in range(agent_count):
            agent_id = f"{self.colony_id}_node_{idx}"
            agents[agent_id] = ConsciousnessAgent(id=agent_id, resonance=0.55 + random.random() * 0.2)

        agent_ids = list(agents.keys())
        for idx, agent_id in enumerate(agent_ids):
            neighbor_id = agent_ids[(idx + 1) % len(agent_ids)]
            agents[agent_id].neighbors.add(neighbor_id)
            agents[neighbor_id].neighbors.add(agent_id)
            if self.belief_network:
                self.belief_network.add_edge(agent_id, neighbor_id)

        return agents

    async def execute_task(self, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """Execute symbolic reasoning task as required by BaseColony."""

        processed = self.process(task_data)
        belief_result = await self.propagate_belief(
            {
                "concept": task_data.get("concept", task_id),
                "value": task_data.get("value", ""),
                "strength": float(task_data.get("strength", 0.6)),
                "iterations": int(task_data.get("iterations", 1)),
            }
        )

        return {
            "task_id": task_id,
            "processed": processed,
            "belief_states": belief_result,
        }

    # ΛTAG: glyph_processing
    def process(self, task: Any) -> dict[str, Any]:
        """Process a consciousness task using GLYPH symbolic reasoning."""

        payload = task if isinstance(task, dict) else {"concept": str(task)}
        concept = payload.get("concept", "UNKNOWN").upper()
        value = payload.get("value", concept.lower())
        confidence = float(payload.get("confidence", 0.75))
        tag = Tag(key=concept, value=value, scope=payload.get("scope", TagScope.GLOBAL), confidence=confidence)

        self.vocabulary.register(concept, value, metadata={"confidence": confidence})
        activation_map = self._activate_mesh(tag)

        drift_score = sum(agent.driftScore for agent in self.agents.values()) / len(self.agents)
        affect_delta = sum(agent.affect_delta for agent in self.agents.values()) / len(self.agents)

        return {
            "tag": tag.serialize(),
            "activation": activation_map,
            "driftScore": drift_score,
            "affect_delta": affect_delta,
        }

    def _activate_mesh(self, tag: Tag) -> dict[str, float]:
        activation: dict[str, float] = {}
        base_signal = tag.confidence

        for agent_id, agent in self.agents.items():
            neighbor_signal = (
                sum(self.agents[n].resonance for n in agent.neighbors) / max(1, len(agent.neighbors))
                if agent.neighbors
                else base_signal
            )
            signal = (base_signal + neighbor_signal) / 2
            activation[agent_id] = agent.activate(signal)

        return activation

    # ΛTAG: glyph_consensus
    def reach_consensus(self, proposal: Any) -> ConsensusResult:
        """Reach consciousness consensus across colony using GLYPH communication."""

        weights = {agent_id: agent.resonance for agent_id, agent in self.agents.items()}
        weight_sum = sum(weights.values()) or 1.0
        confidence = min(1.0, weight_sum / len(weights))

        votes = {
            agent_id: ("approve" if resonance >= 0.5 else "observe") for agent_id, resonance in weights.items()
        }

        decision_payload = {"proposal": proposal, "weights": weights}
        participation = sum(1 for resonance in weights.values() if resonance > 0.2) / len(weights)

        return ConsensusResult(
            consensus_reached=confidence >= 0.5,
            decision=decision_payload,
            confidence=confidence,
            votes=votes,
            participation_rate=participation,
        )

    # ΛTAG: belief_propagation
    async def propagate_belief(self, initial_belief: dict[str, Any]) -> dict[str, float]:
        belief_states = {agent_id: 0.0 for agent_id in self.agents}
        strength = float(initial_belief.get("strength", 0.5))
        concept = initial_belief.get("concept", "UNKNOWN")
        value = initial_belief.get("value", concept.lower())

        self.vocabulary.register(concept, value, metadata={"source": "propagation"})

        if self.belief_network and len(self.agents) > 1:
            centrality = nx.degree_centrality(self.belief_network)
        else:
            centrality = {agent_id: 1.0 for agent_id in self.agents}

        seed_agent = max(centrality, key=centrality.get)
        belief_states[seed_agent] = strength
        belief_tag = Tag(key=concept, value=value, scope=TagScope.GLOBAL, confidence=strength)

        iterations = max(1, int(initial_belief.get("iterations", 1)))
        for iteration in range(iterations):
            new_states: dict[str, float] = {}
            for agent_id, agent in self.agents.items():
                neighbor_values = [belief_states[n] for n in agent.neighbors]
                neighbor_influence = sum(neighbor_values) / max(1, len(neighbor_values))
                decay = 0.85
                new_value = min(1.0, decay * belief_states[agent_id] + (1 - decay) * neighbor_influence)
                if agent_id == seed_agent:
                    new_value = min(1.0, max(new_value, strength))
                new_states[agent_id] = new_value

            belief_states = new_states
            self.propagation_history.append(
                {
                    "iteration": iteration,
                    "belief_distribution": belief_states.copy(),
                    "tag": belief_tag.serialize(),
                }
            )

        return belief_states

    def _get_agent_neighbors(self, agent_id: str) -> Iterable[str]:
        return self.agents.get(agent_id, ConsciousnessAgent(agent_id)).neighbors

    def _get_agent_distance(self, a: str, b: str) -> float:
        if a == b:
            return 0.0
        if self.belief_network and nx:
            try:
                return float(nx.shortest_path_length(self.belief_network, a, b))
            except Exception:
                return math.inf
        return 1.0
