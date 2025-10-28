"""Symbolic colony orchestration for consciousness mesh propagation."""

from __future__ import annotations

import logging
from importlib import import_module, util
from typing import Any, Callable

import networkx as nx

from core.colonies import (
    BaseColony,
    ConsensusResult,
    MeshTopologyService,
    Tag,
    TagScope,
    get_mesh_topology_service,
)

logger = logging.getLogger(__name__)

_VOCAB_MODULE_CANDIDATES: tuple[str, ...] = (
    "core.symbolic_core.vocabularies",
    "lukhas.core.symbolic_core.vocabularies",
    "labs.core.symbolic_core.vocabularies",
)


def _resolve_symbolic_vocabulary() -> type:
    """Resolve the active SymbolicVocabulary implementation with deterministic fallback."""

    for module_name in _VOCAB_MODULE_CANDIDATES:
        if util.find_spec(module_name) is None:
            continue

        module = import_module(module_name)
        vocabulary_cls = getattr(module, "SymbolicVocabulary", None)
        if vocabulary_cls is not None:
            return vocabulary_cls

    logger.warning("SymbolicVocabulary not available, using fallback implementation")

    class _FallbackSymbolicVocabulary:
        """Fallback vocabulary implementation for consciousness development."""

        def __init__(self) -> None:
            self.vocabulary: dict[str, dict[str, Any]] = {}

        def register(self, concept: str, payload: dict[str, Any]) -> None:
            self.vocabulary[concept] = payload

    return _FallbackSymbolicVocabulary


SymbolicVocabulary = _resolve_symbolic_vocabulary()


def _register_symbolic_concept(
    vocabulary: Any,
    tag: Tag,
    *,
    metadata_factory: Callable[[Tag], dict[str, Any]] | None = None,
) -> None:
    """Record a symbolic concept within the active vocabulary."""

    payload = {
        "value": tag.value,
        "confidence": tag.confidence,
        "last_colony": tag.metadata.get("colony_id"),
    }
    if metadata_factory is not None:
        payload.update(metadata_factory(tag))

    if hasattr(vocabulary, "register"):
        vocabulary.register(tag.key, payload)
    else:
        vocab_store = getattr(vocabulary, "vocabulary", None)
        if isinstance(vocab_store, dict):
            vocab_store[tag.key] = payload


