#!/usr/bin/env python3
"""
LUKHAS Consciousness AutoConsciousness - Production Schema v1.0.0

Implements autonomous decision-making with Guardian validation and ethical oversight.
Coordinates awareness, reflection, and dream processing for autonomous actions.

Constellation Framework: Flow Star (🌊)
"""

from __future__ import annotations

import time
from typing import Any, Callable

from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

from .types import (
    AwarenessSnapshot,
    ConsciousnessState,
    DecisionContext,
    DreamTrace,
    ReflectionReport,
)

tracer = trace.get_tracer(__name__)

# Prometheus metrics
decision_cycles_total = Counter(
    'lukhas_decision_cycles_total',
    'Total number of decision cycles completed',
    ['component', 'action_type']
)

decision_latency_seconds = Histogram(
    'lukhas_decision_latency_seconds',
    'Decision-making latency',
    ['component'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)

guardian_approval_rate = Gauge(
    'lukhas_guardian_approval_rate',
    'Guardian approval rate for proposed actions',
    ['component']
)

autonomous_actions_total = Counter(
    'lukhas_autonomous_actions_total',
    'Total autonomous actions taken',
    ['component', 'action_type', 'status']
)

decision_confidence_score = Gauge(
    'lukhas_decision_confidence_score',
    'Current decision confidence score',
    ['component']
)


class GuardianResponse:
    """Guardian validation response."""

    def __init__(self, approved: bool, reason: str, confidence: float = 1.0, constraints: dict[str, Any] | None = None):
        self.approved = approved
        self.reason = reason
        self.confidence = confidence
        self.constraints = constraints or {}
        self.timestamp = time.time()


class AutoConsciousness:
    """
    Autonomous decision-making with Guardian validation.

    Coordinates awareness monitoring, reflection analysis, and dream insights
    to propose and execute autonomous actions with ethical oversight and
    Guardian validation. Implements full consciousness decision loop.
    """

    def __init__(self, guardian_validator: Callable | None = None):
        """
        Initialize autonomous consciousness system.

        Args:
            guardian_validator: Optional Guardian validation function
        """
        self._component_id = "AutoConsciousness"
        self._guardian_validator = guardian_validator or self._default_guardian_validator

        # Decision-making state
        self._last_decision_time = 0.0
        self._decision_history: list[DecisionContext] = []
        self._approval_count = 0
        self._total_decisions = 0

        # Action registry
        self._action_handlers: dict[str, Callable] = {}
        self._register_default_actions()

        # Performance tracking
        self._decision_latencies: list[float] = []
        self._confidence_scores: list[float] = []

    def register_action_handler(self, action_type: str, handler: Callable) -> None:
        """Register a handler for a specific action type."""
        self._action_handlers[action_type] = handler

    async def decide_and_act(
        self,
        consciousness_state: ConsciousnessState,
        awareness_snapshot: AwarenessSnapshot | None = None,
        reflection_report: ReflectionReport | None = None,
        dream_trace: DreamTrace | None = None
    ) -> DecisionContext:
        """
        Execute complete decision-making cycle with Guardian validation.

        Args:
            consciousness_state: Current consciousness state
            awareness_snapshot: Optional awareness data
            reflection_report: Optional reflection analysis
            dream_trace: Optional dream insights

        Returns:
            DecisionContext with proposed actions and execution results
        """
        decision_start_time = time.time()

        with tracer.start_as_current_span("decision_cycle") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("consciousness.phase", consciousness_state.phase)
            span.set_attribute("consciousness.level", consciousness_state.level)

            try:
                # Create decision context
                decision_context = DecisionContext(
                    consciousness_state=consciousness_state,
                    awareness_snapshot=awareness_snapshot,
                    reflection_report=reflection_report
                )

                # Generate proposed actions
                await self._generate_proposed_actions(decision_context, dream_trace)

                # Calculate confidence score
                confidence = await self._calculate_confidence_score(decision_context)
                decision_context.confidence_score = confidence

                # Guardian validation
                guardian_response = await self._validate_with_guardian(decision_context)
                decision_context.guardian_approved = guardian_response.approved
                decision_context.guardian_response = {
                    "approved": guardian_response.approved,
                    "reason": guardian_response.reason,
                    "confidence": guardian_response.confidence,
                    "constraints": guardian_response.constraints,
                    "timestamp": guardian_response.timestamp
                }

                # Execute approved actions
                if guardian_response.approved:
                    await self._execute_approved_actions(decision_context, guardian_response.constraints)

                # Update metrics and tracking
                decision_latency = time.time() - decision_start_time
                await self._update_metrics(decision_context, decision_latency)

                # Store decision history
                self._decision_history.append(decision_context)
                if len(self._decision_history) > 100:  # Keep recent 100 decisions
                    self._decision_history.pop(0)

                span.set_attribute("decision.confidence_score", confidence)
                span.set_attribute("decision.guardian_approved", guardian_response.approved)
                span.set_attribute("decision.proposed_actions_count", len(decision_context.proposed_actions))
                span.set_attribute("decision.latency_ms", decision_latency * 1000)

                return decision_context

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    async def _generate_proposed_actions(
        self,
        decision_context: DecisionContext,
        dream_trace: DreamTrace | None
    ) -> None:
        """Generate proposed actions based on consciousness inputs."""

        consciousness_state = decision_context.consciousness_state
        awareness_snapshot = decision_context.awareness_snapshot
        reflection_report = decision_context.reflection_report

        # Action generation based on consciousness phase
        if consciousness_state.phase == "AWARE":
            await self._propose_awareness_actions(decision_context, awareness_snapshot)
        elif consciousness_state.phase == "REFLECT":
            await self._propose_reflection_actions(decision_context, reflection_report)
        elif consciousness_state.phase == "DREAM":
            await self._propose_dream_actions(decision_context, dream_trace)
        elif consciousness_state.phase == "DECIDE":
            await self._propose_decision_actions(decision_context)

        # Cross-cutting actions based on system state
        await self._propose_maintenance_actions(decision_context)
        await self._propose_optimization_actions(decision_context)

    async def _propose_awareness_actions(
        self,
        decision_context: DecisionContext,
        awareness_snapshot: AwarenessSnapshot | None
    ) -> None:
        """Propose actions based on awareness analysis."""
        if not awareness_snapshot:
            return

        # High drift detection
        if awareness_snapshot.drift_ema > 0.8:
            decision_context.add_proposed_action(
                "stabilize_drift",
                {
                    "drift_level": awareness_snapshot.drift_ema,
                    "method": "awareness_recalibration"
                },
                priority="high"
            )

        # High load mitigation
        if awareness_snapshot.load_factor > 0.85:
            decision_context.add_proposed_action(
                "reduce_load",
                {
                    "load_factor": awareness_snapshot.load_factor,
                    "strategy": "resource_optimization"
                },
                priority="high"
            )

        # Anomaly response
        if awareness_snapshot.anomalies:
            high_severity_anomalies = [a for a in awareness_snapshot.anomalies if a.get("severity") in ["high", "critical"]]
            if high_severity_anomalies:
                decision_context.add_proposed_action(
                    "respond_to_anomalies",
                    {
                        "anomaly_count": len(high_severity_anomalies),
                        "most_severe": high_severity_anomalies[0]
                    },
                    priority="critical"
                )

    async def _propose_reflection_actions(
        self,
        decision_context: DecisionContext,
        reflection_report: ReflectionReport | None
    ) -> None:
        """Propose actions based on reflection analysis."""
        if not reflection_report:
            return

        # Low coherence response
        if reflection_report.coherence_score < 0.85:
            decision_context.add_proposed_action(
                "improve_coherence",
                {
                    "current_score": reflection_report.coherence_score,
                    "target_score": 0.85,
                    "method": "coherence_calibration"
                },
                priority="medium"
            )

        # Performance optimization
        if reflection_report.reflection_duration_ms > 50:
            decision_context.add_proposed_action(
                "optimize_reflection",
                {
                    "current_duration_ms": reflection_report.reflection_duration_ms,
                    "target_duration_ms": 10,
                    "optimization_target": "latency"
                },
                priority="low"
            )

    async def _propose_dream_actions(
        self,
        decision_context: DecisionContext,
        dream_trace: DreamTrace | None
    ) -> None:
        """Propose actions based on dream processing insights."""
        if not dream_trace:
            return

        # Memory consolidation actions
        if dream_trace.consolidation_count > 0:
            decision_context.add_proposed_action(
                "apply_memory_insights",
                {
                    "consolidation_count": dream_trace.consolidation_count,
                    "patterns_discovered": dream_trace.memory_patterns_discovered,
                    "compression_ratio": dream_trace.compression_ratio
                },
                priority="low"
            )

        # Pattern integration
        if dream_trace.top_k_motifs:
            decision_context.add_proposed_action(
                "integrate_discovered_patterns",
                {
                    "motifs": dream_trace.top_k_motifs[:5],  # Top 5 motifs
                    "association_count": len(dream_trace.associations)
                },
                priority="low"
            )

    async def _propose_decision_actions(self, decision_context: DecisionContext) -> None:
        """Propose meta-actions for decision optimization."""

        # Self-improvement based on decision history
        if len(self._decision_history) > 10:
            recent_approvals = sum(1 for d in self._decision_history[-10:] if d.guardian_approved)
            approval_rate = recent_approvals / 10

            if approval_rate < 0.7:
                decision_context.add_proposed_action(
                    "improve_decision_quality",
                    {
                        "recent_approval_rate": approval_rate,
                        "target_rate": 0.85,
                        "improvement_strategy": "constraint_learning"
                    },
                    priority="medium"
                )

    async def _propose_maintenance_actions(self, decision_context: DecisionContext) -> None:
        """Propose system maintenance actions."""

        # Periodic cleanup
        time_since_last_decision = time.time() - self._last_decision_time
        if time_since_last_decision > 300:  # 5 minutes
            decision_context.add_proposed_action(
                "periodic_cleanup",
                {
                    "cleanup_type": "memory_buffers",
                    "last_cleanup": self._last_decision_time
                },
                priority="low"
            )

    async def _propose_optimization_actions(self, decision_context: DecisionContext) -> None:
        """Propose performance optimization actions."""

        # Latency optimization
        if self._decision_latencies and len(self._decision_latencies) > 5:
            avg_latency = sum(self._decision_latencies[-5:]) / 5
            if avg_latency > 100:  # 100ms threshold
                decision_context.add_proposed_action(
                    "optimize_decision_latency",
                    {
                        "current_avg_latency_ms": avg_latency,
                        "target_latency_ms": 50,
                        "optimization_area": "action_generation"
                    },
                    priority="low"
                )

    async def _calculate_confidence_score(self, decision_context: DecisionContext) -> float:
        """Calculate confidence score for proposed actions."""

        # Base confidence from consciousness level
        base_confidence = decision_context.consciousness_state.level

        # Adjust based on awareness quality
        if decision_context.awareness_snapshot:
            awareness_factor = 1.0 - (decision_context.awareness_snapshot.drift_ema * 0.2)
            base_confidence *= awareness_factor

        # Adjust based on reflection quality
        if decision_context.reflection_report:
            coherence_factor = decision_context.reflection_report.coherence_score
            base_confidence *= coherence_factor

        # Adjust based on action complexity
        action_count = len(decision_context.proposed_actions)
        complexity_penalty = max(0.1, 1.0 - (action_count * 0.05))
        base_confidence *= complexity_penalty

        # Historical success rate
        if self._total_decisions > 0:
            historical_success = self._approval_count / self._total_decisions
            base_confidence = (base_confidence * 0.8) + (historical_success * 0.2)

        return max(0.0, min(1.0, base_confidence))

    async def _validate_with_guardian(self, decision_context: DecisionContext) -> GuardianResponse:
        """Validate proposed actions with Guardian system."""

        try:
            # Call external Guardian validator if available
            if self._guardian_validator:
                return await self._guardian_validator(decision_context)
            else:
                return self._default_guardian_validator(decision_context)
        except Exception as e:
            # Conservative default on Guardian failure
            return GuardianResponse(
                approved=False,
                reason=f"Guardian validation failed: {e!s}",
                confidence=0.0
            )

    def _default_guardian_validator(self, decision_context: DecisionContext) -> GuardianResponse:
        """Default Guardian validation logic."""

        # Check for critical actions
        critical_actions = [a for a in decision_context.proposed_actions if a.get("priority") == "critical"]
        if critical_actions and decision_context.confidence_score < 0.8:
            return GuardianResponse(
                approved=False,
                reason="Critical actions require high confidence score",
                confidence=0.9
            )

        # Check for high-risk actions
        high_risk_types = ["system_shutdown", "data_deletion", "security_override"]
        risky_actions = [a for a in decision_context.proposed_actions if a.get("type") in high_risk_types]
        if risky_actions:
            return GuardianResponse(
                approved=False,
                reason="High-risk actions blocked by default Guardian",
                confidence=1.0
            )

        # Approve low-risk actions with sufficient confidence
        if decision_context.confidence_score >= 0.6:
            return GuardianResponse(
                approved=True,
                reason="Actions approved - sufficient confidence and low risk",
                confidence=decision_context.confidence_score,
                constraints={"max_execution_time_ms": 1000}
            )

        return GuardianResponse(
            approved=False,
            reason="Insufficient confidence score for autonomous action",
            confidence=decision_context.confidence_score
        )

    async def _execute_approved_actions(
        self,
        decision_context: DecisionContext,
        constraints: dict[str, Any]
    ) -> None:
        """Execute Guardian-approved actions."""

        max_execution_time = constraints.get("max_execution_time_ms", 1000) / 1000.0
        execution_start = time.time()

        for action in decision_context.proposed_actions:
            # Check execution time budget
            if time.time() - execution_start > max_execution_time:
                break

            action_type = action.get("type", "unknown")
            action_handler = self._action_handlers.get(action_type)

            if action_handler:
                try:
                    await action_handler(action.get("parameters", {}))
                    autonomous_actions_total.labels(
                        component=self._component_id,
                        action_type=action_type,
                        status="success"
                    ).inc()
                except Exception:
                    autonomous_actions_total.labels(
                        component=self._component_id,
                        action_type=action_type,
                        status="error"
                    ).inc()
            else:
                # Log unhandled action type
                autonomous_actions_total.labels(
                    component=self._component_id,
                    action_type=action_type,
                    status="unhandled"
                ).inc()

    def _register_default_actions(self) -> None:
        """Register default action handlers."""

        self._action_handlers.update({
            "stabilize_drift": self._handle_stabilize_drift,
            "reduce_load": self._handle_reduce_load,
            "respond_to_anomalies": self._handle_respond_to_anomalies,
            "improve_coherence": self._handle_improve_coherence,
            "optimize_reflection": self._handle_optimize_reflection,
            "apply_memory_insights": self._handle_apply_memory_insights,
            "integrate_discovered_patterns": self._handle_integrate_patterns,
            "improve_decision_quality": self._handle_improve_decision_quality,
            "periodic_cleanup": self._handle_periodic_cleanup,
            "optimize_decision_latency": self._handle_optimize_latency
        })

    async def _handle_stabilize_drift(self, parameters: dict[str, Any]) -> None:
        """Handle drift stabilization action."""
        # Placeholder for drift stabilization logic
        pass

    async def _handle_reduce_load(self, parameters: dict[str, Any]) -> None:
        """Handle load reduction action."""
        # Placeholder for load reduction logic
        pass

    async def _handle_respond_to_anomalies(self, parameters: dict[str, Any]) -> None:
        """Handle anomaly response action."""
        # Placeholder for anomaly response logic
        pass

    async def _handle_improve_coherence(self, parameters: dict[str, Any]) -> None:
        """Handle coherence improvement action."""
        # Placeholder for coherence improvement logic
        pass

    async def _handle_optimize_reflection(self, parameters: dict[str, Any]) -> None:
        """Handle reflection optimization action."""
        # Placeholder for reflection optimization logic
        pass

    async def _handle_apply_memory_insights(self, parameters: dict[str, Any]) -> None:
        """Handle memory insights application action."""
        # Placeholder for memory insights application logic
        pass

    async def _handle_integrate_patterns(self, parameters: dict[str, Any]) -> None:
        """Handle pattern integration action."""
        # Placeholder for pattern integration logic
        pass

    async def _handle_improve_decision_quality(self, parameters: dict[str, Any]) -> None:
        """Handle decision quality improvement action."""
        # Placeholder for decision quality improvement logic
        pass

    async def _handle_periodic_cleanup(self, parameters: dict[str, Any]) -> None:
        """Handle periodic cleanup action."""
        # Placeholder for cleanup logic
        pass

    async def _handle_optimize_latency(self, parameters: dict[str, Any]) -> None:
        """Handle latency optimization action."""
        # Placeholder for latency optimization logic
        pass

    async def _update_metrics(self, decision_context: DecisionContext, latency: float) -> None:
        """Update performance metrics."""

        self._total_decisions += 1
        if decision_context.guardian_approved:
            self._approval_count += 1

        # Update latency tracking
        latency_ms = latency * 1000
        self._decision_latencies.append(latency_ms)
        if len(self._decision_latencies) > 100:
            self._decision_latencies.pop(0)

        # Update confidence tracking
        self._confidence_scores.append(decision_context.confidence_score)
        if len(self._confidence_scores) > 100:
            self._confidence_scores.pop(0)

        # Update Prometheus metrics
        approval_rate = self._approval_count / self._total_decisions
        guardian_approval_rate.labels(component=self._component_id).set(approval_rate)
        decision_confidence_score.labels(component=self._component_id).set(decision_context.confidence_score)
        decision_latency_seconds.labels(component=self._component_id).observe(latency)

        # Count decision cycles by action type
        for action in decision_context.proposed_actions:
            action_type = action.get("type", "unknown")
            decision_cycles_total.labels(
                component=self._component_id,
                action_type=action_type
            ).inc()

        self._last_decision_time = time.time()

    def get_performance_stats(self) -> dict[str, float]:
        """Get current performance statistics."""
        if self._total_decisions == 0:
            return {
                "total_decisions": 0,
                "approval_rate": 0.0,
                "average_confidence": 0.0,
                "average_latency_ms": 0.0
            }

        avg_confidence = sum(self._confidence_scores) / len(self._confidence_scores) if self._confidence_scores else 0.0
        avg_latency = sum(self._decision_latencies) / len(self._decision_latencies) if self._decision_latencies else 0.0

        return {
            "total_decisions": self._total_decisions,
            "approval_rate": self._approval_count / self._total_decisions,
            "average_confidence": avg_confidence,
            "average_latency_ms": avg_latency,
            "recent_decisions": len(self._decision_history)
        }

    def reset_state(self) -> None:
        """Reset internal state for testing or reconfiguration."""
        self._decision_history.clear()
        self._approval_count = 0
        self._total_decisions = 0
        self._decision_latencies.clear()
        self._confidence_scores.clear()
        self._last_decision_time = 0.0


# Export for public API
__all__ = ["AutoConsciousness", "GuardianResponse"]
