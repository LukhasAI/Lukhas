#!/usr/bin/env python3
"""
LUKHAS O.2 Orchestration Core - Multi-AI Router
Production Schema v1.0.0

Implements multi-AI routing and consensus with performance monitoring,
load balancing, and intelligent model selection.

Constellation Framework: Flow Star (🌊) coordination hub
"""

from __future__ import annotations
import asyncio
import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union
from opentelemetry import trace
from prometheus_client import Counter, Histogram, Gauge
import logging

# Import provider factory
from .providers import create_provider_client, get_provider_status, validate_provider_configuration

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Prometheus metrics
multi_ai_requests_total = Counter(
    'lukhas_multi_ai_requests_total',
    'Total multi-AI requests',
    ['provider', 'model', 'consensus_type']
)

multi_ai_latency_seconds = Histogram(
    'lukhas_multi_ai_latency_seconds',
    'Multi-AI request latency',
    ['provider', 'model'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

consensus_agreement_ratio = Gauge(
    'lukhas_consensus_agreement_ratio',
    'Consensus agreement ratio',
    ['consensus_type']
)

model_availability = Gauge(
    'lukhas_model_availability',
    'Model availability status',
    ['provider', 'model']
)


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    PERPLEXITY = "perplexity"
    LOCAL = "local"


class ConsensusType(Enum):
    """Types of consensus mechanisms"""
    MAJORITY = "majority"
    WEIGHTED = "weighted"
    UNANIMOUS = "unanimous"
    BEST_OF_N = "best_of_n"
    HYBRID = "hybrid"


@dataclass
class AIModel:
    """AI model configuration"""
    provider: AIProvider
    model_id: str
    weight: float = 1.0
    max_tokens: int = 4096
    temperature: float = 0.7
    available: bool = True
    avg_latency: float = 0.0
    success_rate: float = 1.0
    cost_per_token: float = 0.0


@dataclass
class RoutingRequest:
    """Multi-AI routing request"""
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    models: List[str] = field(default_factory=list)
    consensus_type: ConsensusType = ConsensusType.MAJORITY
    min_responses: int = 2
    max_responses: int = 3
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResponse:
    """Response from a single AI model"""
    provider: AIProvider
    model_id: str
    response: str
    latency: float
    tokens_used: int
    cost: float
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusResult:
    """Result of consensus evaluation"""
    final_response: str
    confidence: float
    agreement_ratio: float
    participating_models: List[str]
    individual_responses: List[AIResponse]
    consensus_type: ConsensusType
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModelSelector:
    """Intelligent model selection based on performance and availability"""

    def __init__(self):
        self.models: Dict[str, AIModel] = {}
        self.performance_history: Dict[str, List[float]] = {}

    def register_model(self, model: AIModel) -> None:
        """Register a new AI model"""
        key = f"{model.provider.value}:{model.model_id}"
        self.models[key] = model
        self.performance_history[key] = []

        model_availability.labels(
            provider=model.provider.value,
            model=model.model_id
        ).set(1 if model.available else 0)

    def select_models(self,
                     request: RoutingRequest,
                     exclude_models: List[str] = None) -> List[AIModel]:
        """Select optimal models for the request"""
        exclude_models = exclude_models or []

        # Filter available models
        available_models = [
            model for key, model in self.models.items()
            if model.available and key not in exclude_models
        ]

        if request.models:
            # Use specific models if requested
            selected = [
                model for model in available_models
                if f"{model.provider.value}:{model.model_id}" in request.models
            ]
        else:
            # Intelligent selection based on performance
            selected = self._intelligent_selection(available_models, request)

        # Ensure we have enough models
        num_needed = min(request.max_responses, len(selected))
        num_needed = max(num_needed, request.min_responses)

        return selected[:num_needed]

    def _intelligent_selection(self,
                             available_models: List[AIModel],
                             request: RoutingRequest) -> List[AIModel]:
        """Intelligent model selection algorithm"""
        # Score models based on multiple factors
        scored_models = []

        for model in available_models:
            score = self._calculate_model_score(model, request)
            scored_models.append((score, model))

        # Sort by score (higher is better) and return top models
        scored_models.sort(key=lambda x: x[0], reverse=True)
        return [model for _, model in scored_models]

    def _calculate_model_score(self, model: AIModel, request: RoutingRequest) -> float:
        """Calculate model score for selection"""
        # Base score from model weight
        score = model.weight

        # Adjust for success rate
        score *= model.success_rate

        # Adjust for latency (lower is better)
        if model.avg_latency > 0:
            score *= (1.0 / (1.0 + model.avg_latency))

        # Adjust for cost efficiency
        if model.cost_per_token > 0:
            cost_factor = 1.0 / (1.0 + model.cost_per_token)
            score *= cost_factor

        return score

    def update_performance(self,
                          provider: AIProvider,
                          model_id: str,
                          latency: float,
                          success: bool) -> None:
        """Update model performance metrics"""
        key = f"{provider.value}:{model_id}"
        if key not in self.models:
            return

        model = self.models[key]

        # Update latency (exponential moving average)
        alpha = 0.1
        if model.avg_latency == 0:
            model.avg_latency = latency
        else:
            model.avg_latency = alpha * latency + (1 - alpha) * model.avg_latency

        # Update success rate
        history = self.performance_history[key]
        history.append(1.0 if success else 0.0)

        # Keep only recent history
        if len(history) > 100:
            history = history[-100:]
            self.performance_history[key] = history

        # Calculate success rate from recent history
        if history:
            model.success_rate = sum(history) / len(history)


class ConsensusEngine:
    """Consensus evaluation engine"""

    def __init__(self):
        self.similarity_cache: Dict[str, float] = {}

    async def evaluate_consensus(self,
                               responses: List[AIResponse],
                               consensus_type: ConsensusType) -> ConsensusResult:
        """Evaluate consensus from multiple AI responses"""

        with tracer.start_span("consensus.evaluate") as span:
            span.set_attribute("consensus_type", consensus_type.value)
            span.set_attribute("response_count", len(responses))

            if consensus_type == ConsensusType.MAJORITY:
                return await self._majority_consensus(responses)
            elif consensus_type == ConsensusType.WEIGHTED:
                return await self._weighted_consensus(responses)
            elif consensus_type == ConsensusType.UNANIMOUS:
                return await self._unanimous_consensus(responses)
            elif consensus_type == ConsensusType.BEST_OF_N:
                return await self._best_of_n_consensus(responses)
            elif consensus_type == ConsensusType.HYBRID:
                return await self._hybrid_consensus(responses)
            else:
                # Default to majority
                return await self._majority_consensus(responses)

    async def _majority_consensus(self, responses: List[AIResponse]) -> ConsensusResult:
        """Simple majority consensus"""
        if not responses:
            raise ValueError("No responses to evaluate")

        # Group similar responses
        groups = await self._group_similar_responses(responses)

        # Find largest group
        largest_group = max(groups, key=len)

        # Calculate agreement ratio
        agreement_ratio = len(largest_group) / len(responses)

        # Select best response from largest group
        best_response = max(largest_group, key=lambda r: r.confidence)

        consensus_agreement_ratio.labels(
            consensus_type="majority"
        ).set(agreement_ratio)

        return ConsensusResult(
            final_response=best_response.response,
            confidence=best_response.confidence,
            agreement_ratio=agreement_ratio,
            participating_models=[f"{r.provider.value}:{r.model_id}" for r in responses],
            individual_responses=responses,
            consensus_type=ConsensusType.MAJORITY,
            metadata={"largest_group_size": len(largest_group)}
        )

    async def _weighted_consensus(self, responses: List[AIResponse]) -> ConsensusResult:
        """Weighted consensus based on model confidence and performance"""
        if not responses:
            raise ValueError("No responses to evaluate")

        # Calculate weighted scores for each response
        weighted_responses = []
        total_weight = 0

        for response in responses:
            # Weight based on confidence, inverse latency, and success rate
            weight = (
                response.confidence *
                (1.0 / (1.0 + response.latency)) *
                (1.0 / (1.0 + response.cost)) if response.cost > 0 else 1.0
            )
            weighted_responses.append((weight, response))
            total_weight += weight

        # Sort by weight
        weighted_responses.sort(key=lambda x: x[0], reverse=True)

        # Select highest weighted response
        best_weight, best_response = weighted_responses[0]

        # Calculate agreement ratio (normalized weight of best response)
        agreement_ratio = best_weight / total_weight if total_weight > 0 else 0

        consensus_agreement_ratio.labels(
            consensus_type="weighted"
        ).set(agreement_ratio)

        return ConsensusResult(
            final_response=best_response.response,
            confidence=best_response.confidence,
            agreement_ratio=agreement_ratio,
            participating_models=[f"{r.provider.value}:{r.model_id}" for r in responses],
            individual_responses=responses,
            consensus_type=ConsensusType.WEIGHTED,
            metadata={"best_weight": best_weight, "total_weight": total_weight}
        )

    async def _unanimous_consensus(self, responses: List[AIResponse]) -> ConsensusResult:
        """Unanimous consensus - all responses must be similar"""
        if not responses:
            raise ValueError("No responses to evaluate")

        # Check if all responses are similar
        similarity_threshold = 0.8
        all_similar = True

        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                similarity = await self._calculate_similarity(
                    responses[i].response,
                    responses[j].response
                )
                if similarity < similarity_threshold:
                    all_similar = False
                    break
            if not all_similar:
                break

        agreement_ratio = 1.0 if all_similar else 0.0

        # If unanimous, select highest confidence response
        if all_similar:
            best_response = max(responses, key=lambda r: r.confidence)
        else:
            # Fallback to majority consensus
            return await self._majority_consensus(responses)

        consensus_agreement_ratio.labels(
            consensus_type="unanimous"
        ).set(agreement_ratio)

        return ConsensusResult(
            final_response=best_response.response,
            confidence=best_response.confidence,
            agreement_ratio=agreement_ratio,
            participating_models=[f"{r.provider.value}:{r.model_id}" for r in responses],
            individual_responses=responses,
            consensus_type=ConsensusType.UNANIMOUS,
            metadata={"unanimous": all_similar}
        )

    async def _best_of_n_consensus(self, responses: List[AIResponse]) -> ConsensusResult:
        """Best-of-N consensus - select single best response"""
        if not responses:
            raise ValueError("No responses to evaluate")

        # Score each response based on multiple factors
        scored_responses = []

        for response in responses:
            score = self._calculate_response_score(response)
            scored_responses.append((score, response))

        # Sort by score and select best
        scored_responses.sort(key=lambda x: x[0], reverse=True)
        best_score, best_response = scored_responses[0]

        # Calculate agreement ratio as normalized score
        total_score = sum(score for score, _ in scored_responses)
        agreement_ratio = best_score / total_score if total_score > 0 else 0

        consensus_agreement_ratio.labels(
            consensus_type="best_of_n"
        ).set(agreement_ratio)

        return ConsensusResult(
            final_response=best_response.response,
            confidence=best_response.confidence,
            agreement_ratio=agreement_ratio,
            participating_models=[f"{r.provider.value}:{r.model_id}" for r in responses],
            individual_responses=responses,
            consensus_type=ConsensusType.BEST_OF_N,
            metadata={"best_score": best_score, "all_scores": [s for s, _ in scored_responses]}
        )

    async def _hybrid_consensus(self, responses: List[AIResponse]) -> ConsensusResult:
        """Hybrid consensus combining multiple approaches"""
        # First try majority consensus
        majority_result = await self._majority_consensus(responses)

        # If agreement is high, use majority
        if majority_result.agreement_ratio >= 0.7:
            majority_result.consensus_type = ConsensusType.HYBRID
            majority_result.metadata["method_used"] = "majority"
            return majority_result

        # Otherwise, use weighted consensus
        weighted_result = await self._weighted_consensus(responses)
        weighted_result.consensus_type = ConsensusType.HYBRID
        weighted_result.metadata["method_used"] = "weighted"
        return weighted_result

    def _calculate_response_score(self, response: AIResponse) -> float:
        """Calculate overall score for a response"""
        # Base score from confidence
        score = response.confidence

        # Adjust for latency (lower is better)
        latency_factor = 1.0 / (1.0 + response.latency)
        score *= latency_factor

        # Adjust for cost efficiency
        if response.cost > 0:
            cost_factor = 1.0 / (1.0 + response.cost)
            score *= cost_factor

        # Adjust for response length (moderate length preferred)
        length = len(response.response)
        if 100 <= length <= 1000:
            length_factor = 1.0
        else:
            length_factor = 0.8
        score *= length_factor

        return score

    async def _group_similar_responses(self,
                                     responses: List[AIResponse],
                                     threshold: float = 0.7) -> List[List[AIResponse]]:
        """Group responses by similarity"""
        groups = []

        for response in responses:
            # Find group for this response
            found_group = False

            for group in groups:
                # Check similarity with first response in group
                similarity = await self._calculate_similarity(
                    response.response,
                    group[0].response
                )

                if similarity >= threshold:
                    group.append(response)
                    found_group = True
                    break

            # Create new group if no similar group found
            if not found_group:
                groups.append([response])

        return groups

    async def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text responses"""
        # Create cache key
        key = hashlib.md5(f"{text1}:{text2}".encode()).hexdigest()

        if key in self.similarity_cache:
            return self.similarity_cache[key]

        # Simple similarity based on common words
        # In production, you might use more sophisticated NLP techniques
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            similarity = 0.0
        else:
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            similarity = intersection / union if union > 0 else 0.0

        # Cache result
        self.similarity_cache[key] = similarity

        # Keep cache size manageable
        if len(self.similarity_cache) > 10000:
            # Remove oldest entries
            keys_to_remove = list(self.similarity_cache.keys())[:1000]
            for k in keys_to_remove:
                del self.similarity_cache[k]

        return similarity


class MultiAIRouter:
    """Main multi-AI routing and consensus orchestrator"""

    def __init__(self):
        self.model_selector = ModelSelector()
        self.consensus_engine = ConsensusEngine()
        self.ai_clients: Dict[AIProvider, Any] = {}
        self.default_models: List[str] = []
        self._initialize_providers()

    def register_ai_client(self, provider: AIProvider, client: Any) -> None:
        """Register an AI client for a provider"""
        self.ai_clients[provider] = client
        logger.info(f"Registered AI client for {provider.value}")

    def register_default_models(self) -> None:
        """Register default AI models"""
        # OpenAI models
        self.model_selector.register_model(AIModel(
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            weight=1.0,
            cost_per_token=0.00003
        ))

        self.model_selector.register_model(AIModel(
            provider=AIProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            weight=0.8,
            cost_per_token=0.000002
        ))

        # Anthropic models
        self.model_selector.register_model(AIModel(
            provider=AIProvider.ANTHROPIC,
            model_id="claude-3-sonnet",
            weight=1.0,
            cost_per_token=0.000015
        ))

        # Google models
        self.model_selector.register_model(AIModel(
            provider=AIProvider.GOOGLE,
            model_id="gemini-pro",
            weight=0.9,
            cost_per_token=0.000001
        ))

        logger.info("Registered default AI models")

    def _initialize_providers(self) -> None:
        """Initialize AI provider clients with feature flag gating"""
        logger.info("Initializing AI provider clients...")

        # Validate provider configuration
        validation = validate_provider_configuration()
        logger.info(f"Provider validation: {validation}")

        # Create clients for all providers
        for provider in AIProvider:
            try:
                client = create_provider_client(provider)
                self.ai_clients[provider] = client
                logger.info(f"✅ {provider.value} client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {provider.value} client: {e}")
                # Fall back to mock client
                from .providers import MockAIClient
                self.ai_clients[provider] = MockAIClient()
                logger.warning(f"🔄 Using mock client for {provider.value}")

        # Log provider status
        status = get_provider_status()
        logger.info(f"Provider status summary: {status}")

    def _calculate_confidence(self, ai_response) -> float:
        """Calculate confidence score based on AI response"""
        base_confidence = 0.8  # Default confidence

        if ai_response.metadata and ai_response.metadata.get('mock'):
            return base_confidence

        # Adjust confidence based on response characteristics
        confidence = base_confidence

        # Factor in response length (longer responses often more confident)
        if len(ai_response.content) > 100:
            confidence += 0.1
        elif len(ai_response.content) < 20:
            confidence -= 0.1

        # Factor in finish reason
        if ai_response.finish_reason == 'stop':
            confidence += 0.05
        elif ai_response.finish_reason in ['length', 'content_filter']:
            confidence -= 0.1

        # Factor in latency (reasonable latency suggests good response)
        if 100 <= ai_response.latency_ms <= 2000:
            confidence += 0.05
        elif ai_response.latency_ms > 5000:
            confidence -= 0.1

        return max(0.1, min(1.0, confidence))  # Clamp between 0.1 and 1.0

    async def route_request(self, request: RoutingRequest) -> ConsensusResult:
        """Route request to multiple AI models and return consensus"""

        with tracer.start_span("multi_ai.route_request") as span:
            span.set_attribute("consensus_type", request.consensus_type.value)
            span.set_attribute("min_responses", request.min_responses)
            span.set_attribute("max_responses", request.max_responses)

            start_time = time.time()

            try:
                # Select models for the request
                selected_models = self.model_selector.select_models(request)

                if not selected_models:
                    raise ValueError("No available models for request")

                if len(selected_models) < request.min_responses:
                    raise ValueError(f"Only {len(selected_models)} models available, need {request.min_responses}")

                span.set_attribute("selected_models", len(selected_models))

                # Send requests to selected models
                responses = await self._send_parallel_requests(
                    request, selected_models
                )

                # Filter successful responses
                successful_responses = [r for r in responses if r is not None]

                if len(successful_responses) < request.min_responses:
                    raise ValueError(f"Only {len(successful_responses)} successful responses, need {request.min_responses}")

                # Evaluate consensus
                consensus_result = await self.consensus_engine.evaluate_consensus(
                    successful_responses,
                    request.consensus_type
                )

                # Record metrics
                latency = time.time() - start_time
                multi_ai_latency_seconds.labels(
                    provider="consensus",
                    model="multi_ai"
                ).observe(latency)

                multi_ai_requests_total.labels(
                    provider="consensus",
                    model="multi_ai",
                    consensus_type=request.consensus_type.value
                ).inc()

                span.set_attribute("final_confidence", consensus_result.confidence)
                span.set_attribute("agreement_ratio", consensus_result.agreement_ratio)

                return consensus_result

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    async def _send_parallel_requests(self,
                                    request: RoutingRequest,
                                    models: List[AIModel]) -> List[Optional[AIResponse]]:
        """Send requests to multiple models in parallel"""

        tasks = []
        for model in models:
            task = asyncio.create_task(
                self._send_single_request(request, model)
            )
            tasks.append(task)

        # Wait for all requests with timeout
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=request.timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Multi-AI request timed out after {request.timeout}s")
            responses = [None] * len(models)

        # Process results
        final_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.warning(f"Model {models[i].model_id} failed: {response}")
                final_responses.append(None)
            else:
                final_responses.append(response)

        return final_responses

    async def _send_single_request(self,
                                 request: RoutingRequest,
                                 model: AIModel) -> Optional[AIResponse]:
        """Send request to a single AI model"""

        start_time = time.time()

        with tracer.start_span("multi_ai.single_request") as span:
            span.set_attribute("provider", model.provider.value)
            span.set_attribute("model", model.model_id)

            try:
                # Get client for provider
                client = self.ai_clients.get(model.provider)
                if not client:
                    raise ValueError(f"No client registered for {model.provider.value}")

                # Call actual AI provider or mock
                ai_response = await client.generate(
                    prompt=request.prompt,
                    model=model.model_id,
                    max_tokens=request.max_tokens,
                    temperature=model.temperature,
                    system_prompt=getattr(request, 'system_prompt', None)
                )

                response_text = ai_response.content
                tokens_used = ai_response.usage.get('total_tokens', len(response_text.split())) if ai_response.usage else len(response_text.split())
                cost = tokens_used * model.cost_per_token
                latency = time.time() - start_time

                # Update model performance
                self.model_selector.update_performance(
                    model.provider,
                    model.model_id,
                    latency,
                    True
                )

                # Record metrics
                multi_ai_latency_seconds.labels(
                    provider=model.provider.value,
                    model=model.model_id
                ).observe(latency)

                multi_ai_requests_total.labels(
                    provider=model.provider.value,
                    model=model.model_id,
                    consensus_type=request.consensus_type.value
                ).inc()

                return AIResponse(
                    provider=model.provider,
                    model_id=model.model_id,
                    response=response_text,
                    latency=latency,
                    tokens_used=tokens_used,
                    cost=cost,
                    confidence=self._calculate_confidence(ai_response),
                    metadata={
                        "temperature": model.temperature,
                        "provider_metadata": ai_response.metadata,
                        "finish_reason": ai_response.finish_reason
                    }
                )

            except Exception as e:
                latency = time.time() - start_time

                # Update model performance (failure)
                self.model_selector.update_performance(
                    model.provider,
                    model.model_id,
                    latency,
                    False
                )

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                logger.error(f"Request failed for {model.model_id}: {e}")
                return None


# Global router instance
_global_router: Optional[MultiAIRouter] = None

def get_multi_ai_router() -> MultiAIRouter:
    """Get global multi-AI router instance"""
    global _global_router
    if _global_router is None:
        _global_router = MultiAIRouter()
        _global_router.register_default_models()
    return _global_router


async def route_multi_ai_request(request: RoutingRequest) -> ConsensusResult:
    """Convenience function for routing multi-AI requests"""
    router = get_multi_ai_router()
    return await router.route_request(request)