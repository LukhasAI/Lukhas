#!/usr/bin/env python3
"""
Multi-Agent Safety Consensus System
Multiple specialized AI agents collaborate to make safety decisions.
Ensures robust, balanced safety through diverse perspectives.
"""

import asyncio
import json
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Specialized roles for safety agents"""

    SAFETY_ADVOCATE = "safety_advocate"  # Prioritizes user protection above all
    BUSINESS_ADVOCATE = "business_advocate"  # Considers commercial viability
    ETHICS_ADVOCATE = "ethics_advocate"  # Ensures ethical standards
    LEGAL_ADVOCATE = "legal_advocate"  # Checks regulatory compliance
    USER_ADVOCATE = "user_advocate"  # Represents user interests
    TECHNICAL_ADVOCATE = "technical_advocate"  # Evaluates technical feasibility
    PRIVACY_ADVOCATE = "privacy_advocate"  # Guards data protection
    CHILD_ADVOCATE = "child_advocate"  # Special protection for minors


@dataclass
class AgentVote:
    """A vote from a safety agent"""

    agent_role: AgentRole
    decision: str  # approve, reject, conditional
    confidence: float  # 0-1
    reasoning: str
    conditions: List[str] = field(default_factory=list)  # For conditional approval
    dissent_points: List[str] = field(default_factory=list)  # Specific concerns
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConsensusResult:
    """Result of multi-agent consensus"""

    consensus_reached: bool
    final_decision: str  # approve, reject, conditional, escalate
    confidence: float  # Average confidence
    vote_breakdown: Dict[str, int]
    dissenting_opinions: List[AgentVote]
    conditions: List[str]  # Consolidated conditions
    reasoning_summary: str
    requires_human_review: bool
    timestamp: datetime = field(default_factory=datetime.now)


class SafetyAgent:
    """Individual safety agent with specific role and perspective"""

    def __init__(self, role: AgentRole, openai_client: Optional[AsyncOpenAI] = None):
        self.role = role
        self.openai = openai_client
        self.decision_history: List[AgentVote] = []
        self.role_prompts = self._initialize_role_prompts()

    def _initialize_role_prompts(self) -> Dict[str, str]:
        """Initialize role-specific prompts"""
        return {
            AgentRole.SAFETY_ADVOCATE: """You are a safety advocate. Your primary concern is user protection.
            Prioritize: preventing harm, emotional wellbeing, long-term safety.
            Be conservative with safety decisions. When in doubt, protect the user.""",
            AgentRole.BUSINESS_ADVOCATE: """You are a business advocate. Consider commercial viability while respecting safety.
            Balance: revenue potential, user engagement, brand reputation, sustainable growth.
            Find safe ways to achieve business goals.""",
            AgentRole.ETHICS_ADVOCATE: """You are an ethics advocate. Ensure all actions meet high ethical standards.
            Consider: fairness, transparency, consent, human dignity, societal impact.
            Apply philosophical and ethical frameworks.""",
            AgentRole.LEGAL_ADVOCATE: """You are a legal advocate. Ensure regulatory compliance.
            Check: GDPR, CCPA, EU AI Act, FTC guidelines, sector-specific regulations.
            Flag any legal risks or compliance issues.""",
            AgentRole.USER_ADVOCATE: """You are a user advocate. Represent user interests and preferences.
            Consider: user autonomy, choice, experience quality, value delivery.
            Ensure users get what they want safely.""",
            AgentRole.TECHNICAL_ADVOCATE: """You are a technical advocate. Evaluate technical feasibility and risks.
            Consider: implementation complexity, system impact, performance, security.
            Identify technical constraints and opportunities.""",
            AgentRole.PRIVACY_ADVOCATE: """You are a privacy advocate. Protect user data and privacy.
            Enforce: data minimization, purpose limitation, consent requirements.
            Apply privacy-by-design principles.""",
            AgentRole.CHILD_ADVOCATE: """You are a child advocate. Provide special protection for minors.
            Enforce: COPPA compliance, age-appropriate content, parental controls.
            Zero tolerance for child exploitation or manipulation.""",
        }

    async def evaluate_proposal(
        self, proposal: Dict[str, Any], context: Dict[str, Any]
    ) -> AgentVote:
        """Evaluate a proposal from this agent's perspective"""
        if not self.openai:
            return self._heuristic_evaluation(proposal, context)

        try:
            # Get role-specific prompt
            role_prompt = self.role_prompts.get(
                self.role, "Evaluate the proposal for safety."
            )

            # Evaluate with AI
            response = await self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": f"{role_prompt}\nProvide thorough analysis from your perspective.",
                    },
                    {
                        "role": "user",
                        "content": f"""Evaluate this proposal:
                    {json.dumps(proposal)}

                    Context:
                    {json.dumps(context)}""",
                    },
                ],
                functions=[
                    {
                        "name": "vote_on_proposal",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "decision": {
                                    "type": "string",
                                    "enum": ["approve", "reject", "conditional"],
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "reasoning": {"type": "string"},
                                "conditions": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "concerns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "opportunities": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["decision", "confidence", "reasoning"],
                        },
                    }
                ],
                function_call={"name": "vote_on_proposal"},
                temperature=0.3,  # Lower temperature for consistency
            )

            vote_data = json.loads(response.choices[0].message.function_call.arguments)

            vote = AgentVote(
                agent_role=self.role,
                decision=vote_data["decision"],
                confidence=vote_data["confidence"],
                reasoning=vote_data["reasoning"],
                conditions=vote_data.get("conditions", []),
                dissent_points=vote_data.get("concerns", []),
            )

            # Store in history
            self.decision_history.append(vote)
            if len(self.decision_history) > 100:
                self.decision_history = self.decision_history[-50:]

            return vote

        except Exception as e:
            logger.error(f"Agent {self.role.value} evaluation failed: {e}")
            return self._heuristic_evaluation(proposal, context)

    def _heuristic_evaluation(
        self, proposal: Dict[str, Any], context: Dict[str, Any]
    ) -> AgentVote:
        """Fallback heuristic evaluation"""
        # Simple role-based heuristics
        decision = "conditional"
        confidence = 0.5
        reasoning = f"Heuristic evaluation by {self.role.value}"

        if self.role == AgentRole.SAFETY_ADVOCATE:
            # Safety advocate is conservative
            risk_level = proposal.get("risk_assessment", {}).get("level", 0.5)
            if risk_level > 0.3:
                decision = "reject"
                reasoning = "Risk level exceeds safety threshold"
            confidence = 0.7

        elif self.role == AgentRole.CHILD_ADVOCATE:
            # Child advocate checks age
            if context.get("user_age", 100) < 18:
                decision = (
                    "reject"
                    if proposal.get("type") in ["marketing", "data_collection"]
                    else "conditional"
                )
                reasoning = "Special protection for minors required"
            confidence = 0.8

        return AgentVote(
            agent_role=self.role,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
        )


