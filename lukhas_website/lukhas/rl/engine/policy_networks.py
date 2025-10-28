"""
Consciousness Policy Networks for LUKHAS RL
==========================================

Neural network architectures specifically designed for consciousness-aware
policy learning. Includes attention mechanisms, reflection components, and
ethical constraint integration.

Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from __future__ import annotations

import logging

import torch
import torch.nn as nn
from observability.matriz_decorators import instrument
from torch.distributions import Categorical, Normal

logger = logging.getLogger(__name__)


class ConsciousnessAttention(nn.Module):
    """Multi-head attention mechanism for consciousness state integration"""

    def __init__(self, embed_dim: int, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads

        self.attention = nn.MultiheadAttention(
            embed_dim=embed_dim, num_heads=num_heads, dropout=dropout, batch_first=True
        )

        self.layer_norm = nn.LayerNorm(embed_dim)

    def forward(self, consciousness_features: torch.Tensor) -> torch.Tensor:
        """Apply attention to consciousness features"""

        # Add batch dimension if needed
        if consciousness_features.dim() == 1:
            consciousness_features = consciousness_features.unsqueeze(0)
        if consciousness_features.dim() == 2:
            consciousness_features = consciousness_features.unsqueeze(0)

        # Self-attention over consciousness features
        attended_features, attention_weights = self.attention(
            consciousness_features, consciousness_features, consciousness_features
        )

        # Residual connection and layer norm
        output = self.layer_norm(consciousness_features + attended_features)

        return output.squeeze(0) if output.shape[0] == 1 else output


class ReflectionModule(nn.Module):
    """Neural module for consciousness reflection and meta-cognition"""

    def __init__(self, input_dim: int, reflection_dim: int = 128):
        super().__init__()

        self.reflection_dim = reflection_dim

        # Reflection encoder
        self.reflection_encoder = nn.Sequential(
            nn.Linear(input_dim, reflection_dim),
            nn.ReLU(),
            nn.Linear(reflection_dim, reflection_dim),
            nn.LayerNorm(reflection_dim),
        )

        # Meta-cognitive processor
        self.meta_cognitive = nn.Sequential(
            nn.Linear(reflection_dim, reflection_dim // 2),
            nn.Tanh(),
            nn.Linear(reflection_dim // 2, reflection_dim),
        )

        # Self-awareness estimator
        self.self_awareness = nn.Sequential(nn.Linear(reflection_dim, 64), nn.ReLU(), nn.Linear(64, 1), nn.Sigmoid())

    def forward(self, consciousness_state: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Generate reflection features and self-awareness estimation"""

        # Encode consciousness state for reflection
        reflection_features = self.reflection_encoder(consciousness_state)

        # Meta-cognitive processing
        meta_features = self.meta_cognitive(reflection_features)

        # Combine reflection and meta-cognitive features
        combined_reflection = reflection_features + meta_features

        # Estimate self-awareness level
        self_awareness_score = self.self_awareness(combined_reflection)

        return combined_reflection, self_awareness_score


