"""
Colony Consensus Mechanisms
===========================
Advanced consensus algorithms for multi-agent colony decision making.
Implements voting, confidence scoring, and hormone-based consensus.

Based on GPT5 audit recommendations and existing colony architecture.
"""

import asyncio
import logging
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

# Import our signal system
from candidate.orchestration.signals.signal_bus import Signal, SignalBus, SignalType

logger = logging.getLogger(__name__)


class ConsensusMethod(Enum):
    """Types of consensus methods"""

    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_VOTE = "weighted_vote"
    QUORUM = "quorum"
    BYZANTINE = "byzantine_fault_tolerant"
    HORMONE = "hormone_based"
    PROBABILISTIC = "probabilistic"
    EMERGENT = "emergent"


class VoteType(Enum):
    """Types of votes an agent can cast"""

    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    DELEGATE = "delegate"


@dataclass
class AgentVote:
    """A single agent's vote"""

    agent_id: str
    vote: VoteType
    confidence: float  # 0.0 to 1.0
    reasoning: str = ""
    delegated_to: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusProposal:
    """A proposal for colony consensus"""

    proposal_id: str
    content: Any
    proposer: str
    created_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    min_participation: float = 0.5
    required_confidence: float = 0.7
    method: ConsensusMethod = ConsensusMethod.WEIGHTED_VOTE
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusOutcome:
    """Result of a consensus process"""

    proposal_id: str
    decision: VoteType
    confidence: float
    participation_rate: float
    votes: list[AgentVote]
    method_used: ConsensusMethod
    hormone_levels: dict[str, float] = field(default_factory=dict)
    convergence_time: float = 0.0
    dissent_analysis: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_approved(self) -> bool:
        return self.decision == VoteType.APPROVE

    @property
    def is_unanimous(self) -> bool:
        return all(v.vote == self.decision for v in self.votes)


