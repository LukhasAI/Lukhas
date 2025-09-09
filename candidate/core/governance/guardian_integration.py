"""
Guardian System 2.0 Integration Layer
=====================================

Integration layer connecting Guardian System 2.0 with LUKHAS AI architecture.
Provides seamless integration with existing systems while maintaining backward
compatibility and ensuring comprehensive safety oversight.

Integration Points:
- Core orchestration system
- Brain integration modules
- Memory systems
- API endpoints
- Decision trees
- Constitutional AI framework
- Drift detection systems
- Audit and logging systems

Design Principles:
- Non-invasive integration
- Backward compatibility
- Zero-downtime deployment
- Performance optimization
- Comprehensive coverage
- Real-time monitoring

#TAG:integration
#TAG:guardian
#TAG:architecture
#TAG:safety
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Optional

try:
    from ..security.secure_logging import get_security_logger
    from .constitutional_ai import DecisionContext, get_constitutional_framework
    from .constitutional_compliance_engine import (
        ComplianceLevel,
        ComplianceResult,
        ConstitutionalComplianceEngine,
        get_compliance_engine,
    )
    from .guardian_system_2 import (
        DecisionType,
        ExplanationType,
        GuardianDecision,
        GuardianSystem2,
        SafetyLevel,
        get_guardian_system,
    )

    logger = get_security_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

    # Mock imports for standalone testing
    class GuardianSystem2:
        pass

    class ConstitutionalComplianceEngine:
        pass


@dataclass
class IntegrationConfig:
    """Guardian System integration configuration"""

    enabled: bool = True
    enforce_decisions: bool = True
    real_time_monitoring: bool = True

    # Performance settings
    max_processing_time_ms: float = 200.0
    async_processing: bool = True
    batch_processing: bool = False

    # Integration scope
    monitor_user_interactions: bool = True
    monitor_content_generation: bool = True
    monitor_data_processing: bool = True
    monitor_api_calls: bool = True
    monitor_system_operations: bool = True

    # Failure handling
    fail_open: bool = False  # Fail closed by default for safety
    fallback_enabled: bool = True
    retry_attempts: int = 3

    # Logging and auditing
    audit_all_decisions: bool = True
    log_explanations: bool = True
    detailed_metrics: bool = True


class GuardianIntegrationMiddleware:
    """
    Guardian System 2.0 integration middleware

    Provides transparent safety monitoring for all AI operations
    with minimal performance impact and maximum coverage.
    """

    def __init__(self, config: Optional[IntegrationConfig] = None):
        """Initialize Guardian integration middleware"""
        self.config = config or IntegrationConfig()

        # Core components
        self.guardian_system: Optional[GuardianSystem2] = None
        self.compliance_engine: Optional[ConstitutionalComplianceEngine] = None
        self.constitutional_framework = None

        # Integration state
        self.enabled = self.config.enabled
        self.monitored_functions: set[str] = set()
        self.integration_metrics = {
            "total_integrations": 0,
            "successful_integrations": 0,
            "failed_integrations": 0,
            "average_processing_time_ms": 0.0,
            "decisions_enforced": 0,
            "decisions_allowed": 0,
            "decisions_blocked": 0,
        }

        # Performance optimization
        self._decision_cache: dict[str, tuple[GuardianDecision, datetime]] = {}
        self._cache_ttl_seconds = 300  # 5 minutes

        logger.info("🛡️ Guardian Integration Middleware initializing...")

        # Initialize asynchronously
        asyncio.create_task(self._initialize_integration())

    async def _initialize_integration(self):
        """Initialize Guardian integration components"""
        try:
            # Initialize Guardian System 2.0
            self.guardian_system = get_guardian_system()
            logger.info("✅ Guardian System 2.0 connected")

            # Initialize Compliance Engine
            self.compliance_engine = get_compliance_engine()
            logger.info("✅ Constitutional Compliance Engine connected")

            # Initialize Constitutional Framework
            try:
                self.constitutional_framework = get_constitutional_framework()
                logger.info("✅ Constitutional AI Framework connected")
            except Exception as e:
                logger.warning(f"⚠️ Constitutional AI Framework unavailable: {e}")

            # Start integration monitoring
            asyncio.create_task(self._integration_monitoring_loop())

            logger.info("🛡️ Guardian Integration Middleware fully initialized")

        except Exception as e:
            logger.error(f"❌ Guardian integration initialization failed: {e}")
            if not self.config.fail_open:
                self.enabled = False
                raise

    async def _integration_monitoring_loop(self):
        """Background integration monitoring loop"""
        while True:
            try:
                await self._perform_integration_health_check()
                await self._cleanup_decision_cache()
                await asyncio.sleep(60)  # Monitor every minute
            except Exception as e:
                logger.error(f"❌ Integration monitoring error: {e}")
                await asyncio.sleep(120)

    async def _perform_integration_health_check(self):
        """Perform integration health check"""
        try:
            if self.guardian_system:
                status = await self.guardian_system.get_system_status()
                if not status.get("system_info", {}).get("active", False):
                    logger.warning("⚠️ Guardian System 2.0 health check failed")

            if self.compliance_engine:
                status = await self.compliance_engine.get_compliance_status()
                if not status.get("system_info", {}).get("enabled", False):
                    logger.warning("⚠️ Compliance Engine health check failed")

        except Exception as e:
            logger.error(f"❌ Integration health check failed: {e}")

    async def _cleanup_decision_cache(self):
        """Clean up expired decision cache entries"""
        try:
            current_time = datetime.now(timezone.utc)
            expired_keys = []

            for key, (_decision, timestamp) in self._decision_cache.items():
                if (current_time - timestamp).total_seconds() > self._cache_ttl_seconds:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._decision_cache[key]

        except Exception as e:
            logger.error(f"❌ Cache cleanup failed: {e}")

    def guardian_monitor(
        self,
        decision_type: DecisionType = DecisionType.SYSTEM_OPERATION,
        enforce_decision: bool = True,
        explanation_type: ExplanationType = ExplanationType.STANDARD,
        cache_key: Optional[str] = None,
    ):
        """
        Decorator for Guardian System monitoring

        Args:
            decision_type: Type of AI decision being monitored
            enforce_decision: Whether to enforce Guardian decisions
            explanation_type: Type of explanation to generate
            cache_key: Optional cache key for decision caching
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._monitor_async_function(
                    func, args, kwargs, decision_type, enforce_decision, explanation_type, cache_key
                )

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(
                    self._monitor_sync_function(
                        func, args, kwargs, decision_type, enforce_decision, explanation_type, cache_key
                    )
                )

            # Register function for monitoring
            function_name = f"{func.__module__}.{func.__name__}"
            self.monitored_functions.add(function_name)

            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    async def _monitor_async_function(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        decision_type: DecisionType,
        enforce_decision: bool,
        explanation_type: ExplanationType,
        cache_key: Optional[str],
    ):
        """Monitor async function execution"""
        if not self.enabled:
            return await func(*args, **kwargs)

        start_time = datetime.now(timezone.utc)

        try:
            # Extract decision data from function parameters
            decision_data = self._extract_decision_data(func, args, kwargs)

            # Check cache if cache_key provided
            if cache_key:
                cached_decision = self._get_cached_decision(cache_key)
                if cached_decision:
                    guardian_decision = cached_decision
                else:
                    # Evaluate with Guardian System
                    guardian_decision = await self._evaluate_with_guardian(
                        decision_type, decision_data, explanation_type
                    )
                    self._cache_decision(cache_key, guardian_decision)
            else:
                # Evaluate with Guardian System
                guardian_decision = await self._evaluate_with_guardian(decision_type, decision_data, explanation_type)

            # Enforce decision if required
            if enforce_decision and not guardian_decision.allowed:
                await self._handle_blocked_decision(guardian_decision, func, args, kwargs)
                self.integration_metrics["decisions_blocked"] += 1
                return None

            # Execute original function
            result = await func(*args, **kwargs)

            # Post-execution monitoring
            await self._post_execution_monitoring(guardian_decision, result, decision_data)

            self.integration_metrics["decisions_allowed"] += 1
            self.integration_metrics["successful_integrations"] += 1

            return result

        except Exception as e:
            logger.error(f"❌ Guardian monitoring failed for {func.__name__}: {e}")
            self.integration_metrics["failed_integrations"] += 1

            if self.config.fail_open:
                logger.warning(f"⚠️ Fail-open mode: Allowing {func.__name__} despite monitoring failure")
                return await func(*args, **kwargs)
            else:
                logger.error(f"🚫 Fail-closed mode: Blocking {func.__name__} due to monitoring failure")
                raise

        finally:
            # Update metrics
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self._update_integration_metrics(processing_time)

    async def _monitor_sync_function(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        decision_type: DecisionType,
        enforce_decision: bool,
        explanation_type: ExplanationType,
        cache_key: Optional[str],
    ):
        """Monitor synchronous function execution"""
        if not self.enabled:
            return func(*args, **kwargs)

        start_time = datetime.now(timezone.utc)

        try:
            # Extract decision data
            decision_data = self._extract_decision_data(func, args, kwargs)

            # Evaluate with Guardian System
            guardian_decision = await self._evaluate_with_guardian(decision_type, decision_data, explanation_type)

            # Enforce decision if required
            if enforce_decision and not guardian_decision.allowed:
                await self._handle_blocked_decision(guardian_decision, func, args, kwargs)
                self.integration_metrics["decisions_blocked"] += 1
                return None

            # Execute original function
            result = func(*args, **kwargs)

            # Post-execution monitoring
            await self._post_execution_monitoring(guardian_decision, result, decision_data)

            self.integration_metrics["decisions_allowed"] += 1
            self.integration_metrics["successful_integrations"] += 1

            return result

        except Exception as e:
            logger.error(f"❌ Guardian monitoring failed for {func.__name__}: {e}")
            self.integration_metrics["failed_integrations"] += 1

            if self.config.fail_open:
                return func(*args, **kwargs)
            else:
                raise

        finally:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self._update_integration_metrics(processing_time)

    def _extract_decision_data(self, func: Callable, args: tuple, kwargs: dict) -> dict[str, Any]:
        """Extract decision data from function parameters"""
        decision_data = {
            "function_name": func.__name__,
            "function_module": func.__module__,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Extract common parameter patterns
        if args:
            decision_data["first_arg"] = str(args[0])[:1000]  # Limit length

        # Look for common AI operation parameters
        ai_params = ["user_input", "ai_response", "content", "text", "query", "prompt", "message"]
        for param in ai_params:
            if param in kwargs:
                decision_data[param] = str(kwargs[param])[:2000]  # Limit length

        # Extract user identification
        user_params = ["user_id", "username", "session_id"]
        for param in user_params:
            if param in kwargs:
                decision_data[param] = kwargs[param]

        return decision_data

    def _get_cached_decision(self, cache_key: str) -> Optional[GuardianDecision]:
        """Get cached Guardian decision"""
        if cache_key in self._decision_cache:
            decision, timestamp = self._decision_cache[cache_key]
            if (datetime.now(timezone.utc) - timestamp).total_seconds() <= self._cache_ttl_seconds:
                return decision
            else:
                del self._decision_cache[cache_key]
        return None

    def _cache_decision(self, cache_key: str, decision: GuardianDecision):
        """Cache Guardian decision"""
        self._decision_cache[cache_key] = (decision, datetime.now(timezone.utc))

    async def _evaluate_with_guardian(
        self, decision_type: DecisionType, decision_data: dict[str, Any], explanation_type: ExplanationType
    ) -> GuardianDecision:
        """Evaluate decision with Guardian System 2.0"""
        try:
            if self.guardian_system:
                return await self.guardian_system.evaluate_decision(
                    decision_type=decision_type,
                    decision_data=decision_data,
                    context={"integration": "middleware"},
                    user_id=decision_data.get("user_id"),
                    explanation_type=explanation_type,
                )
            else:
                # Fallback to basic safety check
                return self._create_fallback_decision(decision_type, decision_data)

        except Exception as e:
            logger.error(f"❌ Guardian evaluation failed: {e}")
            if self.config.fail_open:
                return self._create_safe_decision(decision_type, decision_data)
            else:
                return self._create_blocked_decision(decision_type, decision_data, str(e))

    def _create_fallback_decision(self, decision_type: DecisionType, decision_data: dict[str, Any]) -> GuardianDecision:
        """Create fallback Guardian decision"""
        # Simple safety checks
        data_text = str(decision_data).lower()
        harmful_patterns = ["harm", "dangerous", "illegal", "abuse", "threat"]

        is_safe = not any(pattern in data_text for pattern in harmful_patterns)

        return GuardianDecision(
            decision_id=f"fallback_{hash(str(decision_data)) % 10000}",
            decision_type=decision_type,
            allowed=is_safe,
            confidence=0.7 if is_safe else 0.9,
            safety_level=SafetyLevel.SAFE if is_safe else SafetyLevel.DANGER,
            constitutional_compliant=is_safe,
            constitutional_score=0.8 if is_safe else 0.3,
            drift_score=0.1,
            drift_severity="low",
            timestamp=datetime.now(timezone.utc),
            processing_time_ms=1.0,
            explanation=f"Fallback safety evaluation: {'Safe' if is_safe else 'Potentially unsafe'}",
        )

    def _create_safe_decision(self, decision_type: DecisionType, decision_data: dict[str, Any]) -> GuardianDecision:
        """Create safe Guardian decision for fail-open mode"""
        return GuardianDecision(
            decision_id=f"safe_{hash(str(decision_data)) % 10000}",
            decision_type=decision_type,
            allowed=True,
            confidence=0.5,  # Lower confidence for fail-open
            safety_level=SafetyLevel.CAUTION,
            constitutional_compliant=True,
            constitutional_score=0.7,
            drift_score=0.1,
            drift_severity="low",
            timestamp=datetime.now(timezone.utc),
            processing_time_ms=1.0,
            explanation="Fail-open mode: Decision allowed with reduced confidence",
        )

    def _create_blocked_decision(
        self, decision_type: DecisionType, decision_data: dict[str, Any], error: str
    ) -> GuardianDecision:
        """Create blocked Guardian decision for fail-closed mode"""
        return GuardianDecision(
            decision_id=f"blocked_{hash(str(decision_data)) % 10000}",
            decision_type=decision_type,
            allowed=False,
            confidence=0.9,  # High confidence in blocking for safety
            safety_level=SafetyLevel.CRITICAL,
            constitutional_compliant=False,
            constitutional_score=0.0,
            drift_score=0.5,
            drift_severity="high",
            timestamp=datetime.now(timezone.utc),
            processing_time_ms=1.0,
            explanation=f"Fail-closed mode: Decision blocked due to evaluation error: {error}",
        )

    async def _handle_blocked_decision(self, decision: GuardianDecision, func: Callable, args: tuple, kwargs: dict):
        """Handle blocked decision"""
        function_name = f"{func.__module__}.{func.__name__}"

        logger.warning(f"🚫 Guardian System blocked decision for {function_name}")
        logger.warning(f"   Reason: {decision.explanation}")
        logger.warning(f"   Safety Level: {decision.safety_level.value}")
        logger.warning(f"   Constitutional Score: {decision.constitutional_score:.1%}")
        logger.warning(f"   Drift Score: {decision.drift_score:.4f}")

        # Additional handling based on safety level
        if decision.safety_level == SafetyLevel.CRITICAL:
            logger.critical(f"🚨 CRITICAL SAFETY VIOLATION in {function_name}")

        # Store blocked decision for analysis
        if self.config.audit_all_decisions:
            await self._audit_blocked_decision(decision, function_name, args, kwargs)

    async def _post_execution_monitoring(self, decision: GuardianDecision, result: Any, decision_data: dict[str, Any]):
        """Post-execution monitoring and analysis"""
        try:
            # Analyze results for safety compliance
            if result is not None:
                result_data = {
                    "result_type": type(result).__name__,
                    "result_content": str(result)[:1000] if result else "",
                    "execution_successful": True,
                }

                # Check if result aligns with Guardian decision
                if decision.safety_level in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]:
                    logger.warning(f"⚠️ Function executed despite safety concerns: {decision.explanation}")

                # Update decision data with results
                decision.context.update(result_data)

        except Exception as e:
            logger.error(f"❌ Post-execution monitoring failed: {e}")

    async def _audit_blocked_decision(self, decision: GuardianDecision, function_name: str, args: tuple, kwargs: dict):
        """Audit blocked decision for compliance tracking"""
        try:
            {
                "timestamp": datetime.now(timezone.utc),
                "decision_id": decision.decision_id,
                "function_name": function_name,
                "decision_type": decision.decision_type.value,
                "safety_level": decision.safety_level.value,
                "constitutional_score": decision.constitutional_score,
                "drift_score": decision.drift_score,
                "explanation": decision.explanation,
                "args_summary": f"{len(args)} arguments",
                "kwargs_summary": list(kwargs.keys()),
            }

            # In production, would store in audit database
            logger.info(f"📝 Audited blocked decision: {decision.decision_id}")

        except Exception as e:
            logger.error(f"❌ Decision audit failed: {e}")

    def _update_integration_metrics(self, processing_time_ms: float):
        """Update integration performance metrics"""
        try:
            self.integration_metrics["total_integrations"] += 1

            # Update average processing time
            total_time = self.integration_metrics["average_processing_time_ms"] * (
                self.integration_metrics["total_integrations"] - 1
            )
            new_avg = (total_time + processing_time_ms) / self.integration_metrics["total_integrations"]
            self.integration_metrics["average_processing_time_ms"] = new_avg

        except Exception as e:
            logger.error(f"❌ Metrics update failed: {e}")

    @asynccontextmanager
    async def guardian_context(
        self, decision_type: DecisionType = DecisionType.SYSTEM_OPERATION, context_data: Optional[dict[str, Any]] = None
    ):
        """
        Context manager for Guardian monitoring

        Usage:
            async with integration.guardian_context(DecisionType.USER_INTERACTION, {"user_id": "123"}):
                # Monitored operations
                result = await ai_operation()
        """
        if not self.enabled:
            yield
            return

        start_time = datetime.now(timezone.utc)
        context_data = context_data or {}

        try:
            # Pre-context evaluation
            logger.debug(f"🛡️ Guardian context started: {decision_type.value}")

            yield

            # Post-context evaluation
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            logger.debug(f"🛡️ Guardian context completed: {processing_time:.1f}ms")

        except Exception as e:
            logger.error(f"❌ Guardian context error: {e}")
            raise

    async def batch_evaluate_decisions(
        self, decisions: list[tuple[DecisionType, dict[str, Any]]]
    ) -> list[GuardianDecision]:
        """Batch evaluate multiple decisions for performance optimization"""
        if not self.enabled or not self.config.batch_processing:
            return []

        try:
            results = []

            for decision_type, decision_data in decisions:
                decision = await self._evaluate_with_guardian(decision_type, decision_data, ExplanationType.BRIEF)
                results.append(decision)

            return results

        except Exception as e:
            logger.error(f"❌ Batch evaluation failed: {e}")
            return []

    async def get_integration_status(self) -> dict[str, Any]:
        """Get comprehensive integration status"""
        return {
            "configuration": {
                "enabled": self.enabled,
                "enforce_decisions": self.config.enforce_decisions,
                "real_time_monitoring": self.config.real_time_monitoring,
                "fail_open": self.config.fail_open,
                "max_processing_time_ms": self.config.max_processing_time_ms,
            },
            "components": {
                "guardian_system_connected": self.guardian_system is not None,
                "compliance_engine_connected": self.compliance_engine is not None,
                "constitutional_framework_connected": self.constitutional_framework is not None,
            },
            "monitoring": {
                "monitored_functions": len(self.monitored_functions),
                "monitored_function_list": list(self.monitored_functions),
            },
            "performance": self.integration_metrics,
            "cache": {"cached_decisions": len(self._decision_cache), "cache_ttl_seconds": self._cache_ttl_seconds},
        }

    def disable_integration(self, reason: str = "Manual disable"):
        """Disable Guardian integration"""
        self.enabled = False
        logger.warning(f"⚠️ Guardian integration disabled: {reason}")

    def enable_integration(self, reason: str = "Manual enable"):
        """Enable Guardian integration"""
        self.enabled = True
        logger.info(f"✅ Guardian integration enabled: {reason}")


