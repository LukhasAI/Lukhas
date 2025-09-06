"""
Cost Optimizer for Multi-Model Orchestration

Optimizes model selection and usage patterns for cost efficiency while
maintaining quality thresholds. Integrates with LUKHAS Guardian system
for ethical cost management.
"""

import logging
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__, timezone)


class CostTier(Enum):
    """Cost tier classification for model usage."""

    PREMIUM = "premium"  # High-capability, high-cost models
    STANDARD = "standard"  # Balanced cost/capability models
    ECONOMY = "economy"  # Fast, low-cost models
    BULK = "bulk"  # Very low cost for simple tasks


class OptimizationStrategy(Enum):
    """Cost optimization strategies."""

    MINIMIZE_COST = "minimize_cost"
    BALANCE_COST_QUALITY = "balance_cost_quality"
    MAXIMIZE_QUALITY = "maximize_quality"
    ADAPTIVE = "adaptive"


@dataclass
class CostProfile:
    """Model cost profile with usage patterns."""

    model_id: str
    cost_tier: CostTier
    cost_per_input_token: float
    cost_per_output_token: float
    avg_input_tokens: int
    avg_output_tokens: int
    typical_cost_per_request: float
    quality_cost_ratio: float  # Quality score per dollar

    def calculate_request_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for specific token counts."""
        return input_tokens * self.cost_per_input_token + output_tokens * self.cost_per_output_token


@dataclass
class CostConstraints:
    """Cost constraints for optimization."""

    max_cost_per_request: Optional[float] = None
    max_cost_per_hour: Optional[float] = None
    max_cost_per_day: Optional[float] = None
    budget_priority: float = 1.0  # Higher = more cost-conscious
    quality_threshold: float = 0.7  # Minimum acceptable quality
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCE_COST_QUALITY


@dataclass
class UsageStats:
    """Usage statistics for cost tracking."""

    requests_count: int
    total_cost: float
    total_input_tokens: int
    total_output_tokens: int
    avg_quality_score: float
    time_period: timedelta


class CostOptimizer:
    """
    Cost Optimizer for AGI Multi-Model Orchestration

    Provides intelligent cost optimization for model selection while
    maintaining quality standards and respecting Guardian system constraints.
    """

    def __init__(self):
        self.cost_profiles: dict[str, CostProfile] = {}
        self.usage_history: list[dict[str, Any]] = []
        self.current_usage: dict[str, float] = {"hour": 0.0, "day": 0.0}
        self.last_reset = {"hour": datetime.now(timezone.utc), "day": datetime.now(timezone.utc).replace(hour=0, minute=0)}
        self._initialize_cost_profiles()

    def _initialize_cost_profiles(self):
        """Initialize cost profiles for supported models."""

        # GPT-4 Turbo (Premium tier)
        self.cost_profiles["gpt-4-turbo"] = CostProfile(
            model_id="gpt-4-turbo",
            cost_tier=CostTier.PREMIUM,
            cost_per_input_token=0.00001,
            cost_per_output_token=0.00003,
            avg_input_tokens=2000,
            avg_output_tokens=800,
            typical_cost_per_request=0.044,
            quality_cost_ratio=20.5,  # Quality/cost efficiency
        )

        # Claude-3.5 Sonnet (Premium tier)
        self.cost_profiles["claude-3-5-sonnet"] = CostProfile(
            model_id="claude-3-5-sonnet",
            cost_tier=CostTier.PREMIUM,
            cost_per_input_token=0.000003,
            cost_per_output_token=0.000015,
            avg_input_tokens=2000,
            avg_output_tokens=800,
            typical_cost_per_request=0.018,
            quality_cost_ratio=52.8,  # Excellent quality/cost ratio
        )

        # Gemini Pro 1.5 (Standard tier)
        self.cost_profiles["gemini-1.5-pro"] = CostProfile(
            model_id="gemini-1.5-pro",
            cost_tier=CostTier.STANDARD,
            cost_per_input_token=0.0000035,
            cost_per_output_token=0.0000105,
            avg_input_tokens=2000,
            avg_output_tokens=800,
            typical_cost_per_request=0.0154,
            quality_cost_ratio=57.1,  # Best cost efficiency
        )

        # GPT-3.5 Turbo (Economy tier)
        self.cost_profiles["gpt-3.5-turbo"] = CostProfile(
            model_id="gpt-3.5-turbo",
            cost_tier=CostTier.ECONOMY,
            cost_per_input_token=0.0000005,
            cost_per_output_token=0.0000015,
            avg_input_tokens=1500,
            avg_output_tokens=600,
            typical_cost_per_request=0.00165,
            quality_cost_ratio=45.5,  # Good for simple tasks
        )

        # Claude-3 Haiku (Bulk tier)
        self.cost_profiles["claude-3-haiku"] = CostProfile(
            model_id="claude-3-haiku",
            cost_tier=CostTier.BULK,
            cost_per_input_token=0.00000025,
            cost_per_output_token=0.00000125,
            avg_input_tokens=1200,
            avg_output_tokens=400,
            typical_cost_per_request=0.0008,
            quality_cost_ratio=62.5,  # Excellent for bulk tasks
        )

    def _update_usage_tracking(self):
        """Update usage tracking with time-based resets."""
        now = datetime.now(timezone.utc)

        # Reset hourly usage
        if now - self.last_reset["hour"] >= timedelta(hours=1):
            self.current_usage["hour"] = 0.0
            self.last_reset["hour"] = now

        # Reset daily usage
        if now.date() != self.last_reset["day"].date():
            self.current_usage["day"] = 0.0
            self.last_reset["day"] = now.replace(hour=0, minute=0)

    def check_cost_constraints(self, estimated_cost: float, constraints: CostConstraints) -> bool:
        """Check if estimated cost violates constraints."""
        self._update_usage_tracking()

        # Per-request constraint
        if constraints.max_cost_per_request and estimated_cost > constraints.max_cost_per_request:
            return False

        # Hourly constraint
        if constraints.max_cost_per_hour:
            if self.current_usage["hour"] + estimated_cost > constraints.max_cost_per_hour:
                return False

        # Daily constraint
        if constraints.max_cost_per_day:
            if self.current_usage["day"] + estimated_cost > constraints.max_cost_per_day:
                return False

        return True

    def calculate_cost_efficiency_score(self, model_id: str, quality_score: float) -> float:
        """Calculate cost efficiency score for model."""
        if model_id not in self.cost_profiles:
            return 0.0

        profile = self.cost_profiles[model_id]

        # Cost efficiency = quality per dollar spent
        if profile.typical_cost_per_request > 0:
            return quality_score / profile.typical_cost_per_request

        return 0.0

    def optimize_model_selection(
        self, candidate_models: list[tuple[str, float]], constraints: CostConstraints
    ) -> list[tuple[str, float, float]]:
        """
        Optimize model selection based on cost constraints and strategy.

        Args:
            candidate_models: List of (model_id, quality_score) tuples
            constraints: Cost constraints and optimization strategy

        Returns:
            List of (model_id, quality_score, cost_efficiency) tuples sorted by optimization strategy
        """
        optimized_candidates = []

        for model_id, quality_score in candidate_models:
            if model_id not in self.cost_profiles:
                continue

            profile = self.cost_profiles[model_id]

            # Check quality threshold
            if quality_score < constraints.quality_threshold:
                continue

            # Estimate cost
            estimated_cost = profile.typical_cost_per_request

            # Check cost constraints
            if not self.check_cost_constraints(estimated_cost, constraints):
                continue

            # Calculate cost efficiency
            cost_efficiency = self.calculate_cost_efficiency_score(model_id, quality_score)

            optimized_candidates.append((model_id, quality_score, cost_efficiency))

        # Sort by optimization strategy
        if constraints.strategy == OptimizationStrategy.MINIMIZE_COST:
            # Sort by lowest cost (highest efficiency for given quality)
            optimized_candidates.sort(key=lambda x: -x[2])  # Higher efficiency = lower cost

        elif constraints.strategy == OptimizationStrategy.MAXIMIZE_QUALITY:
            # Sort by highest quality
            optimized_candidates.sort(key=lambda x: -x[1])

        elif constraints.strategy == OptimizationStrategy.BALANCE_COST_QUALITY:
            # Sort by balanced score: quality * cost_efficiency * budget_priority
            def balanced_score(candidate):
                model_id, quality, efficiency = candidate
                return quality * efficiency * constraints.budget_priority

            optimized_candidates.sort(key=balanced_score, reverse=True)

        elif constraints.strategy == OptimizationStrategy.ADAPTIVE:
            # Adaptive strategy based on current usage
            self._update_usage_tracking()

            # If usage is high, prioritize cost efficiency
            daily_usage_ratio = 0.0
            if constraints.max_cost_per_day:
                daily_usage_ratio = self.current_usage["day"] / constraints.max_cost_per_day

            if daily_usage_ratio > 0.7:  # High usage - prioritize cost
                optimized_candidates.sort(key=lambda x: -x[2])
            else:  # Normal usage - balance quality and cost

                def adaptive_score(candidate):
                    model_id, quality, efficiency = candidate
                    cost_weight = min(1.0, daily_usage_ratio * 2)  # Increase cost importance
                    quality_weight = 1.0 - cost_weight
                    return quality * quality_weight + efficiency * cost_weight

                optimized_candidates.sort(key=adaptive_score, reverse=True)

        return optimized_candidates

    def select_cost_optimal_model(
        self, candidate_models: list[tuple[str, float]], constraints: CostConstraints
    ) -> Optional[str]:
        """Select the most cost-optimal model from candidates."""
        optimized = self.optimize_model_selection(candidate_models, constraints)
        return optimized[0][0] if optimized else None

    def record_usage(self, model_id: str, input_tokens: int, output_tokens: int, quality_score: float):
        """Record model usage for cost tracking and optimization."""
        if model_id not in self.cost_profiles:
            return

        profile = self.cost_profiles[model_id]
        cost = profile.calculate_request_cost(input_tokens, output_tokens)

        # Update current usage
        self._update_usage_tracking()
        self.current_usage["hour"] += cost
        self.current_usage["day"] += cost

        # Record in history
        usage_record = {
            "timestamp": datetime.now(timezone.utc),
            "model_id": model_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "quality_score": quality_score,
        }

        self.usage_history.append(usage_record)

        # Keep only recent history (last 10,000 requests)
        if len(self.usage_history) > 10000:
            self.usage_history = self.usage_history[-10000:]

        logger.info(f"Recorded usage: {model_id} - ${cost:.4f} (Q:{quality_score:.2f})")

    def get_usage_statistics(self, time_period: Optional[timedelta] = None) -> UsageStats:
        """Get usage statistics for specified time period."""
        cutoff_time = datetime.now(timezone.utc)
        if time_period:
            cutoff_time -= time_period
        else:
            time_period = timedelta(days=1)  # Default to last day

        relevant_usage = [record for record in self.usage_history if record["timestamp"] >= cutoff_time]

        if not relevant_usage:
            return UsageStats(0, 0.0, 0, 0, 0.0, time_period)

        total_cost = sum(record["cost"] for record in relevant_usage)
        total_input_tokens = sum(record["input_tokens"] for record in relevant_usage)
        total_output_tokens = sum(record["output_tokens"] for record in relevant_usage)
        avg_quality = statistics.mean(record["quality_score"] for record in relevant_usage)

        return UsageStats(
            requests_count=len(relevant_usage),
            total_cost=total_cost,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            avg_quality_score=avg_quality,
            time_period=time_period,
        )

    def get_model_cost_analysis(self, model_id: str, time_period: Optional[timedelta] = None) -> dict[str, Any]:
        """Get detailed cost analysis for specific model."""
        cutoff_time = datetime.now(timezone.utc)
        if time_period:
            cutoff_time -= time_period

        model_usage = [
            record
            for record in self.usage_history
            if record["model_id"] == model_id and record["timestamp"] >= cutoff_time
        ]

        if not model_usage:
            return {"model_id": model_id, "usage_count": 0}

        costs = [record["cost"] for record in model_usage]
        qualities = [record["quality_score"] for record in model_usage]

        return {
            "model_id": model_id,
            "usage_count": len(model_usage),
            "total_cost": sum(costs),
            "average_cost": statistics.mean(costs),
            "cost_std_dev": statistics.stdev(costs) if len(costs) > 1 else 0.0,
            "average_quality": statistics.mean(qualities),
            "cost_efficiency": statistics.mean(qualities) / statistics.mean(costs),
            "total_tokens": sum(r["input_tokens"] + r["output_tokens"] for r in model_usage),
        }

    def recommend_cost_optimization(self, current_usage: UsageStats, constraints: CostConstraints) -> dict[str, Any]:
        """Provide cost optimization recommendations."""
        recommendations = {
            "current_efficiency": (
                current_usage.avg_quality_score / current_usage.total_cost if current_usage.total_cost > 0 else 0
            ),
            "suggestions": [],
        }

        # Analyze usage patterns
        if current_usage.total_cost > 0:
            cost_per_request = current_usage.total_cost / current_usage.requests_count

            # High cost per request
            if cost_per_request > 0.02:
                recommendations["suggestions"].append(
                    {
                        "type": "high_cost_per_request",
                        "message": f"Average cost per request (${cost_per_request:.4f}) is high. Consider using economy tier models for simpler tasks.",
                        "priority": "medium",
                    }
                )

            # Low quality for cost
            if current_usage.avg_quality_score < 0.8 and cost_per_request > 0.01:
                recommendations["suggestions"].append(
                    {
                        "type": "poor_quality_cost_ratio",
                        "message": "Quality/cost ratio is suboptimal. Review model selection strategy.",
                        "priority": "high",
                    }
                )

            # Budget utilization
            if constraints.max_cost_per_day:
                daily_usage = self.current_usage["day"]
                utilization = daily_usage / constraints.max_cost_per_day

                if utilization > 0.8:
                    recommendations["suggestions"].append(
                        {
                            "type": "high_budget_utilization",
                            "message": f"Daily budget {utilization*100:.1f}% utilized. Consider switching to economy models.",
                            "priority": "high",
                        }
                    )
                elif utilization < 0.3:
                    recommendations["suggestions"].append(
                        {
                            "type": "low_budget_utilization",
                            "message": f"Daily budget only {utilization*100:.1f}% utilized. Could use premium models for better quality.",
                            "priority": "low",
                        }
                    )

        return recommendations

    def get_cost_tier_distribution(self) -> dict[CostTier, float]:
        """Get distribution of usage across cost tiers."""
        tier_costs = {tier: 0.0 for tier in CostTier}

        for record in self.usage_history[-1000:]:  # Last 1000 requests
            model_id = record["model_id"]
            if model_id in self.cost_profiles:
                tier = self.cost_profiles[model_id].cost_tier
                tier_costs[tier] += record["cost"]

        total_cost = sum(tier_costs.values())
        if total_cost > 0:
            return {tier: cost / total_cost for tier, cost in tier_costs.items()}

        return tier_costs
