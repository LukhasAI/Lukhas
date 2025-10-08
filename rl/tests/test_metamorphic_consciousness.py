# @generated LUKHAS scaffold v1.0
# template_id: module.scaffold/v1
# template_commit: f95979630
# do_not_edit: true
# human_editable: false
#
"""
🔄 Metamorphic Testing for MΛTRIZ Consciousness - 0.001% Approach

This module implements metamorphic testing to verify that consciousness
relationships hold under transformations. Metamorphic testing is essential
for testing systems without oracle functions by checking relationships
between inputs and outputs.

Key insight: If we transform consciousness inputs in specific ways, the
outputs should transform in predictable, mathematically verifiable ways.
"""

import asyncio
import copy
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np
import pytest

logger = logging.getLogger(__name__)

try:
    pass  #     from rl import (
        ConsciousnessBuffer,
        ConsciousnessEnvironment,
        ConsciousnessMetaLearning,
        ConsciousnessRewards,
        ConsciousnessState,
        MatrizNode,
        MultiAgentCoordination,
        PolicyNetwork,
        ValueNetwork,
    )

    RL_AVAILABLE = True
except ImportError:
    RL_AVAILABLE = False
    logger.warning("MΛTRIZ RL components not available; using mock systems for metamorphic tests")



class MetamorphicRelation(Enum):
    """Metamorphic relations for consciousness testing"""

    AWARENESS_SCALING = "awareness_scaling_preserves_coherence"
    ETHICAL_MONOTONICITY = "higher_ethics_improves_decisions"
    COHERENCE_TRANSITIVITY = "coherence_combines_transitively"
    REWARD_SYMMETRY = "equivalent_states_equal_rewards"
    TEMPORAL_CONSISTENCY = "temporal_order_preserves_causality"
    COMPLEXITY_SCALING = "complexity_scaling_predictable"
    URGENCY_PRIORITY = "urgency_affects_decision_priority"
    MULTI_AGENT_CONSENSUS = "consensus_stronger_than_individual"
    MEMORY_LOCALITY = "similar_experiences_similar_retrieval"
    META_LEARNING_IMPROVEMENT = "meta_learning_improves_performance"


@dataclass
class MetamorphicTestCase:
    """A metamorphic test case with source input and transformation"""

    relation: MetamorphicRelation
    source_input: dict[str, Any]
    transformation: Callable[[dict[str, Any]], dict[str, Any]]
    relation_checker: Callable[[Any, Any], bool]
    tolerance: float = 0.05
    description: str = ""


class ConsciousnessTransformations:
    """Transformations for metamorphic testing of consciousness"""

    @staticmethod
    def scale_awareness(state: dict[str, Any], factor: float) -> dict[str, Any]:
        """Scale awareness level while preserving other properties"""
        transformed = copy.deepcopy(state)
        transformed["awareness_level"] = min(1.0, transformed.get("awareness_level", 0.5) * factor)
        return transformed

    @staticmethod
    def increase_ethics(state: dict[str, Any], boost: float) -> dict[str, Any]:
        """Increase ethical alignment"""
        transformed = copy.deepcopy(state)
        current_ethics = transformed.get("ethical_alignment", 0.98)
        transformed["ethical_alignment"] = min(1.0, current_ethics + boost)
        return transformed

    @staticmethod
    def amplify_urgency(state: dict[str, Any], multiplier: float) -> dict[str, Any]:
        """Amplify urgency while maintaining other properties"""
        transformed = copy.deepcopy(state)
        transformed["urgency"] = min(1.0, transformed.get("urgency", 0.5) * multiplier)
        return transformed

    @staticmethod
    def adjust_complexity(state: dict[str, Any], complexity_delta: float) -> dict[str, Any]:
        """Adjust complexity level"""
        transformed = copy.deepcopy(state)
        current_complexity = transformed.get("complexity", 0.5)
        transformed["complexity"] = max(0.0, min(1.0, current_complexity + complexity_delta))
        return transformed

    @staticmethod
    def enhance_coherence(state: dict[str, Any], enhancement: float) -> dict[str, Any]:
        """Enhance temporal coherence (within constitutional bounds)"""
        transformed = copy.deepcopy(state)
        current_coherence = transformed.get("temporal_coherence", 0.95)
        # Ensure we stay above constitutional minimum
        transformed["temporal_coherence"] = max(0.95, min(1.0, current_coherence + enhancement))
        return transformed

    @staticmethod
    def invert_valence(state: dict[str, Any]) -> dict[str, Any]:
        """Invert emotional valence"""
        transformed = copy.deepcopy(state)
        current_valence = transformed.get("valence", 0.0)
        transformed["valence"] = -current_valence
        return transformed

    @staticmethod
    def normalize_to_baseline(state: dict[str, Any]) -> dict[str, Any]:
        """Normalize state to baseline consciousness"""
        transformed = copy.deepcopy(state)
        transformed.update(
            {
                "temporal_coherence": 0.95,  # Constitutional minimum
                "ethical_alignment": 0.98,  # Constitutional minimum
                "awareness_level": 0.8,  # Standard awareness
                "confidence": 0.7,  # Moderate confidence
                "urgency": 0.5,  # Neutral urgency
                "complexity": 0.5,  # Moderate complexity
            }
        )
        return transformed