class SymbolicReasoningColony(BaseColony):
    """Colony for symbolic reasoning and belief propagation."""

    def __init__(
        self,
        colony_id: str,
        agent_count: int = 3,
        *,
        mesh_service: MeshTopologyService | None = None,
    ) -> None:
        super().__init__(colony_id, capabilities=["symbolic_reasoning"])
        self.vocabulary = SymbolicVocabulary()
        self.mesh_service: MeshTopologyService = mesh_service or get_mesh_topology_service()
        self.belief_network = nx.DiGraph()
        self.propagation_history: list[dict[str, Any]] = []
        self.processing_history: list[dict[str, Any]] = []

        self._initialize_mesh_agents(agent_count)

    def _initialize_mesh_agents(self, agent_count: int) -> None:
        """Register deterministic mesh agents and activate the colony."""

        if agent_count <= 0:
            logger.warning(
                "SymbolicReasoningColony requested with no agents; defaulting to one agent"
            )
            agent_count = 1

        for index in range(agent_count):
            mesh_agent = self.mesh_service.register_agent(
                node_type="symbolic_reasoning",
                capabilities=["belief_propagation", "symbolic_inference"],
                metadata={
                    "colony_id": self.colony_id,
                    "node_index": index,
                },
            )

            # ΛTAG: mesh_registry - persist deterministic mesh agent linkage
            self.register_agent(
                mesh_agent.agent_id,
                {
                    "mesh_agent": mesh_agent,
                    "node_type": mesh_agent.node_type,
                    "capabilities": mesh_agent.capabilities,
                },
            )
            self.belief_network.add_node(mesh_agent.agent_id, belief=0.0)

        if not self.state["active"]:
            self.activate()

        logger.info(
            "Colony %s initialized with %d agents from mesh registry",
            self.colony_id,
            len(self.agents),
        )

    def process(self, task: Any) -> dict[str, Any]:
        """Process a consciousness task using GLYPH symbolic reasoning"""
        # Track processing metrics
        self.state["processing_count"] += 1

        if not self.state["active"]:
            self.activate()

        # Update drift based on processing complexity
        drift_delta = 0.0
        affect_total = 0.01 * len(self.agents) if self.agents else 0.0
        concept_tags: list[str] = []

        if isinstance(task, dict):
            complexity = float(task.get("complexity", 0.0))
            drift_delta = max(0.0, min(1.0, complexity * 0.01))
            self.update_drift_score(drift_delta)

            if "affect_delta" in task:
                affect_total = float(task["affect_delta"])
            affect_total = max(0.0, affect_total)

            concept = task.get("concept")
            if concept:
                confidence = float(task.get("confidence", 0.8))
                confidence = max(0.0, min(1.0, confidence))
                tag = Tag(
                    key=str(concept),
                    value=task.get("value"),
                    scope=TagScope.COLONY,
                    confidence=confidence,
                    metadata={
                        "source": "process",
                        "colony_id": self.colony_id,
                        "processing_count": self.state["processing_count"],
                    },
                )
                # ΛTAG: concept_trace - capture concept drift-safe lineage
                self.add_tag(tag)
                concept_tags.append(tag.key)
                _register_symbolic_concept(self.vocabulary, tag)
                self.belief_network.add_node(tag.key, confidence=confidence)
                for agent_id in self.agents:
                    self.belief_network.add_edge(agent_id, tag.key, weight=confidence)

        # Synchronize metrics with mesh topology service
        affect_step = affect_total / len(self.agents) if self.agents else 0.0
        for agent_id, agent_data in self.agents.items():
            if "mesh_agent" in agent_data:
                self.mesh_service.update_agent_metrics(
                    agent_id,
                    drift_delta=drift_delta / len(self.agents) if self.agents else 0.0,
                    affect_delta=affect_step,
                )

        # Create consciousness processing result with mesh metadata
        activation_level = min(1.0, self.drift_score + affect_total)
        mesh_metrics = self.mesh_service.get_mesh_metrics()
        # ΛTAG: activation_metrics - expose deterministic activation telemetry
        result = {
            "task": task,
            "processed": True,
            "colony_id": self.colony_id,
            "mesh_generation": self.mesh_generation,
            "agent_count": len(self.agents),
            "drift_score": self.drift_score,
            "driftScore": self.drift_score,
            "mesh_metrics": mesh_metrics,
            "activation": self.state["active"],
            "activation_metrics": {
                "level": activation_level,
                "processing_count": self.state["processing_count"],
            },
            "affect_propagated": affect_total,
            "tags_applied": concept_tags,
        }

        # ΛTAG: driftScore - record processing snapshot for determinism analysis
        self.processing_history.append(
            {
                "task": task,
                "drift_delta": drift_delta,
                "affect_total": affect_total,
                "activation_level": activation_level,
                "mesh_snapshot": mesh_metrics,
            }
        )

        logger.debug(f"Consciousness task processed by colony {self.colony_id}")
        return result

    def reach_consensus(self, proposal: Any) -> ConsensusResult:
        """Reach consciousness consensus across colony using GLYPH communication"""
        # Calculate participation from active agents
        total_agents = len(self.agents)
        participating_agents = total_agents  # All agents participate in current implementation

        participation_rate = participating_agents / total_agents if total_agents > 0 else 0.0

        # Simulate voting across consciousness nodes
        votes = {agent_id: "approved" for agent_id in self.agents.keys()}

        # Update affect_delta based on consensus formation
        affect_change = 0.1 * participation_rate
        self.update_affect_delta(affect_change)

        # Synchronize consensus affect_delta with mesh topology
        for agent_id in self.agents.keys():
            self.mesh_service.update_agent_metrics(
                agent_id,
                drift_delta=0.0,
                affect_delta=affect_change / len(self.agents)
            )

        return ConsensusResult(
            consensus_reached=True,
            decision=proposal,
            confidence=0.8,
            votes=votes,
            participation_rate=participation_rate,
            drift_score=self.drift_score,
            affect_delta=self.affect_delta
        )

    async def propagate_belief(self, initial_belief: dict[str, Any]) -> dict[str, float]:
        belief_states = dict.fromkeys(self.agents, 0.0)
        if self.agents:
            seed_agent = next(iter(self.agents.keys()))
            belief_strength = initial_belief["strength"]
            belief_states[seed_agent] = belief_strength
            self.belief_network.add_node(seed_agent, belief=belief_strength)
            belief_tag = Tag(
                key=initial_belief["concept"],
                value=initial_belief["value"],
                scope=TagScope.GLOBAL,
                confidence=initial_belief["strength"],
            )
        else:
            belief_tag = None

        for iteration in range(initial_belief.get("iterations", 1)):
            new_states = {}
            for agent_id in belief_states:
                neighbors = self._get_agent_neighbors(agent_id)
                total_influence = 0.0
                for n in neighbors:
                    distance = self._get_agent_distance(agent_id, n)
                    total_influence += belief_states.get(n, 0) / (1 + distance)
                decay = 0.9
                new_belief = decay * belief_states[agent_id] + (1 - decay) * total_influence
                new_states[agent_id] = min(1.0, new_belief)
                if belief_tag and new_belief > 0.1:
                    # ΛTAG: belief_adoption - synchronize symbolic adoption across agents
                    adoption_tag = Tag(
                        key=belief_tag.key,
                        value=belief_tag.value,
                        scope=TagScope.MESH,
                        confidence=min(1.0, new_belief),
                        metadata={
                            "source_agent": agent_id,
                            "iteration": iteration,
                            "colony_id": self.colony_id,
                        },
                    )
                    self.add_tag(adoption_tag)
                    _register_symbolic_concept(self.vocabulary, adoption_tag)
                    self.belief_network.add_edge(agent_id, adoption_tag.key, weight=new_belief)
            belief_states = new_states
            self.propagation_history.append(
                {
                    "iteration": iteration,
                    "belief_distribution": belief_states.copy(),
                }
            )
        return belief_states

    def _get_agent_neighbors(self, agent_id: str) -> list[str]:
        return [a for a in self.agents if a != agent_id]

    def _get_agent_distance(self, a: str, b: str) -> float:
        return 1.0
