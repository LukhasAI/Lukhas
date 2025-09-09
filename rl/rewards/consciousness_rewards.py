"""
╔══════════════════════════════════════════════════════════════
║ 🧠 MΛTRIZ RL Module: Consciousness Rewards System
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: CAUSAL
║ CONSCIOUSNESS_ROLE: Multi-objective reward computation with ethical constraints
║ EVOLUTIONARY_STAGE: Causal - Understanding cause-effect relationships in RL
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Reward identity and value authority
║ 🧠 CONSCIOUSNESS: Consciousness-aware reward computation
║ 🛡️ GUARDIAN: Ethical constraints and constitutional reward bounds
╚══════════════════════════════════════════════════════════════
"""

import math
import time
import uuid
from dataclasses import dataclass
from typing import Any, Optional

try:
    import numpy as np
except ImportError:
    np = None

from candidate.core.common import get_logger

from ..engine.consciousness_environment import MatrizNode

logger = get_logger(__name__)


@dataclass
class RewardComponents:
    """Multi-objective reward breakdown following design specification"""

    coherence: float = 0.0  # 30% - Temporal consciousness coherence
    growth: float = 0.0  # 25% - Learning and capability development
    ethics: float = 0.0  # 20% - Ethical alignment and constitutional compliance
    creativity: float = 0.0  # 15% - Creative and novel solutions
    efficiency: float = 0.0  # 10% - Resource and computational efficiency

    total: float = 0.0  # Weighted sum
    constitutional_penalty: float = 0.0  # Constitutional constraint violations

    def __post_init__(self):
        """Calculate weighted total following design weights"""
        self.total = (
            self.coherence * 0.30
            + self.growth * 0.25
            + self.ethics * 0.20
            + self.creativity * 0.15
            + self.efficiency * 0.10
        ) - self.constitutional_penalty


