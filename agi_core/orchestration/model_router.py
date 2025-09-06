"""
Multi-Model Router for AGI Orchestration

Routes requests to the most appropriate AI model based on task type,
performance requirements, cost constraints, and capability matching.
Integrates with LUKHAS consciousness and dream systems.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# Try to import existing model wrappers
try:
    from lukhas.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
    from lukhas.bridge.llm_wrappers.unified_openai_client import UnifiedOpenAIClient

    LUKHAS_WRAPPERS_AVAILABLE = True
except ImportError:
    LUKHAS_WRAPPERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported AI model types"""

    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_HAIKU = "claude-3-5-haiku-20241022"
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"


class TaskType(Enum):
    """Types of tasks for model selection"""

    REASONING = "reasoning"
    CODE_GENERATION = "code_generation"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    CONVERSATION = "conversation"
    MATH = "math"
    RESEARCH = "research"
    DREAM_SYNTHESIS = "dream_synthesis"


class PerformanceRequirement(Enum):
    """Performance requirement levels"""

    FAST = "fast"  # <1s response time
    BALANCED = "balanced"  # <5s response time
    THOROUGH = "thorough"  # <30s response time
    DEEP = "deep"  # >30s acceptable


@dataclass
class ModelCapability:
    """Capabilities of a specific model"""

    model_type: ModelType
    reasoning_score: float  # 0-1 reasoning capability
    creativity_score: float  # 0-1 creativity capability
    code_score: float  # 0-1 coding capability
    analysis_score: float  # 0-1 analysis capability
    speed_score: float  # 0-1 speed score
    cost_efficiency: float  # 0-1 cost efficiency
    context_length: int  # Maximum context tokens
    supports_function_calls: bool = False
    supports_vision: bool = False
    supports_code_execution: bool = False


@dataclass
class RoutingRequest:
    """Request for model routing"""

    task_type: TaskType
    content: str
    context: Optional[dict[str, Any]] = None
    performance_requirement: PerformanceRequirement = PerformanceRequirement.BALANCED
    max_cost: Optional[float] = None
    preferred_models: Optional[list[ModelType]] = None
    require_consensus: bool = False
    dream_enhanced: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ModelResponse:
    """Response from a model"""

    model_type: ModelType
    content: str
    confidence: float
    processing_time_ms: float
    tokens_used: int
    cost_estimate: float
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RoutingDecision:
    """Decision made by the router"""

    selected_model: ModelType
    alternative_models: list[ModelType] = field(default_factory=list)
    reasoning: str = ""
    confidence: float = 0.0
    expected_cost: float = 0.0
    expected_time_ms: float = 0.0


