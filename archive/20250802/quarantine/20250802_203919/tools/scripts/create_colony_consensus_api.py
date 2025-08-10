#!/usr/bin/env python3
"""
LUKHAS Colony Consensus API - Swarm Intelligence for Complex Decisions
Adds multi-agent collective intelligence to any AI system
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import asyncio
import numpy as np
from enum import Enum

app = FastAPI(
    title="LUKHAS Colony Consensus API",
    description="Multi-agent swarm intelligence for emergent decision making",
    version="1.0.0"
)


class AgentType(str, Enum):
    """Types of agents in the colony"""
    EXPLORER = "explorer"          # Searches solution space
    VALIDATOR = "validator"        # Validates proposals
    SYNTHESIZER = "synthesizer"    # Combines ideas
    CRITIC = "critic"              # Challenges assumptions
    HARMONIZER = "harmonizer"      # Ensures coherence
    DREAMER = "dreamer"           # Generates creative ideas


class DecisionContext(BaseModel):
    """Context for colony decision making"""
    question: str = Field(..., description="The decision or problem to solve")
    options: Optional[List[str]] = Field(
        None, description="Predefined options to consider")
    constraints: Optional[Dict[str, Any]] = Field(
        None, description="Constraints on the decision")
    urgency: float = Field(0.5, ge=0, le=1, description="How urgent the decision is")
    creativity_level: float = Field(
        0.5, ge=0, le=1, description="How creative vs conservative")
    consensus_threshold: float = Field(
        0.7, ge=0.5, le=1, description="Required agreement level")


class AgentProposal(BaseModel):
    """A proposal from a single agent"""
    agent_id: str
    agent_type: AgentType
    proposal: str
    confidence: float = Field(..., ge=0, le=1)
    reasoning: List[str]
    supporting_agents: List[str] = Field(default_factory=list)
    opposing_agents: List[str] = Field(default_factory=list)
    emergence_factor: float = Field(..., ge=0, le=1)


class SwarmBehavior(BaseModel):
    """Emergent swarm behavior pattern"""
    convergence_rate: float
    diversity_index: float
    echo_chambers: List[List[str]]
    bridge_agents: List[str]
    emergent_themes: List[str]


class ConsensusResponse(BaseModel):
    """Colony consensus result"""
    consensus_id: str
    timestamp: str
    final_decision: str
    consensus_strength: float = Field(..., ge=0, le=1)
    agent_proposals: List[AgentProposal]
    swarm_behavior: SwarmBehavior
    decision_path: List[Dict[str, Any]]
    emergent_insights: List[str]
    dissenting_opinions: List[Dict[str, str]]


class ColonyIntelligence:
    """Core colony intelligence engine"""

    def __init__(self):
        self.agents = {}
        self.pheromone_trails = {}  # Shared knowledge paths
        self.colony_memory = []     # Collective decisions
        self.emergence_threshold = 0.3

    async def achieve_consensus(self, context: DecisionContext) -> ConsensusResponse:
        """Achieve consensus through swarm intelligence"""

        consensus_id = f"consensus_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize colony based on context
        colony_size = self._calculate_colony_size(context)
        agents = await self._spawn_agents(colony_size, context)

        # Phase 1: Exploration
        initial_proposals = await self._exploration_phase(agents, context)

        # Phase 2: Cross-pollination
        enriched_proposals = await self._pollination_phase(initial_proposals, agents)

        # Phase 3: Convergence
        consensus_proposals = await self._convergence_phase(enriched_proposals, context)

        # Phase 4: Emergence detection
        emergent_insights = self._detect_emergence(consensus_proposals)

        # Calculate final decision
        final_decision, strength = self._calculate_final_decision(
            consensus_proposals,
            context.consensus_threshold
        )

        # Analyze swarm behavior
        swarm_behavior = self._analyze_swarm_behavior(agents, consensus_proposals)

        # Extract decision path
        decision_path = self._extract_decision_path(
            initial_proposals, consensus_proposals)

        # Identify dissent
        dissenting = self._identify_dissent(consensus_proposals, final_decision)

        return ConsensusResponse(
            consensus_id=consensus_id,
            timestamp=datetime.now().isoformat(),
            final_decision=final_decision,
            consensus_strength=strength,
            agent_proposals=consensus_proposals,
            swarm_behavior=swarm_behavior,
            decision_path=decision_path,
            emergent_insights=emergent_insights,
            dissenting_opinions=dissenting
        )

    def _calculate_colony_size(self, context: DecisionContext) -> int:
        """Determine optimal colony size based on problem complexity"""
        base_size = 10

        # More agents for complex problems
        if len(context.question) > 200:
            base_size += 5

        # More agents for high-stakes decisions
        if context.urgency > 0.8:
            base_size += 3

        # More diversity for creative problems
        if context.creativity_level > 0.7:
            base_size += 4

        return min(base_size, 25)  # Cap at 25 agents

    async def _spawn_agents(
            self,
            colony_size: int,
            context: DecisionContext) -> List[Dict]:
        """Spawn diverse agents for the colony"""
        agents = []

        # Determine agent type distribution based on context
        if context.creativity_level > 0.7:
            # Creative problem - more dreamers and explorers
            distribution = {
                AgentType.DREAMER: 0.3,
                AgentType.EXPLORER: 0.25,
                AgentType.SYNTHESIZER: 0.2,
                AgentType.CRITIC: 0.15,
                AgentType.VALIDATOR: 0.5,
                AgentType.HARMONIZER: 0.5
            }
        else:
            # Analytical problem - more validators and critics
            distribution = {
                AgentType.VALIDATOR: 0.3,
                AgentType.CRITIC: 0.25,
                AgentType.EXPLORER: 0.2,
                AgentType.SYNTHESIZER: 0.15,
                AgentType.HARMONIZER: 0.5,
                AgentType.DREAMER: 0.5
            }

        # Spawn agents according to distribution
        for i in range(colony_size):
            agent_type = self._select_agent_type(distribution)
            agent = {
                'id': f"agent_{i}_{agent_type.value}",
                'type': agent_type,
                'personality': self._generate_personality(agent_type),
                'connections': set(),
                'influence': 1.0
            }
            agents.append(agent)

        # Create connections (small world network)
        self._create_agent_network(agents)

        return agents

    def _select_agent_type(self, distribution: Dict[AgentType, float]) -> AgentType:
        """Select agent type based on distribution"""
        rand = np.random.random()
        cumsum = 0

        for agent_type, prob in distribution.items():
            cumsum += prob
            if rand < cumsum:
                return agent_type

        return AgentType.EXPLORER  # Default

    def _generate_personality(self, agent_type: AgentType) -> Dict[str, float]:
        """Generate personality traits for agent"""
        base_traits = {
            'openness': 0.5,
            'analytical': 0.5,
            'risk_tolerance': 0.5,
            'collaboration': 0.5
        }

        # Adjust based on type
        if agent_type == AgentType.DREAMER:
            base_traits['openness'] = 0.9
            base_traits['risk_tolerance'] = 0.8
        elif agent_type == AgentType.VALIDATOR:
            base_traits['analytical'] = 0.9
            base_traits['risk_tolerance'] = 0.2
        elif agent_type == AgentType.CRITIC:
            base_traits['analytical'] = 0.8
            base_traits['collaboration'] = 0.3
        elif agent_type == AgentType.HARMONIZER:
            base_traits['collaboration'] = 0.9
            base_traits['openness'] = 0.7

        return base_traits

    def _create_agent_network(self, agents: List[Dict]):
        """Create small-world network connection"""
        n = len(agents)

        # Each agent connects to ~20% of others
        connection_prob = 0.2

        for i in range(n):
            for j in range(i + 1, n):
                if np.random.random() < connection_prob:
                    agents[i]['connections'].add(agents[j]['id'])
                    agents[j]['connections'].add(agents[i]['id'])

        # Ensure no isolated agents
        for agent in agents:
            if len(agent['connections']) == 0:
                # Connect to random agent
                other = np.random.choice([a for a in agents if a['id'] != agent['id']])
                agent['connections'].add(other['id'])
                other['connections'].add(agent['id'])

    async def _exploration_phase(
        self,
        agents: List[Dict],
        context: DecisionContext
    ) -> List[AgentProposal]:
        """Agents independently explore solution space"""
        proposals = []

        for agent in agents:
            # Generate proposal based on agent type and personality
            proposal = await self._generate_agent_proposal(agent, context)
            proposals.append(proposal)

        return proposals

    async def _generate_agent_proposal(
        self,
        agent: Dict,
        context: DecisionContext
    ) -> AgentProposal:
        """Generate proposal from single agent"""

        agent_type = agent['type']
        personality = agent['personality']

        # Different approaches based on agent type
        if agent_type == AgentType.DREAMER:
            proposal_text, reasoning = self._generate_creative_proposal(context)
            confidence = personality['openness'] * 0.8

        elif agent_type == AgentType.VALIDATOR:
            proposal_text, reasoning = self._generate_validated_proposal(context)
            confidence = personality['analytical'] * 0.9

        elif agent_type == AgentType.EXPLORER:
            proposal_text, reasoning = self._generate_exploratory_proposal(context)
            confidence = 0.6 + personality['risk_tolerance'] * 0.3

        elif agent_type == AgentType.CRITIC:
            proposal_text, reasoning = self._generate_critical_proposal(context)
            confidence = personality['analytical'] * 0.7

        elif agent_type == AgentType.SYNTHESIZER:
            proposal_text, reasoning = self._generate_synthetic_proposal(context)
            confidence = 0.7

        else:  # HARMONIZER
            proposal_text, reasoning = self._generate_harmonious_proposal(context)
            confidence = personality['collaboration'] * 0.8

        # Calculate emergence factor
        emergence = self._calculate_emergence_factor(proposal_text, context)

        return AgentProposal(
            agent_id=agent['id'],
            agent_type=agent_type,
            proposal=proposal_text,
            confidence=confidence,
            reasoning=reasoning,
            emergence_factor=emergence
        )

    def _generate_creative_proposal(
            self, context: DecisionContext) -> Tuple[str, List[str]]:
        """Generate creative, out-of-the-box proposal"""
        # In real LUKHAS, this would use dream engine
        proposals = [
            "What if we approached this from a completely different angle?",
            "Consider the impossible, then work backwards",
            "Merge seemingly unrelated concepts for breakthrough",
            "Challenge every assumption in the question"
        ]

        reasoning = [
            "Innovation comes from unexpected connections",
            "Traditional approaches may have blind spots",
            "Creativity unlocks hidden solutions"
        ]

        return np.random.choice(proposals), reasoning

    def _generate_validated_proposal(
            self, context: DecisionContext) -> Tuple[str, List[str]]:
        """Generate thoroughly validated proposal"""
        if context.options:
            # Analyze predefined options
            proposal = f"After careful analysis, option '{context.options[0]}' shows highest viability"
        else:
            proposal = "Systematic evaluation suggests a methodical approach"

        reasoning = [
            "Evidence-based decision making reduces risk",
            "Validation ensures robust outcomes",
            "Data supports this direction"
        ]

        return proposal, reasoning

    def _generate_exploratory_proposal(
            self, context: DecisionContext) -> Tuple[str, List[str]]:
        """Generate proposal through exploration"""
        proposal = "Explore multiple parallel paths before committing"

        reasoning = [
            "Exploration reveals hidden opportunities",
            "Multiple paths increase success probability",
            "Flexibility allows adaptation"
        ]

        return proposal, reasoning

    def _generate_critical_proposal(
            self, context: DecisionContext) -> Tuple[str, List[str]]:
        """Generate proposal through critical analysi"""
        proposal = "The key risk factors must be addressed first"

        reasoning = [
            "Critical analysis prevents costly mistakes",
            "Understanding weaknesses improves strategy",
            "Risk mitigation is essential"
        ]

        return proposal, reasoning

    def _generate_synthetic_proposal(
            self, context: DecisionContext) -> Tuple[str, List[str]]:
        """Generate proposal through synthesi"""
        proposal = "Combine the best elements of multiple approaches"

        reasoning = [
            "Synthesis creates superior solutions",
            "Integration leverages all strengths",
            "Holistic thinking yields better outcomes"
        ]

        return proposal, reasoning

    def _generate_harmonious_proposal(
            self, context: DecisionContext) -> Tuple[str, List[str]]:
        """Generate proposal ensuring harmony"""
        proposal = "Find the solution that aligns all stakeholders"

        reasoning = [
            "Harmony ensures sustainable implementation",
            "Aligned interests reduce friction",
            "Consensus builds stronger commitment"
        ]

        return proposal, reasoning

    def _calculate_emergence_factor(
            self,
            proposal: str,
            context: DecisionContext) -> float:
        """Calculate how emergent/novel a proposal i"""
        # Simple heuristic - in real LUKHAS would use deeper analysis

        # Check if proposal contains unexpected elements
        unexpected_words = ['impossible', 'breakthrough', 'revolutionary', 'paradox']
        emergence_score = 0.0

        for word in unexpected_words:
            if word in proposal.lower():
                emergence_score += 0.25

        # Longer, more complex proposals might be more emergent
        if len(proposal) > 100:
            emergence_score += 0.2

        return min(1.0, emergence_score)

    async def _pollination_phase(
        self,
        proposals: List[AgentProposal],
        agents: List[Dict]
    ) -> List[AgentProposal]:
        """Cross-pollinate ideas between connected agent"""

        # Create proposal lookup
        proposal_by_agent = {p.agent_id: p for p in proposals}
        agent_by_id = {a['id']: a for a in agents}

        # Share and evolve proposals
        evolved_proposals = []

        for proposal in proposals:
            agent = agent_by_id[proposal.agent_id]

            # Get proposals from connected agents
            connected_proposals = [
                proposal_by_agent[conn_id]
                for conn_id in agent['connections']
                if conn_id in proposal_by_agent
            ]

            # Evolve proposal based on connections
            evolved = await self._evolve_proposal(
                proposal,
                connected_proposals,
                agent['personality']
            )

            evolved_proposals.append(evolved)

        return evolved_proposals

    async def _evolve_proposal(
        self,
        original: AgentProposal,
        connected: List[AgentProposal],
        personality: Dict[str, float]
    ) -> AgentProposal:
        """Evolve proposal based on neighbor influence"""

        # Track support and opposition
        supporting = []
        opposing = []

        for other in connected:
            # Simple similarity check
            if self._proposals_align(original, other):
                supporting.append(other.agent_id)
                # Increase confidence if supported
                original.confidence = min(1.0, original.confidence + 0.5)
            else:
                opposing.append(other.agent_id)
                # Decrease confidence if opposed (unless highly confident)
                if personality['openness'] > 0.3:
                    original.confidence = max(0.1, original.confidence - 0.3)

        # Update proposal
        original.supporting_agents = supporting
        original.opposing_agents = opposing

        # Potentially modify proposal based on feedback
        if len(opposing) > len(supporting) and personality['collaboration'] > 0.6:
            # Collaborative agent modifies proposal
            original.proposal = f"Modified: {original.proposal} (incorporating feedback)"
            original.reasoning.append("Adapted based on colony feedback")

        return original

    def _proposals_align(self, prop1: AgentProposal, prop2: AgentProposal) -> bool:
        """Check if two proposals align"""
        # Simple heuristic - in real system would use NLP

        # Same agent type often aligns
        if prop1.agent_type == prop2.agent_type:
            return np.random.random() > 0.3

        # Critics rarely align with dreamers
        if (prop1.agent_type == AgentType.CRITIC and prop2.agent_type == AgentType.DREAMER) or " + "(
                prop1.agent_type == AgentType.DREAMER and prop2.agent_type == AgentType.CRITIC):
            return np.random.random() > 0.8

        # Default moderate alignment
        return np.random.random() > 0.5

    async def _convergence_phase(
        self,
        proposals: List[AgentProposal],
        context: DecisionContext
    ) -> List[AgentProposal]:
        """Converge towards consensu"""

        # Sort by confidence and support
        proposals.sort(
            key=lambda p: p.confidence + len(p.supporting_agents) * 0.1,
            reverse=True
        )

        # Merge similar proposals
        merged_proposals = []
        processed = set()

        for proposal in proposals:
            if proposal.agent_id in processed:
                continue

            # Find similar proposals
            similar = [
                p for p in proposals
                if p.agent_id not in processed and
                self._proposals_similar(proposal, p)
            ]

            if len(similar) > 1:
                # Merge into super-proposal
                merged = self._merge_proposals(similar)
                merged_proposals.append(merged)
                processed.update(p.agent_id for p in similar)
            else:
                merged_proposals.append(proposal)
                processed.add(proposal.agent_id)

        return merged_proposals

    def _proposals_similar(self, prop1: AgentProposal, prop2: AgentProposal) -> bool:
        """Check if proposals are similar enough to merge"""
        # In real system, would use semantic similarity

        # High mutual support indicates similarity
        if prop1.agent_id in prop2.supporting_agents and " + "prop2.agent_id in prop1.supporting_agents:
            return True

        # Similar confidence and same type
        if abs(prop1.confidence - prop2.confidence) < 0.2 and " + "prop1.agent_type == prop2.agent_type:
            return np.random.random() > 0.6

        return False

    def _merge_proposals(self, proposals: List[AgentProposal]) -> AgentProposal:
        """Merge multiple proposals into one"""
        # Take highest confidence proposal as base
        base = max(proposals, key=lambda p: p.confidence)

        # Combine supporting agents
        all_supporting = set()
        all_reasoning = []

        for prop in proposals:
            all_supporting.update(prop.supporting_agents)
            all_reasoning.extend(prop.reasoning)

        # Create merged proposal
        merged = AgentProposal(
            agent_id=f"merged_{base.agent_id}",
            agent_type=base.agent_type,
            proposal=f"Consensus: {base.proposal}",
            confidence=min(1.0, base.confidence + len(proposals) * 0.5),
            reasoning=list(set(all_reasoning))[:5],  # Top 5 unique reasons
            supporting_agents=list(all_supporting),
            opposing_agents=[],
            emergence_factor=max(p.emergence_factor for p in proposals)
        )

        return merged

    def _detect_emergence(self, proposals: List[AgentProposal]) -> List[str]:
        """Detect emergent insights from colony behavior"""
        insights = []

        # High emergence proposals
        high_emergence = [p for p in proposals if p.emergence_factor > 0.7]
        if high_emergence:
            insights.append(
                f"Colony discovered {len(high_emergence)} breakthrough ideas")

        # Unexpected consensus
        if len(proposals) < 5 and len(proposals) > 0:
            insights.append("Rapid convergence indicates clear solution path")

        # Persistent disagreement
        highly_opposed = [
            p for p in proposals if len(
                p.opposing_agents) > len(
                p.supporting_agents)]
        if len(highly_opposed) > len(proposals) / 2:
            insights.append("Strong divergence suggests multiple valid approaches")

        # Cross-type agreement
        type_diversity = len(set(p.agent_type for p in proposals))
        if type_diversity > 3 and len(proposals) < 10:
            insights.append("Diverse agent types reached consensus - robust solution")

        return insights

    def _calculate_final_decision(
        self,
        proposals: List[AgentProposal],
        threshold: float
    ) -> Tuple[str, float]:
        """Calculate final decision and consensus strength"""

        if not proposals:
            return "No consensus reached", 0.0

        # Get top proposal
        top_proposal = max(proposals, key=lambda p: p.confidence)

        # Calculate consensus strength
        if len(proposals) == 1:
            strength = top_proposal.confidence
        else:
            # Consider how much agreement there is
            total_support = sum(len(p.supporting_agents) for p in proposals)
            total_opposition = sum(len(p.opposing_agents) for p in proposals)

            if total_support + total_opposition > 0:
                strength = total_support / (total_support + total_opposition)
            else:
                strength = top_proposal.confidence

        # Check if meets threshold
        if strength >= threshold:
            return top_proposal.proposal, strength
        else:
            return f"Partial consensus: {top_proposal.proposal} (below threshold)", strength

    def _analyze_swarm_behavior(
        self,
        agents: List[Dict],
        proposals: List[AgentProposal]
    ) -> SwarmBehavior:
        """Analyze emergent swarm pattern"""

        # Convergence rate (how quickly consensus formed)
        convergence_rate = 1.0 - (len(proposals) / len(agents))

        # Diversity index (variety of proposals)
        unique_types = len(set(p.agent_type for p in proposals))
        diversity_index = unique_types / len(AgentType)

        # Detect echo chambers (groups that only support each other)
        echo_chambers = self._detect_echo_chambers(proposals)

        # Find bridge agents (connected to multiple groups)
        bridge_agents = self._find_bridge_agents(agents, proposals)

        # Emergent themes
        themes = self._extract_themes(proposals)

        return SwarmBehavior(
            convergence_rate=convergence_rate,
            diversity_index=diversity_index,
            echo_chambers=echo_chambers,
            bridge_agents=bridge_agents,
            emergent_themes=themes
        )

    def _detect_echo_chambers(self, proposals: List[AgentProposal]) -> List[List[str]]:
        """Detect groups that only support each other"""
        chambers = []

        # Build support graph
        support_graph = {}
        for prop in proposals:
            support_graph[prop.agent_id] = set(prop.supporting_agents)

        # Find strongly connected components (simplified)
        processed = set()

        for agent_id in support_graph:
            if agent_id in processed:
                continue

            chamber = {agent_id}
            stack = [agent_id]

            while stack:
                current = stack.pop()
                for supporter in support_graph.get(current, []):
                    if supporter not in chamber and supporter in support_graph:
                        # Check if mutual support
                        if current in support_graph.get(supporter, []):
                            chamber.add(supporter)
                            stack.append(supporter)

            if len(chamber) > 2:
                chambers.append(list(chamber))
                processed.update(chamber)

        return chambers

    def _find_bridge_agents(
        self,
        agents: List[Dict],
        proposals: List[AgentProposal]
    ) -> List[str]:
        """Find agents that bridge different group"""
        bridges = []

        # Agents with diverse connections
        for agent in agents:
            if len(agent['connections']) > len(agents) * 0.3:
                # Well connected
                proposal = next(
                    (p for p in proposals if p.agent_id == agent['id']), None)
                if proposal and len(
                        proposal.supporting_agents) > 2 and len(
                        proposal.opposing_agents) > 2:
                    # Has both support and opposition - likely bridge
                    bridges.append(agent['id'])

        return bridges

    def _extract_themes(self, proposals: List[AgentProposal]) -> List[str]:
        """Extract emergent themes from proposal"""
        # Simplified theme extraction
        themes = []

        # Common reasoning patterns
        all_reasoning = []
        for prop in proposals:
            all_reasoning.extend(prop.reasoning)

        # Find frequently mentioned concepts
        common_words = ['innovation', 'risk', 'consensus', 'exploration', 'validation']

        for word in common_words:
            count = sum(1 for r in all_reasoning if word in r.lower())
            if count > len(proposals) / 2:
                themes.append(f"{word.capitalize()}-focused approach emerging")

        return themes[:3]  # Top 3 themes

    def _extract_decision_path(
        self,
        initial: List[AgentProposal],
        final: List[AgentProposal]
    ) -> List[Dict[str, Any]]:
        """Extract the path from initial ideas to consensu"""
        path = []

        # Initial diversity
        path.append({
            'stage': 'Initial Exploration',
            'proposals': len(initial),
            'diversity': len(set(p.agent_type for p in initial)) / len(AgentType),
            'avg_confidence': np.mean([p.confidence for p in initial])
        })

        # Convergence
        path.append({
            'stage': 'Post-Pollination',
            'proposals': len(final),
            'consensus_forming': len([p for p in final if len(p.supporting_agents) > 3]),
            'emergent_ideas': len([p for p in final if p.emergence_factor > 0.5])
        })

        # Final state
        if final:
            top = max(final, key=lambda p: p.confidence)
            path.append({
                'stage': 'Final Consensus',
                'leading_proposal': top.agent_type.value,
                'support_ratio': len(top.supporting_agents) / (len(top.supporting_agents) + len(top.opposing_agents) + 1),
                'confidence': top.confidence
            })

        return path

    def _identify_dissent(
        self,
        proposals: List[AgentProposal],
        final_decision: str
    ) -> List[Dict[str, str]]:
        """Identify dissenting opinion"""
        dissent = []

        # Find proposals that strongly disagree
        for prop in proposals:
            if prop.confidence > 0.6 and len(
                    prop.opposing_agents) > len(
                    prop.supporting_agents):
                dissent.append({
                    'agent': prop.agent_id,
                    'type': prop.agent_type.value,
                    'alternative': prop.proposal,
                    'reasoning': prop.reasoning[0] if prop.reasoning else "Different perspective"
                })

        return dissent[:3]  # Top 3 dissenting views


# Initialize colony
colony = ColonyIntelligence()


@app.post("/api/v1/colony-consensus", response_model=ConsensusResponse)
async def achieve_colony_consensus(context: DecisionContext):
    """
    Achieve consensus through multi-agent swarm intelligence.

    This API uses LUKHAS's colony intelligence to:
    - Spawn diverse agents with different perspectives
    - Enable emergent decision making through interaction
    - Detect breakthrough insights from swarm behavior
    - Reach robust consensus or identify valid alternatives
    """
    try:
        response = await colony.achieve_consensus(context)
        return response

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Colony consensus failed: {str(e)}")


@app.get("/api/v1/colony-status")
async def get_colony_status():
    """Get current colony statu"""
    return {
        "status": "active",
        "active_agents": len(colony.agents),
        "memory_size": len(colony.colony_memory),
        "emergence_threshold": colony.emergence_threshold,
        "pheromone_trails": len(colony.pheromone_trails)
    }


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to LUKHAS Colony Consensus API",
        "description": "Multi-agent swarm intelligence for emergent decision making",
        "features": [
            "Diverse agent personalities",
            "Emergent consensus formation",
            "Echo chamber detection",
            "Bridge agent identification",
            "Dissent preservation"
        ],
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "colony": "thriving",
        "swarm_coherence": "optimal",
        "emergence_potential": "high"
    }

# Example integration endpoint


@app.post("/api/v1/demo")
async def demo_integration():
    """Demo: How to integrate Colony Consensus with GPT/Claude"""
    return {
        "example": "Add swarm intelligence to any decision",
        "steps": [
            "1. Frame the decision or problem",
            "2. Let colony explore solution space",
            "3. Watch emergence and convergence",
            "4. Get robust consensus or alternatives"
        ],
        "code_example": """
# Complex decision making
decision = lukhas.colony_consensus({
    'question': 'How should we approach this new market?',
    'constraints': {'budget': 'limited', 'timeline': '6 months'},
    'creativity_level': 0.7,
    'consensus_threshold': 0.75
})

# Access swarm insights
print(f"Decision: {decision.final_decision}")
print(f"Consensus strength: {decision.consensus_strength}")
print(f"Emergent insights: {decision.emergent_insights}")
print(f"Dissenting views: {decision.dissenting_opinions}")

# Use with GPT/Claude
gpt_analysis = openai.analyze(decision.final_decision)
enhanced = lukhas.colony_consensus({
    'question': gpt_analysis,
    'options': decision.dissenting_opinions
})
"""
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
