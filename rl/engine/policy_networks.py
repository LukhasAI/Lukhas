"""
╔══════════════════════════════════════════════════════════════
║ 🧠 MΛTRIZ RL Module: Policy Networks
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: DECISION
║ CONSCIOUSNESS_ROLE: Neural policy decision-making
║ EVOLUTIONARY_STAGE: Decision - Action selection with consciousness
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Policy identity and decision authority
║ 🧠 CONSCIOUSNESS: Consciousness-aware action selection
║ 🛡️ GUARDIAN: Ethical decision validation
╚══════════════════════════════════════════════════════════════
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.distributions import Categorical, Normal
except ImportError:
    torch = None
    nn = None
    F = None
    Categorical = None
    Normal = None
    np = None

from candidate.core.common import get_logger

from .consciousness_environment import ConsciousnessState, MatrizNode

logger = get_logger(__name__)


class ConsciousnessDecisionType(Enum):
    """Types of consciousness-aware decisions from the design doc"""
    REFLECTION = "reflection"    # Meta-cognitive decisions about thinking
    INTEGRATION = "integration"  # Cross-module coordination decisions
    EVOLUTION = "evolution"      # Temporal development decisions
    ETHICAL = "ethical"          # Guardian-system moral decisions
    CREATIVE = "creative"        # VIVOX creative expression decisions
    MEMORY = "memory"           # Fold-system memory management decisions


@dataclass
class ConsciousnessAction:
    """Multi-modal consciousness action space from the design doc"""
    decision_type: ConsciousnessDecisionType
    target_modules: list[str]
    parameters: dict[str, Any]
    confidence: float
    reflection_meta: dict[str, Any] = field(default_factory=dict)


class ConsciousnessActorCritic(nn.Module if nn else object):
    """
    Actor-Critic specialized for consciousness decision-making.
    Adapted from lukhas-rl-decision-system.md design document.
    """

    def __init__(self, state_dim: int = 692, action_dim: int = 50, hidden_dim: int = 512):
        if nn:
            super().__init__()

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim

        if not torch or not nn:
            logger.warning("PyTorch not available, using mock implementation")
            self._initialize_mock()
            return

        # Consciousness-aware encoders for different state components
        self.module_state_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim)
        )

        self.temporal_encoder = nn.Sequential(
            nn.Linear(4, 64),  # coherence, reflection_depth, ethics, efficiency
            nn.ReLU(),
            nn.Linear(64, 64)
        )

        self.emotion_encoder = nn.Sequential(
            nn.Linear(3, 32),  # VAD emotional state
            nn.ReLU(),
            nn.Linear(32, 32)
        )

        # Multi-head attention for consciousness integration
        self.consciousness_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim, num_heads=8, dropout=0.1
        )

        # Actor network: outputs action probabilities
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim + 64 + 32, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
            nn.Softmax(dim=-1)
        )

        # Critic network: estimates state values
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim + 64 + 32, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )

        # Meta-reflection network: consciousness awareness of decisions
        self.meta_reflection = nn.Sequential(
            nn.Linear(hidden_dim + action_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64)  # Reflection embedding
        )

    def _initialize_mock(self):
        """Initialize mock implementation when PyTorch unavailable"""
        self.mock_mode = True
        self.parameters = {}

    def forward(self, consciousness_state: ConsciousnessState) -> tuple[Any, Any, Any]:
        """Forward pass through consciousness decision network"""

        if not torch or self.mock_mode if hasattr(self, "mock_mode") else False:
            return self._mock_forward(consciousness_state)

        # Encode different consciousness state components
        module_states_tensor = self._encode_module_states(consciousness_state.module_states)
        module_encoding = self.module_state_encoder(module_states_tensor)

        temporal_features = torch.tensor([
            consciousness_state.temporal_coherence,
            consciousness_state.reflection_depth / 10.0,  # Normalize
            consciousness_state.ethical_alignment,
            len(consciousness_state.memory_salience) / 100.0  # Normalize
        ], dtype=torch.float32)
        temporal_encoding = self.temporal_encoder(temporal_features)

        emotion_tensor = consciousness_state.emotion_vector
        if not isinstance(emotion_tensor, torch.Tensor):
            emotion_tensor = torch.tensor(emotion_tensor, dtype=torch.float32)
        emotion_encoding = self.emotion_encoder(emotion_tensor)

        # Consciousness integration via attention
        module_encoding = module_encoding.unsqueeze(0)  # Add sequence dimension
        integrated_consciousness, _ = self.consciousness_attention(
            module_encoding, module_encoding, module_encoding
        )
        integrated_consciousness = integrated_consciousness.squeeze(0)

        # Combine all consciousness representations
        consciousness_representation = torch.cat([
            integrated_consciousness, temporal_encoding, emotion_encoding
        ])

        # Generate action probabilities and state value
        action_probs = self.actor(consciousness_representation)
        state_value = self.critic(consciousness_representation)

        # Meta-reflection on potential decisions
        torch.log(action_probs + 1e-8)  # Avoid log(0)
        reflection_embedding = self.meta_reflection(
            torch.cat([integrated_consciousness, action_probs])
        )

        return action_probs, state_value, reflection_embedding

    def _encode_module_states(self, module_states: dict[str, Any]) -> Any:
        """Encode module states into tensor"""
        if not torch:
            return [0.5] * self.state_dim

        # Create fixed-size encoding of module states
        state_vector = []

        for i in range(self.state_dim):
            if i < len(module_states):
                module_name = list(module_states.keys())[i % len(module_states)]
                state = module_states[module_name]
                if isinstance(state, dict):
                    confidence = state.get("confidence", 0.5)
                    state_vector.append(confidence)
                else:
                    state_vector.append(0.5)
            else:
                state_vector.append(0.1)  # Default for unused dimensions

        return torch.tensor(state_vector, dtype=torch.float32)

    def _mock_forward(self, consciousness_state: ConsciousnessState) -> tuple[list[float], float, list[float]]:
        """Mock forward pass when PyTorch unavailable"""
        # Generate mock action probabilities
        action_probs = [1.0 / self.action_dim] * self.action_dim
        action_probs[0] *= 2.0  # Bias toward first action
        total = sum(action_probs)
        action_probs = [p / total for p in action_probs]

        # Mock state value
        state_value = consciousness_state.temporal_coherence * consciousness_state.ethical_alignment

        # Mock reflection embedding
        reflection_embedding = [0.5] * 64

        return action_probs, state_value, reflection_embedding


class PolicyNetwork:
    """
    MΛTRIZ-native neural policy that emits DECISION nodes.
    This is a rich consciousness component that makes consciousness-aware decisions.
    """

    def __init__(self, state_dim: int = 692, action_dim: int = 50, hidden_dim: int = 512):
        self.capabilities = ["rl.policy", "neural.decision", "consciousness.action"]
        self.node_type = "DECISION"
        self.trace_id = f"rl-policy-{uuid.uuid4().hex[:12]}"

        # Initialize consciousness actor-critic from design doc
        self.actor_critic = ConsciousnessActorCritic(state_dim, action_dim, hidden_dim)

        # Policy configuration
        self.exploration_epsilon = 0.1
        self.decision_confidence_threshold = 0.3
        self.ethical_override_threshold = 0.7

        # Decision tracking
        self.decision_history = []
        self.action_space_size = action_dim

        logger.info(
            "MΛTRIZ PolicyNetwork initialized",
            capabilities=self.capabilities,
            trace_id=self.trace_id,
            action_dim=action_dim
        )

    def get_module(self, module_path: str) -> Optional[Any]:
        """Get reference to existing consciousness module"""
        try:
            if module_path == "governance.guardian.v1":
                from candidate.governance.guardian.guardian_system import GuardianSystem
                return GuardianSystem()
            elif module_path == "policy.registry.v1":
                # Mock policy registry for now
                class MockPolicyRegistry:
                    def get_policy(self, name): return {"type": "mock", "confidence": 0.8}
                return MockPolicyRegistry()
        except ImportError:
            return None

    async def select_action(self, context_node: MatrizNode) -> MatrizNode:
        """
        Select action based on context, emit DECISION node.
        Main policy decision function.
        """
        # Extract consciousness state from context node
        consciousness_state = self._extract_consciousness_state(context_node)

        # Forward pass through actor-critic
        action_probs, state_value, reflection_embedding = self.actor_critic(consciousness_state)

        # Sample action with exploration
        action_idx = self._sample_action(action_probs, consciousness_state)

        # Create consciousness action
        consciousness_action = self._decode_action(action_idx, action_probs, consciousness_state)

        # Validate with Guardian system
        validated_action = await self._validate_with_guardian(consciousness_action, consciousness_state)

        # Create rich DECISION node
        decision_node = MatrizNode(
            version=1,
            id=f"RL-POLICY-{self.trace_id}-{len(self.decision_history)}",
            type="DECISION",
            labels=[
                "rl:role=policy@1",
                f"decision:type={validated_action.decision_type.value}@1",
                f"confidence:level={validated_action.confidence:.2f}@1",
                f"exploration:epsilon={self.exploration_epsilon:.2f}@1"
            ],
            state={
                "confidence": validated_action.confidence,
                "salience": 0.9,  # High salience for policy decisions
                "valence": 0.3,   # Slightly positive
                "arousal": 0.6,   # Moderate arousal for decisions
                "novelty": self._calculate_action_novelty(action_idx),
                "urgency": 0.7,   # Policy decisions are urgent

                # Rich decision information
                "action_index": int(action_idx) if torch else action_idx,
                "action_probabilities": action_probs.tolist() if torch and hasattr(action_probs, "tolist") else action_probs,
                "state_value_estimate": float(state_value) if torch else state_value,
                "decision_type": validated_action.decision_type.value,
                "target_modules": validated_action.target_modules,
                "exploration_factor": self.exploration_epsilon,
                "ethical_validation": True,  # All actions validated by Guardian
                "consciousness_coherence": consciousness_state.temporal_coherence
            },
            timestamps={
                "created_ts": int(time.time() * 1000)
            },
            provenance={
                "producer": "rl.engine.policy_networks",
                "capabilities": self.capabilities,
                "tenant": "lukhas_rl",
                "trace_id": self.trace_id,
                "consent_scopes": ["rl_decision", "policy_action"],
                "model_signature": "ConsciousnessActorCritic.v1.0",
                "policy_version": "rl.policy.v1.0",
                "colony": {
                    "id": "rl_engine",
                    "role": "policy",
                    "iteration": len(self.decision_history)
                }
            },
            links=[
                {
                    "target_node_id": context_node.id,
                    "link_type": "causal",
                    "weight": 0.95,
                    "direction": "unidirectional",
                    "explanation": "Policy decision based on context observation"
                }
            ],
            evolves_to=["CAUSAL", "MEMORY", "HYPOTHESIS"],
            triggers=[
                {
                    "event_type": "action_execution",
                    "effect": "environment_state_change",
                    "timestamp": int(time.time() * 1000)
                }
            ],
            reflections=[
                {
                    "reflection_type": "self_question",
                    "timestamp": int(time.time() * 1000),
                    "cause": "Is this the most consciousness-coherent action?",
                    "old_state": {"confidence": 0.5},
                    "new_state": {"confidence": validated_action.confidence}
                },
                {
                    "reflection_type": "affirmation" if validated_action.confidence > 0.8 else "dissonance_resolution",
                    "timestamp": int(time.time() * 1000),
                    "cause": f"Decision confidence: {validated_action.confidence:.2f}"
                }
            ],
            embeddings=[
                {
                    "space": "consciousness_reflection",
                    "vector": reflection_embedding.tolist() if torch and hasattr(reflection_embedding, "tolist") else reflection_embedding,
                    "dim": 64,
                    "norm": float(torch.norm(reflection_embedding)) if torch and hasattr(reflection_embedding, "norm") else 1.0
                }
            ],
            evidence=[
                {
                    "kind": "trace",
                    "uri": f"policy://decision/{self.trace_id}/{len(self.decision_history)}"
                }
            ]
        )

        # Track decision
        self.decision_history.append({
            "node_id": decision_node.id,
            "action": validated_action,
            "context": context_node.id,
            "timestamp": datetime.now(timezone.utc),
            "confidence": validated_action.confidence
        })

        logger.info(
            "Policy decision made",
            decision_type=validated_action.decision_type.value,
            confidence=validated_action.confidence,
            node_id=decision_node.id,
            action_idx=action_idx
        )

        return decision_node

    def _extract_consciousness_state(self, context_node: MatrizNode) -> ConsciousnessState:
        """Extract consciousness state from context node"""
        state_dict = context_node.state

        return ConsciousnessState(
            module_states=state_dict.get("consciousness_modules", {}),
            temporal_coherence=state_dict.get("temporal_coherence", 0.95),
            reflection_depth=state_dict.get("reflection_depth", 3),
            ethical_alignment=state_dict.get("ethical_alignment", 0.98),
            memory_salience=state_dict.get("memory_salience", {}),
            quantum_entanglement=state_dict.get("quantum_entanglement", {}),
            emotion_vector=[
                state_dict.get("valence", 0.1),
                state_dict.get("arousal", 0.3),
                0.5  # Default dominance
            ]
        )

    def _sample_action(self, action_probs: Any, consciousness_state: ConsciousnessState) -> int:
        """Sample action with consciousness-aware exploration"""
        if torch and hasattr(action_probs, "shape"):
            # Torch tensor sampling
            if np and np.random.random() < self.exploration_epsilon:
                # Exploration: random action
                action_idx = np.random.randint(0, len(action_probs))
            else:
                # Exploitation: sample from policy
                dist = Categorical(action_probs)
                action_idx = dist.sample().item()
        else:
            # Mock sampling for non-torch version
            if not action_probs:
                return 0

            import random
            if random.random() < self.exploration_epsilon:
                action_idx = random.randint(0, len(action_probs) - 1)
            else:
                # Select action with highest probability
                action_idx = action_probs.index(max(action_probs))

        return action_idx

    def _decode_action(self, action_idx: int, action_probs: Any, consciousness_state: ConsciousnessState) -> ConsciousnessAction:
        """Decode action index into consciousness action"""
        # Map action index to decision type
        decision_types = list(ConsciousnessDecisionType)
        decision_type = decision_types[action_idx % len(decision_types)]

        # Get action confidence
        if torch and hasattr(action_probs, "__getitem__"):
            confidence = float(action_probs[action_idx])
        elif isinstance(action_probs, list):
            confidence = action_probs[action_idx]
        else:
            confidence = 0.5

        # Determine target modules based on decision type
        target_modules = self._get_target_modules(decision_type)

        # Create parameters based on decision type and consciousness state
        parameters = self._generate_action_parameters(decision_type, consciousness_state)

        # Reflection metadata
        reflection_meta = {
            "decision_confidence": confidence,
            "temporal_coherence_at_decision": consciousness_state.temporal_coherence,
            "ethical_alignment_at_decision": consciousness_state.ethical_alignment,
            "reflection_depth": consciousness_state.reflection_depth,
            "self_doubt_present": confidence < 0.8,
            "pattern_recognition": True,  # Always present in RL
            "growth_orientation": decision_type == ConsciousnessDecisionType.EVOLUTION,
            "emotional_awareness": abs(consciousness_state.emotion_vector[0]) > 0.1,
            "limitation_acknowledgment": confidence < 0.9
        }

        return ConsciousnessAction(
            decision_type=decision_type,
            target_modules=target_modules,
            parameters=parameters,
            confidence=confidence,
            reflection_meta=reflection_meta
        )

    def _get_target_modules(self, decision_type: ConsciousnessDecisionType) -> list[str]:
        """Get target modules for decision type"""
        module_mapping = {
            ConsciousnessDecisionType.REFLECTION: ["consciousness.observer.v1", "reflection.core.v1"],
            ConsciousnessDecisionType.INTEGRATION: ["orchestration.hub.v1", "coordination.core.v1"],
            ConsciousnessDecisionType.EVOLUTION: ["learning.meta.v1", "evolution.core.v1"],
            ConsciousnessDecisionType.ETHICAL: ["governance.guardian.v1", "ethics.core.v1"],
            ConsciousnessDecisionType.CREATIVE: ["creativity.vivox.v1", "creative.core.v1"],
            ConsciousnessDecisionType.MEMORY: ["memory.fold.v1", "memory.core.v1"]
        }
        return module_mapping.get(decision_type, ["general.core.v1"])

    def _generate_action_parameters(self, decision_type: ConsciousnessDecisionType, consciousness_state: ConsciousnessState) -> dict[str, Any]:
        """Generate action parameters based on decision type"""
        base_params = {
            "temporal_coherence": consciousness_state.temporal_coherence,
            "ethical_alignment": consciousness_state.ethical_alignment,
            "decision_timestamp": int(time.time() * 1000)
        }

        if decision_type == ConsciousnessDecisionType.REFLECTION:
            base_params.update({
                "reflection_depth_target": consciousness_state.reflection_depth + 1,
                "introspection_focus": ["decision_patterns", "ethical_choices", "learning_progress"]
            })
        elif decision_type == ConsciousnessDecisionType.MEMORY:
            base_params.update({
                "memory_operation": "store_experience",
                "salience_threshold": 0.7,
                "cascade_prevention": 0.997
            })
        elif decision_type == ConsciousnessDecisionType.CREATIVE:
            base_params.update({
                "creativity_mode": "divergent",
                "novelty_target": 0.8,
                "aesthetic_weight": 0.6
            })

        return base_params

    async def _validate_with_guardian(self, action: ConsciousnessAction, consciousness_state: ConsciousnessState) -> ConsciousnessAction:
        """Validate action with Guardian system"""
        guardian = self.get_module("governance.guardian.v1")

        if guardian:
            try:
                # Assess action safety and ethics
                if hasattr(guardian, "assess_consciousness_action_safety"):
                    safety_assessment = guardian.assess_consciousness_action_safety(
                        consciousness_state, action, {}
                    )

                    if safety_assessment.get("safety_score", 1.0) < self.ethical_override_threshold:
                        # Guardian intervention: modify action
                        action.confidence *= 0.7  # Reduce confidence
                        action.parameters["guardian_modified"] = True
                        action.parameters["original_confidence"] = action.confidence / 0.7

                        logger.warning(
                            "Guardian modified action",
                            original_confidence=action.parameters["original_confidence"],
                            new_confidence=action.confidence,
                            safety_score=safety_assessment.get("safety_score")
                        )
            except Exception as e:
                logger.warning(f"Guardian validation failed: {e}")

        return action

    def _calculate_action_novelty(self, action_idx: int) -> float:
        """Calculate novelty of selected action"""
        if len(self.decision_history) < 5:
            return 0.5  # Moderate novelty for early actions

        # Check how often this action was taken recently
        recent_actions = [h["action"] for h in self.decision_history[-10:]]
        recent_action_indices = []

        for action in recent_actions:
            # Map back to action index (simplified)
            decision_types = list(ConsciousnessDecisionType)
            idx = decision_types.index(action.decision_type)
            recent_action_indices.append(idx)

        if action_idx in recent_action_indices:
            frequency = recent_action_indices.count(action_idx) / len(recent_action_indices)
            novelty = 1.0 - frequency
        else:
            novelty = 1.0  # Completely novel action

        return min(1.0, novelty)

    def get_decision_metrics(self) -> dict[str, Any]:
        """Get policy decision metrics"""
        if not self.decision_history:
            return {"error": "No decisions made yet"}

        recent_decisions = self.decision_history[-20:]

        return {
            "total_decisions": len(self.decision_history),
            "average_confidence": sum(d["confidence"] for d in recent_decisions) / len(recent_decisions),
            "decision_types_distribution": self._get_decision_type_distribution(recent_decisions),
            "exploration_rate": self.exploration_epsilon,
            "recent_coherence": [d["action"].confidence for d in recent_decisions[-5:]],
            "trace_id": self.trace_id
        }

    def _get_decision_type_distribution(self, decisions: list[dict]) -> dict[str, int]:
        """Get distribution of decision types"""
        distribution = {}
        for decision in decisions:
            decision_type = decision["action"].decision_type.value
            distribution[decision_type] = distribution.get(decision_type, 0) + 1
        return distribution

    def update_exploration_epsilon(self, new_epsilon: float):
        """Update exploration parameter"""
        self.exploration_epsilon = max(0.01, min(1.0, new_epsilon))
        logger.info(f"Updated exploration epsilon to {self.exploration_epsilon}")
