"""
FastAPI routes for LUKHAS AI multi-AI orchestration system integration
=====================================================================

New orchestration endpoints that integrate with the existing API server
to provide multi-AI capabilities with consensus and context preservation.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import contextlib
import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import the orchestration components
try:
    # Optional: available when orchestration suite is installed
    from bridge.orchestration.multi_ai_orchestrator import (
        AIProvider,
        MultiAIOrchestrator,
        OrchestrationRequest,
        TaskType,
    )

    ORCHESTRATION_AVAILABLE = True
except ImportError as e:
    logging.warning("Orchestration components not available: %s", e)
    ORCHESTRATION_AVAILABLE = False

    # Create stub classes for graceful degradation
    class MultiAIOrchestrator:
        def __init__(self, **_kwargs):
            self.providers = []

        async def execute_consensus(self, _prompt: str, **_kwargs):
            return {
                "response": "Multi-AI orchestration not configured",
                "confidence": 0.5,
                "providers": [],
                "latency_ms": 0,
                "consensus_method": "unavailable",
            }

    # Minimal fallbacks for type-like usage
    class _EnumStr(str):
        def __new__(cls, value: str):
            return str.__new__(cls, value)

        @property
        def value(self) -> str:  # parity with Enum.value
            return str(self)

    class AIProvider(_EnumStr):
        OPENAI = _EnumStr("openai")
        ANTHROPIC = _EnumStr("anthropic")
        GEMINI = _EnumStr("gemini")
        PERPLEXITY = _EnumStr("perplexity")

    class TaskType(_EnumStr):
        CONVERSATION = _EnumStr("conversation")

    class OrchestrationRequest:  # stub for construction only
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orchestration", tags=["Multi-AI Orchestration"])


class MultiAIRequest(BaseModel):
    """Multi-AI orchestration request model"""

    message: str
    task_type: str = "conversation"
    providers: Optional[list[str]] = None
    consensus_required: bool = True
    max_latency_ms: float = 5000
    context_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class MultiAIResponse(BaseModel):
    """Multi-AI orchestration response model"""

    response: str
    confidence: float
    latency_ms: float
    providers_used: list[str]
    consensus_method: str
    participating_models: int
    context_id: Optional[str] = None
    performance_metrics: Optional[dict[str, Any]] = None


class ProviderResponse(BaseModel):
    """Individual provider response model"""

    provider: str
    content: str
    confidence: float
    latency_ms: float


class OrchestrationStatus(BaseModel):
    """Orchestration system status model"""

    status: str
    available_providers: list[str]
    performance_metrics: dict[str, Any]
    context_manager_health: dict[str, Any]


# Global orchestrator instance
_orchestrator: Optional[MultiAIOrchestrator] = None


def get_orchestrator() -> MultiAIOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator

    if not ORCHESTRATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Multi-AI orchestration not available - missing dependencies")

    if _orchestrator is None:
        try:
            _orchestrator = MultiAIOrchestrator()
            logger.info("Multi-AI Orchestrator initialized")
        except Exception as e:
            logger.error("Failed to initialize orchestrator: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Failed to initialize orchestrator: {e!s}") from e

    return _orchestrator


@router.post("/chat", response_model=MultiAIResponse)
async def multi_ai_chat(request: MultiAIRequest):
    """
    Multi-AI chat with consensus orchestration

    This endpoint orchestrates multiple AI models to provide a consensus response
    with improved accuracy and reliability compared to single-model responses.
    """
    try:
        orchestrator = get_orchestrator()

        # Convert string providers to AIProvider enums
        providers = []
        if request.providers:
            valid = {p.value for p in AIProvider}
            for provider_name in request.providers:
                name = provider_name.lower()
                if name in valid:
                    providers.append(AIProvider(name))
                else:
                    logger.warning("Unknown provider: %s", provider_name)

        # Convert task type
        try:
            task_type = TaskType(request.task_type.lower())
        except ValueError:
            task_type = TaskType.CONVERSATION

        # Create orchestration request
        orchestration_request = OrchestrationRequest(
            prompt=request.message,
            task_type=task_type,
            providers=providers,
            consensus_required=request.consensus_required,
            max_latency_ms=request.max_latency_ms,
            context_id=request.context_id,
            metadata=request.metadata or {},
        )

        # Execute orchestration
        consensus_result = await orchestrator.orchestrate(orchestration_request)

        # Get performance metrics
        performance_metrics = await orchestrator.performance_monitor.get_metrics()

        # Build response
        response = MultiAIResponse(
            response=consensus_result.final_response,
            confidence=consensus_result.confidence_score,
            latency_ms=consensus_result.processing_time_ms,
            providers_used=[r.provider.value for r in consensus_result.individual_responses],
            consensus_method=consensus_result.consensus_method,
            participating_models=consensus_result.participating_models,
            context_id=request.context_id,
            performance_metrics=performance_metrics,
        )

        logger.info(
            "Multi-AI chat completed: %.2fms, confidence: %.3f",
            consensus_result.processing_time_ms,
            consensus_result.confidence_score,
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Multi-AI chat failed: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {e!s}") from e


@router.post("/compare", response_model=dict[str, Any])
async def compare_providers(request: MultiAIRequest):
    """
    Compare responses from multiple AI providers

    Returns individual responses from each provider for comparison,
    along with a consensus result.
    """
    try:
        orchestrator = get_orchestrator()

        # Convert providers and task type
        providers = []
        if request.providers:
            for provider_name in request.providers:
                with contextlib.suppress(ValueError):
                    providers.append(AIProvider(provider_name.lower()))
        else:
            # Use all available providers for comparison
            providers = [
                AIProvider.OPENAI,
                AIProvider.ANTHROPIC,
                AIProvider.GEMINI,
                AIProvider.PERPLEXITY,
            ]

        try:
            task_type = TaskType(request.task_type.lower())
        except ValueError:
            task_type = TaskType.CONVERSATION

        # Create orchestration request
        orchestration_request = OrchestrationRequest(
            prompt=request.message,
            task_type=task_type,
            providers=providers,
            consensus_required=True,
            max_latency_ms=request.max_latency_ms,
            parallel_execution=True,  # Force parallel for fair comparison
            context_id=request.context_id,
            metadata=request.metadata or {},
        )

        # Execute orchestration
        consensus_result = await orchestrator.orchestrate(orchestration_request)

        # Build individual responses
        individual_responses = [
            ProviderResponse(
                provider=response.provider.value,
                content=response.content,
                confidence=response.confidence,
                latency_ms=response.latency_ms,
            )
            for response in consensus_result.individual_responses
        ]

        return {
            "consensus": {
                "response": consensus_result.final_response,
                "confidence": consensus_result.confidence_score,
                "method": consensus_result.consensus_method,
                "processing_time_ms": consensus_result.processing_time_ms,
            },
            "individual_responses": [r.dict() for r in individual_responses],
            "quality_metrics": consensus_result.quality_metrics,
            "similarity_analysis": consensus_result.similarity_matrix,
        }

    except Exception as e:
        logger.error("Provider comparison failed: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Comparison failed: {e!s}") from e


@router.get("/status", response_model=OrchestrationStatus)
async def orchestration_status():
    """
    Get orchestration system status and health metrics

    Returns information about available providers, performance metrics,
    and system health indicators.
    """
    try:
        if not ORCHESTRATION_AVAILABLE:
            return OrchestrationStatus(
                status="unavailable",
                available_providers=[],
                performance_metrics={},
                context_manager_health={"status": "unavailable"},
            )

        orchestrator = get_orchestrator()

        # Get system status
        system_status = await orchestrator.get_status()

        # Get performance metrics
        performance_metrics = await orchestrator.performance_monitor.get_metrics()

        # Get context manager health
        context_health = await orchestrator.context_manager.health_check()

        return OrchestrationStatus(
            status=system_status.get("status", "unknown"),
            available_providers=system_status.get("available_providers", []),
            performance_metrics=performance_metrics,
            context_manager_health=context_health,
        )

    except Exception as e:
        logger.error("Status check failed: %s", str(e))
        return OrchestrationStatus(
            status="error",
            available_providers=[],
            performance_metrics={"error": str(e)},
            context_manager_health={"status": "error", "error": str(e)},
        )


@router.get("/health")
async def health_check():
    """
    Comprehensive health check for the orchestration system

    Returns detailed health information for all orchestration components.
    """
    try:
        if not ORCHESTRATION_AVAILABLE:
            return {
                "status": "unavailable",
                "message": "Multi-AI orchestration not available",
                "components": {
                    "orchestrator": {"status": "unavailable"},
                    "consensus_engine": {"status": "unavailable"},
                    "context_manager": {"status": "unavailable"},
                    "performance_monitor": {"status": "unavailable"},
                },
            }

        orchestrator = get_orchestrator()

        # Comprehensive health check
        health_status = await orchestrator.health_check()

        return {
            "status": "healthy" if health_status.get("orchestrator") == "healthy" else "degraded",
            "timestamp": health_status.get("timestamp"),
            "components": health_status,
        }

    except Exception as e:
        logger.error("Health check failed: %s", str(e))
        return {"status": "unhealthy", "error": str(e), "components": {}


@router.post("/providers/{provider}/direct")
async def direct_provider_chat(provider: str, request: MultiAIRequest):
    """
    Direct chat with a specific AI provider

    Bypasses consensus orchestration and queries a single provider directly.
    Useful for testing individual provider capabilities.
    """
    try:
        orchestrator = get_orchestrator()

        # Validate provider
        try:
            ai_provider = AIProvider(provider.lower())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}") from e

        # Create single-provider request
        orchestration_request = OrchestrationRequest(
            prompt=request.message,
            task_type=TaskType(request.task_type.lower()) if request.task_type else TaskType.CONVERSATION,
            providers=[ai_provider],
            consensus_required=False,
            max_latency_ms=request.max_latency_ms,
            context_id=request.context_id,
            metadata=request.metadata or {},
        )

        # Execute single provider
        result = await orchestrator.orchestrate(orchestration_request)

        return {
            "provider": provider,
            "response": result.final_response,
            "confidence": result.confidence_score,
            "latency_ms": result.processing_time_ms,
            "metadata": {
                "consensus_method": result.consensus_method,
                "processing_details": result.individual_responses[0].__dict__ if result.individual_responses else {},
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Direct provider chat failed: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Provider {provider} failed: {e!s}") from e


@router.get("/metrics")
async def get_metrics():
    """
    Get detailed performance metrics for the orchestration system

    Returns comprehensive metrics including latency, throughput, provider performance,
    consensus accuracy, and context management statistics.
    """
    try:
        if not ORCHESTRATION_AVAILABLE:
            return {"error": "Orchestration not available"}

        orchestrator = get_orchestrator()

        # Get comprehensive metrics
        performance_metrics = await orchestrator.performance_monitor.get_metrics()
        context_metrics = await orchestrator.context_manager.get_performance_metrics()
        consensus_metrics = await orchestrator.consensus_engine.health_check()

        return {
            "performance": performance_metrics,
            "context_management": context_metrics,
            "consensus_engine": consensus_metrics,
            "system_info": {
                "orchestration_available": True,
                "active_contexts": await orchestrator.context_manager.get_active_context_count(),
                "uptime": "runtime_dependent",
            },
        }

    except Exception as e:
        logger.error("Metrics collection failed: %s", str(e))
        return {"error": str(e)}


# Legacy compatibility endpoints for existing API consumers
@router.post("/ai-chat", response_model=MultiAIResponse)
async def legacy_ai_chat(request: MultiAIRequest):
    """Legacy endpoint for backward compatibility"""
    return await multi_ai_chat(request)


@router.get("/ai-status")
async def legacy_ai_status():
    """Legacy status endpoint for backward compatibility"""
    status = await orchestration_status()
    return status.dict()