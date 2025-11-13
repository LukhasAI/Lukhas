"""
Tool learning capabilities for LUKHAS Cognitive AI.

This module provides adaptive tool learning functionality that enables the system
to learn how to use tools more effectively and discover optimal tool combinations.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ToolLearningStrategy(Enum):
    """Tool learning strategy types."""

    REINFORCEMENT = "reinforcement"
    IMITATION = "imitation"
    EXPLORATION = "exploration"
    ADAPTIVE = "adaptive"
    COLLABORATIVE = "collaborative"


class ToolUsagePattern(Enum):
    """Common tool usage patterns."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ITERATIVE = "iterative"
    HIERARCHICAL = "hierarchical"


@dataclass
class ToolPerformanceMetric:
    """Performance metrics for tool usage."""

    tool_name: str
    success_rate: float
    average_execution_time: float
    error_rate: float
    user_satisfaction: float
    efficiency_score: float
    context_adaptability: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolLearningContext:
    """Context for tool learning operations."""

    task_description: str
    available_tools: list[str]
    success_criteria: dict[str, Any]
    environment_constraints: dict[str, Any] = field(default_factory=dict)
    user_preferences: dict[str, Any] = field(default_factory=dict)
    historical_performance: list[ToolPerformanceMetric] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolRecommendation:
    """Recommendation for tool usage."""

    recommended_tools: list[str]
    usage_pattern: ToolUsagePattern
    confidence: float
    reasoning: str
    expected_performance: dict[str, float]
    alternative_approaches: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolLearningResult:
    """Result of tool learning operation."""

    learning_id: str
    context: ToolLearningContext
    recommendation: ToolRecommendation
    actual_performance: Optional[ToolPerformanceMetric] = None
    learning_insights: list[str] = field(default_factory=list)
    adaptation_applied: bool = False
    success: bool = True
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolExperience:
    """Experience data from tool usage for learning."""

    experience_id: str
    tool_name: str
    context_description: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    execution_time: float
    success: bool
    user_feedback: Optional[str] = None
    error_details: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolMastery:
    """Tool mastery level tracking."""

    tool_name: str
    mastery_level: float  # 0.0 to 1.0
    usage_count: int
    success_rate: float
    average_efficiency: float
    learning_progress: list[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ToolLearner:
    """Adaptive tool learning engine for LUKHAS."""

    def __init__(self, strategy: ToolLearningStrategy = ToolLearningStrategy.ADAPTIVE):
        self.strategy = strategy
        self.tool_performance_history: dict[str, list[ToolPerformanceMetric]] = {}
        self.usage_patterns: dict[str, list[ToolUsagePattern]] = {}
        self.learning_experiences: list[ToolLearningResult] = []
        self.tool_compatibility_matrix: dict[tuple[str, str], float] = {}

        logger.info(f"ToolLearner initialized with strategy: {strategy.value}")

    async def learn_tool_usage(self, context: ToolLearningContext) -> ToolLearningResult:
        """Learn optimal tool usage for a given context."""

        learning_id = f"tool_learn_{int(datetime.now(timezone.utc).timestamp() * 1000)}"

        try:
            # Analyze historical performance
            historical_insights = await self._analyze_historical_performance(context)

            # Generate tool recommendation
            recommendation = await self._generate_recommendation(context, historical_insights)

            # Learn from the recommendation process
            learning_insights = await self._extract_learning_insights(context, recommendation)

            result = ToolLearningResult(
                learning_id=learning_id,
                context=context,
                recommendation=recommendation,
                learning_insights=learning_insights,
                success=True,
            )

            # Store the learning experience
            self.learning_experiences.append(result)

            logger.info(f"Tool learning completed for {learning_id}")
            return result

        except Exception as e:
            logger.error(f"Tool learning failed for {learning_id}: {e}")
            return ToolLearningResult(
                learning_id=learning_id,
                context=context,
                recommendation=ToolRecommendation(
                    recommended_tools=[],
                    usage_pattern=ToolUsagePattern.SEQUENTIAL,
                    confidence=0.0,
                    reasoning=f"Learning failed: {e}",
                    expected_performance={},
                ),
                success=False,
                error_message=str(e),
            )

    async def update_performance(self, learning_id: str, actual_metric: ToolPerformanceMetric):
        """Update the tool learning with actual performance results."""

        # Find the corresponding learning experience
        experience = next((exp for exp in self.learning_experiences if exp.learning_id == learning_id), None)

        if not experience:
            logger.warning(f"Learning experience {learning_id} not found")
            return

        # Update the experience with actual performance
        experience.actual_performance = actual_metric

        # Update tool performance history
        tool_name = actual_metric.tool_name
        if tool_name not in self.tool_performance_history:
            self.tool_performance_history[tool_name] = []
        self.tool_performance_history[tool_name].append(actual_metric)

        # Adapt learning strategy based on performance
        await self._adapt_learning_strategy(experience)

        logger.info(f"Performance updated for {learning_id}: {actual_metric.success_rate:.3f} success rate")

    async def _analyze_historical_performance(self, context: ToolLearningContext) -> dict[str, Any]:
        """Analyze historical performance data for insights."""

        insights = {
            "tool_rankings": {},
            "pattern_effectiveness": {},
            "context_similarities": [],
            "performance_trends": {},
        }

        # Analyze tool performance rankings
        for tool in context.available_tools:
            if tool in self.tool_performance_history:
                metrics = self.tool_performance_history[tool]
                if metrics:
                    avg_success = sum(m.success_rate for m in metrics) / len(metrics)
                    avg_efficiency = sum(m.efficiency_score for m in metrics) / len(metrics)
                    insights["tool_rankings"][tool] = {
                        "success_rate": avg_success,
                        "efficiency": avg_efficiency,
                        "sample_size": len(metrics),
                    }

        # Analyze usage pattern effectiveness
        for pattern in ToolUsagePattern:
            pattern_performances = []
            for exp in self.learning_experiences:
                if exp.recommendation.usage_pattern == pattern and exp.actual_performance:
                    pattern_performances.append(exp.actual_performance.success_rate)

            if pattern_performances:
                insights["pattern_effectiveness"][pattern.value] = {
                    "avg_success": sum(pattern_performances) / len(pattern_performances),
                    "sample_size": len(pattern_performances),
                }

        return insights

    async def _generate_recommendation(
        self, context: ToolLearningContext, insights: dict[str, Any]
    ) -> ToolRecommendation:
        """Generate tool usage recommendation based on context and insights."""

        # Rank available tools based on historical performance
        tool_scores = {}
        for tool in context.available_tools:
            score = 0.5  # Default score

            if tool in insights["tool_rankings"]:
                ranking = insights["tool_rankings"][tool]
                score = (ranking["success_rate"] + ranking["efficiency"]) / 2

                # Adjust for sample size confidence
                confidence_factor = min(1.0, ranking["sample_size"] / 10)
                score = score * confidence_factor + 0.5 * (1 - confidence_factor)

            tool_scores[tool] = score

        # Select top tools
        sorted_tools = sorted(tool_scores.keys(), key=lambda t: tool_scores[t], reverse=True)
        recommended_tools = sorted_tools[: min(3, len(sorted_tools))]

        # Determine usage pattern
        usage_pattern = await self._recommend_usage_pattern(context, insights)

        # Calculate confidence
        if recommended_tools:
            confidence = sum(tool_scores[tool] for tool in recommended_tools) / len(recommended_tools)
        else:
            confidence = 0.5

        # Generate reasoning
        reasoning = f"Selected {len(recommended_tools)} tools based on historical performance and context analysis"
        if insights["tool_rankings"]:
            best_tool = max(
                insights["tool_rankings"].keys(), key=lambda t: insights["tool_rankings"][t]["success_rate"]
            )
            reasoning += f". Best performing tool historically: {best_tool}"

        # Expected performance
        expected_performance = {
            "success_rate": confidence,
            "efficiency": confidence * 0.9,
            "adaptability": confidence * 0.8,
        }

        return ToolRecommendation(
            recommended_tools=recommended_tools,
            usage_pattern=usage_pattern,
            confidence=confidence,
            reasoning=reasoning,
            expected_performance=expected_performance,
        )

    async def _recommend_usage_pattern(
        self, context: ToolLearningContext, insights: dict[str, Any]
    ) -> ToolUsagePattern:
        """Recommend the optimal usage pattern for the given context."""

        # Default to sequential for simplicity
        default_pattern = ToolUsagePattern.SEQUENTIAL

        # Use pattern effectiveness insights if available
        if insights["pattern_effectiveness"]:
            best_pattern_name = max(
                insights["pattern_effectiveness"].keys(),
                key=lambda p: insights["pattern_effectiveness"][p]["avg_success"],
            )
            try:
                return ToolUsagePattern(best_pattern_name)
            except ValueError:
                pass

        # Context-based pattern selection
        num_tools = len(context.available_tools)
        if num_tools > 3:
            return ToolUsagePattern.PARALLEL
        elif "iterative" in context.task_description.lower():
            return ToolUsagePattern.ITERATIVE
        elif "complex" in context.task_description.lower():
            return ToolUsagePattern.HIERARCHICAL

        return default_pattern

    async def _extract_learning_insights(
        self, context: ToolLearningContext, recommendation: ToolRecommendation
    ) -> list[str]:
        """Extract learning insights from the recommendation process."""

        insights = []

        # Tool selection insights
        if len(recommendation.recommended_tools) > 1:
            insights.append(f"Multi-tool approach recommended for: {context.task_description[:50]}...")

        # Pattern insights
        if recommendation.usage_pattern != ToolUsagePattern.SEQUENTIAL:
            insights.append(f"Non-sequential pattern ({recommendation.usage_pattern.value}) may improve efficiency")

        # Confidence insights
        if recommendation.confidence > 0.8:
            insights.append("High confidence recommendation based on strong historical data")
        elif recommendation.confidence < 0.4:
            insights.append("Low confidence - may need more exploration or different approach")

        # Performance expectations
        expected_success = recommendation.expected_performance.get("success_rate", 0.5)
        if expected_success > 0.8:
            insights.append("High success rate expected based on tool performance history")

        return insights

    async def _adapt_learning_strategy(self, experience: ToolLearningResult):
        """Adapt the learning strategy based on actual performance."""

        if not experience.actual_performance:
            return

        predicted_success = experience.recommendation.expected_performance.get("success_rate", 0.5)
        actual_success = experience.actual_performance.success_rate

        prediction_error = abs(predicted_success - actual_success)

        # Adapt strategy based on prediction accuracy
        if prediction_error > 0.3:
            if self.strategy == ToolLearningStrategy.ADAPTIVE:
                # Switch to more exploration-based learning
                self.strategy = ToolLearningStrategy.EXPLORATION
                logger.info("Switched to exploration strategy due to prediction errors")
            elif prediction_error > 0.5:
                # Reset to imitation learning for more conservative approach
                self.strategy = ToolLearningStrategy.IMITATION
                logger.info("Switched to imitation strategy due to high prediction errors")

        experience.adaptation_applied = True

    def get_tool_performance_summary(self) -> dict[str, dict[str, float]]:
        """Get a summary of tool performance across all learning experiences."""

        summary = {}

        for tool_name, metrics in self.tool_performance_history.items():
            if metrics:
                summary[tool_name] = {
                    "avg_success_rate": sum(m.success_rate for m in metrics) / len(metrics),
                    "avg_efficiency": sum(m.efficiency_score for m in metrics) / len(metrics),
                    "avg_execution_time": sum(m.average_execution_time for m in metrics) / len(metrics),
                    "sample_size": len(metrics),
                }

        return summary

    def get_learning_insights(self) -> list[str]:
        """Get overall learning insights from all experiences."""

        insights = []

        if self.learning_experiences:
            total_experiences = len(self.learning_experiences)
            successful_experiences = sum(1 for exp in self.learning_experiences if exp.success)
            success_rate = successful_experiences / total_experiences

            insights.append(
                f"Overall learning success rate: {success_rate:.1%} ({successful_experiences}/{total_experiences})"
            )

            # Strategy insights
            strategy_counts = {}
            for _exp in self.learning_experiences:
                # Assuming we track strategy used (would need to add this field)
                strategy = "current"  # Placeholder
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

            if len(strategy_counts) > 1:
                best_strategy = max(strategy_counts.keys(), key=lambda s: strategy_counts[s])
                insights.append(f"Most used learning approach: {best_strategy}")

        return insights


# Convenience functions


async def quick_tool_learning(task_description: str, available_tools: list[str]) -> ToolRecommendation:
    """Quick tool learning for a simple task."""

    learner = ToolLearner()
    context = ToolLearningContext(
        task_description=task_description, available_tools=available_tools, success_criteria={"completion": True}
    )

    result = await learner.learn_tool_usage(context)
    return result.recommendation


def create_tool_learning_context(task: str, tools: list[str], **kwargs) -> ToolLearningContext:
    """Create a tool learning context with specified parameters."""

    return ToolLearningContext(
        task_description=task,
        available_tools=tools,
        success_criteria=kwargs.get("success_criteria", {}),
        environment_constraints=kwargs.get("environment_constraints", {}),
        user_preferences=kwargs.get("user_preferences", {}),
    )


# Export main classes and functions
__all__ = [
    "ToolExperience",
    "ToolLearner",
    "ToolLearningContext",
    "ToolLearningEngine",  # Alias for ToolLearner for backward compatibility
    "ToolLearningResult",
    "ToolLearningStrategy",
    "ToolMastery",
    "ToolPerformanceMetric",
    "ToolRecommendation",
    "ToolUsagePattern",
    "create_tool_learning_context",
    "quick_tool_learning",
]

# Backward compatibility aliases
ToolLearningEngine = ToolLearner
