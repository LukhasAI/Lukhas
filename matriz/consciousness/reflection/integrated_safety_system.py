"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🛡️ LUKHAS AI - INTEGRATED SAFETY SYSTEM
║ Comprehensive safety, ethics, and compliance integration with event-bus,
║ colony, and swarm architecture
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: integrated_safety_system.py
║ Path: core/integrated_safety_system.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Safety Team
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module integrates all safety components into a unified system:
║
║ 🛡️ SAFETY COMPONENTS:
║ • Memory Safety System with drift tracking and reality anchors
║ • Bio-Symbolic Fallback Manager with 4-level degradation
║ • Quantized Thought Cycles for predictable processing
║ • Circuit Breakers and Rate Limiting
║
║ ⚖️ ETHICS & COMPLIANCE:
║ • Ethics Swarm Colony for distributed ethical reasoning
║ • Governance Colony for policy enforcement
║ • Compliance Validator for regulatory adherence
║ • Real-time ethical drift monitoring
║
║ 🌐 DISTRIBUTED ARCHITECTURE:
║ • Event-Bus for real-time safety event broadcasting
║ • Colony-based validation with consensus mechanisms
║ • Swarm intelligence for emergent safety behaviors
║ • No single point of failure design
║
║ 🔄 INTEGRATION FEATURES:
║ • Pre-action safety, ethics, and compliance checks
║ • Real-time monitoring with 100ms cycles
║ • Post-action auditing and learning
║ • Predictive threat detection and prevention
║
║ ΛTAG: ΛSAFETY, ΛETHICS, ΛCOMPLIANCE, ΛEVENTBUS, ΛCOLONY, ΛSWARM
╚══════════════════════════════════════════════════════════════════════════════════
"""

import logging
from datetime import timezone

import asyncio
import hashlib
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import numpy as np


try:
    from dashboard.core.fallback_system import DashboardFallbackSystem
except ImportError as import_error:

    class DashboardFallbackSystem(_FallbackComponent):
        pass


try:
    from bio.core.symbolic_fallback_systems import BioSymbolicFallbackManager, FallbackLevel
except ImportError as import_error:

    class FallbackLevel(Enum):  # type: ignore[no-redef]
        MINIMAL = "minimal"
        MODERATE = "moderate"
        SEVERE = "severe"
        CRITICAL = "critical"

    class BioSymbolicFallbackManager(_FallbackComponent):
        pass


try:
    from ethics.compliance_validator import ComplianceValidator
except ImportError as import_error:

    class ComplianceValidator(_FallbackComponent):
        pass


try:
    from core.colonies.base_colony import BaseColony
except ImportError as import_error:

    class BaseColony(_FallbackComponent):
        pass


try:
    from core.colonies.ethics_swarm_colony import (
        EthicalDecisionRequest,
        EthicalDecisionType,
        EthicsSwarmColony,
    )
except ImportError as import_error:

    @dataclass
    class EthicalDecisionRequest:  # type: ignore[no-redef]
        request_id: str = "placeholder"
        context: dict[str, Any] = field(default_factory=dict)

    class EthicalDecisionType(Enum):  # type: ignore[no-redef]
        STANDARD = "standard"
        ESCALATED = "escalated"

    class EthicsSwarmColony(_FallbackComponent):
        pass


try:
    from core.colonies.governance_colony_enhanced import GovernanceColony
except ImportError as import_error:

    class GovernanceColony(_FallbackComponent):
        pass


try:
    from core.quantized_thought_cycles import QuantizedThoughtProcessor
except ImportError as import_error:

    class QuantizedThoughtProcessor(_FallbackComponent):
        pass


try:
    from memory.systems.memory_safety_features import MemorySafetySystem
except ImportError as import_error:

    class MemorySafetySystem(_FallbackComponent):
        pass


            try:
                result = await agent.validate(output)
                validations.append(result)
            except Exception as e:
                validations.append({"score": 0.0, "valid": False})

            try:
                results[name] = await task
            except Exception as e:
                results[name] = (False, 0.0)

        try:
            # Check for hallucinations
            is_valid, error = await self.memory_safety.prevent_hallucination(action, context or {})

            if not is_valid:
                # Broadcast hallucination event
                event = SafetyEvent(
                    event_id=f"hall_{datetime.now(timezone.utc).timestamp()}",
                    event_type=SafetyEventType.HALLUCINATION_DETECTED,
                    severity=0.8,
                    source_colony="memory_safety",
                    timestamp=datetime.now(timezone.utc),
                    data={"error": error, "action": action},
                )
                await self.event_bus.broadcast_safety_event(event)
                return False, 0.0

            # Check drift if applicable
            if "tags" in action:
                max_drift = 0.0
                for tag in action["tags"]:
                    drift = self.memory_safety.track_drift(
                        tag,
                        np.random.rand(128),
                        context or {},  # Placeholder embedding
                    )
                    max_drift = max(max_drift, drift)

                if max_drift > 0.5:
                    # Broadcast drift warning
                    event = SafetyEvent(
                        event_id=f"drift_{datetime.now(timezone.utc).timestamp()}",
                        event_type=SafetyEventType.DRIFT_WARNING,
                        severity=max_drift,
                        source_colony="memory_safety",
                        timestamp=datetime.now(timezone.utc),
                        data={"max_drift": max_drift, "tags": action["tags"]},
                    )
                    await self.event_bus.broadcast_safety_event(event)

                return True, 1.0 - max_drift

            return True, 1.0

        except Exception as e:
            return False, 0.0

        try:
            # Create ethical decision request
            request = EthicalDecisionRequest(
                request_id=f"eth_{datetime.now(timezone.utc).timestamp()}",
                decision_type=EthicalDecisionType.SYSTEM_ACTION_APPROVAL,
                context={
                    "action": action,
                    "user_context": context or {},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                urgency="normal",
                requires_simulation=True,
            )

            # Get ethics swarm decision
            if self.colonies["ethics"]:
                response = await self.colonies["ethics"].process_ethical_decision(request)

                return {
                    "approved": response.approved,
                    "score": response.ethical_score,
                    "violations": response.violations,
                    "consensus_method": response.consensus_method.value,
                }

            # Fallback if ethics colony not available
            return {"approved": True, "score": 0.5, "violations": []}

        except Exception as e:
            return {"approved": False, "score": 0.0, "violations": [str(e)]}

        try:
            # Check compliance
            result = await self.compliance_validator.validate(action)

            if not result["compliant"]:
                # Broadcast compliance failure
                event = SafetyEvent(
                    event_id=f"comp_{datetime.now(timezone.utc).timestamp()}",
                    event_type=SafetyEventType.COMPLIANCE_FAILURE,
                    severity=0.9,
                    source_colony="compliance",
                    timestamp=datetime.now(timezone.utc),
                    data={"violations": result.get("violations", [])},
                )
                await self.event_bus.broadcast_safety_event(event)

            return result

        except Exception as e:
            return {"compliant": False, "score": 0.0, "violations": [str(e)]}

            try:
                # Check system health
                await self._check_system_health()

                # Monitor drift across all components
                await self._monitor_global_drift()

                # Check for stale threats
                await self._cleanup_stale_threats()

                # Update safety metrics
                self._update_safety_metrics()

                # Sleep for monitoring interval
                await asyncio.sleep(0.1)  # 100ms cycle

            except Exception as e:
                await asyncio.sleep(1)  # Back off on error


class _FallbackComponent:
    """Generic fallback used when optional guardian subsystems are missing."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._init_args = args
        self._init_kwargs = kwargs

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        return None

    def __getattr__(self, name: str) -> Any:
        def _noop(*args: Any, **kwargs: Any) -> None:
            return None

        return _noop