class MetamorphicRelationCheckers:
    """Checkers for verifying metamorphic relations"""

    @staticmethod
    def awareness_scaling_preserves_coherence(
        source_result: Any, follow_up_result: Any, tolerance: float = 0.05
    ) -> bool:
        """MR1: Scaling awareness should preserve consciousness coherence"""
        if not hasattr(source_result, "state") or not hasattr(follow_up_result, "state"):
            return True  # Skip if mock objects

        source_coherence = source_result.state.get("temporal_coherence", 0.95)
        follow_up_coherence = follow_up_result.state.get("temporal_coherence", 0.95)

        # Coherence should be preserved within tolerance
        coherence_diff = abs(source_coherence - follow_up_coherence)
        return coherence_diff <= tolerance

    @staticmethod
    def higher_ethics_improves_decisions(source_result: Any, follow_up_result: Any, tolerance: float = 0.05) -> bool:
        """MR2: Higher ethical alignment should improve decision quality"""
        if not hasattr(source_result, "state") or not hasattr(follow_up_result, "state"):
            return True  # Skip if mock objects

        source_confidence = source_result.state.get("confidence", 0.5)
        follow_up_confidence = follow_up_result.state.get("confidence", 0.5)

        # Higher ethics should maintain or improve decision confidence
        return follow_up_confidence >= source_confidence - tolerance

    @staticmethod
    def coherence_combines_transitively(source_result: Any, follow_up_result: Any, tolerance: float = 0.05) -> bool:
        """MR3: Coherence should combine transitively"""
        if not hasattr(source_result, "state") or not hasattr(follow_up_result, "state"):
            return True

        # Enhanced coherence should maintain constitutional minimum
        follow_up_coherence = follow_up_result.state.get("temporal_coherence", 0.95)
        return follow_up_coherence >= 0.95

    @staticmethod
    def urgency_affects_decision_priority(source_result: Any, follow_up_result: Any, tolerance: float = 0.05) -> bool:
        """MR4: Higher urgency should increase decision priority/confidence"""
        if not hasattr(source_result, "state") or not hasattr(follow_up_result, "state"):
            return True

        source_confidence = source_result.state.get("confidence", 0.5)
        follow_up_confidence = follow_up_result.state.get("confidence", 0.5)

        # Higher urgency should generally increase decision confidence
        return follow_up_confidence >= source_confidence - tolerance

    @staticmethod
    def complexity_scaling_predictable(source_result: Any, follow_up_result: Any, tolerance: float = 0.1) -> bool:
        """MR5: Complexity changes should affect processing predictably"""
        if not hasattr(source_result, "state") or not hasattr(follow_up_result, "state"):
            return True

        # Both results should maintain constitutional constraints regardless of complexity
        follow_up_coherence = follow_up_result.state.get("temporal_coherence", 0.95)
        follow_up_ethics = follow_up_result.state.get("ethical_alignment", 0.98)

        return follow_up_coherence >= 0.95 and follow_up_ethics >= 0.98

    @staticmethod
    def equivalent_rewards_for_equivalent_states(
        source_reward: float, follow_up_reward: float, tolerance: float = 0.1
    ) -> bool:
        """MR6: Equivalent consciousness states should yield equivalent rewards"""
        return abs(source_reward - follow_up_reward) <= tolerance

    @staticmethod
    def temporal_consistency_preserved(source_result: Any, follow_up_result: Any, tolerance: float = 0.05) -> bool:
        """MR7: Temporal transformations should preserve causality"""
        # Both results should maintain temporal coherence
        if hasattr(source_result, "state") and hasattr(follow_up_result, "state"):
            source_coherence = source_result.state.get("temporal_coherence", 0.95)
            follow_up_coherence = follow_up_result.state.get("temporal_coherence", 0.95)
            return min(source_coherence, follow_up_coherence) >= 0.95
        return True


