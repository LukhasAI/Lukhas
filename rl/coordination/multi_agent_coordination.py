"""
Multi-Agent Coordination for MΛTRIZ RL Consciousness Systems
===========================================================

This module provides coordination mechanisms for distributed consciousness agents
in the LUKHAS AI RL system. Used by advanced testing suite for coordination testing.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class CoordinationStrategy(Enum):
    """Strategies for coordinating multiple consciousness agents"""

    CONSENSUS = "consensus"  # Require agreement between agents
    MAJORITY = "majority"  # Use majority decision
    HIERARCHICAL = "hierarchical"  # Use authority-based decisions
    COLLABORATIVE = "collaborative"  # Equal collaboration
    COMPETITIVE = "competitive"  # Competitive coordination


@dataclass
class AgentProfile:
    """Profile for a consciousness agent in coordination system"""

    agent_id: str
    agent_type: str
    specialization: str
    authority_level: float = 1.0
    performance_score: float = 0.5
    last_seen: Optional[datetime] = None

    def __post_init__(self):
        if self.last_seen is None:
            self.last_seen = datetime.now(timezone.utc)


@dataclass
class CoordinationDecision:
    """Decision made through multi-agent coordination"""

    decision_id: str
    decision_type: str
    participating_agents: list[str]
    strategy_used: CoordinationStrategy
    consensus_level: float
    final_decision: Any
    timestamp: datetime

    def __post_init__(self):
        if not hasattr(self, "timestamp") or self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class MultiAgentCoordination:
    """Coordinates decisions between multiple consciousness agents"""

    def __init__(self, strategy: CoordinationStrategy = CoordinationStrategy.CONSENSUS):
        self.strategy = strategy
        self.agents: dict[str, AgentProfile] = {}
        self.decisions: list[CoordinationDecision] = []

    def register_agent(self, agent: AgentProfile) -> bool:
        """Register an agent for coordination"""
        self.agents[agent.agent_id] = agent
        return True

    def coordinate_decision(self, decision_type: str, agent_proposals: dict[str, Any]) -> CoordinationDecision:
        """Coordinate a decision between multiple agents"""

        # Simple coordination logic for testing
        participating_agents = list(agent_proposals.keys())

        if self.strategy == CoordinationStrategy.CONSENSUS:
            # Require unanimous agreement (simplified)
            values = list(agent_proposals.values())
            consensus_level = 1.0 if len({str(v) for v in values}) == 1 else 0.0
            final_decision = values[0] if consensus_level == 1.0 else None

        elif self.strategy == CoordinationStrategy.MAJORITY:
            # Use majority decision
            from collections import Counter

            values = list(agent_proposals.values())
            value_counts = Counter(str(v) for v in values)
            most_common = value_counts.most_common(1)[0]
            consensus_level = most_common[1] / len(values)
            final_decision = most_common[0] if consensus_level > 0.5 else None

        else:
            # Default: use first proposal
            consensus_level = 0.5
            final_decision = next(iter(agent_proposals.values())) if agent_proposals else None

        decision = CoordinationDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=decision_type,
            participating_agents=participating_agents,
            strategy_used=self.strategy,
            consensus_level=consensus_level,
            final_decision=final_decision,
            timestamp=datetime.now(timezone.utc),
        )

        self.decisions.append(decision)
        return decision

    def get_agent_performance(self, agent_id: str) -> Optional[float]:
        """Get performance score for an agent"""
        agent = self.agents.get(agent_id)
        return agent.performance_score if agent else None

    def update_agent_performance(self, agent_id: str, score: float) -> bool:
        """Update performance score for an agent"""
        if agent_id in self.agents:
            self.agents[agent_id].performance_score = score
            return True
        return False

    def get_coordination_stats(self) -> dict[str, Any]:
        """Get statistics about coordination performance"""
        if not self.decisions:
            return {"total_decisions": 0, "average_consensus": 0.0}

        total_decisions = len(self.decisions)
        average_consensus = sum(d.consensus_level for d in self.decisions) / total_decisions

        return {
            "total_decisions": total_decisions,
            "average_consensus": average_consensus,
            "strategy": self.strategy.value,
            "active_agents": len(self.agents),
        }


# Mock classes for testing compatibility
class ConsciousnessAgent:
    """Mock consciousness agent for testing"""

    def __init__(self, agent_id: str, specialization: str = "general"):
        self.agent_id = agent_id
        self.specialization = specialization
        self.coordination = MultiAgentCoordination()

    def propose_decision(self, decision_type: str, proposal: Any) -> Any:
        """Propose a decision for coordination"""
        return proposal

    def evaluate_proposal(self, proposal: Any) -> float:
        """Evaluate a proposal from another agent"""
        return 0.5  # Neutral evaluation


# Export main classes
__all__ = [
    "AgentProfile",
    "ConsciousnessAgent",
    "CoordinationDecision",
    "CoordinationStrategy",
    "MultiAgentCoordination",
]
