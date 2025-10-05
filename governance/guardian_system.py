"""
LUKHAS Guardian System
====================

Core guardian and safety system for LUKHAS AI.
"""

import asyncio
import logging
import os
import statistics
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from lukhas.core.reliability.circuit_breaker import (
        CircuitBreakerOpenError,
        _circuit_registry,
        circuit_breaker,
        get_circuit_health,
    )
    CIRCUIT_BREAKER_AVAILABLE = True
except ImportError:
    CIRCUIT_BREAKER_AVAILABLE = False
    logging.warning("Circuit breaker module not available, using basic error handling")

try:
    from .guardian_reflector import DriftSeverity, GuardianReflector
    GUARDIAN_REFLECTOR_AVAILABLE = True
except ImportError:
    GUARDIAN_REFLECTOR_AVAILABLE = False
    logging.warning("GuardianReflector not available, using basic drift detection")

try:
    from .guardian_policies import DecisionType, GuardianPoliciesEngine, PolicyContext, get_guardian_policies_engine
    GUARDIAN_POLICIES_AVAILABLE = True
except ImportError:
    GUARDIAN_POLICIES_AVAILABLE = False
    logging.warning("GuardianPolicies not available, using basic validation")

logger = logging.getLogger(__name__)


class GuardianSystem:
    """Core guardian and safety system"""

    def __init__(self):
        """Initialize guardian system"""
        self.logger = logger
        self.logger.info("GuardianSystem initialized")
        self.drift_threshold = 0.15
        self._initialized = False
        self._policies = {}
        self._monitoring_active = False

        # Circuit breaker configuration
        self._circuit_breakers = {}
        if CIRCUIT_BREAKER_AVAILABLE:
            self._setup_circuit_breakers()

        # Error handling and retry configuration
        self._max_retries = 3
        self._base_retry_delay = 0.1  # 100ms
        self._error_counts = {}
        self._consecutive_errors = 0
        self._last_error_time = None

        # Advanced drift detection and analysis
        if GUARDIAN_REFLECTOR_AVAILABLE:
            self.reflector = GuardianReflector(drift_threshold=self.drift_threshold)
            self.logger.info("GuardianReflector initialized for advanced drift analysis")
        else:
            self.reflector = None
            self.logger.warning("GuardianReflector not available, using basic drift detection")

        # Memory system integration
        self._memory_integration_enabled = False
        self._memory_event_buffer = deque(maxlen=50)  # Buffer recent memory events
        self._memory_drift_threshold_violations = 0
        self._last_memory_drift_score = None
        self._memory_callbacks = []

        # Guardian Policies Engine integration
        if GUARDIAN_POLICIES_AVAILABLE:
            self.policies_engine = get_guardian_policies_engine()
            self.logger.info("GuardianPoliciesEngine initialized for advanced policy evaluation")
        else:
            self.policies_engine = None
            self.logger.warning("GuardianPoliciesEngine not available, using basic validation")

    def _create_standard_response(self, safe: bool, drift_score: float,
                                guardian_status: str, reason: str = None) -> dict[str, Any]:
        """Create standardized Guardian response with full schema compliance"""
        emergency_file = Path("/tmp/guardian_emergency_disable")
        dsl_setting = os.getenv("ENFORCE_ETHICS_DSL", "1")

        response = {
            "safe": safe,
            "drift_score": drift_score,
            "guardian_status": guardian_status,
            "emergency_active": emergency_file.exists(),
            "enforcement_enabled": dsl_setting != "0",
            "schema_version": "1.0.0",
            "timestamp": time.time(),
            "correlation_id": str(uuid.uuid4())
        }

        if reason:
            response["reason"] = reason

        return response

    def validate_action_async(self,
                           operation_type: str,
                           component: str,
                           request_data: Optional[Dict[str, Any]] = None,
                           user_id: Optional[str] = None,
                           tier: Optional[str] = None,
                           lane: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate action using G.3 Guardian Policies Engine.

        This is the modern interface that uses the standardized schema.
        """
        if self.policies_engine:
            # Use advanced policies engine
            context = PolicyContext(
                operation_type=operation_type,
                component=component,
                user_id=user_id,
                tier=tier,
                lane=lane,
                request_data=request_data
            )

            response = self.policies_engine.evaluate_policies(context, request_data)
            return response.to_dict()
        else:
            # Fallback to legacy validation
            operation = {
                "type": operation_type,
                "component": component,
                "data": request_data or {},
                "user_id": user_id,
                "tier": tier
            }
            return self.validate_safety(operation)

    def validate_safety(self, operation: dict[str, Any]) -> dict[str, Any]:
        """Validate operation safety with emergency kill-switch check"""

        # CRITICAL: Check for emergency kill-switch
        emergency_file = Path("/tmp/guardian_emergency_disable")
        if emergency_file.exists():
            self.logger.critical("🚨 EMERGENCY KILL-SWITCH ACTIVATED - All operations disabled")
            return self._create_standard_response(
                safe=False,
                drift_score=1.0,
                guardian_status="emergency_disabled",
                reason="Emergency kill-switch activated"
            )

        # Check if Guardian enforcement is enabled (FAIL CLOSED by default)
        dsl_setting = os.getenv("ENFORCE_ETHICS_DSL", "1")
        enforce_dsl = dsl_setting != "0"
        if not enforce_dsl:
            self.logger.warning("Guardian enforcement explicitly disabled via ENFORCE_ETHICS_DSL=0")
            return self._create_standard_response(
                safe=True,
                drift_score=0.0,
                guardian_status="disabled"
            )

        # Normal safety validation (when enabled and no emergency)
        self.logger.debug("Guardian validating operation safety")
        return self._create_standard_response(
            safe=True,
            drift_score=0.05,
            guardian_status="active"
        )

    async def initialize_async(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize Guardian system asynchronously with fail-safe defaults

        Args:
            config: Optional configuration dictionary for Guardian policies

        Returns:
            Initialization status with correlation tracking
        """
        start_time = time.time()
        correlation_id = str(uuid.uuid4())

        try:
            self.logger.info(f"Guardian async initialization started - correlation_id: {correlation_id}")

            # Load policies with circuit breaker and retry protection
            try:
                await self._execute_with_retry_and_circuit_breaker(
                    "policy_loading",
                    self._load_policies_async,
                    config,
                    correlation_id=correlation_id,
                    circuit_breaker="policy_loading",
                    max_retries=2  # Lower retries for initialization
                )
            except (GuardianCircuitOpenError, GuardianOperationFailedError) as e:
                self.logger.warning(f"Policy loading failed with protection: {e}, using fail-safe defaults")
                self._policies = self._get_failsafe_policies()

            # Initialize monitoring systems with protection
            try:
                await self._execute_with_retry_and_circuit_breaker(
                    "monitoring_initialization",
                    self._initialize_monitoring_async,
                    correlation_id=correlation_id,
                    circuit_breaker="monitoring",
                    max_retries=1
                )
            except (GuardianCircuitOpenError, GuardianOperationFailedError) as e:
                self.logger.warning(f"Monitoring initialization failed: {e}, continuing without monitoring")
                self._monitoring_active = False

            self._initialized = True
            init_time = time.time() - start_time

            self.logger.info(f"Guardian initialization completed in {init_time:.3f}s - correlation_id: {correlation_id}")

            return {
                "status": "initialized",
                "initialization_time_ms": init_time * 1000,
                "correlation_id": correlation_id,
                "policies_loaded": len(self._policies),
                "monitoring_active": self._monitoring_active,
                "schema_version": "1.0.0",
                "timestamp": time.time()
            }

        except Exception as e:
            self.logger.error(f"Guardian initialization failed: {e} - correlation_id: {correlation_id}")
            # Fail-safe: basic initialization
            self._policies = self._get_failsafe_policies()
            self._initialized = True

            return {
                "status": "initialized_failsafe",
                "error": str(e),
                "correlation_id": correlation_id,
                "policies_loaded": len(self._policies),
                "monitoring_active": False,
                "schema_version": "1.0.0",
                "timestamp": time.time()
            }

    async def validate_action_async(self, action: Dict[str, Any],
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Asynchronously validate action with multi-factor ethical evaluation

        Args:
            action: Action to validate
            context: Optional context data for validation

        Returns:
            Standardized Guardian response with validation results
        """
        start_time = time.time()
        correlation_id = str(uuid.uuid4())

        try:
            # Check emergency kill-switch first
            emergency_file = Path("/tmp/guardian_emergency_disable")
            if emergency_file.exists():
                self.logger.critical(f"🚨 EMERGENCY KILL-SWITCH ACTIVATED - Action blocked - correlation_id: {correlation_id}")
                return self._create_standard_response(
                    safe=False,
                    drift_score=1.0,
                    guardian_status="emergency_disabled",
                    reason="Emergency kill-switch activated"
                )

            # Check enforcement setting
            dsl_setting = os.getenv("ENFORCE_ETHICS_DSL", "1")
            if dsl_setting == "0":
                self.logger.warning(f"Guardian enforcement disabled - correlation_id: {correlation_id}")
                return self._create_standard_response(
                    safe=True,
                    drift_score=0.0,
                    guardian_status="disabled"
                )

            # Perform async validation with circuit breaker protection
            try:
                validation_result = await self._execute_with_retry_and_circuit_breaker(
                    "ethical_evaluation",
                    self._perform_ethical_evaluation_async,
                    action,
                    context,
                    correlation_id=correlation_id,
                    circuit_breaker="validation",
                    max_retries=2
                )
            except GuardianCircuitOpenError:
                self.logger.warning(f"Validation circuit breaker open, failing closed - correlation_id: {correlation_id}")
                return self._create_standard_response(
                    safe=False,
                    drift_score=0.8,
                    guardian_status="circuit_open_fail_closed",
                    reason="Validation circuit breaker open - failed closed for safety"
                )
            except GuardianOperationFailedError:
                self.logger.warning(f"Validation operation failed after retries, failing closed - correlation_id: {correlation_id}")
                return self._create_standard_response(
                    safe=False,
                    drift_score=0.9,
                    guardian_status="validation_failed_fail_closed",
                    reason="Validation failed after retries - failed closed for safety"
                )

            validation_time = time.time() - start_time
            self.logger.debug(f"Action validation completed in {validation_time:.3f}s - correlation_id: {correlation_id}")

            response = self._create_standard_response(
                safe=validation_result.get("safe", False),
                drift_score=validation_result.get("drift_score", 0.05),
                guardian_status="active",
                reason=validation_result.get("reason")
            )
            response["validation_time_ms"] = validation_time * 1000
            response["correlation_id"] = correlation_id

            return response

        except Exception as e:
            self.logger.error(f"Action validation error: {e} - correlation_id: {correlation_id}")
            # Fail closed on errors
            return self._create_standard_response(
                safe=False,
                drift_score=0.9,
                guardian_status="error_fail_closed",
                reason=f"Validation error: {str(e)}"
            )

    async def monitor_behavior_async(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Continuously monitor behavior for ethical compliance and drift detection

        Args:
            behavior_data: Behavioral data to monitor

        Returns:
            Monitoring assessment with drift analysis
        """
        start_time = time.time()
        correlation_id = str(uuid.uuid4())

        try:
            self.logger.debug(f"Guardian behavior monitoring started - correlation_id: {correlation_id}")

            # Perform behavioral analysis with circuit breaker protection
            try:
                monitoring_result = await self._execute_with_retry_and_circuit_breaker(
                    "behavior_analysis",
                    self._analyze_behavior_drift_async,
                    behavior_data,
                    correlation_id=correlation_id,
                    circuit_breaker="monitoring",
                    max_retries=1  # Lower retries for monitoring to maintain responsiveness
                )
            except GuardianCircuitOpenError:
                self.logger.warning(f"Monitoring circuit breaker open - correlation_id: {correlation_id}")
                return {
                    "status": "monitoring_circuit_open",
                    "drift_score": 0.0,
                    "risk_level": "unknown",
                    "correlation_id": correlation_id,
                    "schema_version": "1.0.0",
                    "timestamp": time.time()
                }
            except GuardianOperationFailedError:
                self.logger.warning(f"Behavior monitoring failed after retries - correlation_id: {correlation_id}")
                return {
                    "status": "monitoring_failed",
                    "drift_score": 0.5,  # Conservative default
                    "risk_level": "unknown",
                    "correlation_id": correlation_id,
                    "schema_version": "1.0.0",
                    "timestamp": time.time()
                }

            monitoring_time = time.time() - start_time
            drift_score = monitoring_result.get("drift_score", 0.0)

            # Assess risk level based on drift threshold
            if drift_score >= self.drift_threshold:
                risk_level = "high"
                self.logger.warning(f"High drift detected: {drift_score:.3f} >= {self.drift_threshold} - correlation_id: {correlation_id}")
            elif drift_score >= self.drift_threshold * 0.7:
                risk_level = "medium"
            else:
                risk_level = "low"

            response = {
                "status": "monitoring_complete",
                "drift_score": drift_score,
                "risk_level": risk_level,
                "behavioral_indicators": monitoring_result.get("indicators", {}),
                "monitoring_time_ms": monitoring_time * 1000,
                "correlation_id": correlation_id,
                "schema_version": "1.0.0",
                "timestamp": time.time()
            }

            self.logger.debug(f"Behavior monitoring completed - risk: {risk_level}, drift: {drift_score:.3f} - correlation_id: {correlation_id}")
            return response

        except Exception as e:
            self.logger.error(f"Behavior monitoring error: {e} - correlation_id: {correlation_id}")
            return {
                "status": "monitoring_error",
                "error": str(e),
                "drift_score": 0.5,  # Conservative default
                "risk_level": "unknown",
                "correlation_id": correlation_id,
                "schema_version": "1.0.0",
                "timestamp": time.time()
            }

    # Private async helper methods
    async def _load_policies_async(self, config: Optional[Dict[str, Any]]) -> None:
        """Load Guardian policies asynchronously"""
        # Simulate policy loading (will be enhanced in Phase 2)
        await asyncio.sleep(0.01)  # Minimal delay for realistic async behavior

        if config and "policies" in config:
            self._policies.update(config["policies"])
        else:
            self._policies = self._get_failsafe_policies()

        self.logger.debug(f"Loaded {len(self._policies)} Guardian policies")

    async def _initialize_monitoring_async(self) -> None:
        """Initialize monitoring systems asynchronously"""
        # Simulate monitoring initialization
        await asyncio.sleep(0.005)
        self._monitoring_active = True
        self.logger.debug("Guardian monitoring systems initialized")

    async def _perform_ethical_evaluation_async(self, action: Dict[str, Any],
                                               context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform multi-factor ethical evaluation"""
        # Simulate ethical evaluation (will be enhanced with real policies)
        await asyncio.sleep(0.002)  # Realistic evaluation time

        # Basic safety evaluation (enhanced in Phase 2)
        safe = True
        drift_score = 0.05
        reason = None

        # Check for obvious unsafe patterns
        if isinstance(action, dict):
            action_type = action.get("type", "")
            if "delete" in action_type.lower() or "remove" in action_type.lower():
                drift_score = 0.3
                reason = "Destructive action detected"

        return {
            "safe": safe,
            "drift_score": drift_score,
            "reason": reason
        }

    async def _analyze_behavior_drift_async(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behavioral drift patterns using GuardianReflector"""
        correlation_id = behavior_data.get('correlation_id', str(uuid.uuid4()))

        if self.reflector and GUARDIAN_REFLECTOR_AVAILABLE:
            try:
                # Use GuardianReflector for sophisticated analysis
                drift_analysis = await self.reflector.analyze_drift(behavior_data)

                # Convert to expected format
                return {
                    "drift_score": drift_analysis.overall_drift_score,
                    "indicators": {
                        "severity": drift_analysis.severity.value,
                        "trend_direction": drift_analysis.trend_direction,
                        "indicator_count": len(drift_analysis.indicators),
                        "confidence": drift_analysis.confidence_score,
                        "predictions": drift_analysis.prediction
                    },
                    "analysis_timestamp": drift_analysis.analysis_timestamp,
                    "correlation_id": correlation_id,
                    "advanced_analysis": True
                }
            except Exception as e:
                self.logger.warning(f"GuardianReflector analysis failed: {e}, falling back to basic analysis")

        # Fallback to basic drift analysis
        await asyncio.sleep(0.001)

        # Basic drift calculation
        drift_score = 0.02  # Low baseline drift
        indicators = {
            "pattern_anomalies": 0,
            "frequency_changes": 0,
            "content_shifts": 0,
            "advanced_analysis": False
        }

        return {
            "drift_score": drift_score,
            "indicators": indicators,
            "correlation_id": correlation_id
        }

    def _get_failsafe_policies(self) -> Dict[str, Any]:
        """Get fail-safe default policies"""
        return {
            "basic_safety": {"enabled": True, "threshold": self.drift_threshold},
            "emergency_response": {"enabled": True, "fail_closed": True},
            "drift_monitoring": {"enabled": True, "threshold": self.drift_threshold}
        }

    def _setup_circuit_breakers(self) -> None:
        """Setup Guardian-specific circuit breakers with T4/0.01% reliability"""
        if not CIRCUIT_BREAKER_AVAILABLE:
            return

        # Policy loading circuit breaker (more tolerant for config operations)
        self._circuit_breakers['policy_loading'] = _circuit_registry.get_or_create(
            "guardian_policy_loading",
            failure_threshold=0.7,  # 70% failure rate
            recovery_timeout=30.0,  # 30 seconds
            min_request_threshold=5,
            performance_threshold_ms=500.0  # 500ms for config loading
        )

        # Validation circuit breaker (strict for safety operations)
        self._circuit_breakers['validation'] = _circuit_registry.get_or_create(
            "guardian_validation",
            failure_threshold=0.3,  # 30% failure rate (strict)
            recovery_timeout=60.0,  # 60 seconds
            min_request_threshold=10,
            performance_threshold_ms=100.0  # 100ms SLA requirement
        )

        # Monitoring circuit breaker (balanced for continuous operations)
        self._circuit_breakers['monitoring'] = _circuit_registry.get_or_create(
            "guardian_monitoring",
            failure_threshold=0.5,  # 50% failure rate
            recovery_timeout=45.0,  # 45 seconds
            min_request_threshold=8,
            performance_threshold_ms=50.0  # 50ms for monitoring
        )

        self.logger.info("Guardian circuit breakers initialized")

    async def _execute_with_retry_and_circuit_breaker(self,
                                                     operation_name: str,
                                                     func,
                                                     *args,
                                                     correlation_id: str = None,
                                                     **kwargs) -> Any:
        """Execute function with retry logic and circuit breaker protection"""
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        circuit_breaker_name = kwargs.pop('circuit_breaker', 'validation')
        max_retries = kwargs.pop('max_retries', self._max_retries)

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                if CIRCUIT_BREAKER_AVAILABLE and circuit_breaker_name in self._circuit_breakers:
                    # Execute with circuit breaker protection
                    result = await self._circuit_breakers[circuit_breaker_name].call(
                        func, *args, correlation_id=correlation_id, **kwargs
                    )
                else:
                    # Fallback to direct execution
                    result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

                # Reset error count on success
                self._consecutive_errors = 0
                return result

            except CircuitBreakerOpenError as e:
                self.logger.warning(f"Guardian {operation_name} circuit breaker open - correlation_id: {correlation_id}")
                # Don't retry on circuit breaker open - fail fast
                raise GuardianCircuitOpenError(f"Guardian {operation_name} temporarily unavailable") from e

            except Exception as e:
                last_exception = e
                self._consecutive_errors += 1
                self._last_error_time = time.time()

                # Track error types for analytics
                error_type = type(e).__name__
                self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1

                if attempt < max_retries:
                    # Exponential backoff with jitter
                    delay = self._base_retry_delay * (2 ** attempt) * (0.5 + 0.5 * time.time() % 1)
                    self.logger.warning(
                        f"Guardian {operation_name} attempt {attempt + 1} failed: {e}, "
                        f"retrying in {delay:.3f}s - correlation_id: {correlation_id}"
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(
                        f"Guardian {operation_name} failed after {max_retries + 1} attempts - "
                        f"correlation_id: {correlation_id}, error: {e}"
                    )

        # All retries exhausted
        raise GuardianOperationFailedError(
            f"Guardian {operation_name} failed after {max_retries + 1} attempts"
        ) from last_exception

    def get_guardian_health_status(self) -> Dict[str, Any]:
        """Get comprehensive Guardian health status for monitoring"""
        health_status = {
            "guardian_status": "active" if self._initialized else "initializing",
            "policies_loaded": len(self._policies),
            "monitoring_active": self._monitoring_active,
            "consecutive_errors": self._consecutive_errors,
            "last_error_time": self._last_error_time,
            "error_counts": dict(self._error_counts),
            "drift_threshold": self.drift_threshold,
            "circuit_breakers": {},
            "timestamp": time.time(),
            "schema_version": "1.0.0"
        }

        # Add circuit breaker health if available
        if CIRCUIT_BREAKER_AVAILABLE:
            for name, breaker in self._circuit_breakers.items():
                health_status["circuit_breakers"][name] = breaker.get_health_status()

        # Calculate overall health score
        health_score = 1.0

        # Penalize for consecutive errors
        if self._consecutive_errors > 0:
            health_score *= max(0.1, 1.0 - (self._consecutive_errors * 0.1))

        # Penalize for circuit breaker issues
        if CIRCUIT_BREAKER_AVAILABLE:
            open_circuits = sum(1 for cb in self._circuit_breakers.values()
                              if cb.state.value == "open")
            if open_circuits > 0:
                health_score *= max(0.2, 1.0 - (open_circuits * 0.3))

        health_status["health_score"] = health_score
        health_status["health_grade"] = (
            "excellent" if health_score >= 0.9 else
            "good" if health_score >= 0.7 else
            "degraded" if health_score >= 0.5 else
            "critical"
        )

        # Add GuardianReflector status if available
        if self.reflector and GUARDIAN_REFLECTOR_AVAILABLE:
            health_status["reflector_status"] = {
                "available": True,
                "drift_history_size": len(self.reflector.drift_history),
                "analysis_performance": {
                    "avg_analysis_time_ms": (statistics.mean(self.reflector.analysis_times) * 1000)
                                           if self.reflector.analysis_times else 0,
                    "recent_analyses": len(self.reflector.analysis_times)
                },
                "memory_integration_enabled": self.reflector.memory_integration_enabled
            }
        else:
            health_status["reflector_status"] = {"available": False}

        # Add memory integration status
        health_status["memory_integration"] = {
            "enabled": self._memory_integration_enabled,
            "buffered_events": len(self._memory_event_buffer),
            "threshold_violations": self._memory_drift_threshold_violations,
            "last_drift_score": self._last_memory_drift_score,
            "registered_callbacks": len(self._memory_callbacks)
        }

        return health_status

    # Memory Integration Methods

    def enable_memory_integration(self, memory_event_factory=None) -> None:
        """Enable integration with Memory system for real-time drift monitoring"""
        self._memory_integration_enabled = True

        # Setup GuardianReflector memory integration if available
        if self.reflector and GUARDIAN_REFLECTOR_AVAILABLE:
            self.reflector.memory_integration_enabled = True
            self.reflector.memory_drift_callback = self._process_memory_drift_event

        # If memory_event_factory is provided, register as callback
        if memory_event_factory:
            self._register_memory_callback(memory_event_factory)

        self.logger.info("Guardian-Memory integration enabled")

    def disable_memory_integration(self) -> None:
        """Disable Memory system integration"""
        self._memory_integration_enabled = False

        if self.reflector and GUARDIAN_REFLECTOR_AVAILABLE:
            self.reflector.memory_integration_enabled = False
            self.reflector.memory_drift_callback = None

        self.logger.info("Guardian-Memory integration disabled")

    def _register_memory_callback(self, memory_event_factory) -> None:
        """Register callback with Memory system for drift events"""
        try:
            # Add Guardian as a listener for memory drift events
            # This would integrate with the actual MemoryEventFactory
            callback_id = f"guardian_{id(self)}"
            self._memory_callbacks.append(callback_id)
            self.logger.info(f"Registered memory callback: {callback_id}")
        except Exception as e:
            self.logger.error(f"Failed to register memory callback: {e}")

    async def process_memory_event(self, memory_event: Dict[str, Any]) -> Dict[str, Any]:
        """Process memory event and assess safety implications

        Args:
            memory_event: Memory event data from MemoryEventFactory

        Returns:
            Guardian assessment of memory event safety
        """
        correlation_id = memory_event.get('correlation_id', str(uuid.uuid4()))
        start_time = time.time()

        try:
            # Extract memory drift metrics
            metadata = memory_event.get('metadata', {})
            metrics = metadata.get('metrics', {})

            affect_delta = metrics.get('affect_delta', 0.0)
            drift_score = metrics.get('driftScore', 0.0)
            drift_trend = metrics.get('driftTrend', 0.0)

            # Store memory event in buffer
            memory_summary = {
                'timestamp': time.time(),
                'affect_delta': affect_delta,
                'drift_score': drift_score,
                'drift_trend': drift_trend,
                'correlation_id': correlation_id
            }
            self._memory_event_buffer.append(memory_summary)
            self._last_memory_drift_score = drift_score

            # Check for drift threshold violations
            if drift_score >= self.drift_threshold:
                self._memory_drift_threshold_violations += 1
                self.logger.warning(
                    f"Memory drift threshold exceeded: {drift_score:.3f} >= {self.drift_threshold} - "
                    f"correlation_id: {correlation_id}"
                )

            # Enhanced drift analysis using GuardianReflector if available
            guardian_assessment = {
                'memory_drift_assessment': {
                    'safe': drift_score < self.drift_threshold,
                    'drift_score': drift_score,
                    'affect_delta': affect_delta,
                    'drift_trend': drift_trend,
                    'threshold_exceeded': drift_score >= self.drift_threshold,
                    'violation_count': self._memory_drift_threshold_violations
                },
                'correlation_id': correlation_id,
                'assessment_timestamp': time.time(),
                'processing_time_ms': (time.time() - start_time) * 1000
            }

            # Use GuardianReflector for advanced analysis if available
            if self.reflector and GUARDIAN_REFLECTOR_AVAILABLE:
                try:
                    # Enhance context with memory metrics for advanced analysis
                    enhanced_context = {
                        **memory_event,
                        'memory_metrics': metrics,
                        'guardian_context': True,
                        'correlation_id': correlation_id
                    }

                    reflector_analysis = await self.reflector.analyze_drift(enhanced_context)

                    guardian_assessment['advanced_analysis'] = {
                        'overall_drift_score': reflector_analysis.overall_drift_score,
                        'severity': reflector_analysis.severity.value,
                        'trend_direction': reflector_analysis.trend_direction,
                        'confidence': reflector_analysis.confidence_score,
                        'recommendations': reflector_analysis.remediation_recommendations
                    }

                    # Update safety assessment based on advanced analysis
                    guardian_assessment['memory_drift_assessment']['safe'] = (
                        reflector_analysis.overall_drift_score < self.drift_threshold and
                        reflector_analysis.severity.value not in ['high', 'critical']
                    )

                except Exception as e:
                    self.logger.warning(f"Advanced memory analysis failed: {e}")
                    guardian_assessment['advanced_analysis'] = {'error': str(e)}

            self.logger.debug(
                f"Memory event processed - drift: {drift_score:.3f}, safe: {guardian_assessment['memory_drift_assessment']['safe']} - "
                f"correlation_id: {correlation_id}"
            )

            return guardian_assessment

        except Exception as e:
            self.logger.error(f"Memory event processing failed: {e} - correlation_id: {correlation_id}")
            return {
                'memory_drift_assessment': {
                    'safe': False,  # Fail closed on processing errors
                    'error': str(e),
                    'processing_failed': True
                },
                'correlation_id': correlation_id,
                'assessment_timestamp': time.time(),
                'processing_time_ms': (time.time() - start_time) * 1000
            }

    async def _process_memory_drift_event(self, drift_analysis) -> None:
        """Internal callback for processing drift events from GuardianReflector"""
        try:
            # Handle drift analysis from GuardianReflector
            if drift_analysis.overall_drift_score >= self.drift_threshold:
                self.logger.warning(
                    f"GuardianReflector detected threshold violation: {drift_analysis.overall_drift_score:.3f} - "
                    f"severity: {drift_analysis.severity.value}"
                )

                # Trigger additional safety measures if needed
                if drift_analysis.severity.value in ['high', 'critical']:
                    await self._handle_critical_drift_event(drift_analysis)

        except Exception as e:
            self.logger.error(f"Memory drift event processing failed: {e}")

    async def _handle_critical_drift_event(self, drift_analysis) -> None:
        """Handle critical drift events with emergency protocols"""
        correlation_id = drift_analysis.correlation_id

        self.logger.critical(
            f"CRITICAL DRIFT EVENT - score: {drift_analysis.overall_drift_score:.3f}, "
            f"severity: {drift_analysis.severity.value} - correlation_id: {correlation_id}"
        )

        # Could trigger additional safety measures here:
        # - Notify human operators
        # - Enable enhanced monitoring
        # - Restrict certain operations
        # - Generate incident report

    def get_memory_integration_status(self) -> Dict[str, Any]:
        """Get detailed status of Memory-Guardian integration"""
        recent_events = list(self._memory_event_buffer)[-10:]  # Last 10 events

        return {
            'integration_enabled': self._memory_integration_enabled,
            'total_events_processed': len(self._memory_event_buffer),
            'threshold_violations': self._memory_drift_threshold_violations,
            'last_drift_score': self._last_memory_drift_score,
            'recent_events': recent_events,
            'average_drift_score': (
                sum(event['drift_score'] for event in recent_events) / len(recent_events)
                if recent_events else 0.0
            ),
            'drift_threshold': self.drift_threshold,
            'violation_rate': (
                self._memory_drift_threshold_violations / len(self._memory_event_buffer)
                if self._memory_event_buffer else 0.0
            ),
            'reflector_integration': (
                self.reflector.memory_integration_enabled
                if self.reflector and GUARDIAN_REFLECTOR_AVAILABLE else False
            )
        }


class GuardianCircuitOpenError(Exception):
    """Exception raised when Guardian circuit breaker is open"""
    pass


class GuardianOperationFailedError(Exception):
    """Exception raised when Guardian operation fails after all retries"""
    pass
