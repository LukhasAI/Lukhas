#!/usr/bin/env python3
"""
LUKHAS O.2 Orchestration Core - API Endpoints
Production Schema v1.0.0

REST API for multi-AI orchestration with authentication,
rate limiting, and comprehensive monitoring.

Constellation Framework: Flow Star (🌊) API layer
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from identity.auth_service import verify_token
from opentelemetry import trace
from pydantic import BaseModel, Field

from governance.guardian import get_guardian
from observability import counter, histogram

from .multi_ai_router import AIProvider, ConsensusType, RoutingRequest, get_multi_ai_router

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)
security = HTTPBearer()

# Prometheus metrics
orchestration_api_requests_total = counter(
    'lukhas_orchestration_api_requests_total',
    'Total orchestration API requests',
    ['endpoint', 'status']
)

orchestration_api_latency_seconds = histogram(
    'lukhas_orchestration_api_latency_seconds',
    'Orchestration API latency',
    ['endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


class MultiAIRequest(BaseModel):
    """Multi-AI request model"""
    prompt: str = Field(..., description="The prompt to send to AI models")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    models: list[str] = Field(default_factory=list, description="Specific models to use")
    consensus_type: str = Field(default="majority", description="Consensus mechanism")
    min_responses: int = Field(default=2, description="Minimum responses required")
    max_responses: int = Field(default=3, description="Maximum responses to collect")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Request metadata")


class MultiAIResponse(BaseModel):
    """Multi-AI response model"""
    response: str
    confidence: float
    agreement_ratio: float
    participating_models: list[str]
    consensus_type: str
    latency: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class OrchestrationStatus(BaseModel):
    """Orchestration system status"""
    available_providers: list[str]
    available_models: dict[str, list[str]]
    system_health: str
    active_requests: int
    total_requests: int
    average_latency: float


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_orchestration_api_py_L82"}
    """Verify authentication token"""
    try:
        token = credentials.credentials
        payload = await verify_token(token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.post("/multi-ai", response_model=MultiAIResponse)
async def route_multi_ai(
    request: MultiAIRequest,
    current_user: dict[str, Any] = Depends(get_current_user)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_orchestration_api_py_L98"}
):
    """Route request to multiple AI models and return consensus"""

    with tracer.start_span("orchestration_api.multi_ai") as span:
        span.set_attribute("user_id", current_user.get("sub", "unknown"))
        span.set_attribute("consensus_type", request.consensus_type)
        span.set_attribute("min_responses", request.min_responses)

        import time
        start_time = time.time()

        try:
            # Validate consensus type
            try:
                consensus_type = ConsensusType(request.consensus_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid consensus type: {request.consensus_type}"
                )

            # Check with Guardian for ethical approval
            guardian = get_guardian()
            if guardian:
                approval = await guardian.validate_request_async({
                    "prompt": request.prompt,
                    "user_id": current_user.get("sub"),
                    "consensus_type": request.consensus_type,
                    "models": request.models
                })

                if not approval.get("approved", False):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Request blocked by Guardian system"
                    )

            # Create routing request
            routing_request = RoutingRequest(
                prompt=request.prompt,
                context=request.context,
                models=request.models,
                consensus_type=consensus_type,
                min_responses=request.min_responses,
                max_responses=request.max_responses,
                timeout=request.timeout,
                metadata={
                    **request.metadata,
                    "user_id": current_user.get("sub"),
                    "tenant_id": current_user.get("tenant_id", "default")
                }
            )

            # Route request
            router_instance = get_multi_ai_router()
            result = await router_instance.route_request(routing_request)

            # Calculate latency
            latency = time.time() - start_time

            # Record metrics
            orchestration_api_requests_total.labels(
                endpoint="multi_ai",
                status="success"
            ).inc()

            orchestration_api_latency_seconds.labels(
                endpoint="multi_ai"
            ).observe(latency)

            span.set_attribute("final_confidence", result.confidence)
            span.set_attribute("agreement_ratio", result.agreement_ratio)
            span.set_attribute("latency", latency)

            return MultiAIResponse(
                response=result.final_response,
                confidence=result.confidence,
                agreement_ratio=result.agreement_ratio,
                participating_models=result.participating_models,
                consensus_type=result.consensus_type.value,
                latency=latency,
                metadata=result.metadata
            )

        except HTTPException:
            orchestration_api_requests_total.labels(
                endpoint="multi_ai",
                status="client_error"
            ).inc()
            raise
        except Exception as e:
            orchestration_api_requests_total.labels(
                endpoint="multi_ai",
                status="server_error"
            ).inc()

            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            logger.error(f"Multi-AI routing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during multi-AI routing"
            )


@router.get("/status", response_model=OrchestrationStatus)
async def get_orchestration_status(
    current_user: dict[str, Any] = Depends(get_current_user)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_orchestration_api_py_L207"}
):
    """Get orchestration system status"""

    with tracer.start_span("orchestration_api.status"):
        try:
            get_multi_ai_router()

            # Collect status information
            available_providers = [provider.value for provider in AIProvider]

            available_models = {
                "openai": ["gpt-4", "gpt-3.5-turbo"],
                "anthropic": ["claude-3-sonnet", "claude-3-haiku"],
                "google": ["gemini-pro", "gemini-pro-vision"],
                "perplexity": ["pplx-7b-online", "pplx-70b-online"]
            }

            # Mock status values - in production, collect real metrics
            status_info = OrchestrationStatus(
                available_providers=available_providers,
                available_models=available_models,
                system_health="healthy",
                active_requests=0,  # Would be tracked in real implementation
                total_requests=1000,  # From metrics
                average_latency=2.5  # From metrics
            )

            orchestration_api_requests_total.labels(
                endpoint="status",
                status="success"
            ).inc()

            return status_info

        except Exception as e:
            orchestration_api_requests_total.labels(
                endpoint="status",
                status="server_error"
            ).inc()

            logger.error(f"Status check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve orchestration status"
            )


@router.get("/models")
async def list_available_models(
    current_user: dict[str, Any] = Depends(get_current_user)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_orchestration_api_py_L257"}
):
    """List all available AI models with their status"""

    with tracer.start_span("orchestration_api.list_models"):
        try:
            router_instance = get_multi_ai_router()

            models_info = []
            for _key, model in router_instance.model_selector.models.items():
                models_info.append({
                    "id": f"{model.provider.value}:{model.model_id}",
                    "provider": model.provider.value,
                    "model_id": model.model_id,
                    "available": model.available,
                    "weight": model.weight,
                    "avg_latency": model.avg_latency,
                    "success_rate": model.success_rate,
                    "cost_per_token": model.cost_per_token
                })

            orchestration_api_requests_total.labels(
                endpoint="list_models",
                status="success"
            ).inc()

            return {"models": models_info}

        except Exception as e:
            orchestration_api_requests_total.labels(
                endpoint="list_models",
                status="server_error"
            ).inc()

            logger.error(f"List models failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list available models"
            )


@router.post("/models/{model_id}/enable")
async def enable_model(
    model_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_orchestration_api_py_L301"}
):
    """Enable a specific AI model"""

    with tracer.start_span("orchestration_api.enable_model") as span:
        span.set_attribute("model_id", model_id)

        try:
            router_instance = get_multi_ai_router()

            if model_id not in router_instance.model_selector.models:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Model not found: {model_id}"
                )

            model = router_instance.model_selector.models[model_id]
            model.available = True

            # Update metrics
            from orchestration.multi_ai_router import model_availability
            model_availability.labels(
                provider=model.provider.value,
                model=model.model_id
            ).set(1)

            orchestration_api_requests_total.labels(
                endpoint="enable_model",
                status="success"
            ).inc()

            return {"message": f"Model {model_id} enabled successfully"}

        except HTTPException:
            raise
        except Exception as e:
            orchestration_api_requests_total.labels(
                endpoint="enable_model",
                status="server_error"
            ).inc()

            logger.error(f"Enable model failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to enable model"
            )


@router.post("/models/{model_id}/disable")
async def disable_model(
    model_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_orchestration_api_py_L352"}
):
    """Disable a specific AI model"""

    with tracer.start_span("orchestration_api.disable_model") as span:
        span.set_attribute("model_id", model_id)

        try:
            router_instance = get_multi_ai_router()

            if model_id not in router_instance.model_selector.models:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Model not found: {model_id}"
                )

            model = router_instance.model_selector.models[model_id]
            model.available = False

            # Update metrics
            from orchestration.multi_ai_router import model_availability
            model_availability.labels(
                provider=model.provider.value,
                model=model.model_id
            ).set(0)

            orchestration_api_requests_total.labels(
                endpoint="disable_model",
                status="success"
            ).inc()

            return {"message": f"Model {model_id} disabled successfully"}

        except HTTPException:
            raise
        except Exception as e:
            orchestration_api_requests_total.labels(
                endpoint="disable_model",
                status="server_error"
            ).inc()

            logger.error(f"Disable model failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to disable model"
            )


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for orchestration service"""

    with tracer.start_span("orchestration_api.health_check"):
        try:
            # Basic health checks
            router_instance = get_multi_ai_router()

            # Check if we have available models
            available_count = sum(
                1 for model in router_instance.model_selector.models.values()
                if model.available
            )

            if available_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No AI models available"
                )

            orchestration_api_requests_total.labels(
                endpoint="health_check",
                status="success"
            ).inc()

            return {
                "status": "healthy",
                "available_models": available_count,
                "timestamp": time.time()  # TODO: time
            }

        except HTTPException:
            orchestration_api_requests_total.labels(
                endpoint="health_check",
                status="service_unavailable"
            ).inc()
            raise
        except Exception as e:
            orchestration_api_requests_total.labels(
                endpoint="health_check",
                status="server_error"
            ).inc()

            logger.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Health check failed"
            )