def _warn_placeholder(component: str, error: Exception) -> None:
    logging.getLogger(__name__).warning("Using placeholder for %s: %s", component, error)


logger = logging.getLogger("ΛTRACE.integrated_safety")


class SafetyEventType(Enum):
    """Types of safety events in the system"""

    HALLUCINATION_DETECTED = "hallucination_detected"
    DRIFT_WARNING = "drift_warning"
    CONSENSUS_FAILED = "consensus_failed"
    CIRCUIT_BREAKER_TRIGGERED = "circuit_breaker_triggered"
    REALITY_ANCHOR_VIOLATION = "reality_anchor_violation"
    QUARANTINE_ACTIVATED = "quarantine_activated"
    ETHICAL_VIOLATION = "ethical_violation"
    COMPLIANCE_FAILURE = "compliance_failure"
    FALLBACK_ACTIVATED = "fallback_activated"
    RECOVERY_INITIATED = "recovery_initiated"


class SafetyLevel(Enum):
    """Overall system safety levels"""

    OPTIMAL = "optimal"  # All systems green
    NORMAL = "normal"  # Minor issues, within tolerance
    ELEVATED = "elevated"  # Multiple minor issues or one major
    HIGH = "high"  # Significant safety concerns
    CRITICAL = "critical"  # Emergency protocols active