class EthicalConstraintModule(nn.Module):
    """Neural module for ethical constraint evaluation and enforcement"""

    def __init__(self, input_dim: int, constraint_dim: int = 64):
        super().__init__()

        self.constraint_dim = constraint_dim

        # Ethical evaluation network
        self.ethical_evaluator = nn.Sequential(
            nn.Linear(input_dim, constraint_dim),
            nn.ReLU(),
            nn.Linear(constraint_dim, constraint_dim),
            nn.ReLU(),
            nn.Linear(constraint_dim, 5),  # 5 ethical dimensions
        )

        # Constraint satisfaction predictor
        self.constraint_predictor = nn.Sequential(nn.Linear(5, 16), nn.ReLU(), nn.Linear(16, 1), nn.Sigmoid())

        # Ethical dimensions: safety, fairness, transparency, accountability, beneficence
        self.ethical_weights = nn.Parameter(torch.ones(5))

    def forward(self, consciousness_state: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Evaluate ethical constraints and compute constraint satisfaction"""

        # Evaluate ethical dimensions
        ethical_scores = torch.sigmoid(self.ethical_evaluator(consciousness_state))

        # Weighted ethical evaluation
        weighted_ethics = ethical_scores * self.ethical_weights

        # Predict overall constraint satisfaction
        constraint_satisfaction = self.constraint_predictor(weighted_ethics)

        return weighted_ethics, constraint_satisfaction


class ConsciousnessPolicy(nn.Module):
    """
    Neural network policy for consciousness decision-making.

    Features:
    - Attention-based consciousness state processing
    - Reflection and meta-cognition capabilities
    - Ethical constraint integration
    - Multi-modal action generation
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dim: int = 512,
        num_attention_heads: int = 8,
        reflection_dim: int = 128,
        ethical_constraint_dim: int = 64,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim

        # Input processing
        self.state_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim), nn.ReLU(), nn.LayerNorm(hidden_dim), nn.Dropout(dropout)
        )

        # Consciousness attention mechanism
        self.consciousness_attention = ConsciousnessAttention(
            embed_dim=hidden_dim, num_heads=num_attention_heads, dropout=dropout
        )

        # Reflection module for meta-cognition
        self.reflection_module = ReflectionModule(input_dim=hidden_dim, reflection_dim=reflection_dim)

        # Ethical constraint module
        self.ethical_module = EthicalConstraintModule(input_dim=hidden_dim, constraint_dim=ethical_constraint_dim)

        # Feature integration
        feature_integration_dim = hidden_dim + reflection_dim + ethical_constraint_dim
        self.feature_integrator = nn.Sequential(
            nn.Linear(feature_integration_dim, hidden_dim), nn.ReLU(), nn.LayerNorm(hidden_dim), nn.Dropout(dropout)
        )

        # Policy head for action probabilities
        self.policy_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
            nn.Softmax(dim=-1),
        )

        # Policy parameters for continuous actions (if needed)
        self.continuous_mean = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2), nn.ReLU(), nn.Linear(hidden_dim // 2, action_dim), nn.Tanh()
        )

        self.continuous_std = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2), nn.ReLU(), nn.Linear(hidden_dim // 2, action_dim), nn.Softplus()
        )

        # Consciousness confidence estimator
        self.confidence_estimator = nn.Sequential(nn.Linear(hidden_dim, 64), nn.ReLU(), nn.Linear(64, 1), nn.Sigmoid())

        logger.info(
            "🧠 ConsciousnessPolicy initialized: state_dim=%d, action_dim=%d, hidden_dim=%d",
            state_dim,
            action_dim,
            hidden_dim,
        )

    @instrument("DECISION", label="rl:policy_forward", capability="rl:policy")
    def forward(self, consciousness_state: torch.Tensor, action_type: str = "discrete") -> dict[str, torch.Tensor]:
        """
        Forward pass through consciousness policy network.

        Args:
            consciousness_state: Current consciousness state tensor
            action_type: "discrete" or "continuous" action output

        Returns:
            Dictionary containing policy outputs and consciousness metrics
        """

        # Encode consciousness state
        encoded_state = self.state_encoder(consciousness_state)

        # Apply consciousness attention
        attended_features = self.consciousness_attention(encoded_state)

        # Generate reflection features and self-awareness
        reflection_features, self_awareness = self.reflection_module(attended_features)

        # Evaluate ethical constraints
        ethical_features, constraint_satisfaction = self.ethical_module(attended_features)

        # Integrate all features
        integrated_features = torch.cat([attended_features, reflection_features, ethical_features], dim=-1)

        consciousness_representation = self.feature_integrator(integrated_features)

        # Generate policy outputs
        policy_outputs = {}

        if action_type == "discrete":
            # Discrete action probabilities
            action_probs = self.policy_head(consciousness_representation)
            policy_outputs["action_probs"] = action_probs
            policy_outputs["action_distribution"] = Categorical(action_probs)

        elif action_type == "continuous":
            # Continuous action parameters
            action_mean = self.continuous_mean(consciousness_representation)
            action_std = self.continuous_std(consciousness_representation) + 1e-6  # Numerical stability

            policy_outputs["action_mean"] = action_mean
            policy_outputs["action_std"] = action_std
            policy_outputs["action_distribution"] = Normal(action_mean, action_std)

        # Consciousness-specific outputs
        policy_outputs["consciousness_confidence"] = self.confidence_estimator(consciousness_representation)
        policy_outputs["self_awareness"] = self_awareness
        policy_outputs["ethical_constraint_satisfaction"] = constraint_satisfaction
        policy_outputs["consciousness_representation"] = consciousness_representation

        return policy_outputs

    def sample_action(
        self, consciousness_state: torch.Tensor, action_type: str = "discrete", exploration: bool = True
    ) -> tuple[torch.Tensor, torch.Tensor, dict[str, torch.Tensor]]:
        """
        Sample action from policy distribution.

        Args:
            consciousness_state: Current consciousness state
            action_type: "discrete" or "continuous"
            exploration: Whether to sample or use greedy action

        Returns:
            Tuple of (action, log_prob, policy_info)
        """

        policy_outputs = self.forward(consciousness_state, action_type)
        distribution = policy_outputs["action_distribution"]

        if exploration:
            action = distribution.sample()
        else:
            # Greedy action selection
            if action_type == "discrete":
                action = torch.argmax(policy_outputs["action_probs"], dim=-1)
            else:
                action = policy_outputs["action_mean"]

        log_prob = distribution.log_prob(action)

        # Additional policy info
        policy_info = {
            "consciousness_confidence": policy_outputs["consciousness_confidence"],
            "self_awareness": policy_outputs["self_awareness"],
            "ethical_satisfaction": policy_outputs["ethical_constraint_satisfaction"],
        }

        return action, log_prob, policy_info

    def evaluate_action(
        self, consciousness_state: torch.Tensor, action: torch.Tensor, action_type: str = "discrete"
    ) -> dict[str, torch.Tensor]:
        """
        Evaluate given action under current policy.

        Args:
            consciousness_state: Consciousness state tensor
            action: Action to evaluate
            action_type: "discrete" or "continuous"

        Returns:
            Dictionary with action evaluation results
        """

        policy_outputs = self.forward(consciousness_state, action_type)
        distribution = policy_outputs["action_distribution"]

        log_prob = distribution.log_prob(action)
        entropy = distribution.entropy()

        evaluation = {
            "log_prob": log_prob,
            "entropy": entropy,
            "consciousness_confidence": policy_outputs["consciousness_confidence"],
            "self_awareness": policy_outputs["self_awareness"],
            "ethical_satisfaction": policy_outputs["ethical_constraint_satisfaction"],
        }

        return evaluation