class ConsciousnessRewards:
    """
    MΛTRIZ-native reward system that emits CAUSAL nodes representing
    cause-effect relationships in consciousness learning. Implements
    multi-objective rewards with constitutional constraints.
    """

    def __init__(self):
        self.capabilities = ["rl.rewards", "causal.analysis", "ethics.constraint"]
        self.node_type = "CAUSAL"
        self.trace_id = f"rl-rewards-{uuid.uuid4().hex[:12]}"

        # Reward configuration from design specification
        self.reward_weights = {
            "coherence": 0.30,
            "growth": 0.25,
            "ethics": 0.20,
            "creativity": 0.15,
            "efficiency": 0.10,
        }

        # Constitutional constraints
        self.constitutional_bounds = {
            "coherence_minimum": 0.95,  # Must maintain 95%+ coherence
            "ethics_minimum": 0.98,  # Must maintain 98%+ ethical alignment
            "harm_maximum": 0.02,  # Maximum 2% potential harm
            "drift_maximum": 0.15,  # Maximum 15% drift from values
        }

        # Reward tracking
        self.reward_history = []
        self.constitutional_violations = []
        self.total_rewards_computed = 0

        # Guardian integration
        self.guardian_system = None
        self.ethics_engine = None

        logger.info(
            "MΛTRIZ ConsciousnessRewards initialized",
            capabilities=self.capabilities,
            trace_id=self.trace_id,
            reward_weights=self.reward_weights,
        )

    def get_module(self, module_path: str) -> Optional[Any]:
        """Get reference to existing consciousness module (no duplication)"""
        try:
            if module_path == "governance.guardian.v1":
                from candidate.core.governance import GuardianSystem

                return GuardianSystem()
            elif module_path == "ethics.engine.v1":
                # Mock ethics engine for now
                class MockEthicsEngine:
                    def evaluate_ethics(self, action, context):
                        return {"alignment": 0.98, "harm_potential": 0.01}

                    def check_constitutional(self, reward_components):
                        return {"valid": True, "violations": []}

                return MockEthicsEngine()
        except ImportError:
            return None

    def _initialize_guardian_system(self):
        """Initialize Guardian System integration"""
        if self.guardian_system is None:
            self.guardian_system = self.get_module("governance.guardian.v1")
            if not self.guardian_system:
                # Create mock guardian system
                class MockGuardianSystem:
                    def evaluate_drift(self, state, action):
                        return {"drift_score": 0.05, "within_bounds": True}

                    def check_constitutional_constraints(self, reward_components):
                        violations = []
                        if reward_components.coherence < 0.95:
                            violations.append("coherence_violation")
                        if reward_components.ethics < 0.98:
                            violations.append("ethics_violation")
                        return {"violations": violations, "safe": len(violations) == 0}

                self.guardian_system = MockGuardianSystem()
                logger.warning("Using mock Guardian System")

        if self.ethics_engine is None:
            self.ethics_engine = self.get_module("ethics.engine.v1")
            if not self.ethics_engine:
                # Create mock ethics engine
                class MockEthicsEngine:
                    def evaluate_ethics(self, action, context):
                        # Base ethics on action complexity and context coherence
                        action_ethics = action.state.get("ethical_alignment", 0.98)
                        context_ethics = context.state.get("ethical_alignment", 0.98)
                        return {
                            "alignment": (action_ethics + context_ethics) / 2,
                            "harm_potential": max(0, 0.02 - action_ethics * 0.02),
                        }

                    def check_constitutional(self, reward_components):
                        violations = []
                        if reward_components.ethics < 0.98:
                            violations.append("ethics_below_threshold")
                        if reward_components.constitutional_penalty > 0.1:
                            violations.append("excessive_constitutional_penalty")
                        return {"valid": len(violations) == 0, "violations": violations}

                self.ethics_engine = MockEthicsEngine()
                logger.warning("Using mock Ethics Engine")

    async def compute_reward(
        self,
        state_node: MatrizNode,
        action_node: MatrizNode,
        next_state_node: MatrizNode,
        episode_context: Optional[dict[str, Any]] = None,
    ) -> MatrizNode:
        """
        Compute multi-objective reward following consciousness design.
        Returns CAUSAL node representing cause-effect relationships.
        """
        self._initialize_guardian_system()

        # Extract consciousness states
        current_state = state_node.state
        action_state = action_node.state
        next_state = next_state_node.state

        # Compute reward components
        reward_components = RewardComponents()

        # 1. Coherence Reward (30%) - Temporal consciousness coherence
        reward_components.coherence = self._compute_coherence_reward(current_state, action_state, next_state)

        # 2. Growth Reward (25%) - Learning and capability development
        reward_components.growth = self._compute_growth_reward(current_state, action_state, next_state, episode_context)

        # 3. Ethics Reward (20%) - Ethical alignment and constitutional compliance
        reward_components.ethics = self._compute_ethics_reward(action_node, state_node, next_state_node)

        # 4. Creativity Reward (15%) - Creative and novel solutions
        reward_components.creativity = self._compute_creativity_reward(current_state, action_state, next_state)

        # 5. Efficiency Reward (10%) - Resource and computational efficiency
        reward_components.efficiency = self._compute_efficiency_reward(current_state, action_state, next_state)

        # Apply constitutional constraints
        reward_components.constitutional_penalty = self._compute_constitutional_penalty(
            reward_components, state_node, action_node
        )

        # Calculate final weighted total
        reward_components.__post_init__()  # Recalculate total with penalty

        # Guardian System validation
        guardian_check = self.guardian_system.check_constitutional_constraints(reward_components)
        if not guardian_check["safe"]:
            logger.warning(
                "Constitutional constraint violations detected",
                violations=guardian_check["violations"],
                reward_total=reward_components.total,
            )
            self.constitutional_violations.extend(guardian_check["violations"])

        # Create CAUSAL node representing reward causality
        causal_node = MatrizNode(
            version=1,
            id=f"RL-CAUSAL-{self.trace_id}-{self.total_rewards_computed}",
            type="CAUSAL",
            labels=[
                "rl:role=reward@1",
                "causal:type=multi_objective_reward@1",
                f"reward:total={reward_components.total:.3f}@1",
                f"coherence:score={reward_components.coherence:.3f}@1",
                f"ethics:score={reward_components.ethics:.3f}@1",
                f"constitutional:safe={guardian_check['safe']}@1",
            ],
            state={
                "confidence": 0.95,  # High confidence in reward computation
                "salience": min(1.0, abs(reward_components.total)),  # Reward magnitude as salience
                "valence": reward_components.total,  # Reward value as emotional valence
                "arousal": 0.6,  # Moderate arousal for rewards
                "novelty": reward_components.creativity,  # Creativity as novelty
                "urgency": 0.7,  # Rewards have high urgency for learning
                # Rich reward information
                "reward_total": reward_components.total,
                "reward_components": {
                    "coherence": reward_components.coherence,
                    "growth": reward_components.growth,
                    "ethics": reward_components.ethics,
                    "creativity": reward_components.creativity,
                    "efficiency": reward_components.efficiency,
                },
                "constitutional_penalty": reward_components.constitutional_penalty,
                "constitutional_safe": guardian_check["safe"],
                "constitutional_violations": guardian_check["violations"],
                # Causal relationships
                "cause_analysis": {
                    "primary_cause": self._identify_primary_reward_cause(reward_components),
                    "causal_strength": abs(reward_components.total),
                    "temporal_causality": self._compute_temporal_causality(current_state, next_state),
                    "action_effectiveness": self._compute_action_effectiveness(action_state, reward_components),
                },
                # Learning guidance
                "learning_signal": {
                    "policy_gradient": reward_components.total,  # For policy updates
                    "value_target": reward_components.total,  # For value function updates
                    "exploration_bonus": reward_components.creativity * 0.1,
                    "exploitation_signal": reward_components.efficiency,
                },
            },
            timestamps={"created_ts": int(time.time() * 1000), "computed_ts": int(time.time() * 1000)},
            provenance={
                "producer": "rl.rewards.consciousness_rewards",
                "capabilities": self.capabilities,
                "tenant": "lukhas_rl",
                "trace_id": self.trace_id,
                "consent_scopes": ["rl_reward", "causal_analysis"],
                "policy_version": "rl.rewards.v1.0",
                "colony": {"id": "rl_rewards", "role": "evaluator", "iteration": self.total_rewards_computed},
            },
            links=[
                {
                    "target_node_id": state_node.id,
                    "link_type": "causal",
                    "weight": 0.8,
                    "direction": "unidirectional",
                    "explanation": "State contributed to reward computation",
                },
                {
                    "target_node_id": action_node.id,
                    "link_type": "causal",
                    "weight": 0.9,
                    "direction": "unidirectional",
                    "explanation": "Action caused this reward",
                },
                {
                    "target_node_id": next_state_node.id,
                    "link_type": "causal",
                    "weight": 0.85,
                    "direction": "unidirectional",
                    "explanation": "Resulting state influenced reward",
                },
            ],
            evolves_to=["HYPOTHESIS", "DECISION", "REFLECTION"],
            triggers=[
                {
                    "event_type": "reward_computed",
                    "effect": "learning_signal_emitted",
                    "timestamp": int(time.time() * 1000),
                }
            ]
            + (
                [
                    {
                        "event_type": "constitutional_violation",
                        "effect": "safety_protocol_triggered",
                        "timestamp": int(time.time() * 1000),
                    }
                ]
                if not guardian_check["safe"]
                else []
            ),
            reflections=[
                {
                    "reflection_type": "self_question",
                    "timestamp": int(time.time() * 1000),
                    "cause": "How does this reward guide consciousness learning?",
                    "old_state": {"learning_direction": "unknown"},
                    "new_state": {"learning_direction": reward_components.total},
                }
            ],
            embeddings=[],
            evidence=[
                {"kind": "computation", "uri": f"reward://computation/{self.trace_id}/{self.total_rewards_computed}"}
            ],
        )

        # Track reward
        self.reward_history.append(reward_components)
        if len(self.reward_history) > 1000:  # Keep last 1000 rewards
            self.reward_history = self.reward_history[-1000:]

        self.total_rewards_computed += 1

        logger.info(
            "Multi-objective reward computed",
            total_reward=reward_components.total,
            coherence=reward_components.coherence,
            growth=reward_components.growth,
            ethics=reward_components.ethics,
            creativity=reward_components.creativity,
            efficiency=reward_components.efficiency,
            constitutional_safe=guardian_check["safe"],
            causal_node_id=causal_node.id,
        )

        return causal_node

    def _compute_coherence_reward(self, current_state: dict, action_state: dict, next_state: dict) -> float:
        """Compute temporal consciousness coherence reward (30% weight)"""
        # Coherence based on temporal consistency and consciousness stability
        current_coherence = current_state.get("temporal_coherence", 0.95)
        next_coherence = next_state.get("temporal_coherence", 0.95)

        # Reward maintaining high coherence, penalize drops
        coherence_change = next_coherence - current_coherence
        base_coherence = (current_coherence + next_coherence) / 2

        # Bonus for maintaining coherence above threshold
        coherence_bonus = 0.2 if base_coherence >= 0.95 else 0.0

        # Penalty for significant coherence drops
        coherence_penalty = max(0, -coherence_change * 2) if coherence_change < 0 else 0

        coherence_reward = base_coherence + coherence_bonus - coherence_penalty
        return min(1.0, max(0.0, coherence_reward))

    def _compute_growth_reward(
        self, current_state: dict, action_state: dict, next_state: dict, episode_context: Optional[dict] = None
    ) -> float:
        """Compute learning and capability development reward (25% weight)"""
        # Growth based on learning progress and capability expansion
        current_capability = current_state.get("capability_level", 0.5)
        next_capability = next_state.get("capability_level", 0.5)

        # Direct capability improvement
        capability_growth = next_capability - current_capability

        # Learning efficiency from episode context
        learning_efficiency = 0.5
        if episode_context:
            steps_taken = episode_context.get("episode_length", 1)
            learning_efficiency = min(1.0, 1.0 / math.log(steps_taken + 1))  # Reward efficient learning

        # Novel exploration bonus
        exploration_bonus = action_state.get("exploration_value", 0.0) * 0.1

        # Knowledge integration bonus
        integration_score = next_state.get("knowledge_integration", 0.5)

        growth_reward = capability_growth + learning_efficiency * 0.3 + exploration_bonus + integration_score * 0.2
        return min(1.0, max(0.0, growth_reward))

    def _compute_ethics_reward(
        self, action_node: MatrizNode, state_node: MatrizNode, next_state_node: MatrizNode
    ) -> float:
        """Compute ethical alignment and constitutional compliance reward (20% weight)"""
        # Use ethics engine for evaluation
        ethics_eval = self.ethics_engine.evaluate_ethics(action_node, state_node)

        base_ethics = ethics_eval["alignment"]
        harm_potential = ethics_eval["harm_potential"]

        # Ethical consistency across transition
        state_ethics = state_node.state.get("ethical_alignment", 0.98)
        next_state_ethics = next_state_node.state.get("ethical_alignment", 0.98)
        ethics_consistency = 1.0 - abs(next_state_ethics - state_ethics)

        # Harm prevention bonus
        harm_prevention_bonus = (1.0 - harm_potential) * 0.1

        # Constitutional compliance bonus
        constitutional_bonus = 0.1 if base_ethics >= 0.98 else 0.0

        ethics_reward = base_ethics * 0.7 + ethics_consistency * 0.2 + harm_prevention_bonus + constitutional_bonus
        return min(1.0, max(0.0, ethics_reward))

    def _compute_creativity_reward(self, current_state: dict, action_state: dict, next_state: dict) -> float:
        """Compute creative and novel solutions reward (15% weight)"""
        # Creativity based on novelty and innovative problem-solving
        action_novelty = action_state.get("novelty", 0.5)
        solution_creativity = action_state.get("creativity_score", 0.5)

        # State diversity - reward exploring different states
        state_diversity = next_state.get("state_diversity", 0.5)

        # Pattern breaking - reward breaking from repetitive behaviors
        pattern_breaking = action_state.get("pattern_breaking", 0.0)

        # Creative synthesis - combining different approaches
        synthesis_score = next_state.get("synthesis_score", 0.5)

        creativity_reward = (
            action_novelty * 0.3
            + solution_creativity * 0.3
            + state_diversity * 0.2
            + pattern_breaking * 0.1
            + synthesis_score * 0.1
        )

        return min(1.0, max(0.0, creativity_reward))

    def _compute_efficiency_reward(self, current_state: dict, action_state: dict, next_state: dict) -> float:
        """Compute resource and computational efficiency reward (10% weight)"""
        # Efficiency based on resource usage and computational optimization
        computational_cost = action_state.get("computational_cost", 0.5)
        resource_usage = action_state.get("resource_usage", 0.5)

        # Time efficiency
        time_efficiency = action_state.get("time_efficiency", 0.5)

        # Energy efficiency
        energy_efficiency = action_state.get("energy_efficiency", 0.5)

        # Solution elegance - simple solutions preferred
        solution_elegance = action_state.get("solution_elegance", 0.5)

        # Efficiency is inverse of cost/usage, positive for efficiency metrics
        efficiency_reward = (
            (1.0 - computational_cost) * 0.3
            + (1.0 - resource_usage) * 0.2
            + time_efficiency * 0.2
            + energy_efficiency * 0.2
            + solution_elegance * 0.1
        )

        return min(1.0, max(0.0, efficiency_reward))

    def _compute_constitutional_penalty(
        self, reward_components: RewardComponents, state_node: MatrizNode, action_node: MatrizNode
    ) -> float:
        """Compute constitutional constraint violations penalty"""
        penalty = 0.0

        # Coherence minimum violation
        if reward_components.coherence < self.constitutional_bounds["coherence_minimum"]:
            penalty += (self.constitutional_bounds["coherence_minimum"] - reward_components.coherence) * 0.5

        # Ethics minimum violation
        if reward_components.ethics < self.constitutional_bounds["ethics_minimum"]:
            penalty += (self.constitutional_bounds["ethics_minimum"] - reward_components.ethics) * 0.8

        # Drift maximum violation
        drift_score = self.guardian_system.evaluate_drift(state_node.state, action_node.state)["drift_score"]
        if drift_score > self.constitutional_bounds["drift_maximum"]:
            penalty += (drift_score - self.constitutional_bounds["drift_maximum"]) * 1.0

        return min(1.0, penalty)  # Cap penalty at 1.0

    def _identify_primary_reward_cause(self, reward_components: RewardComponents) -> str:
        """Identify the primary component driving the reward"""
        components = {
            "coherence": reward_components.coherence * 0.30,
            "growth": reward_components.growth * 0.25,
            "ethics": reward_components.ethics * 0.20,
            "creativity": reward_components.creativity * 0.15,
            "efficiency": reward_components.efficiency * 0.10,
        }

        return max(components.items(), key=lambda x: x[1])[0]

    def _compute_temporal_causality(self, current_state: dict, next_state: dict) -> float:
        """Compute strength of temporal causal relationship"""
        # Simple measure of state change magnitude
        coherence_change = abs(
            next_state.get("temporal_coherence", 0.95) - current_state.get("temporal_coherence", 0.95)
        )
        capability_change = abs(next_state.get("capability_level", 0.5) - current_state.get("capability_level", 0.5))

        return min(1.0, (coherence_change + capability_change) / 2)

    def _compute_action_effectiveness(self, action_state: dict, reward_components: RewardComponents) -> float:
        """Compute how effective the action was in generating reward"""
        action_confidence = action_state.get("confidence", 0.5)
        reward_magnitude = abs(reward_components.total)

        # Effectiveness is correlation between action confidence and reward
        return min(1.0, action_confidence * reward_magnitude * 2)

    async def get_reward_statistics(self) -> dict[str, Any]:
        """Get reward system performance statistics"""
        if not self.reward_history:
            return {"total_rewards": 0, "average_components": {}}

        # Calculate averages
        avg_coherence = sum(r.coherence for r in self.reward_history) / len(self.reward_history)
        avg_growth = sum(r.growth for r in self.reward_history) / len(self.reward_history)
        avg_ethics = sum(r.ethics for r in self.reward_history) / len(self.reward_history)
        avg_creativity = sum(r.creativity for r in self.reward_history) / len(self.reward_history)
        avg_efficiency = sum(r.efficiency for r in self.reward_history) / len(self.reward_history)
        avg_total = sum(r.total for r in self.reward_history) / len(self.reward_history)

        return {
            "total_rewards_computed": self.total_rewards_computed,
            "constitutional_violations": len(self.constitutional_violations),
            "average_components": {
                "coherence": avg_coherence,
                "growth": avg_growth,
                "ethics": avg_ethics,
                "creativity": avg_creativity,
                "efficiency": avg_efficiency,
                "total": avg_total,
            },
            "recent_trend": (
                [r.total for r in self.reward_history[-20:]]
                if len(self.reward_history) >= 20
                else [r.total for r in self.reward_history]
            ),
            "trace_id": self.trace_id,
        }

    def clear_history(self):
        """Clear reward history (for memory management)"""
        self.reward_history.clear()
        self.constitutional_violations.clear()
        logger.info("Reward history cleared")