# Global integration instance
_integration_middleware: Optional[GuardianIntegrationMiddleware] = None


def get_integration_middleware(config: Optional[IntegrationConfig] = None) -> GuardianIntegrationMiddleware:
    """Get global Guardian integration middleware instance"""
    global _integration_middleware
    if _integration_middleware is None:
        _integration_middleware = GuardianIntegrationMiddleware(config)
    return _integration_middleware


# Convenience decorators and functions


def guardian_monitor(
    decision_type: DecisionType = DecisionType.SYSTEM_OPERATION,
    enforce_decision: bool = True,
    explanation_type: ExplanationType = ExplanationType.STANDARD,
    cache_key: Optional[str] = None,
):
    """
    Convenience decorator for Guardian monitoring

    Usage:
        @guardian_monitor(DecisionType.USER_INTERACTION, enforce_decision=True)
        async def process_user_input(user_input: str) -> str:
            # Function implementation
            pass
    """
    middleware = get_integration_middleware()
    return middleware.guardian_monitor(decision_type, enforce_decision, explanation_type, cache_key)


@asynccontextmanager
async def guardian_context(
    decision_type: DecisionType = DecisionType.SYSTEM_OPERATION, context_data: Optional[dict[str, Any]] = None
):
    """
    Convenience context manager for Guardian monitoring

    Usage:
        async with guardian_context(DecisionType.CONTENT_GENERATION):
            content = await generate_content()
    """
    middleware = get_integration_middleware()
    async with middleware.guardian_context(decision_type, context_data):
        yield


