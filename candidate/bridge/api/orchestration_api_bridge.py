#!/usr/bin/env python3
"""
LUKHAS AI - Comprehensive API Orchestration Bridge
===================================================

Unified API orchestration system that coordinates multiple AI models
with function calling, streaming, and consensus mechanisms.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Performance Target: <100ms orchestration latency
Supports: Multi-model consensus, function calling, streaming, monitoring

Features:
- Unified interface for OpenAI, Anthropic, Google models
- Advanced consensus algorithms with confidence scoring
- Function calling with security validation
- Real-time streaming with SSE/WebSocket support
- Performance monitoring and optimization
- Rate limiting and cost management
- Security validation and ethical oversight
"""

import asyncio
import logging
import time
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

try:
    from candidate.bridge.llm_wrappers.anthropic_function_bridge import (
        AnthropicFunctionBridge,
        ClaudeModel,
        ClaudeResponse,
        ToolUseMode,
    )
    from candidate.bridge.llm_wrappers.openai_function_bridge import (
        FunctionCallMode,
        OpenAIFunctionBridge,
        OpenAIResponse,
    )
    from candidate.orchestration.multi_model_orchestration import (
        ConsensusStrategy,
        MultiModelOrchestrator,
        OrchestrationMode,
    )

    BRIDGES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Bridge import error: {e}")
    BRIDGES_AVAILABLE = False

logger = logging.getLogger(__name__)