class ModelRouter:
    """
    Advanced model router for AGI orchestration

    Routes requests to optimal models based on capabilities, performance
    requirements, cost constraints, and dream system integration.
    """

    def __init__(self):
        """Initialize the model router"""
        self.capabilities = self._initialize_capabilities()
        self.model_clients = {}
        self.routing_history = []
        self.performance_metrics = {}

        # Initialize available model clients
        self._initialize_model_clients()

        logger.info(f"🌐 Model router initialized with {len(self.capabilities)} models")

    def _initialize_capabilities(self) -> dict[ModelType, ModelCapability]:
        """Initialize model capability profiles"""

        capabilities = {
            ModelType.GPT_4: ModelCapability(
                model_type=ModelType.GPT_4,
                reasoning_score=0.9,
                creativity_score=0.8,
                code_score=0.85,
                analysis_score=0.88,
                speed_score=0.6,
                cost_efficiency=0.5,
                context_length=8192,
                supports_function_calls=True,
                supports_vision=False,
            ),
            ModelType.GPT_4_TURBO: ModelCapability(
                model_type=ModelType.GPT_4_TURBO,
                reasoning_score=0.92,
                creativity_score=0.85,
                code_score=0.87,
                analysis_score=0.9,
                speed_score=0.8,
                cost_efficiency=0.7,
                context_length=128000,
                supports_function_calls=True,
                supports_vision=True,
            ),
            ModelType.GPT_4O: ModelCapability(
                model_type=ModelType.GPT_4O,
                reasoning_score=0.93,
                creativity_score=0.82,
                code_score=0.89,
                analysis_score=0.91,
                speed_score=0.9,
                cost_efficiency=0.8,
                context_length=128000,
                supports_function_calls=True,
                supports_vision=True,
            ),
            ModelType.CLAUDE_3_OPUS: ModelCapability(
                model_type=ModelType.CLAUDE_3_OPUS,
                reasoning_score=0.95,
                creativity_score=0.9,
                code_score=0.85,
                analysis_score=0.93,
                speed_score=0.5,
                cost_efficiency=0.4,
                context_length=200000,
                supports_function_calls=True,
                supports_vision=True,
            ),
            ModelType.CLAUDE_3_SONNET: ModelCapability(
                model_type=ModelType.CLAUDE_3_SONNET,
                reasoning_score=0.88,
                creativity_score=0.87,
                code_score=0.9,
                analysis_score=0.89,
                speed_score=0.8,
                cost_efficiency=0.8,
                context_length=200000,
                supports_function_calls=True,
                supports_vision=True,
            ),
            ModelType.CLAUDE_3_HAIKU: ModelCapability(
                model_type=ModelType.CLAUDE_3_HAIKU,
                reasoning_score=0.75,
                creativity_score=0.78,
                code_score=0.8,
                analysis_score=0.77,
                speed_score=0.95,
                cost_efficiency=0.95,
                context_length=200000,
                supports_function_calls=True,
                supports_vision=True,
            ),
            ModelType.GEMINI_PRO: ModelCapability(
                model_type=ModelType.GEMINI_PRO,
                reasoning_score=0.85,
                creativity_score=0.8,
                code_score=0.82,
                analysis_score=0.86,
                speed_score=0.85,
                cost_efficiency=0.85,
                context_length=30720,
                supports_function_calls=True,
                supports_vision=True,
            ),
            ModelType.GEMINI_ULTRA: ModelCapability(
                model_type=ModelType.GEMINI_ULTRA,
                reasoning_score=0.94,
                creativity_score=0.88,
                code_score=0.87,
                analysis_score=0.92,
                speed_score=0.6,
                cost_efficiency=0.5,
                context_length=30720,
                supports_function_calls=True,
                supports_vision=True,
            ),
        }

        return capabilities

    def _initialize_model_clients(self):
        """Initialize model client connections"""

        if LUKHAS_WRAPPERS_AVAILABLE:
            try:
                # Initialize OpenAI client for GPT models
                self.model_clients["openai"] = UnifiedOpenAIClient()
                logger.info("✅ OpenAI client initialized")

                # Initialize Anthropic client for Claude models
                self.model_clients["anthropic"] = AnthropicWrapper()
                logger.info("✅ Anthropic client initialized")

            except Exception as e:
                logger.warning(f"Failed to initialize some model clients: {e}")
        else:
            logger.warning("LUKHAS model wrappers not available, using fallback mode")

    async def route_request(self, request: RoutingRequest) -> tuple[RoutingDecision, ModelResponse]:
        """
        Route a request to the optimal model

        Args:
            request: The routing request with task details

        Returns:
            Tuple of (routing decision, model response)
        """
        logger.info(f"🌐 Routing {request.task_type.value} request: {request.content[:100]}...")

        start_time = asyncio.get_event_loop().time()

        try:
            # Step 1: Select optimal model
            decision = await self._make_routing_decision(request)

            # Step 2: Execute request with selected model
            response = await self._execute_request(decision.selected_model, request)

            # Step 3: Update performance metrics
            end_time = asyncio.get_event_loop().time()
            actual_time = (end_time - start_time) * 1000

            self._update_performance_metrics(decision.selected_model, actual_time, response.confidence)

            # Step 4: Log routing decision
            self.routing_history.append(
                {
                    "timestamp": request.timestamp,
                    "task_type": request.task_type.value,
                    "selected_model": decision.selected_model.value,
                    "actual_time_ms": actual_time,
                    "confidence": response.confidence,
                    "tokens_used": response.tokens_used,
                    "cost": response.cost_estimate,
                }
            )

            logger.info(
                f"✅ Routed to {decision.selected_model.value}: "
                f"{response.confidence:.3f} confidence, {actual_time:.0f}ms"
            )

            return decision, response

        except Exception as e:
            logger.error(f"❌ Routing failed: {e}")

            # Fallback response
            fallback_response = ModelResponse(
                model_type=ModelType.GPT_4,  # Default fallback
                content=f"Error processing request: {e!s}",
                confidence=0.0,
                processing_time_ms=0.0,
                tokens_used=0,
                cost_estimate=0.0,
                metadata={"error": str(e)},
            )

            fallback_decision = RoutingDecision(
                selected_model=ModelType.GPT_4, reasoning="Fallback due to routing error", confidence=0.0
            )

            return fallback_decision, fallback_response

    async def _make_routing_decision(self, request: RoutingRequest) -> RoutingDecision:
        """Make the optimal routing decision"""

        # Get task-specific capability requirements
        task_weights = self._get_task_capability_weights(request.task_type)

        # Score each model for this specific request
        model_scores = {}

        for model_type, capability in self.capabilities.items():
            # Skip if model not in preferred list (if specified)
            if request.preferred_models and model_type not in request.preferred_models:
                continue

            # Calculate capability score
            capability_score = (
                capability.reasoning_score * task_weights["reasoning"]
                + capability.creativity_score * task_weights["creativity"]
                + capability.code_score * task_weights["code"]
                + capability.analysis_score * task_weights["analysis"]
            )

            # Adjust for performance requirements
            performance_score = self._calculate_performance_score(capability, request.performance_requirement)

            # Adjust for cost constraints
            cost_score = capability.cost_efficiency
            if request.max_cost:
                estimated_cost = self._estimate_cost(model_type, len(request.content))
                if estimated_cost > request.max_cost:
                    cost_score = 0.0  # Exclude if over budget

            # Dream enhancement bonus
            dream_bonus = 0.0
            if request.dream_enhanced:
                # Favor creative and reasoning models for dream tasks
                dream_bonus = (capability.creativity_score + capability.reasoning_score) * 0.1

            # Combined score
            total_score = capability_score * 0.5 + performance_score * 0.2 + cost_score * 0.2 + dream_bonus * 0.1

            model_scores[model_type] = total_score

        # Select best model
        if not model_scores:
            # No models available, use default
            selected_model = ModelType.GPT_4
            alternatives = []
            reasoning = "No models met criteria, using default GPT-4"
            confidence = 0.3
        else:
            # Sort by score
            sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
            selected_model = sorted_models[0][0]
            alternatives = [model for model, _ in sorted_models[1:3]]  # Top 2 alternatives
            reasoning = f"Selected based on combined score: {sorted_models[0][1]:.3f}"
            confidence = min(1.0, sorted_models[0][1])

        return RoutingDecision(
            selected_model=selected_model,
            alternative_models=alternatives,
            reasoning=reasoning,
            confidence=confidence,
            expected_cost=self._estimate_cost(selected_model, len(request.content)),
            expected_time_ms=self._estimate_time(selected_model, request.performance_requirement),
        )

    def _get_task_capability_weights(self, task_type: TaskType) -> dict[str, float]:
        """Get capability weights for specific task types"""

        weights = {
            TaskType.REASONING: {"reasoning": 0.6, "creativity": 0.1, "code": 0.1, "analysis": 0.2},
            TaskType.CODE_GENERATION: {"reasoning": 0.2, "creativity": 0.2, "code": 0.5, "analysis": 0.1},
            TaskType.CREATIVE_WRITING: {"reasoning": 0.1, "creativity": 0.7, "code": 0.0, "analysis": 0.2},
            TaskType.ANALYSIS: {"reasoning": 0.3, "creativity": 0.1, "code": 0.1, "analysis": 0.5},
            TaskType.CONVERSATION: {"reasoning": 0.3, "creativity": 0.3, "code": 0.1, "analysis": 0.3},
            TaskType.MATH: {"reasoning": 0.6, "creativity": 0.0, "code": 0.2, "analysis": 0.2},
            TaskType.RESEARCH: {"reasoning": 0.4, "creativity": 0.1, "code": 0.1, "analysis": 0.4},
            TaskType.DREAM_SYNTHESIS: {"reasoning": 0.3, "creativity": 0.5, "code": 0.0, "analysis": 0.2},
        }

        return weights.get(task_type, {"reasoning": 0.25, "creativity": 0.25, "code": 0.25, "analysis": 0.25})

    def _calculate_performance_score(self, capability: ModelCapability, requirement: PerformanceRequirement) -> float:
        """Calculate performance score based on requirements"""

        if requirement == PerformanceRequirement.FAST:
            return capability.speed_score
        elif requirement == PerformanceRequirement.BALANCED:
            return (capability.speed_score + capability.reasoning_score) / 2
        elif requirement == PerformanceRequirement.THOROUGH:
            return capability.reasoning_score
        elif requirement == PerformanceRequirement.DEEP:
            return (capability.reasoning_score + capability.analysis_score) / 2
        else:
            return 0.5

    def _estimate_cost(self, model_type: ModelType, content_length: int) -> float:
        """Estimate cost for running the model"""

        # Rough cost estimates (these would be updated based on actual pricing)
        base_costs = {
            ModelType.GPT_4: 0.03,
            ModelType.GPT_4_TURBO: 0.01,
            ModelType.GPT_4O: 0.005,
            ModelType.CLAUDE_3_OPUS: 0.015,
            ModelType.CLAUDE_3_SONNET: 0.003,
            ModelType.CLAUDE_3_HAIKU: 0.00025,
            ModelType.GEMINI_PRO: 0.0005,
            ModelType.GEMINI_ULTRA: 0.01,
        }

        base_cost = base_costs.get(model_type, 0.01)

        # Estimate tokens (rough approximation)
        estimated_tokens = content_length / 4  # ~4 chars per token

        return base_cost * (estimated_tokens / 1000)  # Cost per 1k tokens

    def _estimate_time(self, model_type: ModelType, requirement: PerformanceRequirement) -> float:
        """Estimate processing time in milliseconds"""

        capability = self.capabilities.get(model_type)
        if not capability:
            return 5000.0  # Default 5s

        # Base time inversely related to speed score
        base_time = 10000 / max(capability.speed_score, 0.1)  # 1-100s range

        # Adjust for requirement
        if requirement == PerformanceRequirement.FAST:
            return base_time * 0.5
        elif requirement == PerformanceRequirement.BALANCED:
            return base_time
        elif requirement == PerformanceRequirement.THOROUGH:
            return base_time * 2.0
        elif requirement == PerformanceRequirement.DEEP:
            return base_time * 5.0
        else:
            return base_time

    async def _execute_request(self, model_type: ModelType, request: RoutingRequest) -> ModelResponse:
        """Execute the request with the selected model"""

        start_time = asyncio.get_event_loop().time()

        try:
            # This is a simplified implementation - in production would call actual models
            content = await self._call_model(model_type, request)

            end_time = asyncio.get_event_loop().time()
            processing_time = (end_time - start_time) * 1000

            # Simulate realistic response
            confidence = 0.7 + (hash(request.content) % 30) / 100  # Deterministic but varied
            tokens_used = len(request.content) // 3 + len(content) // 3  # Rough estimate
            cost_estimate = self._estimate_cost(model_type, len(request.content + content))

            return ModelResponse(
                model_type=model_type,
                content=content,
                confidence=confidence,
                processing_time_ms=processing_time,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                metadata={"task_type": request.task_type.value, "dream_enhanced": request.dream_enhanced},
            )

        except Exception as e:
            logger.error(f"Model execution failed for {model_type.value}: {e}")

            # Return error response
            return ModelResponse(
                model_type=model_type,
                content=f"Model execution failed: {e!s}",
                confidence=0.0,
                processing_time_ms=0.0,
                tokens_used=0,
                cost_estimate=0.0,
                metadata={"error": str(e)},
            )

    async def _call_model(self, model_type: ModelType, request: RoutingRequest) -> str:
        """Actually call the specified model (simplified implementation)"""

        # In production, this would call the actual model APIs
        # For now, return a mock response based on model capabilities

        capability = self.capabilities.get(model_type)
        if not capability:
            return "Model not available"

        # Simulate model response based on task type and capabilities
        task_responses = {
            TaskType.REASONING: f"Based on {model_type.value} reasoning (score: {capability.reasoning_score:.2f}): Analysis suggests...",
            TaskType.CODE_GENERATION: f"Using {model_type.value} coding capabilities: ```python\n# Generated code here\n```",
            TaskType.CREATIVE_WRITING: f"Creative output from {model_type.value} (creativity: {capability.creativity_score:.2f}): Once upon a time...",
            TaskType.ANALYSIS: f"Analysis from {model_type.value}: The data indicates...",
            TaskType.DREAM_SYNTHESIS: f"Dream insight from {model_type.value}: In the realm of possibilities...",
        }

        base_response = task_responses.get(request.task_type, f"Response from {model_type.value}")

        # Add dream enhancement if requested
        if request.dream_enhanced:
            base_response += "\n\n🌙 Dream-enhanced perspective: This solution transcends conventional approaches..."

        return base_response

    def _update_performance_metrics(self, model_type: ModelType, actual_time: float, confidence: float):
        """Update performance tracking for the model"""

        if model_type not in self.performance_metrics:
            self.performance_metrics[model_type] = {
                "total_requests": 0,
                "avg_time_ms": 0.0,
                "avg_confidence": 0.0,
                "success_count": 0,
            }

        metrics = self.performance_metrics[model_type]
        metrics["total_requests"] += 1

        # Update running averages
        n = metrics["total_requests"]
        metrics["avg_time_ms"] = ((n - 1) * metrics["avg_time_ms"] + actual_time) / n
        metrics["avg_confidence"] = ((n - 1) * metrics["avg_confidence"] + confidence) / n

        if confidence > 0.6:
            metrics["success_count"] += 1

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary for all models"""

        summary = {
            "total_requests_routed": len(self.routing_history),
            "models_available": len(self.capabilities),
            "models_with_clients": len(self.model_clients),
            "model_performance": {},
        }

        for model_type, metrics in self.performance_metrics.items():
            success_rate = metrics["success_count"] / max(metrics["total_requests"], 1)
            summary["model_performance"][model_type.value] = {
                "requests": metrics["total_requests"],
                "avg_time_ms": round(metrics["avg_time_ms"], 1),
                "avg_confidence": round(metrics["avg_confidence"], 3),
                "success_rate": round(success_rate, 3),
            }

        # Recent routing patterns
        if self.routing_history:
            recent_routes = self.routing_history[-10:]  # Last 10 routes
            summary["recent_model_usage"] = {}
            for route in recent_routes:
                model = route["selected_model"]
                if model not in summary["recent_model_usage"]:
                    summary["recent_model_usage"][model] = 0
                summary["recent_model_usage"][model] += 1

        return summary

    def get_model_capabilities(self) -> dict[str, dict[str, Any]]:
        """Get detailed model capabilities"""

        capabilities_dict = {}

        for model_type, capability in self.capabilities.items():
            capabilities_dict[model_type.value] = {
                "reasoning_score": capability.reasoning_score,
                "creativity_score": capability.creativity_score,
                "code_score": capability.code_score,
                "analysis_score": capability.analysis_score,
                "speed_score": capability.speed_score,
                "cost_efficiency": capability.cost_efficiency,
                "context_length": capability.context_length,
                "supports_function_calls": capability.supports_function_calls,
                "supports_vision": capability.supports_vision,
                "supports_code_execution": capability.supports_code_execution,
            }

        return capabilities_dict