class ConsciousnessValueNetwork(nn.Module):
    """
    Value network for consciousness state evaluation.

    Estimates the long-term value of consciousness states considering:
    - Awareness and reflection potential
    - Ethical alignment quality
    - Temporal coherence stability
    - Growth and learning opportunities
    """

    def __init__(self, state_dim: int, hidden_dim: int = 512, num_attention_heads: int = 8, dropout: float = 0.1):
        super().__init__()

        self.state_dim = state_dim
        self.hidden_dim = hidden_dim

        # State encoding
        self.state_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim), nn.ReLU(), nn.LayerNorm(hidden_dim), nn.Dropout(dropout)
        )

        # Consciousness attention for state analysis
        self.consciousness_attention = ConsciousnessAttention(
            embed_dim=hidden_dim, num_heads=num_attention_heads, dropout=dropout
        )

        # Multi-objective value heads
        self.awareness_value = nn.Sequential(nn.Linear(hidden_dim, 128), nn.ReLU(), nn.Linear(128, 1))

        self.coherence_value = nn.Sequential(nn.Linear(hidden_dim, 128), nn.ReLU(), nn.Linear(128, 1))

        self.growth_value = nn.Sequential(nn.Linear(hidden_dim, 128), nn.ReLU(), nn.Linear(128, 1))

        self.ethical_value = nn.Sequential(nn.Linear(hidden_dim, 128), nn.ReLU(), nn.Linear(128, 1))

        # Integrated value head
        self.value_integrator = nn.Sequential(
            nn.Linear(4, 64),  # 4 value components
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

        # Value confidence estimator
        self.value_confidence = nn.Sequential(nn.Linear(hidden_dim, 64), nn.ReLU(), nn.Linear(64, 1), nn.Sigmoid())

        logger.info("🧠 ConsciousnessValueNetwork initialized: state_dim=%d, hidden_dim=%d", state_dim, hidden_dim)

    @instrument("AWARENESS", label="rl:value_estimation", capability="rl:value")
    def forward(self, consciousness_state: torch.Tensor) -> dict[str, torch.Tensor]:
        """
        Estimate value of consciousness state.

        Args:
            consciousness_state: Current consciousness state tensor

        Returns:
            Dictionary containing value estimates and components
        """

        # Encode consciousness state
        encoded_state = self.state_encoder(consciousness_state)

        # Apply consciousness attention for richer state representation
        attended_features = self.consciousness_attention(encoded_state)

        # Multi-objective value estimation
        awareness_val = self.awareness_value(attended_features)
        coherence_val = self.coherence_value(attended_features)
        growth_val = self.growth_value(attended_features)
        ethical_val = self.ethical_value(attended_features)

        # Integrate value components
        value_components = torch.cat([awareness_val, coherence_val, growth_val, ethical_val], dim=-1)
        integrated_value = self.value_integrator(value_components)

        # Value confidence
        confidence = self.value_confidence(attended_features)

        value_outputs = {
            "state_value": integrated_value,
            "awareness_value": awareness_val,
            "coherence_value": coherence_val,
            "growth_value": growth_val,
            "ethical_value": ethical_val,
            "value_confidence": confidence,
            "value_components": value_components,
        }

        return value_outputs

    def estimate_value(self, consciousness_state: torch.Tensor) -> torch.Tensor:
        """Simple interface for value estimation"""
        value_outputs = self.forward(consciousness_state)
        return value_outputs["state_value"]


class ConsciousnessActorCritic(nn.Module):
    """
    Combined Actor-Critic network for consciousness RL.

    Integrates policy and value networks with shared consciousness representation
    and coordinated learning objectives.
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dim: int = 512,
        num_attention_heads: int = 8,
        reflection_dim: int = 128,
        ethical_constraint_dim: int = 64,
        dropout: float = 0.1,
        shared_backbone: bool = True,
    ):
        super().__init__()

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.shared_backbone = shared_backbone

        if shared_backbone:
            # Shared consciousness representation
            self.shared_encoder = nn.Sequential(
                nn.Linear(state_dim, hidden_dim), nn.ReLU(), nn.LayerNorm(hidden_dim), nn.Dropout(dropout)
            )

            self.shared_attention = ConsciousnessAttention(
                embed_dim=hidden_dim, num_heads=num_attention_heads, dropout=dropout
            )

            # Actor and Critic heads
            self.actor = ConsciousnessPolicy(
                state_dim=hidden_dim,  # Using shared representation
                action_dim=action_dim,
                hidden_dim=hidden_dim // 2,
                num_attention_heads=num_attention_heads // 2,
                reflection_dim=reflection_dim,
                ethical_constraint_dim=ethical_constraint_dim,
                dropout=dropout,
            )

            self.critic = ConsciousnessValueNetwork(
                state_dim=hidden_dim,  # Using shared representation
                hidden_dim=hidden_dim // 2,
                num_attention_heads=num_attention_heads // 2,
                dropout=dropout,
            )
        else:
            # Independent actor and critic networks
            self.actor = ConsciousnessPolicy(
                state_dim=state_dim,
                action_dim=action_dim,
                hidden_dim=hidden_dim,
                num_attention_heads=num_attention_heads,
                reflection_dim=reflection_dim,
                ethical_constraint_dim=ethical_constraint_dim,
                dropout=dropout,
            )

            self.critic = ConsciousnessValueNetwork(
                state_dim=state_dim, hidden_dim=hidden_dim, num_attention_heads=num_attention_heads, dropout=dropout
            )

        logger.info("🧠 ConsciousnessActorCritic initialized: shared_backbone=%s", shared_backbone)

    def forward(
        self, consciousness_state: torch.Tensor, action: torch.Tensor | None = None, action_type: str = "discrete"
    ) -> dict[str, torch.Tensor]:
        """
        Forward pass through actor-critic network.

        Args:
            consciousness_state: Current consciousness state
            action: Action to evaluate (if None, samples new action)
            action_type: "discrete" or "continuous"

        Returns:
            Dictionary with actor-critic outputs
        """

        if self.shared_backbone:
            # Shared consciousness representation
            shared_features = self.shared_encoder(consciousness_state)
            shared_representation = self.shared_attention(shared_features)

            # Actor forward pass
            actor_outputs = self.actor(shared_representation, action_type)

            # Critic forward pass
            critic_outputs = self.critic(shared_representation)
        else:
            # Independent forward passes
            actor_outputs = self.actor(consciousness_state, action_type)
            critic_outputs = self.critic(consciousness_state)

        # Sample action if not provided
        if action is None:
            distribution = actor_outputs["action_distribution"]
            action = distribution.sample()
            log_prob = distribution.log_prob(action)
        else:
            log_prob = actor_outputs["action_distribution"].log_prob(action)

        # Combine outputs
        outputs = {
            **actor_outputs,
            **critic_outputs,
            "action": action,
            "log_prob": log_prob,
            "entropy": actor_outputs["action_distribution"].entropy(),
        }

        return outputs

    def get_action_and_value(
        self, consciousness_state: torch.Tensor, action_type: str = "discrete", exploration: bool = True
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, dict[str, torch.Tensor]]:
        """
        Get action and value estimate for consciousness state.

        Returns:
            Tuple of (action, value, log_prob, additional_info)
        """
        outputs = self.forward(consciousness_state, action_type=action_type)

        action = outputs["action"]
        value = outputs["state_value"]
        log_prob = outputs["log_prob"]

        additional_info = {
            "consciousness_confidence": outputs["consciousness_confidence"],
            "self_awareness": outputs["self_awareness"],
            "ethical_satisfaction": outputs["ethical_constraint_satisfaction"],
            "value_confidence": outputs["value_confidence"],
        }

        # Mark exploration as used (lint-only; preserves API)
        _ = exploration

        return action, value, log_prob, additional_info

    def evaluate_actions(
        self, consciousness_states: torch.Tensor, actions: torch.Tensor, action_type: str = "discrete"
    ) -> dict[str, torch.Tensor]:
        """
        Evaluate batch of actions for training.

        Args:
            consciousness_states: Batch of consciousness states
            actions: Batch of actions to evaluate
            action_type: "discrete" or "continuous"

        Returns:
            Dictionary with evaluation results
        """

        batch_size = consciousness_states.shape[0]

        # Handle batch processing
        all_outputs = []
        for i in range(batch_size):
            state = consciousness_states[i]
            action = actions[i]

            outputs = self.forward(state, action, action_type)
            all_outputs.append(outputs)

        # Aggregate batch results
        batch_results = {}
        for key in all_outputs[0]:
            if key in ["action_distribution"]:
                continue  # Skip distribution objects

            batch_results[key] = torch.stack([output[key] for output in all_outputs])

        # Calculate batch log probs and entropy
        log_probs = []
        entropies = []
        for i, output in enumerate(all_outputs):
            log_prob = output["action_distribution"].log_prob(actions[i])
            entropy = output["action_distribution"].entropy()
            log_probs.append(log_prob)
            entropies.append(entropy)

        batch_results["log_probs"] = torch.stack(log_probs)
        batch_results["entropy"] = torch.stack(entropies)

        return batch_results
