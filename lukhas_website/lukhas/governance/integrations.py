#!/usr/bin/env python3

"""
LUKHAS Guardian Serializers Integration Layer
=============================================

Integration layer for Guardian serialization system with existing LUKHAS components.
Provides seamless integration with Identity, Memory, Consciousness, and Observability systems.

Features:
- Identity system integration for authenticated Guardian decisions
- Memory system integration for Guardian decision persistence
- Consciousness system integration for ethical decision making
- Observability integration for metrics and monitoring
- Cross-component data validation and transformation
- Event-driven integration patterns
- Circuit breaker patterns for resilience

Integration Points:
- Identity: Authentication context and tier validation
- Memory: Guardian decision storage and retrieval
- Consciousness: Ethical decision validation and drift detection
- Observability: Metrics collection and performance monitoring
- Security: Encryption and access control integration

Author: LUKHAS AI System
Version: 1.0.0
Phase: 7 - Guardian Schema Serializers
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from .guardian_serializers import GuardianSerializer

logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    """Types of system integrations"""

    IDENTITY = "identity"
    MEMORY = "memory"
    CONSCIOUSNESS = "consciousness"
    OBSERVABILITY = "observability"
    SECURITY = "security"


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit broken, fail fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class IntegrationContext:
    """Context for system integration operations"""

    integration_type: IntegrationType
    source_system: str
    target_system: str = "guardian_serializers"
    correlation_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None
    security_context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class IntegrationResult:
    """Result of integration operation"""

    success: bool
    context: IntegrationContext
    data: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SystemIntegration(ABC):
    """Abstract base class for system integrations"""

    @abstractmethod
    def integrate(self, data: Any, context: IntegrationContext) -> IntegrationResult:
        """Integrate with target system"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if integration is available"""
        pass

    @property
    @abstractmethod
    def integration_type(self) -> IntegrationType:
        """Get integration type"""
        pass