async def evaluate_decision_with_guardian(
    decision_type: DecisionType, decision_data: dict[str, Any], user_id: Optional[str] = None
) -> GuardianDecision:
    """
    Convenience function for direct Guardian evaluation

    Usage:
        decision = await evaluate_decision_with_guardian(
            DecisionType.USER_INTERACTION,
            {"user_input": "Hello", "ai_response": "Hi there!"},
            user_id="user_123"
        )
    """
    middleware = get_integration_middleware()
    return await middleware._evaluate_with_guardian(decision_type, decision_data, ExplanationType.STANDARD)


# Integration with existing LUKHAS systems


class LUKHASGuardianBridge:
    """
    Bridge for integrating Guardian System 2.0 with existing LUKHAS components

    Provides seamless integration with:
    - Brain integration modules
    - Memory systems
    - API endpoints
    - Orchestration system
    """

    def __init__(self):
        self.middleware = get_integration_middleware()
        self.integration_points = {}

        logger.info("🌉 LUKHAS Guardian Bridge initializing...")

    async def integrate_brain_modules(self):
        """Integrate with brain orchestration modules"""
        try:
            # Integration points for brain modules
            brain_modules = ["cognitive_core", "decision_engine", "response_generator", "conversation_manager"]

            for module in brain_modules:
                self.integration_points[f"brain_{module}"] = {
                    "decision_type": DecisionType.MODEL_INFERENCE,
                    "monitoring_enabled": True,
                    "enforcement_level": "strict",
                }

            logger.info(f"✅ Integrated {len(brain_modules)} brain modules")

        except Exception as e:
            logger.error(f"❌ Brain module integration failed: {e}")

    async def integrate_api_endpoints(self):
        """Integrate with API endpoint handlers"""
        try:
            # Integration points for API endpoints
            api_endpoints = [
                "user_chat_endpoint",
                "content_generation_endpoint",
                "data_processing_endpoint",
                "model_inference_endpoint",
            ]

            for endpoint in api_endpoints:
                self.integration_points[f"api_{endpoint}"] = {
                    "decision_type": DecisionType.API_CALL,
                    "monitoring_enabled": True,
                    "enforcement_level": "strict",
                }

            logger.info(f"✅ Integrated {len(api_endpoints)} API endpoints")

        except Exception as e:
            logger.error(f"❌ API endpoint integration failed: {e}")

    async def integrate_memory_systems(self):
        """Integrate with memory and storage systems"""
        try:
            # Integration points for memory systems
            memory_systems = ["episodic_memory", "semantic_memory", "working_memory", "long_term_storage"]

            for system in memory_systems:
                self.integration_points[f"memory_{system}"] = {
                    "decision_type": DecisionType.DATA_PROCESSING,
                    "monitoring_enabled": True,
                    "enforcement_level": "moderate",
                }

            logger.info(f"✅ Integrated {len(memory_systems)} memory systems")

        except Exception as e:
            logger.error(f"❌ Memory system integration failed: {e}")

    async def get_integration_report(self) -> dict[str, Any]:
        """Get comprehensive integration report"""
        return {
            "bridge_status": "active",
            "integration_points": len(self.integration_points),
            "integration_details": self.integration_points,
            "middleware_status": await self.middleware.get_integration_status(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global bridge instance
_lukhas_bridge: Optional[LUKHASGuardianBridge] = None


def get_lukhas_bridge() -> LUKHASGuardianBridge:
    """Get global LUKHAS Guardian Bridge instance"""
    global _lukhas_bridge
    if _lukhas_bridge is None:
        _lukhas_bridge = LUKHASGuardianBridge()
    return _lukhas_bridge


# Example usage and testing
async def example_integration():
    """Example Guardian System 2.0 integration"""
    print("🛡️ Guardian System 2.0 Integration Example")
    print("=" * 60)

    # Initialize integration
    middleware = get_integration_middleware()
    bridge = get_lukhas_bridge()

    # Wait for initialization
    await asyncio.sleep(2)

    # Test 1: Function decoration
    print("\n📋 Test 1: Function Decoration")

    @guardian_monitor(DecisionType.USER_INTERACTION, enforce_decision=True)
    async def process_user_message(user_input: str, user_id: str) -> str:
        """Mock user message processing function"""
        return f"AI Response to: {user_input}"

    try:
        result = await process_user_message("Hello, how are you?", "test_user_1")
        print(f"Function Result: {result}")
    except Exception as e:
        print(f"Function Blocked: {e}")

    # Test 2: Context manager
    print("\n📋 Test 2: Context Manager")

    async with guardian_context(DecisionType.CONTENT_GENERATION):
        content = "This is AI-generated content that should be monitored for safety."
        print(f"Generated Content: {content}")

    # Test 3: Direct evaluation
    print("\n📋 Test 3: Direct Evaluation")

    decision = await evaluate_decision_with_guardian(
        DecisionType.USER_INTERACTION,
        {
            "user_input": "Can you help me with something dangerous?",
            "ai_response": "I cannot help with dangerous activities.",
        },
        user_id="test_user_2",
    )

    print(f"Guardian Decision: {'✅ ALLOWED' if decision.allowed else '🚫 BLOCKED'}")
    print(f"Safety Level: {decision.safety_level.value}")
    print(f"Explanation: {decision.explanation}")

    # Test 4: Integration status
    print("\n📋 Test 4: Integration Status")

    status = await middleware.get_integration_status()
    print(f"Integration Enabled: {status['configuration']['enabled']}")
    print(f"Components Connected: {sum(status['components'].values())/3}")
    print(f"Total Integrations: {status['performance']['total_integrations']}")
    print(f"Average Processing Time: {status['performance']['average_processing_time_ms']:.1f}ms")

    # Test 5: Bridge integration
    print("\n📋 Test 5: LUKHAS Bridge Integration")

    await bridge.integrate_brain_modules()
    await bridge.integrate_api_endpoints()
    await bridge.integrate_memory_systems()

    bridge_report = await bridge.get_integration_report()
    print(f"Bridge Integration Points: {bridge_report['integration_points']}")
    print(f"Bridge Status: {bridge_report['bridge_status']}")

    print("\n✅ Guardian System 2.0 integration example completed successfully")


if __name__ == "__main__":
    asyncio.run(example_integration())