class MultiAgentSafetyConsensus:
    """
    Multi-Agent Safety Consensus System.

    Coordinates multiple specialized agents to reach robust safety decisions
    through diverse perspectives and collaborative evaluation.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

        # Initialize agents
        self.agents = self._initialize_agents()

        # Consensus configuration
        self.min_agents_for_decision = 3
        self.supermajority_threshold = 0.75  # 75% agreement needed
        self.unanimous_for_children = (
            True  # All agents must agree for child-related decisions
        )
        self.confidence_threshold = 0.7

        # Decision history
        self.consensus_history: List[ConsensusResult] = []

        logger.info(
            f"Multi-Agent Safety Consensus initialized with {len(self.agents)} agents"
        )

    def _initialize_agents(self) -> Dict[AgentRole, SafetyAgent]:
        """Initialize all safety agents"""
        agents = {}

        # Create core agents
        core_roles = [
            AgentRole.SAFETY_ADVOCATE,
            AgentRole.ETHICS_ADVOCATE,
            AgentRole.USER_ADVOCATE,
            AgentRole.PRIVACY_ADVOCATE,
        ]

        # Add specialized agents based on configuration
        specialized_roles = [
            AgentRole.BUSINESS_ADVOCATE,
            AgentRole.LEGAL_ADVOCATE,
            AgentRole.TECHNICAL_ADVOCATE,
            AgentRole.CHILD_ADVOCATE,
        ]

        all_roles = core_roles + specialized_roles

        for role in all_roles:
            agents[role] = SafetyAgent(role, self.openai)

        return agents

    async def evaluate_action(
        self,
        action_type: str,
        action_data: Dict[str, Any],
        context: Dict[str, Any],
        required_agents: Optional[List[AgentRole]] = None,
    ) -> ConsensusResult:
        """
        Evaluate an action through multi-agent consensus.

        This is the main entry point for consensus-based safety decisions.
        """
        proposal = {
            "action_type": action_type,
            "action_data": action_data,
            "timestamp": datetime.now().isoformat(),
        }

        # Determine which agents should vote
        voting_agents = self._select_voting_agents(
            action_type, context, required_agents
        )

        # Collect votes from all agents
        votes = await self._collect_votes(proposal, context, voting_agents)

        # Analyze consensus
        consensus = self._analyze_consensus(votes, context)

        # Generate summary explanation
        consensus.reasoning_summary = await self._generate_consensus_summary(
            votes, consensus
        )

        # Store in history
        self.consensus_history.append(consensus)
        if len(self.consensus_history) > 1000:
            self.consensus_history = self.consensus_history[-500:]

        return consensus

    def _select_voting_agents(
        self,
        action_type: str,
        context: Dict[str, Any],
        required_agents: Optional[List[AgentRole]],
    ) -> List[SafetyAgent]:
        """Select which agents should vote on this decision"""
        voting_agents = []

        # If specific agents requested, use those
        if required_agents:
            voting_agents = [
                self.agents[role] for role in required_agents if role in self.agents
            ]
        else:
            # Select based on action type and context
            # Always include core safety agents
            voting_agents.extend(
                [
                    self.agents[AgentRole.SAFETY_ADVOCATE],
                    self.agents[AgentRole.ETHICS_ADVOCATE],
                    self.agents[AgentRole.USER_ADVOCATE],
                ]
            )

            # Add specialized agents based on context
            if context.get("user_age", 100) < 18:
                voting_agents.append(self.agents[AgentRole.CHILD_ADVOCATE])

            if action_type in ["data_collection", "tracking", "biometric"]:
                voting_agents.append(self.agents[AgentRole.PRIVACY_ADVOCATE])

            if action_type in ["marketing", "commercial", "transaction"]:
                voting_agents.append(self.agents[AgentRole.BUSINESS_ADVOCATE])

            if context.get("regulatory_jurisdiction"):
                voting_agents.append(self.agents[AgentRole.LEGAL_ADVOCATE])

            if action_type in ["system_change", "architecture", "integration"]:
                voting_agents.append(self.agents[AgentRole.TECHNICAL_ADVOCATE])

        # Ensure minimum agents
        if len(voting_agents) < self.min_agents_for_decision:
            # Add more agents to meet minimum
            for role, agent in self.agents.items():
                if agent not in voting_agents:
                    voting_agents.append(agent)
                    if len(voting_agents) >= self.min_agents_for_decision:
                        break

        return voting_agents

    async def _collect_votes(
        self,
        proposal: Dict[str, Any],
        context: Dict[str, Any],
        voting_agents: List[SafetyAgent],
    ) -> List[AgentVote]:
        """Collect votes from all voting agents"""
        # Vote in parallel for efficiency
        vote_tasks = [
            agent.evaluate_proposal(proposal, context) for agent in voting_agents
        ]

        votes = await asyncio.gather(*vote_tasks)

        return votes

    def _analyze_consensus(
        self, votes: List[AgentVote], context: Dict[str, Any]
    ) -> ConsensusResult:
        """Analyze votes to determine consensus"""
        # Count votes
        vote_counts = {"approve": 0, "reject": 0, "conditional": 0}
        total_confidence = 0
        all_conditions = []
        dissenting_votes = []

        for vote in votes:
            vote_counts[vote.decision] += 1
            total_confidence += vote.confidence

            if vote.conditions:
                all_conditions.extend(vote.conditions)

            # Track dissent
            if vote.dissent_points:
                dissenting_votes.append(vote)

        # Calculate metrics
        total_votes = len(votes)
        avg_confidence = total_confidence / total_votes if total_votes > 0 else 0

        # Determine final decision
        if context.get("user_age", 100) < 18 and self.unanimous_for_children:
            # Require unanimous approval for children
            if vote_counts["reject"] > 0:
                final_decision = "reject"
            elif vote_counts["conditional"] > 0:
                final_decision = "conditional"
            else:
                final_decision = "approve"
        else:
            # Use supermajority rule
            if vote_counts["approve"] / total_votes >= self.supermajority_threshold:
                final_decision = "approve"
            elif vote_counts["reject"] / total_votes >= self.supermajority_threshold:
                final_decision = "reject"
            elif (
                vote_counts["conditional"] + vote_counts["approve"]
                >= self.supermajority_threshold
            ):
                final_decision = "conditional"
            else:
                # No clear consensus - escalate
                final_decision = "escalate"

        # Check if human review needed
        requires_human = (
            final_decision == "escalate"
            or avg_confidence < self.confidence_threshold
            or len(dissenting_votes) > total_votes * 0.3  # >30% dissent
        )

        # Consolidate conditions
        unique_conditions = list(set(all_conditions))

        return ConsensusResult(
            consensus_reached=final_decision != "escalate",
            final_decision=final_decision,
            confidence=avg_confidence,
            vote_breakdown=vote_counts,
            dissenting_opinions=dissenting_votes,
            conditions=unique_conditions,
            reasoning_summary="",  # Will be filled by _generate_consensus_summary
            requires_human_review=requires_human,
        )

    async def _generate_consensus_summary(
        self, votes: List[AgentVote], consensus: ConsensusResult
    ) -> str:
        """Generate human-readable summary of consensus reasoning"""
        if not self.openai:
            return self._basic_summary(votes, consensus)

        try:
            # Prepare vote summaries
            vote_summaries = [
                {
                    "agent": vote.agent_role.value,
                    "decision": vote.decision,
                    "reasoning": vote.reasoning,
                    "confidence": vote.confidence,
                }
                for vote in votes
            ]

            response = await self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """Synthesize the multi-agent consensus into a clear summary.
                    Highlight key agreements, important dissent, and final reasoning.""",
                    },
                    {
                        "role": "user",
                        "content": f"""Votes: {json.dumps(vote_summaries)}
                    Final decision: {consensus.final_decision}
                    Vote breakdown: {consensus.vote_breakdown}""",
                    },
                ],
                max_tokens=300,
                temperature=0.5,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return self._basic_summary(votes, consensus)

    def _basic_summary(self, votes: List[AgentVote], consensus: ConsensusResult) -> str:
        """Generate basic summary without AI"""
        summary_parts = [
            f"Decision: {consensus.final_decision}",
            f"Confidence: {consensus.confidence:.1%}",
            f"Votes: {consensus.vote_breakdown}",
        ]

        if consensus.dissenting_opinions:
            dissent_summary = f"Dissent from: {', '.join(v.agent_role.value for v in consensus.dissenting_opinions)}"
            summary_parts.append(dissent_summary)

        if consensus.conditions:
            summary_parts.append(
                f"Conditions: {len(consensus.conditions)} requirements"
            )

        return " | ".join(summary_parts)

    async def explain_decision(
        self, consensus: ConsensusResult, perspective: str = "balanced"
    ) -> str:
        """Explain consensus decision from different perspectives"""
        if not self.openai:
            return consensus.reasoning_summary

        try:
            perspective_prompts = {
                "balanced": "Provide a balanced explanation considering all viewpoints",
                "safety": "Explain from a safety-first perspective",
                "user": "Explain focusing on user benefits and experience",
                "business": "Explain the business implications",
                "technical": "Explain the technical considerations",
            }

            response = await self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": f"""Explain this safety consensus decision.
                    {perspective_prompts.get(perspective, perspective_prompts['balanced'])}""",
                    },
                    {
                        "role": "user",
                        "content": f"""Decision: {consensus.final_decision}
                    Reasoning: {consensus.reasoning_summary}
                    Conditions: {consensus.conditions}
                    Dissent: {[v.reasoning for v in consensus.dissenting_opinions]}""",
                    },
                ],
                max_tokens=400,
                temperature=0.6,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Failed to explain decision: {e}")
            return consensus.reasoning_summary

    async def simulate_agent_debate(
        self, proposal: Dict[str, Any], context: Dict[str, Any], rounds: int = 3
    ) -> List[Dict[str, Any]]:
        """Simulate agents debating to reach consensus"""
        debate_log = []
        current_positions = {}

        # Initial positions
        for role, agent in self.agents.items():
            initial_vote = await agent.evaluate_proposal(proposal, context)
            current_positions[role] = initial_vote
            debate_log.append(
                {
                    "round": 0,
                    "agent": role.value,
                    "position": initial_vote.decision,
                    "statement": initial_vote.reasoning,
                }
            )

        # Debate rounds
        for round_num in range(1, rounds + 1):
            # Each agent considers others' positions
            for role, agent in self.agents.items():
                if self.openai:
                    try:
                        # Prepare other agents' positions
                        other_positions = {
                            other_role.value: {
                                "decision": vote.decision,
                                "reasoning": vote.reasoning[
                                    :200
                                ],  # Truncate for context
                            }
                            for other_role, vote in current_positions.items()
                            if other_role != role
                        }

                        response = await self.openai.chat.completions.create(
                            model="gpt-4-turbo-preview",
                            messages=[
                                {
                                    "role": "system",
                                    "content": f"""You are {agent.role_prompts[role]}
                                Consider other agents' positions and potentially update your view.""",
                                },
                                {
                                    "role": "user",
                                    "content": f"""Other agents' positions: {json.dumps(other_positions)}
                                Should you maintain or modify your position?""",
                                },
                            ],
                            max_tokens=200,
                            temperature=0.5,
                        )

                        debate_log.append(
                            {
                                "round": round_num,
                                "agent": role.value,
                                "statement": response.choices[0].message.content,
                            }
                        )

                    except Exception as e:
                        logger.error(f"Debate simulation failed for {role}: {e}")

        return debate_log

    def get_agent_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for each agent"""
        metrics = {}

        for role, agent in self.agents.items():
            if agent.decision_history:
                agent_metrics = {
                    "total_decisions": len(agent.decision_history),
                    "decision_distribution": self._calculate_decision_distribution(
                        agent.decision_history
                    ),
                    "average_confidence": statistics.mean(
                        v.confidence for v in agent.decision_history
                    ),
                    "dissent_rate": sum(
                        1 for v in agent.decision_history if v.dissent_points
                    )
                    / len(agent.decision_history),
                }
                metrics[role.value] = agent_metrics

        return metrics

    def _calculate_decision_distribution(
        self, votes: List[AgentVote]
    ) -> Dict[str, float]:
        """Calculate distribution of decisions"""
        counts = {"approve": 0, "reject": 0, "conditional": 0}

        for vote in votes:
            counts[vote.decision] += 1

        total = len(votes)
        return {
            decision: count / total if total > 0 else 0
            for decision, count in counts.items()
        }

    async def create_safety_constitution(self) -> List[str]:
        """Have agents collaborate to create safety constitution"""
        if not self.openai:
            return ["Safety first", "User consent required", "Protect vulnerable users"]

        constitution_points = []

        # Each agent proposes constitutional principles
        for role, agent in self.agents.items():
            try:
                response = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": f"{agent.role_prompts[role]}\nPropose 3 constitutional principles for NIAS.",
                        },
                        {
                            "role": "user",
                            "content": "What principles should guide all NIAS operations?",
                        },
                    ],
                    max_tokens=200,
                    temperature=0.7,
                )

                # Extract principles (would need better parsing in production)
                principles = response.choices[0].message.content.split("\n")
                constitution_points.extend([p.strip() for p in principles if p.strip()])

            except Exception as e:
                logger.error(f"Failed to get principles from {role}: {e}")

        # Deduplicate and consolidate
        unique_principles = list(set(constitution_points))

        return unique_principles[:10]  # Top 10 principles

    def get_consensus_statistics(self) -> Dict[str, Any]:
        """Get statistics about consensus decisions"""
        if not self.consensus_history:
            return {"total_decisions": 0}

        total = len(self.consensus_history)

        stats = {
            "total_decisions": total,
            "consensus_rate": sum(
                1 for c in self.consensus_history if c.consensus_reached
            )
            / total,
            "average_confidence": statistics.mean(
                c.confidence for c in self.consensus_history
            ),
            "decision_distribution": {
                "approve": sum(
                    1 for c in self.consensus_history if c.final_decision == "approve"
                )
                / total,
                "reject": sum(
                    1 for c in self.consensus_history if c.final_decision == "reject"
                )
                / total,
                "conditional": sum(
                    1
                    for c in self.consensus_history
                    if c.final_decision == "conditional"
                )
                / total,
                "escalate": sum(
                    1 for c in self.consensus_history if c.final_decision == "escalate"
                )
                / total,
            },
            "human_review_rate": sum(
                1 for c in self.consensus_history if c.requires_human_review
            )
            / total,
            "average_dissent_rate": statistics.mean(
                len(c.dissenting_opinions) / sum(c.vote_breakdown.values())
                for c in self.consensus_history
                if sum(c.vote_breakdown.values()) > 0
            ),
        }

        return stats

    async def emergency_consensus(
        self, action_type: str, action_data: Dict[str, Any], context: Dict[str, Any]
    ) -> ConsensusResult:
        """Fast consensus for emergency situations"""
        # Use only core agents for speed
        core_agents = [
            self.agents[AgentRole.SAFETY_ADVOCATE],
            self.agents[AgentRole.ETHICS_ADVOCATE],
            self.agents[AgentRole.USER_ADVOCATE],
        ]

        # Set emergency context
        context["emergency"] = True
        context["time_constraint"] = "immediate"

        # Get rapid votes
        proposal = {
            "action_type": action_type,
            "action_data": action_data,
            "emergency": True,
        }

        votes = await self._collect_votes(proposal, context, core_agents)

        # Quick consensus with lower thresholds
        consensus = self._analyze_consensus(votes, context)

        # Simple summary for emergency
        consensus.reasoning_summary = f"Emergency decision: {consensus.final_decision} (confidence: {consensus.confidence:.1%})"

        return consensus


# Singleton instance
_consensus_instance = None


def get_multi_agent_consensus(
    openai_api_key: Optional[str] = None,
) -> MultiAgentSafetyConsensus:
    """Get or create the singleton Multi-Agent Consensus instance"""
    global _consensus_instance
    if _consensus_instance is None:
        _consensus_instance = MultiAgentSafetyConsensus(openai_api_key)
    return _consensus_instance
