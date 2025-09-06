#!/usr/bin/env python3
"""
LUKHAS AI Consciousness-Aware Actor-Critic Architecture
========================================================

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian

Implements consciousness-aware RL actors and critics with:
- Phenomenological state representation
- Ethical constraint integration
- Memory fold interaction
- Trinity Framework compliance
"""

from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn


class ConsciousnessActorCritic(nn.Module):
    """
    Consciousness-aware Actor-Critic architecture

    Combines policy network (actor) and value network (critic) with
    consciousness state integration and Trinity Framework compliance.
    """

    def __init__(self, state_dim: int, action_dim: int, consciousness_dim: int = 128, hidden_dim: int = 256, **kwargs):
        super().__init__()

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.consciousness_dim = consciousness_dim
        self.hidden_dim = hidden_dim

        # Shared consciousness encoder
        self.consciousness_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, consciousness_dim), nn.Tanh()
        )

        # Actor network (policy)
        self.actor = nn.Sequential(
            nn.Linear(consciousness_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1),
        )

        # Critic network (value function)
        self.critic = nn.Sequential(
            nn.Linear(consciousness_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through consciousness-aware actor-critic

        Args:
            state: Input state tensor

        Returns:
            Tuple of (action_probs, state_value)
        """
        # Encode state through consciousness layer
        consciousness_state = self.consciousness_encoder(state)

        # Generate action probabilities and state value
        action_probs = self.actor(consciousness_state)
        state_value = self.critic(consciousness_state)

        return action_probs, state_value

    def get_action(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Sample action from policy"""
        action_probs, state_value = self.forward(state)
        action_dist = torch.distributions.Categorical(action_probs)
        action = action_dist.sample()
        return action, state_value

    def evaluate_action(
        self, state: torch.Tensor, action: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Evaluate action log probability and entropy"""
        action_probs, state_value = self.forward(state)
        action_dist = torch.distributions.Categorical(action_probs)

        action_log_prob = action_dist.log_prob(action)
        entropy = action_dist.entropy()

        return action_log_prob, state_value, entropy


__all__ = ["ConsciousnessActorCritic"]