class ColonyConsensus:
    """
    Advanced consensus mechanisms for colony decision making.
    Supports multiple voting methods and hormone-based consensus.
    """

    def __init__(self, colony_id: str, signal_bus: Optional[SignalBus] = None):
        self.colony_id = colony_id
        self.signal_bus = signal_bus or SignalBus()

        # Agent registry
        self.agents: dict[str, dict[str, Any]] = {}
        self.agent_weights: dict[str, float] = {}

        # Consensus tracking
        self.active_proposals: dict[str, ConsensusProposal] = {}
        self.votes: dict[str, list[AgentVote]] = defaultdict(list)
        self.outcomes: dict[str, ConsensusOutcome] = {}

        # Hormone levels affect consensus
        self.hormone_levels = {
            "trust": 0.5,
            "urgency": 0.5,
            "stress": 0.3,
            "ambiguity": 0.3,
        }

        # Byzantine fault tolerance
        self.byzantine_threshold = 0.33  # Max faulty agents tolerated

    def register_agent(
        self,
        agent_id: str,
        weight: float = 1.0,
        capabilities: Optional[list[str]] = None,
    ):
        """Register an agent in the colony"""
        self.agents[agent_id] = {
            "weight": weight,
            "capabilities": capabilities or [],
            "reputation": 1.0,
            "vote_history": [],
        }
        self.agent_weights[agent_id] = weight
        logger.info(f"Registered agent {agent_id} with weight {weight}")

    async def propose(
        self,
        content: Any,
        proposer: str,
        method: ConsensusMethod = ConsensusMethod.WEIGHTED_VOTE,
        deadline_seconds: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Create a new consensus proposal"""
        proposal_id = f"{self.colony_id}_{len(self.active_proposals)}_{time.time()}"

        proposal = ConsensusProposal(
            proposal_id=proposal_id,
            content=content,
            proposer=proposer,
            method=method,
            deadline=(time.time() + deadline_seconds if deadline_seconds else None),
            **kwargs,
        )

        self.active_proposals[proposal_id] = proposal

        # Emit proposal signal
        await self._emit_signal(
            SignalType.NOVELTY,
            0.5,
            {"action": "proposal_created", "proposal_id": proposal_id},
        )

        logger.info(f"Created proposal {proposal_id} using {method.value}")
        return proposal_id

    async def vote(
        self,
        proposal_id: str,
        agent_id: str,
        vote: VoteType,
        confidence: float = 1.0,
        reasoning: str = "",
    ) -> bool:
        """Cast a vote on a proposal"""
        if proposal_id not in self.active_proposals:
            return False

        if agent_id not in self.agents:
            return False

        # Check deadline
        proposal = self.active_proposals[proposal_id]
        if proposal.deadline and time.time() > proposal.deadline:
            logger.warning(f"Vote rejected - proposal {proposal_id} expired")
            return False

        # Record vote
        agent_vote = AgentVote(
            agent_id=agent_id,
            vote=vote,
            confidence=confidence,
            reasoning=reasoning,
        )

        self.votes[proposal_id].append(agent_vote)

        # Update agent history
        self.agents[agent_id]["vote_history"].append(
            {
                "proposal": proposal_id,
                "vote": vote.value,
                "timestamp": time.time(),
            }
        )

        return True

    async def reach_consensus(self, proposal_id: str) -> ConsensusOutcome:
        """Execute consensus mechanism and determine outcome"""
        if proposal_id not in self.active_proposals:
            raise ValueError(f"Proposal {proposal_id} not found")

        proposal = self.active_proposals[proposal_id]
        votes = self.votes[proposal_id]

        start_time = time.time()

        # Choose consensus method
        if proposal.method == ConsensusMethod.MAJORITY_VOTE:
            outcome = await self._majority_vote_consensus(proposal, votes)
        elif proposal.method == ConsensusMethod.WEIGHTED_VOTE:
            outcome = await self._weighted_vote_consensus(proposal, votes)
        elif proposal.method == ConsensusMethod.QUORUM:
            outcome = await self._quorum_consensus(proposal, votes)
        elif proposal.method == ConsensusMethod.BYZANTINE:
            outcome = await self._byzantine_consensus(proposal, votes)
        elif proposal.method == ConsensusMethod.HORMONE:
            outcome = await self._hormone_consensus(proposal, votes)
        elif proposal.method == ConsensusMethod.PROBABILISTIC:
            outcome = await self._probabilistic_consensus(proposal, votes)
        elif proposal.method == ConsensusMethod.EMERGENT:
            outcome = await self._emergent_consensus(proposal, votes)
        else:
            outcome = await self._weighted_vote_consensus(proposal, votes)

        outcome.convergence_time = time.time() - start_time
        outcome.hormone_levels = self.hormone_levels.copy()

        # Store outcome
        self.outcomes[proposal_id] = outcome

        # Clean up
        del self.active_proposals[proposal_id]

        # Emit outcome signal
        await self._emit_signal(
            SignalType.TRUST if outcome.is_approved else SignalType.AMBIGUITY,
            outcome.confidence,
            {
                "action": "consensus_reached",
                "proposal_id": proposal_id,
                "decision": outcome.decision.value,
            },
        )

        return outcome

    async def _majority_vote_consensus(
        self, proposal: ConsensusProposal, votes: list[AgentVote]
    ) -> ConsensusOutcome:
        """Simple majority vote consensus"""
        vote_counts = defaultdict(int)

        for vote in votes:
            vote_counts[vote.vote] += 1

        total_votes = len(votes)
        participation_rate = total_votes / max(1, len(self.agents))

        # Find majority
        decision = max(vote_counts.items(), key=lambda x: x[1])[0]
        confidence = vote_counts[decision] / max(1, total_votes)

        return ConsensusOutcome(
            proposal_id=proposal.proposal_id,
            decision=decision,
            confidence=confidence,
            participation_rate=participation_rate,
            votes=votes,
            method_used=ConsensusMethod.MAJORITY_VOTE,
        )

    async def _weighted_vote_consensus(
        self, proposal: ConsensusProposal, votes: list[AgentVote]
    ) -> ConsensusOutcome:
        """Weighted vote consensus based on agent weights and confidence"""
        weighted_scores = defaultdict(float)
        total_weight = 0

        for vote in votes:
            agent_weight = self.agent_weights.get(vote.agent_id, 1.0)
            vote_weight = agent_weight * vote.confidence
            weighted_scores[vote.vote] += vote_weight
            total_weight += agent_weight

        participation_rate = len(votes) / max(1, len(self.agents))

        # Find highest weighted score
        decision = max(weighted_scores.items(), key=lambda x: x[1])[0]
        confidence = weighted_scores[decision] / max(1, total_weight)

        # Analyze dissent
        dissent_analysis = self._analyze_dissent(votes, decision)

        return ConsensusOutcome(
            proposal_id=proposal.proposal_id,
            decision=decision,
            confidence=confidence,
            participation_rate=participation_rate,
            votes=votes,
            method_used=ConsensusMethod.WEIGHTED_VOTE,
            dissent_analysis=dissent_analysis,
        )

    async def _hormone_consensus(
        self, proposal: ConsensusProposal, votes: list[AgentVote]
    ) -> ConsensusOutcome:
        """Hormone-based consensus using signal levels"""

        # Adjust votes based on hormone levels
        hormone_adjusted_votes = []

        for vote in votes:
            # Adjust confidence based on hormones
            adjusted_confidence = vote.confidence

            # High stress reduces confidence in risky decisions
            if self.hormone_levels["stress"] > 0.7:
                if vote.vote == VoteType.APPROVE:
                    adjusted_confidence *= 0.7

            # High trust increases confidence in approvals
            if self.hormone_levels["trust"] > 0.7:
                if vote.vote == VoteType.APPROVE:
                    adjusted_confidence *= 1.3

            # High ambiguity increases abstentions
            if self.hormone_levels["ambiguity"] > 0.7:
                if random.random() < 0.3:  # 30% chance to abstain
                    vote.vote = VoteType.ABSTAIN

            # High urgency speeds up decision
            if self.hormone_levels["urgency"] > 0.8:
                adjusted_confidence *= 1.5  # Boost all decisions

            adjusted_vote = AgentVote(
                agent_id=vote.agent_id,
                vote=vote.vote,
                confidence=min(1.0, adjusted_confidence),
                reasoning=f"{vote.reasoning} [hormone-adjusted]",
                timestamp=vote.timestamp,
            )
            hormone_adjusted_votes.append(adjusted_vote)

        # Use weighted consensus with adjusted votes
        outcome = await self._weighted_vote_consensus(proposal, hormone_adjusted_votes)
        outcome.method_used = ConsensusMethod.HORMONE

        return outcome

    async def _byzantine_consensus(
        self, proposal: ConsensusProposal, votes: list[AgentVote]
    ) -> ConsensusOutcome:
        """Byzantine fault-tolerant consensus"""

        # Identify potential faulty agents (low confidence, inconsistent history)
        faulty_agents = set()

        for vote in votes:
            agent = self.agents.get(vote.agent_id)
            if not agent:
                continue

            # Check for suspicious behavior
            if vote.confidence < 0.2:  # Very low confidence
                faulty_agents.add(vote.agent_id)
            elif len(agent["vote_history"]) > 10:
                # Check for random voting pattern
                history = agent["vote_history"][-10:]
                vote_types = [h["vote"] for h in history]
                if len(set(vote_types)) == len(vote_types):  # All different
                    faulty_agents.add(vote.agent_id)

        # Filter out faulty votes if within threshold
        faulty_ratio = len(faulty_agents) / max(1, len(self.agents))

        if faulty_ratio <= self.byzantine_threshold:
            # Can tolerate faults - filter them out
            filtered_votes = [v for v in votes if v.agent_id not in faulty_agents]
            logger.info(f"Filtered {len(faulty_agents)} potentially faulty votes")
        else:
            # Too many faults - use all votes but reduce confidence
            filtered_votes = votes
            logger.warning(f"Byzantine threshold exceeded: {faulty_ratio:.2%}")

        # Use weighted consensus on filtered votes
        outcome = await self._weighted_vote_consensus(proposal, filtered_votes)
        outcome.method_used = ConsensusMethod.BYZANTINE

        # Reduce confidence if many faults detected
        if faulty_ratio > 0.1:
            outcome.confidence *= 1 - faulty_ratio

        return outcome

    async def _emergent_consensus(
        self, proposal: ConsensusProposal, votes: list[AgentVote]
    ) -> ConsensusOutcome:
        """Emergent consensus through iterative refinement"""

        max_iterations = 5
        convergence_threshold = 0.9

        current_votes = votes.copy()

        for iteration in range(max_iterations):
            # Calculate current consensus
            vote_distribution = defaultdict(list)
            for vote in current_votes:
                vote_distribution[vote.vote].append(vote)

            # Find dominant opinion
            dominant_vote = max(vote_distribution.items(), key=lambda x: len(x[1]))[0]
            dominant_ratio = len(vote_distribution[dominant_vote]) / len(current_votes)

            if dominant_ratio >= convergence_threshold:
                # Consensus emerged
                break

            # Agents influenced by majority (simplified emergence)
            new_votes = []
            for vote in current_votes:
                if vote.vote != dominant_vote and random.random() < 0.2:
                    # 20% chance to switch to dominant
                    new_vote = AgentVote(
                        agent_id=vote.agent_id,
                        vote=dominant_vote,
                        confidence=vote.confidence * 0.8,  # Reduced confidence
                        reasoning=f"Converged to majority (iteration {iteration})",
                    )
                    new_votes.append(new_vote)
                else:
                    new_votes.append(vote)

            current_votes = new_votes

        # Final consensus
        outcome = await self._weighted_vote_consensus(proposal, current_votes)
        outcome.method_used = ConsensusMethod.EMERGENT

        return outcome

    async def _probabilistic_consensus(
        self, proposal: ConsensusProposal, votes: list[AgentVote]
    ) -> ConsensusOutcome:
        """Probabilistic consensus using Monte Carlo sampling"""

        num_samples = 1000
        outcomes = defaultdict(int)

        for _ in range(num_samples):
            # Sample votes based on confidence as probability
            sampled_decision = None
            for vote in votes:
                if random.random() < vote.confidence:
                    sampled_decision = vote.vote
                    break

            if sampled_decision:
                outcomes[sampled_decision] += 1

        # Find most likely outcome
        total_samples = sum(outcomes.values())
        decision = max(outcomes.items(), key=lambda x: x[1])[0]
        confidence = outcomes[decision] / max(1, total_samples)

        participation_rate = len(votes) / max(1, len(self.agents))

        return ConsensusOutcome(
            proposal_id=proposal.proposal_id,
            decision=decision,
            confidence=confidence,
            participation_rate=participation_rate,
            votes=votes,
            method_used=ConsensusMethod.PROBABILISTIC,
        )

    async def _quorum_consensus(
        self, proposal: ConsensusProposal, votes: list[AgentVote]
    ) -> ConsensusOutcome:
        """Quorum-based consensus requiring minimum participation"""

        participation_rate = len(votes) / max(1, len(self.agents))

        if participation_rate < proposal.min_participation:
            # Quorum not met
            return ConsensusOutcome(
                proposal_id=proposal.proposal_id,
                decision=VoteType.ABSTAIN,
                confidence=0.0,
                participation_rate=participation_rate,
                votes=votes,
                method_used=ConsensusMethod.QUORUM,
                dissent_analysis={"reason": "quorum_not_met"},
            )

        # Quorum met - use weighted consensus
        outcome = await self._weighted_vote_consensus(proposal, votes)
        outcome.method_used = ConsensusMethod.QUORUM

        return outcome

    def _analyze_dissent(
        self, votes: list[AgentVote], decision: VoteType
    ) -> dict[str, Any]:
        """Analyze dissenting votes"""
        dissent = []

        for vote in votes:
            if vote.vote != decision:
                dissent.append(
                    {
                        "agent": vote.agent_id,
                        "vote": vote.vote.value,
                        "confidence": vote.confidence,
                        "reasoning": vote.reasoning,
                    }
                )

        return {
            "dissent_count": len(dissent),
            "dissent_rate": len(dissent) / max(1, len(votes)),
            "dissenters": dissent[:5],  # Top 5 dissenters
        }

    def update_hormone_levels(self, hormone_updates: dict[str, float]):
        """Update hormone levels that affect consensus"""
        for hormone, level in hormone_updates.items():
            if hormone in self.hormone_levels:
                self.hormone_levels[hormone] = max(0.0, min(1.0, level))

    async def _emit_signal(self, signal_type: SignalType, level: float, metadata: dict):
        """Emit signal through signal bus"""
        if self.signal_bus:
            signal = Signal(
                name=signal_type,
                source=f"consensus_{self.colony_id}",
                level=level,
                metadata=metadata,
            )
            self.signal_bus.publish(signal)

    def get_consensus_history(self) -> list[dict[str, Any]]:
        """Get history of consensus outcomes"""
        history = []

        for proposal_id, outcome in self.outcomes.items():
            history.append(
                {
                    "proposal_id": proposal_id,
                    "decision": outcome.decision.value,
                    "confidence": outcome.confidence,
                    "participation": outcome.participation_rate,
                    "method": outcome.method_used.value,
                    "unanimous": outcome.is_unanimous,
                    "convergence_time": outcome.convergence_time,
                }
            )

        return history


# Demo usage


async def demo_consensus():
    """Demonstrate colony consensus mechanisms"""

    # Create consensus system
    consensus = ColonyConsensus("alpha-colony")

    # Register agents
    agents = ["agent_1", "agent_2", "agent_3", "agent_4", "agent_5"]
    for i, agent_id in enumerate(agents):
        consensus.register_agent(agent_id, weight=1.0 + i * 0.1)

    print("🏛️ Colony Consensus Demo")
    print("=" * 50)

    # Test different consensus methods
    methods = [
        ConsensusMethod.MAJORITY_VOTE,
        ConsensusMethod.WEIGHTED_VOTE,
        ConsensusMethod.HORMONE,
        ConsensusMethod.BYZANTINE,
        ConsensusMethod.EMERGENT,
    ]

    for method in methods:
        print(f"\n🗳️ Testing {method.value} consensus:")

        # Create proposal
        proposal_id = await consensus.propose(
            content="Should we increase processing resources?",
            proposer="coordinator",
            method=method,
            deadline_seconds=60,
        )

        # Simulate votes
        for agent_id in agents:
            # Random vote with varying confidence
            vote_type = random.choice(
                [VoteType.APPROVE, VoteType.REJECT, VoteType.ABSTAIN]
            )
            confidence = random.uniform(0.3, 1.0)

            await consensus.vote(
                proposal_id,
                agent_id,
                vote_type,
                confidence,
                "Based on analysis of current load",
            )

        # Update hormones for hormone-based consensus
        if method == ConsensusMethod.HORMONE:
            consensus.update_hormone_levels(
                {"stress": 0.8, "urgency": 0.6, "trust": 0.4}
            )

        # Reach consensus
        outcome = await consensus.reach_consensus(proposal_id)

        print(f"  Decision: {outcome.decision.value}")
        print(f"  Confidence: {outcome.confidence:.2%}")
        print(f"  Participation: {outcome.participation_rate:.2%}")
        print(f"  Convergence: {outcome.convergence_time:.3f}s")
        print(f"  Unanimous: {outcome.is_unanimous}")

    # Show history
    print("\n📊 Consensus History:")
    for record in consensus.get_consensus_history():
        print(
            f"  {record['method']}: {record['decision']} "
            f"({record['confidence']:.2%} confidence)"
        )


if __name__ == "__main__":
    asyncio.run(demo_consensus())