@dataclass
class SafetyEvent:
    """Unified safety event structure"""

    event_id: str
    event_type: SafetyEventType
    severity: float  # 0.0-1.0
    source_colony: str
    timestamp: datetime
    data: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    affected_colonies: set[str] = field(default_factory=set)
    mitigation_actions: list[str] = field(default_factory=list)


@dataclass
class SafetyValidationResult:
    """Result of comprehensive safety validation"""

    is_safe: bool
    safety_score: float  # 0.0-1.0
    ethical_score: float
    compliance_score: float
    consensus_score: float
    violations: list[dict[str, Any]]
    recommendations: list[str]
    validation_time_ms: float


class SafetyEventBus:
    """Enhanced event bus with safety-first design"""

    def __init__(self):
        self.safety_channels: dict[SafetyEventType, list[Any]] = defaultdict(list)
        self.event_history = deque(maxlen=10000)
        self.event_validators = []
        self.safety_filters = []
        self.event_metrics = defaultdict(int)

        # Initialize default channels
        for event_type in SafetyEventType:
            self.safety_channels[event_type] = []

        logger.info("SafetyEventBus initialized with all safety channels")

    async def subscribe(self, event_type: SafetyEventType, subscriber: Any):
        """Subscribe to safety events"""
        self.safety_channels[event_type].append(subscriber)
        logger.info(f"Subscriber added to {event_type.value}")

    async def broadcast_safety_event(self, event: SafetyEvent) -> bool:
        """Broadcast safety-critical events with validation"""
        # Pre-broadcast validation
        if not await self._validate_safety_event(event):
            logger.warning(f"Event validation failed: {event.event_id}")
            return False

        # Apply safety filters
        for filter_func in self.safety_filters:
            if not await filter_func(event):
                logger.warning(f"Event filtered: {event.event_id}")
                return False

        # Record event
        self.event_history.append(event)
        self.event_metrics[event.event_type] += 1

        # Broadcast to all subscribers
        tasks = []
        for subscriber in self.safety_channels.get(event.event_type, []):
            if hasattr(subscriber, "handle_safety_event"):
                task = asyncio.create_task(subscriber.handle_safety_event(event))
                tasks.append(task)

        # Wait for all handlers to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        # Log for audit trail
        await self._log_safety_event(event)

        return True

    async def _validate_safety_event(self, event: SafetyEvent) -> bool:
        """Validate safety event before broadcasting"""
        # Check required fields
        if not all([event.event_id, event.event_type, event.source_colony]):
            return False

        # Validate severity
        if not 0.0 <= event.severity <= 1.0:
            return False

        # Run custom validators
        for validator in self.event_validators:
            if not await validator(event):
                return False

        return True

    async def _log_safety_event(self, event: SafetyEvent):
        """Log safety event for audit trail"""
        log_entry = {
            "event_id": event.event_id,
            "type": event.event_type.value,
            "severity": event.severity,
            "source": event.source_colony,
            "timestamp": event.timestamp.isoformat(),
            "affected_colonies": list(event.affected_colonies),
        }
        logger.info(f"Safety event logged: {json.dumps(log_entry)}")

    def get_event_metrics(self) -> dict[str, Any]:
        """Get event bus metrics"""
        return {
            "total_events": len(self.event_history),
            "events_by_type": dict(self.event_metrics),
            "subscribers_by_type": {
                event_type.value: len(subscribers)
                for event_type, subscribers in self.safety_channels.items()
            },
        }


