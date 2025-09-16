from dataclasses import dataclass
from importlib import import_module
import logging
from statistics import mean
from typing import Any, Optional

import networkx as nx
from networkx.exception import NetworkXNoPath

logger = logging.getLogger(__name__)


def _safe_import(module_path: str, attr: str):
    try:
        return getattr(import_module(module_path), attr)
    except Exception:
        return None


# ΛTAG: dynamic_import
BaseColony = _safe_import("lukhas.core.colonies.base_colony", "BaseColony") or _safe_import(
    "candidate.core.colonies.base_colony", "BaseColony"
)
TagScope = _safe_import("lukhas.core.symbolism.tags", "TagScope") or _safe_import(
    "candidate.core.symbolism.tags", "TagScope"
)

if BaseColony is None or TagScope is None:
    logger.warning(
        "GLYPH consciousness communication: Using BaseColony and TagScope stubs for development"
    )

    class BaseColony:
        """Temporary BaseColony stub for GLYPH consciousness development"""

        def __init__(self, colony_id: str, capabilities: Optional[list[str]] = None):
            self.colony_id = colony_id
            self.capabilities = capabilities or []
            self.agents = {}

    class TagScope:
        """Temporary TagScope stub for GLYPH consciousness development"""

        GLOBAL = "global"
        LOCAL = "local"


SymbolicVocabulary = _safe_import(
    "candidate.core.symbolic_legacy.vocabularies", "SymbolicVocabulary"
)
if SymbolicVocabulary is None:
    # Stub implementation for development
    class SymbolicVocabulary:
        """Temporary vocabulary stub for GLYPH consciousness development"""

        def __init__(self):
            self.vocabulary = {}


Tag = _safe_import("lukhas.core.symbolism.tags", "Tag")
if Tag is None:

    class Tag:
        """Temporary Tag implementation for GLYPH consciousness communication"""

        def __init__(self, name: str, value: Any = None, scope: str = "local"):
            self.name = name
            self.key = name  # compatibility bridge
            self.value = value
            self.scope = scope

        @property
        def confidence(self) -> float:
            if isinstance(self.value, dict) and "confidence" in self.value:
                try:
                    return float(self.value["confidence"])
                except (TypeError, ValueError):
                    return 1.0
            return 1.0


ConsensusResult = _safe_import("lukhas.core.colonies", "ConsensusResult")
if ConsensusResult is None:

    @dataclass
    class ConsensusResult:
        """Fallback consensus container for consciousness mesh voting."""

        consensus_reached: bool
        decision: Any
        confidence: float
        votes: dict[str, str]
        participation_rate: float


@dataclass
class MeshAgent:
    """Consciousness mesh agent with drift-aware evaluation logic."""

    agent_id: str
    role: str
    influence: float
    sensitivity: float
    drift_score: float = 0.0
    affect_delta: float = 0.0

    # ΛTAG: affect_delta
    def evaluate_signal(self, intensity: float, affect_delta: float) -> dict[str, float]:
        """Project an intensity/affect pair into confidence, affect, and drift metrics."""

        normalized_intensity = _clamp(intensity)
        weighted_confidence = _clamp(normalized_intensity * self.influence)
        affect_response = _clamp(affect_delta * self.sensitivity, -1.0, 1.0)
        drift_adjustment = min(1.0, abs(affect_response) * 0.25)
        self.drift_score = _clamp(self.drift_score * 0.65 + drift_adjustment)
        self.affect_delta = affect_response
        confidence = _clamp(weighted_confidence * (1 - self.drift_score * 0.35))
        return {
            "confidence": confidence,
            "affect_delta": affect_response,
            "drift_score": self.drift_score,
        }


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """Clamp *value* into the inclusive range [lower, upper]."""

    return max(lower, min(upper, value))