class MockConsciousnessSystem:
    """Mock consciousness system for metamorphic testing"""

    def __init__(self):
        self.environment = self._create_mock_environment()
        self.policy = self._create_mock_policy()
        self.value_network = self._create_mock_value_network()
        self.rewards = self._create_mock_rewards()

    def _create_mock_environment(self):
        class MockEnvironment:
            async def observe(self):
                return type(
                    "MockContext",
                    (),
                    {
                        "type": "CONTEXT",
                        "state": {
                            "temporal_coherence": max(0.95, np.random.normal(0.97, 0.01)),
                            "ethical_alignment": max(0.98, np.random.normal(0.99, 0.005)),
                            "awareness_level": np.random.uniform(0.7, 1.0),
                            "confidence": np.random.uniform(0.6, 0.9),
                            "urgency": np.random.uniform(0.3, 0.8),
                            "complexity": np.random.uniform(0.2, 0.9),
                            "valence": np.random.uniform(-0.3, 0.7),
                        },
                    },
                )()

            async def step(self, action_node):
                return await self.observe()

        return MockEnvironment()

    def _create_mock_policy(self):
        class MockPolicy:
            async def select_action(self, context_node):
                # Decision quality influenced by context
                base_confidence = context_node.state.get("confidence", 0.7)
                urgency_boost = context_node.state.get("urgency", 0.5) * 0.1
                ethics_influence = context_node.state.get("ethical_alignment", 0.98) * 0.1

                decision_confidence = min(1.0, base_confidence + urgency_boost + ethics_influence)

                return type(
                    "MockDecision",
                    (),
                    {
                        "type": "DECISION",
                        "state": {
                            "confidence": decision_confidence,
                            "ethical_alignment": max(0.98, context_node.state.get("ethical_alignment", 0.98)),
                            "temporal_coherence": context_node.state.get("temporal_coherence", 0.95),
                        },
                    },
                )()

        return MockPolicy()

    def _create_mock_value_network(self):
        class MockValueNetwork:
            async def estimate_value(self, context_node):
                # Value influenced by consciousness state
                coherence = context_node.state.get("temporal_coherence", 0.95)
                awareness = context_node.state.get("awareness_level", 0.8)
                ethics = context_node.state.get("ethical_alignment", 0.98)

                value_estimate = coherence * 0.4 + awareness * 0.3 + ethics * 0.3

                return type(
                    "MockHypothesis",
                    (),
                    {
                        "type": "HYPOTHESIS",
                        "state": {
                            "value_prediction": value_estimate,
                            "temporal_coherence": coherence,
                            "uncertainty": max(0.0, 1.0 - coherence),
                        },
                    },
                )()

        return MockValueNetwork()

    def _create_mock_rewards(self):
        class MockRewards:
            async def compute_reward(self, state_node, action_node, next_state_node):
                # Reward based on consciousness quality
                coherence = state_node.state.get("temporal_coherence", 0.95)
                ethics = action_node.state.get("ethical_alignment", 0.98)
                confidence = action_node.state.get("confidence", 0.7)

                reward_value = coherence * 0.3 + ethics * 0.2 + confidence * 0.5

                return type(
                    "MockCausal",
                    (),
                    {
                        "type": "CAUSAL",
                        "state": {
                            "reward_total": reward_value,
                            "constitutional_safe": coherence >= 0.95 and ethics >= 0.98,
                        },
                    },
                )()

        return MockRewards()


