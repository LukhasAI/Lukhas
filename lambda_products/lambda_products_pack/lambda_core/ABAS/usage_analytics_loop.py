"""
Usage Analytics Loop for ABAS
Continuous learning from user behavior to identify and fix pain points
"""

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AnalyticsMetric(Enum):
    """Types of analytics metrics tracked"""

    TASK_COMPLETION_TIME = "task_completion_time"
    ERROR_RATE = "error_rate"
    FEATURE_USAGE = "feature_usage"
    USER_FLOW = "user_flow"
    ABANDONMENT_RATE = "abandonment_rate"
    SEARCH_QUERIES = "search_queries"
    CLICK_PATTERNS = "click_patterns"
    SESSION_DURATION = "session_duration"
    BOUNCE_RATE = "bounce_rate"
    CONVERSION_RATE = "conversion_rate"


class PainPointSeverity(Enum):
    """Severity levels for pain points"""

    CRITICAL = "critical"  # Blocking users
    HIGH = "high"  # Major friction
    MEDIUM = "medium"  # Noticeable issues
    LOW = "low"  # Minor improvements
    INFO = "info"  # Insights only


class OptimizationType(Enum):
    """Types of optimizations"""

    UI_IMPROVEMENT = "ui_improvement"
    WORKFLOW_SIMPLIFICATION = "workflow_simplification"
    FEATURE_SURFACE = "feature_surface"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    ONBOARDING = "onboarding"
    ACCESSIBILITY = "accessibility"


@dataclass
class UsagePattern:
    """Pattern detected in usage data"""

    pattern_id: str
    pattern_type: str
    frequency: int
    users_affected: int
    first_detected: datetime
    last_occurrence: datetime
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class PainPoint:
    """Identified pain point"""

    pain_point_id: str
    description: str
    severity: PainPointSeverity
    location: str  # Where in the app
    impact_score: float  # 0-1 scale
    users_affected: int
    occurrences: int
    patterns: list[UsagePattern] = field(default_factory=list)
    suggested_fixes: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationRecommendation:
    """Recommendation for optimization"""

    recommendation_id: str
    optimization_type: OptimizationType
    title: str
    description: str
    expected_impact: str
    implementation_effort: str  # low, medium, high
    priority: int  # 1-10
    metrics_improvement: dict[str, float] = field(default_factory=dict)
    evidence: list[dict] = field(default_factory=list)


