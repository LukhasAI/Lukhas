"""
══════════════════════════════════════════════════════════════════════════════════
║ 🎯 LUKHAS AI - ADAPTIVE THRESHOLD COLONY
║ Dynamic threshold management for bio-symbolic coherence
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: adaptive_threshold_colony.py
║ Path: bio/symbolic/adaptive_threshold_colony.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS Bio-Symbolic Team | Claude Code
╚══════════════════════════════════════════════════════════════════════════════════
"""
import json
import logging
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import numpy as np

from lukhas.core.colonies.base_colony import BaseColony
from lukhas.core.symbolism.tags import TagPermission, TagScope

logger = logging.getLogger("ΛTRACE.bio.threshold", timezone)


class AdaptiveThresholdColony(BaseColony):
    """
    Dynamic threshold management with methylation model integration.
    Implements context-aware thresholds that adapt based on conditions.
    """

    def __init__(self, colony_id: str = "adaptive_threshold_colony"):
        super().__init__(
            colony_id,
            capabilities=[
                "threshold_adaptation",
                "context_analysis",
                "colony_consensus",
            ],
        )

        # Multi-tier threshold architecture
        self.thresholds = {
            # Tier 1: Individual signal thresholds
            "tier1_signals": {
                "heart_rate": {"low": 0.3, "high": 0.7, "critical": 0.9},
                "temperature": {"low": 0.2, "high": 0.8, "critical": 0.95},
                "energy_level": {"low": 0.4, "high": 0.8, "critical": 0.95},
                "cortisol": {"low": 0.3, "high": 0.6, "critical": 0.8},
                "ph": {"low": 0.1, "high": 0.9, "critical": 0.98},
            },
            # Tier 2: Combined state thresholds
            "tier2_combined": {
                "stress_state": {"low": 0.4, "high": 0.7, "critical": 0.85},
                "energy_state": {"low": 0.35, "high": 0.75, "critical": 0.9},
                "homeostatic": {"low": 0.2, "high": 0.8, "critical": 0.95},
            },
            # Tier 3: Holistic consciousness thresholds
            "tier3_holistic": {
                "coherence": {"low": 0.5, "high": 0.7, "critical": 0.85},
                "consciousness": {"low": 0.4, "high": 0.75, "critical": 0.9},
            },
            # Tier 4: Quantum coherence thresholds
            "tier4_quantum": {
                "entanglement": {"low": 0.6, "high": 0.8, "critical": 0.95},
                "superposition": {"low": 0.5, "high": 0.85, "critical": 0.98},
            },
        }

        # Context factors for threshold adjustment
        self.context_modifiers = {
            "circadian": self._calculate_circadian_modifier,
            "stress_history": self._calculate_stress_modifier,
            "colony_consensus": self._calculate_colony_modifier,
            "methylation": self._calculate_methylation_modifier,
            "user_calibration": self._calculate_user_modifier,
        }

        # Learning parameters (for PPO-based optimization)
        self.learning_config = {
            "learning_rate": 0.001,
            "discount_factor": 0.99,
            "experience_buffer": deque(maxlen=1000),
            "update_frequency": 100,
            "exploration_rate": 0.1,
        }

        # Stress history tracking
        self.stress_history = deque(maxlen=60)  # 1 hour at 1-minute intervals

        # Colony consensus cache
        self.colony_consensus_cache = {}
        self.consensus_ttl = timedelta(seconds=30)

        # User-specific calibration
        self.user_calibration = self._load_user_calibration()

        # A/B testing framework
        self.ab_tests = {}

        logger.info(f"🎯 AdaptiveThresholdColony '{colony_id}' initialized")

    async def execute_task(self, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate dynamic thresholds based on context.

        Args:
            task_id: Unique task identifier
            task_data: Contains bio_data and context information

        Returns:
            Adapted thresholds for current context
        """
        with self.tracer.trace_operation("calculate_adaptive_thresholds") as span:
            self.tracer.add_tag(span, "task_id", task_id)

            # Extract context
            bio_data = task_data.get("bio_data", {})
            context = task_data.get("context", {})

            # Calculate base thresholds
            base_thresholds = self._get_base_thresholds(bio_data)

            # Apply context modifiers
            adapted_thresholds = await self._apply_context_modifiers(base_thresholds, context, bio_data)

            # Check for A/B test overrides
            if self.ab_tests:
                adapted_thresholds = self._apply_ab_tests(adapted_thresholds)

            # Learn from feedback if available
            if "feedback" in task_data:
                await self._update_from_feedback(task_data["feedback"], adapted_thresholds, context)

            # Calculate confidence in thresholds
            confidence = self._calculate_threshold_confidence(adapted_thresholds, context)

            # Apply methylation-based persistence
            adapted_thresholds = self._apply_methylation(adapted_thresholds, confidence)

            # Prepare result
            result = {
                "task_id": task_id,
                "thresholds": adapted_thresholds,
                "confidence": confidence,
                "context_modifiers": await self._get_modifier_values(context, bio_data),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "colony_id": self.colony_id,
            }

            # Tag threshold quality
            self._tag_threshold_quality(confidence)

            return result

    def _get_base_thresholds(self, bio_data: dict[str, Any]) -> dict[str, dict[str, float]]:
        """Get base thresholds for given bio data types."""
        base = {}

        # Tier 1: Individual signals
        tier1 = {}
        for signal in bio_data:
            if signal in self.thresholds["tier1_signals"]:
                tier1[signal] = self.thresholds["tier1_signals"][signal].copy()
        base["tier1"] = tier1

        # Tier 2: Combined states (if relevant data present)
        tier2 = {}
        if "cortisol" in bio_data or "heart_rate" in bio_data:
            tier2["stress_state"] = self.thresholds["tier2_combined"]["stress_state"].copy()
        if "energy_level" in bio_data or "atp_level" in bio_data:
            tier2["energy_state"] = self.thresholds["tier2_combined"]["energy_state"].copy()
        if "temperature" in bio_data and "ph" in bio_data:
            tier2["homeostatic"] = self.thresholds["tier2_combined"]["homeostatic"].copy()
        base["tier2"] = tier2

        # Tier 3 & 4: Always include for holistic processing
        base["tier3"] = self.thresholds["tier3_holistic"].copy()
        base["tier4"] = self.thresholds["tier4_quantum"].copy()

        return base

    async def _apply_context_modifiers(
        self,
        base_thresholds: dict[str, dict[str, float]],
        context: dict[str, Any],
        bio_data: dict[str, Any],
    ) -> dict[str, dict[str, float]]:
        """Apply all context modifiers to thresholds."""
        modified = {}

        # Get all modifier values
        modifiers = await self._get_modifier_values(context, bio_data)

        # Apply modifiers to each tier
        for tier_name, tier_thresholds in base_thresholds.items():
            modified[tier_name] = {}

            for threshold_name, threshold_values in tier_thresholds.items():
                modified[tier_name][threshold_name] = {}

                for level, value in threshold_values.items():
                    # Apply composite modifier
                    composite_modifier = np.prod(list(modifiers.values()))

                    # Adjust threshold based on level
                    if level == "low":
                        # Lower thresholds become more sensitive
                        modified_value = value * (2 - composite_modifier)
                    elif level == "high":
                        # Higher thresholds become less sensitive
                        modified_value = value * composite_modifier
                    else:  # critical
                        # Critical thresholds are more stable
                        modified_value = value * (0.5 + 0.5 * composite_modifier)

                    # Clamp to valid range
                    modified[tier_name][threshold_name][level] = np.clip(modified_value, 0.01, 0.99)

        return modified

    async def _get_modifier_values(self, context: dict[str, Any], bio_data: dict[str, Any]) -> dict[str, float]:
        """Calculate all context modifier values."""
        modifiers = {}

        for name, calc_func in self.context_modifiers.items():
            if name == "colony_consensus":
                modifiers[name] = await calc_func(context, bio_data)
            else:
                modifiers[name] = calc_func(context, bio_data)

        return modifiers

    def _calculate_circadian_modifier(self, context: dict[str, Any], bio_data: dict[str, Any]) -> float:
        """Calculate circadian rhythm modifier."""
        current_hour = datetime.now(timezone.utc).hour

        # Simple circadian model (peak at noon, trough at midnight)
        circadian_value = 0.5 + 0.5 * np.sin((current_hour - 6) * np.pi / 12)

        # Adjust based on user's chronotype if available
        if "chronotype" in context:
            if context["chronotype"] == "morning":
                circadian_value = 0.5 + 0.5 * np.sin((current_hour - 4) * np.pi / 12)
            elif context["chronotype"] == "evening":
                circadian_value = 0.5 + 0.5 * np.sin((current_hour - 8) * np.pi / 12)

        return np.clip(circadian_value, 0.3, 1.0)

    def _calculate_stress_modifier(self, context: dict[str, Any], bio_data: dict[str, Any]) -> float:
        """Calculate stress history modifier."""
        # Add current stress to history
        if "cortisol" in bio_data:
            self.stress_history.append(bio_data["cortisol"])

        if len(self.stress_history) < 5:
            return 1.0  # Neutral modifier if insufficient history

        # Calculate stress trend
        recent_stress = list(self.stress_history)[-10:]
        stress_trend = np.mean(recent_stress)

        # High stress -> more conservative thresholds
        if stress_trend > 0.7:
            return 0.8  # More sensitive
        elif stress_trend < 0.3:
            return 1.2  # Less sensitive
        else:
            return 1.0  # Neutral

    async def _calculate_colony_modifier(self, context: dict[str, Any], bio_data: dict[str, Any]) -> float:
        """Calculate colony consensus modifier."""
        # Check cache first
        cache_key = f"{json.dumps(sorted(bio_data.items()))}"
        if cache_key in self.colony_consensus_cache:
            cached_time, cached_value = self.colony_consensus_cache[cache_key]
            if datetime.now(timezone.utc) - cached_time < self.consensus_ttl:
                return cached_value

        # Simulate colony consensus (in real implementation, query other colonies)
        # For now, return a value based on data completeness
        data_completeness = len(bio_data) / 10  # Assume 10 expected signals
        consensus_value = 0.5 + 0.5 * min(data_completeness, 1.0)

        # Cache the result
        self.colony_consensus_cache[cache_key] = (datetime.now(timezone.utc), consensus_value)

        return consensus_value

    def _calculate_methylation_modifier(self, context: dict[str, Any], bio_data: dict[str, Any]) -> float:
        """Calculate methylation-based modifier."""
        # Get methylation decay factor from model
        decay_factor = self.methylation_model.genetic_decay_factor

        # Recent high-coherence patterns get "methylated" (more persistent)
        if "coherence_history" in context:
            recent_coherence = np.mean(context["coherence_history"][-10:])
            if recent_coherence > 0.8:
                return 1.0 + (1 - decay_factor) * 0.2  # Boost stability

        return 1.0

    def _calculate_user_modifier(self, context: dict[str, Any], bio_data: dict[str, Any]) -> float:
        """Calculate user-specific calibration modifier."""
        if "user_id" in context and context["user_id"] in self.user_calibration:
            calibration = self.user_calibration[context["user_id"]]

            # Apply user's personal sensitivity settings
            return calibration.get("sensitivity", 1.0)

        return 1.0  # Default neutral

    def _calculate_threshold_confidence(
        self, thresholds: dict[str, dict[str, float]], context: dict[str, Any]
    ) -> float:
        """Calculate confidence in the adapted thresholds."""
        confidence_factors = []

        # Factor 1: Data completeness
        if "data_completeness" in context:
            confidence_factors.append(context["data_completeness"])

        # Factor 2: Historical stability
        if hasattr(self, "threshold_history"):
            # Check how stable thresholds have been
            stability = 1.0  # Placeholder
            confidence_factors.append(stability)

        # Factor 3: Colony consensus strength
        if "colony_consensus_strength" in context:
            confidence_factors.append(context["colony_consensus_strength"])

        # Factor 4: Learning convergence
        if len(self.learning_config["experience_buffer"]) > 100:
            convergence = min(len(self.learning_config["experience_buffer"]) / 500, 1.0)
            confidence_factors.append(convergence)

        return np.mean(confidence_factors) if confidence_factors else 0.7

    def _apply_methylation(
        self, thresholds: dict[str, dict[str, float]], confidence: float
    ) -> dict[str, dict[str, float]]:
        """Apply methylation-based persistence to thresholds."""
        if confidence > 0.8:
            # High confidence -> increase persistence
            self._tag_for_methylation(thresholds, confidence)

        return thresholds

    def _tag_for_methylation(self, thresholds: dict[str, Any], confidence: float):
        """Tag thresholds for methylation persistence."""
        tag_name = "ΛTHRESHOLD_METHYLATED"
        self.symbolic_carryover[tag_name] = (
            tag_name,
            TagScope.GENETIC,
            TagPermission.PROTECTED,
            confidence,
            3600.0,  # 1 hour persistence
        )

    def _tag_threshold_quality(self, confidence: float):
        """Tag threshold quality based on confidence."""
        if confidence >= 0.8:
            tag = "ΛTHRESHOLD_HIGH_CONFIDENCE"
        elif confidence >= 0.6:
            tag = "ΛTHRESHOLD_MEDIUM_CONFIDENCE"
        else:
            tag = "ΛTHRESHOLD_LOW_CONFIDENCE"

        self.symbolic_carryover[tag] = (
            tag,
            TagScope.LOCAL,
            TagPermission.PUBLIC,
            confidence,
            None,
        )

    async def _update_from_feedback(
        self,
        feedback: dict[str, Any],
        thresholds: dict[str, dict[str, float]],
        context: dict[str, Any],
    ):
        """Update thresholds based on feedback (reinforcement learning)."""
        # Store experience
        experience = {
            "state": context,
            "thresholds": thresholds,
            "reward": feedback.get("reward", 0.0),
            "timestamp": datetime.now(timezone.utc),
        }

        self.learning_config["experience_buffer"].append(experience)

        # Update if enough experiences
        if len(self.learning_config["experience_buffer"]) >= self.learning_config["update_frequency"]:
            await self._ppo_update()

    async def _ppo_update(self):
        """Proximal Policy Optimization update (simplified)."""
        # This is a placeholder for actual PPO implementation
        # In production, this would use a neural network policy

        experiences = list(self.learning_config["experience_buffer"])
        rewards = [exp["reward"] for exp in experiences]

        # Simple adaptation: adjust thresholds based on average reward
        avg_reward = np.mean(rewards)

        if avg_reward > 0.7:
            # Good performance - make minor adjustments
            adjustment = 1.02
        elif avg_reward < 0.3:
            # Poor performance - larger adjustments
            adjustment = 0.95
        else:
            adjustment = 1.0

        # Apply adjustments (simplified)
        for tier in self.thresholds.values():
            for signal_thresholds in tier.values():
                for level in signal_thresholds:
                    signal_thresholds[level] *= adjustment
                    signal_thresholds[level] = np.clip(signal_thresholds[level], 0.01, 0.99)

        logger.info(f"PPO update complete. Avg reward: {avg_reward:.3f}, Adjustment: {adjustment}")

    def _apply_ab_tests(self, thresholds: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
        """Apply A/B test overrides to thresholds."""
        # Placeholder for A/B testing framework
        # In production, this would randomly assign variants and track results
        return thresholds

    def _load_user_calibration(self) -> dict[str, dict[str, Any]]:
        """Load user-specific calibration data."""
        # In production, this would load from a database
        return {"default_user": {"sensitivity": 1.0, "chronotype": "neutral"}}


# Colony instance factory
def create_threshold_colony(colony_id: Optional[str] = None) -> AdaptiveThresholdColony:
    """Create a new adaptive threshold colony instance."""
    return AdaptiveThresholdColony(colony_id or "threshold_colony_default")