class SymbolicReasoningColony(BaseColony):
    """Colony for symbolic reasoning and belief propagation."""

    def __init__(self, colony_id: str):
        super().__init__(colony_id, capabilities=["symbolic_reasoning"])
        self.vocabulary = SymbolicVocabulary()
        self.belief_network = nx.DiGraph()
        self.propagation_history: list[dict[str, Any]] = []

        # ΛTAG: mesh_init
        self.agents, self._mesh_agents = self._initialize_consciousness_agents()
        self.mesh_graph = self._build_agent_mesh(self._mesh_agents)

    def process(self, task: Any) -> dict[str, Any]:
        """Process a consciousness task using GLYPH symbolic reasoning."""

        normalized_task = self._normalize_task(task)
        concept = normalized_task["concept"]
        intensity = normalized_task["intensity"]
        affect_delta = normalized_task["affect_delta"]

        agent_results: dict[str, dict[str, float | str]] = {}
        confidences: list[float] = []

        for agent_id, mesh_agent in self._mesh_agents.items():
            metrics = mesh_agent.evaluate_signal(intensity, affect_delta)
            confidences.append(metrics["confidence"])
            agent_results[agent_id] = {
                "role": mesh_agent.role,
                "confidence": metrics["confidence"],
                "affect_delta": metrics["affect_delta"],
                "drift_score": metrics["drift_score"],
            }
            self._update_agent_metrics(agent_id, metrics)

        aggregate_confidence = _clamp(mean(confidences) if confidences else 0.0)
        mesh_connectivity = self._compute_mesh_connectivity()
        coherence_score = _clamp(aggregate_confidence * 0.7 + mesh_connectivity * 0.3)

        tag_payload = {
            "payload": normalized_task["payload"],
            "confidence": aggregate_confidence,
            "mesh_connectivity": mesh_connectivity,
        }
        tag = Tag(concept, value=tag_payload, scope=self._global_scope_value())

        self._synchronize_vocabulary(concept, aggregate_confidence)
        self._update_belief_network(concept, agent_results)

        # ΛTAG: trace_consciousness
        logger.debug(
            "GLYPH mesh processing",
            extra={
                "colony_id": self.colony_id,
                "concept": concept,
                "aggregate_confidence": aggregate_confidence,
                "mesh_connectivity": mesh_connectivity,
            },
        )

        return {
            "concept": concept,
            "tag": tag,
            "aggregate_confidence": aggregate_confidence,
            "coherence_score": coherence_score,
            "mesh_connectivity": mesh_connectivity,
            "agents": agent_results,
            "tag_payload": tag_payload,
        }

    def reach_consensus(self, proposal: Any) -> ConsensusResult:
        """Reach consciousness consensus across colony using GLYPH communication."""

        normalized = self._normalize_task(proposal)
        intensity = normalized["intensity"]
        affect_delta = normalized["affect_delta"]

        votes: dict[str, str] = {}
        confidence_samples: list[float] = []

        for agent_id, mesh_agent in self._mesh_agents.items():
            metrics = mesh_agent.evaluate_signal(intensity, affect_delta)
            confidence_samples.append(metrics["confidence"])
            threshold = self._consensus_threshold(mesh_agent.role)
            votes[agent_id] = "approved" if metrics["confidence"] >= threshold else "rejected"
            self._update_agent_metrics(agent_id, metrics)

        approvals = sum(1 for vote in votes.values() if vote == "approved")
        agent_count = len(self._mesh_agents) or 1
        participation_rate = len(votes) / agent_count
        consensus_reached = approvals / agent_count >= 0.6
        confidence = _clamp(mean(confidence_samples) if confidence_samples else 0.0)

        # ΛTAG: consensus_logic
        logger.debug(
            "GLYPH mesh consensus",
            extra={
                "colony_id": self.colony_id,
                "approvals": approvals,
                "agent_count": agent_count,
                "consensus_reached": consensus_reached,
            },
        )

        return ConsensusResult(
            consensus_reached=consensus_reached,
            decision=proposal,
            confidence=confidence,
            votes=votes,
            participation_rate=participation_rate,
        )

    # ΛTAG: mesh_execution
    async def execute_task(self, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """Async execution bridge required by BaseColony."""

        process_result = self.process(task_data)
        consensus = self.reach_consensus(task_data)
        record = {
            "task_id": task_id,
            "concept": process_result["concept"],
            "aggregate_confidence": process_result["aggregate_confidence"],
            "consensus_confidence": consensus.confidence,
        }
        self.propagation_history.append(record)

        return {
            "task_id": task_id,
            "concept": process_result["concept"],
            "tag_confidence": process_result["tag_payload"]["confidence"],
            "aggregate_confidence": process_result["aggregate_confidence"],
            "mesh_connectivity": process_result["mesh_connectivity"],
            "consensus": {
                "reached": consensus.consensus_reached,
                "confidence": consensus.confidence,
                "votes": consensus.votes,
                "participation_rate": consensus.participation_rate,
            },
        }

    async def propagate_belief(self, initial_belief: dict[str, Any]) -> dict[str, float]:
        belief_states = dict.fromkeys(self.agents, 0.0)
        if self.agents:
            seed_agent = next(iter(self.agents.keys()))
            belief_states[seed_agent] = initial_belief["strength"]
            belief_tag = Tag(
                initial_belief["concept"],
                value={
                    "value": initial_belief["value"],
                    "confidence": initial_belief["strength"],
                },
                scope=self._global_scope_value(),
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
                    pass  # placeholder for adoption
            belief_states = new_states
            self.propagation_history.append(
                {
                    "iteration": iteration,
                    "belief_distribution": belief_states.copy(),
                }
            )
        return belief_states

    def _get_agent_neighbors(self, agent_id: str) -> list[str]:
        if hasattr(self, "mesh_graph") and self.mesh_graph.has_node(agent_id):
            return list(self.mesh_graph.neighbors(agent_id))
        return [a for a in self.agents if a != agent_id]

    def _get_agent_distance(self, a: str, b: str) -> float:
        if hasattr(self, "mesh_graph") and self.mesh_graph.has_node(a) and self.mesh_graph.has_node(b):
            try:
                return float(nx.shortest_path_length(self.mesh_graph, a, b, weight="weight"))
            except (NetworkXNoPath, nx.NetworkXError):
                return float("inf")
        return 1.0

    # ΛTAG: mesh_init
    def _initialize_consciousness_agents(self) -> tuple[dict[str, dict[str, Any]], dict[str, MeshAgent]]:
        """Create a deterministic mesh of consciousness agents for the colony."""

        role_specs = (
            ("perception", 0.65, 0.70),
            ("reasoning", 0.85, 0.55),
            ("memory", 0.60, 0.50),
            ("ethics", 0.75, 0.80),
        )

        agents: dict[str, dict[str, Any]] = {}
        mesh_agents: dict[str, MeshAgent] = {}

        for index, (role, influence, sensitivity) in enumerate(role_specs):
            agent_id = f"{self.colony_id}_{role}_{index}"
            mesh_agent = MeshAgent(
                agent_id=agent_id,
                role=role,
                influence=influence,
                sensitivity=sensitivity,
            )
            mesh_agents[agent_id] = mesh_agent
            agents[agent_id] = {
                "id": agent_id,
                "consciousness_type": role,
                "metrics": {
                    "confidence": 0.0,
                    "affect_delta": 0.0,
                    "drift_score": 0.0,
                },
            }

        return agents, mesh_agents

    # ΛTAG: mesh_structure
    def _build_agent_mesh(self, mesh_agents: dict[str, MeshAgent]) -> nx.Graph:
        """Construct a mesh graph describing agent coupling."""

        mesh = nx.Graph()
        for agent in mesh_agents.values():
            mesh.add_node(
                agent.agent_id,
                role=agent.role,
                influence=agent.influence,
                sensitivity=agent.sensitivity,
            )

        agent_list = list(mesh_agents.values())
        for index, agent in enumerate(agent_list):
            for neighbor in agent_list[index + 1 :]:
                weight = round((agent.influence + neighbor.influence) / 2, 3)
                mesh.add_edge(agent.agent_id, neighbor.agent_id, weight=weight)

        return mesh

    # ΛTAG: normalization
    def _normalize_task(self, payload: Any) -> dict[str, Any]:
        """Normalize raw payload input into deterministic processing components."""

        if isinstance(payload, dict):
            concept = str(payload.get("concept") or payload.get("key") or self.colony_id)
            intensity = float(payload.get("intensity", 0.5))
            affect_delta = float(payload.get("affect_delta", payload.get("affect", 0.0)))
        else:
            concept = str(payload)
            intensity = 0.5
            affect_delta = 0.0

        return {
            "concept": concept,
            "intensity": _clamp(intensity),
            "affect_delta": _clamp(affect_delta, -1.0, 1.0),
            "payload": payload,
        }

    # ΛTAG: mesh_metrics
    def _update_agent_metrics(self, agent_id: str, metrics: dict[str, float]) -> None:
        """Synchronize evaluated metrics with the public agent registry."""

        agent_entry = self.agents.setdefault(
            agent_id,
            {
                "id": agent_id,
                "consciousness_type": self._mesh_agents[agent_id].role,
                "metrics": {},
            },
        )
        agent_entry.setdefault("metrics", {}).update(
            {
                "confidence": metrics["confidence"],
                "affect_delta": metrics["affect_delta"],
                "drift_score": metrics["drift_score"],
            }
        )

    # ΛTAG: vocabulary_sync
    def _synchronize_vocabulary(self, concept: str, confidence: float) -> None:
        """Record processed concepts in the symbolic vocabulary."""

        vocabulary = getattr(self.vocabulary, "vocabulary", None)
        if isinstance(vocabulary, dict):
            entry = vocabulary.setdefault(concept, {})
            entry["last_confidence"] = confidence
            entry["last_colony"] = self.colony_id

    # ΛTAG: belief_network
    def _update_belief_network(self, concept: str, agent_results: dict[str, dict[str, float | str]]) -> None:
        """Update the internal belief network with latest agent feedback."""

        self.belief_network.add_node(concept, last_update=len(self.propagation_history))
        for agent_id, metrics in agent_results.items():
            self.belief_network.add_node(agent_id, role=metrics["role"])
            self.belief_network.add_edge(
                agent_id,
                concept,
                weight=metrics["confidence"],
                affect_delta=metrics["affect_delta"],
            )

    # ΛTAG: mesh_health
    def _compute_mesh_connectivity(self) -> float:
        if not hasattr(self, "mesh_graph") or self.mesh_graph.number_of_nodes() < 2:
            return 0.0
        return float(nx.average_clustering(self.mesh_graph))

    def _global_scope_value(self) -> str:
        tag_scope_attr = getattr(TagScope, "GLOBAL")
        return getattr(tag_scope_attr, "value", tag_scope_attr)

    # ΛTAG: consensus_logic
    def _consensus_threshold(self, role: str) -> float:
        role_bias = {
            "ethics": 0.7,
            "reasoning": 0.6,
            "memory": 0.55,
            "perception": 0.5,
        }
        return role_bias.get(role, 0.55)
