"""
Dream-Guided Tool Framework for AGI

Integrates dream processing with tool selection for creative and intuitive
tool usage patterns that go beyond traditional rule-based selection.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np

from ..memory.dream_memory import DreamMemoryBridge
from ..memory.vector_memory import VectorMemoryStore

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Categories of tools available in the system."""

    REASONING = "reasoning"  # Logic and reasoning tools
    CREATIVE = "creative"  # Creative generation tools
    ANALYSIS = "analysis"  # Data analysis and processing
    COMMUNICATION = "communication"  # Communication and interaction
    COMPUTATION = "computation"  # Mathematical and computational
    VISUALIZATION = "visualization"  # Visual and graphical tools
    RESEARCH = "research"  # Research and information gathering
    PLANNING = "planning"  # Planning and strategy tools
    SYNTHESIS = "synthesis"  # Information synthesis tools
    EXECUTION = "execution"  # Task execution tools


class ToolSelectionMode(Enum):
    """Modes of tool selection."""

    LOGICAL = "logical"  # Pure logic-based selection
    INTUITIVE = "intuitive"  # Intuition and pattern-based
    CREATIVE = "creative"  # Creative and novel approaches
    EXPERIMENTAL = "experimental"  # Experimental and exploratory
    DREAM_GUIDED = "dream_guided"  # Dream insight guided selection
    HYBRID = "hybrid"  # Combination of multiple modes


@dataclass
class ToolSpecification:
    """Specification of a tool available in the system."""

    tool_id: str
    name: str
    description: str
    category: ToolCategory

    # Tool capabilities
    input_types: list[str]  # What types of input it accepts
    output_types: list[str]  # What types of output it produces
    capabilities: dict[str, float]  # Capability scores (0-1)

    # Usage information
    complexity: float  # Tool complexity (0-1)
    learning_curve: float  # How hard to master (0-1)
    reliability: float  # How reliable results are (0-1)
    cost: float  # Computational/time cost (0-1)

    # LUKHAS Integration
    constellation_affinity: dict[str, float] = field(default_factory=dict)
    dream_resonance: float = 0.0  # How well tool works with dream insights

    # Function reference
    tool_function: Optional[Callable] = None

    def calculate_suitability(self, context: dict[str, Any]) -> float:
        """Calculate suitability for given context."""
        base_score = 0.5

        # Capability matching
        if "required_capabilities" in context:
            capability_match = 0.0
            for capability, required_level in context["required_capabilities"].items():
                tool_level = self.capabilities.get(capability, 0.0)
                if tool_level >= required_level:
                    capability_match += min(1.0, tool_level / required_level)

            if context["required_capabilities"]:
                capability_match /= len(context["required_capabilities"])
                base_score += capability_match * 0.4

        # Constellation alignment
        if "constellation_context" in context:
            constellation_match = 0.0
            for star, relevance in context["constellation_context"].items():
                affinity = self.constellation_affinity.get(star, 0.0)
                constellation_match += affinity * relevance

            if context["constellation_context"]:
                constellation_match /= len(context["constellation_context"])
                base_score += constellation_match * 0.3

        # Dream compatibility
        if context.get("dream_context", False):
            base_score += self.dream_resonance * 0.2

        # Cost consideration
        cost_preference = context.get("cost_preference", 0.5)  # 0=cheap, 1=expensive ok
        if cost_preference < 0.5 and self.cost > 0.7:
            base_score *= 0.8  # Penalize expensive tools if cost-sensitive

        return min(1.0, base_score)


