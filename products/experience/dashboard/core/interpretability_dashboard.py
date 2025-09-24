#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
Unified System Interpretability Dashboard
========================================
Real-time visualization and explanation of LUKHAS decision-making processes,
integrating user feedback, audit trails, and system telemetry.

Features:
- Real-time decision explanations
- User feedback integration
- System health monitoring
- Decision replay with feedback context
- Comprehensive audit trail visualization
"""

import asyncio
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

# Use stable module interfaces instead of candidate/ imports
from lukhas.core.interfaces import CoreInterface
from lukhas.core.registry import resolve, register


class LukhasError(Exception):
    """Base exception for LUKHAS system errors"""
    pass


class ValidationError(LukhasError):
    """Exception for validation errors"""
    pass


def get_logger(name: str):
    """Get logger instance - stable interface"""
    return logging.getLogger(name)


def get_service(service_name: str):
    """Get service via registry - T4 compliant interface"""
    return resolve(service_name)


def register_service(service_name: str, service_instance):
    """Register service via registry - T4 compliant interface"""
    return register(service_name, service_instance)

logger = get_logger(__name__)


class DashboardView(Enum):
    """Available dashboard views"""

    OVERVIEW = "overview"
    DECISIONS = "decisions"
    FEEDBACK = "feedback"
    CONSCIOUSNESS = "consciousness"
    MEMORY = "memory"
    PERFORMANCE = "performance"
    AUDIT_TRAIL = "audit_trail"
    HEALTH = "health"


@dataclass
class DecisionTrace:
    """Complete trace of a decision including feedback"""

    decision_id: str
    timestamp: datetime
    module: str
    decision_type: str
    input_data: dict[str, Any]
    reasoning_steps: list[dict[str, Any]]
    output: dict[str, Any]
    confidence: float
    alternatives_considered: list[dict[str, Any]]
    feedback_received: list[dict[str, Any]] = field(default_factory=list)
    performance_metrics: dict[str, float] = field(default_factory=dict)

    def get_explanation(self) -> str:
        """Generate human-readable explanation"""
        explanation = f"Decision {self.decision_id} made by {self.module}:\n"
        explanation += f"Type: {self.decision_type}\n"
        explanation += f"Confidence: {self.confidence:.1%}\n\n"

        explanation += "Reasoning:\n"
        for i, step in enumerate(self.reasoning_steps, 1):
            explanation += f"{i}. {step.get('description', 'Processing step')}\n"

        if self.alternatives_considered:
            explanation += f"\nConsidered {len(self.alternatives_considered)} alternatives\n"

        if self.feedback_received:
            avg_rating = sum(f.get("rating", 0) for f in self.feedback_received) / len(self.feedback_received)
            explanation += f"\nUser feedback: {avg_rating:.1f}/5 from {len(self.feedback_received)} users\n"

        return explanation


@dataclass
class SystemMetrics:
    """Real-time system performance metrics"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_modules: int
    decisions_per_minute: float
    average_decision_time: float
    feedback_rate: float
    error_rate: float
    health_score: float


@dataclass
class ModuleHealth:
    """Health status for individual module"""

    module_name: str
    operational: bool
    health_score: float
    last_activity: datetime
    error_count: int
    performance_score: float
    recent_decisions: int
    user_satisfaction: Optional[float] = None


