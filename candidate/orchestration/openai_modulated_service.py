"""
OpenAI Modulated Service for Multi-AI Orchestration
Integration specialist for OpenAI models within LUKHAS orchestration framework
Implements consensus processing, context preservation, and performance optimization
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from candidate.core.orchestration.core_modules.symbolic_signal_router import route_signal, SymbolicSignal, SignalType
from candidate.orchestration.context_bus import ContextBusOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class OpenAIModelConfig:
    """Configuration for OpenAI model integration"""
    model_name: str
    api_key: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout_seconds: int = 30
    retry_attempts: int = 3
    enable_streaming: bool = False


@dataclass
class AIModelResponse:
    """Standardized response from AI models"""
    model_name: str
    response_text: str
    token_count: int
    processing_time_ms: float
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = None


class OpenAIModulatedService:
    """
    Multi-AI orchestration service with OpenAI integration
    Implements consensus processing and context preservation
    """

    def __init__(self, context_bus: Optional[ContextBusOrchestrator] = None):
        """
        Initialize OpenAI modulated service

        Args:
            context_bus: Optional context bus for orchestration integration
        """
        self.context_bus = context_bus
        self.clients = {}
        self.model_configs = {}
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time_ms": 0.0,
            "token_usage": 0,
        }

        # Initialize default model configurations
        self._initialize_default_models()

        # Service status
        self.is_initialized = False
        self.last_health_check = None

        logger.info("OpenAI Modulated Service initialized")

    def _initialize_default_models(self):
        """Initialize default OpenAI model configurations"""
        default_models = [
            OpenAIModelConfig(
                model_name="gpt-4",
                max_tokens=4000,
                temperature=0.7,
                timeout_seconds=30
            ),
            OpenAIModelConfig(
                model_name="gpt-3.5-turbo",
                max_tokens=4000,
                temperature=0.7,
                timeout_seconds=20
            ),
            OpenAIModelConfig(
                model_name="gpt-4-turbo",
                max_tokens=8000,
                temperature=0.7,
                timeout_seconds=45
            )
        ]

        for config in default_models:
            self.model_configs[config.model_name] = config

    async def initialize(self, api_key: Optional[str] = None) -> bool:
        """
        Initialize the service with API credentials

        Args:
            api_key: OpenAI API key

        Returns:
            bool: True if initialization successful
        """
        try:
            if not OPENAI_AVAILABLE:
                logger.error("OpenAI library not available - install openai package")
                return False

            # Set API key if provided
            if api_key:
                openai.api_key = api_key

            # Test connection with a simple request
            await self._test_connection()

            self.is_initialized = True
            self.last_health_check = datetime.now(timezone.utc)

            logger.info("OpenAI Modulated Service initialization successful")
            return True

        except Exception as e:
            logger.error(f"OpenAI service initialization failed: {e}")
            return False

    async def _test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            # Simple test request
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False

    async def process_with_consensus(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process prompt with multiple models for consensus

        Args:
            prompt: Input prompt for processing
            models: List of model names to use (uses defaults if None)
            context: Additional context for processing

        Returns:
            Dict containing consensus results and individual responses
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized - call initialize() first")

        # Use default models if none specified
        if models is None:
            models = ["gpt-4", "gpt-3.5-turbo"]

        # Filter to available models
        available_models = [m for m in models if m in self.model_configs]

        if not available_models:
            raise ValueError(f"No available models from requested: {models}")

        logger.info(f"Processing consensus with {len(available_models)} models")

        # Send signal for multi-AI processing start
        if self.context_bus:
            signal = SymbolicSignal(
                signal_type=SignalType.INTENT_PROCESS,
                source_module="openai_service",
                target_module="orchestrator",
                payload={
                    "operation": "multi_ai_consensus",
                    "models": available_models,
                    "prompt_length": len(prompt)
                },
                timestamp=time.time()
            )
            await route_signal(signal)

        # Process with each model in parallel
        tasks = []
        for model_name in available_models:
            task = self._process_single_model(prompt, model_name, context)
            tasks.append(task)

        # Wait for all responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful_responses = []
        failed_responses = []

        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                failed_responses.append({
                    "model": available_models[i],
                    "error": str(response)
                })
            else:
                successful_responses.append(response)

        # Generate consensus
        consensus_result = await self._generate_consensus(successful_responses)

        # Update metrics
        self.performance_metrics["total_requests"] += len(available_models)
        self.performance_metrics["successful_requests"] += len(successful_responses)
        self.performance_metrics["failed_requests"] += len(failed_responses)

        return {
            "consensus": consensus_result,
            "individual_responses": successful_responses,
            "failed_responses": failed_responses,
            "processing_stats": {
                "models_used": len(available_models),
                "successful_models": len(successful_responses),
                "failed_models": len(failed_responses)
            }
        }

    async def _process_single_model(
        self,
        prompt: str,
        model_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AIModelResponse:
        """
        Process prompt with a single model

        Args:
            prompt: Input prompt
            model_name: Name of the model to use
            context: Additional context

        Returns:
            AIModelResponse containing the result
        """
        start_time = time.perf_counter()
        config = self.model_configs[model_name]

        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]

            # Add context if provided
            if context:
                system_message = f"Context: {context}"
                messages.insert(0, {"role": "system", "content": system_message})

            # Make API call
            response = await openai.ChatCompletion.acreate(
                model=model_name,
                messages=messages,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                timeout=config.timeout_seconds
            )

            # Calculate processing time
            processing_time = (time.perf_counter() - start_time) * 1000

            # Extract response data
            response_text = response.choices[0].message.content
            token_count = response.usage.total_tokens

            # Update metrics
            self.performance_metrics["token_usage"] += token_count

            return AIModelResponse(
                model_name=model_name,
                response_text=response_text,
                token_count=token_count,
                processing_time_ms=processing_time,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )

        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Model {model_name} processing failed: {e}")
            raise

    async def _generate_consensus(self, responses: List[AIModelResponse]) -> Dict[str, Any]:
        """
        Generate consensus from multiple model responses

        Args:
            responses: List of model responses

        Returns:
            Dict containing consensus analysis
        """
        if not responses:
            return {"error": "No successful responses for consensus"}

        # Calculate average metrics
        avg_processing_time = sum(r.processing_time_ms for r in responses) / len(responses)
        total_tokens = sum(r.token_count for r in responses)

        # Simple consensus: take the longest response as primary
        # In a more sophisticated implementation, this would use semantic similarity
        primary_response = max(responses, key=lambda x: len(x.response_text))

        # Identify common themes (simplified)
        response_texts = [r.response_text for r in responses]
        common_words = self._find_common_themes(response_texts)

        return {
            "primary_response": primary_response.response_text,
            "primary_model": primary_response.model_name,
            "consensus_confidence": self._calculate_consensus_confidence(responses),
            "common_themes": common_words,
            "metrics": {
                "avg_processing_time_ms": avg_processing_time,
                "total_tokens_used": total_tokens,
                "response_count": len(responses)
            },
            "all_responses": [
                {
                    "model": r.model_name,
                    "response": r.response_text,
                    "tokens": r.token_count,
                    "time_ms": r.processing_time_ms
                }
                for r in responses
            ]
        }

    def _find_common_themes(self, texts: List[str]) -> List[str]:
        """Find common themes across response texts (simplified implementation)"""
        # This is a basic implementation - in production, use more sophisticated NLP
        word_counts = {}
        for text in texts:
            words = text.lower().split()
            for word in words:
                if len(word) > 4:  # Only consider longer words
                    word_counts[word] = word_counts.get(word, 0) + 1

        # Return words that appear in multiple responses
        common_threshold = max(1, len(texts) // 2)
        common_words = [word for word, count in word_counts.items() if count >= common_threshold]
        return sorted(common_words, key=lambda w: word_counts[w], reverse=True)[:10]

    def _calculate_consensus_confidence(self, responses: List[AIModelResponse]) -> float:
        """Calculate confidence in consensus based on response similarity"""
        if len(responses) < 2:
            return 1.0

        # Simplified confidence calculation based on response length similarity
        lengths = [len(r.response_text) for r in responses]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)

        # Lower variance = higher confidence (normalized to 0-1)
        confidence = max(0.0, 1.0 - (variance / (avg_length ** 2)))
        return confidence

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the service"""
        try:
            if not self.is_initialized:
                return {"status": "not_initialized", "healthy": False}

            # Test connection
            connection_ok = await self._test_connection()

            # Update health check time
            self.last_health_check = datetime.now(timezone.utc)

            return {
                "status": "healthy" if connection_ok else "connection_failed",
                "healthy": connection_ok,
                "last_check": self.last_health_check.isoformat(),
                "metrics": self.performance_metrics,
                "available_models": list(self.model_configs.keys()),
                "openai_library_available": OPENAI_AVAILABLE
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "healthy": False,
                "error": str(e),
                "last_check": datetime.now(timezone.utc).isoformat()
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        if self.performance_metrics["total_requests"] > 0:
            success_rate = (
                self.performance_metrics["successful_requests"] /
                self.performance_metrics["total_requests"]
            )
        else:
            success_rate = 0.0

        return {
            **self.performance_metrics,
            "success_rate": success_rate,
            "is_initialized": self.is_initialized,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
        }

    async def shutdown(self):
        """Gracefully shutdown the service"""
        logger.info("Shutting down OpenAI Modulated Service")

        # Send shutdown signal
        if self.context_bus:
            signal = SymbolicSignal(
                signal_type=SignalType.DIAGNOSTIC,
                source_module="openai_service",
                target_module="orchestrator",
                payload={"operation": "service_shutdown", "metrics": self.performance_metrics},
                timestamp=time.time()
            )
            await route_signal(signal)

        self.is_initialized = False
        logger.info("OpenAI Modulated Service shutdown complete")


# Factory function for easy instantiation
def create_openai_service(context_bus: Optional[ContextBusOrchestrator] = None) -> OpenAIModulatedService:
    """
    Factory function to create OpenAI modulated service

    Args:
        context_bus: Optional context bus for integration

    Returns:
        OpenAIModulatedService instance
    """
    return OpenAIModulatedService(context_bus=context_bus)


# Convenience functions for common operations
async def simple_openai_request(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Simple OpenAI request without full service setup

    Args:
        prompt: Input prompt
        model: Model name to use

    Returns:
        Response text
    """
    service = create_openai_service()

    if not await service.initialize():
        raise RuntimeError("Failed to initialize OpenAI service")

    response = await service._process_single_model(prompt, model)
    return response.response_text


async def multi_model_consensus(
    prompt: str,
    models: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get consensus from multiple models

    Args:
        prompt: Input prompt
        models: List of models to use

    Returns:
        Consensus results
    """
    service = create_openai_service()

    if not await service.initialize():
        raise RuntimeError("Failed to initialize OpenAI service")

    return await service.process_with_consensus(prompt, models)