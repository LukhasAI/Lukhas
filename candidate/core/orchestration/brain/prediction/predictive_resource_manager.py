from datetime import datetime, timezone
"""
Predictive Resource Manager for lukhas AI

This module provides predictive modeling and resource management capabilities
to anticipate system needs and optimize performance proactively.

Based on the advanced implementation from Lukhas GitHub repository.
"""

import datetime
import logging
import statistics
from collections import defaultdict, deque
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ResourceType:
    """Resource type enumeration"""

    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    COGNITIVE_LOAD = "cognitive_load"


class PredictionModel:
    """Simple prediction model for resource usage"""

    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.data_points = deque(maxlen=window_size)
        self.model_accuracy = 0.0

    def add_data_point(self, value: float, timestamp: Optional[str] = None):
        """Add a new data point to the model"""
        if timestamp is None:
            timestamp = datetime.datetime.now(timezone.utc).isoformat()

        self.data_points.append({"value": value, "timestamp": timestamp})

    def predict_next(self) -> Optional[float]:
        """Predict the next value based on historical data"""
        if len(self.data_points) < 3:
            return None

        values = [point["value"] for point in self.data_points]

        # Simple trend-based prediction
        if len(values) >= 3:
            # Calculate linear trend
            recent_values = values[-5:]  # Use last 5 points
            trend = self._calculate_trend(recent_values)

            # Predict next value
            last_value = values[-1]
            predicted = last_value + trend

            # Ensure reasonable bounds
            return max(0.0, min(100.0, predicted))

        return statistics.mean(values)

    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend from a series of values"""
        if len(values) < 2:
            return 0.0

        # Simple linear regression slope
        n = len(values)
        x_values = list(range(n))

        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0

        return (n * sum_xy - sum_x * sum_y) / denominator


class PredictiveResourceManager:
    """
    Advanced resource manager that predicts future resource needs
    and optimizes allocation proactively.
    """

    def __init__(self):
        self.prediction_models = {}
        self.resource_history = defaultdict(list)
        self.allocation_strategies = {}
        self.optimization_rules = {}
        self.prediction_horizon = 300  # seconds
        self.stats = {
            "predictions_made": 0,
            "optimizations_applied": 0,
            "accuracy_score": 0.0,
            "last_prediction": None,
            "total_resources_managed": 0,
        }

        # Initialize prediction models for each resource type
        self._initialize_prediction_models()

        # Initialize optimization strategies
        self._initialize_optimization_strategies()

        logger.info("Predictive Resource Manager initialized")

    def _initialize_prediction_models(self):
        """Initialize prediction models for different resource types"""
        resource_types = [
            ResourceType.CPU,
            ResourceType.MEMORY,
            ResourceType.STORAGE,
            ResourceType.NETWORK,
            ResourceType.COGNITIVE_LOAD,
        ]

        for resource_type in resource_types:
            self.prediction_models[resource_type] = PredictionModel()

    def _initialize_optimization_strategies(self):
        """Initialize optimization strategies for different scenarios"""
        self.optimization_rules = {
            ResourceType.CPU: {
                "high_usage_threshold": 80.0,
                "critical_threshold": 95.0,
                "optimization_actions": [
                    "reduce_parallel_processing",
                    "defer_non_critical_tasks",
                    "enable_cpu_boost_mode",
                ],
            },
            ResourceType.MEMORY: {
                "high_usage_threshold": 85.0,
                "critical_threshold": 95.0,
                "optimization_actions": [
                    "garbage_collection",
                    "memory_consolidation",
                    "cache_optimization",
                ],
            },
            ResourceType.COGNITIVE_LOAD: {
                "high_usage_threshold": 75.0,
                "critical_threshold": 90.0,
                "optimization_actions": [
                    "reduce_cognitive_complexity",
                    "prioritize_critical_decisions",
                    "defer_learning_tasks",
                ],
            },
        }

    def update_resource_usage(
        self,
        resource_type: str,
        usage_value: float,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update current resource usage and trigger prediction

        Args:
            resource_type: Type of resource (CPU, memory, etc.)
            usage_value: Current usage value (0-100 scale)
            metadata: Additional context about the usage
        """
        timestamp = datetime.datetime.now(timezone.utc).isoformat()

        # Record usage in history
        usage_record = {
            "value": usage_value,
            "timestamp": timestamp,
            "metadata": metadata or {},
        }

        self.resource_history[resource_type].append(usage_record)

        # Update prediction model
        if resource_type in self.prediction_models:
            self.prediction_models[resource_type].add_data_point(usage_value, timestamp)

        # Check if optimization is needed
        self._check_optimization_needed(resource_type, usage_value)

        self.stats["total_resources_managed"] += 1

    def predict_resource_needs(self, resource_type: str, time_horizon: Optional[int] = None) -> dict:
        """
        Predict future resource needs for a specific resource type

        Args:
            resource_type: Type of resource to predict
            time_horizon: Prediction horizon in seconds (optional)

        Returns:
            Dictionary containing prediction results
        """
        if time_horizon is None:
            time_horizon = self.prediction_horizon

        if resource_type not in self.prediction_models:
            return {
                "error": f"No prediction model available for {resource_type}",
                "resource_type": resource_type,
            }

        model = self.prediction_models[resource_type]
        predicted_value = model.predict_next()

        if predicted_value is None:
            return {
                "error": "Insufficient data for prediction",
                "resource_type": resource_type,
            }

        # Generate prediction metadata
        current_time = datetime.datetime.now(timezone.utc)
        prediction_time = current_time + datetime.timedelta(seconds=time_horizon)

        # Assess prediction confidence
        confidence = self._calculate_prediction_confidence(resource_type)

        # Determine risk level
        risk_level = self._assess_risk_level(resource_type, predicted_value)

        # Generate recommendations
        recommendations = self._generate_recommendations(resource_type, predicted_value, risk_level)

        prediction = {
            "resource_type": resource_type,
            "predicted_value": predicted_value,
            "confidence": confidence,
            "risk_level": risk_level,
            "prediction_horizon": time_horizon,
            "prediction_time": prediction_time.isoformat(),
            "recommendations": recommendations,
            "timestamp": current_time.isoformat(),
        }

        self.stats["predictions_made"] += 1
        self.stats["last_prediction"] = prediction

        logger.debug(
            "Generated prediction for %s: %.2f (confidence: %.2f)",
            resource_type,
            predicted_value,
            confidence,
        )

        return prediction

    async def predict_resource_needs(
        self,
        input_data,
        context: dict[str, Any],
        processing_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Predict resource needs based on input data, context, and current processing

        Args:
            input_data: The input being processed
            context: Processing context
            processing_result: Current processing results

        Returns:
            Predictive analysis and resource recommendations
        """
        try:
            # Analyze current resource usage from processing
            current_usage = self._analyze_current_usage(input_data, context, processing_result)

            # Update resource models with current data
            for resource_type, usage in current_usage.items():
                if resource_type in self.resource_models:
                    self.resource_models[resource_type].add_data_point(usage)

            # Generate predictions for each resource type
            predictions = {}
            for resource_type, model in self.resource_models.items():
                predicted_value = model.predict_next()
                if predicted_value is not None:
                    predictions[resource_type] = {
                        "predicted_usage": predicted_value,
                        "current_usage": current_usage.get(resource_type, 0.0),
                        "trend": (
                            "increasing"
                            if predicted_value > current_usage.get(resource_type, 0.0)
                            else "stable_or_decreasing"
                        ),
                        "confidence": self._calculate_prediction_confidence(model),
                    }

            # Analyze processing complexity for future resource planning
            complexity_analysis = self._analyze_processing_complexity(processing_result)

            # Generate resource recommendations
            recommendations = self._generate_resource_recommendations(predictions, complexity_analysis)

            # Calculate overall prediction accuracy
            overall_accuracy = self._calculate_overall_accuracy()

            predictive_insights = {
                "accuracy": overall_accuracy,
                "resource_predictions": predictions,
                "complexity_analysis": complexity_analysis,
                "recommendations": recommendations,
                "risk_level": self._assess_resource_risk(predictions),
                "optimization_opportunities": self._identify_optimization_opportunities(predictions),
                "prediction_timestamp": datetime.datetime.now(timezone.utc).isoformat(),
            }

            return {
                "status": "success",
                "predictive_analysis": predictive_insights,
                "enhancement_applied": True,
            }

        except Exception as e:
            logger.error(f"Predictive analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "enhancement_applied": False,
            }

    def _analyze_current_usage(
        self,
        input_data,
        context: dict[str, Any],
        processing_result: dict[str, Any],
    ) -> dict[str, float]:
        """Analyze current resource usage from processing data"""
        usage = {}

        # CPU usage estimate based on processing time
        processing_time = processing_result.get("processing_time", 0.0)
        usage[ResourceType.CPU] = min(100.0, processing_time * 20.0)  # Scale processing time to CPU %

        # Memory usage estimate based on data size and complexity
        data_size = len(str(input_data))
        context_size = len(str(context))
        usage[ResourceType.MEMORY] = min(100.0, (data_size + context_size) / 1000.0)  # Scale to memory %

        # Cognitive load estimate based on component usage
        agi_enhancements = processing_result.get("agi_enhancements", {})
        component_count = len(agi_enhancements)
        usage[ResourceType.COGNITIVE_LOAD] = min(100.0, component_count * 12.5)  # 8 components = 100%

        # Network usage estimate (simplified)
        usage[ResourceType.NETWORK] = 10.0  # Base network usage

        return usage

    def _calculate_prediction_confidence(self, model: PredictionModel) -> float:
        """Calculate confidence in a prediction model"""
        if len(model.data_points) < 5:
            return 0.3  # Low confidence with little data

        # Base confidence on data consistency and model accuracy
        values = [point["value"] for point in model.data_points]
        variance = statistics.variance(values) if len(values) > 1 else 0

        # Lower variance = higher confidence
        confidence = max(0.1, min(0.95, 1.0 - (variance / 1000.0)))

        return confidence

    def _analyze_processing_complexity(self, processing_result: dict[str, Any]) -> dict[str, Any]:
        """Analyze the complexity of current processing"""
        complexity = {
            "component_complexity": 0.0,
            "integration_complexity": 0.0,
            "error_complexity": 0.0,
        }

        # Component complexity based on AI enhancements
        agi_enhancements = processing_result.get("agi_enhancements", {})
        complexity["component_complexity"] = len(agi_enhancements) / 8.0  # Normalize to 0-1

        # Integration complexity based on AI summary
        agi_summary = processing_result.get("agi_summary", {})
        if agi_summary.get("integration_complete"):
            complexity["integration_complexity"] = agi_summary.get("overall_score", 0.5)

        # Error complexity
        if processing_result.get("status") == "error":
            complexity["error_complexity"] = 1.0

        return complexity

    def _generate_resource_recommendations(self, predictions: dict, complexity_analysis: dict) -> list[str]:
        """Generate resource management recommendations"""
        recommendations = []

        # Check for high predicted usage
        for resource_type, prediction in predictions.items():
            predicted_usage = prediction["predicted_usage"]
            if predicted_usage > 80.0:
                recommendations.append(f"Consider optimizing {resource_type} usage - high load predicted")

        # Check for increasing trends
        increasing_resources = [
            resource_type for resource_type, prediction in predictions.items() if prediction["trend"] == "increasing"
        ]
        if len(increasing_resources) > 2:
            recommendations.append("Multiple resource types showing increasing demand - consider system optimization")

        # Complexity-based recommendations
        if complexity_analysis["component_complexity"] > 0.8:
            recommendations.append("High component complexity detected - consider processing optimization")

        return recommendations

    def _assess_resource_risk(self, predictions: dict) -> str:
        """Assess overall resource risk level"""
        high_usage_count = sum(1 for prediction in predictions.values() if prediction["predicted_usage"] > 80.0)

        if high_usage_count >= 3:
            return "high"
        elif high_usage_count >= 1:
            return "medium"
        else:
            return "low"

    def _identify_optimization_opportunities(self, predictions: dict) -> list[str]:
        """Identify opportunities for resource optimization"""
        opportunities = []

        # Look for stable or decreasing usage
        stable_resources = [
            resource_type
            for resource_type, prediction in predictions.items()
            if prediction["trend"] == "stable_or_decreasing" and prediction["current_usage"] < 50.0
        ]

        if stable_resources:
            opportunities.append(f"Underutilized resources: {', '.join(stable_resources)}")

        # Look for highly variable usage (optimization potential)
        variable_resources = [
            resource_type for resource_type, prediction in predictions.items() if prediction["confidence"] < 0.6
        ]

        if variable_resources:
            opportunities.append(
                f"Variable usage patterns in: {', '.join(variable_resources)} - potential for optimization"
            )

        return opportunities

    def _calculate_overall_accuracy(self) -> float:
        """Calculate overall prediction accuracy across all models"""
        accuracies = []
        for model in self.resource_models.values():
            if hasattr(model, "model_accuracy"):
                accuracies.append(model.model_accuracy)

        return statistics.mean(accuracies) if accuracies else 0.5

    def predict_all_resources(self) -> dict:
        """
        Predict needs for all resource types

        Returns:
            Dictionary containing predictions for all resources
        """
        predictions = {}
        overall_risk = "low"
        critical_resources = []

        for resource_type in self.prediction_models:
            prediction = self.predict_resource_needs(resource_type)
            predictions[resource_type] = prediction

            # Track critical resources
            if not prediction.get("error") and prediction.get("risk_level") == "critical":
                critical_resources.append(resource_type)
                overall_risk = "critical"
            elif not prediction.get("error") and prediction.get("risk_level") == "high" and overall_risk != "critical":
                overall_risk = "high"

        return {
            "predictions": predictions,
            "overall_risk": overall_risk,
            "critical_resources": critical_resources,
            "prediction_summary": self._generate_prediction_summary(predictions),
            "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        }

    def optimize_resource_allocation(self, resource_type: str, predicted_usage: float) -> dict:
        """
        Optimize resource allocation based on predictions

        Args:
            resource_type: Type of resource to optimize
            predicted_usage: Predicted usage level

        Returns:
            Dictionary containing optimization results
        """
        if resource_type not in self.optimization_rules:
            return {
                "error": f"No optimization rules defined for {resource_type}",
                "resource_type": resource_type,
            }

        rules = self.optimization_rules[resource_type]
        actions_taken = []

        # Determine optimization level needed
        if predicted_usage >= rules["critical_threshold"]:
            optimization_level = "critical"
        elif predicted_usage >= rules["high_usage_threshold"]:
            optimization_level = "high"
        else:
            optimization_level = "normal"

        # Apply optimization actions
        if optimization_level in ["high", "critical"]:
            for action in rules["optimization_actions"]:
                result = self._apply_optimization_action(resource_type, action, optimization_level)
                if result:
                    actions_taken.append(
                        {
                            "action": action,
                            "level": optimization_level,
                            "result": result,
                        }
                    )

        optimization_result = {
            "resource_type": resource_type,
            "predicted_usage": predicted_usage,
            "optimization_level": optimization_level,
            "actions_taken": actions_taken,
            "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        }

        if actions_taken:
            self.stats["optimizations_applied"] += len(actions_taken)
            logger.info(
                "Applied %d optimizations for %s (predicted usage: %.2f%%)",
                len(actions_taken),
                resource_type,
                predicted_usage,
            )

        return optimization_result

    def _check_optimization_needed(self, resource_type: str, current_usage: float) -> None:
        """Check if immediate optimization is needed"""
        if resource_type in self.optimization_rules:
            rules = self.optimization_rules[resource_type]

            if current_usage >= rules["critical_threshold"]:
                logger.warning(
                    "Critical resource usage detected for %s: %.2f%%",
                    resource_type,
                    current_usage,
                )
                self.optimize_resource_allocation(resource_type, current_usage)

    def _calculate_prediction_confidence(self, resource_type: str) -> float:
        """Calculate confidence in prediction based on data quality"""
        if resource_type not in self.prediction_models:
            return 0.0

        model = self.prediction_models[resource_type]
        data_points = len(model.data_points)

        if data_points < 5:
            return 0.3  # Low confidence with little data
        elif data_points < 20:
            return 0.6  # Medium confidence
        else:
            return 0.8  # High confidence with sufficient data

    def _assess_risk_level(self, resource_type: str, predicted_value: float) -> str:
        """Assess risk level based on predicted value"""
        if resource_type not in self.optimization_rules:
            return "unknown"

        rules = self.optimization_rules[resource_type]

        if predicted_value >= rules["critical_threshold"]:
            return "critical"
        elif predicted_value >= rules["high_usage_threshold"]:
            return "high"
        elif predicted_value >= 50.0:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, resource_type: str, predicted_value: float, risk_level: str) -> list[str]:
        """Generate recommendations based on prediction"""
        recommendations = []

        if risk_level == "critical":
            recommendations.extend(
                [
                    f"Immediate action required for {resource_type}",
                    "Consider scaling resources",
                    "Implement emergency optimization protocols",
                ]
            )
        elif risk_level == "high":
            recommendations.extend(
                [
                    f"Monitor {resource_type} closely",
                    "Prepare optimization strategies",
                    "Consider proactive scaling",
                ]
            )
        elif risk_level == "medium":
            recommendations.append(f"Normal monitoring for {resource_type}")
        else:
            recommendations.append(f"No immediate action needed for {resource_type}")

        return recommendations

    def _apply_optimization_action(self, resource_type: str, action: str, level: str) -> dict:
        """Apply a specific optimization action"""
        # This would integrate with actual system optimization mechanisms
        # For now, we simulate the action

        result = {
            "action": action,
            "level": level,
            "success": True,
            "estimated_improvement": self._estimate_improvement(action),
            "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "Applied optimization action: %s for %s (level: %s)",
            action,
            resource_type,
            level,
        )

        return result

    def _estimate_improvement(self, action: str) -> float:
        """Estimate the improvement from an optimization action"""
        # Simple heuristic for improvement estimation
        improvement_estimates = {
            "reduce_parallel_processing": 15.0,
            "defer_non_critical_tasks": 10.0,
            "enable_cpu_boost_mode": 5.0,
            "garbage_collection": 20.0,
            "memory_consolidation": 25.0,
            "cache_optimization": 12.0,
            "reduce_cognitive_complexity": 18.0,
            "prioritize_critical_decisions": 8.0,
            "defer_learning_tasks": 15.0,
        }

        return improvement_estimates.get(action, 5.0)

    def _generate_prediction_summary(self, predictions: dict) -> str:
        """Generate a human-readable summary of predictions"""
        high_risk_count = 0
        critical_risk_count = 0

        for prediction in predictions.values():
            if not prediction.get("error"):
                risk = prediction.get("risk_level", "unknown")
                if risk == "critical":
                    critical_risk_count += 1
                elif risk == "high":
                    high_risk_count += 1

        if critical_risk_count > 0:
            return f"Critical: {critical_risk_count} resources at critical risk"
        elif high_risk_count > 0:
            return f"Warning: {high_risk_count} resources at high risk"
        else:
            return "All resources within normal parameters"

    def get_prediction_statistics(self) -> dict:
        """
        Get comprehensive statistics about the prediction system

        Returns:
            Statistics dictionary
        """
        model_stats = {}
        for resource_type, model in self.prediction_models.items():
            model_stats[resource_type] = {
                "data_points": len(model.data_points),
                "model_accuracy": model.model_accuracy,
            }

        return {
            **self.stats,
            "model_statistics": model_stats,
            "active_models": len(self.prediction_models),
            "optimization_rules": len(self.optimization_rules),
            "prediction_horizon_seconds": self.prediction_horizon,
        }

    def analyze_resource_trends(self, resource_type: str, days: int = 7) -> dict:
        """
        Analyze resource usage trends over a specified period

        Args:
            resource_type: Type of resource to analyze
            days: Number of days to analyze

        Returns:
            Trend analysis results
        """
        if resource_type not in self.resource_history:
            return {"error": f"No history available for {resource_type}"}

        # Filter data for the specified period
        cutoff_time = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=days)
        recent_data = [
            record
            for record in self.resource_history[resource_type]
            if datetime.datetime.fromisoformat(record["timestamp"]) >= cutoff_time
        ]

        if not recent_data:
            return {"error": f"No recent data available for {resource_type}"}

        values = [record["value"] for record in recent_data]

        # Calculate trend statistics
        trend_analysis = {
            "resource_type": resource_type,
            "period_days": days,
            "data_points": len(values),
            "average_usage": statistics.mean(values),
            "peak_usage": max(values),
            "minimum_usage": min(values),
            "usage_variance": (statistics.variance(values) if len(values) > 1 else 0.0),
            "trend_direction": self._calculate_trend_direction(values),
            "volatility": self._calculate_volatility(values),
            "analysis_timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        }

        return trend_analysis

    def _calculate_trend_direction(self, values: list[float]) -> str:
        """Calculate overall trend direction"""
        if len(values) < 2:
            return "insufficient_data"

        # Compare first half with second half
        mid_point = len(values) // 2
        first_half_avg = statistics.mean(values[:mid_point])
        second_half_avg = statistics.mean(values[mid_point:])

        if second_half_avg > first_half_avg * 1.05:
            return "increasing"
        elif second_half_avg < first_half_avg * 0.95:
            return "decreasing"
        else:
            return "stable"

    def _calculate_volatility(self, values: list[float]) -> float:
        """Calculate volatility (coefficient of variation)"""
        if len(values) < 2:
            return 0.0

        mean_value = statistics.mean(values)
        if mean_value == 0:
            return 0.0

        std_dev = statistics.stdev(values)
        return std_dev / mean_value