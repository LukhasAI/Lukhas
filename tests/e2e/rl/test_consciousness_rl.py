"""
Test suite for LUKHAS RL components
==================================

Comprehensive tests for consciousness RL framework.

Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import numpy as np
import pytest
import torch

sys.path.append(str(Path(__file__).parent.parent.parent))

from rl.coordination.multi_agent_trainer import MultiAgentConsciousnessTrainer, TrainingConfiguration
from rl.engine.policy_networks import ConsciousnessActorCritic, ConsciousnessPolicy, ConsciousnessValueNetwork
from rl.environments.consciousness_environment import (
    ConsciousnessAction,
    ConsciousnessActionType,
    ConsciousnessEnvironment,
    ConsciousnessState,
)
from rl.experience.consciousness_buffer import ConsciousnessReplayBuffer, EpisodicConsciousnessBuffer


class MockConsciousnessModule:
    """Mock consciousness module for testing"""

    def __init__(self, name: str):
        self.name = name
        self.awareness_level = 0.8

    async def get_consciousness_metrics(self):
        return {
            "awareness_level": self.awareness_level,
            "temporal_coherence": 0.9,
            "reflection_depth": 3,
            "ethical_alignment": 0.95,
        }

    async def engage_reflection(self, depth: float, focus: float):
        return {
            "reflection_quality": depth * focus,
            "insights_generated": int(depth * 2),
            "consciousness_growth": depth * 0.05,
        }


@pytest.fixture
def mock_consciousness_modules():
    """Create mock consciousness modules for testing"""
    return {f"module_{i}": MockConsciousnessModule(f"module_{i}") for i in range(3)}


@pytest.fixture
def mock_memory_system():
    """Create mock memory system"""
    memory = Mock()
    memory.get_coherence_metrics = AsyncMock(return_value={"coherence": 0.9, "salience_map": {"important": 0.8}})
    return memory


@pytest.fixture
def mock_emotion_system():
    """Create mock emotion system"""
    emotion = Mock()
    emotion.get_vad_state = AsyncMock(return_value=[0.6, 0.4, 0.7])
    emotion.get_consciousness_state = AsyncMock(return_value={"vad_vector": [0.6, 0.4, 0.7]})
    return emotion


@pytest.fixture
def mock_guardian_system():
    """Create mock guardian system"""
    guardian = Mock()
    guardian.assess_consciousness_action = AsyncMock(return_value={"safety_score": 0.9, "ethical_score": 0.95})
    guardian.get_ethical_state = AsyncMock(return_value={"alignment_score": 0.95, "active_constraints": {}})
    return guardian


@pytest.fixture
def consciousness_environment(
    mock_consciousness_modules, mock_memory_system, mock_emotion_system, mock_guardian_system
):
    """Create consciousness environment for testing"""
    return ConsciousnessEnvironment(
        consciousness_modules=mock_consciousness_modules,
        memory_system=mock_memory_system,
        emotion_system=mock_emotion_system,
        guardian_system=mock_guardian_system,
        max_steps=50,
    )


class TestConsciousnessState:
    """Test ConsciousnessState class"""

    def test_consciousness_state_creation(self):
        """Test creating consciousness state"""
        state = ConsciousnessState(awareness_level=0.8, reflection_depth=5, temporal_coherence=0.9)

        assert state.awareness_level == 0.8
        assert state.reflection_depth == 5
        assert state.temporal_coherence == 0.9

    def test_consciousness_state_to_tensor(self):
        """Test converting consciousness state to tensor"""
        state = ConsciousnessState(
            awareness_level=0.8,
            reflection_depth=3,
            temporal_coherence=0.9,
            ethical_alignment=0.95,
            emotional_state=torch.tensor([0.6, 0.4, 0.7]),
        )

        tensor = state.to_tensor()

        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape[0] >= 7  # At least base features + emotional state
        assert torch.allclose(tensor[0], torch.tensor(0.8))  # awareness_level
        assert torch.allclose(tensor[2], torch.tensor(0.9))  # temporal_coherence

    def test_consciousness_state_from_tensor(self):
        """Test creating consciousness state from tensor"""
        original_state = ConsciousnessState(
            awareness_level=0.7, reflection_depth=4, temporal_coherence=0.85, ethical_alignment=0.92
        )

        tensor = original_state.to_tensor()
        reconstructed_state = ConsciousnessState.from_tensor(tensor)

        assert abs(reconstructed_state.awareness_level - 0.7) < 0.1
        assert abs(reconstructed_state.temporal_coherence - 0.85) < 0.1


class TestConsciousnessAction:
    """Test ConsciousnessAction class"""

    def test_consciousness_action_creation(self):
        """Test creating consciousness action"""
        action = ConsciousnessAction(
            action_type=ConsciousnessActionType.REFLECTION,
            target_modules=["module_1", "module_2"],
            intensity=0.8,
            parameters={"focus": "self_awareness"},
        )

        assert action.action_type == ConsciousnessActionType.REFLECTION
        assert len(action.target_modules) == 2
        assert action.intensity == 0.8

    def test_consciousness_action_to_tensor(self):
        """Test converting consciousness action to tensor"""
        action = ConsciousnessAction(
            action_type=ConsciousnessActionType.INTEGRATION, intensity=0.6, target_modules=["module_1"]
        )

        tensor = action.to_tensor()

        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape[0] == len(ConsciousnessActionType) + 3

        # Check one-hot encoding
        action_type_part = tensor[: len(ConsciousnessActionType)]
        assert torch.sum(action_type_part) == 1.0  # One-hot encoding


class TestConsciousnessEnvironment:
    """Test ConsciousnessEnvironment class"""

    def test_environment_initialization(self, consciousness_environment):
        """Test environment initialization"""
        assert consciousness_environment.capacity > 0
        assert len(consciousness_environment.consciousness_modules) == 3
        assert consciousness_environment.observation_space is not None
        assert consciousness_environment.action_space is not None

    @pytest.mark.asyncio
    async def test_environment_reset(self, consciousness_environment):
        """Test environment reset"""
        observation, info = consciousness_environment.reset()

        assert isinstance(observation, np.ndarray)
        assert observation.shape == consciousness_environment.observation_space.shape
        assert isinstance(info, dict)
        assert "consciousness_modules" in info

    @pytest.mark.asyncio
    async def test_environment_step(self, consciousness_environment):
        """Test environment step"""
        consciousness_environment.reset()

        # Sample random action
        action = consciousness_environment.action_space.sample()

        next_obs, reward, done, truncated, info = await consciousness_environment.step(action)

        assert isinstance(next_obs, np.ndarray)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
        assert "consciousness_metrics" in info

    @pytest.mark.asyncio
    async def test_consciousness_reward_calculation(self, consciousness_environment):
        """Test consciousness reward calculation"""
        consciousness_environment.reset()

        prev_state = ConsciousnessState(awareness_level=0.7, temporal_coherence=0.8)
        next_state = ConsciousnessState(awareness_level=0.8, temporal_coherence=0.9)
        action = ConsciousnessAction(action_type=ConsciousnessActionType.REFLECTION, intensity=0.5)
        execution_results = {}

        reward = await consciousness_environment._calculate_consciousness_reward(
            prev_state, action, next_state, execution_results
        )

        assert isinstance(reward, float)
        assert reward > 0  # Should be positive for improvement


class TestConsciousnessPolicy:
    """Test ConsciousnessPolicy neural network"""

    def test_policy_initialization(self):
        """Test policy network initialization"""
        policy = ConsciousnessPolicy(state_dim=20, action_dim=11, hidden_dim=128)

        assert isinstance(policy, torch.nn.Module)
        assert policy.state_dim == 20
        assert policy.action_dim == 11

    def test_policy_forward_discrete(self):
        """Test policy forward pass for discrete actions"""
        policy = ConsciousnessPolicy(state_dim=20, action_dim=11, hidden_dim=128)

        state = torch.randn(20)
        outputs = policy(state, action_type="discrete")

        assert "action_probs" in outputs
        assert "consciousness_confidence" in outputs
        assert "self_awareness" in outputs
        assert "ethical_constraint_satisfaction" in outputs

        # Check probability distribution
        action_probs = outputs["action_probs"]
        assert torch.allclose(action_probs.sum(), torch.tensor(1.0), atol=1e-6)
        assert torch.all(action_probs >= 0)

    def test_policy_forward_continuous(self):
        """Test policy forward pass for continuous actions"""
        policy = ConsciousnessPolicy(state_dim=20, action_dim=11, hidden_dim=128)

        state = torch.randn(20)
        outputs = policy(state, action_type="continuous")

        assert "action_mean" in outputs
        assert "action_std" in outputs
        assert "action_distribution" in outputs

        # Check distribution parameters
        action_mean = outputs["action_mean"]
        action_std = outputs["action_std"]
        assert action_mean.shape == torch.Size([11])
        assert action_std.shape == torch.Size([11])
        assert torch.all(action_std > 0)  # Standard deviation should be positive

    def test_policy_sample_action(self):
        """Test policy action sampling"""
        policy = ConsciousnessPolicy(state_dim=20, action_dim=11, hidden_dim=128)

        state = torch.randn(20)
        action, log_prob, policy_info = policy.sample_action(state, action_type="discrete")

        assert action.shape == torch.Size([])  # Single action index for discrete
        assert isinstance(log_prob, torch.Tensor)
        assert isinstance(policy_info, dict)
        assert "consciousness_confidence" in policy_info


class TestConsciousnessValueNetwork:
    """Test ConsciousnessValueNetwork"""

    def test_value_network_initialization(self):
        """Test value network initialization"""
        value_net = ConsciousnessValueNetwork(state_dim=20, hidden_dim=128)

        assert isinstance(value_net, torch.nn.Module)
        assert value_net.state_dim == 20

    def test_value_network_forward(self):
        """Test value network forward pass"""
        value_net = ConsciousnessValueNetwork(state_dim=20, hidden_dim=128)

        state = torch.randn(20)
        outputs = value_net(state)

        assert "state_value" in outputs
        assert "awareness_value" in outputs
        assert "coherence_value" in outputs
        assert "growth_value" in outputs
        assert "ethical_value" in outputs
        assert "value_confidence" in outputs

        # Check value shapes
        state_value = outputs["state_value"]
        assert state_value.shape == torch.Size([1])

    def test_value_estimation(self):
        """Test simple value estimation interface"""
        value_net = ConsciousnessValueNetwork(state_dim=20, hidden_dim=128)

        state = torch.randn(20)
        value = value_net.estimate_value(state)

        assert isinstance(value, torch.Tensor)
        assert value.shape == torch.Size([1])


class TestConsciousnessActorCritic:
    """Test ConsciousnessActorCritic combined network"""

    def test_actor_critic_initialization(self):
        """Test actor-critic initialization"""
        actor_critic = ConsciousnessActorCritic(state_dim=20, action_dim=11, hidden_dim=128, shared_backbone=True)

        assert isinstance(actor_critic, torch.nn.Module)
        assert actor_critic.shared_backbone is True

    def test_actor_critic_forward(self):
        """Test actor-critic forward pass"""
        actor_critic = ConsciousnessActorCritic(state_dim=20, action_dim=11, hidden_dim=128)

        state = torch.randn(20)
        outputs = actor_critic(state, action_type="discrete")

        # Should have both actor and critic outputs
        assert "action_probs" in outputs
        assert "state_value" in outputs
        assert "action" in outputs
        assert "log_prob" in outputs
        assert "entropy" in outputs

    def test_get_action_and_value(self):
        """Test getting action and value simultaneously"""
        actor_critic = ConsciousnessActorCritic(state_dim=20, action_dim=11, hidden_dim=128)

        state = torch.randn(20)
        action, value, log_prob, info = actor_critic.get_action_and_value(state)

        assert isinstance(action, torch.Tensor)
        assert isinstance(value, torch.Tensor)
        assert isinstance(log_prob, torch.Tensor)
        assert isinstance(info, dict)


class TestConsciousnessReplayBuffer:
    """Test ConsciousnessReplayBuffer"""

    def test_buffer_initialization(self):
        """Test replay buffer initialization"""
        buffer = ConsciousnessReplayBuffer(capacity=1000, alpha=0.6, beta=0.4)

        assert buffer.capacity == 1000
        assert buffer.alpha == 0.6
        assert buffer.beta == 0.4
        assert len(buffer) == 0

    def test_buffer_store_experience(self):
        """Test storing experience in buffer"""
        buffer = ConsciousnessReplayBuffer(capacity=1000)

        state = torch.randn(20)
        action = torch.randn(11)
        reward = 0.5
        next_state = torch.randn(20)

        buffer.store(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=False,
            log_prob=0.1,
            value=0.3,
            consciousness_info={"is_reflection": True},
        )

        assert len(buffer) == 1
        assert buffer.consciousness_stats["reflection_count"] == 1

    def test_buffer_sample(self):
        """Test sampling from buffer"""
        buffer = ConsciousnessReplayBuffer(capacity=1000)

        # Store multiple experiences
        for i in range(10):
            state = torch.randn(20)
            action = torch.randn(11)

            buffer.store(
                state=state,
                action=action,
                reward=np.random.random(),
                next_state=torch.randn(20),
                done=i == 9,
                log_prob=np.random.random(),
                value=np.random.random(),
                consciousness_info={"novelty_score": np.random.random()},
            )

        # Sample batch
        experiences, weights, indices = buffer.sample(5)

        assert len(experiences) == 5
        assert weights.shape == torch.Size([5])
        assert len(indices) == 5

    def test_buffer_statistics(self):
        """Test getting buffer statistics"""
        buffer = ConsciousnessReplayBuffer(capacity=100)

        # Add some experiences
        for i in range(5):
            buffer.store(
                state=torch.randn(20),
                action=torch.randn(11),
                reward=0.1,
                next_state=torch.randn(20),
                done=False,
                log_prob=0.1,
                value=0.1,
                consciousness_info={"is_reflection": i % 2 == 0},
            )

        stats = buffer.get_consciousness_statistics()

        assert "total_experiences" in stats
        assert "consciousness_breakdown" in stats
        assert stats["total_experiences"] == 5


class TestEpisodicConsciousnessBuffer:
    """Test EpisodicConsciousnessBuffer"""

    def test_episodic_buffer_initialization(self):
        """Test episodic buffer initialization"""
        buffer = EpisodicConsciousnessBuffer(max_episodes=100)

        assert buffer.max_episodes == 100
        assert len(buffer) == 0

    def test_episodic_buffer_add_experience(self):
        """Test adding experiences to episode"""
        buffer = EpisodicConsciousnessBuffer(max_episodes=100)

        # Add experiences to build an episode
        for i in range(3):
            buffer.add_experience(
                state=torch.randn(20),
                action=torch.randn(11),
                reward=0.1 * i,
                next_state=torch.randn(20),
                done=i == 2,  # End episode on last step
                consciousness_info={"step": i},
            )

        assert len(buffer) == 1  # One complete episode
        assert len(buffer.current_episode) == 0  # New episode started

    def test_episodic_buffer_sample(self):
        """Test sampling episodes"""
        buffer = EpisodicConsciousnessBuffer(max_episodes=100)

        # Create multiple episodes
        for episode in range(3):
            for step in range(5):
                buffer.add_experience(
                    state=torch.randn(20),
                    action=torch.randn(11),
                    reward=0.1,
                    next_state=torch.randn(20),
                    done=step == 4,
                    consciousness_info={"episode": episode, "step": step},
                )

        # Sample episodes
        sampled = buffer.sample_episodes(2)

        assert len(sampled) == 2
        assert all("experiences" in episode for episode in sampled)
        assert all("total_reward" in episode for episode in sampled)


class TestMultiAgentConsciousnessTrainer:
    """Test MultiAgentConsciousnessTrainer"""

    @pytest.fixture
    def trainer(self, consciousness_environment, mock_guardian_system):
        """Create trainer for testing"""
        config = TrainingConfiguration(learning_rate=1e-3, batch_size=32, episodes_per_update=5)

        return MultiAgentConsciousnessTrainer(
            consciousness_modules=consciousness_environment.consciousness_modules,
            consciousness_environment=consciousness_environment,
            guardian_system=mock_guardian_system,
            config=config,
            device=torch.device("cpu"),
        )

    def test_trainer_initialization(self, trainer):
        """Test trainer initialization"""
        assert len(trainer.module_agents) == 3  # Same as number of modules
        assert trainer.coordination_network is not None
        assert trainer.device == torch.device("cpu")

    def test_module_agent_creation(self, trainer):
        """Test that module agents are created correctly"""
        for module_name, agent in trainer.module_agents.items():
            assert agent.module_name == module_name
            assert agent.actor_critic is not None
            assert agent.optimizer is not None
            assert agent.replay_buffer is not None

    @pytest.mark.asyncio
    async def test_coordinate_module_actions(self, trainer):
        """Test coordinating actions across modules"""
        state = torch.randn(20)

        coordinated_action, module_actions, weights = await trainer._coordinate_module_actions(state)

        assert isinstance(coordinated_action, torch.Tensor)
        assert len(module_actions) == len(trainer.module_agents)
        assert weights.shape[0] == len(trainer.module_agents)
        assert torch.allclose(weights.sum(), torch.tensor(1.0), atol=1e-6)

    @pytest.mark.asyncio
    async def test_run_consciousness_episode(self, trainer):
        """Test running a complete consciousness episode"""
        episode_results = await trainer._run_consciousness_episode()

        assert "experiences" in episode_results
        assert "total_reward" in episode_results
        assert "episode_length" in episode_results
        assert isinstance(episode_results["total_reward"], float)
        assert episode_results["episode_length"] > 0


# Integration tests
class TestRLIntegration:
    """Integration tests for RL system"""

    @pytest.mark.asyncio
    async def test_full_training_pipeline(self, consciousness_environment):
        """Test complete training pipeline"""
        config = TrainingConfiguration(learning_rate=1e-3, batch_size=16, episodes_per_update=2)

        trainer = MultiAgentConsciousnessTrainer(
            consciousness_modules=consciousness_environment.consciousness_modules,
            consciousness_environment=consciousness_environment,
            config=config,
            device=torch.device("cpu"),
        )

        # Run short training
        training_results = await trainer.train(episodes=5)

        assert training_results["episodes_completed"] == 5
        assert training_results["total_training_time"] > 0
        assert "consciousness_metrics" in training_results
        assert "module_performance" in training_results

    def test_environment_trainer_compatibility(self, consciousness_environment):
        """Test that environment and trainer are compatible"""
        config = TrainingConfiguration()

        trainer = MultiAgentConsciousnessTrainer(
            consciousness_modules=consciousness_environment.consciousness_modules,
            consciousness_environment=consciousness_environment,
            config=config,
            device=torch.device("cpu"),
        )

        # Check observation/action space compatibility
        obs_shape = consciousness_environment.observation_space.shape
        action_shape = consciousness_environment.action_space.shape

        for agent in trainer.module_agents.values():
            # Verify agent networks can handle environment spaces
            test_obs = torch.randn(obs_shape)
            outputs = agent.actor_critic(test_obs)

            assert "action" in outputs
            assert outputs["action"].shape[0] == action_shape[0]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