@dataclass
class ToolInsight:
    """Insight about tool usage from dream processing."""

    insight_id: str
    tool_id: str
    insight_type: str  # Type of insight discovered
    description: str  # Description of the insight
    confidence: float  # Confidence in insight validity

    # Context information
    discovery_context: dict[str, Any] = field(default_factory=dict)
    dream_session_id: Optional[str] = None

    # Application information
    suggested_usage: Optional[str] = None
    expected_benefits: list[str] = field(default_factory=list)
    potential_risks: list[str] = field(default_factory=list)

    # Validation
    validated: bool = False
    validation_results: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolRecommendation:
    """Recommendation for tool usage."""

    recommendation_id: str
    primary_tool: str  # Primary recommended tool
    supporting_tools: list[str] = field(default_factory=list)

    # Recommendation details
    reasoning: str  # Why this tool is recommended
    confidence: float  # Confidence in recommendation
    selection_mode: ToolSelectionMode

    # Context and insights
    context_factors: dict[str, Any] = field(default_factory=dict)
    dream_insights: list[ToolInsight] = field(default_factory=list)

    # Expected outcomes
    expected_effectiveness: float = 0.5
    expected_creativity: float = 0.5
    expected_learning: float = 0.5

    # Risk assessment
    risk_level: float = 0.1  # Risk level (0-1)
    fallback_tools: list[str] = field(default_factory=list)