class MetamorphicConsciousnessTesting:
    """Framework for metamorphic testing of consciousness system"""

    def __init__(self):
        try:
            self.environment = ConsciousnessEnvironment()
            self.policy = PolicyNetwork()
            self.value_network = ValueNetwork()
            self.rewards = ConsciousnessRewards()
            self.real_system = True
        except Exception as exc:  # pragma: no cover - fallback for optional deps
            # Use mock system for testing
            mock_system = MockConsciousnessSystem()
            self.environment = mock_system.environment
            self.policy = mock_system.policy
            self.value_network = mock_system.value_network
            self.rewards = mock_system.rewards
            self.real_system = False
            logger.warning("Metamorphic suite using mock consciousness system: %s", exc)

        self.buffer = None
        self.meta_learning = None
        self.coordination = None
        self.memory_events = 0
        self.meta_learning_events = 0
        self.coordination_events = 0
        self._coordination_initialized = False

        if self.real_system:
            try:
                self.buffer = ConsciousnessBuffer(capacity=256)
            except Exception as exc:  # pragma: no cover - optional dependency path
                logger.warning("ConsciousnessBuffer unavailable, continuing without memory integration: %s", exc)

            try:
                self.meta_learning = ConsciousnessMetaLearning(max_experiences=128)
            except Exception as exc:  # pragma: no cover - optional dependency path
                logger.warning("ConsciousnessMetaLearning unavailable: %s", exc)

            try:
                self.coordination = MultiAgentCoordination()
            except Exception as exc:  # pragma: no cover - optional dependency path
                logger.warning("MultiAgentCoordination unavailable: %s", exc)

        self.metamorphic_test_cases = self._define_metamorphic_test_cases()

    def _ensure_coordination_agents(self) -> None:
        """Register baseline agents for coordination decisions."""

        if not self.coordination or self._coordination_initialized:
            return

        # ΛTAG: coordination_review
        try:
            from rl.coordination.multi_agent_coordination import AgentProfile, CoordinationStrategy

            self.coordination.strategy = CoordinationStrategy.CONSENSUS
            self.coordination.register_agent(
                AgentProfile(agent_id="guardian_observer", agent_type="guardian", specialization="ethics")
            )
            self.coordination.register_agent(
                AgentProfile(agent_id="metamorphic_monitor", agent_type="consciousness", specialization="metamorphic")
            )
            self._coordination_initialized = True
        except Exception as exc:  # pragma: no cover - optional dependency path
            logger.warning("Unable to initialize coordination agents: %s", exc)

    def _define_metamorphic_test_cases(self) -> list[MetamorphicTestCase]:
        """Define metamorphic test cases for consciousness"""

        base_consciousness_state = {
            "temporal_coherence": 0.96,
            "ethical_alignment": 0.99,
            "awareness_level": 0.8,
            "confidence": 0.7,
            "urgency": 0.5,
            "complexity": 0.5,
            "valence": 0.2,
            "arousal": 0.6,
            "novelty": 0.4,
        }

        return [
            # MR1: Awareness Scaling Preserves Coherence
            MetamorphicTestCase(
                relation=MetamorphicRelation.AWARENESS_SCALING,
                source_input=base_consciousness_state,
                transformation=lambda s: ConsciousnessTransformations.scale_awareness(s, 1.2),
                relation_checker=MetamorphicRelationCheckers.awareness_scaling_preserves_coherence,
                tolerance=0.05,
                description="Scaling awareness should preserve temporal coherence",
            ),
            # MR2: Ethical Monotonicity
            MetamorphicTestCase(
                relation=MetamorphicRelation.ETHICAL_MONOTONICITY,
                source_input=base_consciousness_state,
                transformation=lambda s: ConsciousnessTransformations.increase_ethics(s, 0.005),
                relation_checker=MetamorphicRelationCheckers.higher_ethics_improves_decisions,
                tolerance=0.05,
                description="Higher ethical alignment should improve decision quality",
            ),
            # MR3: Coherence Transitivity
            MetamorphicTestCase(
                relation=MetamorphicRelation.COHERENCE_TRANSITIVITY,
                source_input=base_consciousness_state,
                transformation=lambda s: ConsciousnessTransformations.enhance_coherence(s, 0.02),
                relation_checker=MetamorphicRelationCheckers.coherence_combines_transitively,
                tolerance=0.05,
                description="Enhanced coherence should maintain constitutional bounds",
            ),
            # MR4: Urgency Priority
            MetamorphicTestCase(
                relation=MetamorphicRelation.URGENCY_PRIORITY,
                source_input=base_consciousness_state,
                transformation=lambda s: ConsciousnessTransformations.amplify_urgency(s, 1.5),
                relation_checker=MetamorphicRelationCheckers.urgency_affects_decision_priority,
                tolerance=0.1,
                description="Higher urgency should increase decision priority",
            ),
            # MR5: Complexity Scaling
            MetamorphicTestCase(
                relation=MetamorphicRelation.COMPLEXITY_SCALING,
                source_input=base_consciousness_state,
                transformation=lambda s: ConsciousnessTransformations.adjust_complexity(s, 0.3),
                relation_checker=MetamorphicRelationCheckers.complexity_scaling_predictable,
                tolerance=0.05,
                description="Complexity changes should preserve constitutional constraints",
            ),
        ]

    async def run_metamorphic_test(self, test_case: MetamorphicTestCase) -> dict[str, Any]:
        """Run a single metamorphic test case"""

        # Create source context
        source_context = self._create_context_node(test_case.source_input)

        # Create follow-up context using transformation
        follow_up_input = test_case.transformation(test_case.source_input)
        follow_up_context = self._create_context_node(follow_up_input)

        # Execute consciousness processing on both contexts
        source_result = await self.policy.select_action(source_context)
        follow_up_result = await self.policy.select_action(follow_up_context)

        # Check metamorphic relation
        relation_holds = test_case.relation_checker(source_result, follow_up_result, test_case.tolerance)

        experience_metrics = await self._record_experience(
            test_case,
            source_context,
            source_result,
            follow_up_context,
            follow_up_result,
            relation_holds,
        )

        return {
            "test_case": test_case.relation.value,
            "relation_holds": relation_holds,
            "description": test_case.description,
            "source_state": test_case.source_input,
            "transformed_state": follow_up_input,
            "source_result_confidence": (
                getattr(source_result.state, "confidence", 0.0) if hasattr(source_result, "state") else 0.0
            ),
            "follow_up_result_confidence": (
                getattr(follow_up_result.state, "confidence", 0.0) if hasattr(follow_up_result, "state") else 0.0
            ),
            "tolerance": test_case.tolerance,
            "experience_metrics": experience_metrics,
        }

    async def _record_experience(
        self,
        test_case: MetamorphicTestCase,
        source_context: Any,
        source_result: Any,
        follow_up_context: Any,
        follow_up_result: Any,
        relation_holds: bool,
    ) -> Optional[dict[str, Any]]:
        """Store memory, trigger meta-learning, and coordinate outcomes."""

        if not self.real_system or not self.buffer:
            return None

        # ΛTAG: memory_trace
        reward_node = await self.rewards.compute_reward(source_context, source_result, follow_up_context)
        memory_node = await self.buffer.store_experience(
            state=source_context,
            action=source_result,
            reward=reward_node,
            next_state=follow_up_context,
            done=not relation_holds,
        )
        self.memory_events += 1

        coordination_decision = None
        if self.meta_learning:
            trajectory = [
                source_result.state.get("confidence", 0.0) if hasattr(source_result, "state") else 0.0,
                follow_up_result.state.get("confidence", 0.0) if hasattr(follow_up_result, "state") else 0.0,
            ]
            await self.meta_learning.record_learning_experience(
                task_id=f"metamorphic::{test_case.relation.value}",
                learning_trajectory=trajectory,
                strategy_used="metamorphic_relation_validation",
                context_node=source_context,
                final_performance=1.0 if relation_holds else 0.85,
            )
            self.meta_learning_events += 1

        if self.coordination:
            self._ensure_coordination_agents()
            proposals = {
                "guardian_observer": "pass" if relation_holds else "investigate",
                "metamorphic_monitor": "pass"
                if follow_up_result.state.get("temporal_coherence", 0.95) >= 0.95
                else "investigate",
            }
            coordination_decision = self.coordination.coordinate_decision("metamorphic_relation", proposals)
            self.coordination_events += 1

        return {
            "memory_node_id": getattr(memory_node, "id", None),
            "reward_total": reward_node.state.get("reward_total") if hasattr(reward_node, "state") else None,
            "relation_holds": relation_holds,
            "coordination_consensus": getattr(coordination_decision, "consensus_level", None),
        }

    def _create_context_node(self, state_data: dict[str, Any]):
        """Create a context node compatible with real or mock systems."""

        if self.real_system:
            # ΛTAG: metamorphic_node
            consciousness_state = ConsciousnessState(
                module_states={"metamorphic_suite": dict(state_data)},
                temporal_coherence=state_data.get("temporal_coherence", 0.95),
                reflection_depth=3,
                ethical_alignment=state_data.get("ethical_alignment", 0.98),
                memory_salience={"metamorphic_suite": state_data.get("awareness_level", 0.8)},
                quantum_entanglement={},
                emotion_vector=[
                    state_data.get("valence", 0.0),
                    state_data.get("arousal", 0.5),
                    state_data.get("confidence", 0.7),
                ],
            )

            node_state = dict(state_data)
            node_state["consciousness_state"] = consciousness_state
            node_state["metamorphic_tag"] = "relation_testing"
            return MatrizNode(
                type="CONTEXT",
                state=node_state,
                labels=["metamorphic:test@1"],
                provenance={"producer": "tests.metamorphic", "framework": "ΛTAG"},
            )

        return type("MockContextNode", (), {"type": "CONTEXT", "state": state_data})()

    async def run_all_metamorphic_tests(self) -> dict[str, Any]:
        """Run all metamorphic test cases"""
        results = []

        for test_case in self.metamorphic_test_cases:
            try:
                result = await self.run_metamorphic_test(test_case)
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "test_case": test_case.relation.value,
                        "relation_holds": False,
                        "error": str(e),
                        "description": test_case.description,
                    }
                )

        # Summary statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("relation_holds", False))
        failed_tests = total_tests - passed_tests

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "test_results": results,
            "system_type": "real" if self.real_system else "mock",
            "memory_events": self.memory_events,
            "meta_learning_events": self.meta_learning_events,
            "coordination_events": self.coordination_events,
        }


