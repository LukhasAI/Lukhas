"""
Capability Matrix for Multi-Model Orchestration

Manages capability scoring and model selection based on task requirements.
Integrates with LUKHAS Constellation Framework for consciousness-aware routing.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Task classification for capability matching."""
    REASONING = "reasoning"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"
    CODE_GENERATION = "code_generation"
    MATH = "mathematical"
    SCIENTIFIC = "scientific"
    SYNTHESIS = "synthesis"
    CLASSIFICATION = "classification"

class CapabilityDimension(Enum):
    """Capability dimensions for model evaluation."""
    REASONING = "reasoning"
    CREATIVITY = "creativity"
    TECHNICAL_ACCURACY = "technical_accuracy"
    MATHEMATICAL = "mathematical"
    SCIENTIFIC = "scientific"
    LANGUAGE_QUALITY = "language_quality"
    CODE_QUALITY = "code_quality"
    SPEED = "speed"
    COST_EFFICIENCY = "cost_efficiency"
    CONSISTENCY = "consistency"

@dataclass
class CapabilityProfile:
    """Model capability profile with constellation alignment."""
    model_id: str
    capabilities: dict[CapabilityDimension, float]  # 0.0-1.0 scores
    constellation_alignment: dict[str, float]  # Alignment with 8 constellation stars
    specializations: list[TaskType]
    latency_ms: int
    cost_per_token: float
    context_window: int

    def get_capability_score(self, dimension: CapabilityDimension) -> float:
        """Get capability score for specific dimension."""
        return self.capabilities.get(dimension, 0.0)

    def get_constellation_score(self, star: str) -> float:
        """Get alignment score with constellation star."""
        return self.constellation_alignment.get(star, 0.0)

@dataclass
class TaskRequirements:
    """Task requirements for model selection."""
    task_type: TaskType
    required_capabilities: dict[CapabilityDimension, float]  # Minimum scores
    preferred_capabilities: dict[CapabilityDimension, float]  # Preferred scores
    constellation_context: Optional[dict[str, float]] = None  # Star relevance
    max_latency_ms: Optional[int] = None
    max_cost_per_token: Optional[float] = None
    min_context_window: Optional[int] = None
    priority: float = 1.0  # Task priority multiplier