class UsageAnalyticsLoop:
    """
    Continuous analytics loop that learns from usage patterns
    and automatically identifies optimization opportunities
    """

    def __init__(self):
        self.usage_data: dict[str, list[dict]] = defaultdict(list)
        self.pain_points: dict[str, PainPoint] = {}
        self.usage_patterns: list[UsagePattern] = []
        self.recommendations: list[OptimizationRecommendation] = []
        self.metrics_history: dict[str, list[tuple[datetime, float]]] = defaultdict(list)

        # Thresholds for pain point detection
        self.thresholds = {
            "high_error_rate": 0.2,  # 20% errors
            "slow_task": 30.0,  # 30 seconds
            "high_abandonment": 0.3,  # 30% abandonment
            "low_feature_usage": 0.1,  # 10% usage
            "high_search_rate": 0.4,  # 40% sessions include search
            "short_session": 60.0,  # 1 minute sessions
            "high_bounce": 0.5,  # 50% bounce rate
        }

        # Learning parameters
        self.pattern_min_occurrences = 5
        self.pattern_min_users = 3
        self.recommendation_confidence_threshold = 0.7

    def track_usage_event(self, user_id: str, event_type: str, event_data: dict[str, Any]) -> None:
        """Track a usage event for analysis"""
        event = {
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": datetime.now(),
            "data": event_data,
        }

        self.usage_data[event_type].append(event)

        # Real-time pattern detection
        self._detect_patterns_realtime(event)

        # Update metrics
        self._update_metrics(event)

    def analyze_usage_patterns(self) -> dict[str, Any]:
        """
        Analyze all usage data to identify patterns and pain points
        """
        analysis = {
            "patterns": [],
            "pain_points": [],
            "metrics": {},
            "recommendations": [],
        }

        # Analyze different aspects
        task_patterns = self._analyze_task_patterns()
        error_patterns = self._analyze_error_patterns()
        navigation_patterns = self._analyze_navigation_patterns()
        feature_patterns = self._analyze_feature_usage()
        search_patterns = self._analyze_search_patterns()

        # Combine patterns
        all_patterns = task_patterns + error_patterns + navigation_patterns + feature_patterns + search_patterns

        # Filter significant patterns
        significant_patterns = self._filter_significant_patterns(all_patterns)
        analysis["patterns"] = significant_patterns

        # Identify pain points from patterns
        pain_points = self._identify_pain_points_from_patterns(significant_patterns)
        analysis["pain_points"] = pain_points

        # Calculate current metrics
        analysis["metrics"] = self._calculate_current_metrics()

        # Generate recommendations
        recommendations = self._generate_optimization_recommendations(pain_points)
        analysis["recommendations"] = recommendations

        # Store for future reference
        self.usage_patterns = significant_patterns
        self.pain_points = {pp.pain_point_id: pp for pp in pain_points}
        self.recommendations = recommendations

        return analysis

    def get_real_time_insights(self) -> dict[str, Any]:
        """Get real-time insights based on current data"""
        insights = {
            "current_issues": [],
            "trending_problems": [],
            "improving_areas": [],
            "alerts": [],
        }

        # Check for current issues
        current_metrics = self._calculate_current_metrics()

        # High error rate alert
        if current_metrics.get("error_rate", 0) > self.thresholds["high_error_rate"]:
            insights["alerts"].append(
                {
                    "type": "high_error_rate",
                    "severity": "critical",
                    "message": f"Error rate is {current_metrics['error_rate']:.1%}",
                    "action": "Investigate error causes immediately",
                }
            )

        # High abandonment alert
        if current_metrics.get("abandonment_rate", 0) > self.thresholds["high_abandonment"]:
            insights["alerts"].append(
                {
                    "type": "high_abandonment",
                    "severity": "high",
                    "message": f"Abandonment rate is {current_metrics['abandonment_rate']:.1%}",
                    "action": "Review user flow for friction points",
                }
            )

        # Trending problems (getting worse)
        trending = self._identify_trending_problems()
        insights["trending_problems"] = trending

        # Improving areas (getting better)
        improving = self._identify_improving_areas()
        insights["improving_areas"] = improving

        # Current active issues
        insights["current_issues"] = self._get_active_issues()

        return insights

    def generate_improvement_plan(self) -> list[dict[str, Any]]:
        """
        Generate prioritized improvement plan based on analytics
        """
        if not self.recommendations:
            self.analyze_usage_patterns()

        # Sort by priority and impact
        sorted_recs = sorted(
            self.recommendations,
            key=lambda r: (r.priority, -sum(r.metrics_improvement.values())),
            reverse=True,
        )

        improvement_plan = []

        for rec in sorted_recs[:10]:  # Top 10 improvements
            plan_item = {
                "id": rec.recommendation_id,
                "title": rec.title,
                "type": rec.optimization_type.value,
                "description": rec.description,
                "priority": rec.priority,
                "effort": rec.implementation_effort,
                "expected_impact": rec.expected_impact,
                "metrics_improvement": rec.metrics_improvement,
                "implementation_steps": self._generate_implementation_steps(rec),
                "success_criteria": self._generate_success_criteria(rec),
            }
            improvement_plan.append(plan_item)

        return improvement_plan

    def _detect_patterns_realtime(self, event: dict) -> None:
        """Detect patterns in real-time as events come in"""
        # Check for repeated errors
        if event["event_type"] == "error":
            self._check_error_pattern(event)

        # Check for search patterns
        elif event["event_type"] == "search":
            self._check_search_pattern(event)

        # Check for navigation loops
        elif event["event_type"] == "navigation":
            self._check_navigation_loop(event)

    def _update_metrics(self, event: dict) -> None:
        """Update metrics with new event"""
        timestamp = event["timestamp"]

        # Update relevant metrics based on event type
        if event["event_type"] == "error":
            self._update_error_metrics(timestamp)
        elif event["event_type"] == "task_complete":
            self._update_task_metrics(timestamp, event["data"])
        elif event["event_type"] == "session_end":
            self._update_session_metrics(timestamp, event["data"])

    def _analyze_task_patterns(self) -> list[UsagePattern]:
        """Analyze task completion patterns"""
        patterns = []

        task_events = self.usage_data.get("task_complete", [])
        if not task_events:
            return patterns

        # Group by task type
        tasks_by_type = defaultdict(list)
        for event in task_events:
            task_type = event["data"].get("task_type", "unknown")
            tasks_by_type[task_type].append(event)

        # Analyze each task type
        for task_type, events in tasks_by_type.items():
            if len(events) < self.pattern_min_occurrences:
                continue

            # Calculate statistics
            completion_times = [e["data"].get("duration", 0) for e in events]
            avg_time = statistics.mean(completion_times)

            # Check if slow
            if avg_time > self.thresholds["slow_task"]:
                pattern = UsagePattern(
                    pattern_id=f"slow_task_{task_type}",
                    pattern_type="slow_task",
                    frequency=len(events),
                    users_affected=len({e["user_id"] for e in events}),
                    first_detected=min(e["timestamp"] for e in events),
                    last_occurrence=max(e["timestamp"] for e in events),
                    context={
                        "task_type": task_type,
                        "avg_duration": avg_time,
                        "threshold": self.thresholds["slow_task"],
                    },
                )
                patterns.append(pattern)

        return patterns

    def _analyze_error_patterns(self) -> list[UsagePattern]:
        """Analyze error patterns"""
        patterns = []

        error_events = self.usage_data.get("error", [])
        if not error_events:
            return patterns

        # Group by error type
        errors_by_type = defaultdict(list)
        for event in error_events:
            error_type = event["data"].get("error_type", "unknown")
            errors_by_type[error_type].append(event)

        # Find recurring errors
        for error_type, events in errors_by_type.items():
            if len(events) < self.pattern_min_occurrences:
                continue

            pattern = UsagePattern(
                pattern_id=f"recurring_error_{error_type}",
                pattern_type="recurring_error",
                frequency=len(events),
                users_affected=len({e["user_id"] for e in events}),
                first_detected=min(e["timestamp"] for e in events),
                last_occurrence=max(e["timestamp"] for e in events),
                context={
                    "error_type": error_type,
                    "error_locations": list({e["data"].get("location", "") for e in events}),
                },
            )
            patterns.append(pattern)

        return patterns

    def _analyze_navigation_patterns(self) -> list[UsagePattern]:
        """Analyze navigation patterns"""
        patterns = []

        nav_events = self.usage_data.get("navigation", [])
        if not nav_events:
            return patterns

        # Detect circular navigation
        user_paths = defaultdict(list)
        for event in nav_events:
            user_paths[event["user_id"]].append(event["data"].get("page", ""))

        circular_count = 0
        users_with_circular = set()

        for user_id, path in user_paths.items():
            if self._has_circular_navigation(path):
                circular_count += 1
                users_with_circular.add(user_id)

        if circular_count >= self.pattern_min_occurrences:
            pattern = UsagePattern(
                pattern_id="circular_navigation",
                pattern_type="navigation_issue",
                frequency=circular_count,
                users_affected=len(users_with_circular),
                first_detected=min(e["timestamp"] for e in nav_events),
                last_occurrence=max(e["timestamp"] for e in nav_events),
                context={"issue": "Users navigating in circles"},
            )
            patterns.append(pattern)

        return patterns

    def _analyze_feature_usage(self) -> list[UsagePattern]:
        """Analyze feature usage patterns"""
        patterns = []

        feature_events = self.usage_data.get("feature_use", [])
        if not feature_events:
            return patterns

        # Count feature usage
        feature_counts = Counter(e["data"].get("feature", "") for e in feature_events)
        total_users = len({e["user_id"] for e in feature_events})

        # Find underused features
        for feature, count in feature_counts.items():
            usage_rate = count / total_users if total_users > 0 else 0

            if usage_rate < self.thresholds["low_feature_usage"]:
                pattern = UsagePattern(
                    pattern_id=f"underused_feature_{feature}",
                    pattern_type="low_adoption",
                    frequency=count,
                    users_affected=count,
                    first_detected=datetime.now(),
                    last_occurrence=datetime.now(),
                    context={
                        "feature": feature,
                        "usage_rate": usage_rate,
                        "threshold": self.thresholds["low_feature_usage"],
                    },
                )
                patterns.append(pattern)

        return patterns

    def _analyze_search_patterns(self) -> list[UsagePattern]:
        """Analyze search patterns"""
        patterns = []

        search_events = self.usage_data.get("search", [])
        if not search_events:
            return patterns

        # Analyze search queries
        queries = [e["data"].get("query", "") for e in search_events]
        query_counts = Counter(queries)

        # Find frequently searched items (indicating they're hard to find)
        for query, count in query_counts.most_common(10):
            if count >= self.pattern_min_occurrences:
                pattern = UsagePattern(
                    pattern_id=f"frequent_search_{query[:20]}",
                    pattern_type="frequent_search",
                    frequency=count,
                    users_affected=len({e["user_id"] for e in search_events if e["data"].get("query") == query}),
                    first_detected=min(e["timestamp"] for e in search_events if e["data"].get("query") == query),
                    last_occurrence=max(e["timestamp"] for e in search_events if e["data"].get("query") == query),
                    context={
                        "query": query,
                        "suggestion": f"Make '{query}' more discoverable",
                    },
                )
                patterns.append(pattern)

        return patterns

    def _filter_significant_patterns(self, patterns: list[UsagePattern]) -> list[UsagePattern]:
        """Filter patterns to keep only significant ones"""
        significant = []

        for pattern in patterns:
            # Check minimum thresholds
            if pattern.frequency >= self.pattern_min_occurrences and pattern.users_affected >= self.pattern_min_users:
                significant.append(pattern)

        return significant

    def _identify_pain_points_from_patterns(self, patterns: list[UsagePattern]) -> list[PainPoint]:
        """Convert patterns into actionable pain points"""
        pain_points = []

        # Group patterns by type
        patterns_by_type = defaultdict(list)
        for pattern in patterns:
            patterns_by_type[pattern.pattern_type].append(pattern)

        # Create pain points for each pattern type
        for pattern_type, type_patterns in patterns_by_type.items():
            if pattern_type == "slow_task":
                for pattern in type_patterns:
                    pain_point = PainPoint(
                        pain_point_id=f"pp_{pattern.pattern_id}",
                        description=f"Task '{pattern.context['task_type']}' takes too long",
                        severity=PainPointSeverity.HIGH,
                        location=pattern.context["task_type"],
                        impact_score=0.8,
                        users_affected=pattern.users_affected,
                        occurrences=pattern.frequency,
                        patterns=[pattern],
                        suggested_fixes=[
                            {
                                "type": "workflow_simplification",
                                "description": "Reduce steps required",
                                "expected_improvement": "50% time reduction",
                            },
                            {
                                "type": "performance",
                                "description": "Optimize backend processing",
                                "expected_improvement": "30% speed increase",
                            },
                        ],
                    )
                    pain_points.append(pain_point)

            elif pattern_type == "recurring_error":
                for pattern in type_patterns:
                    pain_point = PainPoint(
                        pain_point_id=f"pp_{pattern.pattern_id}",
                        description=f"Recurring error: {pattern.context['error_type']}",
                        severity=PainPointSeverity.CRITICAL,
                        location=", ".join(pattern.context["error_locations"]),
                        impact_score=0.9,
                        users_affected=pattern.users_affected,
                        occurrences=pattern.frequency,
                        patterns=[pattern],
                        suggested_fixes=[
                            {
                                "type": "error_handling",
                                "description": "Fix root cause of error",
                                "expected_improvement": "90% error reduction",
                            },
                            {
                                "type": "ui_improvement",
                                "description": "Add better error messaging",
                                "expected_improvement": "Improved user understanding",
                            },
                        ],
                    )
                    pain_points.append(pain_point)

            elif pattern_type == "frequent_search":
                for pattern in type_patterns:
                    pain_point = PainPoint(
                        pain_point_id=f"pp_{pattern.pattern_id}",
                        description=f"Users frequently search for '{pattern.context['query']}'",
                        severity=PainPointSeverity.MEDIUM,
                        location="search",
                        impact_score=0.6,
                        users_affected=pattern.users_affected,
                        occurrences=pattern.frequency,
                        patterns=[pattern],
                        suggested_fixes=[
                            {
                                "type": "feature_surface",
                                "description": pattern.context["suggestion"],
                                "expected_improvement": "80% reduction in searches",
                            }
                        ],
                    )
                    pain_points.append(pain_point)

        return pain_points

    def _calculate_current_metrics(self) -> dict[str, float]:
        """Calculate current metric values"""
        metrics = {}

        # Error rate
        total_events = sum(len(events) for events in self.usage_data.values())
        error_events = len(self.usage_data.get("error", []))
        metrics["error_rate"] = error_events / total_events if total_events > 0 else 0

        # Task completion time
        task_events = self.usage_data.get("task_complete", [])
        if task_events:
            completion_times = [e["data"].get("duration", 0) for e in task_events]
            metrics["avg_task_time"] = statistics.mean(completion_times)

        # Abandonment rate
        started_tasks = len(self.usage_data.get("task_start", []))
        completed_tasks = len(self.usage_data.get("task_complete", []))
        if started_tasks > 0:
            metrics["abandonment_rate"] = 1 - (completed_tasks / started_tasks)

        # Session duration
        session_events = self.usage_data.get("session_end", [])
        if session_events:
            durations = [e["data"].get("duration", 0) for e in session_events]
            metrics["avg_session_duration"] = statistics.mean(durations)

        return metrics

    def _generate_optimization_recommendations(self, pain_points: list[PainPoint]) -> list[OptimizationRecommendation]:
        """Generate optimization recommendations from pain points"""
        recommendations = []

        for pain_point in pain_points:
            # Create recommendation for each suggested fix
            for i, fix in enumerate(pain_point.suggested_fixes):
                rec = OptimizationRecommendation(
                    recommendation_id=f"rec_{pain_point.pain_point_id}_{i}",
                    optimization_type=OptimizationType(fix["type"]),
                    title=f"Fix: {pain_point.description}",
                    description=fix["description"],
                    expected_impact=fix["expected_improvement"],
                    implementation_effort=self._estimate_effort(fix["type"]),
                    priority=self._calculate_priority(pain_point),
                    metrics_improvement=self._estimate_metrics_improvement(pain_point, fix),
                    evidence=[
                        {
                            "type": "pain_point",
                            "description": pain_point.description,
                            "users_affected": pain_point.users_affected,
                            "occurrences": pain_point.occurrences,
                        }
                    ],
                )
                recommendations.append(rec)

        return recommendations

    def _has_circular_navigation(self, path: list[str]) -> bool:
        """Check if navigation path is circular"""
        if len(path) < 4:
            return False

        # Check for A-B-A-B pattern
        for i in range(len(path) - 3):
            if path[i] == path[i + 2] and path[i + 1] == path[i + 3]:
                return True

        return False

    def _check_error_pattern(self, event: dict) -> None:
        """Check for error patterns in real-time"""
        # Would implement real-time error pattern detection

    def _check_search_pattern(self, event: dict) -> None:
        """Check for search patterns in real-time"""
        # Would implement real-time search pattern detection

    def _check_navigation_loop(self, event: dict) -> None:
        """Check for navigation loops in real-time"""
        # Would implement real-time navigation loop detection

    def _update_error_metrics(self, timestamp: datetime) -> None:
        """Update error-related metrics"""
        # Calculate current error rate
        recent_events = []
        for events in self.usage_data.values():
            recent_events.extend([e for e in events if (timestamp - e["timestamp"]).total_seconds() < 3600])

        if recent_events:
            error_count = sum(1 for e in recent_events if e["event_type"] == "error")
            error_rate = error_count / len(recent_events)
            self.metrics_history["error_rate"].append((timestamp, error_rate))

    def _update_task_metrics(self, timestamp: datetime, data: dict) -> None:
        """Update task-related metrics"""
        if "duration" in data:
            self.metrics_history["task_duration"].append((timestamp, data["duration"]))

    def _update_session_metrics(self, timestamp: datetime, data: dict) -> None:
        """Update session-related metrics"""
        if "duration" in data:
            self.metrics_history["session_duration"].append((timestamp, data["duration"]))

    def _identify_trending_problems(self) -> list[dict]:
        """Identify problems that are getting worse"""
        trending = []

        for metric_name, history in self.metrics_history.items():
            if len(history) < 10:
                continue

            # Compare recent vs older values
            recent_values = [v for t, v in history[-5:]]
            older_values = [v for t, v in history[-10:-5]]

            if recent_values and older_values:
                recent_avg = statistics.mean(recent_values)
                older_avg = statistics.mean(older_values)

                # Check if getting worse (depends on metric)
                if metric_name == "error_rate" and recent_avg > older_avg * 1.2:
                    trending.append(
                        {
                            "metric": metric_name,
                            "trend": "increasing",
                            "change": f"+{(recent_avg - older_avg) / older_avg * 100:.1f}%",
                            "severity": "high",
                        }
                    )

        return trending

    def _identify_improving_areas(self) -> list[dict]:
        """Identify areas that are improving"""
        improving = []

        for metric_name, history in self.metrics_history.items():
            if len(history) < 10:
                continue

            # Compare recent vs older values
            recent_values = [v for t, v in history[-5:]]
            older_values = [v for t, v in history[-10:-5]]

            if recent_values and older_values:
                recent_avg = statistics.mean(recent_values)
                older_avg = statistics.mean(older_values)

                # Check if improving (depends on metric)
                if metric_name == "task_duration" and recent_avg < older_avg * 0.8:
                    improving.append(
                        {
                            "metric": metric_name,
                            "trend": "decreasing",
                            "change": f"-{(older_avg - recent_avg) / older_avg * 100:.1f}%",
                            "impact": "positive",
                        }
                    )

        return improving

    def _get_active_issues(self) -> list[dict]:
        """Get currently active issues"""
        active = []

        # Check recent pain points
        for pain_point in self.pain_points.values():
            # Check if still occurring
            recent_occurrence = any(
                (datetime.now() - p.last_occurrence).total_seconds() < 3600 for p in pain_point.patterns
            )

            if recent_occurrence:
                active.append(
                    {
                        "id": pain_point.pain_point_id,
                        "description": pain_point.description,
                        "severity": pain_point.severity.value,
                        "users_affected": pain_point.users_affected,
                    }
                )

        return active

    def _generate_implementation_steps(self, recommendation: OptimizationRecommendation) -> list[str]:
        """Generate implementation steps for recommendation"""
        steps_map = {
            OptimizationType.UI_IMPROVEMENT: [
                "Identify specific UI elements to modify",
                "Create design mockups",
                "Implement changes",
                "A/B test with users",
                "Deploy if successful",
            ],
            OptimizationType.WORKFLOW_SIMPLIFICATION: [
                "Map current workflow",
                "Identify redundant steps",
                "Design simplified flow",
                "Implement changes",
                "Monitor adoption",
            ],
            OptimizationType.FEATURE_SURFACE: [
                "Identify optimal placement",
                "Update navigation/UI",
                "Add discovery hints",
                "Track usage changes",
            ],
        }

        return steps_map.get(recommendation.optimization_type, ["Implement recommendation"])

    def _generate_success_criteria(self, recommendation: OptimizationRecommendation) -> list[str]:
        """Generate success criteria for recommendation"""
        criteria = []

        for metric, improvement in recommendation.metrics_improvement.items():
            if improvement > 0:
                criteria.append(f"{metric} improves by {improvement:.1%}")

        if not criteria:
            criteria.append("User satisfaction increases")

        return criteria

    def _estimate_effort(self, fix_type: str) -> str:
        """Estimate implementation effort"""
        effort_map = {
            "ui_improvement": "medium",
            "workflow_simplification": "high",
            "feature_surface": "low",
            "error_handling": "medium",
            "performance": "high",
            "documentation": "low",
        }
        return effort_map.get(fix_type, "medium")

    def _calculate_priority(self, pain_point: PainPoint) -> int:
        """Calculate priority score (1-10)"""
        base_priority = {
            PainPointSeverity.CRITICAL: 10,
            PainPointSeverity.HIGH: 8,
            PainPointSeverity.MEDIUM: 5,
            PainPointSeverity.LOW: 3,
            PainPointSeverity.INFO: 1,
        }

        priority = base_priority[pain_point.severity]

        # Adjust based on impact
        if pain_point.users_affected > 100:
            priority = min(10, priority + 2)
        elif pain_point.users_affected > 50:
            priority = min(10, priority + 1)

        return priority

    def _estimate_metrics_improvement(self, pain_point: PainPoint, fix: dict) -> dict[str, float]:
        """Estimate metrics improvement from fix"""
        improvements = {}

        if fix["type"] == "error_handling":
            improvements["error_rate"] = -0.5  # 50% reduction
        elif fix["type"] == "workflow_simplification":
            improvements["task_completion_time"] = -0.3  # 30% reduction
            improvements["abandonment_rate"] = -0.2  # 20% reduction
        elif fix["type"] == "feature_surface":
            improvements["search_rate"] = -0.4  # 40% reduction

        return improvements