class DreamGuidedToolFramework:
    """
    Advanced Tool Framework with Dream-Guided Selection

    Provides intelligent tool selection that combines logical analysis
    with creative dream insights for more intuitive and effective tool usage.
    """

    def __init__(self, memory_store: VectorMemoryStore, dream_bridge: DreamMemoryBridge):
        self.memory_store = memory_store
        self.dream_bridge = dream_bridge

        # Tool registry
        self.tools: dict[str, ToolSpecification] = {}
        self.tool_experiences: list[dict[str, Any]] = []
        self.tool_insights: dict[str, list[ToolInsight]] = {}

        # Learning and adaptation
        self.usage_patterns: dict[str, list[dict[str, Any]]] = {}
        self.success_rates: dict[str, float] = {}
        self.dream_enhanced_tools: set[str] = set()

        # Configuration
        self.insight_confidence_threshold = 0.6
        self.dream_integration_weight = 0.3
        self.experience_weight = 0.4
        self.novelty_bonus = 0.1

        # Initialize with some basic tools
        self._initialize_basic_tools()

        # Statistics
        self.stats = {
            "total_recommendations": 0,
            "dream_guided_recommendations": 0,
            "successful_recommendations": 0,
            "tools_discovered": 0,
            "avg_recommendation_confidence": 0.0,
        }

    def _initialize_basic_tools(self):
        """Initialize basic tools for the framework."""

        # Reasoning tools
        self.register_tool(
            ToolSpecification(
                tool_id="chain_of_thought",
                name="Chain of Thought Reasoning",
                description="Step-by-step logical reasoning through complex problems",
                category=ToolCategory.REASONING,
                input_types=["problem", "question", "scenario"],
                output_types=["reasoning_chain", "solution", "analysis"],
                capabilities={"reasoning": 0.9, "logic": 0.95, "analysis": 0.8},
                complexity=0.3,
                learning_curve=0.2,
                reliability=0.9,
                cost=0.3,
                constellation_affinity={"IDENTITY": 0.8, "VISION": 0.7},
                dream_resonance=0.4,
            )
        )

        # Creative tools
        self.register_tool(
            ToolSpecification(
                tool_id="creative_synthesis",
                name="Creative Synthesis Engine",
                description="Combine disparate elements into novel creative solutions",
                category=ToolCategory.CREATIVE,
                input_types=["concepts", "ideas", "elements"],
                output_types=["creative_solution", "innovation", "synthesis"],
                capabilities={"creativity": 0.95, "synthesis": 0.9, "innovation": 0.85},
                complexity=0.6,
                learning_curve=0.5,
                reliability=0.7,
                cost=0.4,
                constellation_affinity={"DREAM": 0.95, "QUANTUM": 0.8, "BIO": 0.7},
                dream_resonance=0.9,
            )
        )

        # Analysis tools
        self.register_tool(
            ToolSpecification(
                tool_id="pattern_analyzer",
                name="Pattern Analysis Tool",
                description="Identify and analyze patterns in data and information",
                category=ToolCategory.ANALYSIS,
                input_types=["data", "information", "observations"],
                output_types=["patterns", "insights", "correlations"],
                capabilities={"pattern_recognition": 0.9, "analysis": 0.85, "insight": 0.8},
                complexity=0.4,
                learning_curve=0.3,
                reliability=0.85,
                cost=0.2,
                constellation_affinity={"VISION": 0.9, "MEMORY": 0.7},
                dream_resonance=0.6,
            )
        )

        # Communication tools
        self.register_tool(
            ToolSpecification(
                tool_id="narrative_builder",
                name="Narrative Construction Tool",
                description="Build compelling narratives and explanations",
                category=ToolCategory.COMMUNICATION,
                input_types=["facts", "events", "concepts"],
                output_types=["narrative", "explanation", "story"],
                capabilities={"communication": 0.9, "storytelling": 0.85, "clarity": 0.8},
                complexity=0.5,
                learning_curve=0.4,
                reliability=0.8,
                cost=0.3,
                constellation_affinity={"ETHICS": 0.7, "DREAM": 0.6},
                dream_resonance=0.5,
            )
        )

    def register_tool(self, tool_spec: ToolSpecification):
        """Register a new tool in the framework."""
        self.tools[tool_spec.tool_id] = tool_spec
        self.tool_insights[tool_spec.tool_id] = []
        self.usage_patterns[tool_spec.tool_id] = []
        self.success_rates[tool_spec.tool_id] = 0.5  # Start with neutral success rate

        logger.info(f"Registered tool: {tool_spec.name} ({tool_spec.category.value})")

    async def recommend_tools(
        self,
        context: dict[str, Any],
        selection_mode: ToolSelectionMode = ToolSelectionMode.HYBRID,
        max_recommendations: int = 5,
    ) -> list[ToolRecommendation]:
        """
        Recommend tools based on context and selection mode.

        Args:
            context: Context information including task, constraints, preferences
            selection_mode: How to select tools (logical, intuitive, creative, etc.)
            max_recommendations: Maximum number of recommendations to return

        Returns:
            List of tool recommendations sorted by suitability
        """

        recommendations = []

        try:
            if selection_mode == ToolSelectionMode.LOGICAL:
                recommendations = await self._logical_tool_selection(context, max_recommendations)

            elif selection_mode == ToolSelectionMode.INTUITIVE:
                recommendations = await self._intuitive_tool_selection(context, max_recommendations)

            elif selection_mode == ToolSelectionMode.CREATIVE:
                recommendations = await self._creative_tool_selection(context, max_recommendations)

            elif selection_mode == ToolSelectionMode.DREAM_GUIDED:
                recommendations = await self._dream_guided_tool_selection(context, max_recommendations)

            elif selection_mode == ToolSelectionMode.EXPERIMENTAL:
                recommendations = await self._experimental_tool_selection(context, max_recommendations)

            elif selection_mode == ToolSelectionMode.HYBRID:
                recommendations = await self._hybrid_tool_selection(context, max_recommendations)

            # Update statistics
            self.stats["total_recommendations"] += len(recommendations)
            if selection_mode == ToolSelectionMode.DREAM_GUIDED:
                self.stats["dream_guided_recommendations"] += len(recommendations)

            if recommendations:
                avg_confidence = np.mean([r.confidence for r in recommendations])
                current_avg = self.stats["avg_recommendation_confidence"]
                total_recs = self.stats["total_recommendations"]
                self.stats["avg_recommendation_confidence"] = (
                    current_avg * (total_recs - len(recommendations)) + avg_confidence * len(recommendations)
                ) / total_recs

            return recommendations

        except Exception as e:
            logger.error(f"Error in tool recommendation: {e}")
            return []

    async def _logical_tool_selection(
        self, context: dict[str, Any], max_recommendations: int
    ) -> list[ToolRecommendation]:
        """Pure logic-based tool selection."""

        scored_tools = []

        for tool_id, tool_spec in self.tools.items():
            suitability = tool_spec.calculate_suitability(context)

            # Add experience bonus
            success_rate = self.success_rates.get(tool_id, 0.5)
            experience_bonus = (success_rate - 0.5) * self.experience_weight

            total_score = suitability + experience_bonus
            scored_tools.append((tool_id, total_score))

        # Sort by score and create recommendations
        scored_tools.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for tool_id, score in scored_tools[:max_recommendations]:
            tool_spec = self.tools[tool_id]

            rec = ToolRecommendation(
                recommendation_id=f"logical_{datetime.now(timezone.utc).strftime('%H%M%S')}_{tool_id}",
                primary_tool=tool_id,
                reasoning=f"Logical selection based on capability match and experience (score: {score:.2f})",
                confidence=min(0.95, score),
                selection_mode=ToolSelectionMode.LOGICAL,
                context_factors=context,
                expected_effectiveness=min(1.0, score),
                risk_level=0.05,  # Low risk for logical selection
            )

            recommendations.append(rec)

        return recommendations

    async def _intuitive_tool_selection(
        self, context: dict[str, Any], max_recommendations: int
    ) -> list[ToolRecommendation]:
        """Intuition and pattern-based tool selection."""

        # Look for patterns in previous successful tool usage
        pattern_scores = {}

        for tool_id, usage_history in self.usage_patterns.items():
            pattern_score = 0.0

            for past_usage in usage_history[-10:]:  # Last 10 usages
                # Simple pattern matching based on context similarity
                context_similarity = self._calculate_context_similarity(context, past_usage.get("context", {}))
                if past_usage.get("success", False):
                    pattern_score += context_similarity * 0.1

            # Add constellation alignment intuition
            if "constellation_context" in context:
                tool_spec = self.tools[tool_id]
                constellation_intuition = 0.0
                for star, relevance in context["constellation_context"].items():
                    affinity = tool_spec.constellation_affinity.get(star, 0.0)
                    constellation_intuition += affinity * relevance * 0.2

                pattern_score += constellation_intuition

            pattern_scores[tool_id] = pattern_score

        # Sort by intuitive score
        sorted_tools = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)

        recommendations = []
        for tool_id, score in sorted_tools[:max_recommendations]:
            if score > 0.1:  # Only recommend if there's some intuitive basis
                rec = ToolRecommendation(
                    recommendation_id=f"intuitive_{datetime.now(timezone.utc).strftime('%H%M%S')}_{tool_id}",
                    primary_tool=tool_id,
                    reasoning="Intuitive selection based on pattern recognition and past success",
                    confidence=min(0.8, score * 2),  # Scale confidence
                    selection_mode=ToolSelectionMode.INTUITIVE,
                    context_factors=context,
                    expected_effectiveness=min(1.0, score * 1.5),
                    risk_level=0.2,  # Medium risk for intuitive selection
                )

                recommendations.append(rec)

        return recommendations

    async def _creative_tool_selection(
        self, context: dict[str, Any], max_recommendations: int
    ) -> list[ToolRecommendation]:
        """Creative and novel tool selection approaches."""

        # Favor creative tools and unusual combinations
        creative_scores = {}

        for tool_id, tool_spec in self.tools.items():
            creative_score = 0.0

            # Base creativity of the tool
            creative_score += tool_spec.capabilities.get("creativity", 0.0) * 0.4

            # Novelty bonus for less frequently used tools
            usage_frequency = len(self.usage_patterns.get(tool_id, []))
            max_usage = max([len(patterns) for patterns in self.usage_patterns.values()] + [1])
            novelty_score = (1.0 - usage_frequency / max_usage) * self.novelty_bonus
            creative_score += novelty_score

            # Dream resonance bonus
            creative_score += tool_spec.dream_resonance * 0.3

            # Creative constellation alignment
            if "constellation_context" in context:
                creative_constellations = ["DREAM", "QUANTUM", "BIO"]
                for star in creative_constellations:
                    if star in context["constellation_context"]:
                        affinity = tool_spec.constellation_affinity.get(star, 0.0)
                        creative_score += affinity * context["constellation_context"][star] * 0.2

            creative_scores[tool_id] = creative_score

        # Sort by creative score
        sorted_tools = sorted(creative_scores.items(), key=lambda x: x[1], reverse=True)

        recommendations = []
        for tool_id, score in sorted_tools[:max_recommendations]:
            rec = ToolRecommendation(
                recommendation_id=f"creative_{datetime.now(timezone.utc).strftime('%H%M%S')}_{tool_id}",
                primary_tool=tool_id,
                reasoning="Creative selection emphasizing novelty and creative potential",
                confidence=min(0.7, score),
                selection_mode=ToolSelectionMode.CREATIVE,
                context_factors=context,
                expected_creativity=min(1.0, score),
                expected_effectiveness=score * 0.8,  # May be less predictably effective
                risk_level=0.3,  # Higher risk for creative approaches
            )

            recommendations.append(rec)

        return recommendations

    async def _dream_guided_tool_selection(
        self, context: dict[str, Any], max_recommendations: int
    ) -> list[ToolRecommendation]:
        """Dream insight guided tool selection."""

        # Get dream insights about tool usage
        dream_insights = await self._gather_tool_dream_insights(context)

        dream_scores = {}
        dream_recommendations = []

        # Score tools based on dream insights
        for tool_id, tool_spec in self.tools.items():
            dream_score = 0.0
            relevant_insights = []

            # Check for direct tool insights
            if tool_id in self.tool_insights:
                for insight in self.tool_insights[tool_id]:
                    if insight.confidence > self.insight_confidence_threshold:
                        dream_score += insight.confidence * 0.4
                        relevant_insights.append(insight)

            # General dream resonance
            dream_score += tool_spec.dream_resonance * 0.3

            # Dream-derived context matching
            for insight in dream_insights:
                if self._insight_matches_tool(insight, tool_spec):
                    dream_score += insight.confidence * 0.2
                    relevant_insights.append(insight)

            if dream_score > 0.1:  # Only consider tools with some dream connection
                dream_scores[tool_id] = dream_score

                rec = ToolRecommendation(
                    recommendation_id=f"dream_{datetime.now(timezone.utc).strftime('%H%M%S')}_{tool_id}",
                    primary_tool=tool_id,
                    reasoning=f"Dream-guided selection based on {len(relevant_insights)} insights",
                    confidence=min(0.85, dream_score),
                    selection_mode=ToolSelectionMode.DREAM_GUIDED,
                    context_factors=context,
                    dream_insights=relevant_insights,
                    expected_effectiveness=dream_score * 0.9,
                    expected_creativity=min(1.0, dream_score + 0.2),
                    risk_level=0.15,  # Medium-low risk - dreams can be insightful but uncertain
                )

                dream_recommendations.append(rec)

        # Sort by dream score and return top recommendations
        dream_recommendations.sort(key=lambda r: r.confidence, reverse=True)
        return dream_recommendations[:max_recommendations]

    async def _experimental_tool_selection(
        self, context: dict[str, Any], max_recommendations: int
    ) -> list[ToolRecommendation]:
        """Experimental and exploratory tool selection."""

        # Select tools that haven't been tried much or in novel combinations
        experimental_scores = {}

        for tool_id, tool_spec in self.tools.items():
            experimental_score = 0.0

            # Novelty factor (prefer less used tools)
            usage_count = len(self.usage_patterns.get(tool_id, []))
            novelty_factor = 1.0 / (usage_count + 1)  # Add 1 to avoid division by zero
            experimental_score += novelty_factor * 0.5

            # Complexity bonus (more complex tools for experimentation)
            experimental_score += tool_spec.complexity * 0.3

            # Low reliability tools can be interesting to experiment with
            if tool_spec.reliability < 0.8:
                experimental_score += (0.8 - tool_spec.reliability) * 0.2

            experimental_scores[tool_id] = experimental_score

        # Sort by experimental score
        sorted_tools = sorted(experimental_scores.items(), key=lambda x: x[1], reverse=True)

        recommendations = []
        for tool_id, score in sorted_tools[:max_recommendations]:
            rec = ToolRecommendation(
                recommendation_id=f"experimental_{datetime.now(timezone.utc).strftime('%H%M%S')}_{tool_id}",
                primary_tool=tool_id,
                reasoning="Experimental selection for exploration and learning",
                confidence=0.6,  # Moderate confidence for experimental approaches
                selection_mode=ToolSelectionMode.EXPERIMENTAL,
                context_factors=context,
                expected_learning=min(1.0, score),
                expected_effectiveness=0.5,  # Uncertain effectiveness
                risk_level=0.4,  # Higher risk for experimental approaches
            )

            recommendations.append(rec)

        return recommendations

    async def _hybrid_tool_selection(
        self, context: dict[str, Any], max_recommendations: int
    ) -> list[ToolRecommendation]:
        """Hybrid approach combining multiple selection methods."""

        # Get recommendations from multiple approaches
        logical_recs = await self._logical_tool_selection(context, max_recommendations)
        intuitive_recs = await self._intuitive_tool_selection(context, max_recommendations // 2)
        creative_recs = await self._creative_tool_selection(context, max_recommendations // 2)

        # Try dream guidance if context suggests it
        dream_recs = []
        if context.get("creative_context", False) or "DREAM" in context.get("constellation_context", {}):
            dream_recs = await self._dream_guided_tool_selection(context, max_recommendations // 2)

        # Combine and weight recommendations
        all_recs = {}

        # Weight logical recommendations highly
        for rec in logical_recs:
            all_recs[rec.primary_tool] = rec
            rec.confidence *= 0.9  # Slightly reduce confidence for hybrid

        # Add intuitive recommendations with medium weight
        for rec in intuitive_recs:
            if rec.primary_tool not in all_recs or rec.confidence > all_recs[rec.primary_tool].confidence * 0.8:
                rec.selection_mode = ToolSelectionMode.HYBRID
                rec.reasoning = f"Hybrid: {rec.reasoning}"
                all_recs[rec.primary_tool] = rec

        # Add creative recommendations with lower weight
        for rec in creative_recs:
            if rec.primary_tool not in all_recs:
                rec.selection_mode = ToolSelectionMode.HYBRID
                rec.reasoning = f"Hybrid: {rec.reasoning}"
                rec.confidence *= 0.7  # Reduce confidence for creative additions
                all_recs[rec.primary_tool] = rec

        # Add dream recommendations with special consideration
        for rec in dream_recs:
            if rec.primary_tool not in all_recs or len(rec.dream_insights) > 0:
                rec.selection_mode = ToolSelectionMode.HYBRID
                rec.reasoning = f"Hybrid (Dream-enhanced): {rec.reasoning}"
                all_recs[rec.primary_tool] = rec

        # Sort by confidence and return
        final_recs = list(all_recs.values())
        final_recs.sort(key=lambda r: r.confidence, reverse=True)

        return final_recs[:max_recommendations]

    async def _gather_tool_dream_insights(self, context: dict[str, Any]) -> list[ToolInsight]:
        """Gather dream insights relevant to tool selection."""

        insights = []

        # Look for recent dream sessions that might have tool-related insights
        recent_dream_sessions = [
            session
            for session in self.dream_bridge.dream_sessions[-5:]  # Last 5 sessions
            if session.success
            and (datetime.now(timezone.utc) - datetime.fromisoformat(session.session_id.split("_")[1]) < timedelta(hours=24))
        ]

        for session in recent_dream_sessions:
            for insight_data in session.insights_generated:
                # Convert dream insights to tool insights if relevant
                if any(
                    keyword in insight_data.get("content", "").lower()
                    for keyword in ["tool", "method", "approach", "technique"]
                ):

                    tool_insight = ToolInsight(
                        insight_id=f"dream_tool_{session.session_id}_{len(insights)}",
                        tool_id="",  # Will be matched later
                        insight_type="dream_guidance",
                        description=insight_data.get("content", ""),
                        confidence=insight_data.get("confidence", 0.5),
                        discovery_context=context,
                        dream_session_id=session.session_id,
                    )

                    insights.append(tool_insight)

        return insights

    def _insight_matches_tool(self, insight: ToolInsight, tool_spec: ToolSpecification) -> bool:
        """Check if a dream insight is relevant to a specific tool."""

        # Simple keyword matching (could be enhanced with semantic similarity)
        insight_text = insight.description.lower()
        tool_keywords = [
            tool_spec.name.lower(),
            tool_spec.category.value,
            *tool_spec.input_types,
            *tool_spec.output_types,
        ]

        return any(keyword in insight_text for keyword in tool_keywords)

    def _calculate_context_similarity(self, context1: dict[str, Any], context2: dict[str, Any]) -> float:
        """Calculate similarity between two contexts."""

        # Simple similarity based on shared keys and constellation context
        similarity = 0.0

        # Check for shared constellation context
        if "constellation_context" in context1 and "constellation_context" in context2:
            shared_stars = set(context1["constellation_context"].keys()) & set(context2["constellation_context"].keys())
            similarity += len(shared_stars) * 0.1

        # Check for shared keywords or categories
        context1_str = " ".join(str(v) for v in context1.values()).lower()
        context2_str = " ".join(str(v) for v in context2.values()).lower()

        # Simple word overlap
        words1 = set(context1_str.split())
        words2 = set(context2_str.split())
        word_overlap = len(words1 & words2) / max(len(words1 | words2), 1)
        similarity += word_overlap * 0.5

        return min(1.0, similarity)

    async def record_tool_usage(
        self,
        tool_id: str,
        context: dict[str, Any],
        success: bool,
        effectiveness: float,
        insights_gained: Optional[list[str]] = None,
    ):
        """Record tool usage for learning and improvement."""

        if tool_id not in self.tools:
            return

        usage_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": context,
            "success": success,
            "effectiveness": effectiveness,
            "insights": insights_gained or [],
        }

        self.usage_patterns[tool_id].append(usage_record)

        # Update success rate with exponential moving average
        current_rate = self.success_rates[tool_id]
        alpha = 0.1  # Learning rate
        self.success_rates[tool_id] = current_rate * (1 - alpha) + (1.0 if success else 0.0) * alpha

        # Update statistics
        if success:
            self.stats["successful_recommendations"] += 1

        logger.debug(f"Recorded tool usage: {tool_id} - Success: {success}, Effectiveness: {effectiveness}")

    async def discover_tool_insight(self, tool_id: str, insight: ToolInsight):
        """Record a discovered insight about tool usage."""

        if tool_id not in self.tool_insights:
            self.tool_insights[tool_id] = []

        self.tool_insights[tool_id].append(insight)

        # Mark tool as dream-enhanced if insight comes from dreams
        if insight.dream_session_id:
            self.dream_enhanced_tools.add(tool_id)

        self.stats["tools_discovered"] += 1

        logger.info(f"Discovered tool insight for {tool_id}: {insight.description}")

    def get_tool_framework_stats(self) -> dict[str, Any]:
        """Get comprehensive tool framework statistics."""

        return {
            **self.stats,
            "registered_tools": len(self.tools),
            "tools_with_insights": len([tid for tid, insights in self.tool_insights.items() if insights]),
            "dream_enhanced_tools": len(self.dream_enhanced_tools),
            "tool_categories": {
                category.value: len([t for t in self.tools.values() if t.category == category])
                for category in ToolCategory
            },
            "success_rates": {
                tool_id: rate
                for tool_id, rate in self.success_rates.items()
                if rate != 0.5  # Only show tools with recorded usage
            },
        }
