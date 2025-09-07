"""
LUKHAS AGI - Tool Selector Engine
Intelligent tool selection and recommendation system for consciousness development.
⚛️🧠🛡️ Trinity Framework: Identity-Consciousness-Guardian
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional


class SelectionStrategy(Enum):
    """Strategies for tool selection."""
    OPTIMAL = "optimal"
    FASTEST = "fastest"
    MOST_ACCURATE = "most_accurate"
    MOST_RELIABLE = "most_reliable"
    LEAST_RESOURCE_INTENSIVE = "least_resource_intensive"
    ADAPTIVE = "adaptive"


class ToolCategory(Enum):
    """Categories of tools."""
    LEARNING = "learning"
    REASONING = "reasoning"
    MEMORY = "memory"
    CREATIVITY = "creativity"
    ANALYSIS = "analysis"
    ORCHESTRATION = "orchestration"
    COMMUNICATION = "communication"


@dataclass
class ToolMetrics:
    """Performance metrics for a tool."""

    accuracy: float = 0.0  # 0.0 to 1.0
    speed: float = 0.0     # Inverted execution time (higher = faster)
    reliability: float = 0.0  # Success rate 0.0 to 1.0
    resource_usage: float = 0.0  # 0.0 to 1.0 (lower = better)
    user_satisfaction: float = 0.0  # 0.0 to 1.0
    usage_count: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolInfo:
    """Information about a registered tool."""

    tool_id: str
    name: str
    description: str
    category: ToolCategory
    capabilities: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    tool_function: Optional[Callable] = None
    metrics: ToolMetrics = field(default_factory=ToolMetrics)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SelectionContext:
    """Context for tool selection."""

    task_description: str
    required_capabilities: list[str] = field(default_factory=list)
    performance_priorities: dict[str, float] = field(default_factory=dict)
    resource_constraints: dict[str, Any] = field(default_factory=dict)
    selection_strategy: SelectionStrategy = SelectionStrategy.ADAPTIVE
    max_tools: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)


# Alias for backward compatibility
SelectionCriteria = SelectionContext

# Additional alias for tool selection - defined after class


@dataclass
class ToolRecommendation:
    """A tool recommendation with scoring."""

    tool_info: ToolInfo
    compatibility_score: float
    performance_score: float
    overall_score: float
    reasoning: str
    confidence: float = 0.0


class ToolSelector:
    """Intelligent tool selection and recommendation system."""

    def __init__(self):
        """Initialize the tool selector."""
        self.registered_tools: dict[str, ToolInfo] = {}
        self.selection_history: list[dict[str, Any]] = []

    def register_tool(
        self,
        tool_id: str,
        name: str,
        description: str,
        category: ToolCategory,
        capabilities: Optional[list[str]] = None,
        tool_function: Optional[Callable] = None,
        **kwargs
    ) -> ToolInfo:
        """Register a tool with the selector."""
        tool_info = ToolInfo(
            tool_id=tool_id,
            name=name,
            description=description,
            category=category,
            capabilities=capabilities or [],
            tool_function=tool_function,
            **kwargs
        )

        self.registered_tools[tool_id] = tool_info

        # Log registration
        self.selection_history.append({
            "event": "tool_registered",
            "tool_id": tool_id,
            "name": name,
            "category": category.value,
            "timestamp": datetime.now(timezone.utc)
        })

        return tool_info

    async def select_tools(
        self,
        context: SelectionContext
    ) -> list[ToolRecommendation]:
        """Select the best tools for a given context."""
        candidates = []

        # Score all tools
        for tool_info in self.registered_tools.values():
            compatibility_score = self._calculate_compatibility(tool_info, context)

            if compatibility_score > 0.0:  # Only consider compatible tools
                performance_score = self._calculate_performance_score(tool_info, context)
                overall_score = self._calculate_overall_score(
                    compatibility_score,
                    performance_score,
                    context
                )

                reasoning = self._generate_reasoning(
                    tool_info,
                    compatibility_score,
                    performance_score,
                    context
                )

                recommendation = ToolRecommendation(
                    tool_info=tool_info,
                    compatibility_score=compatibility_score,
                    performance_score=performance_score,
                    overall_score=overall_score,
                    reasoning=reasoning,
                    confidence=min(compatibility_score, performance_score)
                )

                candidates.append(recommendation)

        # Sort by overall score (highest first)
        candidates.sort(key=lambda x: x.overall_score, reverse=True)

        # Apply selection strategy
        selected = self._apply_selection_strategy(candidates, context)

        # Log selection
        self.selection_history.append({
            "event": "tools_selected",
            "context": context.task_description,
            "strategy": context.selection_strategy.value,
            "selected_tools": [r.tool_info.tool_id for r in selected],
            "timestamp": datetime.now(timezone.utc)
        })

        return selected[:context.max_tools]

    def _calculate_compatibility(
        self,
        tool_info: ToolInfo,
        context: SelectionContext
    ) -> float:
        """Calculate how compatible a tool is with the context."""
        score = 0.0

        # Check capability match
        if context.required_capabilities:
            matching_capabilities = set(tool_info.capabilities) & set(context.required_capabilities)
            capability_score = len(matching_capabilities) / len(context.required_capabilities)
            score += capability_score * 0.6

        # Check prerequisites
        if tool_info.prerequisites:
            # Simplified: assume prerequisites are met for now
            score += 0.2
        else:
            score += 0.2

        # Task description matching (simplified keyword matching)
        description_words = set(context.task_description.lower().split())
        tool_words = set((tool_info.name + " " + tool_info.description).lower().split())

        if description_words & tool_words:
            score += 0.2

        return min(score, 1.0)

    def _calculate_performance_score(
        self,
        tool_info: ToolInfo,
        context: SelectionContext
    ) -> float:
        """Calculate performance score based on metrics and priorities."""
        metrics = tool_info.metrics
        priorities = context.performance_priorities

        # Default weights if no priorities specified
        default_weights = {
            "accuracy": 0.3,
            "speed": 0.2,
            "reliability": 0.3,
            "resource_usage": 0.1,  # Inverted (lower is better)
            "user_satisfaction": 0.1
        }

        weights = {**default_weights, **priorities}

        # Calculate weighted score
        score = (
            weights.get("accuracy", 0) * metrics.accuracy +
            weights.get("speed", 0) * metrics.speed +
            weights.get("reliability", 0) * metrics.reliability +
            weights.get("resource_usage", 0) * (1.0 - metrics.resource_usage) +  # Inverted
            weights.get("user_satisfaction", 0) * metrics.user_satisfaction
        )

        return min(score, 1.0)

    def _calculate_overall_score(
        self,
        compatibility_score: float,
        performance_score: float,
        context: SelectionContext
    ) -> float:
        """Calculate overall score for tool selection."""
        # Weighted combination of compatibility and performance
        compatibility_weight = 0.6
        performance_weight = 0.4

        # Adjust weights based on strategy
        if context.selection_strategy == SelectionStrategy.FASTEST:
            performance_weight = 0.7
            compatibility_weight = 0.3
        elif context.selection_strategy == SelectionStrategy.MOST_ACCURATE:
            performance_weight = 0.7
            compatibility_weight = 0.3

        overall = (compatibility_score * compatibility_weight +
                  performance_score * performance_weight)

        return overall

    def _generate_reasoning(
        self,
        tool_info: ToolInfo,
        compatibility_score: float,
        performance_score: float,
        context: SelectionContext
    ) -> str:
        """Generate human-readable reasoning for the recommendation."""
        reasons = []

        if compatibility_score > 0.8:
            reasons.append("highly compatible with task requirements")
        elif compatibility_score > 0.6:
            reasons.append("good match for task requirements")
        else:
            reasons.append("basic compatibility with task")

        if performance_score > 0.8:
            reasons.append("excellent performance metrics")
        elif performance_score > 0.6:
            reasons.append("good performance history")
        else:
            reasons.append("adequate performance")

        # Add strategy-specific reasoning
        if context.selection_strategy == SelectionStrategy.FASTEST:
            if tool_info.metrics.speed > 0.7:
                reasons.append("fast execution time")
        elif context.selection_strategy == SelectionStrategy.MOST_ACCURATE:
            if tool_info.metrics.accuracy > 0.7:
                reasons.append("high accuracy")

        return f"{tool_info.name}: " + ", ".join(reasons)

    def _apply_selection_strategy(
        self,
        candidates: list[ToolRecommendation],
        context: SelectionContext
    ) -> list[ToolRecommendation]:
        """Apply the selection strategy to filter candidates."""
        if context.selection_strategy == SelectionStrategy.FASTEST:
            # Sort by speed
            candidates.sort(key=lambda x: x.tool_info.metrics.speed, reverse=True)
        elif context.selection_strategy == SelectionStrategy.MOST_ACCURATE:
            # Sort by accuracy
            candidates.sort(key=lambda x: x.tool_info.metrics.accuracy, reverse=True)
        elif context.selection_strategy == SelectionStrategy.MOST_RELIABLE:
            # Sort by reliability
            candidates.sort(key=lambda x: x.tool_info.metrics.reliability, reverse=True)
        elif context.selection_strategy == SelectionStrategy.LEAST_RESOURCE_INTENSIVE:
            # Sort by resource usage (ascending - lower is better)
            candidates.sort(key=lambda x: x.tool_info.metrics.resource_usage)
        # OPTIMAL and ADAPTIVE use the overall score sorting (already done)

        return candidates

    def update_tool_metrics(
        self,
        tool_id: str,
        accuracy: Optional[float] = None,
        speed: Optional[float] = None,
        reliability: Optional[float] = None,
        resource_usage: Optional[float] = None,
        user_satisfaction: Optional[float] = None
    ) -> bool:
        """Update metrics for a tool."""
        if tool_id not in self.registered_tools:
            return False

        metrics = self.registered_tools[tool_id].metrics

        if accuracy is not None:
            metrics.accuracy = accuracy
        if speed is not None:
            metrics.speed = speed
        if reliability is not None:
            metrics.reliability = reliability
        if resource_usage is not None:
            metrics.resource_usage = resource_usage
        if user_satisfaction is not None:
            metrics.user_satisfaction = user_satisfaction

        metrics.usage_count += 1
        metrics.last_updated = datetime.now(timezone.utc)

        return True

    def get_tool_info(self, tool_id: str) -> Optional[ToolInfo]:
        """Get information about a specific tool."""
        return self.registered_tools.get(tool_id)

    def get_all_tools(self) -> list[ToolInfo]:
        """Get all registered tools."""
        return list(self.registered_tools.values())

    def get_tools_by_category(self, category: ToolCategory) -> list[ToolInfo]:
        """Get all tools in a specific category."""
        return [tool for tool in self.registered_tools.values()
                if tool.category == category]


# Convenience functions
async def quick_tool_selection(
    task_description: str,
    required_capabilities: Optional[list[str]] = None,
    strategy: SelectionStrategy = SelectionStrategy.ADAPTIVE
) -> list[ToolRecommendation]:
    """Quick tool selection for simple use cases."""
    selector = ToolSelector()

    # Register some basic tools (for demonstration)
    selector.register_tool(
        "basic_analyzer", "Basic Analyzer", "Simple analysis tool",
        ToolCategory.ANALYSIS, ["analysis", "processing"]
    )

    context = SelectionContext(
        task_description=task_description,
        required_capabilities=required_capabilities or [],
        selection_strategy=strategy
    )

    return await selector.select_tools(context)


# Backward compatibility aliases
ToolSelection = ToolSelector


def create_selection_context(
    task_description: str,
    strategy: SelectionStrategy = SelectionStrategy.ADAPTIVE,
    **kwargs
) -> SelectionContext:
    """Create a selection context with common settings."""
    return SelectionContext(
        task_description=task_description,
        selection_strategy=strategy,
        **kwargs
    )


# Export main classes and functions
__all__ = [
    "ToolSelector",
    "ToolSelection",  # Alias for ToolSelector
    "SelectionStrategy",
    "ToolCategory",
    "ToolMetrics",
    "ToolInfo",
    "SelectionContext",
    "SelectionCriteria",  # Alias for SelectionContext
    "ToolRecommendation",
    "quick_tool_selection",
    "create_selection_context"
]