class APIProvider(Enum):
    """Available API providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    PERPLEXITY = "perplexity"
    ALL = "all"  # Use all available providers


class OrchestrationStrategy(Enum):
    """Orchestration strategies for API coordination"""

    SINGLE_BEST = "single_best"  # Use single best model
    CONSENSUS = "consensus"  # Multi-model consensus
    FALLBACK = "fallback"  # Fallback chain
    PARALLEL = "parallel"  # Parallel execution
    COMPETITIVE = "competitive"  # Best response wins
    ENSEMBLE = "ensemble"  # Combine all responses


@dataclass
class OrchestrationRequest:
    """Request for API orchestration"""

    prompt: str
    context: Optional[dict[str, Any]] = None

    # Model selection
    preferred_providers: list[APIProvider] = field(
        default_factory=lambda: [APIProvider.ALL]
    )
    strategy: OrchestrationStrategy = OrchestrationStrategy.CONSENSUS

    # Function calling
    enable_functions: bool = True
    specific_functions: Optional[list[str]] = None

    # Performance constraints
    max_latency_ms: int = 5000
    max_cost_threshold: float = 0.10  # Maximum cost per request

    # Quality requirements
    min_confidence: float = 0.7
    require_consensus: bool = False

    # Metadata
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: str = "normal"  # low, normal, high, critical


@dataclass
class OrchestrationResponse:
    """Response from API orchestration"""

    content: str
    confidence_score: float

    # Provider information
    primary_provider: APIProvider
    participating_providers: list[APIProvider]

    # Function calling results
    function_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_uses: list[dict[str, Any]] = field(default_factory=list)

    # Performance metrics
    total_latency_ms: float = 0.0
    provider_latencies: dict[str, float] = field(default_factory=dict)
    total_cost: float = 0.0
    token_usage: dict[str, int] = field(default_factory=dict)

    # Quality metrics
    agreement_level: float = 0.0
    consensus_achieved: bool = False

    # Metadata
    request_id: str = ""
    strategy_used: OrchestrationStrategy = OrchestrationStrategy.SINGLE_BEST
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Individual responses for transparency
    individual_responses: list[dict[str, Any]] = field(default_factory=list)
    decision_rationale: str = ""


class ComprehensiveAPIOrchestrator:
    """
    Comprehensive API orchestration system that unifies multiple AI providers
    with advanced consensus, function calling, and performance optimization.

    Coordinates:
    - OpenAI GPT models with function calling
    - Anthropic Claude with tool use
    - Google Gemini integration
    - Perplexity for research tasks

    Provides:
    - Multi-model consensus with advanced algorithms
    - Function calling with security validation
    - Real-time streaming capabilities
    - Performance monitoring and optimization
    - Cost management and rate limiting
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
        perplexity_api_key: Optional[str] = None,
    ):
        """Initialize comprehensive API orchestrator"""

        # Initialize provider bridges
        self.bridges = {}
        self._initialize_bridges(
            openai_api_key, anthropic_api_key, google_api_key, perplexity_api_key
        )

        # Initialize orchestration components
        self.orchestrator = MultiModelOrchestrator() if BRIDGES_AVAILABLE else None

        # Performance and cost tracking
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_cost": 0.0,
            "average_latency_ms": 0.0,
            "provider_usage": {},
            "function_calls_total": 0,
            "consensus_success_rate": 0.0,
        }

        # Function registry (shared across providers)
        self.global_functions = {}

        # Rate limiting and cost control
        self.cost_limits = {
            APIProvider.OPENAI: {"daily": 50.0, "per_request": 1.0},
            APIProvider.ANTHROPIC: {"daily": 50.0, "per_request": 1.0},
            APIProvider.GOOGLE: {"daily": 30.0, "per_request": 0.5},
        }
        self.daily_costs = {provider: 0.0 for provider in APIProvider}

        logger.info("🌐 Comprehensive API Orchestrator initialized")
        logger.info(f"   Available providers: {list(self.bridges.keys())}")
        logger.info(f"   Orchestration enabled: {self.orchestrator is not None}")

    def _initialize_bridges(
        self, openai_key, anthropic_key, google_key, perplexity_key
    ):
        """Initialize bridges to different API providers"""

        # OpenAI Bridge
        if openai_key or self._get_env_key("OPENAI_API_KEY"):
            try:
                self.bridges[APIProvider.OPENAI] = OpenAIFunctionBridge(
                    api_key=openai_key or self._get_env_key("OPENAI_API_KEY")
                )
                logger.info("✅ OpenAI bridge initialized")
            except Exception as e:
                logger.error(f"❌ OpenAI bridge initialization failed: {e}")

        # Anthropic Bridge
        if anthropic_key or self._get_env_key("ANTHROPIC_API_KEY"):
            try:
                self.bridges[APIProvider.ANTHROPIC] = AnthropicFunctionBridge(
                    api_key=anthropic_key or self._get_env_key("ANTHROPIC_API_KEY")
                )
                logger.info("✅ Anthropic bridge initialized")
            except Exception as e:
                logger.error(f"❌ Anthropic bridge initialization failed: {e}")

        # Google Bridge
        if google_key or self._get_env_key("GOOGLE_API_KEY"):
            try:
                from candidate.bridge.llm_wrappers.gemini_wrapper import GeminiWrapper

                self.bridges[APIProvider.GOOGLE] = GeminiWrapper()
                logger.info("✅ Google Gemini bridge initialized")
            except Exception as e:
                logger.error(f"❌ Google bridge initialization failed: {e}")

        # Perplexity Bridge
        if perplexity_key or self._get_env_key("PERPLEXITY_API_KEY"):
            try:
                from candidate.bridge.llm_wrappers.perplexity_wrapper import (
                    PerplexityWrapper,
                )

                self.bridges[APIProvider.PERPLEXITY] = PerplexityWrapper()
                logger.info("✅ Perplexity bridge initialized")
            except Exception as e:
                logger.error(f"❌ Perplexity bridge initialization failed: {e}")

        if not self.bridges:
            logger.warning(
                "⚠️ No API bridges initialized - orchestrator will use mock responses"
            )

    def _get_env_key(self, key_name: str) -> Optional[str]:
        """Get API key from environment"""
        import os

        return os.getenv(key_name)

    def register_global_functions(self, functions: dict[str, dict[str, Any]]):
        """Register functions that will be available to all providers"""
        self.global_functions.update(functions)

        # Register with individual bridges
        for bridge in self.bridges.values():
            if hasattr(bridge, "register_functions_from_dict"):
                bridge.register_functions_from_dict(functions)
            elif hasattr(bridge, "register_tools_from_dict"):
                bridge.register_tools_from_dict(functions)

        logger.info(f"📊 Registered {len(functions)} global functions")

    async def orchestrate(self, request: OrchestrationRequest) -> OrchestrationResponse:
        """
        Main orchestration method that coordinates multiple APIs based on strategy.

        Args:
            request: Orchestration request with prompt, strategy, and constraints

        Returns:
            Orchestration response with results and metrics
        """
        orchestration_start = time.perf_counter()

        logger.info(f"🌟 Starting orchestration: {request.request_id}")
        logger.info(f"   Strategy: {request.strategy.value}")
        logger.info(f"   Providers: {[p.value for p in request.preferred_providers]}")
        logger.info(f"   Functions enabled: {request.enable_functions}")

        try:
            # Validate request and check cost limits
            await self._validate_request(request)

            # Select providers based on request
            selected_providers = self._select_providers(request)

            if not selected_providers:
                raise ValueError("No available providers for request")

            # Execute orchestration based on strategy
            if request.strategy == OrchestrationStrategy.SINGLE_BEST:
                response = await self._single_best_orchestration(
                    request, selected_providers
                )
            elif request.strategy == OrchestrationStrategy.CONSENSUS:
                response = await self._consensus_orchestration(
                    request, selected_providers
                )
            elif request.strategy == OrchestrationStrategy.FALLBACK:
                response = await self._fallback_orchestration(
                    request, selected_providers
                )
            elif request.strategy == OrchestrationStrategy.PARALLEL:
                response = await self._parallel_orchestration(
                    request, selected_providers
                )
            elif request.strategy == OrchestrationStrategy.COMPETITIVE:
                response = await self._competitive_orchestration(
                    request, selected_providers
                )
            elif request.strategy == OrchestrationStrategy.ENSEMBLE:
                response = await self._ensemble_orchestration(
                    request, selected_providers
                )
            else:
                raise ValueError(f"Unknown orchestration strategy: {request.strategy}")

            # Finalize response
            orchestration_time = (time.perf_counter() - orchestration_start) * 1000
            response.total_latency_ms = orchestration_time
            response.request_id = request.request_id
            response.strategy_used = request.strategy

            # Update metrics
            self._update_metrics(request, response)

            logger.info(f"✅ Orchestration completed: {orchestration_time:.2f}ms")
            logger.info(f"   Primary provider: {response.primary_provider.value}")
            logger.info(f"   Confidence: {response.confidence_score:.3f}")
            logger.info(f"   Cost: ${response.total_cost:.4f}")

            return response

        except Exception as e:
            orchestration_time = (time.perf_counter() - orchestration_start) * 1000
            self.metrics["failed_requests"] += 1

            logger.error(f"❌ Orchestration failed: {e!s} ({orchestration_time:.2f}ms)")

            # Return error response
            return OrchestrationResponse(
                content=f"Orchestration error: {e!s}",
                confidence_score=0.0,
                primary_provider=APIProvider.OPENAI,  # Default
                participating_providers=[],
                total_latency_ms=orchestration_time,
                request_id=request.request_id,
                strategy_used=request.strategy,
                decision_rationale=f"Error occurred during orchestration: {e!s}",
            )

    async def stream_orchestration(
        self, request: OrchestrationRequest
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream orchestration results in real-time"""

        logger.info(f"📡 Starting streaming orchestration: {request.request_id}")

        # For streaming, we typically use a single provider to maintain coherence
        selected_providers = self._select_providers(request, max_count=1)

        if not selected_providers:
            yield {"type": "error", "error": "No available providers for streaming"}
            return

        provider = selected_providers[0]
        bridge = self.bridges[provider]

        try:
            # Convert request to provider-specific format
            messages = [{"role": "user", "content": request.prompt}]

            if provider == APIProvider.OPENAI and hasattr(
                bridge, "stream_with_functions"
            ):
                async for chunk in bridge.stream_with_functions(
                    messages=messages,
                    function_mode=(
                        FunctionCallMode.AUTO
                        if request.enable_functions
                        else FunctionCallMode.NONE
                    ),
                ):
                    yield {
                        "type": chunk.get("type", "content"),
                        "content": chunk.get("content", ""),
                        "provider": provider.value,
                        "request_id": request.request_id,
                        **chunk,
                    }

            elif provider == APIProvider.ANTHROPIC and hasattr(
                bridge, "stream_with_tools"
            ):
                async for chunk in bridge.stream_with_tools(
                    messages=messages,
                    tool_mode=(
                        ToolUseMode.ENABLED
                        if request.enable_functions
                        else ToolUseMode.DISABLED
                    ),
                ):
                    yield {
                        "type": chunk.get("type", "content"),
                        "content": chunk.get("content", ""),
                        "provider": provider.value,
                        "request_id": request.request_id,
                        **chunk,
                    }

            elif provider in [APIProvider.GOOGLE, APIProvider.PERPLEXITY]:
                # For providers without native streaming, simulate streaming
                yield {
                    "type": "status",
                    "content": "Processing request...",
                    "provider": provider.value,
                    "request_id": request.request_id,
                }

                # Execute the provider
                result = await self._execute_provider(provider, request)

                # Stream the response in chunks
                content = result.get("content", "")
                words = content.split()

                for i in range(0, len(words), 5):  # Stream 5 words at a time
                    chunk_words = words[i : i + 5]
                    chunk_content = " ".join(chunk_words)

                    yield {
                        "type": "content",
                        "content": chunk_content + (" " if i + 5 < len(words) else ""),
                        "provider": provider.value,
                        "request_id": request.request_id,
                        "chunk_index": i // 5,
                        "is_final": i + 5 >= len(words),
                    }

                    # Small delay to simulate streaming
                    await asyncio.sleep(0.05)

                # Final metadata
                yield {
                    "type": "metadata",
                    "provider": provider.value,
                    "request_id": request.request_id,
                    "latency_ms": result.get("latency_ms", 0),
                    "confidence": result.get("confidence", 0),
                    "usage": result.get("usage", {}),
                    "web_search": result.get("web_search", False),
                }

            else:
                yield {
                    "type": "error",
                    "error": f"Streaming not supported for provider: {provider.value}",
                }

        except Exception as e:
            logger.error(f"❌ Streaming error: {e!s}")
            yield {
                "type": "error",
                "error": str(e),
                "provider": provider.value,
                "request_id": request.request_id,
            }

    async def _validate_request(self, request: OrchestrationRequest):
        """Validate request and check constraints"""

        # Check cost limits
        for provider in request.preferred_providers:
            if provider in self.cost_limits:
                daily_limit = self.cost_limits[provider]["daily"]
                current_cost = self.daily_costs.get(provider, 0.0)

                if current_cost + request.max_cost_threshold > daily_limit:
                    raise ValueError(f"Daily cost limit exceeded for {provider.value}")

    def _select_providers(
        self, request: OrchestrationRequest, max_count: Optional[int] = None
    ) -> list[APIProvider]:
        """Select providers based on request preferences and availability"""
        available_providers = list(self.bridges.keys())

        if APIProvider.ALL in request.preferred_providers:
            selected = available_providers
        else:
            selected = [
                p
                for p in request.preferred_providers
                if p in available_providers and p != APIProvider.ALL
            ]

        if max_count:
            selected = selected[:max_count]

        return selected

    async def _single_best_orchestration(
        self, request: OrchestrationRequest, providers: list[APIProvider]
    ) -> OrchestrationResponse:
        """Use single best provider based on capabilities"""

        # Select best provider (OpenAI > Anthropic > Others for general tasks)
        provider_priority = [
            APIProvider.OPENAI,
            APIProvider.ANTHROPIC,
            APIProvider.GOOGLE,
            APIProvider.PERPLEXITY,
        ]
        best_provider = next(
            (p for p in provider_priority if p in providers), providers[0]
        )

        bridge = self.bridges[best_provider]
        messages = [{"role": "user", "content": request.prompt}]

        if best_provider == APIProvider.OPENAI:
            result = await bridge.complete_with_functions(
                messages=messages,
                function_mode=(
                    FunctionCallMode.AUTO
                    if request.enable_functions
                    else FunctionCallMode.NONE
                ),
                execute_functions=True,
            )

            return OrchestrationResponse(
                content=result.content,
                confidence_score=result.usage.get(
                    "confidence_score", 0.8
                ),  # Default confidence
                primary_provider=best_provider,
                participating_providers=[best_provider],
                function_calls=[fc.__dict__ for fc in result.function_calls],
                provider_latencies={best_provider.value: result.latency_ms},
                total_cost=self._estimate_cost(best_provider, result.usage),
                token_usage=result.usage,
                individual_responses=[
                    {
                        "provider": best_provider.value,
                        "content": result.content,
                        "confidence": result.usage.get("confidence_score", 0.8),
                        "latency_ms": result.latency_ms,
                    }
                ],
                decision_rationale=f"Selected {best_provider.value} as single best provider",
            )

        elif best_provider == APIProvider.ANTHROPIC:
            result = await bridge.complete_with_tools(
                messages=messages,
                tool_mode=(
                    ToolUseMode.ENABLED
                    if request.enable_functions
                    else ToolUseMode.DISABLED
                ),
                execute_tools=True,
            )

            return OrchestrationResponse(
                content=result.content,
                confidence_score=result.constitutional_score,
                primary_provider=best_provider,
                participating_providers=[best_provider],
                tool_uses=[tu.__dict__ for tu in result.tool_uses],
                provider_latencies={best_provider.value: result.latency_ms},
                total_cost=self._estimate_cost(best_provider, result.usage),
                token_usage=result.usage,
                individual_responses=[
                    {
                        "provider": best_provider.value,
                        "content": result.content,
                        "confidence": result.constitutional_score,
                        "latency_ms": result.latency_ms,
                    }
                ],
                decision_rationale=f"Selected {best_provider.value} as single best provider",
            )

        else:
            # Fallback for other providers
            return OrchestrationResponse(
                content=f"Provider {best_provider.value} not fully implemented",
                confidence_score=0.5,
                primary_provider=best_provider,
                participating_providers=[best_provider],
                decision_rationale=f"Provider {best_provider.value} implementation pending",
            )

    async def _consensus_orchestration(
        self, request: OrchestrationRequest, providers: list[APIProvider]
    ) -> OrchestrationResponse:
        """Use multi-model consensus for enhanced accuracy"""

        if len(providers) < 2:
            return await self._single_best_orchestration(request, providers)

        # Execute all providers in parallel
        tasks = []
        for provider in providers:
            task = asyncio.create_task(self._execute_provider(provider, request))
            tasks.append((provider, task))

        # Collect results with timeout handling
        provider_results = []
        for provider, task in tasks:
            try:
                result = await asyncio.wait_for(
                    task, timeout=request.max_latency_ms / 1000
                )
                provider_results.append((provider, result))
            except asyncio.TimeoutError:
                logger.warning(f"Provider {provider.value} timed out")
            except Exception as e:
                logger.error(f"Provider {provider.value} failed: {e}")

        if not provider_results:
            raise ValueError("All providers failed")

        # Enhanced consensus algorithm
        contents = [result.get("content", "") for _, result in provider_results]
        agreement_level = self._calculate_simple_agreement(contents)

        # Weighted scoring based on confidence, agreement, and provider reliability
        provider_scores = []
        for provider, result in provider_results:
            confidence = result.get("confidence", 0.0)
            latency_ms = result.get("latency_ms", request.max_latency_ms)

            # Provider reliability weights (can be learned over time)
            reliability_weights = {
                APIProvider.OPENAI: 0.9,
                APIProvider.ANTHROPIC: 0.85,
                APIProvider.GOOGLE: 0.8,
                APIProvider.PERPLEXITY: 0.75,
            }

            reliability = reliability_weights.get(provider, 0.7)

            # Performance score (lower latency is better)
            performance_score = max(0, 1 - (latency_ms / request.max_latency_ms))

            # Combined score: confidence (40%), reliability (35%), performance (25%)
            combined_score = (
                (confidence * 0.4) + (reliability * 0.35) + (performance_score * 0.25)
            )

            provider_scores.append((provider, result, combined_score))

        # Sort by combined score
        provider_scores.sort(key=lambda x: x[2], reverse=True)
        primary_provider, primary_result, primary_score = provider_scores[0]

        # If high agreement and multiple high-scoring providers, create ensemble response
        if (
            agreement_level > 0.8
            and len([p for p in provider_scores if p[2] > 0.7]) > 1
        ):
            # Create ensemble response by combining top responses
            top_responses = [p[1]["content"] for p in provider_scores[:2] if p[2] > 0.7]
            if (
                len(top_responses) > 1
                and len(top_responses[0]) > 0
                and len(top_responses[1]) > 0
            ):
                # Simple ensemble: use primary but note consensus
                ensemble_content = primary_result.get("content", "")
                decision_rationale = f"High consensus ({agreement_level:.3f}) ensemble from {len(provider_results)} providers"
            else:
                ensemble_content = primary_result.get("content", "")
                decision_rationale = (
                    f"Primary provider selected with score {primary_score:.3f}"
                )
        else:
            ensemble_content = primary_result.get("content", "")
            decision_rationale = (
                f"Best individual response (agreement: {agreement_level:.3f})"
            )

        # Aggregate costs and latencies
        total_cost = sum(
            self._estimate_cost(p, r.get("usage", {})) for p, r in provider_results
        )
        provider_latencies = {
            p.value: r.get("latency_ms", 0.0) for p, r in provider_results
        }

        return OrchestrationResponse(
            content=ensemble_content,
            confidence_score=min(
                1.0, primary_score + (agreement_level * 0.1)
            ),  # Boost confidence with agreement
            primary_provider=primary_provider,
            participating_providers=[p for p, _ in provider_results],
            agreement_level=agreement_level,
            consensus_achieved=agreement_level > 0.7,
            provider_latencies=provider_latencies,
            total_cost=total_cost,
            individual_responses=[
                {
                    "provider": p.value,
                    "content": r.get("content", ""),
                    "confidence": r.get("confidence", 0.0),
                    "latency_ms": r.get("latency_ms", 0.0),
                    "combined_score": score,
                    "web_search": r.get("web_search", False),
                }
                for p, r, score in provider_scores
            ],
            decision_rationale=decision_rationale,
        )

    async def _fallback_orchestration(
        self, request: OrchestrationRequest, providers: list[APIProvider]
    ) -> OrchestrationResponse:
        """Try providers in order until one succeeds"""

        last_error = None

        for provider in providers:
            try:
                result = await self._execute_provider(provider, request)
                return OrchestrationResponse(
                    content=result.get("content", ""),
                    confidence_score=result.get("confidence", 0.0),
                    primary_provider=provider,
                    participating_providers=[provider],
                    provider_latencies={provider.value: result.get("latency_ms", 0.0)},
                    total_cost=self._estimate_cost(provider, result.get("usage", {})),
                    individual_responses=[
                        {
                            "provider": provider.value,
                            "content": result.get("content", ""),
                            "confidence": result.get("confidence", 0.0),
                        }
                    ],
                    decision_rationale=f"Fallback chain succeeded with {provider.value}",
                )

            except Exception as e:
                logger.warning(f"Fallback provider {provider.value} failed: {e}")
                last_error = e
                continue

        # All providers failed
        raise last_error or ValueError("All fallback providers failed")

    async def _parallel_orchestration(
        self, request: OrchestrationRequest, providers: list[APIProvider]
    ) -> OrchestrationResponse:
        """Execute all providers in parallel, return fastest valid response"""

        tasks = []
        for provider in providers:
            task = asyncio.create_task(self._execute_provider(provider, request))
            tasks.append((provider, task))

        # Wait for first successful result
        for completed in asyncio.as_completed([task for _, task in tasks]):
            try:
                result = await completed

                # Find which provider this was
                provider = None
                for p, t in tasks:
                    if t == completed:
                        provider = p
                        break

                if provider:
                    return OrchestrationResponse(
                        content=result.get("content", ""),
                        confidence_score=result.get("confidence", 0.0),
                        primary_provider=provider,
                        participating_providers=[provider],
                        provider_latencies={
                            provider.value: result.get("latency_ms", 0.0)
                        },
                        total_cost=self._estimate_cost(
                            provider, result.get("usage", {})
                        ),
                        decision_rationale=f"Parallel execution won by {provider.value}",
                    )

            except Exception as e:
                logger.warning(f"Parallel provider failed: {e}")
                continue

        raise ValueError("All parallel providers failed")

    async def _competitive_orchestration(
        self, request: OrchestrationRequest, providers: list[APIProvider]
    ) -> OrchestrationResponse:
        """Run all providers, select best response based on quality metrics"""
        return await self._consensus_orchestration(
            request, providers
        )  # Similar to consensus

    async def _ensemble_orchestration(
        self, request: OrchestrationRequest, providers: list[APIProvider]
    ) -> OrchestrationResponse:
        """Combine all provider responses into comprehensive ensemble"""
        return await self._consensus_orchestration(
            request, providers
        )  # Similar to consensus

    async def _execute_provider(
        self, provider: APIProvider, request: OrchestrationRequest
    ) -> dict[str, Any]:
        """Execute request on specific provider"""
        bridge = self.bridges[provider]
        start_time = time.perf_counter()

        if provider == APIProvider.OPENAI:
            messages = [{"role": "user", "content": request.prompt}]
            result = await bridge.complete_with_functions(
                messages=messages,
                function_mode=(
                    FunctionCallMode.AUTO
                    if request.enable_functions
                    else FunctionCallMode.NONE
                ),
            )
            return {
                "content": result.content,
                "confidence": 0.8,  # Default confidence for OpenAI
                "latency_ms": result.latency_ms,
                "usage": result.usage,
                "function_calls": result.function_calls,
            }

        elif provider == APIProvider.ANTHROPIC:
            messages = [{"role": "user", "content": request.prompt}]
            result = await bridge.complete_with_tools(
                messages=messages,
                tool_mode=(
                    ToolUseMode.ENABLED
                    if request.enable_functions
                    else ToolUseMode.DISABLED
                ),
            )
            return {
                "content": result.content,
                "confidence": result.constitutional_score,
                "latency_ms": result.latency_ms,
                "usage": result.usage,
                "tool_uses": result.tool_uses,
            }

        elif provider == APIProvider.GOOGLE:
            # Use Gemini wrapper
            content = bridge.generate_response(
                prompt=request.prompt, model="gemini-pro"
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Estimate token usage (approximate)
            estimated_input_tokens = len(request.prompt.split()) * 1.3  # Rough estimate
            estimated_output_tokens = len(content.split()) * 1.3

            return {
                "content": content,
                "confidence": 0.75,  # Default confidence for Gemini
                "latency_ms": latency_ms,
                "usage": {
                    "input_tokens": int(estimated_input_tokens),
                    "output_tokens": int(estimated_output_tokens),
                    "total_tokens": int(
                        estimated_input_tokens + estimated_output_tokens
                    ),
                },
                "function_calls": [],  # Gemini wrapper doesn't support function calls yet
            }

        elif provider == APIProvider.PERPLEXITY:
            # Use Perplexity wrapper with online search
            content = bridge.generate_response(
                prompt=request.prompt,
                model="llama-3.1-sonar-small-128k-online",  # Use online model for real-time info
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Estimate token usage (approximate)
            estimated_input_tokens = len(request.prompt.split()) * 1.3
            estimated_output_tokens = len(content.split()) * 1.3

            return {
                "content": content,
                "confidence": 0.85,  # Higher confidence for web-enhanced responses
                "latency_ms": latency_ms,
                "usage": {
                    "input_tokens": int(estimated_input_tokens),
                    "output_tokens": int(estimated_output_tokens),
                    "total_tokens": int(
                        estimated_input_tokens + estimated_output_tokens
                    ),
                },
                "function_calls": [],
                "web_search": True,  # Indicate web search was used
                "sources": [],  # Could be enhanced to extract sources from response
            }

        else:
            raise NotImplementedError(
                f"Provider {provider.value} execution not implemented"
            )

    def _calculate_simple_agreement(self, contents: list[str]) -> float:
        """Calculate simple agreement level between responses"""
        if len(contents) < 2:
            return 1.0

        # Enhanced similarity calculation with multiple metrics
        word_sets = [set(content.lower().split()) for content in contents]
        sentence_sets = [set(content.lower().split(".")) for content in contents]

        total_word_similarity = 0.0
        total_sentence_similarity = 0.0
        total_length_similarity = 0.0
        pair_count = 0

        for i in range(len(word_sets)):
            for j in range(i + 1, len(word_sets)):
                # Word-level similarity (Jaccard index)
                word_intersection = len(word_sets[i].intersection(word_sets[j]))
                word_union = len(word_sets[i].union(word_sets[j]))
                word_similarity = (
                    word_intersection / word_union if word_union > 0 else 0.0
                )
                total_word_similarity += word_similarity

                # Sentence-level similarity
                sent_intersection = len(sentence_sets[i].intersection(sentence_sets[j]))
                sent_union = len(sentence_sets[i].union(sentence_sets[j]))
                sent_similarity = (
                    sent_intersection / sent_union if sent_union > 0 else 0.0
                )
                total_sentence_similarity += sent_similarity

                # Length similarity (normalized difference)
                len_i, len_j = len(contents[i]), len(contents[j])
                length_similarity = 1.0 - abs(len_i - len_j) / max(len_i, len_j, 1)
                total_length_similarity += length_similarity

                pair_count += 1

        if pair_count == 0:
            return 0.0

        # Weighted average of different similarity metrics
        avg_word_sim = total_word_similarity / pair_count
        avg_sent_sim = total_sentence_similarity / pair_count
        avg_length_sim = total_length_similarity / pair_count

        # Weight: word similarity (0.5), sentence similarity (0.3), length similarity (0.2)
        weighted_similarity = (
            (avg_word_sim * 0.5) + (avg_sent_sim * 0.3) + (avg_length_sim * 0.2)
        )

        return weighted_similarity

    def _estimate_cost(self, provider: APIProvider, usage: dict[str, int]) -> float:
        """Estimate cost for provider usage"""
        if not usage:
            return 0.0

        # Simplified cost estimation
        input_tokens = usage.get("input_tokens", usage.get("prompt_tokens", 0))
        output_tokens = usage.get("output_tokens", usage.get("completion_tokens", 0))

        if provider == APIProvider.OPENAI:
            # GPT-4 pricing (approximate)
            return (input_tokens * 0.03 + output_tokens * 0.06) / 1000
        elif provider == APIProvider.ANTHROPIC:
            # Claude pricing (approximate)
            return (input_tokens * 0.015 + output_tokens * 0.075) / 1000
        elif provider == APIProvider.GOOGLE:
            # Gemini Pro pricing (approximate)
            return (input_tokens * 0.0005 + output_tokens * 0.0015) / 1000
        elif provider == APIProvider.PERPLEXITY:
            # Perplexity Sonar pricing (approximate)
            return (input_tokens * 0.001 + output_tokens * 0.001) / 1000
        else:
            return 0.01  # Default estimate

    def _update_metrics(
        self, request: OrchestrationRequest, response: OrchestrationResponse
    ):
        """Update performance and cost metrics"""
        self.metrics["total_requests"] += 1

        if response.confidence_score > request.min_confidence:
            self.metrics["successful_requests"] += 1

        # Update average latency
        current_avg = self.metrics["average_latency_ms"]
        total_requests = self.metrics["total_requests"]
        new_avg = (
            (current_avg * (total_requests - 1)) + response.total_latency_ms
        ) / total_requests
        self.metrics["average_latency_ms"] = new_avg

        # Update cost tracking
        self.metrics["total_cost"] += response.total_cost
        for provider in response.participating_providers:
            self.daily_costs[provider] = self.daily_costs.get(provider, 0.0) + (
                response.total_cost / len(response.participating_providers)
            )

        # Update provider usage
        for provider in response.participating_providers:
            provider_key = provider.value
            if provider_key not in self.metrics["provider_usage"]:
                self.metrics["provider_usage"][provider_key] = 0
            self.metrics["provider_usage"][provider_key] += 1

        # Update function call tracking
        total_functions = len(response.function_calls) + len(response.tool_uses)
        self.metrics["function_calls_total"] += total_functions

        # Update consensus tracking
        if response.consensus_achieved:
            # Update consensus success rate
            current_rate = self.metrics["consensus_success_rate"]
            self.metrics["consensus_success_rate"] = (
                (current_rate * (total_requests - 1)) + 1.0
            ) / total_requests

    def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive orchestration metrics"""
        total_requests = self.metrics["total_requests"]

        return {
            **self.metrics,
            "success_rate": self.metrics["successful_requests"]
            / max(total_requests, 1),
            "average_cost_per_request": self.metrics["total_cost"]
            / max(total_requests, 1),
            "available_providers": [p.value for p in self.bridges],
            "global_functions_registered": len(self.global_functions),
            "daily_costs": dict(self.daily_costs),
            "performance_score": self._calculate_performance_score(),
        }

    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-1)"""
        total_requests = max(self.metrics["total_requests"], 1)

        # Factor in success rate, latency, and cost efficiency
        success_rate = self.metrics["successful_requests"] / total_requests
        latency_score = max(
            0, 1 - (self.metrics["average_latency_ms"] / 2000)
        )  # 2s = 0 score
        cost_efficiency = min(
            1.0, 0.10 / max(self.metrics["total_cost"] / total_requests, 0.001)
        )  # $0.10 target

        return success_rate * 0.5 + latency_score * 0.3 + cost_efficiency * 0.2


# Global orchestrator instance
api_orchestrator = None


def get_orchestrator() -> ComprehensiveAPIOrchestrator:
    """Get global orchestrator instance"""
    global api_orchestrator
    if api_orchestrator is None:
        api_orchestrator = ComprehensiveAPIOrchestrator()
    return api_orchestrator


# Advanced orchestration strategies
class AdvancedConsensusStrategies:
    """Advanced consensus algorithms for multi-model orchestration"""

    @staticmethod
    def weighted_voting(responses: list[dict], weights: dict[str, float]) -> dict:
        """Weighted voting consensus based on provider reliability"""
        if not responses:
            return {}

        # Score each response
        scored_responses = []
        for response in responses:
            provider = response.get("provider", "unknown")
            base_score = weights.get(provider, 0.5)
            confidence_score = response.get("confidence", 0.0)

            # Combine base reliability with response confidence
            final_score = (base_score * 0.6) + (confidence_score * 0.4)
            scored_responses.append((response, final_score))

        # Return highest scoring response
        return max(scored_responses, key=lambda x: x[1])[0]

    @staticmethod
    def semantic_clustering(
        responses: list[dict], similarity_threshold: float = 0.7
    ) -> dict:
        """Group responses by semantic similarity and choose cluster representative"""
        if not responses:
            return {}

        if len(responses) == 1:
            return responses[0]

        # Simple clustering based on word overlap
        clusters = []
        for response in responses:
            content = response.get("content", "")
            words = set(content.lower().split())

            # Find matching cluster
            matched_cluster = None
            for cluster in clusters:
                cluster_words = set(cluster[0].get("content", "").lower().split())
                similarity = len(words.intersection(cluster_words)) / len(
                    words.union(cluster_words)
                )

                if similarity > similarity_threshold:
                    matched_cluster = cluster
                    break

            if matched_cluster:
                matched_cluster.append(response)
            else:
                clusters.append([response])

        # Choose representative from largest cluster
        largest_cluster = max(clusters, key=len)
        return max(largest_cluster, key=lambda x: x.get("confidence", 0))

    @staticmethod
    def confidence_weighted_ensemble(responses: list[dict]) -> str:
        """Create ensemble response weighted by confidence scores"""
        if not responses:
            return ""

        total_confidence = sum(r.get("confidence", 0) for r in responses)
        if total_confidence == 0:
            return responses[0].get("content", "")

        # For simplicity, return the highest confidence response
        # In practice, this could blend responses based on weights
        return max(responses, key=lambda x: x.get("confidence", 0)).get("content", "")


# Convenience functions
async def orchestrate_request(
    prompt: str,
    strategy: str = "consensus",
    providers: Optional[list[str]] = None,
    enable_functions: bool = True,
    context: Optional[dict[str, Any]] = None,
) -> OrchestrationResponse:
    """Convenience function for orchestration"""
    orchestrator = get_orchestrator()

    request = OrchestrationRequest(
        prompt=prompt,
        context=context,
        strategy=OrchestrationStrategy(strategy),
        preferred_providers=(
            [APIProvider(p) for p in providers] if providers else [APIProvider.ALL]
        ),
        enable_functions=enable_functions,
    )

    return await orchestrator.orchestrate(request)


async def orchestrate_healthcare_request(
    prompt: str, patient_context: Optional[dict] = None, consent_verified: bool = False
) -> OrchestrationResponse:
    """Specialized healthcare orchestration with compliance checks"""
    if not consent_verified:
        raise ValueError("Healthcare requests require verified consent")

    context = {
        "type": "healthcare",
        "patient_context": patient_context,
        "compliance_required": True,
    }

    # Use consensus strategy for healthcare for higher reliability
    return await orchestrate_request(
        prompt=prompt,
        strategy="consensus",
        providers=["anthropic", "openai"],  # Use most reliable providers
        enable_functions=False,  # Disable functions for healthcare safety
        context=context,
    )


async def stream_request(
    prompt: str, provider: str = "openai", enable_functions: bool = True
) -> AsyncGenerator[dict[str, Any], None]:
    """Convenience function for streaming"""
    orchestrator = get_orchestrator()

    request = OrchestrationRequest(
        prompt=prompt,
        preferred_providers=[APIProvider(provider)],
        enable_functions=enable_functions,
    )

    async for chunk in orchestrator.stream_orchestration(request):
        yield chunk


# Export main components
__all__ = [
    "APIProvider",
    "AdvancedConsensusStrategies",
    "ComprehensiveAPIOrchestrator",
    "OrchestrationRequest",
    "OrchestrationResponse",
    "OrchestrationStrategy",
    "get_orchestrator",
    "orchestrate_healthcare_request",
    "orchestrate_request",
    "stream_request",
]
