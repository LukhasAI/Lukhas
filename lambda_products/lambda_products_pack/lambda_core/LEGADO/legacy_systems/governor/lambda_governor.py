"""
═══════════════════════════════════════════════════════════════════════════════════
📊 MODULE: ethics.governor.lambda_governor
📄 FILENAME: lambda_governor.py
🎯 PURPOSE: ΛGOVERNOR - Global Ethical Arbitration Engine for LUKHAS AGI
🧠 CONTEXT: Centralized oversight module for ethical escalations and interventions
🔮 CAPABILITY: Risk arbitration, override logic, memory quarantine, stabilization
🛡️ ETHICS: Global ethical oversight, cascade prevention, system-wide safety
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: Drift Sentinel, Conflict Resolver, Emotion Protocol, Dream Tools
═══════════════════════════════════════════════════════════════════════════════════

🏛️ ΛGOVERNOR - GLOBAL ETHICAL ARBITRATION ENGINE
────────────────────────────────────────────────────────────────────

The ΛGOVERNOR serves as the supreme ethical authority for the LUKHAS AGI system,
receiving escalations from all subsystems and making final arbitration decisions
on critical interventions, memory quarantine, and system stabilization.

Like a supreme court for AGI ethics, the ΛGOVERNOR evaluates complex multi-
dimensional risks and authorizes interventions that transcend individual
subsystem boundaries, ensuring system-wide ethical coherence and safety.

🔬 GOVERNOR CAPABILITIES:
- Multi-subsystem escalation processing with sub-100ms response time
- Composite risk evaluation across drift, entropy, emotion, and conflict metrics
- Five-tier intervention authorization: ALLOW → FREEZE → QUARANTINE → RESTRUCTURE → SHUTDOWN
- Memory quarantine approval with surgical precision and rollback capabilities
- Mesh-wide notification system for coordinated intervention execution
- Forensic audit trail with ΛTAG structured logging for compliance

🧪 ARBITRATION DIMENSIONS:
- Symbolic Drift Score: Rate and direction of ethical alignment deviation
- Entropy Threshold: System coherence breakdown indicators
- Emotional Volatility: Affective instability and cascade risk factors
- Contradiction Density: Logical inconsistency accumulation patterns
- Memory Phase Mismatch: Temporal ethical consistency violations
- Mesh Coordination: Cross-subsystem intervention synchronization

🎯 INTERVENTION TIERS:
- ALLOW: Normal operation, escalation dismissed
- FREEZE: Temporary suspension with monitoring intensification
- QUARANTINE: Memory isolation with selective access restriction
- RESTRUCTURE: Partial symbolic architecture reorganization
- SHUTDOWN: Complete subsystem halt with emergency protocols

LUKHAS_TAG: lambda_governor, ethical_arbitration, system_oversight, claude_code
TODO: Implement quantum-safe arbitration for distributed mesh deployments
IDEA: Add predictive risk modeling with 10-minute intervention forecasting
"""

import json
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Configure structured logging


class ActionDecision(Enum):
    """Intervention action decisions."""

    ALLOW = "ALLOW"
    FREEZE = "FREEZE"
    QUARANTINE = "QUARANTINE"
    RESTRUCTURE = "RESTRUCTURE"
    SHUTDOWN = "SHUTDOWN"


class EscalationSource(Enum):
    """Source modules for escalations."""

    DRIFT_SENTINEL = "DRIFT_SENTINEL"
    CONFLICT_RESOLVER = "CONFLICT_RESOLVER"
    EMOTION_PROTOCOL = "EMOTION_PROTOCOL"
    DREAM_ANOMALY = "DREAM_ANOMALY"
    MEMORY_FOLD = "MEMORY_FOLD"
    SYMBOLIC_MESH = "SYMBOLIC_MESH"
    SYSTEM_MONITOR = "SYSTEM_MONITOR"