# Example usage
if __name__ == "__main__":
    analytics = UsageAnalyticsLoop()

    # Simulate usage events
    import random

    # Some users complete tasks slowly
    for _i in range(10):
        analytics.track_usage_event(
            f"user_{random.randint(1, 5)}",
            "task_complete",
            {"task_type": "data_export", "duration": 45.0},  # Slow task
        )

    # Some users encounter errors
    for _i in range(8):
        analytics.track_usage_event(
            f"user_{random.randint(1, 5)}",
            "error",
            {"error_type": "validation_error", "location": "form_submit"},
        )

    # Users searching for features
    for _i in range(15):
        analytics.track_usage_event(f"user_{random.randint(1, 10)}", "search", {"query": "export data"})

    # Analyze patterns
    analysis = analytics.analyze_usage_patterns()

    print("Identified Pain Points:")
    for pain_point in analysis["pain_points"]:
        print(f"- {pain_point.description} (Severity: {pain_point.severity.value})")
        print(f"  Users affected: {pain_point.users_affected}")

    print("\nRecommendations:")
    for rec in analysis["recommendations"][:3]:
        print(f"- {rec.title}")
        print(f"  {rec.description}")
        print(f"  Priority: {rec.priority}, Effort: {rec.implementation_effort}")

    # Get real-time insights
    insights = analytics.get_real_time_insights()
    print("\nReal-time Alerts:")
    for alert in insights["alerts"]:
        print(f"- {alert['severity'].upper()}: {alert['message']}")

    # Generate improvement plan
    plan = analytics.generate_improvement_plan()
    print("\nImprovement Plan:")
    for item in plan[:3]:
        print(f"- {item['title']} (Priority: {item['priority']})")
        print(f"  Expected impact: {item['expected_impact']}")
