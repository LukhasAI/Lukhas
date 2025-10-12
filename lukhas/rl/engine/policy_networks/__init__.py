"""Lightweight policy networks used by consciousness RL tests."""

from __future__ import annotations

import math
from importlib import import_module
from typing import Iterable, List, Sequence

__all__ = [
    "ConsciousnessPolicy",
    "ConsciousnessValueNetwork",
    "ConsciousnessActorCritic",
    "TrainingConfiguration",
    "MultiAgentConsciousnessTrainer",
]


def _try(name: str):
    try:
        module = import_module(name)
    except Exception:
        return None
    if module.__name__ == __name__:
        return None
    return module


_CANDIDATES = (
    "lukhas_website.lukhas.rl.engine.policy_networks",
    "labs.rl.engine.policy_networks",
    "rl.engine.policy_networks",
)

_BACKEND = None
for _candidate in _CANDIDATES:
    _module = _try(_candidate)
    if not _module:
        continue
    _BACKEND = _module
    globals().update({attr: getattr(_module, attr) for attr in dir(_module) if not attr.startswith("_")})
    break

try:  # pragma: no cover - optional dependency
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except Exception:  # pragma: no cover - fallback
    torch = None
    nn = None
    F = None


class _ModuleBase(nn.Module if nn else object):
    def __init__(self) -> None:
        if nn:
            super().__init__()


if "ConsciousnessPolicy" not in globals():

    class ConsciousnessPolicy(_ModuleBase):  # type: ignore[misc]
        def __init__(self, input_dim: int = 16, hidden_dim: int = 32, action_dim: int = 8):
            super().__init__()
            self.action_dim = action_dim
            if nn:
                self.net = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, action_dim),
                )

        def forward(self, state):  # type: ignore[override]
            if torch is not None and nn is not None:
                logits = self.net(state)
                return F.softmax(logits, dim=-1)
            return [1.0 / self.action_dim] * self.action_dim

        def sample_action(self, state) -> int:
            probs = self.forward(state)
            if torch is not None and isinstance(probs, torch.Tensor):
                return torch.argmax(probs).item()
            return max(range(len(probs)), key=probs.__getitem__)


if "ConsciousnessValueNetwork" not in globals():

    class ConsciousnessValueNetwork(_ModuleBase):  # type: ignore[misc]
        def __init__(self, input_dim: int = 16, hidden_dim: int = 32):
            super().__init__()
            if nn:
                self.net = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, 1),
                )

        def forward(self, state):  # type: ignore[override]
            if torch is not None and nn is not None:
                return self.net(state)
            return 0.0


if "ConsciousnessActorCritic" not in globals():

    class ConsciousnessActorCritic(_ModuleBase):  # type: ignore[misc]
        def __init__(self, policy: ConsciousnessPolicy | None = None, value: ConsciousnessValueNetwork | None = None):
            super().__init__()
            self.policy = policy or ConsciousnessPolicy()
            self.value = value or ConsciousnessValueNetwork()

        def act(self, state):
            action = self.policy.sample_action(state)
            value = self.value.forward(state)
            return action, value


if "TrainingConfiguration" not in globals():

    class TrainingConfiguration:  # type: ignore[misc]
        def __init__(self, episodes: int = 10, learning_rate: float = 1e-3):
            self.episodes = episodes
            self.learning_rate = learning_rate


if "MultiAgentConsciousnessTrainer" not in globals():

    class MultiAgentConsciousnessTrainer:  # type: ignore[misc]
        def __init__(self, agents: Sequence[ConsciousnessActorCritic], config: TrainingConfiguration):
            self.agents = list(agents)
            self.config = config

        async def train(self, environment) -> dict[str, int]:
            for episode in range(self.config.episodes):
                state = environment.reset() if hasattr(environment, "reset") else None
                for agent in self.agents:
                    action, _ = agent.act(state)
                    if hasattr(environment, "step"):
                        environment.step(action)
            return {"episodes": self.config.episodes}