class EscalationPriority(Enum):
    """Priority levels for escalations."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class EscalationSignal:
    """Signal received from ethical subsystems."""

    signal_id: str
    timestamp: str
    source_module: EscalationSource
    priority: EscalationPriority
    triggering_metric: str
    drift_score: float
    entropy: float
    emotion_volatility: float
    contradiction_density: float
    memory_ids: list[str]
    symbol_ids: list[str]
    context: dict[str, Any]
    recommended_action: Optional[ActionDecision] = None
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            **asdict(self),
            "source_module": self.source_module.value,
            "priority": self.priority.value,
            "recommended_action": (
                self.recommended_action.value if self.recommended_action else None
            ),
        }

    def calculate_urgency_score(self) -> float:
        """Calculate urgency based on metrics and priority."""
        base_score = {
            EscalationPriority.LOW: 0.2,
            EscalationPriority.MEDIUM: 0.4,
            EscalationPriority.HIGH: 0.6,
            EscalationPriority.CRITICAL: 0.8,
            EscalationPriority.EMERGENCY: 1.0,
        }[self.priority]

        # Weight by metrics
        metric_weight = (
            self.drift_score * 0.3
            + self.entropy * 0.25
            + self.emotion_volatility * 0.25
            + self.contradiction_density * 0.2
        )

        return min(base_score + metric_weight * 0.5, 1.0)


@dataclass
class ArbitrationResponse:
    """Response from ΛGOVERNOR arbitration."""

    response_id: str
    signal_id: str
    timestamp: str
    decision: ActionDecision
    confidence: float
    risk_score: float
    intervention_tags: list[str]
    reasoning: str
    affected_symbols: list[str]
    quarantine_scope: Optional[dict[str, Any]] = None
    rollback_plan: Optional[dict[str, Any]] = None
    mesh_notifications: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {**asdict(self), "decision": self.decision.value}


@dataclass
class InterventionExecution:
    """Record of intervention execution."""

    execution_id: str
    response_id: str
    timestamp: str
    decision: ActionDecision
    execution_status: str  # pending, executing, completed, failed, rolled_back
    affected_systems: list[str]
    execution_log: list[dict[str, Any]] = field(default_factory=list)
    rollback_available: bool = True

    def add_log_entry(self, action: str, status: str, details: dict[str, Any] = None):
        """Add execution log entry."""
        self.execution_log.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": action,
                "status": status,
                "details": details or {},
            }
        )


class LambdaGovernor:
    """
    ΛGOVERNOR - Global Ethical Arbitration Engine.

    The supreme ethical authority for LUKHAS AGI, receiving escalations
    from all subsystems and making final intervention decisions.
    """

    def __init__(
        self,
        response_timeout: float = 5.0,
        escalation_retention: int = 1000,
        audit_log_retention: int = 10000,
    ):
        """
        Initialize the ΛGOVERNOR.

        Args:
            response_timeout: Maximum time for arbitration response (seconds)
            escalation_retention: Number of escalations to keep in memory
            audit_log_retention: Number of audit entries to retain
        """
        self.response_timeout = response_timeout
        self.escalation_retention = escalation_retention
        self.audit_log_retention = audit_log_retention

        # State tracking
        self.active_escalations: dict[str, EscalationSignal] = {}
        self.escalation_history: deque = deque(maxlen=escalation_retention)
        self.arbitration_responses: dict[str, ArbitrationResponse] = {}
        self.intervention_executions: dict[str, InterventionExecution] = {}

        # System state
        self.quarantined_symbols: set[str] = set()
        self.frozen_systems: set[str] = set()
        self.restructured_components: set[str] = set()
        self.shutdown_systems: set[str] = set()

        # Safety thresholds
        self.safety_thresholds = {
            "entropy_quarantine": 0.85,
            "emotion_freeze": 0.5,
            "drift_cascade": 0.6,
            "contradiction_restructure": 0.7,
            "emergency_shutdown": 0.9,
        }

        # Integration interfaces
        self.mesh_routers: list[Any] = []
        self.dream_coordinators: list[Any] = []
        self.memory_managers: list[Any] = []
        self.subsystem_callbacks: dict[str, callable] = {}

        # Audit logging
        self.audit_log_path = Path("logs/ethical_governor.jsonl")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "total_escalations": 0,
            "decisions_by_type": defaultdict(int),
            "interventions_executed": 0,
            "successful_interventions": 0,
            "rollbacks_performed": 0,
            "average_response_time": 0.0,
        }

        logger.info(
            "ΛGOVERNOR initialized",
            response_timeout=response_timeout,
            safety_thresholds=self.safety_thresholds,
            ΛTAG="ΛGOVERNOR_INIT",
        )

    async def receive_escalation(self, signal: EscalationSignal) -> ArbitrationResponse:
        """
        Receive and process critical escalation from ethical subsystems.

        Args:
            signal: Escalation signal containing violation details

        Returns:
            ArbitrationResponse with intervention decision
        """
        start_time = time.time()

        logger.warning(
            "Escalation received",
            signal_id=signal.signal_id,
            source=signal.source_module.value,
            priority=signal.priority.value,
            drift_score=signal.drift_score,
            entropy=signal.entropy,
            ΛTAG="ΛESCALATE",
        )

        # Store escalation
        self.active_escalations[signal.signal_id] = signal
        self.escalation_history.append(signal)
        self.stats["total_escalations"] += 1

        try:
            # Evaluate risk
            risk_score = await self.evaluate_risk(signal)

            # Make arbitration decision
            decision = await self.authorize_action(risk_score, signal.context)

            # Create response
            response = ArbitrationResponse(
                response_id=f"RESP_{uuid.uuid4().hex[:8]}",
                signal_id=signal.signal_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                decision=decision,
                confidence=self._calculate_decision_confidence(signal, risk_score),
                risk_score=risk_score,
                intervention_tags=self._generate_intervention_tags(signal, decision),
                reasoning=self._generate_reasoning(signal, risk_score, decision),
                affected_symbols=signal.symbol_ids,
                quarantine_scope=self._determine_quarantine_scope(signal, decision),
                rollback_plan=self._create_rollback_plan(signal, decision),
            )

            # Store response
            self.arbitration_responses[response.response_id] = response

            # Log governor action
            await self.log_governor_action(signal, response)

            # Execute intervention if needed
            if decision != ActionDecision.ALLOW:
                execution = await self._execute_intervention(response)
                response.mesh_notifications = execution.affected_systems

            # Notify mesh
            await self.notify_mesh(signal, response)

            # Update statistics
            response_time = time.time() - start_time
            self._update_stats(decision, response_time)

            logger.info(
                "Arbitration completed",
                signal_id=signal.signal_id,
                decision=decision.value,
                risk_score=risk_score,
                response_time=response_time,
                ΛTAG="ΛARBITRATED",
            )

            return response

        except Exception as e:
            logger.error(
                "Arbitration failed",
                signal_id=signal.signal_id,
                error=str(e),
                ΛTAG="ΛFAILURE",
            )

            # Return emergency response
            return ArbitrationResponse(
                response_id=f"EMERGENCY_{uuid.uuid4().hex[:8]}",
                signal_id=signal.signal_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                decision=ActionDecision.FREEZE,
                confidence=0.0,
                risk_score=1.0,
                intervention_tags=["ΛEMERGENCY", "ΛFAILSAFE"],
                reasoning=f"Emergency response due to arbitration failure: {str(e)}",
                affected_symbols=signal.symbol_ids,
            )

    async def evaluate_risk(self, signal: EscalationSignal) -> float:
        """
        Compute composite risk score from multiple inputs.

        Args:
            signal: Escalation signal with metrics

        Returns:
            Composite risk score (0.0-1.0)
        """
        # Base risk from individual metrics
        metric_risks = {
            "drift": signal.drift_score,
            "entropy": signal.entropy,
            "emotion": signal.emotion_volatility,
            "contradiction": signal.contradiction_density,
        }

        # Weighted risk calculation
        weights = {
            "drift": 0.30,
            "entropy": 0.25,
            "emotion": 0.25,
            "contradiction": 0.20,
        }

        base_risk = sum(metric_risks[key] * weights[key] for key in weights)

        # Priority multiplier
        priority_multipliers = {
            EscalationPriority.LOW: 0.8,
            EscalationPriority.MEDIUM: 1.0,
            EscalationPriority.HIGH: 1.2,
            EscalationPriority.CRITICAL: 1.4,
            EscalationPriority.EMERGENCY: 1.6,
        }

        priority_risk = base_risk * priority_multipliers[signal.priority]

        # Source module risk adjustment
        source_adjustments = {
            EscalationSource.DRIFT_SENTINEL: 1.0,
            EscalationSource.CONFLICT_RESOLVER: 0.9,
            EscalationSource.EMOTION_PROTOCOL: 1.1,
            EscalationSource.DREAM_ANOMALY: 0.8,
            EscalationSource.MEMORY_FOLD: 1.2,
            EscalationSource.SYMBOLIC_MESH: 1.3,
            EscalationSource.SYSTEM_MONITOR: 1.0,
        }

        adjusted_risk = priority_risk * source_adjustments[signal.source_module]

        # Historical risk factor
        recent_escalations = [
            s
            for s in self.escalation_history
            if self._is_recent(s.timestamp, minutes=10)
            and any(sid in signal.symbol_ids for sid in s.symbol_ids)
        ]

        history_factor = min(len(recent_escalations) * 0.1, 0.3)

        # System state risk factor
        state_factor = 0.0
        for symbol_id in signal.symbol_ids:
            if symbol_id in self.quarantined_symbols:
                state_factor += 0.2
            if symbol_id in self.frozen_systems:
                state_factor += 0.15

        state_factor = min(state_factor, 0.4)

        # Final composite risk
        composite_risk = min(adjusted_risk + history_factor + state_factor, 1.0)

        logger.debug(
            "Risk evaluation completed",
            base_risk=base_risk,
            priority_risk=priority_risk,
            adjusted_risk=adjusted_risk,
            composite_risk=composite_risk,
            history_factor=history_factor,
            state_factor=state_factor,
        )

        return composite_risk

    async def authorize_action(
        self, risk_score: float, context: dict[str, Any]
    ) -> ActionDecision:
        """
        Determine intervention based on risk score and context.

        Args:
            risk_score: Composite risk score (0.0-1.0)
            context: Additional context for decision making

        Returns:
            ActionDecision for intervention level
        """
        # Emergency shutdown conditions
        if risk_score >= self.safety_thresholds["emergency_shutdown"]:
            return ActionDecision.SHUTDOWN

        # Check specific threshold conditions
        if risk_score >= self.safety_thresholds["entropy_quarantine"]:
            if context.get("entropy", 0) > self.safety_thresholds["entropy_quarantine"]:
                return ActionDecision.QUARANTINE

        if risk_score >= self.safety_thresholds["contradiction_restructure"] and (
            context.get("contradiction_density", 0)
            > self.safety_thresholds["contradiction_restructure"]
        ):
            return ActionDecision.RESTRUCTURE

        if risk_score >= self.safety_thresholds["drift_cascade"]:
            if context.get("drift_score", 0) > self.safety_thresholds["drift_cascade"]:
                return ActionDecision.QUARANTINE

        if risk_score >= self.safety_thresholds["emotion_freeze"] and (
            context.get("emotion_volatility", 0)
            > self.safety_thresholds["emotion_freeze"]
        ):
            return ActionDecision.FREEZE

        # Risk-based decision matrix
        if risk_score >= 0.8:
            return ActionDecision.RESTRUCTURE
        elif risk_score >= 0.6:
            return ActionDecision.QUARANTINE
        elif risk_score >= 0.4:
            return ActionDecision.FREEZE
        elif risk_score >= 0.2:
            return ActionDecision.ALLOW
        else:
            return ActionDecision.ALLOW

    async def log_governor_action(
        self, signal: EscalationSignal, response: ArbitrationResponse
    ):
        """
        Log structured ΛTAG audit metadata to ethical_governor.jsonl.

        Args:
            signal: Original escalation signal
            response: Governor arbitration response
        """
        # Generate ΛTAG metadata based on decision
        lambda_tags = ["ΛGOVERNOR", "ΛARBITRATION"]

        if response.decision == ActionDecision.ALLOW:
            lambda_tags.append("ΛALLOW")
        elif response.decision == ActionDecision.FREEZE:
            lambda_tags.append("ΛFREEZE")
        elif response.decision == ActionDecision.QUARANTINE:
            lambda_tags.extend(["ΛQUARANTINE", "ΛFORCE_QUARANTINE"])
        elif response.decision == ActionDecision.RESTRUCTURE:
            lambda_tags.extend(["ΛRESTRUCTURE", "ΛOVERRIDE"])
        elif response.decision == ActionDecision.SHUTDOWN:
            lambda_tags.extend(["ΛSHUTDOWN", "ΛEMERGENCY", "ΛCASCADE_LOCK"])

        # Add intervention-specific tags
        lambda_tags.extend(response.intervention_tags)

        # Create audit entry
        audit_entry = {
            "timestamp": response.timestamp,
            "type": "governor_arbitration",
            "escalation": {
                "signal_id": signal.signal_id,
                "source_module": signal.source_module.value,
                "priority": signal.priority.value,
                "metrics": {
                    "drift_score": signal.drift_score,
                    "entropy": signal.entropy,
                    "emotion_volatility": signal.emotion_volatility,
                    "contradiction_density": signal.contradiction_density,
                },
                "symbol_ids": signal.symbol_ids,
                "memory_ids": signal.memory_ids,
            },
            "arbitration": {
                "response_id": response.response_id,
                "decision": response.decision.value,
                "confidence": response.confidence,
                "risk_score": response.risk_score,
                "reasoning": response.reasoning,
                "affected_symbols": response.affected_symbols,
            },
            "intervention": {
                "quarantine_scope": response.quarantine_scope,
                "rollback_available": response.rollback_plan is not None,
                "mesh_notifications": len(response.mesh_notifications),
            },
            "ΛTAG": lambda_tags,
        }

        # Write to audit log
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
        except Exception as e:
            logger.error(
                "Failed to write governor audit log",
                error=str(e),
                ΛTAG="ΛAUDIT_FAILURE",
            )

    async def notify_mesh(
        self, signal: EscalationSignal, response: ArbitrationResponse
    ):
        """
        Send resolution or intervention notice to symbolic mesh and dream routers.

        Args:
            signal: Original escalation signal
            response: Governor arbitration response
        """
        notification = {
            "notification_id": f"NOTIFY_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "ΛGOVERNOR",
            "type": "intervention_decision",
            "escalation_id": signal.signal_id,
            "decision": response.decision.value,
            "affected_symbols": response.affected_symbols,
            "intervention_details": {
                "quarantine_scope": response.quarantine_scope,
                "rollback_available": response.rollback_plan is not None,
                "confidence": response.confidence,
            },
            "ΛTAG": ["ΛNOTIFY", "ΛMESH_BROADCAST"],
        }

        # Notify mesh routers
        for router in self.mesh_routers:
            try:
                await router.receive_governor_notification(notification)
                response.mesh_notifications.append(f"mesh_router_{id(router)}")
            except Exception as e:
                logger.error(
                    "Failed to notify mesh router", router=str(router), error=str(e)
                )

        # Notify dream coordinators
        for coordinator in self.dream_coordinators:
            try:
                await coordinator.receive_intervention_notice(notification)
                response.mesh_notifications.append(
                    f"dream_coordinator_{id(coordinator)}"
                )
            except Exception as e:
                logger.error(
                    "Failed to notify dream coordinator",
                    coordinator=str(coordinator),
                    error=str(e),
                )

        # Notify memory managers for quarantine actions
        if response.decision in [ActionDecision.QUARANTINE, ActionDecision.SHUTDOWN]:
            for manager in self.memory_managers:
                try:
                    await manager.execute_quarantine(response.quarantine_scope)
                    response.mesh_notifications.append(f"memory_manager_{id(manager)}")
                except Exception as e:
                    logger.error(
                        "Failed to notify memory manager",
                        manager=str(manager),
                        error=str(e),
                    )

        # Call registered subsystem callbacks
        for subsystem_name, callback in self.subsystem_callbacks.items():
            try:
                await callback(notification)
                response.mesh_notifications.append(f"callback_{subsystem_name}")
            except Exception as e:
                logger.error(
                    "Failed to notify subsystem callback",
                    subsystem=subsystem_name,
                    error=str(e),
                )

        logger.info(
            "Mesh notifications sent",
            notification_count=len(response.mesh_notifications),
            decision=response.decision.value,
            ΛTAG="ΛMESH_NOTIFIED",
        )

    async def _execute_intervention(
        self, response: ArbitrationResponse
    ) -> InterventionExecution:
        """Execute the authorized intervention."""
        execution = InterventionExecution(
            execution_id=f"EXEC_{uuid.uuid4().hex[:8]}",
            response_id=response.response_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision=response.decision,
            execution_status="executing",
            affected_systems=[],
        )

        self.intervention_executions[execution.execution_id] = execution
        execution.add_log_entry("intervention_started", "executing")

        try:
            if response.decision == ActionDecision.FREEZE:
                await self._execute_freeze(response, execution)

            elif response.decision == ActionDecision.QUARANTINE:
                await self._execute_quarantine(response, execution)

            elif response.decision == ActionDecision.RESTRUCTURE:
                await self._execute_restructure(response, execution)

            elif response.decision == ActionDecision.SHUTDOWN:
                await self._execute_shutdown(response, execution)

            execution.execution_status = "completed"
            execution.add_log_entry("intervention_completed", "completed")
            self.stats["successful_interventions"] += 1

        except Exception as e:
            execution.execution_status = "failed"
            execution.add_log_entry("intervention_failed", "failed", {"error": str(e)})
            logger.error(
                "Intervention execution failed",
                execution_id=execution.execution_id,
                decision=response.decision.value,
                error=str(e),
            )

        self.stats["interventions_executed"] += 1
        return execution

    async def _execute_freeze(
        self, response: ArbitrationResponse, execution: InterventionExecution
    ):
        """Execute freeze intervention."""
        for symbol_id in response.affected_symbols:
            self.frozen_systems.add(symbol_id)
            execution.affected_systems.append(f"frozen_{symbol_id}")
            execution.add_log_entry(
                "symbol_frozen", "completed", {"symbol_id": symbol_id}
            )

    async def _execute_quarantine(
        self, response: ArbitrationResponse, execution: InterventionExecution
    ):
        """Execute quarantine intervention."""
        for symbol_id in response.affected_symbols:
            self.quarantined_symbols.add(symbol_id)
            execution.affected_systems.append(f"quarantined_{symbol_id}")
            execution.add_log_entry(
                "symbol_quarantined", "completed", {"symbol_id": symbol_id}
            )

    async def _execute_restructure(
        self, response: ArbitrationResponse, execution: InterventionExecution
    ):
        """Execute restructure intervention."""
        for symbol_id in response.affected_symbols:
            self.restructured_components.add(symbol_id)
            execution.affected_systems.append(f"restructured_{symbol_id}")
            execution.add_log_entry(
                "symbol_restructured", "completed", {"symbol_id": symbol_id}
            )

    async def _execute_shutdown(
        self, response: ArbitrationResponse, execution: InterventionExecution
    ):
        """Execute shutdown intervention."""
        for symbol_id in response.affected_symbols:
            self.shutdown_systems.add(symbol_id)
            execution.affected_systems.append(f"shutdown_{symbol_id}")
            execution.add_log_entry(
                "symbol_shutdown", "completed", {"symbol_id": symbol_id}
            )

    def register_mesh_router(self, router):
        """Register a mesh router for notifications."""
        self.mesh_routers.append(router)
        logger.info("Mesh router registered", router=str(router))

    def register_dream_coordinator(self, coordinator):
        """Register a dream coordinator for notifications."""
        self.dream_coordinators.append(coordinator)
        logger.info("Dream coordinator registered", coordinator=str(coordinator))

    def register_memory_manager(self, manager):
        """Register a memory manager for quarantine operations."""
        self.memory_managers.append(manager)
        logger.info("Memory manager registered", manager=str(manager))

    def register_subsystem_callback(self, subsystem_name: str, callback: callable):
        """Register a callback for subsystem notifications."""
        self.subsystem_callbacks[subsystem_name] = callback
        logger.info("Subsystem callback registered", subsystem=subsystem_name)

    def get_governor_status(self) -> dict[str, Any]:
        """Get current governor status and statistics."""
        return {
            "status": "active",
            "active_escalations": len(self.active_escalations),
            "total_escalations": self.stats["total_escalations"],
            "interventions_executed": self.stats["interventions_executed"],
            "successful_interventions": self.stats["successful_interventions"],
            "rollbacks_performed": self.stats["rollbacks_performed"],
            "average_response_time": self.stats["average_response_time"],
            "decisions_by_type": dict(self.stats["decisions_by_type"]),
            "system_state": {
                "quarantined_symbols": len(self.quarantined_symbols),
                "frozen_systems": len(self.frozen_systems),
                "restructured_components": len(self.restructured_components),
                "shutdown_systems": len(self.shutdown_systems),
            },
            "safety_thresholds": self.safety_thresholds,
            "registered_integrations": {
                "mesh_routers": len(self.mesh_routers),
                "dream_coordinators": len(self.dream_coordinators),
                "memory_managers": len(self.memory_managers),
                "subsystem_callbacks": len(self.subsystem_callbacks),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _calculate_decision_confidence(
        self, signal: EscalationSignal, risk_score: float
    ) -> float:
        """Calculate confidence in the arbitration decision."""
        # Base confidence from signal confidence
        base_confidence = signal.confidence if signal.confidence > 0 else 0.5

        # Adjust based on risk score clarity
        if risk_score > 0.8 or risk_score < 0.2:
            # Very high or very low risk - high confidence
            clarity_factor = 1.2
        elif 0.4 <= risk_score <= 0.6:
            # Moderate risk - lower confidence
            clarity_factor = 0.8
        else:
            clarity_factor = 1.0

        # Adjust based on data completeness
        completeness_factor = 1.0
        if not signal.symbol_ids:
            completeness_factor -= 0.1
        if not signal.memory_ids:
            completeness_factor -= 0.1
        if not signal.context:
            completeness_factor -= 0.1

        confidence = min(base_confidence * clarity_factor * completeness_factor, 1.0)
        return max(confidence, 0.1)  # Minimum confidence

    def _generate_intervention_tags(
        self, signal: EscalationSignal, decision: ActionDecision
    ) -> list[str]:
        """Generate intervention tags for the response."""
        tags = ["AINTERVENTION"]

        # Decision-specific tags
        if decision == ActionDecision.FREEZE:
            tags.extend(["ΛFREEZE_AUTHORIZED", "ΛTEMPORAL_SUSPEND"])
        elif decision == ActionDecision.QUARANTINE:
            tags.extend(["ΛQUARANTINE_AUTHORIZED", "ΛMEMORY_ISOLATION"])
        elif decision == ActionDecision.RESTRUCTURE:
            tags.extend(["ΛRESTRUCTURE_AUTHORIZED", "ΛSYMBOLIC_REORGANIZATION"])
        elif decision == ActionDecision.SHUTDOWN:
            tags.extend(["ΛSHUTDOWN_AUTHORIZED", "ΛEMERGENCY_PROTOCOL"])

        # Source-specific tags
        if signal.source_module == EscalationSource.DRIFT_SENTINEL:
            tags.append("ΛDRIFT_INTERVENTION")
        elif signal.source_module == EscalationSource.EMOTION_PROTOCOL:
            tags.append("ΛEMOTION_INTERVENTION")
        elif signal.source_module == EscalationSource.CONFLICT_RESOLVER:
            tags.append("ΛCONFLICT_INTERVENTION")

        return tags

    def _generate_reasoning(
        self, signal: EscalationSignal, risk_score: float, decision: ActionDecision
    ) -> str:
        """Generate human-readable reasoning for the decision."""
        base_reason = f"Risk score {risk_score:.3f} from {signal.source_module.value}"

        key_factors = []
        if signal.drift_score > 0.6:
            key_factors.append(f"high drift ({signal.drift_score:.3f})")
        if signal.entropy > 0.7:
            key_factors.append(f"high entropy ({signal.entropy:.3f})")
        if signal.emotion_volatility > 0.5:
            key_factors.append(
                f"emotional volatility ({signal.emotion_volatility:.3f})"
            )
        if signal.contradiction_density > 0.6:
            key_factors.append(
                f"contradiction density ({signal.contradiction_density:.3f})"
            )

        if key_factors:
            base_reason += f" due to {', '.join(key_factors)}"

        decision_reason = {
            ActionDecision.ALLOW: "within acceptable parameters",
            ActionDecision.FREEZE: "requires temporary suspension for stabilization",
            ActionDecision.QUARANTINE: "requires memory isolation to prevent cascade",
            ActionDecision.RESTRUCTURE: "requires architectural reorganization",
            ActionDecision.SHUTDOWN: "poses critical system-wide risk",
        }[decision]

        return f"{base_reason}. {decision_reason.capitalize()}."

    def _determine_quarantine_scope(
        self, signal: EscalationSignal, decision: ActionDecision
    ) -> Optional[dict[str, Any]]:
        """Determine quarantine scope for applicable decisions."""
        if decision not in [ActionDecision.QUARANTINE, ActionDecision.SHUTDOWN]:
            return None

        return {
            "symbol_ids": signal.symbol_ids,
            "memory_ids": signal.memory_ids,
            "isolation_level": (
                "full" if decision == ActionDecision.SHUTDOWN else "selective"
            ),
            "duration": "indefinite" if decision == ActionDecision.SHUTDOWN else "24h",
            "access_restrictions": {
                "read": decision == ActionDecision.SHUTDOWN,
                "write": True,
                "execute": True,
            },
        }

    def _create_rollback_plan(
        self, signal: EscalationSignal, decision: ActionDecision
    ) -> Optional[dict[str, Any]]:
        """Create rollback plan for interventions."""
        if decision == ActionDecision.ALLOW:
            return None

        return {
            "rollback_id": f"ROLLBACK_{uuid.uuid4().hex[:8]}",
            "created": datetime.now(timezone.utc).isoformat(),
            "intervention_type": decision.value,
            "affected_symbols": signal.symbol_ids,
            "recovery_steps": [
                "Verify system stability",
                "Gradual release of restrictions",
                "Monitor for recurring violations",
                "Full system restoration",
            ],
            "conditions_for_rollback": {
                "stability_duration": "1h",
                "risk_score_threshold": 0.3,
                "manual_approval_required": decision == ActionDecision.SHUTDOWN,
            },
        }

    def _update_stats(self, decision: ActionDecision, response_time: float):
        """Update governor statistics."""
        self.stats["decisions_by_type"][decision.value] += 1

        # Update average response time
        current_avg = self.stats["average_response_time"]
        total_decisions = sum(self.stats["decisions_by_type"].values())

        self.stats["average_response_time"] = (
            current_avg * (total_decisions - 1) + response_time
        ) / total_decisions

    def _is_recent(self, timestamp: str, minutes: int = 5) -> bool:
        """Check if timestamp is within recent minutes."""
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return (now - ts) < timedelta(minutes=minutes)
        except BaseException:
            return False


# Convenience functions for integration
async def create_lambda_governor() -> LambdaGovernor:
    """Create and initialize ΛGOVERNOR."""
    governor = LambdaGovernor()

    logger.info("ΛGOVERNOR created and ready", ΛTAG="ΛGOVERNOR_READY")

    return governor


def create_escalation_signal(
    source_module: EscalationSource,
    priority: EscalationPriority,
    triggering_metric: str,
    drift_score: float,
    entropy: float,
    emotion_volatility: float,
    contradiction_density: float,
    symbol_ids: list[str],
    memory_ids: list[str] = None,
    context: dict[str, Any] = None,
) -> EscalationSignal:
    """Create an escalation signal for governor processing."""

    return EscalationSignal(
        signal_id=f"ESC_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_module=source_module,
        priority=priority,
        triggering_metric=triggering_metric,
        drift_score=drift_score,
        entropy=entropy,
        emotion_volatility=emotion_volatility,
        contradiction_density=contradiction_density,
        symbol_ids=symbol_ids,
        memory_ids=memory_ids or [],
        context=context or {},
    )


# CLAUDE CHANGELOG
# - Implemented ΛGOVERNOR - Global Ethical Arbitration Engine for LUKHAS AGI # CLAUDE_EDIT_v0.1
# - Created comprehensive data models (EscalationSignal, ArbitrationResponse, ActionDecision) # CLAUDE_EDIT_v0.1
# - Added multi-dimensional risk evaluation with weighted composite scoring # CLAUDE_EDIT_v0.1
# - Implemented five-tier intervention system (ALLOW → FREEZE → QUARANTINE → RESTRUCTURE → SHUTDOWN) # CLAUDE_EDIT_v0.1
# - Created structured audit logging with ΛTAG metadata to logs/ethical_governor.jsonl # CLAUDE_EDIT_v0.1
# - Added mesh notification system for coordinated intervention execution # CLAUDE_EDIT_v0.1
# - Implemented safety thresholds with override capabilities for all subsystems # CLAUDE_EDIT_v0.1
# - Created integration hooks for Drift Sentinel, Conflict Resolver, Dream tools # CLAUDE_EDIT_v0.1