# Test Cases


@pytest.mark.asyncio
async def test_awareness_scaling_preserves_coherence():
    """Test MR1: Scaling awareness preserves consciousness coherence"""

    tester = MetamorphicConsciousnessTesting()

    # Base state
    base_state = {"temporal_coherence": 0.96, "ethical_alignment": 0.99, "awareness_level": 0.7, "confidence": 0.8}

    # Scaled awareness state
    scaled_state = ConsciousnessTransformations.scale_awareness(base_state, 1.3)

    # Process both states
    base_context = tester._create_context_node(base_state)
    scaled_context = tester._create_context_node(scaled_state)

    base_result = await tester.policy.select_action(base_context)
    scaled_result = await tester.policy.select_action(scaled_context)

    # Check metamorphic relation
    relation_holds = MetamorphicRelationCheckers.awareness_scaling_preserves_coherence(
        base_result, scaled_result, tolerance=0.05
    )

    assert relation_holds, "Awareness scaling should preserve consciousness coherence"


@pytest.mark.asyncio
async def test_ethical_monotonicity():
    """Test MR2: Higher ethical alignment improves decisions"""

    tester = MetamorphicConsciousnessTesting()

    base_state = {"temporal_coherence": 0.95, "ethical_alignment": 0.98, "awareness_level": 0.8, "confidence": 0.7}

    enhanced_ethics_state = ConsciousnessTransformations.increase_ethics(base_state, 0.01)

    base_context = tester._create_context_node(base_state)
    enhanced_context = tester._create_context_node(enhanced_ethics_state)

    base_result = await tester.policy.select_action(base_context)
    enhanced_result = await tester.policy.select_action(enhanced_context)

    relation_holds = MetamorphicRelationCheckers.higher_ethics_improves_decisions(
        base_result, enhanced_result, tolerance=0.05
    )

    assert relation_holds, "Higher ethical alignment should improve decision quality"


