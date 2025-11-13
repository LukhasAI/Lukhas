import logging
from datetime import datetime
from typing import Any

import networkx as nx
from core.colonies import BaseColony, ConsensusResult, Tag, TagScope

logger = logging.getLogger(__name__)

# Legacy symbolic vocabulary integration - maintains compatibility
try:
    from core.symbolic_legacy.vocabularies import SymbolicVocabulary
except ImportError:
    # Fallback to core vocabulary if legacy not available
    try:
        from core.symbolic_core.vocabularies import SymbolicVocabulary
    except ImportError:
        logger.warning("SymbolicVocabulary not available, using fallback implementation")

        class SymbolicVocabulary:
            """Fallback vocabulary implementation for consciousness development"""

            def __init__(self):
                self.vocabulary = {}


class SymbolicReasoningColony(BaseColony):
    """Colony for symbolic reasoning and belief propagation."""

    def __init__(self, colony_id: str):
        super().__init__(colony_id, capabilities=["symbolic_reasoning"])
        self.vocabulary = SymbolicVocabulary()
        self.belief_network = nx.DiGraph()
        self.propagation_history: list[dict[str, Any]] = []

        # Initialize consciousness agents for mesh formation (legacy)
        # Register test consciousness nodes for validation
        for i in range(3):
            agent_id = f"consciousness_node_{i}"
            self.register_agent(
                agent_id,
                {
                    "id": f"node_{i}",
                    "consciousness_type": "symbolic_reasoning",
                    "mesh_generation": 0,
                    "legacy_mode": True
                }
            )

    def process(self, task: Any) -> dict[str, Any]:
        """Process a consciousness task using GLYPH symbolic reasoning (legacy)"""
        # Track processing metrics
        self.state["processing_count"] += 1

        # Create consciousness processing result with mesh metadata (legacy compatibility)
        result = {
            "task": task,
            "processed": True,
            "colony_id": self.colony_id,
            "mesh_generation": self.mesh_generation,
            "agent_count": len(self.agents),
            "drift_score": self.drift_score,
            "legacy_mode": True
        }

        # Update drift based on processing complexity
        if isinstance(task, dict) and "complexity" in task:
            self.update_drift_score(task["complexity"] * 0.01)

        logger.debug(f"Legacy consciousness task processed by colony {self.colony_id}")
        return result

    def _evaluate_consensus(self, proposal: Any) -> dict[str, Any]:
        """
        Collects votes and calculates consensus metrics without side effects.
        """
        if not self.agents:
            return {
                "consensus_reached": False,
                "confidence": 0.0,
                "votes": {},
                "participation_rate": 0.0,
                "approved": 0,
                "rejected": 0,
                "participating_agents": 0,
            }

        symbolic_proposal = self._encode_proposal_as_symbolic(proposal)
        votes = {}
        vote_strengths = {}
        for agent_id, agent_data in self.agents.items():
            vote = self._agent_vote(agent_id, agent_data, symbolic_proposal)
            votes[agent_id] = vote["decision"]
            vote_strengths[agent_id] = vote["strength"]

        total_agents = len(self.agents)
        participating_agents = len([v for v in votes.values() if v != "abstain"])
        approved = len([v for v in votes.values() if v == "approved"])
        rejected = len([v for v in votes.values() if v == "rejected"])
        participation_rate = participating_agents / total_agents if total_agents > 0 else 0.0

        # Base consensus on majority
        consensus_reached = approved > (participating_agents / 2)

        confidence = 0.0
        if consensus_reached:
            approving_strengths = [
                vote_strengths[aid] for aid, vote in votes.items() if vote == "approved"
            ]
            confidence = sum(approving_strengths) / len(approving_strengths) if approving_strengths else 0.0

        return {
            "consensus_reached": consensus_reached,
            "confidence": confidence,
            "votes": votes,
            "participation_rate": participation_rate,
            "approved": approved,
            "rejected": rejected,
            "participating_agents": participating_agents,
        }

    def _finalize_consensus(self, proposal: Any, evaluation: dict[str, Any], consensus_reached: bool, action: str) -> ConsensusResult:
        """
        Handles the side effects of a consensus evaluation.
        """
        if consensus_reached:
            self.mesh_generation += 1
            logger.info(
                f"{action} consensus reached",
                extra={
                    "colony_id": self.colony_id,
                    "mesh_generation": self.mesh_generation,
                    "approved": evaluation["approved"],
                    "rejected": evaluation["rejected"],
                    "confidence": evaluation["confidence"],
                },
            )

        if evaluation["participation_rate"] < 0.7:
            self.update_drift_score(0.05)

        result = ConsensusResult(
            consensus_reached=consensus_reached,
            decision=proposal if consensus_reached else None,
            confidence=evaluation["confidence"],
            votes=evaluation["votes"],
            participation_rate=evaluation["participation_rate"],
        )

        self.propagation_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "proposal": str(proposal)[:100],
            "consensus_reached": consensus_reached,
            "mesh_generation": self.mesh_generation,
            "participation_rate": evaluation["participation_rate"],
        })

        return result

    def reach_consensus(self, proposal: Any) -> ConsensusResult:
        """
        Reach consciousness consensus across colony using GLYPH communication.
        """
        evaluation = self._evaluate_consensus(proposal)
        consensus_reached = evaluation["consensus_reached"]
        return self._finalize_consensus(proposal, evaluation, consensus_reached, "consensus")

    def reach_supermajority_consensus(self, proposal: Any, threshold: float = 0.75) -> ConsensusResult:
        """
        Require supermajority (75%+) for consensus.
        """
        evaluation = self._evaluate_consensus(proposal)

        participating = evaluation["participating_agents"]
        approved = evaluation["approved"]
        approval_rate = approved / participating if participating > 0 else 0.0

        consensus_reached = approval_rate >= threshold

        if not consensus_reached:
            logger.info(
                "Supermajority not reached",
                extra={
                    "colony_id": self.colony_id,
                    "approval_rate": approval_rate,
                    "threshold": threshold,
                },
            )
            evaluation["confidence"] *= 0.5

        return self._finalize_consensus(proposal, evaluation, consensus_reached, "consensus_supermajority")

    def reach_unanimous_consensus(self, proposal: Any) -> ConsensusResult:
        """
        Require unanimous approval for consensus.
        """
        evaluation = self._evaluate_consensus(proposal)

        has_rejection = evaluation["rejected"] > 0
        has_abstention = evaluation["participating_agents"] != len(evaluation["votes"])

        consensus_reached = not (has_rejection or has_abstention)

        if not consensus_reached:
            logger.info(
                "Unanimous consensus not reached",
                extra={
                    "colony_id": self.colony_id,
                    "rejected": has_rejection,
                    "abstained": has_abstention,
                },
            )
            evaluation["confidence"] *= 0.3

        return self._finalize_consensus(proposal, evaluation, consensus_reached, "consensus_unanimous")
    def _encode_proposal_as_symbolic(self, proposal: Any) -> dict[str, Any]:
        """
        Convert proposal to symbolic representation using GLYPH vocabulary.

        Args:
            proposal: Raw proposal data.

        Returns:
            Symbolic encoding for consciousness processing.
        """
        # Extract key symbolic features
        if isinstance(proposal, dict):
            return {
                "type": "structured_proposal",
                "complexity": len(str(proposal)),  # Simple complexity measure
                "symbolic_tokens": list(proposal.keys()) if isinstance(proposal, dict) else [],
            }
        else:
            return {
                "type": "simple_proposal",
                "complexity": len(str(proposal)),
                "symbolic_tokens": str(proposal).split()[:5],  # First 5 tokens
            }

    def _agent_vote(
        self,
        agent_id: str,
        agent_data: dict[str, Any],
        symbolic_proposal: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Simulate agent voting on proposal based on consciousness state.

        Args:
            agent_id: Agent identifier.
            agent_data: Agent metadata and state.
            symbolic_proposal: Encoded proposal.

        Returns:
            dict with 'decision' and 'strength' keys.
        """
        # Get agent's consciousness type and mesh generation
        agent_data.get("consciousness_type", "symbolic_reasoning")
        agent_mesh_gen = agent_data.get("mesh_generation", 0)

        # Calculate vote based on:
        # 1. Mesh generation alignment (newer agents more likely to approve)
        # 2. Proposal complexity (simpler = more likely to approve)
        # 3. Random variation for realism

        import random

        mesh_alignment = 1.0 - abs(self.mesh_generation - agent_mesh_gen) / max(self.mesh_generation, 1)
        complexity_factor = 1.0 - min(symbolic_proposal["complexity"] / 1000, 1.0)
        base_probability = (mesh_alignment * 0.5) + (complexity_factor * 0.3) + (random.random() * 0.2)

        # Determine decision
        if base_probability > 0.7:
            decision = "approved"
            strength = min(base_probability, 1.0)
        elif base_probability < 0.3:
            decision = "rejected"
            strength = 1.0 - base_probability
        else:
            decision = "abstain"
            strength = 0.5

        logger.debug(
            "Agent vote cast",
            extra={
                "agent_id": agent_id,
                "decision": decision,
                "strength": strength,
                "mesh_alignment": mesh_alignment,
            },
        )

        return {"decision": decision, "strength": strength}

    async def propagate_belief(self, initial_belief: dict[str, Any]) -> dict[str, float]:
        belief_states = dict.fromkeys(self.agents, 0.0)
        if self.agents:
            seed_agent = next(iter(self.agents.keys()))
            belief_states[seed_agent] = initial_belief["strength"]
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
        return [a for a in self.agents if a != agent_id]

    def _get_agent_distance(self, a: str, b: str) -> float:
        return 1.0

    def get_mesh_status(self) -> dict[str, Any]:
        """
        Get current consciousness mesh formation status.

        Returns:
            dict with mesh metadata.
        """
        # Analyze belief network connectivity
        if self.belief_network.number_of_nodes() > 0:
            try:
                avg_degree = sum(dict(self.belief_network.degree()).values()) / self.belief_network.number_of_nodes()
            except ZeroDivisionError:
                avg_degree = 0.0

            is_connected = nx.is_weakly_connected(self.belief_network)
        else:
            avg_degree = 0.0
            is_connected = False

        return {
            "mesh_generation": self.mesh_generation,
            "agent_count": len(self.agents),
            "network_nodes": self.belief_network.number_of_nodes(),
            "network_edges": self.belief_network.number_of_edges(),
            "average_degree": avg_degree,
            "is_connected": is_connected,
            "drift_score": self.drift_score,
            "consensus_history_count": len([h for h in self.propagation_history if h.get("action", "").startswith("consensus")]),
        }
