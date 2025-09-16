"""
Symbolic Pattern Analyzer
=========================

Analyzes ΛTRACE symbolic data to identify patterns and behaviors.
Used for insights, recommendations, and anomaly detection.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics
import hashlib

logger = logging.getLogger(__name__)


class SymbolicPatternAnalyzer:
    """Analyze symbolic trace patterns"""

    def __init__(self, config):
        self.config = config
        self.pattern_cache = {}
        self.baseline_patterns = {}
        self.anomaly_threshold = config.get("anomaly_threshold", 0.7)
        self.pattern_window = config.get("pattern_window", 100)

    def analyze_patterns(self, trace_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze symbolic patterns in trace data"""
        if not trace_data:
            return {"status": "no_data", "patterns": []}

        try:
            patterns = {
                "temporal_patterns": self._analyze_temporal_patterns(trace_data),
                "frequency_patterns": self._analyze_frequency_patterns(trace_data),
                "sequence_patterns": self._analyze_sequence_patterns(trace_data),
                "interaction_patterns": self._analyze_interaction_patterns(trace_data),
                "symbolic_patterns": self._analyze_symbolic_patterns(trace_data)
            }

            # Calculate pattern confidence scores
            pattern_scores = {}
            for pattern_type, pattern_data in patterns.items():
                pattern_scores[pattern_type] = self._calculate_pattern_confidence(pattern_data)

            return {
                "status": "success",
                "patterns": patterns,
                "pattern_scores": pattern_scores,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "trace_count": len(trace_data)
            }

        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "patterns": []
            }

    def _analyze_temporal_patterns(self, trace_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in user activity"""
        timestamps = []
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)

        for trace in trace_data:
            timestamp = trace.get("timestamp")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamps.append(dt)
                    hourly_activity[dt.hour] += 1
                    daily_activity[dt.strftime('%A')] += 1
                except Exception:
                    continue

        if not timestamps:
            return {"status": "no_timestamps"}

        # Calculate activity patterns
        peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_days = sorted(daily_activity.items(), key=lambda x: x[1], reverse=True)[:3]

        # Calculate session patterns
        session_gaps = []
        for i in range(1, len(timestamps)):
            gap = (timestamps[i] - timestamps[i-1]).total_seconds() / 60  # minutes
            session_gaps.append(gap)

        avg_session_gap = statistics.mean(session_gaps) if session_gaps else 0

        return {
            "peak_hours": peak_hours,
            "peak_days": peak_days,
            "avg_session_gap_minutes": avg_session_gap,
            "total_sessions": len([gap for gap in session_gaps if gap > 30]),  # 30+ min gaps = new session
            "activity_regularity": self._calculate_regularity(hourly_activity)
        }

    def _analyze_frequency_patterns(self, trace_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze frequency patterns of actions and symbols"""
        action_counts = Counter()
        symbol_counts = Counter()
        trace_type_counts = Counter()

        for trace in trace_data:
            action = trace.get("action")
            symbol_id = trace.get("symbol_id")
            trace_type = trace.get("trace_type")

            if action:
                action_counts[action] += 1
            if symbol_id:
                symbol_counts[symbol_id] += 1
            if trace_type:
                trace_type_counts[trace_type] += 1

        return {
            "top_actions": action_counts.most_common(10),
            "top_symbols": symbol_counts.most_common(10),
            "trace_types": trace_type_counts.most_common(),
            "action_diversity": len(action_counts),
            "symbol_diversity": len(symbol_counts)
        }

    def _analyze_sequence_patterns(self, trace_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze action sequences and transitions"""
        sequences = []
        transitions = defaultdict(int)

        # Extract action sequences
        actions = [trace.get("action") for trace in trace_data if trace.get("action")]

        # Build n-grams (2-grams and 3-grams)
        bigrams = []
        trigrams = []

        for i in range(len(actions) - 1):
            if i < len(actions) - 1:
                bigrams.append((actions[i], actions[i + 1]))
                transitions[f"{actions[i]} -> {actions[i + 1]}"] += 1

            if i < len(actions) - 2:
                trigrams.append((actions[i], actions[i + 1], actions[i + 2]))

        bigram_counts = Counter(bigrams)
        trigram_counts = Counter(trigrams)

        return {
            "common_bigrams": bigram_counts.most_common(10),
            "common_trigrams": trigram_counts.most_common(10),
            "transition_patterns": dict(Counter(transitions).most_common(15)),
            "sequence_complexity": len(set(bigrams)) / max(len(bigrams), 1)
        }

    def _analyze_interaction_patterns(self, trace_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze interaction patterns with system components"""
        component_interactions = defaultdict(int)
        success_rates = defaultdict(list)
        response_times = defaultdict(list)

        for trace in trace_data:
            component = trace.get("component", "unknown")
            success = trace.get("success", True)
            response_time = trace.get("response_time", 0)

            component_interactions[component] += 1
            success_rates[component].append(1 if success else 0)

            if response_time > 0:
                response_times[component].append(response_time)

        # Calculate metrics
        component_success_rates = {}
        component_avg_response_times = {}

        for component in component_interactions:
            if success_rates[component]:
                component_success_rates[component] = statistics.mean(success_rates[component])
            if response_times[component]:
                component_avg_response_times[component] = statistics.mean(response_times[component])

        return {
            "component_interactions": dict(component_interactions),
            "success_rates": component_success_rates,
            "avg_response_times": component_avg_response_times,
            "most_used_components": sorted(component_interactions.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    def _analyze_symbolic_patterns(self, trace_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze symbolic and governance-related patterns"""
        governance_actions = []
        ethical_scores = []
        drift_scores = []
        compliance_events = []

        for trace in trace_data:
            metadata = trace.get("metadata", {})

            if trace.get("action_type") == "governance":
                governance_actions.append(trace.get("action"))

            if "ethical_score" in metadata:
                try:
                    ethical_scores.append(float(metadata["ethical_score"]))
                except (ValueError, TypeError):
                    pass

            if "drift_score" in metadata:
                try:
                    drift_scores.append(float(metadata["drift_score"]))
                except (ValueError, TypeError):
                    pass

            if metadata.get("compliance_check"):
                compliance_events.append(metadata["compliance_check"])

        return {
            "governance_actions": Counter(governance_actions).most_common(),
            "avg_ethical_score": statistics.mean(ethical_scores) if ethical_scores else None,
            "avg_drift_score": statistics.mean(drift_scores) if drift_scores else None,
            "compliance_events": Counter(compliance_events).most_common(),
            "ethical_score_trend": self._calculate_trend(ethical_scores),
            "drift_score_trend": self._calculate_trend(drift_scores)
        }

    def _calculate_pattern_confidence(self, pattern_data: Dict[str, Any]) -> float:
        """Calculate confidence score for pattern data"""
        if not pattern_data or pattern_data.get("status") == "no_data":
            return 0.0

        # Simple confidence calculation based on data completeness and consistency
        confidence_factors = []

        # Check data completeness
        non_empty_fields = sum(1 for v in pattern_data.values() if v)
        total_fields = len(pattern_data)
        completeness = non_empty_fields / max(total_fields, 1)
        confidence_factors.append(completeness)

        # Check for patterns in lists
        for value in pattern_data.values():
            if isinstance(value, list) and len(value) > 0:
                confidence_factors.append(0.8)
            elif isinstance(value, dict) and len(value) > 0:
                confidence_factors.append(0.7)

        return statistics.mean(confidence_factors) if confidence_factors else 0.5

    def _calculate_regularity(self, activity_data: Dict) -> float:
        """Calculate activity regularity score"""
        if not activity_data:
            return 0.0

        values = list(activity_data.values())
        if len(values) < 2:
            return 0.0

        # Lower standard deviation = higher regularity
        std_dev = statistics.stdev(values)
        mean_val = statistics.mean(values)

        # Normalize to 0-1 scale
        regularity = max(0, 1 - (std_dev / max(mean_val, 1)))
        return regularity

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values"""
        if len(values) < 2:
            return "insufficient_data"

        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]

        if not first_half or not second_half:
            return "insufficient_data"

        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)

        if second_avg > first_avg * 1.1:
            return "increasing"
        elif second_avg < first_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    def detect_anomalies(self, user_patterns: Dict[str, Any], current_activity: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect anomalous activity patterns"""
        if not user_patterns or not current_activity:
            return {"status": "insufficient_data", "anomalies": []}

        try:
            anomalies = []

            # Analyze current activity patterns
            current_patterns = self.analyze_patterns(current_activity)

            if current_patterns["status"] != "success":
                return {"status": "analysis_failed", "anomalies": []}

            # Compare against baseline patterns
            for pattern_type, current_pattern in current_patterns["patterns"].items():
                baseline_pattern = user_patterns.get("patterns", {}).get(pattern_type, {})

                if baseline_pattern:
                    anomaly_score = self._compare_patterns(baseline_pattern, current_pattern)

                    if anomaly_score > self.anomaly_threshold:
                        anomalies.append({
                            "type": pattern_type,
                            "anomaly_score": anomaly_score,
                            "description": f"Unusual {pattern_type.replace('_', ' ')} detected",
                            "current_pattern": current_pattern,
                            "baseline_pattern": baseline_pattern
                        })

            return {
                "status": "success",
                "anomalies": anomalies,
                "anomaly_count": len(anomalies),
                "overall_anomaly_score": statistics.mean([a["anomaly_score"] for a in anomalies]) if anomalies else 0.0
            }

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "anomalies": []
            }

    def _compare_patterns(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> float:
        """Compare two pattern dictionaries and return anomaly score"""
        differences = []

        # Compare numerical values
        for key in baseline:
            if key in current:
                baseline_val = baseline[key]
                current_val = current[key]

                if isinstance(baseline_val, (int, float)) and isinstance(current_val, (int, float)):
                    if baseline_val != 0:
                        diff = abs(current_val - baseline_val) / abs(baseline_val)
                        differences.append(min(diff, 2.0))  # Cap at 200% difference

        # Compare list/dict structures
        for key in baseline:
            if key in current and isinstance(baseline[key], (list, dict)):
                baseline_size = len(baseline[key]) if baseline[key] else 0
                current_size = len(current[key]) if current[key] else 0

                if baseline_size > 0:
                    size_diff = abs(current_size - baseline_size) / baseline_size
                    differences.append(min(size_diff, 1.0))

        return statistics.mean(differences) if differences else 0.0

    def generate_insights(self, user_id: str, analysis_period: int = 30) -> Dict[str, Any]:
        """Generate behavioral insights from patterns"""
        try:
            # This would typically fetch user trace data for the analysis period
            # For now, we'll generate insights based on cached patterns

            insights = {
                "user_id": user_id,
                "analysis_period_days": analysis_period,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "insights": []
            }

            # Check if we have cached patterns for this user
            user_pattern_key = f"user_{user_id}_patterns"
            if user_pattern_key in self.pattern_cache:
                patterns = self.pattern_cache[user_pattern_key]

                # Generate activity insights
                temporal_patterns = patterns.get("patterns", {}).get("temporal_patterns", {})
                if temporal_patterns:
                    insights["insights"].extend(self._generate_temporal_insights(temporal_patterns))

                # Generate frequency insights
                frequency_patterns = patterns.get("patterns", {}).get("frequency_patterns", {})
                if frequency_patterns:
                    insights["insights"].extend(self._generate_frequency_insights(frequency_patterns))

                # Generate interaction insights
                interaction_patterns = patterns.get("patterns", {}).get("interaction_patterns", {})
                if interaction_patterns:
                    insights["insights"].extend(self._generate_interaction_insights(interaction_patterns))

                # Generate security insights
                symbolic_patterns = patterns.get("patterns", {}).get("symbolic_patterns", {})
                if symbolic_patterns:
                    insights["insights"].extend(self._generate_security_insights(symbolic_patterns))

            else:
                insights["insights"].append({
                    "type": "no_data",
                    "priority": "info",
                    "message": "Insufficient data for insight generation. Please use the system more to build behavioral patterns."
                })

            return insights

        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return {
                "user_id": user_id,
                "status": "error",
                "error": str(e),
                "insights": []
            }

    def _generate_temporal_insights(self, temporal_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from temporal patterns"""
        insights = []

        peak_hours = temporal_patterns.get("peak_hours", [])
        if peak_hours:
            top_hour = peak_hours[0][0]
            insights.append({
                "type": "temporal_pattern",
                "priority": "info",
                "message": f"Most active during hour {top_hour}:00. Consider scheduling important tasks during this time.",
                "data": {"peak_hour": top_hour}
            })

        regularity = temporal_patterns.get("activity_regularity", 0)
        if regularity > 0.8:
            insights.append({
                "type": "behavior_pattern",
                "priority": "positive",
                "message": "Highly regular activity pattern detected. This suggests good routine establishment.",
                "data": {"regularity_score": regularity}
            })
        elif regularity < 0.3:
            insights.append({
                "type": "behavior_pattern",
                "priority": "suggestion",
                "message": "Irregular activity pattern. Consider establishing a more consistent routine for better productivity.",
                "data": {"regularity_score": regularity}
            })

        return insights

    def _generate_frequency_insights(self, frequency_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from frequency patterns"""
        insights = []

        action_diversity = frequency_patterns.get("action_diversity", 0)
        if action_diversity > 20:
            insights.append({
                "type": "usage_pattern",
                "priority": "info",
                "message": f"High action diversity ({action_diversity} different actions). You're exploring many system features.",
                "data": {"action_diversity": action_diversity}
            })

        top_actions = frequency_patterns.get("top_actions", [])
        if top_actions and len(top_actions) > 0:
            most_common = top_actions[0]
            insights.append({
                "type": "usage_pattern",
                "priority": "info",
                "message": f"Most frequent action: '{most_common[0]}' ({most_common[1]} times)",
                "data": {"top_action": most_common[0], "frequency": most_common[1]}
            })

        return insights

    def _generate_interaction_insights(self, interaction_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from interaction patterns"""
        insights = []

        success_rates = interaction_patterns.get("success_rates", {})
        for component, rate in success_rates.items():
            if rate < 0.8:
                insights.append({
                    "type": "performance_issue",
                    "priority": "warning",
                    "message": f"Low success rate with {component} ({rate:.1%}). Consider reviewing usage or reporting issues.",
                    "data": {"component": component, "success_rate": rate}
                })

        response_times = interaction_patterns.get("avg_response_times", {})
        for component, time in response_times.items():
            if time > 5.0:  # 5 seconds
                insights.append({
                    "type": "performance_issue",
                    "priority": "suggestion",
                    "message": f"Slow response times with {component} ({time:.1f}s average). Performance optimization may be needed.",
                    "data": {"component": component, "avg_response_time": time}
                })

        return insights

    def _generate_security_insights(self, symbolic_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security and governance insights"""
        insights = []

        drift_trend = symbolic_patterns.get("drift_score_trend")
        if drift_trend == "increasing":
            insights.append({
                "type": "security_concern",
                "priority": "warning",
                "message": "Increasing drift scores detected. System behavior may be becoming less predictable.",
                "data": {"trend": drift_trend}
            })

        ethical_score = symbolic_patterns.get("avg_ethical_score")
        if ethical_score is not None and ethical_score < 0.6:
            insights.append({
                "type": "ethical_concern",
                "priority": "warning",
                "message": f"Lower than expected ethical scores ({ethical_score:.2f}). Review recent actions for compliance.",
                "data": {"avg_ethical_score": ethical_score}
            })

        governance_actions = symbolic_patterns.get("governance_actions", [])
        if governance_actions:
            insights.append({
                "type": "governance_activity",
                "priority": "info",
                "message": f"Governance actions detected: {len(governance_actions)} different types",
                "data": {"governance_action_types": len(governance_actions)}
            })

        return insights
