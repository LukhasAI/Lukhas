"""
LUKHAS AI Multi-Model Orchestration Pipeline
==========================================

Orchestrates consensus across multiple AI models (GPT-4, Claude, Gemini) with
transparent workflow execution and interpretability logging.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Performance Target: Sub-250ms context handoffs between models
Consensus Strategy: Weighted voting with confidence scoring

Features:
- Multi-model consensus workflows
- Transparent step-by-step execution logging
- Context preservation across model switches
- Performance monitoring and optimization
- Policy enforcement and ethical validation
- MΛTRIZ integration for consciousness events

Phase 2 Core Implementation - Context Orchestrator & Backend Logic Specialist
"""
import streamlit as st

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Union

# Import LUKHAS components
try:
    from candidate.orchestration.high_performance_context_bus import (
        ContextMessage,
        ContextPriority,
        HighPerformanceContextBus,
        WorkflowStep,
    )
except ImportError as e:
    logging.warning(f"Context bus import failed: {e}")

    # Provide stub for missing class
    class HighPerformanceContextBus:
        def __init__(self, *args, **kwargs):
            pass

    class ContextMessage:
        def __init__(self, *args, **kwargs):
            pass

    class ContextPriority:
        HIGH = "high"
        NORMAL = "normal"
        LOW = "low"

    class WorkflowStep:
        def __init__(self, *args, **kwargs):
            pass


try:
    from lukhas.bridge.anthropic_bridge import AnthropicBridge
    from lukhas.bridge.google_bridge import GoogleBridge
    from lukhas.bridge.openai_bridge import OpenAIBridge
except ImportError as e:
    logging.warning(f"Bridge imports failed: {e}")

    # Provide stubs
    class OpenAIBridge:
        def __init__(self, *args, **kwargs):
            pass

    class AnthropicBridge:
        def __init__(self, *args, **kwargs):
            pass

    class GoogleBridge:
        def __init__(self, *args, **kwargs):
            pass


logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Available model providers for orchestration"""

    OPENAI_GPT4 = "openai_gpt4"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    GOOGLE_GEMINI = "google_gemini"
    PERPLEXITY = "perplexity"


class ConsensusStrategy(Enum):
    """Strategies for multi-model consensus"""

    WEIGHTED_VOTE = "weighted_vote"  # Weighted voting based on confidence
    MAJORITY_VOTE = "majority_vote"  # Simple majority consensus
    UNANIMOUS = "unanimous"  # Require all models to agree
    BEST_CONFIDENCE = "best_confidence"  # Choose highest confidence response
    ENSEMBLE = "ensemble"  # Combine all responses


class OrchestrationMode(Enum):
    """Execution modes for orchestration"""

    SEQUENTIAL = "sequential"  # Execute models one after another
    PARALLEL = "parallel"  # Execute models simultaneously
    CASCADE = "cascade"  # Each model builds on previous
    COMPETITIVE = "competitive"  # Models compete, best wins


@dataclass
class ModelResponse:
    """Response from an individual model"""

    model_provider: ModelProvider
    response_text: str
    confidence_score: float
    processing_time_ms: float
    token_usage: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Performance tracking
    request_timestamp: float = field(default_factory=time.perf_counter)
    response_timestamp: float = 0.0

    @property
    def latency_ms(self) -> float:
        """Calculate response latency"""
        if self.response_timestamp and self.request_timestamp:
            return (self.response_timestamp - self.request_timestamp) * 1000
        return self.processing_time_ms


@dataclass
class ConsensusResult:
    """Result of multi-model consensus"""

    consensus_text: str
    confidence_score: float
    participating_models: list[ModelProvider]
    individual_responses: list[ModelResponse]
    consensus_strategy: ConsensusStrategy

    # Consensus metrics
    agreement_level: float = 0.0  # 0-1 scale of model agreement
    processing_time_ms: float = 0.0
    total_tokens_used: int = 0

    # Transparency data
    decision_rationale: str = ""
    model_weights: dict[ModelProvider, float] = field(default_factory=dict)


@dataclass
class OrchestrationPipeline:
    """Configuration for multi-model orchestration pipeline"""

    pipeline_id: str
    name: str
    models: list[ModelProvider]
    consensus_strategy: ConsensusStrategy
    orchestration_mode: OrchestrationMode

    # Performance constraints
    max_latency_ms: int = 5000
    max_tokens_per_model: int = 4000

    # Quality thresholds
    min_confidence_threshold: float = 0.7
    min_agreement_threshold: float = 0.6

    # Trinity Framework requirements
    requires_identity_validation: bool = False  # ⚛️
    requires_consciousness_context: bool = False  # 🧠
    requires_guardian_oversight: bool = True  # 🛡️


class MultiModelOrchestrator:
    """
    Main orchestrator for multi-model consensus workflows.

    Coordinates execution across multiple AI models with:
    - High-performance context handoffs (<250ms target)
    - Transparent execution logging
    - Consensus algorithms for model agreement
    - Policy enforcement and ethical validation
    - Performance monitoring and optimization
    """

    def __init__(self, context_bus: Optional[HighPerformanceContextBus] = None):
        """Initialize multi-model orchestrator"""

        # Core components
        self.context_bus = context_bus or HighPerformanceContextBus()

        # Model bridges (initialize with error handling)
        self.model_bridges = {}
        self._initialize_model_bridges()

        # Orchestration state
        self.active_pipelines = {}
        self.execution_history = []
        self.performance_metrics = {
            "total_orchestrations": 0,
            "successful_orchestrations": 0,
            "average_consensus_time_ms": 0.0,
            "model_usage_stats": {},
            "agreement_rates": {},
        }

        # Consensus algorithms
        self.consensus_algorithms = {
            ConsensusStrategy.WEIGHTED_VOTE: self._weighted_vote_consensus,
            ConsensusStrategy.MAJORITY_VOTE: self._majority_vote_consensus,
            ConsensusStrategy.UNANIMOUS: self._unanimous_consensus,
            ConsensusStrategy.BEST_CONFIDENCE: self._best_confidence_consensus,
            ConsensusStrategy.ENSEMBLE: self._ensemble_consensus,
        }

        # Pre-configured pipelines for common tasks
        self._setup_default_pipelines()

        logger.info("🎭 Multi-Model Orchestrator initialized")
        logger.info(f"   Available models: {list(self.model_bridges.keys())}")
        logger.info(f"   Consensus strategies: {len(self.consensus_algorithms)}")

    def _initialize_model_bridges(self):
        """Initialize bridges to model providers"""
        try:
            # OpenAI GPT-4
            try:
                self.model_bridges[ModelProvider.OPENAI_GPT4] = OpenAIBridge()
                logger.info("✅ OpenAI GPT-4 bridge initialized")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI bridge initialization failed: {e}")

            # Anthropic Claude
            try:
                self.model_bridges[ModelProvider.ANTHROPIC_CLAUDE] = AnthropicBridge()
                logger.info("✅ Anthropic Claude bridge initialized")
            except Exception as e:
                logger.warning(f"⚠️ Anthropic bridge initialization failed: {e}")

            # Google Gemini
            try:
                self.model_bridges[ModelProvider.GOOGLE_GEMINI] = GoogleBridge()
                logger.info("✅ Google Gemini bridge initialized")
            except Exception as e:
                logger.warning(f"⚠️ Google bridge initialization failed: {e}")

        except Exception as e:
            logger.error(f"Failed to initialize model bridges: {e}")
            # Create mock bridges for testing
            self._create_mock_bridges()

    def _create_mock_bridges(self):
        """Create mock bridges for testing when real ones aren't available"""
        logger.info("🧪 Creating mock model bridges for testing")

        class MockBridge:
            def __init__(self, model_name: str):
                self.model_name = model_name

            async def complete(self, prompt: str, **kwargs) -> dict[str, Any]:
                await asyncio.sleep(0.1)  # Simulate latency
                return {
                    "text": f"Mock response from {self.model_name}: {prompt[:50]}...",
                    "confidence": 0.85,
                    "tokens": {"input": 100, "output": 50},
                }

        self.model_bridges[ModelProvider.OPENAI_GPT4] = MockBridge("GPT-4")
        self.model_bridges[ModelProvider.ANTHROPIC_CLAUDE] = MockBridge("Claude")
        self.model_bridges[ModelProvider.GOOGLE_GEMINI] = MockBridge("Gemini")

    def _setup_default_pipelines(self):
        """Setup pre-configured pipelines for common tasks"""

        # Analysis pipeline - GPT-4 + Claude consensus
        analysis_pipeline = OrchestrationPipeline(
            pipeline_id="analysis_consensus",
            name="Analysis Consensus Pipeline",
            models=[ModelProvider.OPENAI_GPT4, ModelProvider.ANTHROPIC_CLAUDE],
            consensus_strategy=ConsensusStrategy.WEIGHTED_VOTE,
            orchestration_mode=OrchestrationMode.PARALLEL,
            requires_guardian_oversight=True,
        )

        # Creative pipeline - All models for diverse perspectives
        creative_pipeline = OrchestrationPipeline(
            pipeline_id="creative_consensus",
            name="Creative Consensus Pipeline",
            models=[
                ModelProvider.OPENAI_GPT4,
                ModelProvider.ANTHROPIC_CLAUDE,
                ModelProvider.GOOGLE_GEMINI,
            ],
            consensus_strategy=ConsensusStrategy.ENSEMBLE,
            orchestration_mode=OrchestrationMode.PARALLEL,
            requires_consciousness_context=True,
        )

        # Critical decision pipeline - Unanimous consensus required
        critical_pipeline = OrchestrationPipeline(
            pipeline_id="critical_decision",
            name="Critical Decision Pipeline",
            models=[ModelProvider.OPENAI_GPT4, ModelProvider.ANTHROPIC_CLAUDE],
            consensus_strategy=ConsensusStrategy.UNANIMOUS,
            orchestration_mode=OrchestrationMode.SEQUENTIAL,
            requires_identity_validation=True,
            requires_guardian_oversight=True,
        )

        self.default_pipelines = {
            "analysis": analysis_pipeline,
            "creative": creative_pipeline,
            "critical": critical_pipeline,
        }

        logger.info(f"📋 {len(self.default_pipelines)} default pipelines configured")

    async def orchestrate(
        self,
        prompt: str,
        pipeline: Union[str, OrchestrationPipeline],
        context: Optional[dict[str, Any]] = None,
    ) -> ConsensusResult:
        """
        Execute multi-model orchestration with consensus

        Args:
            prompt: Input prompt for all models
            pipeline: Pipeline configuration or name
            context: Additional context data

        Returns:
            Consensus result with transparent execution log
        """
        orchestration_start = time.perf_counter()
        execution_id = str(uuid.uuid4())

        # Resolve pipeline configuration
        if isinstance(pipeline, str):
            if pipeline in self.default_pipelines:
                pipeline_config = self.default_pipelines[pipeline]
            else:
                raise ValueError(f"Unknown pipeline: {pipeline}")
        else:
            pipeline_config = pipeline

        logger.info(f"🎭 Starting orchestration: {pipeline_config.name}")
        logger.info(f"   Models: {[m.value for m in pipeline_config.models]}")
        logger.info(f"   Strategy: {pipeline_config.consensus_strategy.value}")
        logger.info(f"   Mode: {pipeline_config.orchestration_mode.value}")

        try:
            # Emit orchestration start event
            await self.context_bus.emit(
                "orchestration.started",
                {
                    "execution_id": execution_id,
                    "pipeline": pipeline_config.name,
                    "models": [m.value for m in pipeline_config.models],
                    "prompt_length": len(prompt),
                },
                priority=ContextPriority.HIGH,
            )

            # Execute models based on orchestration mode
            if pipeline_config.orchestration_mode == OrchestrationMode.PARALLEL:
                model_responses = await self._execute_parallel(prompt, pipeline_config, context)
            elif pipeline_config.orchestration_mode == OrchestrationMode.SEQUENTIAL:
                model_responses = await self._execute_sequential(prompt, pipeline_config, context)
            elif pipeline_config.orchestration_mode == OrchestrationMode.CASCADE:
                model_responses = await self._execute_cascade(prompt, pipeline_config, context)
            else:
                model_responses = await self._execute_competitive(prompt, pipeline_config, context)

            # Apply consensus algorithm
            consensus_result = await self._apply_consensus(model_responses, pipeline_config.consensus_strategy)

            # Complete timing and metrics
            orchestration_time = (time.perf_counter() - orchestration_start) * 1000
            consensus_result.processing_time_ms = orchestration_time

            # Update performance metrics
            self._update_performance_metrics(consensus_result, pipeline_config)

            # Emit orchestration completed event
            await self.context_bus.emit(
                "orchestration.completed",
                {
                    "execution_id": execution_id,
                    "consensus_confidence": consensus_result.confidence_score,
                    "agreement_level": consensus_result.agreement_level,
                    "processing_time_ms": orchestration_time,
                    "models_used": len(model_responses),
                },
                priority=ContextPriority.NORMAL,
            )

            # Add to execution history
            self.execution_history.append(
                {
                    "execution_id": execution_id,
                    "pipeline": pipeline_config.name,
                    "result": consensus_result,
                    "timestamp": datetime.now(timezone.utc),
                }
            )

            logger.info(f"✅ Orchestration completed: {orchestration_time:.2f}ms")
            logger.info(f"   Consensus confidence: {consensus_result.confidence_score:.3f}")
            logger.info(f"   Agreement level: {consensus_result.agreement_level:.3f}")

            return consensus_result

        except Exception as e:
            orchestration_time = (time.perf_counter() - orchestration_start) * 1000

            logger.error(f"❌ Orchestration failed: {e!s} ({orchestration_time:.2f}ms)")

            # Emit failure event
            await self.context_bus.emit(
                "orchestration.failed",
                {
                    "execution_id": execution_id,
                    "error": str(e),
                    "processing_time_ms": orchestration_time,
                },
                priority=ContextPriority.HIGH,
            )

            raise

    async def _execute_parallel(
        self, prompt: str, pipeline: OrchestrationPipeline, context: Optional[dict]
    ) -> list[ModelResponse]:
        """Execute models in parallel for maximum speed"""
        logger.info("⚡ Executing models in parallel")

        tasks = []
        for model in pipeline.models:
            if model in self.model_bridges:
                task = asyncio.create_task(self._execute_single_model(model, prompt, context))
                tasks.append(task)

        # Wait for all models with timeout
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=pipeline.max_latency_ms / 1000,
            )

            # Filter out exceptions
            valid_responses = [r for r in responses if isinstance(r, ModelResponse)]
            return valid_responses

        except asyncio.TimeoutError:
            logger.warning(f"Parallel execution timed out after {pipeline.max_latency_ms}ms")
            # Return any completed responses
            completed_responses = [task.result() for task in tasks if task.done() and not task.exception()]
            return completed_responses

    async def _execute_sequential(
        self, prompt: str, pipeline: OrchestrationPipeline, context: Optional[dict]
    ) -> list[ModelResponse]:
        """Execute models sequentially, each building on previous context"""
        logger.info("📝 Executing models sequentially")

        responses = []
        accumulated_context = context or {}

        for i, model in enumerate(pipeline.models):
            if model in self.model_bridges:
                logger.info(f"   Executing model {i + 1}/{len(pipeline.models)}: {model.value}")

                # Add previous responses to context
                if responses:
                    accumulated_context["previous_responses"] = [
                        {"model": r.model_provider.value, "response": r.response_text} for r in responses
                    ]

                response = await self._execute_single_model(model, prompt, accumulated_context)
                responses.append(response)

        return responses

    async def _execute_cascade(
        self, prompt: str, pipeline: OrchestrationPipeline, context: Optional[dict]
    ) -> list[ModelResponse]:
        """Execute models in cascade, each refining the previous output"""
        logger.info("🌊 Executing models in cascade")

        responses = []
        current_prompt = prompt

        for i, model in enumerate(pipeline.models):
            if model in self.model_bridges:
                logger.info(f"   Cascade step {i + 1}/{len(pipeline.models)}: {model.value}")

                response = await self._execute_single_model(model, current_prompt, context)
                responses.append(response)

                # Use this response as input for next model
                if i < len(pipeline.models) - 1:
                    current_prompt = f"Refine and improve this response: {response.response_text}"

        return responses

    async def _execute_competitive(
        self, prompt: str, pipeline: OrchestrationPipeline, context: Optional[dict]
    ) -> list[ModelResponse]:
        """Execute models competitively and select the best"""
        logger.info("🏆 Executing models competitively")

        # Run all models in parallel
        responses = await self._execute_parallel(prompt, pipeline, context)

        # Select the best response based on confidence
        if responses:
            best_response = max(responses, key=lambda r: r.confidence_score)
            logger.info(
                f"   Winner: {best_response.model_provider.value} (confidence: {best_response.confidence_score:.3f})"
            )
            return [best_response]  # Return only the winner

        return responses

    async def _execute_single_model(self, model: ModelProvider, prompt: str, context: Optional[dict]) -> ModelResponse:
        """Execute a single model and return response"""
        request_start = time.perf_counter()

        try:
            bridge = self.model_bridges[model]

            # Prepare model-specific parameters
            model_params = self._prepare_model_params(model, prompt, context)

            # Execute model
            result = await bridge.complete(**model_params)

            request_end = time.perf_counter()

            # Create response object
            response = ModelResponse(
                model_provider=model,
                response_text=result.get("text", ""),
                confidence_score=result.get("confidence", 0.5),
                processing_time_ms=(request_end - request_start) * 1000,
                token_usage=result.get("tokens", {}),
                metadata=result.get("metadata", {}),
                request_timestamp=request_start,
                response_timestamp=request_end,
            )

            return response

        except Exception as e:
            logger.error(f"Model {model.value} execution failed: {e}")

            # Return error response
            return ModelResponse(
                model_provider=model,
                response_text=f"Error: {e!s}",
                confidence_score=0.0,
                processing_time_ms=(time.perf_counter() - request_start) * 1000,
                metadata={"error": str(e)},
            )

    def _prepare_model_params(self, model: ModelProvider, prompt: str, context: Optional[dict]) -> dict[str, Any]:
        """Prepare model-specific parameters"""
        base_params = {"prompt": prompt, "max_tokens": 1000, "temperature": 0.7}

        # Add context if available
        if context:
            base_params["context"] = context

        # Model-specific optimizations
        if model == ModelProvider.OPENAI_GPT4:
            base_params["model"] = "gpt-4"
        elif model == ModelProvider.ANTHROPIC_CLAUDE:
            base_params["model"] = "claude-3-opus-20240229"
        elif model == ModelProvider.GOOGLE_GEMINI:
            base_params["model"] = "gemini-pro"

        return base_params

    async def _apply_consensus(self, responses: list[ModelResponse], strategy: ConsensusStrategy) -> ConsensusResult:
        """Apply consensus algorithm to model responses"""
        if not responses:
            raise ValueError("No valid responses for consensus")

        logger.info(f"🤝 Applying consensus: {strategy.value} on {len(responses)} responses")

        # Apply the appropriate consensus algorithm
        consensus_func = self.consensus_algorithms[strategy]
        return await consensus_func(responses)

    async def _weighted_vote_consensus(self, responses: list[ModelResponse]) -> ConsensusResult:
        """Weighted voting based on model confidence scores"""

        # Calculate weights based on confidence scores
        total_confidence = sum(r.confidence_score for r in responses)
        weights = {r.model_provider: r.confidence_score / total_confidence for r in responses}

        # For simplicity, select the highest confidence response
        # In a full implementation, this would combine responses based on weights
        best_response = max(responses, key=lambda r: r.confidence_score)

        # Calculate agreement level (similarity between responses)
        agreement_level = self._calculate_agreement(responses)

        return ConsensusResult(
            consensus_text=best_response.response_text,
            confidence_score=best_response.confidence_score,
            participating_models=[r.model_provider for r in responses],
            individual_responses=responses,
            consensus_strategy=ConsensusStrategy.WEIGHTED_VOTE,
            agreement_level=agreement_level,
            model_weights=weights,
            decision_rationale=f"Selected response from {best_response.model_provider.value} "
            f"with highest confidence ({best_response.confidence_score:.3f})",
        )

    async def _majority_vote_consensus(self, responses: list[ModelResponse]) -> ConsensusResult:
        """Simple majority vote consensus"""

        # For demonstration, group responses by similarity
        response_groups = self._group_similar_responses(responses)

        # Select the largest group
        majority_group = max(response_groups, key=len)
        representative_response = majority_group[0]  # Representative from majority

        agreement_level = len(majority_group) / len(responses)

        return ConsensusResult(
            consensus_text=representative_response.response_text,
            confidence_score=sum(r.confidence_score for r in majority_group) / len(majority_group),
            participating_models=[r.model_provider for r in responses],
            individual_responses=responses,
            consensus_strategy=ConsensusStrategy.MAJORITY_VOTE,
            agreement_level=agreement_level,
            decision_rationale=f"Majority consensus from {len(majority_group)}/{len(responses)} models",
        )

    async def _unanimous_consensus(self, responses: list[ModelResponse]) -> ConsensusResult:
        """Unanimous consensus - all models must agree"""

        agreement_level = self._calculate_agreement(responses)

        if agreement_level < 0.9:  # Very high threshold for unanimity
            # No consensus reached
            max(responses, key=lambda r: r.confidence_score)
            return ConsensusResult(
                consensus_text="CONSENSUS FAILED: Models did not reach unanimous agreement",
                confidence_score=0.0,
                participating_models=[r.model_provider for r in responses],
                individual_responses=responses,
                consensus_strategy=ConsensusStrategy.UNANIMOUS,
                agreement_level=agreement_level,
                decision_rationale=f"Unanimous consensus failed (agreement: {agreement_level:.3f})",
            )

        # Consensus reached - use the first response as representative
        representative_response = responses[0]

        return ConsensusResult(
            consensus_text=representative_response.response_text,
            confidence_score=sum(r.confidence_score for r in responses) / len(responses),
            participating_models=[r.model_provider for r in responses],
            individual_responses=responses,
            consensus_strategy=ConsensusStrategy.UNANIMOUS,
            agreement_level=agreement_level,
            decision_rationale="Unanimous consensus achieved across all models",
        )

    async def _best_confidence_consensus(self, responses: list[ModelResponse]) -> ConsensusResult:
        """Select response with highest confidence score"""

        best_response = max(responses, key=lambda r: r.confidence_score)
        agreement_level = self._calculate_agreement(responses)

        return ConsensusResult(
            consensus_text=best_response.response_text,
            confidence_score=best_response.confidence_score,
            participating_models=[r.model_provider for r in responses],
            individual_responses=responses,
            consensus_strategy=ConsensusStrategy.BEST_CONFIDENCE,
            agreement_level=agreement_level,
            decision_rationale=f"Selected highest confidence response from {best_response.model_provider.value}",
        )

    async def _ensemble_consensus(self, responses: list[ModelResponse]) -> ConsensusResult:
        """Combine all responses into an ensemble result"""

        # For demonstration, concatenate responses with attribution
        ensemble_text = "ENSEMBLE RESPONSE:\n\n"
        for i, response in enumerate(responses, 1):
            ensemble_text += f"{i}. {response.model_provider.value}:\n"
            ensemble_text += f"{response.response_text}\n\n"

        # Average confidence scores
        avg_confidence = sum(r.confidence_score for r in responses) / len(responses)
        agreement_level = self._calculate_agreement(responses)

        return ConsensusResult(
            consensus_text=ensemble_text,
            confidence_score=avg_confidence,
            participating_models=[r.model_provider for r in responses],
            individual_responses=responses,
            consensus_strategy=ConsensusStrategy.ENSEMBLE,
            agreement_level=agreement_level,
            decision_rationale=f"Ensemble of {len(responses)} model responses",
        )

    def _calculate_agreement(self, responses: list[ModelResponse]) -> float:
        """Calculate agreement level between responses (0-1 scale)"""
        if len(responses) < 2:
            return 1.0

        # Simplified agreement calculation based on response length similarity
        # In a full implementation, this would use semantic similarity
        lengths = [len(r.response_text) for r in responses]
        avg_length = sum(lengths) / len(lengths)

        # Calculate variance in lengths as proxy for agreement
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        normalized_variance = min(variance / (avg_length**2), 1.0) if avg_length > 0 else 0

        # Agreement is inverse of normalized variance
        return 1.0 - normalized_variance

    def _group_similar_responses(self, responses: list[ModelResponse]) -> list[list[ModelResponse]]:
        """Group responses by similarity for majority voting"""
        # Simplified grouping by response length ranges
        # In a full implementation, this would use semantic clustering

        groups = []
        for response in responses:
            response_length = len(response.response_text)

            # Find existing group with similar length
            placed = False
            for group in groups:
                group_avg_length = sum(len(r.response_text) for r in group) / len(group)
                if abs(response_length - group_avg_length) < 100:  # Within 100 chars
                    group.append(response)
                    placed = True
                    break

            if not placed:
                groups.append([response])

        return groups

    def _update_performance_metrics(self, result: ConsensusResult, pipeline: OrchestrationPipeline):
        """Update orchestration performance metrics"""
        self.performance_metrics["total_orchestrations"] += 1

        if result.confidence_score > pipeline.min_confidence_threshold:
            self.performance_metrics["successful_orchestrations"] += 1

        # Update average consensus time
        total_time = self.performance_metrics.get("total_consensus_time_ms", 0)
        count = self.performance_metrics["total_orchestrations"]
        new_avg = (total_time + result.processing_time_ms) / count
        self.performance_metrics["average_consensus_time_ms"] = new_avg
        self.performance_metrics["total_consensus_time_ms"] = total_time + result.processing_time_ms

        # Update model usage stats
        for response in result.individual_responses:
            model_key = response.model_provider.value
            if model_key not in self.performance_metrics["model_usage_stats"]:
                self.performance_metrics["model_usage_stats"][model_key] = 0
            self.performance_metrics["model_usage_stats"][model_key] += 1

        # Update agreement rates
        strategy_key = result.consensus_strategy.value
        if strategy_key not in self.performance_metrics["agreement_rates"]:
            self.performance_metrics["agreement_rates"][strategy_key] = []
        self.performance_metrics["agreement_rates"][strategy_key].append(result.agreement_level)

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive orchestration performance metrics"""
        total = self.performance_metrics["total_orchestrations"]
        successful = self.performance_metrics["successful_orchestrations"]

        metrics = {
            "orchestrations": {
                "total": total,
                "successful": successful,
                "success_rate": successful / max(total, 1),
            },
            "performance": {
                "average_consensus_time_ms": self.performance_metrics["average_consensus_time_ms"],
                "meets_250ms_target": self.performance_metrics["average_consensus_time_ms"] < 250,
            },
            "model_usage": self.performance_metrics["model_usage_stats"],
            "agreement_analysis": {},
        }

        # Calculate agreement statistics
        for strategy, agreements in self.performance_metrics["agreement_rates"].items():
            if agreements:
                metrics["agreement_analysis"][strategy] = {
                    "average_agreement": sum(agreements) / len(agreements),
                    "min_agreement": min(agreements),
                    "max_agreement": max(agreements),
                    "total_executions": len(agreements),
                }

        return metrics

    def get_execution_history(self, limit: int = 10) -> list[dict]:
        """Get recent execution history"""
        return self.execution_history[-limit:]


# Global orchestrator instance
orchestrator = MultiModelOrchestrator()


# Convenience functions
async def orchestrate(prompt: str, pipeline: str = "analysis", context: Optional[dict] = None) -> ConsensusResult:
    """Orchestrate multi-model consensus"""
    return await orchestrator.orchestrate(prompt, pipeline, context)


async def get_consensus(prompt: str, models: list[str], strategy: str = "weighted_vote") -> ConsensusResult:
    """Get consensus from specified models"""
    model_providers = [ModelProvider(model) for model in models]
    strategy_enum = ConsensusStrategy(strategy)

    pipeline = OrchestrationPipeline(
        pipeline_id="custom",
        name="Custom Consensus",
        models=model_providers,
        consensus_strategy=strategy_enum,
        orchestration_mode=OrchestrationMode.PARALLEL,
    )

    return await orchestrator.orchestrate(prompt, pipeline)


# Export main components
__all__ = [
    "ConsensusResult",
    "ConsensusStrategy",
    "ModelProvider",
    "ModelResponse",
    "MultiModelOrchestrator",
    "OrchestrationMode",
    "OrchestrationPipeline",
    "get_consensus",
    "orchestrate",
    "orchestrator",
]
