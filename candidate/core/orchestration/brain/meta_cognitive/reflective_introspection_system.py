"""
Reflective Introspection System for lukhas AI

This module provides meta-cognitive capabilities for the system to evaluate its own
performance and identify areas for improvement through reflective introspection.

Based on the advanced implementation from Lukhas GitHub repository.
"""

import datetime
import logging
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)


class ReflectiveIntrospectionSystem:
    """
    System that evaluates its own performance and identifies areas for improvement.
    Provides meta-cognitive capabilities for architectural self-adaptation.
    """

    def __init__(self):
        self.reflection_cycle = 0
        self.reflection_interval = 50  # Reflection after this many interactions
        self.interaction_buffer = []
        self.insight_history = []
        self.improvement_plans = []
        self.active_improvements = {}
        self.last_reflection_time = None
        self.performance_metrics = {
            "accuracy": [],
            "response_time": [],
            "user_satisfaction": [],
            "adaptation_rate": [],
            "memory_efficiency": [],
            "cognitive_load": [],
        }

    def log_interaction(self, interaction_data: dict) -> None:
        """
        Log an interaction for future reflection

        Args:
            interaction_data: Data about the interaction including metrics
        """
        # Add timestamp if not present
        if "timestamp" not in interaction_data:
            interaction_data["timestamp"] = datetime.datetime.now().isoformat()

        self.interaction_buffer.append(interaction_data)

        # Extract and store performance metrics
        if "metrics" in interaction_data:
            metrics = interaction_data["metrics"]
            for key in self.performance_metrics:
                if key in metrics:
                    self.performance_metrics[key].append(metrics[key])

        # Check if we should trigger reflection
        if len(self.interaction_buffer) >= self.reflection_interval:
            self.reflect()

    def reflect(self) -> dict:
        """
        Perform reflective introspection on recent interactions

        Returns:
            Dictionary containing insights and improvement plans
        """
        if not self.interaction_buffer:
            return {"insights": [], "improvements": []}

        self.reflection_cycle += 1
        self.last_reflection_time = datetime.datetime.now()
        logger.info(
            f"Performing reflective introspection cycle {self.reflection_cycle}"
        )

        # Analyze recent interactions
        insights = self._analyze_interactions()

        # Create improvement plans based on insights
        improvements = self._generate_improvement_plans(insights)

        # Store insights and plans
        self.insight_history.extend(insights)
        self.improvement_plans.extend(improvements)

        # Implement immediate improvements
        self._implement_improvements(improvements)

        # Clear buffer after reflection
        self.interaction_buffer = []

        # Return insights and improvement plans
        result = {
            "cycle": self.reflection_cycle,
            "insights": insights,
            "improvements": improvements,
            "timestamp": self.last_reflection_time.isoformat(),
        }

        return result

    def _analyze_interactions(self) -> list[dict]:
        """
        Analyze recent interactions to derive insights

        Returns:
            List of insights derived from analysis
        """
        insights = []

        # Pattern detection in user interactions
        user_patterns = self._detect_user_patterns()
        if user_patterns:
            insights.append(
                {
                    "type": "user_pattern",
                    "description": "Detected recurring patterns in user interactions",
                    "details": user_patterns,
                    "confidence": 0.75,
                }
            )

        # Performance trend analysis
        for metric, values in self.performance_metrics.items():
            if len(values) >= 10:
                trend = self._calculate_trend(values[-10:])
                if abs(trend) > 0.1:  # Significant trend
                    direction = "improving" if trend > 0 else "declining"
                    insights.append(
                        {
                            "type": "performance_trend",
                            "description": f"System {metric} is {direction}",
                            "metric": metric,
                            "trend": trend,
                            "confidence": min(0.9, abs(trend) * 5),
                        }
                    )

        # Error pattern analysis
        error_patterns = self._detect_error_patterns()
        if error_patterns:
            insights.append(
                {
                    "type": "error_pattern",
                    "description": "Identified recurring error patterns",
                    "details": error_patterns,
                    "confidence": 0.8,
                }
            )

        # Add timestamp
        for insight in insights:
            insight["timestamp"] = datetime.datetime.now().isoformat()

        return insights

    def _detect_user_patterns(self) -> list[dict]:
        """
        Detect patterns in user interactions

        Returns:
            List of detected user patterns
        """
        patterns = []

        # Group interactions by user behavior
        user_actions = defaultdict(list)
        for interaction in self.interaction_buffer:
            action_type = interaction.get("action_type", "unknown")
            user_actions[action_type].append(interaction)

        # Look for frequent patterns
        for action_type, actions in user_actions.items():
            if len(actions) >= 3:  # Minimum for pattern detection
                patterns.append(
                    {
                        "pattern_type": action_type,
                        "frequency": len(actions),
                        "confidence": min(
                            0.9, len(actions) / len(self.interaction_buffer)
                        ),
                    }
                )

        return patterns

    def _detect_error_patterns(self) -> list[dict]:
        """
        Detect patterns in system errors

        Returns:
            List of detected error patterns
        """
        error_patterns = []

        error_types = defaultdict(list)
        for interaction in self.interaction_buffer:
            if "error" in interaction:
                error_type = interaction.get("error_type", "unknown")
                error_types[error_type].append(interaction)

        for error_type, occurrences in error_types.items():
            if len(occurrences) >= 2:
                error_patterns.append(
                    {
                        "type": error_type,
                        "count": len(occurrences),
                        "example": occurrences[0].get("error"),
                    }
                )

        return error_patterns

    def _calculate_trend(self, values: list[float]) -> float:
        """
        Calculate trend in a series of values

        Args:
            values: List of numeric values

        Returns:
            Trend coefficient (-1 to 1)
        """
        if len(values) < 2:
            return 0.0

        n = len(values)
        x_values = list(range(n))

        # Calculate linear regression slope
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0

        numerator = n * sum_xy - sum_x * sum_y
        slope = numerator / denominator

        # Normalize to -1..1 range
        max_abs_slope = (max(values) - min(values)) / (n - 1)
        if max_abs_slope == 0:
            return 0.0

        normalized_slope = slope / max_abs_slope
        return max(-1.0, min(1.0, normalized_slope))

    def _generate_improvement_plans(self, insights: list[dict]) -> list[dict]:
        """
        Generate improvement plans based on insights

        Args:
            insights: List of insights from analysis

        Returns:
            List of improvement plans
        """
        improvements = []

        for insight in insights:
            if insight["type"] == "performance_trend":
                metric = insight["metric"]
                trend = insight["trend"]

                if trend < 0:  # Declining performance
                    improvements.append(
                        {
                            "type": "performance_optimization",
                            "description": f"Optimize {metric} performance",
                            "target": metric,
                            "priority": 0.8,
                            "status": "proposed",
                        }
                    )

            elif insight["type"] == "error_pattern":
                for error in insight.get("details", []):
                    improvements.append(
                        {
                            "type": "error_handling",
                            "description": f"Improve handling of {error['type']} errors",
                            "target": error["type"],
                            "priority": 0.9,
                            "status": "proposed",
                        }
                    )

        # Add timestamp and ID
        for i, improvement in enumerate(improvements):
            improvement["id"] = f"imp_{self.reflection_cycle}_{i}"
            improvement["created_at"] = datetime.datetime.now().isoformat()

        return improvements

    def _implement_improvements(self, improvements: list[dict]) -> None:
        """
        Implement improvement plans

        Args:
            improvements: List of improvement plans
        """
        for improvement in improvements:
            # Add to active improvements
            improvement_id = improvement["id"]
            improvement["status"] = "active"
            improvement["implemented_at"] = datetime.datetime.now().isoformat()
            self.active_improvements[improvement_id] = improvement

            logger.info(f"Implementing improvement: {improvement['description']}")

            # Actual implementation would vary based on improvement type
            # This is a placeholder for future implementation logic

    def get_status_report(self) -> dict:
        """
        Generate a status report on the reflection system

        Returns:
            Dictionary with status information
        """
        # Calculate improvement metrics
        total_insights = len(self.insight_history)
        total_improvements = len(self.improvement_plans)
        active_improvements = len(
            [imp for imp in self.improvement_plans if imp.get("status") == "active"]
        )
        completed_improvements = len(
            [imp for imp in self.improvement_plans if imp.get("status") == "completed"]
        )

        # Latest insights
        latest_insights = self.insight_history[-5:] if self.insight_history else []

        return {
            "reflection_cycles": self.reflection_cycle,
            "last_reflection": (
                self.last_reflection_time.isoformat()
                if self.last_reflection_time
                else None
            ),
            "total_insights_generated": total_insights,
            "total_improvements_proposed": total_improvements,
            "active_improvements": active_improvements,
            "completed_improvements": completed_improvements,
            "latest_insights": latest_insights,
            "generated_at": datetime.datetime.now().isoformat(),
        }

    def analyze_system_performance(self) -> dict:
        """
        Analyze and optimize overall system architecture

        Returns:
            Analysis results and optimization recommendations
        """
        bottlenecks = self.identify_bottlenecks()
        adaptations = self.apply_architectural_adaptations(bottlenecks)

        return {
            "bottlenecks": bottlenecks,
            "adaptations": adaptations,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def identify_bottlenecks(self) -> list[dict]:
        """
        Identify performance bottlenecks in the system

        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []

        # Analyze performance metrics for bottlenecks
        for metric, values in self.performance_metrics.items():
            if len(values) >= 5:
                recent_avg = sum(values[-5:]) / 5

                # Define thresholds for different metrics
                thresholds = {
                    "response_time": 2.0,  # seconds
                    "memory_efficiency": 0.8,  # efficiency ratio
                    "cognitive_load": 0.9,  # load ratio
                    "accuracy": 0.95,  # accuracy ratio
                }

                threshold = thresholds.get(metric, 1.0)

                if (
                    metric in ["response_time", "cognitive_load"]
                    and recent_avg > threshold
                ) or " + "(
                    metric in ["memory_efficiency", "accuracy"]
                    and recent_avg < threshold
                ):
                    bottlenecks.append(
                        {
                            "type": "performance_bottleneck",
                            "metric": metric,
                            "current_value": recent_avg,
                            "threshold": threshold,
                            "severity": abs(recent_avg - threshold) / threshold,
                        }
                    )

        return bottlenecks

    def apply_architectural_adaptations(self, bottlenecks: list[dict]) -> list[dict]:
        """
        Apply architectural adaptations based on identified bottlenecks

        Args:
            bottlenecks: List of identified bottlenecks

        Returns:
            List of applied adaptations
        """
        adaptations = []

        for bottleneck in bottlenecks:
            metric = bottleneck["metric"]
            severity = bottleneck["severity"]

            adaptation = {
                "target_metric": metric,
                "adaptation_type": "optimization",
                "severity": severity,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            if metric == "response_time":
                adaptation["action"] = "increase_parallel_processing"
            elif metric == "memory_efficiency":
                adaptation["action"] = "optimize_memory_usage"
            elif metric == "cognitive_load":
                adaptation["action"] = "reduce_cognitive_complexity"
            elif metric == "accuracy":
                adaptation["action"] = "enhance_reasoning_precision"

            adaptations.append(adaptation)
            logger.info(f"Applied adaptation: {adaptation['action']} for {metric}")

        return adaptations

    async def reflect_on_processing(
        self,
        input_data,
        context: dict[str, Any],
        processing_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Reflect on current processing to provide meta-cognitive insights

        Args:
            input_data: The original input being processed
            context: Processing context
            processing_result: Current processing results to reflect on

        Returns:
            Meta-cognitive reflection results
        """
        try:
            # Create interaction record for this processing
            interaction_record = {
                "input_data": str(input_data)[:200],  # Truncate for storage
                "context": context,
                "processing_status": processing_result.get("status", "unknown"),
                "timestamp": datetime.datetime.now().isoformat(),
                "metrics": {
                    "processing_time": processing_result.get("processing_time", 0),
                    "complexity": self._assess_complexity(input_data),
                    "context_richness": len(context),
                    "success": processing_result.get("status") == "completed",
                },
            }

            # Log the interaction
            self.log_interaction(interaction_record)

            # Generate immediate reflection
            reflection = {
                "awareness_level": self._calculate_awareness_level(processing_result),
                "processing_quality": self._assess_processing_quality(
                    processing_result
                ),
                "learning_opportunities": self._identify_learning_opportunities(
                    input_data, context, processing_result
                ),
                "cognitive_load": self._estimate_cognitive_load(context),
                "adaptation_suggestions": self._generate_adaptation_suggestions(
                    processing_result
                ),
                "meta_timestamp": datetime.datetime.now().isoformat(),
            }

            return reflection

        except Exception as e:
            logger.error(f"Meta-cognitive reflection failed: {e}")
            return {
                "awareness_level": 0.5,
                "error": str(e),
                "reflection_status": "failed",
            }

    def _assess_complexity(self, input_data) -> float:
        """Assess the complexity of input data"""
        data_str = str(input_data)
        # Simple complexity assessment based on length, nested structures, etc.
        base_complexity = min(1.0, len(data_str) / 1000.0)  # Length factor

        # Check for nested structures
        nesting_factor = data_str.count("{") + data_str.count("[") + data_str.count("(")
        nesting_complexity = min(0.5, nesting_factor / 20.0)

        return min(1.0, base_complexity + nesting_complexity)

    def _calculate_awareness_level(self, processing_result: dict[str, Any]) -> float:
        """Calculate the system's awareness level of its processing"""
        # Base awareness on successful component integration
        agi_enhancements = processing_result.get("agi_enhancements", {})
        component_count = len(agi_enhancements)

        # More components involved = higher awareness
        base_awareness = min(0.9, component_count / 8.0)  # Max at 8 components

        # Boost for successful processing
        if processing_result.get("status") == "completed":
            base_awareness += 0.1

        return min(1.0, base_awareness)

    def _assess_processing_quality(self, processing_result: dict[str, Any]) -> float:
        """Assess the quality of processing"""
        if processing_result.get("status") == "error":
            return 0.2
        elif processing_result.get("status") == "completed":
            # Check for comprehensive results
            agi_summary = processing_result.get("agi_summary", {})
            overall_score = agi_summary.get("overall_score", 0.5)
            return overall_score
        else:
            return 0.5

    def _identify_learning_opportunities(
        self,
        input_data,
        context: dict[str, Any],
        processing_result: dict[str, Any],
    ) -> list[str]:
        """Identify opportunities for learning and improvement"""
        opportunities = []

        # Check for errors or warnings
        if processing_result.get("status") == "error":
            opportunities.append("error_handling_improvement")

        if processing_result.get("ethical_warnings"):
            opportunities.append("ethical_reasoning_refinement")

        # Check for missing components
        agi_enhancements = processing_result.get("agi_enhancements", {})
        expected_components = ["compliance", "ethics", "memory", "prediction"]

        for component in expected_components:
            if component not in agi_enhancements:
                opportunities.append(f"{component}_integration_enhancement")

        # Learning from context richness
        if len(context) > 5:
            opportunities.append("context_utilization_optimization")

        return opportunities

    def _estimate_cognitive_load(self, context: dict[str, Any]) -> float:
        """Estimate the cognitive load of current processing"""
        # Base load on context complexity
        base_load = min(0.8, len(context) / 10.0)

        # Increase load for governance requirements
        if context.get("requires_governance"):
            base_load += 0.2

        # Increase load for emergency situations
        if context.get("emergency_mode"):
            base_load += 0.3

        return min(1.0, base_load)

    def _generate_adaptation_suggestions(
        self, processing_result: dict[str, Any]
    ) -> list[str]:
        """Generate suggestions for system adaptation"""
        suggestions = []

        # Performance-based suggestions
        processing_time = processing_result.get("processing_time", 0)
        if processing_time > 1.0:  # More than 1 second
            suggestions.append("optimize_processing_pipeline")

        # Integration-based suggestions
        agi_summary = processing_result.get("agi_summary", {})
        overall_score = agi_summary.get("overall_score", 0.5)

        if overall_score < 0.7:
            suggestions.append("enhance_component_coordination")

        recommendations = agi_summary.get("recommendations", [])
        if recommendations:
            suggestions.append("implement_agi_recommendations")

        return suggestions
