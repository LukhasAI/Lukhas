import asyncio
from typing import Any, Dict, List

import numpy as np
import torch
import torch.nn as nn
from learning.meta_adaptive import MetaLearner

from core.colonies.base_colony import BaseColony
from core.swarm import SwarmAgent


class LearningAgent(SwarmAgent):
    """Agent with local learning capabilities."""

    def __init__(self, agent_id: str, model_architecture: nn.Module):
        super().__init__(agent_id, None)
        self.local_model = model_architecture
        self.optimizer = torch.optim.Adam(self.local_model.parameters())
        self.local_data: List[Any] = []

    async def learn_local(self, data_batch: List[Any]) -> Dict[str, Any]:
        losses = []
        for data in data_batch:
            output = self.local_model(data["input"])
            loss = nn.functional.mse_loss(output, data["target"])
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            losses.append(loss.item())
        return {
            "agent_id": self.agent_id,
            "avg_loss": float(np.mean(losses)),
            "model_state": self.local_model.state_dict(),
        }


class FederatedLearningColony(BaseColony):
    """Colony for federated learning across agents."""

    def __init__(self, colony_id: str, model_architecture: nn.Module):
        super().__init__(colony_id, capabilities=["federated_learning"])
        self.global_model = model_architecture
        self.meta_learner = MetaLearner()
        self.learning_rounds = 0

    async def federated_learning_round(self, data_distribution: Dict[str, List]):
        learning_tasks = []
        for agent_id, agent in self.agents.items():
            if agent_id in data_distribution:
                task = agent.learn_local(data_distribution[agent_id])
                learning_tasks.append(task)
        local_results = await asyncio.gather(*learning_tasks)
        aggregated = self._federate_models(local_results)
        self.global_model.load_state_dict(aggregated)
        self.learning_rounds += 1
        return {
            "round": self.learning_rounds,
            "participants": len(local_results),
            "avg_loss": (
                float(np.mean([r["avg_loss"] for r in local_results]))
                if local_results
                else 0.0
            ),
            "model_version": self.learning_rounds,
        }

    def _federate_models(self, local_results: List[Dict]) -> Dict:
        aggregated_state = {}
        for key in self.global_model.state_dict().keys():
            param_sum = None
            for result in local_results:
                local_param = result["model_state"][key]
                param_sum = (
                    local_param.clone()
                    if param_sum is None
                    else param_sum + local_param
                )
            if param_sum is not None:
                aggregated_state[key] = param_sum / len(local_results)
        return aggregated_state
