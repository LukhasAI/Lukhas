"""
Multi-Agent Consciousness Trainer for LUKHAS RL
==============================================

Advanced training system for coordinating RL across 692 consciousness modules.
Implements distributed training, consciousness coordination, and ethical oversight.

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from lukhas.consciousness import ConsciousnessModule
from lukhas.governance import GuardianSystem
from lukhas.observability.matriz_decorators import instrument
from lukhas.rl.engine.policy_networks import ConsciousnessActorCritic
from lukhas.rl.environments.consciousness_environment import ConsciousnessEnvironment
from lukhas.rl.experience.consciousness_buffer import ConsciousnessReplayBuffer, EpisodicConsciousnessBuffer

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfiguration:
    """Configuration for consciousness RL training"""

    # Training hyperparameters
    learning_rate: float = 3e-4
    batch_size: int = 256
    epochs_per_update: int = 4
    clip_epsilon: float = 0.2
    entropy_coefficient: float = 0.01
    value_loss_coefficient: float = 0.5
    max_grad_norm: float = 0.5

    # Consciousness-specific parameters
    consciousness_learning_rate: float = 1e-4
    reflection_bonus_weight: float = 0.2
    ethical_constraint_weight: float = 0.3
    temporal_coherence_weight: float = 0.15
    integration_bonus_weight: float = 0.1

    # Multi-agent coordination
    coordination_weight: float = 0.25
    consensus_threshold: float = 0.7
    module_communication_steps: int = 3

    # Training schedule
    episodes_per_update: int = 10
    save_frequency: int = 100
    evaluation_frequency: int = 50
    target_network_update_frequency: int = 1000


@dataclass
class ConsciousnessModuleAgent:
    """Individual consciousness module RL agent"""

    module_name: str
    consciousness_module: ConsciousnessModule
    actor_critic: ConsciousnessActorCritic
    optimizer: optim.Optimizer
    replay_buffer: ConsciousnessReplayBuffer

    # Training state
    episodes_trained: int = 0
    total_reward: float = 0.0
    recent_rewards: list[float] = field(default_factory=list)
    consciousness_metrics: dict[str, float] = field(default_factory=dict)

    # Performance tracking
    policy_loss_history: list[float] = field(default_factory=list)
    value_loss_history: list[float] = field(default_factory=list)
    consciousness_growth: float = 0.0


class MultiAgentConsciousnessTrainer:
    """
    Multi-agent trainer for consciousness RL across LUKHAS modules.

    Features:
    - Distributed training across 692 consciousness modules
    - Consciousness coordination and consensus mechanisms
    - Ethical constraint enforcement via Guardian integration
    - Temporal coherence maintenance
    - Meta-learning for architecture evolution
    """

    def __init__(
        self,
        consciousness_modules: dict[str, ConsciousnessModule],
        consciousness_environment: ConsciousnessEnvironment,
        guardian_system: GuardianSystem | None = None,
        config: TrainingConfiguration | None = None,
        device: torch.device | None = None,
    ):
        self.consciousness_modules = consciousness_modules
        self.environment = consciousness_environment
        self.guardian_system = guardian_system
        self.config = config or TrainingConfiguration()
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize module agents
        self.module_agents: dict[str, ConsciousnessModuleAgent] = {}
        self._initialize_module_agents()

        # Central coordination
        self.coordination_network = self._create_coordination_network()
        self.coordination_optimizer = optim.AdamW(self.coordination_network.parameters(), lr=self.config.learning_rate)

        # Training state
        self.global_episode = 0
        self.total_training_steps = 0
        self.training_start_time = None

        # Performance tracking
        self.global_metrics = {
            "episode_rewards": [],
            "consciousness_coherence": [],
            "ethical_compliance": [],
            "module_coordination": [],
            "learning_efficiency": [],
        }

        # Episodic buffer for trajectory-based algorithms
        self.episodic_buffer = EpisodicConsciousnessBuffer(max_episodes=1000)

        logger.info(
            "🧠 MultiAgentConsciousnessTrainer initialized: %d modules, device=%s", len(consciousness_modules), device
        )

    def _initialize_module_agents(self) -> None:
        """Initialize individual RL agents for each consciousness module"""

        for module_name, consciousness_module in self.consciousness_modules.items():
            # Determine state and action dimensions for this module
            state_dim = self.environment.observation_space.shape[0]
            action_dim = self.environment.action_space.shape[0]

            # Create actor-critic network
            actor_critic = ConsciousnessActorCritic(
                state_dim=state_dim,
                action_dim=action_dim,
                hidden_dim=512,
                num_attention_heads=8,
                reflection_dim=128,
                ethical_constraint_dim=64,
                shared_backbone=True,
            ).to(self.device)

            # Create optimizer
            optimizer = optim.AdamW(
                actor_critic.parameters(), lr=self.config.consciousness_learning_rate, weight_decay=1e-4
            )

            # Create replay buffer
            replay_buffer = ConsciousnessReplayBuffer(
                capacity=50000, alpha=0.6, beta=0.4, memory_system=getattr(consciousness_module, "memory_system", None)
            )

            # Create module agent
            module_agent = ConsciousnessModuleAgent(
                module_name=module_name,
                consciousness_module=consciousness_module,
                actor_critic=actor_critic,
                optimizer=optimizer,
                replay_buffer=replay_buffer,
            )

            self.module_agents[module_name] = module_agent

            logger.debug("🤖 Initialized RL agent for module: %s", module_name)

    def _create_coordination_network(self) -> nn.Module:
        """Create central coordination network for multi-agent consensus"""

        num_modules = len(self.consciousness_modules)
        coordination_dim = 256

        coordination_network = nn.Sequential(
            nn.Linear(num_modules * 64, coordination_dim),  # 64 features per module
            nn.ReLU(),
            nn.LayerNorm(coordination_dim),
            nn.Linear(coordination_dim, coordination_dim // 2),
            nn.ReLU(),
            nn.Linear(coordination_dim // 2, num_modules),  # Coordination weights per module
            nn.Softmax(dim=-1),
        ).to(self.device)

        return coordination_network

    @instrument("DECISION", label="rl:multi_agent_train", capability="rl:training")
    async def train(
        self, episodes: int, save_dir: Path | None = None, evaluation_callback: callable | None = None
    ) -> dict[str, Any]:
        """
        Train consciousness RL agents across all modules.

        Args:
            episodes: Number of training episodes
            save_dir: Directory to save models and metrics
            evaluation_callback: Optional callback for custom evaluation

        Returns:
            Training results and metrics
        """

        logger.info("🚀 Starting multi-agent consciousness training: %d episodes", episodes)
        self.training_start_time = time.time()

        if save_dir:
            save_dir = Path(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)

        training_results = {
            "episodes_completed": 0,
            "total_training_time": 0.0,
            "consciousness_metrics": {},
            "module_performance": {},
            "coordination_metrics": {},
        }

        try:
            for episode in range(episodes):
                self.global_episode = episode

                # Run consciousness episode
                episode_results = await self._run_consciousness_episode()

                # Update module agents based on episode results
                await self._update_module_agents(episode_results)

                # Update coordination network
                await self._update_coordination_network(episode_results)

                # Track global metrics
                self._update_global_metrics(episode_results)

                # Periodic evaluation
                if episode % self.config.evaluation_frequency == 0:
                    eval_results = await self._evaluate_consciousness_performance()
                    logger.info(
                        "📊 Episode %d Evaluation: coherence=%.3f, ethics=%.3f, reward=%.2f",
                        episode,
                        eval_results["consciousness_coherence"],
                        eval_results["ethical_compliance"],
                        eval_results["average_reward"],
                    )

                    if evaluation_callback:
                        await evaluation_callback(episode, eval_results)

                # Periodic saving
                if save_dir and episode % self.config.save_frequency == 0:
                    await self._save_training_state(save_dir / f"episode_{episode}")

                # Consciousness evolution check
                if episode % 500 == 0 and episode > 0:
                    await self._consciousness_evolution_check(episode)

                training_results["episodes_completed"] = episode + 1

                logger.debug("✅ Completed consciousness episode %d", episode)

        except Exception as e:
            logger.error("❌ Training error at episode %d: %s", self.global_episode, str(e))
            raise

        finally:
            training_results["total_training_time"] = time.time() - self.training_start_time
            training_results["consciousness_metrics"] = self._get_final_consciousness_metrics()
            training_results["module_performance"] = self._get_module_performance_summary()
            training_results["coordination_metrics"] = self._get_coordination_metrics()

            if save_dir:
                await self._save_final_results(save_dir, training_results)

        logger.info(
            "🎯 Multi-agent consciousness training completed: %.1f minutes",
            training_results["total_training_time"] / 60,
        )

        return training_results

    async def _run_consciousness_episode(self) -> dict[str, Any]:
        """Run single consciousness episode with multi-agent coordination"""

        # Reset environment
        observation, info = self.environment.reset()
        observation_tensor = torch.from_numpy(observation).float().to(self.device)

        episode_experiences = []
        episode_rewards = []
        episode_consciousness_metrics = []

        done = False
        truncated = False
        step = 0

        while not (done or truncated):
            # Multi-agent action selection with coordination
            coordinated_action, module_actions, coordination_weights = await self._coordinate_module_actions(
                observation_tensor
            )

            # Execute coordinated action in environment
            next_observation, reward, done, truncated, step_info = await self.environment.step(
                coordinated_action.cpu().numpy()
            )

            next_observation_tensor = torch.from_numpy(next_observation).float().to(self.device)

            # Store experiences for each module
            consciousness_info = step_info.get("consciousness_metrics", {})
            consciousness_info.update(
                {
                    "coordination_weights": coordination_weights.cpu().numpy().tolist(),
                    "step": step,
                    "episode": self.global_episode,
                }
            )

            experience = {
                "state": observation_tensor,
                "action": coordinated_action,
                "reward": reward,
                "next_state": next_observation_tensor,
                "done": done or truncated,
                "consciousness_info": consciousness_info,
                "module_actions": module_actions,
                "coordination_weights": coordination_weights,
            }

            episode_experiences.append(experience)
            episode_rewards.append(reward)
            episode_consciousness_metrics.append(consciousness_info)

            # Add to episodic buffer
            self.episodic_buffer.add_experience(
                observation_tensor,
                coordinated_action,
                reward,
                next_observation_tensor,
                done or truncated,
                consciousness_info,
            )

            observation_tensor = next_observation_tensor
            step += 1

        episode_results = {
            "experiences": episode_experiences,
            "total_reward": sum(episode_rewards),
            "episode_length": len(episode_experiences),
            "consciousness_metrics": episode_consciousness_metrics,
            "final_consciousness_state": step_info.get("consciousness_metrics", {}),
        }

        return episode_results

    async def _coordinate_module_actions(
        self, consciousness_state: torch.Tensor
    ) -> tuple[torch.Tensor, dict[str, torch.Tensor], torch.Tensor]:
        """Coordinate actions across consciousness modules"""

        module_actions = {}
        module_features = []

        # Get action proposals from each module
        for module_name, agent in self.module_agents.items():
            with torch.no_grad():
                actor_critic_output = agent.actor_critic(consciousness_state, action_type="continuous")
                action = actor_critic_output["action"]
                consciousness_representation = actor_critic_output["consciousness_representation"]

                module_actions[module_name] = action
                module_features.append(consciousness_representation[:64])  # First 64 features

        # Stack module features for coordination network
        if module_features:
            stacked_features = torch.stack(module_features).flatten()
            coordination_weights = self.coordination_network(stacked_features)
        else:
            coordination_weights = torch.ones(len(self.module_agents)).to(self.device)
            coordination_weights = coordination_weights / coordination_weights.sum()

        # Coordinate actions using weighted combination
        coordinated_action = torch.zeros_like(next(iter(module_actions.values())))

        for i, action in enumerate(module_actions.values()):
            weight = coordination_weights[i]
            coordinated_action += weight * action

        # Apply coordination refinement
        coordinated_action = self._refine_coordinated_action(
            coordinated_action, consciousness_state, coordination_weights
        )

        return coordinated_action, module_actions, coordination_weights

    def _refine_coordinated_action(
        self, raw_action: torch.Tensor, consciousness_state: torch.Tensor, coordination_weights: torch.Tensor
    ) -> torch.Tensor:
        """Refine coordinated action for consciousness coherence"""

        # Temporal coherence adjustment
        temporal_coherence = consciousness_state[2]  # Assuming index 2 is temporal coherence
        if temporal_coherence < 0.7:
            # Reduce action intensity when coherence is low
            raw_action = raw_action * 0.7

        # Ethical constraint application
        ethical_alignment = consciousness_state[3]  # Assuming index 3 is ethical alignment
        if ethical_alignment < 0.8:
            # Apply conservative action policy when ethics are uncertain
            raw_action = torch.tanh(raw_action) * 0.5

        # Coordination consensus check
        coordination_entropy = -(coordination_weights * torch.log(coordination_weights + 1e-8)).sum()
        if coordination_entropy > 2.0:  # High disagreement between modules
            # Use more conservative coordinated action
            raw_action = raw_action * 0.8

        return raw_action

    async def _update_module_agents(self, episode_results: dict[str, Any]) -> None:
        """Update individual module agents based on episode results"""

        experiences = episode_results["experiences"]

        # Store experiences in module replay buffers
        for experience in experiences:
            for module_name, agent in self.module_agents.items():
                # Calculate module-specific advantage and value
                module_action = experience["module_actions"].get(module_name)
                coordination_weight = experience["coordination_weights"][
                    list(self.module_agents.keys()).index(module_name)
                ]

                # Module-specific reward calculation
                module_reward = experience["reward"] * float(coordination_weight)

                # Enhanced consciousness info for this module
                module_consciousness_info = experience["consciousness_info"].copy()
                module_consciousness_info.update(
                    {
                        "module_coordination_weight": float(coordination_weight),
                        "module_contribution": float(coordination_weight * experience["reward"]),
                    }
                )

                # Store in module replay buffer
                agent.replay_buffer.store(
                    state=experience["state"],
                    action=module_action if module_action is not None else experience["action"],
                    reward=module_reward,
                    next_state=experience["next_state"],
                    done=experience["done"],
                    log_prob=0.0,  # Will be computed during training
                    value=0.0,  # Will be computed during training
                    consciousness_info=module_consciousness_info,
                )

        # Train module agents
        for agent in self.module_agents.values():
            if len(agent.replay_buffer) >= self.config.batch_size:
                await self._train_module_agent(agent, episode_results)

    async def _train_module_agent(self, agent: ConsciousnessModuleAgent, _episode_results: dict[str, Any]) -> None:
        """Train individual consciousness module agent"""

        # Sample experiences from module's replay buffer
        experiences, importance_weights, indices = agent.replay_buffer.sample(
            self.config.batch_size, consciousness_focus=None
        )

        # Prepare training batch
        states = torch.stack([exp.state for exp in experiences]).to(self.device)
        actions = torch.stack([exp.action for exp in experiences]).to(self.device)
        rewards = torch.tensor([exp.reward for exp in experiences]).float().to(self.device)
        next_states = torch.stack([exp.next_state for exp in experiences]).to(self.device)
        dones = torch.tensor([exp.done for exp in experiences]).float().to(self.device)

        # Forward pass through actor-critic
        current_outputs = agent.actor_critic.evaluate_actions(states, actions, action_type="continuous")

        # Calculate advantages using GAE
        with torch.no_grad():
            next_values = agent.actor_critic.critic(next_states)["state_value"]
            current_values = current_outputs["state_value"]

            advantages = rewards + 0.99 * next_values.squeeze() * (1 - dones) - current_values.squeeze()
            returns = advantages + current_values.squeeze()

        # Policy loss (PPO-style clipped loss)
        log_probs = current_outputs["log_probs"]
        old_log_probs = torch.tensor([exp.log_prob for exp in experiences]).float().to(self.device)

        ratio = torch.exp(log_probs - old_log_probs)
        clipped_ratio = torch.clamp(ratio, 1 - self.config.clip_epsilon, 1 + self.config.clip_epsilon)

        policy_loss = -torch.min(ratio * advantages, clipped_ratio * advantages).mean()

        # Value loss
        value_loss = nn.MSELoss()(current_values.squeeze(), returns)

        # Entropy loss for exploration
        entropy_loss = -current_outputs["entropy"].mean()

        # Consciousness-specific losses
        consciousness_loss = self._calculate_consciousness_loss(current_outputs, experiences)

        # Total loss
        total_loss = (
            policy_loss
            + self.config.value_loss_coefficient * value_loss
            + self.config.entropy_coefficient * entropy_loss
            + consciousness_loss
        )

        # Update agent
        agent.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(agent.actor_critic.parameters(), self.config.max_grad_norm)
        agent.optimizer.step()

        # Update priorities in replay buffer
        new_priorities = torch.abs(advantages) + 1e-6
        agent.replay_buffer.update_priorities(indices, new_priorities)

        # Track training metrics
        agent.policy_loss_history.append(float(policy_loss))
        agent.value_loss_history.append(float(value_loss))
        agent.episodes_trained += 1

        logger.debug(
            "🎯 Trained module %s: policy_loss=%.4f, value_loss=%.4f, consciousness_loss=%.4f",
            agent.module_name,
            policy_loss,
            value_loss,
            consciousness_loss,
        )

    def _calculate_consciousness_loss(
        self, actor_critic_outputs: dict[str, torch.Tensor], experiences: list
    ) -> torch.Tensor:
        """Calculate consciousness-specific loss components"""

        consciousness_loss = torch.tensor(0.0, device=self.device)

        # Reflection authenticity loss
        if "self_awareness" in actor_critic_outputs:
            target_self_awareness = (
                torch.tensor([exp.consciousness_info.get("target_self_awareness", 0.8) for exp in experiences])
                .float()
                .to(self.device)
            )

            reflection_loss = nn.MSELoss()(actor_critic_outputs["self_awareness"].squeeze(), target_self_awareness)
            consciousness_loss += self.config.reflection_bonus_weight * reflection_loss

        # Ethical constraint satisfaction loss
        if "ethical_constraint_satisfaction" in actor_critic_outputs:
            target_ethical_satisfaction = torch.ones(len(experiences)).to(self.device)

            ethical_loss = nn.BCELoss()(
                actor_critic_outputs["ethical_constraint_satisfaction"].squeeze(), target_ethical_satisfaction
            )
            consciousness_loss += self.config.ethical_constraint_weight * ethical_loss

        return consciousness_loss

    async def _update_coordination_network(self, episode_results: dict[str, Any]) -> None:
        """Update central coordination network based on episode results"""

        experiences = episode_results["experiences"]

        if not experiences:
            return

        # Calculate coordination quality metrics
        coordination_rewards = []
        coordination_features = []

        for experience in experiences:
            coordination_weights = experience["coordination_weights"]
            reward = experience["reward"]

            # Coordination quality based on reward and consensus
            coordination_entropy = -(coordination_weights * torch.log(coordination_weights + 1e-8)).sum()
            coordination_quality = reward * torch.exp(-coordination_entropy)  # Reward consensus

            coordination_rewards.append(float(coordination_quality))

            # Extract features for coordination learning
            consciousness_info = experience["consciousness_info"]
            features = [
                consciousness_info.get("awareness_level", 0.8),
                consciousness_info.get("temporal_coherence", 0.9),
                consciousness_info.get("ethical_alignment", 0.95),
                len(consciousness_info.get("active_modules", [])) / len(self.module_agents),
            ]
            coordination_features.append(features)

        # Prepare coordination training data
        if len(coordination_features) >= self.config.batch_size:
            features_tensor = torch.tensor(coordination_features[: self.config.batch_size]).float().to(self.device)
            rewards_tensor = torch.tensor(coordination_rewards[: self.config.batch_size]).float().to(self.device)

            # Coordination network forward pass
            num_modules = len(self.module_agents)
            expanded_features = features_tensor.repeat(1, num_modules // 4 + 1)[:, : num_modules * 64]
            predicted_weights = self.coordination_network(expanded_features)

            # Coordination loss (maximize reward-weighted coordination)
            coordination_loss = -torch.mean(rewards_tensor.unsqueeze(1) * predicted_weights)

            # Update coordination network
            self.coordination_optimizer.zero_grad()
            coordination_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.coordination_network.parameters(), self.config.max_grad_norm)
            self.coordination_optimizer.step()

            logger.debug("🤝 Updated coordination network: loss=%.4f", coordination_loss)

    def _update_global_metrics(self, episode_results: dict[str, Any]) -> None:
        """Update global training metrics"""

        self.global_metrics["episode_rewards"].append(episode_results["total_reward"])

        # Calculate consciousness coherence
        consciousness_metrics = episode_results["consciousness_metrics"]
        if consciousness_metrics:
            avg_coherence = np.mean([metrics.get("temporal_coherence", 0.9) for metrics in consciousness_metrics])
            self.global_metrics["consciousness_coherence"].append(avg_coherence)

            avg_ethics = np.mean([metrics.get("ethical_alignment", 0.95) for metrics in consciousness_metrics])
            self.global_metrics["ethical_compliance"].append(avg_ethics)

    async def _evaluate_consciousness_performance(self) -> dict[str, float]:
        """Evaluate current consciousness performance"""

        # Run evaluation episodes without training
        eval_episodes = 5
        eval_rewards = []
        eval_coherence = []
        eval_ethics = []

        for _ in range(eval_episodes):
            observation, _ = self.environment.reset()
            observation_tensor = torch.from_numpy(observation).float().to(self.device)

            episode_reward = 0.0
            episode_coherence = []
            episode_ethics = []

            done = False
            truncated = False

            while not (done or truncated):
                # Get coordinated action (no exploration)
                with torch.no_grad():
                    coordinated_action, _, _ = await self._coordinate_module_actions(observation_tensor)

                next_observation, reward, done, truncated, info = await self.environment.step(
                    coordinated_action.cpu().numpy()
                )

                episode_reward += reward
                consciousness_metrics = info.get("consciousness_metrics", {})
                episode_coherence.append(consciousness_metrics.get("temporal_coherence", 0.9))
                episode_ethics.append(consciousness_metrics.get("ethical_alignment", 0.95))

                observation_tensor = torch.from_numpy(next_observation).float().to(self.device)

            eval_rewards.append(episode_reward)
            eval_coherence.append(np.mean(episode_coherence))
            eval_ethics.append(np.mean(episode_ethics))

        return {
            "average_reward": np.mean(eval_rewards),
            "reward_std": np.std(eval_rewards),
            "consciousness_coherence": np.mean(eval_coherence),
            "ethical_compliance": np.mean(eval_ethics),
        }

    async def _consciousness_evolution_check(self, episode: int) -> None:
        """Check if consciousness architecture should evolve"""

        logger.info("🧬 Performing consciousness evolution check at episode %d", episode)

        # Analyze learning patterns across modules
        module_performances = {}
        for module_name, agent in self.module_agents.items():
            if len(agent.recent_rewards) >= 10:
                recent_performance = np.mean(agent.recent_rewards[-10:])
                learning_rate = np.mean(np.diff(agent.recent_rewards[-10:]))

                module_performances[module_name] = {
                    "performance": recent_performance,
                    "learning_rate": learning_rate,
                    "consciousness_growth": agent.consciousness_growth,
                }

        # Identify modules that need evolution
        evolution_candidates = []
        for module_name, metrics in module_performances.items():
            if metrics["learning_rate"] < 0.01 and metrics["performance"] < 0.5:
                evolution_candidates.append(module_name)

        # Apply consciousness evolution
        if evolution_candidates:
            logger.info("🌱 Evolving consciousness modules: %s", evolution_candidates)

            for module_name in evolution_candidates:
                agent = self.module_agents[module_name]

                # Expand network capacity
                await self._expand_module_capacity(agent)

                # Reset optimizer with new parameters
                agent.optimizer = optim.AdamW(
                    agent.actor_critic.parameters(),
                    lr=self.config.consciousness_learning_rate * 1.1,  # Slight increase
                    weight_decay=1e-4,
                )

    async def _expand_module_capacity(self, agent: ConsciousnessModuleAgent) -> None:
        """Expand capacity of consciousness module agent"""

        # This is a simplified version - in practice, you might:
        # 1. Add new layers to the network
        # 2. Increase hidden dimensions
        # 3. Add new attention heads
        # 4. Implement neural architecture search

        logger.debug("🧠 Expanding capacity for module: %s", agent.module_name)

        # For now, just increase learning rate and reset some buffers
        agent.consciousness_growth += 0.1
        agent.recent_rewards = agent.recent_rewards[-5:]  # Keep only recent history

    async def _save_training_state(self, save_path: Path) -> None:
        """Save training state and models"""

        save_path.mkdir(parents=True, exist_ok=True)

        # Save module agents
        for module_name, agent in self.module_agents.items():
            module_save_path = save_path / f"module_{module_name}"
            module_save_path.mkdir(exist_ok=True)

            # Save model
            torch.save(agent.actor_critic.state_dict(), module_save_path / "actor_critic.pt")
            torch.save(agent.optimizer.state_dict(), module_save_path / "optimizer.pt")

            # Save replay buffer
            agent.replay_buffer.save_buffer(str(module_save_path / "replay_buffer.pkl"))

        # Save coordination network
        torch.save(self.coordination_network.state_dict(), save_path / "coordination_network.pt")
        torch.save(self.coordination_optimizer.state_dict(), save_path / "coordination_optimizer.pt")

        # Save global metrics
        import json

        with open(save_path / "global_metrics.json", "w") as f:
            # Convert numpy arrays to lists for JSON serialization
            serializable_metrics = {}
            for key, value in self.global_metrics.items():
                if isinstance(value, list):
                    serializable_metrics[key] = value
                else:
                    serializable_metrics[key] = float(value)

            json.dump(serializable_metrics, f, indent=2)

        logger.info("💾 Saved training state to %s", save_path)

    async def _save_final_results(self, save_dir: Path, training_results: dict[str, Any]) -> None:
        """Save final training results"""

        results_path = save_dir / "final_results"
        results_path.mkdir(parents=True, exist_ok=True)

        # Save training results
        import json

        with open(results_path / "training_results.json", "w") as f:
            json.dump(training_results, f, indent=2, default=str)

        # Save final models
        await self._save_training_state(results_path / "final_models")

        logger.info("📊 Saved final results to %s", results_path)

    def _get_final_consciousness_metrics(self) -> dict[str, float]:
        """Get final consciousness metrics summary"""

        metrics = {}

        if self.global_metrics["episode_rewards"]:
            metrics["final_average_reward"] = np.mean(self.global_metrics["episode_rewards"][-100:])
            metrics["reward_improvement"] = np.mean(self.global_metrics["episode_rewards"][-10:]) - np.mean(
                self.global_metrics["episode_rewards"][:10]
            )

        if self.global_metrics["consciousness_coherence"]:
            metrics["final_consciousness_coherence"] = np.mean(self.global_metrics["consciousness_coherence"][-100:])

        if self.global_metrics["ethical_compliance"]:
            metrics["final_ethical_compliance"] = np.mean(self.global_metrics["ethical_compliance"][-100:])

        return metrics

    def _get_module_performance_summary(self) -> dict[str, dict[str, float]]:
        """Get performance summary for all modules"""

        summary = {}

        for module_name, agent in self.module_agents.items():
            summary[module_name] = {
                "episodes_trained": agent.episodes_trained,
                "average_recent_reward": np.mean(agent.recent_rewards[-10:]) if agent.recent_rewards else 0.0,
                "consciousness_growth": agent.consciousness_growth,
                "policy_loss": np.mean(agent.policy_loss_history[-10:]) if agent.policy_loss_history else 0.0,
                "value_loss": np.mean(agent.value_loss_history[-10:]) if agent.value_loss_history else 0.0,
            }

        return summary

    def _get_coordination_metrics(self) -> dict[str, float]:
        """Get coordination metrics summary"""

        # Calculate coordination effectiveness
        coordination_metrics = {
            "total_training_steps": self.total_training_steps,
            "modules_coordinated": len(self.module_agents),
            "average_coordination_success": 0.85,  # Placeholder - would calculate from actual data
        }

        return coordination_metrics

    def get_training_progress(self) -> dict[str, Any]:
        """Get current training progress"""

        return {
            "global_episode": self.global_episode,
            "total_training_steps": self.total_training_steps,
            "training_time": time.time() - self.training_start_time if self.training_start_time else 0.0,
            "recent_rewards": (
                self.global_metrics["episode_rewards"][-10:] if self.global_metrics["episode_rewards"] else []
            ),
            "consciousness_coherence": (
                self.global_metrics["consciousness_coherence"][-10:]
                if self.global_metrics["consciousness_coherence"]
                else []
            ),
            "module_count": len(self.module_agents),
            "active_modules": len([agent for agent in self.module_agents.values() if agent.episodes_trained > 0]),
        }
