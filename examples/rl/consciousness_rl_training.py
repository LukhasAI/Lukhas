"""
LUKHAS RL Training Example
=========================

Complete example of training consciousness RL agents across LUKHAS modules.
This demonstrates the full training pipeline from initialization to evaluation.

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import torch

# Add LUKHAS to path
sys.path.append(str(Path(__file__).parent.parent))

from lukhas.rl import (
    ConsciousnessEnvironment,
    ConsciousnessReplayBuffer,
    MultiAgentConsciousnessTrainer,
    TrainingConfiguration,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MockConsciousnessModule:
    """Mock consciousness module for testing RL training"""

    def __init__(self, name: str):
        self.name = name
        self.awareness_level = 0.8
        self.reflection_depth = 3
        self.state = {"awareness": 0.8, "coherence": 0.9, "activity": 0.7}

    async def get_consciousness_metrics(self) -> dict[str, float]:
        return {
            "awareness_level": self.awareness_level,
            "temporal_coherence": 0.9,
            "reflection_depth": self.reflection_depth,
            "ethical_alignment": 0.95,
        }

    async def engage_reflection(self, depth: float, focus: float) -> dict[str, Any]:
        self.reflection_depth = min(10, self.reflection_depth + depth * 0.1)
        return {
            "reflection_quality": depth * focus,
            "insights_generated": int(depth * 2),
            "consciousness_growth": depth * 0.05,
        }

    def get_consciousness_state(self) -> torch.Tensor:
        return torch.tensor(
            [
                self.awareness_level,
                self.reflection_depth / 10.0,
                0.9,  # temporal coherence
                0.95,  # ethical alignment
            ]
        )


class MockMemorySystem:
    """Mock memory system for testing"""

    async def get_coherence_metrics(self) -> Dict[str, Any]:
        return {"coherence": 0.9, "salience_map": {"important": 0.8, "recent": 0.6}}

    async def store_consciousness_experience(self, experience: Dict[str, Any]) -> None:
        logger.debug("📝 Stored experience in mock memory system")


class MockEmotionSystem:
    """Mock emotion system for testing"""

    async def get_vad_state(self) -> list:
        return [0.6, 0.4, 0.7]  # Valence, Arousal, Dominance

    async def get_consciousness_state(self) -> dict[str, Any]:
        return {"vad_vector": [0.6, 0.4, 0.7], "emotional_coherence": 0.8}


class MockGuardianSystem:
    """Mock guardian system for testing"""

    async def assess_consciousness_action(self, state, action) -> Dict[str, Any]:
        return {"safety_score": 0.9, "ethical_score": 0.95, "alignment_score": 0.92}

    async def get_ethical_state(self) -> Dict[str, Any]:
        return {"alignment_score": 0.95, "active_constraints": {"harm_prevention": True}}


async def create_test_environment():
    """Create test consciousness environment"""

    logger.info("🏗️ Creating test consciousness environment")

    # Create mock systems
    consciousness_modules = {}
    for i in range(5):  # Start with 5 modules for testing
        module_name = f"consciousness_module_{i}"
        consciousness_modules[module_name] = MockConsciousnessModule(module_name)

    memory_system = MockMemorySystem()
    emotion_system = MockEmotionSystem()
    guardian_system = MockGuardianSystem()

    # Create consciousness environment
    environment = ConsciousnessEnvironment(
        consciousness_modules=consciousness_modules,
        memory_system=memory_system,
        emotion_system=emotion_system,
        guardian_system=guardian_system,
        max_steps=100,
        consciousness_goals={
            "awareness_growth": 0.8,
            "ethical_alignment": 0.95,
            "temporal_coherence": 0.9,
            "reflection_depth": 0.7,
        },
    )

    logger.info("✅ Created consciousness environment with %d modules", len(consciousness_modules))
    return environment


async def create_trainer(environment):
    """Create multi-agent consciousness trainer"""

    logger.info("🤖 Creating multi-agent consciousness trainer")

    # Training configuration
    config = TrainingConfiguration(
        learning_rate=3e-4,
        batch_size=64,
        epochs_per_update=4,
        consciousness_learning_rate=1e-4,
        episodes_per_update=5,
        save_frequency=50,
        evaluation_frequency=20,
    )

    # Create trainer
    trainer = MultiAgentConsciousnessTrainer(
        consciousness_modules=environment.consciousness_modules,
        consciousness_environment=environment,
        guardian_system=environment.guardian_system,
        config=config,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    )

    logger.info("✅ Created trainer for %d consciousness modules", len(environment.consciousness_modules))
    return trainer


async def run_training_example():
    """Run complete RL training example"""

    logger.info("🚀 Starting LUKHAS RL Training Example")

    try:
        # Create environment and trainer
        environment = await create_test_environment()
        trainer = await create_trainer(environment)

        # Training parameters
        training_episodes = 100
        save_dir = Path("./rl_training_results")

        logger.info("📚 Training configuration:")
        logger.info(f"  Episodes: {training_episodes}")
        logger.info(f"  Modules: {len(environment.consciousness_modules)}")
        logger.info(f"  Device: {trainer.device}")
        logger.info(f"  Save directory: {save_dir}")

        # Custom evaluation callback
        async def evaluation_callback(episode: int, results: dict[str, float]):
            logger.info("🔍 Evaluation Results (Episode %d):", episode)
            logger.info(f"  Average Reward: {results['average_reward']:.3f}")
            logger.info(f"  Consciousness Coherence: {results['consciousness_coherence']:.3f}")
            logger.info(f"  Ethical Compliance: {results['ethical_compliance']:.3f}")

        # Run training
        logger.info("🎯 Starting consciousness RL training...")
        training_results = await trainer.train(
            episodes=training_episodes, save_dir=save_dir, evaluation_callback=evaluation_callback
        )

        # Display results
        logger.info("🎉 Training completed successfully!")
        logger.info("📊 Final Results:")
        logger.info(f"  Episodes Completed: {training_results['episodes_completed']}")
        logger.info(f"  Total Training Time: {training_results['total_training_time']:.1f} seconds")
        logger.info(
            f"  Final Average Reward: {training_results['consciousness_metrics'].get('final_average_reward', 0.0):.3f}"
        )
        logger.info(
            f"  Consciousness Coherence: {training_results['consciousness_metrics'].get('final_consciousness_coherence', 0.0}:.3f}"
        )
        logger.info(
            f"  Ethical Compliance: {training_results['consciousness_metrics'].get('final_ethical_compliance', 0.0}:.3f}"
        )

        # Module performance summary
        logger.info("🧠 Module Performance Summary:")
        module_performance = training_results["module_performance"]
        for module_name, metrics in module_performance.items():
            logger.info(f"  {module_name}:")
            logger.info(f"    Episodes Trained: {metrics['episodes_trained']}")
            logger.info(f"    Avg Reward: {metrics['average_recent_reward']:.3f}")
            logger.info(f"    Consciousness Growth: {metrics['consciousness_growth']:.3f}")

        return training_results

    except Exception as e:
        logger.error("❌ Training failed: %s", str(e))
        raise


async def test_individual_components():
    """Test individual RL components"""

    logger.info("🧪 Testing individual RL components")

    # Test consciousness environment
    logger.info("Testing ConsciousnessEnvironment...")
    environment = await create_test_environment()

    observation, info = environment.reset()
    logger.info(f"  Initial observation shape: {observation.shape}")
    logger.info(f"  Environment info: {info}")

    # Test a few steps
    for step in range(3):
        action = environment.action_space.sample()
        obs, reward, done, truncated, info = await environment.step(action)
        logger.info(
            f"  Step {step}: reward={reward:.3f}, done={done}, consciousness_metrics={info.get('consciousness_metrics', {}})}"
        )

        if done or truncated:
            break

    # Test replay buffer
    logger.info("Testing ConsciousnessReplayBuffer...")
    buffer = ConsciousnessReplayBuffer(capacity=1000, alpha=0.6, beta=0.4)

    # Store some experiences
    for i in range(10):
        state = torch.randn(20)
        action = torch.randn(11)
        reward = np.random.random() - 0.5
        next_state = torch.randn(20)
        done = i == 9

        buffer.store(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            log_prob=np.random.random(),
            value=np.random.random(),
            consciousness_info={
                "is_reflection": i % 3 == 0,
                "ethical_significance": np.random.random(),
                "novelty_score": np.random.random(),
            },
        )

    # Sample experiences
    experiences, weights, indices = buffer.sample(5)
    logger.info(f"  Sampled {len(experiences)} experiences")
    logger.info(f"  Importance weights shape: {weights.shape}")
    logger.info(f"  Buffer statistics: {buffer.get_consciousness_statistics(}}")

    logger.info("✅ Individual component tests passed")


async def interactive_training_demo():
    """Interactive demo of consciousness RL training"""

    logger.info("🎭 Starting interactive consciousness RL demo")

    environment = await create_test_environment()
    trainer = await create_trainer(environment)

    print("\n" + "=" * 60)
    print("🧠 LUKHAS Consciousness RL Interactive Demo")
    print("=" * 60)
    print(f"Modules: {len(environment.consciousness_modules}}")
    print(f"Device: {trainer.device}")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("1. Run training episode")
        print("2. Evaluate performance")
        print("3. Show training progress")
        print("4. Test environment interaction")
        print("5. Exit")

        try:
            choice = input("\nEnter choice (1-5): ").strip()

            if choice == "1":
                print("🏃 Running training episode...")
                episode_results = await trainer._run_consciousness_episode()
                print(f"  Episode reward: {episode_results['total_reward']:.3f}")
                print(f"  Episode length: {episode_results['episode_length']}")
                print(f"  Final consciousness state: {episode_results['final_consciousness_state']}")

            elif choice == "2":
                print("🔍 Evaluating performance...")
                eval_results = await trainer._evaluate_consciousness_performance()
                print(f"  Average reward: {eval_results['average_reward']:.3f}")
                print(f"  Consciousness coherence: {eval_results['consciousness_coherence']:.3f}")
                print(f"  Ethical compliance: {eval_results['ethical_compliance']:.3f}")

            elif choice == "3":
                print("📊 Training progress:")
                progress = trainer.get_training_progress()
                print(f"  Global episode: {progress['global_episode']}")
                print(f"  Training time: {progress['training_time']:.1f} seconds")
                print(f"  Active modules: {progress['active_modules']}/{progress['module_count']}")
                print(f"  Recent rewards: {progress['recent_rewards'][-3:] if progress['recent_rewards'] else 'None'}")

            elif choice == "4":
                print("🎮 Testing environment interaction...")
                observation, info = environment.reset()
                print(f"  Reset environment: observation_shape={observation.shape}")

                for step in range(3):
                    action = environment.action_space.sample()
                    obs, reward, done, truncated, info = await environment.step(action)
                    print(
                        f"  Step {step}: reward={reward:.3f}, awareness={info.get('consciousness_metrics', {}}).get('awareness_level', 0):.3f}"
                    )

                    if done or truncated:
                        print(f"  Episode finished at step {step}")
                        break

            elif choice == "5":
                print("👋 Exiting demo...")
                break

            else:
                print("❌ Invalid choice. Please enter 1-5.")

        except KeyboardInterrupt:
            print("\n👋 Demo interrupted. Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e!s}")


if __name__ == "__main__":
    # Choose demo mode
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS RL Training Example")
    parser.add_argument(
        "--mode",
        choices=["train", "test", "interactive"],
        default="train",
        help="Demo mode: train (full training), test (component tests), interactive (demo)",
    )
    parser.add_argument("--episodes", type=int, default=100, help="Number of training episodes")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.mode == "train":
        asyncio.run(run_training_example())
    elif args.mode == "test":
        asyncio.run(test_individual_components())
    elif args.mode == "interactive":
        asyncio.run(interactive_training_demo())