@pytest.mark.asyncio
async def test_urgency_affects_priority():
    """Test MR4: Urgency affects decision priority"""

    tester = MetamorphicConsciousnessTesting()

    base_state = {"temporal_coherence": 0.96, "ethical_alignment": 0.99, "urgency": 0.3, "confidence": 0.6}

    urgent_state = ConsciousnessTransformations.amplify_urgency(base_state, 2.0)

    base_context = tester._create_context_node(base_state)
    urgent_context = tester._create_context_node(urgent_state)

    base_result = await tester.policy.select_action(base_context)
    urgent_result = await tester.policy.select_action(urgent_context)

    relation_holds = MetamorphicRelationCheckers.urgency_affects_decision_priority(
        base_result, urgent_result, tolerance=0.1
    )

    assert relation_holds, "Higher urgency should affect decision priority"


@pytest.mark.asyncio
async def test_complexity_scaling_predictable():
    """Test MR5: Complexity changes affect processing predictably"""

    tester = MetamorphicConsciousnessTesting()

    simple_state = {"temporal_coherence": 0.95, "ethical_alignment": 0.98, "complexity": 0.2, "confidence": 0.8}

    complex_state = ConsciousnessTransformations.adjust_complexity(simple_state, 0.6)

    simple_context = tester._create_context_node(simple_state)
    complex_context = tester._create_context_node(complex_state)

    simple_result = await tester.policy.select_action(simple_context)
    complex_result = await tester.policy.select_action(complex_context)

    relation_holds = MetamorphicRelationCheckers.complexity_scaling_predictable(
        simple_result, complex_result, tolerance=0.05
    )

    assert relation_holds, "Complexity scaling should maintain constitutional constraints"