class UnifiedInterpretabilityDashboard(CoreInterface):
    """
    Comprehensive dashboard for system interpretability,
    combining decision explanations with user feedback.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize interpretability dashboard"""
        self.config = config or {}
        self.operational = False

        # Services
        self.feedback_system = None
        self.audit_service = None
        self.consciousness_service = None
        self.memory_service = None
        self.explainability_framework = None

        # Data storage
        self.decision_traces: dict[str, DecisionTrace] = {}
        # Backward-compatible alias expected by some tests
        self.decisions: dict[str, dict[str, Any]] = {}
        self.system_metrics: deque = deque(maxlen=1000)  # Keep last 1000 metrics
        self.module_health: dict[str, ModuleHealth] = {}
        self.active_sessions: dict[str, dict[str, Any]] = {}

        # Real-time data streams
        self.decision_stream: deque = deque(maxlen=100)
        self.feedback_stream: deque = deque(maxlen=100)
        self.alert_stream: deque = deque(maxlen=50)

        # Configuration
        self.update_interval = self.config.get("update_interval", 5)  # seconds
        self.retention_hours = self.config.get("retention_hours", 24)
        self.enable_realtime = self.config.get("enable_realtime", True)

        # Metrics tracking
        self.dashboard_metrics = {
            "total_decisions_tracked": 0,
            "total_feedback_integrated": 0,
            "active_users": 0,
            "dashboard_views": defaultdict(int),
        }

    async def initialize(self) -> None:
        """Initialize dashboard and connect to services"""
        try:
            logger.info("Initializing Unified Interpretability Dashboard...")

            # Get services
            # Optionalize dependencies for test environments; use when available
            try:
                self.feedback_system = get_service("user_feedback_system")
            except Exception:
                self.feedback_system = None
            try:
                self.audit_service = get_service("audit_service")
            except Exception:
                self.audit_service = None
            try:
                self.consciousness_service = get_service("consciousness_service")
            except Exception:
                self.consciousness_service = None
            try:
                self.memory_service = get_service("memory_service")
            except Exception:
                self.memory_service = None
            try:
                self.explainability_framework = get_service("explainability_framework")
            except Exception:
                self.explainability_framework = None

            # Register this service
            register_service("interpretability_dashboard", self, singleton=True)

            # Start background tasks
            if self.enable_realtime:
                asyncio.create_task(self._update_loop())
                asyncio.create_task(self._cleanup_loop())

            self.operational = True
            logger.info("Interpretability Dashboard initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize dashboard: {e}")
            raise LukhasError(f"Initialization failed: {e}")

    async def _update_loop(self):
        """Background task to update metrics"""
        while self.operational:
            try:
                await self._collect_system_metrics()
                await self._update_module_health()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(self.update_interval * 2)

    async def _cleanup_loop(self):
        """Background task to cleanup old data"""
        while self.operational:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Run hourly
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)

    async def _collect_system_metrics(self):
        """Collect current system metrics"""
        # Simulated metrics - in production, collect from actual system
        import psutil

        current_metrics = SystemMetrics(
            timestamp=datetime.now(timezone.utc),
            cpu_usage=(psutil.cpu_percent(interval=0.1) if "psutil" in globals() else 50.0),
            memory_usage=(psutil.virtual_memory().percent if "psutil" in globals() else 60.0),
            active_modules=len(self.module_health),
            decisions_per_minute=len(self.decision_stream) / max(1, self.update_interval / 60),
            average_decision_time=self._calculate_avg_decision_time(),
            feedback_rate=self._calculate_feedback_rate(),
            error_rate=self._calculate_error_rate(),
            health_score=self._calculate_overall_health(),
        )

        self.system_metrics.append(current_metrics)

    async def _update_module_health(self):
        """Update health status for all modules"""
        modules_to_check = [
            "consciousness_service",
            "memory_service",
            "emotion_service",
            "dream_engine",
            "guardian_service",
            "parallel_reality_simulator",
        ]

        for module_name in modules_to_check:
            try:
                service = get_service(module_name)
                if service and hasattr(service, "get_status"):
                    status = await service.get_status()

                    # Calculate user satisfaction from feedback
                    satisfaction = None
                    if self.feedback_system:
                        # Get recent feedback for this module
                        module_decisions = [
                            d for d in self.decision_traces.values() if d.module == module_name and d.feedback_received
                        ]
                        if module_decisions:
                            all_ratings = []
                            for decision in module_decisions[-10:]:  # Last 10 decisions
                                ratings = [f.get("rating", 0) for f in decision.feedback_received if "rating" in f]
                                all_ratings.extend(ratings)

                            if all_ratings:
                                # Normalize to 0-1
                                satisfaction = sum(all_ratings) / len(all_ratings) / 5.0

                    self.module_health[module_name] = ModuleHealth(
                        module_name=module_name,
                        operational=status.get("operational", False),
                        health_score=status.get("health_score", 0.0),
                        last_activity=datetime.now(timezone.utc),
                        error_count=status.get("metrics", {}).get("errors", 0),
                        performance_score=1.0 - status.get("metrics", {}).get("error_rate", 0.0),
                        recent_decisions=status.get("metrics", {}).get("decisions_made", 0),
                        user_satisfaction=satisfaction,
                    )
            except Exception as e:
                logger.debug(f"Could not update health for {module_name}: {e}")

    async def track_decision(
        self,
        decision_id: str,
        module: str,
        decision_type: str,
        input_data: dict[str, Any],
        reasoning_steps: list[dict[str, Any]],
        output: dict[str, Any],
        confidence: float,
        alternatives: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        """
        Track a decision for interpretability.

        Args:
            decision_id: Unique decision identifier
            module: Module that made the decision
            decision_type: Type of decision
            input_data: Input that led to decision
            reasoning_steps: Step-by-step reasoning
            output: Decision output
            confidence: Confidence level
            alternatives: Other options considered
        """
        trace = DecisionTrace(
            decision_id=decision_id,
            timestamp=datetime.now(timezone.utc),
            module=module,
            decision_type=decision_type,
            input_data=input_data,
            reasoning_steps=reasoning_steps,
            output=output,
            confidence=confidence,
            alternatives_considered=alternatives or [],
        )

        self.decision_traces[decision_id] = trace
        # Maintain simplified mirror for tests using plain dict access
        self.decisions[decision_id] = {
            "module": module,
            "decision_type": decision_type,
            "input_data": input_data,
            "reasoning_steps": reasoning_steps,
            "output": output,
            "confidence": confidence,
            "feedback_references": [],
            "timestamp": trace.timestamp,
        }
        self.decision_stream.append(trace)
        self.dashboard_metrics["total_decisions_tracked"] += 1

        # Audit trail
        if self.audit_service:
            await self.audit_service.log_event(
                {
                    "event_type": "decision_tracked",
                    "decision_id": decision_id,
                    "module": module,
                    "confidence": confidence,
                    "timestamp": trace.timestamp,
                }
            )

        logger.debug(f"Tracked decision {decision_id} from {module}")

    async def integrate_feedback(self, decision_id: str, feedback_data: dict[str, Any]) -> None:
        """
        Integrate user feedback with decision trace.

        Args:
            decision_id: Decision the feedback is about
            feedback_data: Feedback information
        """
        if decision_id not in self.decision_traces:
            logger.warning(f"Decision {decision_id} not found for feedback integration")
            return

        trace = self.decision_traces[decision_id]
        trace.feedback_received.append(feedback_data)

        # Mirror into decisions alias for compatibility
        if decision_id in self.decisions:
            self.decisions[decision_id].setdefault("feedback_references", []).append(feedback_data)

        self.feedback_stream.append(
            {
                "decision_id": decision_id,
                "feedback": feedback_data,
                "timestamp": datetime.now(timezone.utc),
            }
        )

        self.dashboard_metrics["total_feedback_integrated"] += 1

        # Update module satisfaction score
        await self._update_module_health()

    async def get_decision_explanation(self, decision_id: str, include_feedback: bool = True) -> dict[str, Any]:
        """
        Get comprehensive explanation for a decision.

        Args:
            decision_id: Decision to explain
            include_feedback: Include user feedback in explanation

        Returns:
            Detailed explanation with context
        """
        if decision_id not in self.decision_traces:
            raise LukhasError(f"Decision {decision_id} not found")

        trace = self.decision_traces[decision_id]

        explanation = {
            "decision_id": decision_id,
            "summary": trace.get_explanation(),
            "details": {
                "timestamp": trace.timestamp.isoformat(),
                "module": trace.module,
                "type": trace.decision_type,
                "confidence": trace.confidence,
                "input_summary": self._summarize_input(trace.input_data),
                "reasoning": trace.reasoning_steps,
                "alternatives": trace.alternatives_considered,
            },
        }

        if include_feedback and trace.feedback_received:
            feedback_summary = {
                "count": len(trace.feedback_received),
                "average_rating": None,
                "sentiments": defaultdict(float),
                "comments": [],
            }

            ratings = []
            for feedback in trace.feedback_received:
                if "rating" in feedback:
                    ratings.append(feedback["rating"])
                if "sentiment" in feedback:
                    for emotion, score in feedback["sentiment"].items():
                        feedback_summary["sentiments"][emotion] += score
                if "text" in feedback:
                    feedback_summary["comments"].append(feedback["text"])

            if ratings:
                feedback_summary["average_rating"] = sum(ratings) / len(ratings)

            # Normalize sentiments
            if feedback_summary["sentiments"]:
                total = sum(feedback_summary["sentiments"].values())
                feedback_summary["sentiments"] = {k: v / total for k, v in feedback_summary["sentiments"].items()}

            explanation["feedback"] = feedback_summary

        return explanation

    def _summarize_input(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Create summary of input data for display"""
        summary = {}

        for key, value in input_data.items():
            if isinstance(value, (str, int, float, bool)):
                summary[key] = value
            elif isinstance(value, list):
                summary[key] = f"List with {len(value)} items"
            elif isinstance(value, dict):
                summary[key] = f"Object with {len(value)} fields"
            else:
                summary[key] = type(value).__name__

        return summary

    async def get_dashboard_view(self, view: DashboardView) -> dict[str, Any]:
        """
        Get data for specific dashboard view.

        Args:
            view: Which dashboard view to retrieve

        Returns:
            View-specific data
        """
        self.dashboard_metrics["dashboard_views"][view.value] += 1

        if view == DashboardView.OVERVIEW:
            return await self._get_overview_data()
        elif view == DashboardView.DECISIONS:
            return await self._get_decisions_data()
        elif view == DashboardView.FEEDBACK:
            return await self._get_feedback_data()
        elif view == DashboardView.CONSCIOUSNESS:
            return await self._get_consciousness_data()
        elif view == DashboardView.MEMORY:
            return await self._get_memory_data()
        elif view == DashboardView.PERFORMANCE:
            return await self._get_performance_data()
        elif view == DashboardView.AUDIT_TRAIL:
            return await self._get_audit_trail_data()
        elif view == DashboardView.HEALTH:
            return await self._get_health_data()
        else:
            raise ValidationError(f"Unknown view: {view}")

    async def _get_overview_data(self) -> dict[str, Any]:
        """Get overview dashboard data"""
        recent_metrics = list(self.system_metrics)[-1] if self.system_metrics else None

        return {
            "current_metrics": {
                "health_score": recent_metrics.health_score if recent_metrics else 0.0,
                "active_modules": len([m for m in self.module_health.values() if m.operational]),
                "decisions_per_minute": (recent_metrics.decisions_per_minute if recent_metrics else 0),
                "user_satisfaction": self._calculate_overall_satisfaction(),
            },
            "recent_decisions": [
                {
                    "id": d.decision_id,
                    "module": d.module,
                    "type": d.decision_type,
                    "confidence": d.confidence,
                    "timestamp": d.timestamp.isoformat(),
                }
                for d in list(self.decision_stream)[-10:]
            ],
            "recent_feedback": [
                {
                    "decision_id": f["decision_id"],
                    "type": f["feedback"].get("type", "unknown"),
                    "sentiment": f["feedback"].get("sentiment", {}),
                    "timestamp": f["timestamp"].isoformat(),
                }
                for f in list(self.feedback_stream)[-10:]
            ],
            "alerts": list(self.alert_stream)[-5:],
        }

    async def _get_decisions_data(self) -> dict[str, Any]:
        """Get decisions view data"""
        decisions_by_module = defaultdict(list)
        decisions_by_type = defaultdict(list)

        for trace in self.decision_traces.values():
            decisions_by_module[trace.module].append(trace)
            decisions_by_type[trace.decision_type].append(trace)

        return {
            "total_decisions": len(self.decision_traces),
            "by_module": {
                module: {
                    "count": len(decisions),
                    "average_confidence": sum(d.confidence for d in decisions) / len(decisions),
                    "with_feedback": len([d for d in decisions if d.feedback_received]),
                }
                for module, decisions in decisions_by_module.items()
            },
            "by_type": {
                dtype: {
                    "count": len(decisions),
                    "recent": [
                        {
                            "id": d.decision_id,
                            "timestamp": d.timestamp.isoformat(),
                            "confidence": d.confidence,
                        }
                        for d in sorted(decisions, key=lambda x: x.timestamp, reverse=True)[:5]
                    ],
                }
                for dtype, decisions in decisions_by_type.items()
            },
            "recent_explanations": [
                await self.get_decision_explanation(d.decision_id, include_feedback=False)
                for d in list(self.decision_stream)[-5:]
            ],
        }

    async def _get_feedback_data(self) -> dict[str, Any]:
        """Get feedback view data"""
        if not self.feedback_system:
            return {"error": "Feedback system not available"}

        # Get feedback summary
        feedback_summary = await self.feedback_system.generate_feedback_report(
            start_date=datetime.now(timezone.utc) - timedelta(hours=24),
            end_date=datetime.now(timezone.utc),
            anonymize=False,
        )

        # Correlate with decisions
        feedback_by_decision = defaultdict(list)
        for trace in self.decision_traces.values():
            if trace.feedback_received:
                feedback_by_decision[trace.module].extend(trace.feedback_received)

        return {
            "summary": feedback_summary,
            "by_module": {
                module: {
                    "total_feedback": len(feedbacks),
                    "average_rating": (
                        sum(f.get("rating", 0) for f in feedbacks) / len(feedbacks)
                        if feedbacks and any("rating" in f for f in feedbacks)
                        else None
                    ),
                    "sentiment_summary": self._aggregate_sentiments(feedbacks),
                }
                for module, feedbacks in feedback_by_decision.items()
            },
            "recent_feedback": list(self.feedback_stream)[-20:],
            "trends": self._analyze_feedback_trends(),
        }

    async def _get_consciousness_data(self) -> dict[str, Any]:
        """Get consciousness view data"""
        if not self.consciousness_service:
            return {"error": "Consciousness service not available"}

        try:
            awareness_state = await self.consciousness_service.assess_awareness({})

            # Get consciousness-related decisions
            consciousness_decisions = [d for d in self.decision_traces.values() if d.module == "consciousness_service"]

            return {
                "current_state": awareness_state,
                "recent_decisions": [
                    {
                        "id": d.decision_id,
                        "type": d.decision_type,
                        "confidence": d.confidence,
                        "timestamp": d.timestamp.isoformat(),
                        "user_satisfaction": self._calculate_decision_satisfaction(d),
                    }
                    for d in sorted(consciousness_decisions, key=lambda x: x.timestamp, reverse=True)[:10]
                ],
                "awareness_history": self._get_awareness_history(),
                "decision_patterns": self._analyze_consciousness_patterns(consciousness_decisions),
            }
        except Exception as e:
            logger.error(f"Error getting consciousness data: {e}")
            return {"error": str(e)}

    async def _get_memory_data(self) -> dict[str, Any]:
        """Get memory view data"""
        if not self.memory_service:
            return {"error": "Memory service not available"}

        try:
            memory_status = await self.memory_service.get_status()

            # Get memory-related decisions
            memory_decisions = [d for d in self.decision_traces.values() if d.module == "memory_service"]

            return {
                "status": memory_status,
                "recent_operations": [
                    {
                        "id": d.decision_id,
                        "type": d.decision_type,
                        "timestamp": d.timestamp.isoformat(),
                        "context": d.input_data.get("query", "unknown"),
                    }
                    for d in sorted(memory_decisions, key=lambda x: x.timestamp, reverse=True)[:10]
                ],
                "memory_usage_trends": self._analyze_memory_trends(),
            }
        except Exception as e:
            logger.error(f"Error getting memory data: {e}")
            return {"error": str(e)}

    async def _get_performance_data(self) -> dict[str, Any]:
        """Get performance view data"""
        metrics_list = list(self.system_metrics)

        if not metrics_list:
            return {"error": "No performance data available"}

        return {
            "current": {
                "cpu_usage": metrics_list[-1].cpu_usage,
                "memory_usage": metrics_list[-1].memory_usage,
                "decisions_per_minute": metrics_list[-1].decisions_per_minute,
                "average_decision_time": metrics_list[-1].average_decision_time,
                "error_rate": metrics_list[-1].error_rate,
            },
            "trends": {
                "cpu": [m.cpu_usage for m in metrics_list[-20:]],
                "memory": [m.memory_usage for m in metrics_list[-20:]],
                "decisions": [m.decisions_per_minute for m in metrics_list[-20:]],
                "errors": [m.error_rate for m in metrics_list[-20:]],
            },
            "by_module": {
                module: {
                    "performance_score": health.performance_score,
                    "recent_decisions": health.recent_decisions,
                    "error_count": health.error_count,
                }
                for module, health in self.module_health.items()
            },
        }

    async def _get_audit_trail_data(self) -> dict[str, Any]:
        """Get audit trail view data"""
        if not self.audit_service:
            return {"error": "Audit service not available"}

        try:
            # Get recent audit entries
            recent_entries = await self.audit_service.get_recent_entries(limit=50)

            # Group by event type
            entries_by_type = defaultdict(list)
            for entry in recent_entries:
                entries_by_type[entry.get("event_type", "unknown")].append(entry)

            return {
                "total_entries": len(recent_entries),
                "by_type": {
                    event_type: {"count": len(entries), "recent": entries[:5]}
                    for event_type, entries in entries_by_type.items()
                },
                "decision_audit_trail": [
                    entry for entry in recent_entries if entry.get("event_type") == "decision_tracked"
                ][:20],
                "feedback_audit_trail": [
                    entry for entry in recent_entries if entry.get("event_type") == "user_feedback_collected"
                ][:20],
            }
        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return {"error": str(e)}

    async def _get_health_data(self) -> dict[str, Any]:
        """Get health view data"""
        return {
            "overall_health": self._calculate_overall_health(),
            "modules": {
                name: {
                    "operational": health.operational,
                    "health_score": health.health_score,
                    "last_activity": health.last_activity.isoformat(),
                    "error_count": health.error_count,
                    "performance_score": health.performance_score,
                    "user_satisfaction": health.user_satisfaction,
                }
                for name, health in self.module_health.items()
            },
            "alerts": list(self.alert_stream),
            "recommendations": self._generate_health_recommendations(),
        }

    def _calculate_avg_decision_time(self) -> float:
        """Calculate average decision processing time"""
        # Simplified - in production, track actual timings
        return 250.0  # ms

    def _calculate_feedback_rate(self) -> float:
        """Calculate feedback collection rate"""
        if not self.decision_traces:
            return 0.0

        decisions_with_feedback = sum(1 for d in self.decision_traces.values() if d.feedback_received)

        return decisions_with_feedback / len(self.decision_traces)

    def _calculate_error_rate(self) -> float:
        """Calculate system error rate"""
        total_errors = sum(h.error_count for h in self.module_health.values())
        total_decisions = self.dashboard_metrics["total_decisions_tracked"]

        if total_decisions == 0:
            return 0.0

        return min(1.0, total_errors / total_decisions)

    def _calculate_overall_health(self) -> float:
        """Calculate overall system health score"""
        if not self.module_health:
            return 0.5

        health_scores = [h.health_score for h in self.module_health.values()]
        operational_count = sum(1 for h in self.module_health.values() if h.operational)

        base_health = sum(health_scores) / len(health_scores) if health_scores else 0.5
        operational_ratio = operational_count / len(self.module_health) if self.module_health else 0.5

        # Factor in error rate and user satisfaction
        error_penalty = self._calculate_error_rate() * 0.3
        satisfaction_bonus = self._calculate_overall_satisfaction() * 0.2

        return max(
            0.0,
            min(
                1.0,
                base_health * operational_ratio - error_penalty + satisfaction_bonus,
            ),
        )

    def _calculate_overall_satisfaction(self) -> float:
        """Calculate overall user satisfaction"""
        satisfactions = [h.user_satisfaction for h in self.module_health.values() if h.user_satisfaction is not None]

        if not satisfactions:
            return 0.7  # Default neutral

        return sum(satisfactions) / len(satisfactions)

    def _calculate_decision_satisfaction(self, decision: DecisionTrace) -> Optional[float]:
        """Calculate satisfaction for specific decision"""
        if not decision.feedback_received:
            return None

        ratings = [f.get("rating", 0) for f in decision.feedback_received if "rating" in f]

        if not ratings:
            return None

        return sum(ratings) / len(ratings) / 5.0  # Normalize to 0-1

    def _aggregate_sentiments(self, feedbacks: list[dict[str, Any]]) -> dict[str, float]:
        """Aggregate sentiments from multiple feedbacks"""
        aggregated = defaultdict(float)
        count = 0

        for feedback in feedbacks:
            if "sentiment" in feedback:
                count += 1
                for emotion, score in feedback["sentiment"].items():
                    aggregated[emotion] += score

        if count > 0:
            return {k: v / count for k, v in aggregated.items()}

        return {}

    def _analyze_feedback_trends(self) -> dict[str, Any]:
        """Analyze trends in feedback"""
        if not self.feedback_stream:
            return {"trend": "insufficient_data"}

        # Simple trend analysis
        recent_feedback = list(self.feedback_stream)[-20:]

        positive_count = sum(1 for f in recent_feedback if f["feedback"].get("sentiment", {}).get("positive", 0) > 0.5)

        negative_count = sum(1 for f in recent_feedback if f["feedback"].get("sentiment", {}).get("negative", 0) > 0.5)

        if positive_count > negative_count * 1.5:
            trend = "improving"
        elif negative_count > positive_count * 1.5:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "positive_ratio": (positive_count / len(recent_feedback) if recent_feedback else 0),
            "sample_size": len(recent_feedback),
        }

    def _get_awareness_history(self) -> list[dict[str, Any]]:
        """Get historical awareness data"""
        # Simplified - in production, track actual history
        return [
            {
                "timestamp": datetime.now(timezone.utc) - timedelta(minutes=i * 10),
                "awareness": 0.7 + (i % 3) * 0.1,
            }
            for i in range(6)
        ]

    def _analyze_consciousness_patterns(self, decisions: list[DecisionTrace]) -> dict[str, Any]:
        """Analyze patterns in consciousness decisions"""
        if not decisions:
            return {"patterns": "insufficient_data"}

        # Analyze decision types
        type_counts = defaultdict(int)
        for d in decisions:
            type_counts[d.decision_type] += 1

        # Analyze confidence levels
        confidences = [d.confidence for d in decisions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            "decision_types": dict(type_counts),
            "average_confidence": avg_confidence,
            "confidence_trend": "stable",  # Simplified
        }

    def _analyze_memory_trends(self) -> dict[str, Any]:
        """Analyze memory usage trends"""
        # Simplified - in production, track actual memory metrics
        return {
            "usage_trend": "increasing",
            "retrieval_performance": "optimal",
            "consolidation_rate": "normal",
        }

    def _generate_health_recommendations(self) -> list[str]:
        """Generate health improvement recommendations"""
        recommendations = []

        # Check module health
        for name, health in self.module_health.items():
            if not health.operational:
                recommendations.append(f"Restart {name} - currently non-operational")
            elif health.health_score < 0.5:
                recommendations.append(f"Investigate {name} - low health score ({health.health_score:.1%})")
            elif health.error_count > 10:
                recommendations.append(f"Review {name} errors - {health.error_count} errors detected")

        # Check user satisfaction
        satisfaction = self._calculate_overall_satisfaction()
        if satisfaction < 0.6:
            recommendations.append(f"Improve user experience - satisfaction at {satisfaction:.1%}")

        # Check error rate
        error_rate = self._calculate_error_rate()
        if error_rate > 0.1:
            recommendations.append(f"Reduce error rate - currently at {error_rate:.1%}")

        if not recommendations:
            recommendations.append("System operating optimally - no immediate actions required")

        return recommendations

    async def _cleanup_old_data(self):
        """Clean up data older than retention period"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)

        # Clean up old decisions
        old_decisions = [
            decision_id for decision_id, trace in self.decision_traces.items() if trace.timestamp < cutoff_time
        ]

        for decision_id in old_decisions:
            del self.decision_traces[decision_id]

        if old_decisions:
            logger.info(f"Cleaned up {len(old_decisions)} old decision traces")

    async def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ):
        """Create system alert"""
        alert = {
            "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc),
            "type": alert_type,
            "severity": severity,
            "message": message,
            "details": details or {},
        }

        self.alert_stream.append(alert)

        # Log critical alerts
        if severity == "critical":
            logger.error(f"Critical alert: {message}")

    # Required interface methods

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process dashboard request"""
        action = data.get("action", "get_view")

        if action == "get_view":
            view = DashboardView(data.get("view", "overview"))
            return await self.get_dashboard_view(view)

        elif action == "track_decision":
            await self.track_decision(
                decision_id=data["decision_id"],
                module=data["module"],
                decision_type=data["decision_type"],
                input_data=data["input_data"],
                reasoning_steps=data["reasoning_steps"],
                output=data["output"],
                confidence=data["confidence"],
                alternatives=data.get("alternatives"),
            )
            return {"status": "tracked"}

        elif action == "integrate_feedback":
            await self.integrate_feedback(decision_id=data["decision_id"], feedback_data=data["feedback_data"])
            return {"status": "integrated"}

        elif action == "explain_decision":
            explanation = await self.get_decision_explanation(
                decision_id=data["decision_id"],
                include_feedback=data.get("include_feedback", True),
            )
            return explanation

        else:
            raise ValidationError(f"Unknown action: {action}")

    async def handle_glyph(self, token: Any) -> Any:
        """Handle GLYPH communication"""
        return {"operational": self.operational, "metrics": self.dashboard_metrics}

    async def get_status(self) -> dict[str, Any]:
        """Get dashboard status"""
        return {
            "operational": self.operational,
            "tracked_decisions": len(self.decision_traces),
            "total_decisions": len(self.decision_traces),
            "integrated_feedback": self.dashboard_metrics["total_feedback_integrated"],
            "active_modules": len([m for m in self.module_health.values() if m.operational]),
            "overall_health": self._calculate_overall_health(),
            "user_satisfaction": self._calculate_overall_satisfaction(),
            "update_interval": self.update_interval,
            "retention_hours": self.retention_hours,
        }


# Example usage
async def demo_interpretability_dashboard():
    """Demonstrate the interpretability dashboard"""
    dashboard = UnifiedInterpretabilityDashboard(config={"update_interval": 2, "enable_realtime": True})

    # Mock services
    from unittest.mock import AsyncMock, Mock

    # Mock feedback system
    mock_feedback = Mock()
    mock_feedback.generate_feedback_report = AsyncMock(
        return_value={
            "summary": {
                "total_feedback": 42,
                "unique_users": 15,
                "satisfaction_score": 0.82,
            }
        }
    )

    # Mock consciousness service
    mock_consciousness = Mock()
    mock_consciousness.assess_awareness = AsyncMock(
        return_value={
            "overall_awareness": 0.85,
            "attention_targets": ["decisions", "feedback"],
        }
    )
    mock_consciousness.get_status = AsyncMock(
        return_value={
            "operational": True,
            "health_score": 0.9,
            "metrics": {"decisions_made": 100, "errors": 2},
        }
    )

    from candidate.core.interfaces.dependency_injection import register_service

    register_service("user_feedback_system", mock_feedback)
    register_service("consciousness_service", mock_consciousness)

    await dashboard.initialize()

    print("Unified Interpretability Dashboard Demo")
    print("=" * 50)

    # Track some decisions
    for i in range(3):
        await dashboard.track_decision(
            decision_id=f"demo_decision_{i}",
            module="consciousness_service",
            decision_type="recommendation",
            input_data={"query": f"User query {i}"},
            reasoning_steps=[
                {"description": "Analyzed user intent"},
                {"description": "Evaluated options"},
                {"description": "Selected best match"},
            ],
            output={"recommendation": f"Option {i}"},
            confidence=0.85 + i * 0.05,
            alternatives=[{"option": f"Alt {i}"}],
        )

        # Add feedback
        await dashboard.integrate_feedback(
            decision_id=f"demo_decision_{i}",
            feedback_data={
                "type": "rating",
                "rating": 4 + (i % 2),
                "sentiment": {"positive": 0.8, "negative": 0.2},
                "text": "Good recommendation!" if i % 2 else "Could be better",
            },
        )

    # Get different dashboard views
    print("\n📊 Overview:")
    overview = await dashboard.get_dashboard_view(DashboardView.OVERVIEW)
    print(f"  Health Score: {overview['current_metrics']['health_score']:.1%}")
    print(f"  Active Modules: {overview['current_metrics']['active_modules']}")
    print(f"  User Satisfaction: {overview['current_metrics']['user_satisfaction']:.1%}")

    print("\n🎯 Decisions:")
    decisions = await dashboard.get_dashboard_view(DashboardView.DECISIONS)
    print(f"  Total Tracked: {decisions['total_decisions']}")

    print("\n💬 Feedback:")
    feedback = await dashboard.get_dashboard_view(DashboardView.FEEDBACK)
    print(f"  Summary: {feedback['summary']}")

    print("\n🧠 Consciousness:")
    consciousness = await dashboard.get_dashboard_view(DashboardView.CONSCIOUSNESS)
    print(f"  Current Awareness: {consciousness['current_state']['overall_awareness']:.1%}")

    # Get decision explanation
    print("\n📝 Decision Explanation:")
    explanation = await dashboard.get_decision_explanation("demo_decision_0")
    print(explanation["summary"])

    # Show status
    status = await dashboard.get_status()
    print(f"\nDashboard Status: {status}")


if __name__ == "__main__":
    asyncio.run(demo_interpretability_dashboard())