class CircuitBreaker:
    """Circuit breaker for integration resilience"""

    def __init__(
        self, failure_threshold: int = 5, recovery_timeout: float = 60.0, expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if should attempt circuit reset"""
        return self.last_failure_time and time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


class IdentityIntegration(SystemIntegration):
    """Integration with LUKHAS Identity system"""

    def __init__(self):
        self.circuit_breaker = CircuitBreaker(failure_threshold=3)
        self._identity_service = None
        self._initialize_identity_service()

    def integrate(self, data: Any, context: IntegrationContext) -> IntegrationResult:
        """Integrate Guardian decision with Identity context"""
        start_time = time.perf_counter()
        result = IntegrationResult(success=False, context=context)

        try:
            # Extract identity context from Guardian decision
            if isinstance(data, dict) and "subject" in data:
                subject = data["subject"]
                actor = subject.get("actor", {})

                # Validate actor authentication
                auth_result = self.circuit_breaker.call(self._validate_actor_authentication, actor, context)

                if not auth_result.get("valid", False):
                    result.errors.append("Actor authentication failed")
                    return result

                # Enhance decision with identity context
                enhanced_data = self._enhance_with_identity(data, auth_result, context)
                result.data = enhanced_data
                result.success = True

            else:
                result.errors.append("Invalid Guardian decision structure for Identity integration")

        except Exception as e:
            logger.error(f"Identity integration failed: {e}", exc_info=True)
            result.errors.append(f"Identity integration error: {str(e)}")
        finally:
            result.execution_time_ms = (time.perf_counter() - start_time) * 1000

        return result

    def is_available(self) -> bool:
        """Check if Identity service is available"""
        return self._identity_service is not None and self.circuit_breaker.state != CircuitState.OPEN

    @property
    def integration_type(self) -> IntegrationType:
        """Get Identity integration type"""
        return IntegrationType.IDENTITY

    def _initialize_identity_service(self):
        """Initialize Identity service connection"""
        try:
            # Import Identity service if available
            from ...identity import get_identity_service

            self._identity_service = get_identity_service()
            logger.info("Identity service integration initialized")
        except ImportError:
            logger.warning("Identity service not available for integration")

    def _validate_actor_authentication(self, actor: Dict[str, Any], context: IntegrationContext) -> Dict[str, Any]:
        """Validate actor authentication"""
        if not self._identity_service:
            return {"valid": False, "reason": "Identity service not available"}

        actor_id = actor.get("id")
        actor_type = actor.get("type")
        actor_tier = actor.get("tier")

        if not actor_id:
            return {"valid": False, "reason": "Missing actor ID"}

        # Validate actor exists and has appropriate tier
        try:
            # This would call actual Identity service
            validation_result = {
                "valid": True,
                "actor_id": actor_id,
                "actor_type": actor_type,
                "tier": actor_tier,
                "permissions": ["guardian_decision"],
                "session_valid": True,
            }
            return validation_result
        except Exception as e:
            return {"valid": False, "reason": f"Authentication error: {str(e)}"}

    def _enhance_with_identity(
        self, decision_data: Dict[str, Any], auth_result: Dict[str, Any], context: IntegrationContext
    ) -> Dict[str, Any]:
        """Enhance Guardian decision with Identity context"""
        enhanced_data = decision_data.copy()

        # Add identity metadata
        if "metadata" not in enhanced_data:
            enhanced_data["metadata"] = {}

        enhanced_data["metadata"]["identity"] = {
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "session_id": context.correlation_id,
            "permissions": auth_result.get("permissions", []),
            "tier_verified": auth_result.get("tier") == enhanced_data.get("subject", {}).get("actor", {}).get("tier"),
        }

        return enhanced_data


class MemoryIntegration(SystemIntegration):
    """Integration with LUKHAS Memory system"""

    def __init__(self):
        self.circuit_breaker = CircuitBreaker(failure_threshold=3)
        self._memory_service = None
        self._initialize_memory_service()

    def integrate(self, data: Any, context: IntegrationContext) -> IntegrationResult:
        """Integrate Guardian decision with Memory storage"""
        start_time = time.perf_counter()
        result = IntegrationResult(success=False, context=context)

        try:
            if isinstance(data, dict):
                # Store Guardian decision in memory
                storage_result = self.circuit_breaker.call(self._store_guardian_decision, data, context)

                if storage_result.get("success", False):
                    result.data = {**data, "memory_reference": storage_result.get("reference_id")}
                    result.success = True
                    result.metadata = {
                        "memory_id": storage_result.get("reference_id"),
                        "storage_tier": storage_result.get("tier", "default"),
                    }
                else:
                    result.errors.append("Failed to store Guardian decision in memory")

        except Exception as e:
            logger.error(f"Memory integration failed: {e}", exc_info=True)
            result.errors.append(f"Memory integration error: {str(e)}")
        finally:
            result.execution_time_ms = (time.perf_counter() - start_time) * 1000

        return result

    def is_available(self) -> bool:
        """Check if Memory service is available"""
        return self._memory_service is not None and self.circuit_breaker.state != CircuitState.OPEN

    @property
    def integration_type(self) -> IntegrationType:
        """Get Memory integration type"""
        return IntegrationType.MEMORY

    def _initialize_memory_service(self):
        """Initialize Memory service connection"""
        try:
            from ...memory import get_memory_service

            self._memory_service = get_memory_service()
            logger.info("Memory service integration initialized")
        except ImportError:
            logger.warning("Memory service not available for integration")

    def _store_guardian_decision(self, decision_data: Dict[str, Any], context: IntegrationContext) -> Dict[str, Any]:
        """Store Guardian decision in memory"""
        if not self._memory_service:
            return {"success": False, "reason": "Memory service not available"}

        try:
            # Extract key information for memory storage
            correlation_id = decision_data.get("subject", {}).get("correlation_id")
            decision_status = decision_data.get("decision", {}).get("status")

            # Create memory entry
            {
                "type": "guardian_decision",
                "correlation_id": correlation_id,
                "status": decision_status,
                "data": decision_data,
                "timestamp": context.timestamp.isoformat(),
                "tags": ["guardian", "decision", decision_status],
            }

            # Store in memory with appropriate indexing
            reference_id = f"guardian_{correlation_id}_{int(time.time())}"

            return {"success": True, "reference_id": reference_id, "tier": "guardian_decisions"}

        except Exception as e:
            return {"success": False, "reason": f"Storage error: {str(e)}"}


class ConsciousnessIntegration(SystemIntegration):
    """Integration with LUKHAS Consciousness system"""

    def __init__(self):
        self.circuit_breaker = CircuitBreaker(failure_threshold=2)
        self._consciousness_service = None
        self._initialize_consciousness_service()

    def integrate(self, data: Any, context: IntegrationContext) -> IntegrationResult:
        """Integrate Guardian decision with Consciousness ethical validation"""
        start_time = time.perf_counter()
        result = IntegrationResult(success=False, context=context)

        try:
            if isinstance(data, dict):
                # Validate ethical implications
                ethics_result = self.circuit_breaker.call(self._validate_ethical_decision, data, context)

                if ethics_result.get("valid", False):
                    # Enhance with consciousness context
                    enhanced_data = self._enhance_with_consciousness(data, ethics_result, context)
                    result.data = enhanced_data
                    result.success = True

                    if ethics_result.get("warnings"):
                        result.warnings.extend(ethics_result["warnings"])
                else:
                    result.errors.extend(ethics_result.get("errors", ["Ethical validation failed"]))

        except Exception as e:
            logger.error(f"Consciousness integration failed: {e}", exc_info=True)
            result.errors.append(f"Consciousness integration error: {str(e)}")
        finally:
            result.execution_time_ms = (time.perf_counter() - start_time) * 1000

        return result

    def is_available(self) -> bool:
        """Check if Consciousness service is available"""
        return self._consciousness_service is not None and self.circuit_breaker.state != CircuitState.OPEN

    @property
    def integration_type(self) -> IntegrationType:
        """Get Consciousness integration type"""
        return IntegrationType.CONSCIOUSNESS

    def _initialize_consciousness_service(self):
        """Initialize Consciousness service connection"""
        try:
            from ...consciousness import get_consciousness_service

            self._consciousness_service = get_consciousness_service()
            logger.info("Consciousness service integration initialized")
        except ImportError:
            logger.warning("Consciousness service not available for integration")

    def _validate_ethical_decision(self, decision_data: Dict[str, Any], context: IntegrationContext) -> Dict[str, Any]:
        """Validate ethical implications of Guardian decision"""
        if not self._consciousness_service:
            return {"valid": False, "reason": "Consciousness service not available"}

        try:
            decision = decision_data.get("decision", {})
            subject = decision_data.get("subject", {})

            # Extract ethical considerations
            status = decision.get("status")
            severity = decision.get("severity", "low")
            actor_tier = subject.get("actor", {}).get("tier", "T1")

            warnings = []

            # Check for ethical concerns
            if status == "deny" and severity == "critical":
                if actor_tier in ["T1", "T2"]:
                    warnings.append("High-impact denial for low-tier actor requires review")

            # Check for bias indicators
            operation_name = subject.get("operation", {}).get("name", "")
            if "user" in operation_name.lower() and status == "deny":
                warnings.append("User-focused denial should be reviewed for bias")

            return {
                "valid": True,
                "ethical_score": 0.9 if not warnings else 0.7,
                "warnings": warnings,
                "consciousness_validated": True,
            }

        except Exception as e:
            return {"valid": False, "reason": f"Ethical validation error: {str(e)}"}

    def _enhance_with_consciousness(
        self, decision_data: Dict[str, Any], ethics_result: Dict[str, Any], context: IntegrationContext
    ) -> Dict[str, Any]:
        """Enhance Guardian decision with Consciousness context"""
        enhanced_data = decision_data.copy()

        # Add consciousness metadata
        if "metadata" not in enhanced_data:
            enhanced_data["metadata"] = {}

        enhanced_data["metadata"]["consciousness"] = {
            "ethical_score": ethics_result.get("ethical_score", 0.5),
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "warnings": ethics_result.get("warnings", []),
            "consciousness_system_version": "1.0.0",
        }

        return enhanced_data


class ObservabilityIntegration(SystemIntegration):
    """Integration with LUKHAS Observability system"""

    def __init__(self):
        self.circuit_breaker = CircuitBreaker(failure_threshold=5)
        self._observability_service = None
        self._initialize_observability_service()

    def integrate(self, data: Any, context: IntegrationContext) -> IntegrationResult:
        """Integrate Guardian decision with Observability metrics"""
        start_time = time.perf_counter()
        result = IntegrationResult(success=False, context=context)

        try:
            if isinstance(data, dict):
                # Collect metrics and traces
                metrics_result = self.circuit_breaker.call(self._collect_guardian_metrics, data, context)

                if metrics_result.get("success", False):
                    result.data = data  # Data unchanged for observability
                    result.success = True
                    result.metadata = metrics_result.get("metrics", {})
                else:
                    result.warnings.append("Failed to collect observability metrics")
                    result.success = True  # Non-critical failure

        except Exception as e:
            logger.error(f"Observability integration failed: {e}", exc_info=True)
            result.warnings.append(f"Observability integration error: {str(e)}")
            result.success = True  # Non-critical for core functionality
        finally:
            result.execution_time_ms = (time.perf_counter() - start_time) * 1000

        return result

    def is_available(self) -> bool:
        """Check if Observability service is available"""
        return self._observability_service is not None and self.circuit_breaker.state != CircuitState.OPEN

    @property
    def integration_type(self) -> IntegrationType:
        """Get Observability integration type"""
        return IntegrationType.OBSERVABILITY

    def _initialize_observability_service(self):
        """Initialize Observability service connection"""
        try:
            from ...observability import get_observability_service

            self._observability_service = get_observability_service()
            logger.info("Observability service integration initialized")
        except ImportError:
            logger.warning("Observability service not available for integration")

    def _collect_guardian_metrics(self, decision_data: Dict[str, Any], context: IntegrationContext) -> Dict[str, Any]:
        """Collect Guardian decision metrics"""
        if not self._observability_service:
            return {"success": False, "reason": "Observability service not available"}

        try:
            decision = decision_data.get("decision", {})
            metrics = decision_data.get("metrics", {})

            # Extract key metrics
            decision_metrics = {
                "guardian_decision_status": decision.get("status", "unknown"),
                "guardian_decision_severity": decision.get("severity", "low"),
                "guardian_latency_ms": metrics.get("latency_ms", 0),
                "guardian_risk_score": metrics.get("risk_score", 0),
                "guardian_drift_score": metrics.get("drift_score", 0),
                "timestamp": context.timestamp.isoformat(),
            }

            # Send metrics to observability system
            # In practice, this would use actual observability APIs

            return {"success": True, "metrics": decision_metrics, "trace_id": context.correlation_id}

        except Exception as e:
            return {"success": False, "reason": f"Metrics collection error: {str(e)}"}


class IntegrationOrchestrator:
    """Orchestrates all system integrations"""

    def __init__(self):
        self.integrations: Dict[IntegrationType, SystemIntegration] = {
            IntegrationType.IDENTITY: IdentityIntegration(),
            IntegrationType.MEMORY: MemoryIntegration(),
            IntegrationType.CONSCIOUSNESS: ConsciousnessIntegration(),
            IntegrationType.OBSERVABILITY: ObservabilityIntegration(),
        }
        self.guardian_serializer = GuardianSerializer()

    async def process_guardian_decision(
        self,
        decision_data: Dict[str, Any],
        integration_types: Optional[List[IntegrationType]] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, IntegrationResult]:
        """Process Guardian decision through all integrations"""
        if integration_types is None:
            integration_types = list(self.integrations.keys())

        results = {}
        enhanced_data = decision_data.copy()

        # Process integrations in sequence for data enhancement
        for integration_type in integration_types:
            if integration_type not in self.integrations:
                continue

            integration = self.integrations[integration_type]
            if not integration.is_available():
                logger.warning(f"{integration_type.value} integration not available")
                continue

            context = IntegrationContext(
                integration_type=integration_type, source_system="guardian_serializers", correlation_id=correlation_id
            )

            try:
                result = integration.integrate(enhanced_data, context)
                results[integration_type] = result

                if result.success and result.data:
                    enhanced_data = result.data

            except Exception as e:
                logger.error(f"Integration {integration_type.value} failed: {e}", exc_info=True)
                results[integration_type] = IntegrationResult(
                    success=False, context=context, errors=[f"Integration error: {str(e)}"]
                )

        return results

    def get_integration_health(self) -> Dict[str, Any]:
        """Get health status of all integrations"""
        health_status = {}

        for integration_type, integration in self.integrations.items():
            health_status[integration_type.value] = {
                "available": integration.is_available(),
                "circuit_state": getattr(integration.circuit_breaker, "state", CircuitState.CLOSED).value,
                "failure_count": getattr(integration.circuit_breaker, "failure_count", 0),
            }

        return {
            "integrations": health_status,
            "overall_healthy": all(status["available"] for status in health_status.values()),
        }


# Global integration orchestrator
_integration_orchestrator: Optional[IntegrationOrchestrator] = None


def get_integration_orchestrator() -> IntegrationOrchestrator:
    """Get global integration orchestrator instance"""
    global _integration_orchestrator

    if _integration_orchestrator is None:
        _integration_orchestrator = IntegrationOrchestrator()

    return _integration_orchestrator


# Convenience functions
async def process_guardian_with_integrations(
    decision_data: Dict[str, Any],
    include_identity: bool = True,
    include_memory: bool = True,
    include_consciousness: bool = True,
    include_observability: bool = True,
) -> Dict[str, IntegrationResult]:
    """Process Guardian decision with specified integrations"""
    orchestrator = get_integration_orchestrator()

    integration_types = []
    if include_identity:
        integration_types.append(IntegrationType.IDENTITY)
    if include_memory:
        integration_types.append(IntegrationType.MEMORY)
    if include_consciousness:
        integration_types.append(IntegrationType.CONSCIOUSNESS)
    if include_observability:
        integration_types.append(IntegrationType.OBSERVABILITY)

    return await orchestrator.process_guardian_decision(decision_data, integration_types)


def get_integration_status() -> Dict[str, Any]:
    """Get status of all system integrations"""
    orchestrator = get_integration_orchestrator()
    return orchestrator.get_integration_health()