class SafetyColony(BaseColony):
    """Specialized colony for safety validation"""

    def __init__(self, colony_id: str):
        super().__init__(colony_id, capabilities=["safety_validation"])
        self.safety_agents = []
        self.validation_threshold = 0.8
        self.validation_cache = {}
        self.validation_metrics = defaultdict(float)

        # Initialize safety components
        self.memory_safety = MemorySafetySystem()
        self.fallback_manager = BioSymbolicFallbackManager()

        logger.info(f"SafetyColony {colony_id} initialized")

    async def validate_output(self, output: dict[str, Any]) -> tuple[bool, float]:
        """Multi-agent validation of output"""
        start_time = datetime.now(timezone.utc)
        validations = []

        # Check cache first
        output_hash = self._hash_output(output)
        if output_hash in self.validation_cache:
            cached = self.validation_cache[output_hash]
            if (datetime.now(timezone.utc) - cached["timestamp"]).seconds < 60:
                return cached["result"]

        # Each agent performs independent validation
        for agent in self.safety_agents:
        # Calculate consensus
        if not validations:
            return False, 0.0

        consensus_score = sum(v.get("score", 0.0) for v in validations) / len(validations)
        is_safe = consensus_score >= self.validation_threshold

        # Cache result
        self.validation_cache[output_hash] = {
            "result": (is_safe, consensus_score),
            "timestamp": datetime.now(timezone.utc),
        }

        # Update metrics
        validation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        self.validation_metrics["total_validations"] += 1
        self.validation_metrics["average_time"] = (
            self.validation_metrics["average_time"]
            * (self.validation_metrics["total_validations"] - 1)
            + validation_time
        ) / self.validation_metrics["total_validations"]

        return is_safe, consensus_score

    def _hash_output(self, output: dict[str, Any]) -> str:
        """Generate hash for output caching"""
        # Remove volatile fields
        stable_output = {k: v for k, v in output.items() if k not in ["timestamp", "request_id"]}
        return hashlib.sha256(json.dumps(stable_output, sort_keys=True).encode()).hexdigest()[:16]

    async def handle_safety_event(self, event: SafetyEvent):
        """Handle incoming safety events"""
        logger.info(f"SafetyColony handling event: {event.event_type.value}")

        # Route to appropriate handler
        handlers = {
            SafetyEventType.HALLUCINATION_DETECTED: self._handle_hallucination,
            SafetyEventType.DRIFT_WARNING: self._handle_drift,
            SafetyEventType.CIRCUIT_BREAKER_TRIGGERED: self._handle_circuit_breaker,
            SafetyEventType.REALITY_ANCHOR_VIOLATION: self._handle_reality_violation,
        }

        handler = handlers.get(event.event_type)
        if handler:
            await handler(event)
        else:
            logger.warning(f"No handler for event type: {event.event_type}")

    async def _handle_hallucination(self, event: SafetyEvent):
        """Handle hallucination detection"""
        # Update reality anchors
        if "detected_hallucination" in event.data:
            self.memory_safety.add_reality_anchor(
                f"hallucination_{event.event_id}", event.data["detected_hallucination"]
            )

        # Trigger validation of related memories
        await self._validate_related_memories(event)

    async def _handle_drift(self, event: SafetyEvent):
        """Handle drift warnings"""
        drift_score = event.data.get("drift_score", 0.0)

        if drift_score > 0.8:
            # Critical drift - activate fallback
            await self.fallback_manager.activate_fallback(
                "safety_colony",
                FallbackLevel.MODERATE,
                f"Critical drift detected: {drift_score}",
            )

    async def _handle_circuit_breaker(self, event: SafetyEvent):
        """Handle circuit breaker triggers"""
        affected_component = event.data.get("component")

        # Isolate affected component
        if affected_component:
            await self._isolate_component(affected_component)

        # Initiate recovery protocol
        await self._initiate_recovery(event)

    async def _handle_reality_violation(self, event: SafetyEvent):
        """Handle reality anchor violations"""
        violation_data = event.data.get("violation", {})

        # Log violation
        logger.warning(f"Reality anchor violation: {violation_data}")

        # Update safety model
        await self._update_safety_model(violation_data)

    async def _validate_related_memories(self, event: SafetyEvent):
        """Validate memories related to a safety event"""
        # Implementation depends on memory system integration

    async def _isolate_component(self, component: str):
        """Isolate a component for safety"""
        logger.info(f"Isolating component: {component}")
        # Implementation depends on system architecture

    async def _initiate_recovery(self, event: SafetyEvent):
        """Initiate recovery protocol"""
        SafetyEvent(
            event_id=f"recovery_{event.event_id}",
            event_type=SafetyEventType.RECOVERY_INITIATED,
            severity=0.5,
            source_colony=self.colony_id,
            timestamp=datetime.now(timezone.utc),
            data={"original_event": event.event_id},
        )
        # Broadcast recovery event
        # await self.event_bus.broadcast_safety_event(recovery_event)

    async def _update_safety_model(self, violation_data: dict[str, Any]):
        """Update safety model based on violations"""
        # Learn from violations to prevent future occurrences


