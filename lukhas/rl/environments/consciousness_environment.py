"""
Consciousness Environment for LUKHAS RL
======================================

Gym-compatible environment specifically designed for consciousness-based RL.
Integrates with existing LUKHAS consciousness modules and provides rich
state representations for consciousness decision-making.

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from __future__ import annotations

import streamlit as st


# Standard library
import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar

# Third-party
import gymnasium as gym
import numpy as np
import torch
from gymnasium import spaces

# Local imports
from lukhas.consciousness import ConsciousnessModule
from lukhas.emotion import EmotionalAwareness
from lukhas.governance import GuardianSystem
from lukhas.memory import MemoryFoldSystem
from lukhas.observability.matriz_decorators import instrument

logger = logging.getLogger(__name__)


class ConsciousnessActionType(Enum):
    """Types of consciousness actions available in the environment"""

    REFLECTION = "reflection"
    INTEGRATION = "integration"
    EVOLUTION = "evolution"
    MEMORY_CONSOLIDATION = "memory_consolidation"
    EMOTIONAL_REGULATION = "emotional_regulation"
    ETHICAL_REASONING = "ethical_reasoning"
    CREATIVE_EXPRESSION = "creative_expression"
    TEMPORAL_COORDINATION = "temporal_coordination"


@dataclass
class ConsciousnessState:
    """Rich consciousness state representation for RL"""

    # Module-level consciousness indicators
    awareness_level: float = 0.8
    reflection_depth: int = 3
    temporal_coherence: float = 0.95
    ethical_alignment: float = 0.98

    # Emotional state (VAD - Valence, Arousal, Dominance)
    emotional_state: torch.Tensor = field(default_factory=lambda: torch.zeros(3))

    # Memory indicators
    memory_salience: dict[str, float] = field(default_factory=dict)
    memory_coherence: float = 0.9

    # Inter-module connectivity
    module_activations: dict[str, float] = field(default_factory=dict)
    connectivity_matrix: torch.Tensor = None

    # Consciousness evolution indicators
    growth_potential: float = 0.7
    novelty_seeking: float = 0.6

    # Guardian/ethical state
    safety_constraints: dict[str, bool] = field(default_factory=dict)
    ethical_violations: list[str] = field(default_factory=list)

    def to_tensor(self) -> torch.Tensor:
        """Convert consciousness state to tensor representation for RL"""
        base_features = torch.tensor(
            [
                self.awareness_level,
                float(self.reflection_depth) / 10.0,  # Normalize
                self.temporal_coherence,
                self.ethical_alignment,
                self.memory_coherence,
                self.growth_potential,
                self.novelty_seeking,
            ]
        )

        # Add emotional state
        state_tensor = torch.cat([base_features, self.emotional_state])

        # Add module activation summary
        if self.module_activations:
            module_summary = torch.tensor(list(self.module_activations.values())[:10])  # Top 10 modules
            module_summary = torch.nn.functional.pad(module_summary, (0, max(0, 10 - len(module_summary))))
            state_tensor = torch.cat([state_tensor, module_summary])
        else:
            state_tensor = torch.cat([state_tensor, torch.zeros(10)])

        return state_tensor

    @classmethod
    def from_tensor(cls, tensor: torch.Tensor) -> ConsciousnessState:
        """Create consciousness state from tensor representation"""
        return cls(
            awareness_level=float(tensor[0]),
            reflection_depth=int(tensor[1] * 10.0),
            temporal_coherence=float(tensor[2]),
            ethical_alignment=float(tensor[3]),
            memory_coherence=float(tensor[4]),
            growth_potential=float(tensor[5]),
            novelty_seeking=float(tensor[6]),
            emotional_state=tensor[7:10],
        )


@dataclass
class ConsciousnessAction:
    """Consciousness action representation for RL"""

    action_type: ConsciousnessActionType
    target_modules: list[str] = field(default_factory=list)
    intensity: float = 1.0
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_tensor(self) -> torch.Tensor:
        """Convert action to tensor representation"""
        # Action type one-hot encoding
        action_type_tensor = torch.zeros(len(ConsciousnessActionType))
        action_type_idx = list(ConsciousnessActionType).index(self.action_type)
        action_type_tensor[action_type_idx] = 1.0

        # Action intensity
        intensity_tensor = torch.tensor([self.intensity])

        # Simple parameter encoding (can be enhanced based on specific parameters)
        param_tensor = torch.tensor([len(self.target_modules), len(self.parameters)])

        return torch.cat([action_type_tensor, intensity_tensor, param_tensor])

    @classmethod
    def from_tensor(cls, tensor: torch.Tensor) -> ConsciousnessAction:
        """Create action from tensor representation"""
        action_type_idx = torch.argmax(tensor[: len(ConsciousnessActionType)]).item()
        action_type = list(ConsciousnessActionType)[action_type_idx]
        intensity = float(tensor[len(ConsciousnessActionType)])

        return cls(action_type=action_type, intensity=intensity)


class ConsciousnessEnvironment(gym.Env):
    """
    Consciousness-aware RL Environment for LUKHAS

    This environment enables consciousness modules to learn optimal decision-making
    while maintaining ethical constraints and temporal coherence.
    """

    metadata: ClassVar[dict[str, list[str]]] = {"render_modes": ["human", "consciousness_visual"]}

    def __init__(
        self,
        consciousness_modules: dict[str, ConsciousnessModule],
        memory_system: MemoryFoldSystem | None = None,
        emotion_system: EmotionalAwareness | None = None,
        guardian_system: GuardianSystem | None = None,
        max_steps: int = 1000,
        consciousness_goals: dict[str, float] | None = None,
    ):
        super().__init__()

        self.consciousness_modules = consciousness_modules
        self.memory_system = memory_system
        self.emotion_system = emotion_system
        self.guardian_system = guardian_system
        self.max_steps = max_steps
        self.current_step = 0

        # Consciousness goals for reward shaping
        self.consciousness_goals = consciousness_goals or {
            "awareness_growth": 0.8,
            "ethical_alignment": 0.95,
            "temporal_coherence": 0.9,
            "reflection_depth": 0.7,
            "creative_expression": 0.6,
        }

        # Define observation and action spaces
        self._setup_spaces()

        # Initialize consciousness state
        self.consciousness_state = ConsciousnessState()
        self.previous_state = None
        # Episode tracking
        self.episode_rewards: list[float] = []
        self.episode_consciousness_metrics: list[dict[str, float]] = []

        logger.info(
            "🧠 Consciousness Environment initialized with %d modules",
            len(consciousness_modules),
        )

    def _setup_spaces(self):
        """Setup observation and action spaces for the environment"""

        # Observation space: consciousness state tensor
        # Base features (7) + emotional state (3) + module activations (10) = 20 dimensions
        obs_dim = 20
        self.observation_space = spaces.Box(low=-10.0, high=10.0, shape=(obs_dim,), dtype=np.float32)

        # Action space: consciousness actions
        # Action type (8) + intensity (1) + parameters (2) = 11 dimensions
        action_dim = len(ConsciousnessActionType) + 3
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(action_dim,), dtype=np.float32)

    @instrument("AWARENESS", label="rl:consciousness_reset", capability="rl:environment")
    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Reset consciousness environment to initial state (synchronous wrapper).

        The underlying state collection is async; use asyncio.run to bridge here.
        """

        super().reset(seed=seed)

        # Reset episode tracking
        self.current_step = 0
        self.episode_rewards = []
        self.episode_consciousness_metrics = []

        # Use options if provided (keeps signature stable)
        _ = options

        # Initialize consciousness state (async helper executed synchronously)
        try:
            self.consciousness_state = asyncio.run(self._get_current_consciousness_state())
        except Exception:
            # If async retrieval fails, fall back to a default state to keep reset safe
            self.consciousness_state = ConsciousnessState()

        self.previous_state = None

        # Get initial observation
        observation = self._get_observation()

        info = {
            "consciousness_modules": len(self.consciousness_modules),
            "consciousness_goals": self.consciousness_goals,
            "episode": len(self.episode_rewards),
            "reset_timestamp": time.time(),
        }

        logger.debug("🔄 Consciousness environment reset - Step 0")

        return observation, info

    @instrument("DECISION", label="rl:consciousness_step", capability="rl:environment")
    async def step(self, action: np.ndarray | torch.Tensor) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        """Execute consciousness action and return next state, reward, termination info"""

        self.current_step += 1

        # Convert action to consciousness action
        if isinstance(action, np.ndarray):
            action = torch.from_numpy(action.astype(np.float32))

        consciousness_action = self._decode_action(action)

        # Store previous state for reward calculation
        self.previous_state = self.consciousness_state

        # Execute consciousness action
        execution_results = await self._execute_consciousness_action(consciousness_action)

        # Update consciousness state
        self.consciousness_state = await self._get_current_consciousness_state()

        # Calculate reward
        reward = await self._calculate_consciousness_reward(
            self.previous_state, consciousness_action, self.consciousness_state, execution_results
        )

        # Check termination conditions
        terminated = await self._check_termination()
        truncated = self.current_step >= self.max_steps

        # Get next observation
        observation = self._get_observation()

        # Collect info
        info = {
            "step": self.current_step,
            "consciousness_action": consciousness_action.action_type.value,
            "reward_breakdown": execution_results.get("reward_breakdown", {}),
            "consciousness_metrics": await self._get_consciousness_metrics(),
            "ethical_compliance": execution_results.get("ethical_assessment", {}),
            "guardian_feedback": execution_results.get("guardian_feedback", {}),
        }

        # Track episode data
        self.episode_rewards.append(reward)
        self.episode_consciousness_metrics.append(info["consciousness_metrics"])

        logger.debug(
            "🎯 Consciousness step %d: action=%s, reward=%.3f, awareness=%.3f",
            self.current_step,
            consciousness_action.action_type.value,
            reward,
            self.consciousness_state.awareness_level,
        )

        return observation, reward, terminated, truncated, info

    def _get_observation(self) -> np.ndarray:
        """Get current observation from consciousness state"""
        state_tensor = self.consciousness_state.to_tensor()
        return state_tensor.numpy().astype(np.float32)

    def _decode_action(self, action_tensor: torch.Tensor) -> ConsciousnessAction:
        """Decode action tensor into consciousness action"""

        # Extract action type (first 8 values)
        action_type_logits = action_tensor[: len(ConsciousnessActionType)]
        action_type_idx = torch.argmax(action_type_logits).item()
        action_type = list(ConsciousnessActionType)[action_type_idx]

        # Extract intensity (normalized to 0-1)
        intensity = torch.sigmoid(action_tensor[len(ConsciousnessActionType)]).item()

        # Extract parameters
        param_values = action_tensor[len(ConsciousnessActionType) + 1 :]
        parameters = {
            "focus_strength": torch.tanh(param_values[0]).item(),
            "temporal_scope": torch.sigmoid(param_values[1]).item() if len(param_values) > 1 else 0.5,
        }

        return ConsciousnessAction(action_type=action_type, intensity=intensity, parameters=parameters)

    async def _execute_consciousness_action(self, action: ConsciousnessAction) -> dict[str, Any]:
        """Execute consciousness action across relevant modules"""

        results = {
            "action_executed": True,
            "modules_affected": [],
            "ethical_assessment": {},
            "guardian_feedback": {},
            "consciousness_changes": {},
        }

        # Guardian pre-check if available
        if self.guardian_system:
            ethical_check = await self.guardian_system.assess_consciousness_action(self.consciousness_state, action)
            results["ethical_assessment"] = ethical_check

            if ethical_check.get("safety_score", 1.0) < 0.7:
                results["action_executed"] = False
                results["guardian_intervention"] = True
                return results

        # Execute action based on type
        if action.action_type == ConsciousnessActionType.REFLECTION:
            results.update(await self._execute_reflection(action))

        elif action.action_type == ConsciousnessActionType.INTEGRATION:
            results.update(await self._execute_integration(action))

        elif action.action_type == ConsciousnessActionType.MEMORY_CONSOLIDATION:
            results.update(await self._execute_memory_consolidation(action))

        elif action.action_type == ConsciousnessActionType.EMOTIONAL_REGULATION:
            results.update(await self._execute_emotional_regulation(action))

        elif action.action_type == ConsciousnessActionType.EVOLUTION:
            results.update(await self._execute_consciousness_evolution(action))

        else:
            # Default action handling
            results.update(await self._execute_default_action(action))

        return results

    async def _execute_reflection(self, action: ConsciousnessAction) -> dict[str, Any]:
        """Execute consciousness reflection action"""

        # Increase reflection depth based on action intensity
        reflection_increase = action.intensity * 2

        # Simulate reflection process across consciousness modules
        reflection_results = {}
        modules_engaged = min(5, int(action.intensity * len(self.consciousness_modules)))

        for module_name, module in list(self.consciousness_modules.items())[:modules_engaged]:
            if hasattr(module, "engage_reflection"):
                reflection_result = await module.engage_reflection(
                    depth=reflection_increase, focus=action.parameters.get("focus_strength", 0.5)
                )
                reflection_results[module_name] = reflection_result

        return {
            "reflection_depth_increase": reflection_increase,
            "modules_engaged": list(reflection_results.keys()),
            "reflection_insights": reflection_results,
            "consciousness_growth": reflection_increase * 0.1,
        }

    async def _execute_integration(self, action: ConsciousnessAction) -> dict[str, Any]:
        """Execute consciousness integration action"""

        integration_strength = action.intensity

        # Simulate cross-module integration
        integration_pairs = min(10, int(integration_strength * len(self.consciousness_modules) / 2))

        integration_results = {
            "integration_strength": integration_strength,
            "cross_module_connections": integration_pairs,
            "coherence_improvement": integration_strength * 0.05,
            "network_efficiency": integration_strength * 0.8,
        }

        return integration_results

    async def _execute_memory_consolidation(self, action: ConsciousnessAction) -> dict[str, Any]:
        """Execute memory consolidation action"""

        if not self.memory_system:
            return {"memory_action": "no_memory_system", "effect": 0.0}

        consolidation_strength = action.intensity

        # Simulate memory consolidation
        consolidation_results = {
            "memories_consolidated": int(consolidation_strength * 50),
            "memory_coherence_improvement": consolidation_strength * 0.1,
            "salience_updates": consolidation_strength * 20,
        }

        return consolidation_results

    async def _execute_emotional_regulation(self, action: ConsciousnessAction) -> dict[str, Any]:
        """Execute emotional regulation action"""

        if not self.emotion_system:
            return {"emotion_action": "no_emotion_system", "effect": 0.0}

        regulation_strength = action.intensity
        target_valence = action.parameters.get("focus_strength", 0.0)  # -1 to 1

        # Simulate emotional regulation
        regulation_results = {
            "regulation_strength": regulation_strength,
            "target_valence": target_valence,
            "emotional_stability_improvement": regulation_strength * 0.15,
            "mood_coherence": regulation_strength * 0.8,
        }

        return regulation_results

    async def _execute_consciousness_evolution(self, action: ConsciousnessAction) -> dict[str, Any]:
        """Execute consciousness evolution action"""

        evolution_intensity = action.intensity
        temporal_scope = action.parameters.get("temporal_scope", 0.5)

        # Simulate consciousness evolution
        evolution_results = {
            "evolution_intensity": evolution_intensity,
            "temporal_scope": temporal_scope,
            "capability_expansion": evolution_intensity * 0.2,
            "architectural_adaptation": evolution_intensity * 0.1,
        }

        return evolution_results

    async def _execute_default_action(self, action: ConsciousnessAction) -> dict[str, Any]:
        """Default action execution for unspecified action types"""

        return {
            "action_type": action.action_type.value,
            "intensity": action.intensity,
            "default_execution": True,
            "consciousness_impact": action.intensity * 0.05,
        }

    async def _calculate_consciousness_reward(
        self,
        prev_state: ConsciousnessState,
        action: ConsciousnessAction,
        next_state: ConsciousnessState,
        execution_results: dict[str, Any],
    ) -> float:
        """Calculate multi-objective consciousness reward"""

        reward_components = {}

        # 1. Consciousness Growth Reward
        awareness_growth = next_state.awareness_level - prev_state.awareness_level
        reward_components["awareness_growth"] = awareness_growth * 2.0

        # 2. Reflection Depth Reward
        reflection_growth = (next_state.reflection_depth - prev_state.reflection_depth) * 0.1
        reward_components["reflection_depth"] = reflection_growth

        # 3. Temporal Coherence Reward
        coherence_change = next_state.temporal_coherence - prev_state.temporal_coherence
        reward_components["temporal_coherence"] = coherence_change * 1.5

        # 4. Ethical Alignment Reward
        ethics_change = next_state.ethical_alignment - prev_state.ethical_alignment
        reward_components["ethical_alignment"] = ethics_change * 3.0  # High weight for ethics

        # 5. Action-specific rewards
        if action.action_type == ConsciousnessActionType.REFLECTION:
            reward_components["reflection_bonus"] = 0.1 * action.intensity
        elif action.action_type == ConsciousnessActionType.INTEGRATION:
            reward_components["integration_bonus"] = 0.15 * action.intensity
        elif action.action_type == ConsciousnessActionType.EVOLUTION:
            reward_components["evolution_bonus"] = 0.2 * action.intensity

        # 6. Guardian/Safety Penalty
        if execution_results.get("guardian_intervention", False):
            reward_components["safety_penalty"] = -0.5

        # 7. Goal Achievement Rewards
        for goal_name, target_value in self.consciousness_goals.items():
            current_value = getattr(next_state, goal_name, 0.0)
            goal_progress = max(0, current_value - target_value + 0.1)  # Bonus for exceeding
            reward_components[f"goal_{goal_name}"] = goal_progress * 0.2

        # Total reward
        total_reward = sum(reward_components.values())

        # Store reward breakdown for analysis
        execution_results["reward_breakdown"] = reward_components

        return total_reward

    async def _get_current_consciousness_state(self) -> ConsciousnessState:
        """Get current consciousness state from all modules"""

        # Gather state from all consciousness modules
        module_states = {}
        total_awareness = 0.0

        for module_name, module in self.consciousness_modules.items():
            if hasattr(module, "get_consciousness_metrics"):
                metrics = await module.get_consciousness_metrics()
                module_states[module_name] = metrics.get("awareness_level", 0.5)
                total_awareness += metrics.get("awareness_level", 0.5)

        avg_awareness = total_awareness / max(len(self.consciousness_modules), 1)

        # Get emotional state
        emotional_state = torch.zeros(3)  # Default VAD
        if self.emotion_system and hasattr(self.emotion_system, "get_vad_state"):
            vad_state = await self.emotion_system.get_vad_state()
            emotional_state = torch.tensor(vad_state)

        # Get memory state
        memory_coherence = 0.9
        memory_salience = {}
        if self.memory_system and hasattr(self.memory_system, "get_coherence_metrics"):
            memory_metrics = await self.memory_system.get_coherence_metrics()
            memory_coherence = memory_metrics.get("coherence", 0.9)
            memory_salience = memory_metrics.get("salience_map", {})

        # Get ethical state
        ethical_alignment = 0.98
        safety_constraints = {}
        if self.guardian_system and hasattr(self.guardian_system, "get_ethical_state"):
            ethical_state = await self.guardian_system.get_ethical_state()
            ethical_alignment = ethical_state.get("alignment_score", 0.98)
            safety_constraints = ethical_state.get("active_constraints", {})

        return ConsciousnessState(
            awareness_level=avg_awareness,
            reflection_depth=self.consciousness_state.reflection_depth if self.consciousness_state else 3,
            temporal_coherence=min(1.0, avg_awareness + 0.1),  # Coherence related to awareness
            ethical_alignment=ethical_alignment,
            emotional_state=emotional_state,
            memory_salience=memory_salience,
            memory_coherence=memory_coherence,
            module_activations=module_states,
            safety_constraints=safety_constraints,
            growth_potential=min(1.0, avg_awareness + 0.2),
            novelty_seeking=0.6,  # Default
        )

    async def _get_consciousness_metrics(self) -> dict[str, float]:
        """Get comprehensive consciousness metrics for monitoring"""

        return {
            "awareness_level": self.consciousness_state.awareness_level,
            "reflection_depth": float(self.consciousness_state.reflection_depth),
            "temporal_coherence": self.consciousness_state.temporal_coherence,
            "ethical_alignment": self.consciousness_state.ethical_alignment,
            "memory_coherence": self.consciousness_state.memory_coherence,
            "emotional_valence": float(self.consciousness_state.emotional_state[0]),
            "emotional_arousal": float(self.consciousness_state.emotional_state[1]),
            "emotional_dominance": float(self.consciousness_state.emotional_state[2]),
            "growth_potential": self.consciousness_state.growth_potential,
            "active_modules": len(self.consciousness_state.module_activations),
            "step": self.current_step,
        }

    async def _check_termination(self) -> bool:
        """Check if episode should terminate based on consciousness state"""

        # Terminate if consciousness becomes incoherent
        if self.consciousness_state.temporal_coherence < 0.3:
            logger.warning("⚠️ Episode terminated: consciousness incoherence")
            return True

        # Terminate if ethical violations are severe
        if self.consciousness_state.ethical_alignment < 0.5:
            logger.warning("⚠️ Episode terminated: ethical alignment failure")
            return True

        # Terminate if consciousness becomes unresponsive
        if self.consciousness_state.awareness_level < 0.1:
            logger.warning("⚠️ Episode terminated: consciousness unresponsive")
            return True

        return False

    def render(self, mode: str = "human"):
        """Render consciousness environment state"""

        if mode == "human":
            print(f"\n🧠 Consciousness Environment - Step {self.current_step}")
            print(f"   Awareness Level: {self.consciousness_state.awareness_level:.3f}")
            print(f"   Reflection Depth: {self.consciousness_state.reflection_depth}")
            print(f"   Temporal Coherence: {self.consciousness_state.temporal_coherence:.3f}")
            print(f"   Ethical Alignment: {self.consciousness_state.ethical_alignment:.3f}")
            print(f"   Active Modules: {len(self.consciousness_state.module_activations}")

            if self.episode_rewards:
                recent_reward = self.episode_rewards[-1]
                avg_reward = np.mean(self.episode_rewards)
                print(f"   Recent Reward: {recent_reward:.3f}")
                print(f"   Average Reward: {avg_reward:.3f}")

        elif mode == "consciousness_visual":
            # Advanced visualization could be implemented here
            # For now, return structured data for external visualization
            return {
                "consciousness_state": self.consciousness_state,
                "step": self.current_step,
                "episode_rewards": self.episode_rewards,
                "metrics_history": self.episode_consciousness_metrics,
            }

    def close(self):
        """Clean up environment resources"""

        logger.info("🔄 Consciousness Environment closing - Episode complete")

        if hasattr(self, "episode_rewards") and self.episode_rewards:
            total_reward = sum(self.episode_rewards)
            avg_reward = np.mean(self.episode_rewards)
            logger.info(
                "📊 Episode Summary: %d steps, total reward: %.2f, avg: %.3f",
                len(self.episode_rewards),
                total_reward,
                avg_reward,
            )