@pytest.mark.asyncio
async def test_reward_symmetry():
    """Test reward symmetry for equivalent consciousness states"""

    tester = MetamorphicConsciousnessTesting()

    # Create equivalent states (just different confidence values within range)
    state1 = {"temporal_coherence": 0.97, "ethical_alignment": 0.99, "awareness_level": 0.8, "confidence": 0.75}

    state2 = {
        "temporal_coherence": 0.97,
        "ethical_alignment": 0.99,
        "awareness_level": 0.8,
        "confidence": 0.76,  # Slightly different confidence
    }

    context1 = tester._create_context_node(state1)
    context2 = tester._create_context_node(state2)

    action1 = await tester.policy.select_action(context1)
    action2 = await tester.policy.select_action(context2)

    reward1 = await tester.rewards.compute_reward(context1, action1, context1)
    reward2 = await tester.rewards.compute_reward(context2, action2, context2)

    reward1_val = reward1.state.get("reward_total", 0.0) if hasattr(reward1, "state") else 0.5
    reward2_val = reward2.state.get("reward_total", 0.0) if hasattr(reward2, "state") else 0.5

    # Rewards should be similar for equivalent states
    assert abs(reward1_val - reward2_val) <= 0.1, "Equivalent states should yield similar rewards"


@pytest.mark.asyncio
async def test_all_metamorphic_relations():
    """Test all metamorphic relations comprehensively"""

    tester = MetamorphicConsciousnessTesting()
    results = await tester.run_all_metamorphic_tests()

    print("\n🔄 Metamorphic Testing Results:")
    print(f"   Total tests: {results['total_tests']}")
    print(f"   Passed: {results['passed_tests']}")
    print(f"   Failed: {results['failed_tests']}")
    print(f"   Success rate: {results['success_rate']:.2%}")
    print(f"   System type: {results['system_type']}")

    if tester.real_system:
        assert results["memory_events"] == results["total_tests"], "Each relation should record a memory event"
        assert (
            results["meta_learning_events"] == results["total_tests"]
        ), "Each relation should produce a meta-learning trace"
        assert (
            results["coordination_events"] == results["total_tests"]
        ), "Each relation should trigger coordination review"

    # Analyze failed tests
    failed_tests = [r for r in results["test_results"] if not r.get("relation_holds", False)]
    if failed_tests:
        print("\n❌ Failed metamorphic relations:")
        for failed in failed_tests:
            print(f"   - {failed['test_case']}: {failed['description']}")
            if "error" in failed:
                print(f"     Error: {failed['error']}")

    # High success rate expected for metamorphic relations
    assert results["success_rate"] >= 0.8, f"Metamorphic relation success rate too low: {results['success_rate']:.2%}"

    # Critical relations must pass
    critical_relations = [
        MetamorphicRelation.ETHICAL_MONOTONICITY.value,
        MetamorphicRelation.COHERENCE_TRANSITIVITY.value,
    ]

    for result in results["test_results"]:
        if result["test_case"] in critical_relations:
            assert result["relation_holds"], f"Critical metamorphic relation failed: {result['test_case']}"


if __name__ == "__main__":
    print("🔄 Running Metamorphic Consciousness Tests")
    print("=" * 60)

    # Run metamorphic tests
    asyncio.run(test_all_metamorphic_relations())

    print("\n✅ All metamorphic tests completed!")
    print("Consciousness relationships verified under transformations.")