class IntegratedSafetySystem:
    """
    Master safety system integrating all components with event-bus,
    colony, and swarm architecture
    """

    def __init__(self):
        self.system_id = f"integrated_safety_{datetime.now(timezone.utc).timestamp()}"

        # Initialize event bus
        self.event_bus = SafetyEventBus()

        # Initialize safety components
        self.memory_safety = MemorySafetySystem()
        self.bio_fallback = BioSymbolicFallbackManager()
        self.dashboard_fallback = DashboardFallbackSystem()
        self.qi_processor = QuantizedThoughtProcessor()

        # Initialize colonies
        self.colonies = {
            "safety": SafetyColony("safety_primary"),
            "ethics": EthicsSwarmColony("ethics_swarm"),
            "governance": GovernanceColony("governance"),
            "memory": None,  # To be initialized with memory colony
            "reasoning": None,  # To be initialized with reasoning colony
        }

        # Initialize compliance
        self.compliance_validator = ComplianceValidator()

        # System state
        self.safety_level = SafetyLevel.OPTIMAL
        self.active_threats = {}
        self.mitigation_strategies = {}

        # Metrics
        self.safety_metrics = {
            "validations_performed": 0,
            "threats_detected": 0,
            "mitigations_successful": 0,
            "average_response_time": 0.0,
            "system_uptime": datetime.now(timezone.utc),
        }

        # Circuit breakers
        self.circuit_breakers = defaultdict(
            lambda: {"failures": 0, "last_failure": None, "is_open": False}
        )

        # Subscribe colonies to events
        asyncio.create_task(self._initialize_subscriptions())

        logger.info(f"IntegratedSafetySystem {self.system_id} initialized")

    async def _initialize_subscriptions(self):
        """Initialize event subscriptions for all colonies"""
        # Subscribe safety colony to all safety events
        for event_type in SafetyEventType:
            if self.colonies["safety"]:
                await self.event_bus.subscribe(event_type, self.colonies["safety"])

        # Subscribe ethics colony to ethical events
        ethical_events = [
            SafetyEventType.ETHICAL_VIOLATION,
            SafetyEventType.COMPLIANCE_FAILURE,
            SafetyEventType.HALLUCINATION_DETECTED,
        ]
        for event_type in ethical_events:
            if self.colonies["ethics"]:
                await self.event_bus.subscribe(event_type, self.colonies["ethics"])

        logger.info("Event subscriptions initialized")

    async def validate_action(
        self, action: dict[str, Any], context: Optional[dict[str, Any]] = None
    ) -> SafetyValidationResult:
        """
        Comprehensive validation combining safety, ethics, and compliance
        """
        start_time = datetime.now(timezone.utc)
        validation_tasks = []

        # 1. Memory safety check
        memory_task = asyncio.create_task(self._validate_memory_safety(action, context))
        validation_tasks.append(("memory", memory_task))

        # 2. Safety colony validation
        safety_task = asyncio.create_task(self.colonies["safety"].validate_output(action))
        validation_tasks.append(("safety", safety_task))

        # 3. Ethics evaluation
        ethics_task = asyncio.create_task(self._validate_ethics(action, context))
        validation_tasks.append(("ethics", ethics_task))

        # 4. Compliance check
        compliance_task = asyncio.create_task(self._validate_compliance(action, context))
        validation_tasks.append(("compliance", compliance_task))

        # Gather all results
        results = {}
        for name, task in validation_tasks:
        # Calculate overall scores
        safety_score = results.get("safety", (False, 0.0))[1]
        memory_score = results.get("memory", (False, 0.0))[1]
        ethics_score = results.get("ethics", {}).get("score", 0.0)
        compliance_score = results.get("compliance", {}).get("score", 0.0)

        # Consensus calculation
        all_scores = [safety_score, memory_score, ethics_score, compliance_score]
        consensus_score = np.mean([s for s in all_scores if s > 0])

        # Determine if action is safe
        is_safe = all(
            [
                results.get("safety", (False, 0))[0],
                results.get("memory", (False, 0))[0],
                results.get("ethics", {}).get("approved", False),
                results.get("compliance", {}).get("compliant", False),
            ]
        )

        # Collect violations
        violations = []
        if not results.get("safety", (True, 0))[0]:
            violations.append({"type": "safety", "details": "Failed safety validation"})
        if not results.get("memory", (True, 0))[0]:
            violations.append({"type": "memory", "details": "Failed memory validation"})
        if not results.get("ethics", {}).get("approved", True):
            violations.extend(results.get("ethics", {}).get("violations", []))
        if not results.get("compliance", {}).get("compliant", True):
            violations.extend(results.get("compliance", {}).get("violations", []))

        # Generate recommendations
        recommendations = self._generate_recommendations(violations, results)

        # Calculate validation time
        validation_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        # Update metrics
        self.safety_metrics["validations_performed"] += 1
        self.safety_metrics["average_response_time"] = (
            self.safety_metrics["average_response_time"]
            * (self.safety_metrics["validations_performed"] - 1)
            + validation_time
        ) / self.safety_metrics["validations_performed"]

        return SafetyValidationResult(
            is_safe=is_safe,
            safety_score=safety_score,
            ethical_score=ethics_score,
            compliance_score=compliance_score,
            consensus_score=consensus_score,
            violations=violations,
            recommendations=recommendations,
            validation_time_ms=validation_time,
        )

    async def _validate_memory_safety(
        self, action: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> tuple[bool, float]:
        """Validate action against memory safety system"""
    async def _validate_ethics(
        self, action: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Validate action through ethics colony"""
    async def _validate_compliance(
        self, action: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Validate action through compliance system"""
    def _generate_recommendations(
        self, violations: list[dict[str, Any]], results: dict[str, Any]
    ) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Safety recommendations
        if any(v["type"] == "safety" for v in violations):
            recommendations.append("Review safety parameters and thresholds")
            recommendations.append("Consider activating fallback mode")

        # Memory recommendations
        if any(v["type"] == "memory" for v in violations):
            recommendations.append("Verify reality anchors and update if needed")
            recommendations.append("Check for semantic drift in related memories")

        # Ethics recommendations
        ethics_result = results.get("ethics", {})
        if not ethics_result.get("approved", True):
            recommendations.append("Request human oversight for ethical decision")
            recommendations.append("Run additional ethical simulations")

        # Compliance recommendations
        compliance_result = results.get("compliance", {})
        if not compliance_result.get("compliant", True):
            recommendations.append("Review compliance policies")
            recommendations.append("Consult legal/compliance team")

        return recommendations

    async def handle_threat(self, threat: dict[str, Any]) -> dict[str, Any]:
        """
        Coordinate response to detected threats using swarm intelligence
        """
        threat_id = f"threat_{datetime.now(timezone.utc).timestamp()}"
        self.active_threats[threat_id] = threat

        # Assess threat level
        threat_level = self._assess_threat_level(threat)

        # Update system safety level
        self._update_safety_level(threat_level)

        # Determine mitigation strategy
        strategy = await self._determine_mitigation_strategy(threat, threat_level)
        self.mitigation_strategies[threat_id] = strategy

        # Deploy mitigation across colonies
        mitigation_results = await self._deploy_mitigation(strategy, threat)

        # Verify mitigation effectiveness
        effectiveness = await self._verify_mitigation_effectiveness(mitigation_results)

        # Update metrics
        self.safety_metrics["threats_detected"] += 1
        if effectiveness > 0.8:
            self.safety_metrics["mitigations_successful"] += 1

        return {
            "threat_id": threat_id,
            "threat_level": threat_level.value,
            "mitigation_strategy": strategy,
            "effectiveness": effectiveness,
            "system_safety_level": self.safety_level.value,
        }

    def _assess_threat_level(self, threat: dict[str, Any]) -> SafetyLevel:
        """Assess the severity of a threat"""
        severity = threat.get("severity", 0.5)

        if severity < 0.2:
            return SafetyLevel.NORMAL
        elif severity < 0.4:
            return SafetyLevel.ELEVATED
        elif severity < 0.7:
            return SafetyLevel.HIGH
        else:
            return SafetyLevel.CRITICAL

    def _update_safety_level(self, threat_level: SafetyLevel):
        """Update overall system safety level"""
        # Simple escalation logic - can be made more sophisticated
        current_index = list(SafetyLevel).index(self.safety_level)
        threat_index = list(SafetyLevel).index(threat_level)

        if threat_index > current_index:
            self.safety_level = threat_level
            logger.warning(f"System safety level escalated to: {self.safety_level.value}")

    async def _determine_mitigation_strategy(
        self, threat: dict[str, Any], threat_level: SafetyLevel
    ) -> dict[str, Any]:
        """Determine appropriate mitigation strategy"""
        strategies = {
            SafetyLevel.NORMAL: {
                "action": "monitor",
                "resources": "minimal",
                "colonies_involved": ["safety"],
            },
            SafetyLevel.ELEVATED: {
                "action": "active_mitigation",
                "resources": "moderate",
                "colonies_involved": ["safety", "ethics"],
            },
            SafetyLevel.HIGH: {
                "action": "coordinated_response",
                "resources": "significant",
                "colonies_involved": ["safety", "ethics", "governance"],
            },
            SafetyLevel.CRITICAL: {
                "action": "emergency_protocol",
                "resources": "maximum",
                "colonies_involved": ["all"],
                "fallback_activation": True,
            },
        }

        return strategies.get(threat_level, strategies[SafetyLevel.NORMAL])

    async def _deploy_mitigation(
        self, strategy: dict[str, Any], threat: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Deploy mitigation strategy across colonies"""
        results = []

        # Activate fallback if needed
        if strategy.get("fallback_activation"):
            fallback_result = await self.bio_fallback.activate_fallback(
                "integrated_safety",
                FallbackLevel.SEVERE,
                f"Critical threat detected: {threat}",
            )
            results.append({"component": "fallback", "result": fallback_result})

        # Deploy to specified colonies
        colonies_to_activate = strategy.get("colonies_involved", [])
        if "all" in colonies_to_activate:
            colonies_to_activate = list(self.colonies.keys())

        for colony_name in colonies_to_activate:
            colony = self.colonies.get(colony_name)
            if colony:
                # Each colony handles the threat according to its capabilities
                result = {"colony": colony_name, "status": "activated"}
                results.append(result)

        return results

    async def _verify_mitigation_effectiveness(
        self, mitigation_results: list[dict[str, Any]]
    ) -> float:
        """Verify the effectiveness of mitigation efforts"""
        if not mitigation_results:
            return 0.0

        # Simple effectiveness calculation
        successful = sum(
            1
            for r in mitigation_results
            if r.get("status") == "activated" or r.get("result", {}).get("success")
        )

        return successful / len(mitigation_results)

    def check_circuit_breaker(self, component: str) -> bool:
        """Check if a component's circuit breaker is open"""
        breaker = self.circuit_breakers[component]

        # Reset if enough time has passed
        if breaker["is_open"] and breaker["last_failure"]:
            time_since_failure = (
                datetime.now(timezone.utc) - breaker["last_failure"]
            ).total_seconds()
            if time_since_failure > 300:  # 5 minute reset
                breaker["failures"] = 0
                breaker["is_open"] = False
                logger.info(f"Circuit breaker reset for: {component}")

        return not breaker["is_open"]

    def trip_circuit_breaker(self, component: str):
        """Trip a component's circuit breaker"""
        breaker = self.circuit_breakers[component]
        breaker["failures"] += 1
        breaker["last_failure"] = datetime.now(timezone.utc)

        if breaker["failures"] >= 5:  # Threshold
            breaker["is_open"] = True
            logger.error(f"Circuit breaker tripped for: {component}")

            # Broadcast circuit breaker event
            event = SafetyEvent(
                event_id=f"cb_{datetime.now(timezone.utc).timestamp()}",
                event_type=SafetyEventType.CIRCUIT_BREAKER_TRIGGERED,
                severity=0.7,
                source_colony="safety_system",
                timestamp=datetime.now(timezone.utc),
                data={"component": component, "failures": breaker["failures"]},
            )
            asyncio.create_task(self.event_bus.broadcast_safety_event(event))

    async def run_continuous_monitoring(self):
        """Run continuous safety monitoring"""
        logger.info("Starting continuous safety monitoring")

        while True:
    async def _check_system_health(self) -> dict[str, Any]:
        """Check overall system health"""
        health = {
            "colonies_active": sum(1 for c in self.colonies.values() if c is not None),
            "event_bus_active": len(self.event_bus.event_history) > 0,
            "safety_level": self.safety_level.value,
            "active_threats": len(self.active_threats),
            "open_circuit_breakers": sum(1 for b in self.circuit_breakers.values() if b["is_open"]),
        }

        # Determine if system is healthy
        health["is_healthy"] = (
            health["colonies_active"] > 0
            and health["safety_level"] != SafetyLevel.CRITICAL.value
            and health["open_circuit_breakers"] < 3
        )

        return health

    async def _monitor_global_drift(self) -> dict[str, float]:
        """Monitor drift across all components"""
        drift_scores = {}

        # Get drift from memory safety
        memory_drift_report = self.memory_safety.get_safety_report()
        drift_scores["memory"] = memory_drift_report["drift_analysis"]["average_drift"]

        # Get drift from ethics colony if available
        if self.colonies.get("ethics"):
            # Placeholder for ethics drift
            drift_scores["ethics"] = 0.1

        # Check if any drift is concerning
        max_drift = max(drift_scores.values()) if drift_scores else 0.0
        if max_drift > 0.5:
            event = SafetyEvent(
                event_id=f"drift_global_{datetime.now(timezone.utc).timestamp()}",
                event_type=SafetyEventType.DRIFT_WARNING,
                severity=max_drift,
                source_colony="monitoring",
                timestamp=datetime.now(timezone.utc),
                data={"drift_scores": drift_scores},
            )
            await self.event_bus.broadcast_safety_event(event)

        return drift_scores

    async def _cleanup_stale_threats(self):
        """Remove old threats that have been mitigated"""
        stale_threshold = timedelta(hours=1)
        current_time = datetime.now(timezone.utc)

        stale_threats = []
        for threat_id, threat in self.active_threats.items():
            threat_time = threat.get("timestamp", current_time)
            if isinstance(threat_time, str):
                threat_time = datetime.fromisoformat(threat_time)

            if current_time - threat_time > stale_threshold:
                stale_threats.append(threat_id)

        for threat_id in stale_threats:
            del self.active_threats[threat_id]
            if threat_id in self.mitigation_strategies:
                del self.mitigation_strategies[threat_id]

    def _update_safety_metrics(self):
        """Update real-time safety metrics"""
        # Calculate uptime
        uptime = datetime.now(timezone.utc) - self.safety_metrics["system_uptime"]
        self.safety_metrics["uptime_hours"] = uptime.total_seconds() / 3600

        # Success rate
        if self.safety_metrics["threats_detected"] > 0:
            self.safety_metrics["mitigation_success_rate"] = (
                self.safety_metrics["mitigations_successful"]
                / self.safety_metrics["threats_detected"]
            )

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "system_id": self.system_id,
            "safety_level": self.safety_level.value,
            "active_threats": len(self.active_threats),
            "event_metrics": self.event_bus.get_event_metrics(),
            "safety_metrics": self.safety_metrics,
            "circuit_breakers": {
                component: {
                    "is_open": breaker["is_open"],
                    "failures": breaker["failures"],
                }
                for component, breaker in self.circuit_breakers.items()
            },
            "colonies_status": {
                name: "active" if colony else "inactive" for name, colony in self.colonies.items()
            },
        }


async def main():
    """Demonstration of integrated safety system"""
    print("🛡️ INTEGRATED SAFETY SYSTEM DEMONSTRATION")
    print("=" * 60)

    # Initialize system
    safety_system = IntegratedSafetySystem()

    # Start monitoring in background
    monitoring_task = asyncio.create_task(safety_system.run_continuous_monitoring())

    print("\n1. Testing Safe Action...")
    safe_action = {
        "action": "process_data",
        "data": {"user_input": "Hello, how can you help me today?"},
        "tags": ["greeting", "help_request"],
        "timestamp": datetime.now(timezone.utc),
    }

    result = await safety_system.validate_action(safe_action)
    print(f"   Is Safe: {result.is_safe}")
    print(f"   Safety Score: {result.safety_score:.2f}")
    print(f"   Ethical Score: {result.ethical_score:.2f}")
    print(f"   Compliance Score: {result.compliance_score:.2f}")
    print(f"   Consensus Score: {result.consensus_score:.2f}")

    print("\n2. Testing Unsafe Action (Hallucination)...")
    unsafe_action = {
        "action": "generate_response",
        "content": "The current year is 2030",  # Contradicts reality anchor
        "tags": ["temporal", "factual"],
        "timestamp": datetime.now(timezone.utc),
    }

    result = await safety_system.validate_action(unsafe_action)
    print(f"   Is Safe: {result.is_safe}")
    print(f"   Violations: {result.violations}")
    print(f"   Recommendations: {result.recommendations}")

    print("\n3. Testing Threat Response...")
    threat = {
        "type": "anomaly_detected",
        "severity": 0.7,
        "source": "network_monitor",
        "details": "Unusual pattern in request frequency",
        "timestamp": datetime.now(timezone.utc),
    }

    threat_response = await safety_system.handle_threat(threat)
    print(f"   Threat Level: {threat_response['threat_level']}")
    print(f"   Mitigation Strategy: {threat_response['mitigation_strategy']}")
    print(f"   Effectiveness: {threat_response['effectiveness']:.2%}")
    print(f"   System Safety Level: {threat_response['system_safety_level']}")

    print("\n4. System Status:")
    status = safety_system.get_system_status()
    print(f"   Safety Level: {status['safety_level']}")
    print(f"   Active Threats: {status['active_threats']}")
    print(f"   Total Events: {status['event_metrics']['total_events']}")
    print(f"   Validations Performed: {status['safety_metrics']['validations_performed']}")
    print(f"   Average Response Time: {status['safety_metrics']['average_response_time']:.2f}ms")

    # Let monitoring run for a bit
    await asyncio.sleep(2)

    # Cancel monitoring
    monitoring_task.cancel()

    print("\n✅ Demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