class CapabilityMatrix:
    """
    Capability Matrix for AGI Multi-Model Orchestration

    Manages model capabilities and provides intelligent routing decisions
    based on task requirements and constellation framework alignment.
    """

    def __init__(self):
        self.model_profiles: dict[str, CapabilityProfile] = {}
        self.task_history: list[dict[str, Any]] = []
        self._initialize_model_profiles()

    def _initialize_model_profiles(self):
        """Initialize capability profiles for supported models."""

        # GPT-4 Turbo
        self.model_profiles["gpt-4-turbo"] = CapabilityProfile(
            model_id="gpt-4-turbo",
            capabilities={
                CapabilityDimension.REASONING: 0.92,
                CapabilityDimension.CREATIVITY: 0.88,
                CapabilityDimension.TECHNICAL_ACCURACY: 0.90,
                CapabilityDimension.MATHEMATICAL: 0.85,
                CapabilityDimension.SCIENTIFIC: 0.87,
                CapabilityDimension.LANGUAGE_QUALITY: 0.90,
                CapabilityDimension.CODE_QUALITY: 0.88,
                CapabilityDimension.SPEED: 0.80,
                CapabilityDimension.COST_EFFICIENCY: 0.70,
                CapabilityDimension.CONSISTENCY: 0.85
            },
            constellation_alignment={
                "IDENTITY": 0.85, "MEMORY": 0.80, "VISION": 0.85, "BIO": 0.75,
                "DREAM": 0.90, "ETHICS": 0.85, "GUARDIAN": 0.80, "QUANTUM": 0.85
            },
            specializations=[TaskType.REASONING, TaskType.CREATIVE, TaskType.SYNTHESIS],
            latency_ms=2000,
            cost_per_token=0.00003,
            context_window=128000
        )

        # Claude-3.5 Sonnet
        self.model_profiles["claude-3-5-sonnet"] = CapabilityProfile(
            model_id="claude-3-5-sonnet",
            capabilities={
                CapabilityDimension.REASONING: 0.95,
                CapabilityDimension.CREATIVITY: 0.92,
                CapabilityDimension.TECHNICAL_ACCURACY: 0.93,
                CapabilityDimension.MATHEMATICAL: 0.88,
                CapabilityDimension.SCIENTIFIC: 0.90,
                CapabilityDimension.LANGUAGE_QUALITY: 0.95,
                CapabilityDimension.CODE_QUALITY: 0.92,
                CapabilityDimension.SPEED: 0.75,
                CapabilityDimension.COST_EFFICIENCY: 0.65,
                CapabilityDimension.CONSISTENCY: 0.90
            },
            constellation_alignment={
                "IDENTITY": 0.90, "MEMORY": 0.85, "VISION": 0.88, "BIO": 0.80,
                "DREAM": 0.95, "ETHICS": 0.95, "GUARDIAN": 0.90, "QUANTUM": 0.88
            },
            specializations=[TaskType.REASONING, TaskType.ANALYTICAL, TaskType.TECHNICAL],
            latency_ms=2500,
            cost_per_token=0.000015,
            context_window=200000
        )

        # Gemini Pro 1.5
        self.model_profiles["gemini-1.5-pro"] = CapabilityProfile(
            model_id="gemini-1.5-pro",
            capabilities={
                CapabilityDimension.REASONING: 0.88,
                CapabilityDimension.CREATIVITY: 0.85,
                CapabilityDimension.TECHNICAL_ACCURACY: 0.87,
                CapabilityDimension.MATHEMATICAL: 0.90,
                CapabilityDimension.SCIENTIFIC: 0.92,
                CapabilityDimension.LANGUAGE_QUALITY: 0.85,
                CapabilityDimension.CODE_QUALITY: 0.85,
                CapabilityDimension.SPEED: 0.85,
                CapabilityDimension.COST_EFFICIENCY: 0.80,
                CapabilityDimension.CONSISTENCY: 0.80
            },
            constellation_alignment={
                "IDENTITY": 0.80, "MEMORY": 0.85, "VISION": 0.90, "BIO": 0.85,
                "DREAM": 0.80, "ETHICS": 0.80, "GUARDIAN": 0.75, "QUANTUM": 0.90
            },
            specializations=[TaskType.SCIENTIFIC, TaskType.MATHEMATICAL, TaskType.ANALYTICAL],
            latency_ms=1800,
            cost_per_token=0.000007,
            context_window=1000000
        )

        # GPT-3.5 Turbo (Fast/Cheap option)
        self.model_profiles["gpt-3.5-turbo"] = CapabilityProfile(
            model_id="gpt-3.5-turbo",
            capabilities={
                CapabilityDimension.REASONING: 0.75,
                CapabilityDimension.CREATIVITY: 0.80,
                CapabilityDimension.TECHNICAL_ACCURACY: 0.72,
                CapabilityDimension.MATHEMATICAL: 0.70,
                CapabilityDimension.SCIENTIFIC: 0.72,
                CapabilityDimension.LANGUAGE_QUALITY: 0.85,
                CapabilityDimension.CODE_QUALITY: 0.75,
                CapabilityDimension.SPEED: 0.95,
                CapabilityDimension.COST_EFFICIENCY: 0.95,
                CapabilityDimension.CONSISTENCY: 0.75
            },
            constellation_alignment={
                "IDENTITY": 0.70, "MEMORY": 0.65, "VISION": 0.70, "BIO": 0.65,
                "DREAM": 0.75, "ETHICS": 0.70, "GUARDIAN": 0.65, "QUANTUM": 0.70
            },
            specializations=[TaskType.CONVERSATIONAL, TaskType.CREATIVE],
            latency_ms=800,
            cost_per_token=0.000002,
            context_window=16000
        )

    def calculate_model_score(self, model_id: str, requirements: TaskRequirements) -> float:
        """
        Calculate comprehensive score for model given task requirements.

        Combines capability matching, constellation alignment, and constraints.
        """
        if model_id not in self.model_profiles:
            return 0.0

        profile = self.model_profiles[model_id]
        score = 0.0

        # 1. Required capabilities (must meet minimum)
        required_met = True
        for capability, min_score in requirements.required_capabilities.items():
            model_score = profile.get_capability_score(capability)
            if model_score < min_score:
                required_met = False
                break

        if not required_met:
            return 0.0  # Hard constraint violation

        # 2. Preferred capabilities scoring (40% weight)
        capability_score = 0.0
        if requirements.preferred_capabilities:
            total_weight = 0.0
            for capability, preferred_score in requirements.preferred_capabilities.items():
                model_score = profile.get_capability_score(capability)
                weight = preferred_score  # Use preferred score as weight
                capability_score += model_score * weight
                total_weight += weight

            if total_weight > 0:
                capability_score /= total_weight

        score += capability_score * 0.4

        # 3. Constellation alignment (30% weight)
        constellation_score = 0.0
        if requirements.constellation_context:
            total_relevance = 0.0
            for star, relevance in requirements.constellation_context.items():
                alignment = profile.get_constellation_score(star)
                constellation_score += alignment * relevance
                total_relevance += relevance

            if total_relevance > 0:
                constellation_score /= total_relevance
        else:
            # Default constellation weighting
            constellation_score = sum(profile.constellation_alignment.values()) / len(profile.constellation_alignment)

        score += constellation_score * 0.3

        # 4. Specialization bonus (15% weight)
        specialization_score = 1.0 if requirements.task_type in profile.specializations else 0.7
        score += specialization_score * 0.15

        # 5. Performance constraints (15% weight)
        constraint_score = 1.0

        # Latency constraint
        if requirements.max_latency_ms and profile.latency_ms > requirements.max_latency_ms:
            constraint_score *= 0.5

        # Cost constraint
        if requirements.max_cost_per_token and profile.cost_per_token > requirements.max_cost_per_token:
            constraint_score *= 0.5

        # Context window constraint
        if requirements.min_context_window and profile.context_window < requirements.min_context_window:
            constraint_score *= 0.3

        score += constraint_score * 0.15

        # Apply priority multiplier
        score *= requirements.priority

        return min(score, 1.0)  # Cap at 1.0

    def rank_models(self, requirements: TaskRequirements) -> list[tuple[str, float]]:
        """
        Rank all models by their suitability for the task.

        Returns list of (model_id, score) tuples sorted by score descending.
        """
        scores = []
        for model_id in self.model_profiles:
            score = self.calculate_model_score(model_id, requirements)
            if score > 0.0:  # Only include viable models
                scores.append((model_id, score))

        return sorted(scores, key=lambda x: x[1], reverse=True)

    def select_optimal_model(self, requirements: TaskRequirements) -> Optional[str]:
        """Select the optimal model for given requirements."""
        rankings = self.rank_models(requirements)
        return rankings[0][0] if rankings else None

    def get_model_capabilities(self, model_id: str) -> Optional[CapabilityProfile]:
        """Get capability profile for specific model."""
        return self.model_profiles.get(model_id)

    def add_task_result(self, model_id: str, task_type: TaskType,
                       success: bool, latency_ms: int, quality_score: float):
        """Record task execution result for learning."""
        self.task_history.append({
            "model_id": model_id,
            "task_type": task_type,
            "success": success,
            "latency_ms": latency_ms,
            "quality_score": quality_score,
            "timestamp": asyncio.get_event_loop().time()
        })

        # Keep only recent history (last 1000 tasks)
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-1000:]

    def get_model_performance_stats(self, model_id: str,
                                  task_type: Optional[TaskType] = None) -> dict[str, float]:
        """Get performance statistics for model."""
        relevant_tasks = [
            task for task in self.task_history
            if task["model_id"] == model_id and (
                task_type is None or task["task_type"] == task_type
            )
        ]

        if not relevant_tasks:
            return {}

        success_rate = sum(1 for task in relevant_tasks if task["success"]) / len(relevant_tasks)
        avg_latency = sum(task["latency_ms"] for task in relevant_tasks) / len(relevant_tasks)
        avg_quality = sum(task["quality_score"] for task in relevant_tasks) / len(relevant_tasks)

        return {
            "success_rate": success_rate,
            "average_latency_ms": avg_latency,
            "average_quality": avg_quality,
            "task_count": len(relevant_tasks)
        }

    async def update_model_profile(self, model_id: str, performance_data: dict[str, float]):
        """Update model profile based on performance data."""
        if model_id not in self.model_profiles:
            return

        profile = self.model_profiles[model_id]

        # Adaptive learning: adjust capabilities based on actual performance
        learning_rate = 0.1

        if "success_rate" in performance_data:
            # Adjust consistency based on success rate
            current_consistency = profile.capabilities[CapabilityDimension.CONSISTENCY]
            observed_consistency = performance_data["success_rate"]
            new_consistency = current_consistency + learning_rate * (observed_consistency - current_consistency)
            profile.capabilities[CapabilityDimension.CONSISTENCY] = max(0.0, min(1.0, new_consistency))

        if "average_latency_ms" in performance_data:
            # Update latency estimate
            profile.latency_ms = int(0.8 * profile.latency_ms + 0.2 * performance_data["average_latency_ms"])

        logger.info(f"Updated capability profile for {model_id}")
