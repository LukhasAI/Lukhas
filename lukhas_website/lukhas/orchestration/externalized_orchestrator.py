#!/usr/bin/env python3
"""
LUKHAS Phase 4 - Externalized Orchestrator
==========================================

Main orchestrator integrating all Phase 4 components:
- Externalized routing configuration with hot-reload
- Health-aware routing strategies
- Context preservation across hops
- Circuit breaker patterns
- A/B testing framework
- Integration with Context Bus

Performance Targets:
- <100ms routing decisions
- <250ms context handoff
- >99.9% availability through fallbacks
- Zero configuration downtime with hot-reload

Constellation Framework: Flow Star (🌊) coordination hub
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

from .context_preservation import ContextType, get_context_preservation_engine
from .health_monitor import get_health_monitor
from .kernel_bus import emit as bus_emit
from .kernel_bus import get_kernel_bus
from .routing_config import get_routing_config_manager
from .routing_strategies import RoutingContext, RoutingResult, get_routing_engine

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Prometheus metrics
orchestrator_requests_total = Counter(
    'lukhas_orchestrator_requests_total',
    'Total orchestrator requests',
    ['request_type', 'success', 'strategy']
)

orchestrator_latency_seconds = Histogram(
    'lukhas_orchestrator_latency_seconds',
    'End-to-end orchestrator latency',
    ['request_type'],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

orchestrator_active_contexts = Gauge(
    'lukhas_orchestrator_active_contexts',
    'Number of active contexts'
)

ab_test_traffic_ratio = Gauge(
    'lukhas_ab_test_traffic_ratio',
    'A/B test traffic ratio',
    ['experiment', 'variant']
)


class RequestType(Enum):
    """Types of orchestrator requests"""
    SINGLE_SHOT = "single_shot"
    STREAMING = "streaming"
    CONSENSUS = "consensus"
    PIPELINE = "pipeline"


@dataclass
class OrchestrationRequest:
    """Complete orchestration request"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    request_type: RequestType = RequestType.SINGLE_SHOT
    prompt: str = ""
    system_prompt: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    routing_hints: Dict[str, Any] = field(default_factory=dict)
    preserve_context: bool = True
    timeout_seconds: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResponse:
    """Complete orchestration response"""
    request_id: str
    session_id: str
    provider: str
    strategy_used: str
    response: str
    context_id: Optional[str] = None
    latency_ms: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)
    routing_hops: List[str] = field(default_factory=list)
    ab_test_variant: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExternalizedOrchestrator:
    """Main externalized orchestrator coordinating all Phase 4 components"""

    def __init__(self):
        # Component references (initialized async)
        self.config_manager = None
        self.routing_engine = None
        self.health_monitor = None
        self.context_engine = None
        self.kernel_bus = None

        # State tracking
        self.active_requests: Dict[str, OrchestrationRequest] = {}
        self.request_metrics: Dict[str, Dict[str, Any]] = {}

        # A/B test state
        self.ab_test_state: Dict[str, Any] = {}

        logger.info("Externalized orchestrator initialized")

    async def initialize(self) -> None:
        """Initialize orchestrator and all components"""
        logger.info("🚀 Initializing externalized orchestrator...")

        with tracer.start_span("orchestrator.initialize") as span:
            try:
                # Initialize all components
                self.config_manager = await get_routing_config_manager()
                self.routing_engine = get_routing_engine()
                self.health_monitor = await get_health_monitor()
                self.context_engine = await get_context_preservation_engine()
                self.kernel_bus = get_kernel_bus()

                # Register for configuration change events
                await self._register_event_handlers()

                # Initialize A/B test state
                await self._initialize_ab_tests()

                span.set_attribute("initialization_complete", True)
                logger.info("✅ Externalized orchestrator initialized successfully")

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                logger.error(f"❌ Failed to initialize orchestrator: {e}")
                raise

    async def orchestrate(self, request: OrchestrationRequest) -> OrchestrationResponse:
        """Main orchestration method"""
        start_time = time.time()

        with tracer.start_span("orchestrator.orchestrate") as span:
            span.set_attribute("request_id", request.request_id)
            span.set_attribute("session_id", request.session_id)
            span.set_attribute("request_type", request.request_type.value)

            try:
                # Track active request
                self.active_requests[request.request_id] = request
                orchestrator_active_contexts.set(len(self.active_requests))

                # Preserve context if requested
                context_id = None
                if request.preserve_context and request.context_data:
                    context_id = await self.context_engine.preserve_context(
                        session_id=request.session_id,
                        context_data=request.context_data,
                        context_type=ContextType.CONVERSATION
                    )

                # Emit orchestration start event
                await bus_emit(
                    "orchestration.request.started",
                    {
                        "request_id": request.request_id,
                        "session_id": request.session_id,
                        "request_type": request.request_type.value,
                        "context_id": context_id
                    },
                    source="externalized_orchestrator",
                    mode="live"
                )

                # Get routing configuration
                config = self.config_manager.get_configuration()

                # Determine request pattern for routing
                request_pattern = self._determine_request_pattern(request)

                # Find matching routing rule
                routing_context = RoutingContext(
                    session_id=request.session_id,
                    request_type=request_pattern,
                    metadata=request.routing_hints
                )

                rule = self.config_manager.get_rule_for_request(request_pattern, routing_context.metadata)
                if not rule:
                    raise ValueError(f"No routing rule found for pattern: {request_pattern}")

                # Check for A/B test
                ab_variant = None
                if rule.name in [test.rules for test in config.ab_tests if test.enabled]:
                    for test in config.ab_tests:
                        if test.enabled and rule.name in test.rules:
                            ab_variant = self.config_manager.get_ab_test_variant(
                                request.session_id, test.name
                            )
                            if ab_variant:
                                # Override rule based on A/B test
                                rule = await self._apply_ab_test_override(rule, test, ab_variant)
                            break

                # Get provider health data
                provider_health = await self.health_monitor.get_all_provider_health()

                # Route the request
                routing_result = await self.routing_engine.route_request(
                    rule, routing_context, provider_health
                )

                if not routing_result:
                    raise ValueError("No available providers for request")

                # Execute the request with selected provider
                response_data = await self._execute_with_provider(
                    request, routing_result, context_id
                )

                # Update context with response
                if context_id and response_data:
                    updated_context = request.context_data.copy()
                    updated_context.update({
                        "last_response": response_data,
                        "provider_used": routing_result.provider,
                        "timestamp": time.time()
                    })

                    await self.context_engine.preserve_context(
                        session_id=request.session_id,
                        context_data=updated_context,
                        context_type=ContextType.CONVERSATION
                    )

                # Build response
                latency_ms = (time.time() - start_time) * 1000
                response = OrchestrationResponse(
                    request_id=request.request_id,
                    session_id=request.session_id,
                    provider=routing_result.provider,
                    strategy_used=routing_result.strategy_used.value,
                    response=response_data.get("content", "") if response_data else "",
                    context_id=context_id,
                    latency_ms=latency_ms,
                    token_usage=response_data.get("usage", {}) if response_data else {},
                    routing_hops=[routing_result.provider],
                    ab_test_variant=ab_variant,
                    metadata={
                        "rule_name": rule.name,
                        "routing_reason": routing_result.reason,
                        "confidence": routing_result.confidence
                    }
                )

                # Record metrics
                orchestrator_requests_total.labels(
                    request_type=request.request_type.value,
                    success="true",
                    strategy=routing_result.strategy_used.value
                ).inc()

                orchestrator_latency_seconds.labels(
                    request_type=request.request_type.value
                ).observe(latency_ms / 1000)

                if ab_variant:
                    ab_test_traffic_ratio.labels(
                        experiment=test.name if 'test' in locals() else "unknown",
                        variant=ab_variant
                    ).set(1.0)

                # Emit completion event
                await bus_emit(
                    "orchestration.request.completed",
                    {
                        "request_id": request.request_id,
                        "session_id": request.session_id,
                        "provider": routing_result.provider,
                        "latency_ms": latency_ms,
                        "success": True
                    },
                    source="externalized_orchestrator",
                    mode="live"
                )

                span.set_attribute("provider_selected", routing_result.provider)
                span.set_attribute("strategy_used", routing_result.strategy_used.value)
                span.set_attribute("latency_ms", latency_ms)

                return response

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000

                # Record error metrics
                orchestrator_requests_total.labels(
                    request_type=request.request_type.value,
                    success="false",
                    strategy="error"
                ).inc()

                # Emit error event
                await bus_emit(
                    "orchestration.request.failed",
                    {
                        "request_id": request.request_id,
                        "session_id": request.session_id,
                        "error": str(e),
                        "latency_ms": latency_ms
                    },
                    source="externalized_orchestrator",
                    mode="live"
                )

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                logger.error(f"❌ Orchestration failed for {request.request_id}: {e}")
                raise

            finally:
                # Clean up active request
                if request.request_id in self.active_requests:
                    del self.active_requests[request.request_id]
                orchestrator_active_contexts.set(len(self.active_requests))

    async def _execute_with_provider(
        self,
        request: OrchestrationRequest,
        routing_result: RoutingResult,
        context_id: Optional[str]
    ) -> Dict[str, Any]:
        """Execute request with selected provider"""

        provider = routing_result.provider

        with tracer.start_span("orchestrator.execute_provider") as span:
            span.set_attribute("provider", provider)

            try:
                # Get provider client
                from .providers import AIProvider, create_provider_client

                provider_enum = AIProvider(provider)
                client = create_provider_client(provider_enum)

                # Prepare request
                prompt = request.prompt
                if request.system_prompt:
                    prompt = f"{request.system_prompt}\n\n{prompt}"

                # Execute request
                start_time = time.time()
                response = await client.generate(
                    prompt=prompt,
                    model=self._get_model_for_provider(provider),
                    max_tokens=request.metadata.get("max_tokens", 2000),
                    temperature=request.metadata.get("temperature", 0.7)
                )

                execution_time = time.time() - start_time

                # Update circuit breaker
                self.routing_engine.update_circuit_breaker(provider, True)

                # Hand off context if needed
                if context_id:
                    await self.context_engine.handoff_context(
                        context_id=context_id,
                        source_provider="orchestrator",
                        destination_provider=provider,
                        additional_metadata={
                            "execution_time_ms": execution_time * 1000,
                            "model_used": self._get_model_for_provider(provider)
                        }
                    )

                span.set_attribute("execution_time_ms", execution_time * 1000)
                span.set_attribute("response_length", len(response.content) if response.content else 0)

                return {
                    "content": response.content,
                    "usage": getattr(response, 'usage', {}),
                    "finish_reason": getattr(response, 'finish_reason', None),
                    "metadata": getattr(response, 'metadata', {})
                }

            except Exception as e:
                # Update circuit breaker for failure
                self.routing_engine.update_circuit_breaker(provider, False)

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                logger.error(f"❌ Provider execution failed for {provider}: {e}")
                raise

    def _determine_request_pattern(self, request: OrchestrationRequest) -> str:
        """Determine routing pattern from request"""

        # Check explicit routing hints
        if "pattern" in request.routing_hints:
            return request.routing_hints["pattern"]

        # Analyze prompt for patterns
        prompt_lower = request.prompt.lower()

        # Documentation patterns
        if any(word in prompt_lower for word in ["document", "architecture", "design", "review"]):
            return "documentation"

        # Code patterns
        if any(word in prompt_lower for word in ["code", "implement", "debug", "programming"]):
            return "code"

        # Analysis patterns
        if any(word in prompt_lower for word in ["analyze", "explain", "understand", "interpret"]):
            return "analysis"

        # Default pattern
        return "general"

    def _get_model_for_provider(self, provider: str) -> str:
        """Get appropriate model for provider"""
        model_map = {
            "openai": "gpt-4",
            "anthropic": "claude-3-sonnet-20240229",
            "google": "gemini-pro",
            "local": "llama2"
        }
        return model_map.get(provider, "default")

    async def _apply_ab_test_override(self, rule, test, variant):
        """Apply A/B test override to routing rule"""
        # Simple override - could be more sophisticated
        if variant in ["anthropic", "openai", "google"]:
            # Override primary provider
            overridden_rule = rule
            overridden_rule.providers = [variant] + [p for p in rule.providers if p != variant]

        return rule

    async def _register_event_handlers(self) -> None:
        """Register event handlers for orchestration events"""

        async def on_config_change(event_data):
            """Handle configuration changes"""
            logger.info(f"🔄 Configuration changed: {event_data}")
            await self._reinitialize_ab_tests()

        async def on_health_change(event_data):
            """Handle provider health changes"""
            logger.info(f"🏥 Provider health changed: {event_data}")

        # Subscribe to events
        self.kernel_bus.subscribe("orchestration.config.changed", on_config_change, mode="live")
        self.kernel_bus.subscribe("health.provider.status_changed", on_health_change, mode="live")

    async def _initialize_ab_tests(self) -> None:
        """Initialize A/B test state"""
        config = self.config_manager.get_configuration()

        for test in config.ab_tests:
            if test.enabled:
                self.ab_test_state[test.name] = {
                    "traffic_split": test.traffic_split,
                    "rules": test.rules,
                    "assignments": {}
                }

        logger.info(f"✅ Initialized {len(self.ab_test_state)} A/B tests")

    async def _reinitialize_ab_tests(self) -> None:
        """Reinitialize A/B test state after configuration change"""
        self.ab_test_state.clear()
        await self._initialize_ab_tests()

    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""

        health_summary = await self.health_monitor.get_health_summary()
        context_stats = await self.context_engine.get_preservation_stats()
        circuit_breaker_status = self.routing_engine.get_circuit_breaker_status()

        return {
            "active_requests": len(self.active_requests),
            "health_summary": health_summary,
            "context_stats": context_stats,
            "circuit_breaker_status": circuit_breaker_status,
            "ab_test_state": {
                name: {
                    "enabled": True,
                    "assignment_count": len(state["assignments"])
                }
                for name, state in self.ab_test_state.items()
            },
            "configuration_version": self.config_manager.config_version
        }


# Global orchestrator instance
_orchestrator: Optional[ExternalizedOrchestrator] = None


async def get_externalized_orchestrator() -> ExternalizedOrchestrator:
    """Get or create global externalized orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ExternalizedOrchestrator()
        await _orchestrator.initialize()
    return _orchestrator


async def orchestrate_request(request: OrchestrationRequest) -> OrchestrationResponse:
    """Convenience function for orchestrating requests"""
    orchestrator = await get_externalized_orchestrator()
    return await orchestrator.orchestrate(request)
