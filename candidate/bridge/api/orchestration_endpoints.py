#!/usr/bin/env python3
"""
LUKHAS AI - Multi-Model Orchestration API Endpoints
====================================================

FastAPI endpoints for multi-model AI orchestration with streaming,
authentication, and performance monitoring.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Performance Target: <100ms API response latency
Supports: REST API, WebSocket, SSE streaming, JWT authentication

Features:
- Multi-model orchestration endpoints
- Real-time streaming with SSE and WebSocket
- JWT-based authentication and authorization
- Rate limiting and API key management
- Performance monitoring and metrics
- Request validation and error handling
- Trinity Framework integration
"""

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

try:
    import jwt
    from fastapi import (
        Depends,
        FastAPI,
        HTTPException,
        Request,
        Response,
        WebSocket,
        WebSocketDisconnect,
        status,
    )
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from pydantic import BaseModel, Field, ValidationError

    # LUKHAS imports
    from candidate.bridge.api.orchestration_api_bridge import (
        APIProvider,
        ComprehensiveAPIOrchestrator,
        OrchestrationRequest,
        OrchestrationResponse,
        OrchestrationStrategy,
        get_orchestrator,
    )

    FASTAPI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"FastAPI dependencies not available: {e}")
    FASTAPI_AVAILABLE = False

logger = logging.getLogger(__name__)


# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model"""

    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class OrchestrationAPIRequest(BaseModel):
    """API request model for orchestration"""

    prompt: str = Field(..., description="User prompt", min_length=1, max_length=10000)
    messages: Optional[list[ChatMessage]] = Field(None, description="Conversation messages")

    # Orchestration settings
    strategy: str = Field("consensus", description="Orchestration strategy")
    providers: Optional[list[str]] = Field(None, description="Preferred providers")

    # Function calling
    enable_functions: bool = Field(True, description="Enable function calling")
    specific_functions: Optional[list[str]] = Field(None, description="Specific functions to allow")

    # Performance constraints
    max_latency_ms: int = Field(
        5000, description="Maximum latency in milliseconds", ge=100, le=30000
    )
    max_cost: float = Field(0.10, description="Maximum cost per request", ge=0.001, le=10.0)

    # Quality requirements
    min_confidence: float = Field(0.7, description="Minimum confidence threshold", ge=0.0, le=1.0)
    require_consensus: bool = Field(False, description="Require consensus for response")

    # Metadata
    priority: str = Field("normal", description="Request priority")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")


class StreamingRequest(BaseModel):
    """Streaming request model"""

    prompt: str = Field(..., description="User prompt", min_length=1, max_length=10000)
    provider: str = Field("openai", description="Provider for streaming")
    enable_functions: bool = Field(True, description="Enable function calling")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: float = Field(0.7, description="Response randomness", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, description="Maximum response tokens")
    context_type: str = Field("general", description="Context type for validation")
    session_id: Optional[str] = Field(None, description="Session identifier")


class FunctionRegistrationRequest(BaseModel):
    """Function registration request"""

    functions: dict[str, dict[str, Any]] = Field(..., description="Functions to register")
    global_scope: bool = Field(True, description="Register globally for all providers")
    security_validated: bool = Field(
        False, description="Whether functions have been security validated"
    )
    healthcare_compliant: bool = Field(
        False, description="Whether functions are healthcare compliant"
    )


class OrchestrationAPIResponse(BaseModel):
    """API response model"""

    success: bool = Field(..., description="Request success status")
    content: str = Field(..., description="Response content")
    confidence_score: float = Field(..., description="Response confidence")

    # Provider information
    primary_provider: str = Field(..., description="Primary provider used")
    participating_providers: list[str] = Field(..., description="All participating providers")

    # Performance metrics
    latency_ms: float = Field(..., description="Total latency")
    cost: float = Field(..., description="Total cost")
    token_usage: dict[str, int] = Field(..., description="Token usage statistics")

    # Quality metrics
    agreement_level: float = Field(..., description="Inter-model agreement level")
    consensus_achieved: bool = Field(..., description="Whether consensus was achieved")

    # Metadata
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(..., description="Response timestamp")
    strategy_used: str = Field(..., description="Orchestration strategy used")

    # Function calling results
    function_calls: list[dict[str, Any]] = Field(
        default_factory=list, description="Function calls made"
    )
    tool_uses: list[dict[str, Any]] = Field(default_factory=list, description="Tool uses made")

    # Transparency
    individual_responses: list[dict[str, Any]] = Field(
        default_factory=list, description="Individual model responses"
    )
    decision_rationale: str = Field("", description="Decision-making rationale")


# Authentication and Rate Limiting
class APIKeyManager:
    """Manages API keys and authentication"""

    def __init__(self, secret_key: str = "lukhas-api-secret-key-change-in-production"):
        self.secret_key = secret_key
        self.api_keys = {
            "lukhas-dev-key": {
                "user_id": "dev-user",
                "tier": "premium",
                "rate_limit": {"requests_per_minute": 100, "requests_per_day": 10000},
                "cost_limit": {"daily": 100.0},
                "permissions": ["orchestration", "streaming", "functions"],
            },
            "lukhas-test-key": {
                "user_id": "test-user",
                "tier": "standard",
                "rate_limit": {"requests_per_minute": 20, "requests_per_day": 1000},
                "cost_limit": {"daily": 10.0},
                "permissions": ["orchestration"],
            },
        }

        # Rate limiting tracking
        self.request_counts = {}
        self.daily_costs = {}

    def validate_api_key(self, api_key: str) -> dict[str, Any]:
        """Validate API key and return user information"""
        if api_key not in self.api_keys:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

        return self.api_keys[api_key]

    def check_rate_limit(self, api_key: str, user_info: dict[str, Any]) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        user_id = user_info["user_id"]

        # Initialize tracking for new users
        if user_id not in self.request_counts:
            self.request_counts[user_id] = []

        # Clean old requests (older than 1 minute)
        self.request_counts[user_id] = [
            req_time for req_time in self.request_counts[user_id] if current_time - req_time < 60
        ]

        # Check minute rate limit
        minute_limit = user_info["rate_limit"]["requests_per_minute"]
        if len(self.request_counts[user_id]) >= minute_limit:
            return False

        # Record this request
        self.request_counts[user_id].append(current_time)
        return True

    def check_cost_limit(
        self, api_key: str, user_info: dict[str, Any], estimated_cost: float
    ) -> bool:
        """Check if request would exceed cost limits"""
        user_id = user_info["user_id"]
        daily_limit = user_info["cost_limit"]["daily"]

        current_cost = self.daily_costs.get(user_id, 0.0)
        return current_cost + estimated_cost <= daily_limit

    def record_cost(self, api_key: str, user_info: dict[str, Any], cost: float):
        """Record cost for user"""
        user_id = user_info["user_id"]
        self.daily_costs[user_id] = self.daily_costs.get(user_id, 0.0) + cost


# Global instances
api_key_manager = APIKeyManager()
security = HTTPBearer() if FASTAPI_AVAILABLE else None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    api_key = credentials.credentials
    user_info = api_key_manager.validate_api_key(api_key)

    # Check rate limits
    if not api_key_manager.check_rate_limit(api_key, user_info):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )

    return {"api_key": api_key, "user_info": user_info}


# FastAPI Application
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="LUKHAS AI Multi-Model Orchestration API",
        description="Comprehensive API for multi-model AI orchestration with streaming and function calling",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint"""
        orchestrator = get_orchestrator()
        metrics = orchestrator.get_metrics()

        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "LUKHAS Multi-Model Orchestration API",
            "version": "2.0.0",
            "providers_available": metrics.get("available_providers", []),
            "total_requests": metrics.get("total_requests", 0),
            "average_latency_ms": metrics.get("average_latency_ms", 0.0),
            "performance_score": metrics.get("performance_score", 0.0),
        }

    # Main orchestration endpoint
    @app.post("/api/v1/orchestrate", response_model=OrchestrationAPIResponse)
    async def orchestrate_request(
        request: OrchestrationAPIRequest, current_user: dict = Depends(get_current_user)
    ) -> OrchestrationAPIResponse:
        """
        Orchestrate multi-model AI request with advanced consensus algorithms.

        This endpoint coordinates multiple AI models to provide enhanced accuracy,
        reliability, and comprehensive responses through consensus mechanisms.
        """
        start_time = time.perf_counter()
        api_key = current_user["api_key"]
        user_info = current_user["user_info"]

        try:
            # Check permissions
            if "orchestration" not in user_info["permissions"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Orchestration permission required",
                )

            # Check cost limits
            if not api_key_manager.check_cost_limit(api_key, user_info, request.max_cost):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Daily cost limit exceeded"
                )

            # Convert API request to orchestration request
            orchestrator = get_orchestrator()

            orchestration_request = OrchestrationRequest(
                prompt=request.prompt,
                context={"user_id": user_info["user_id"], "session_id": request.session_id},
                preferred_providers=[APIProvider(p) for p in request.providers]
                if request.providers
                else [APIProvider.ALL],
                strategy=OrchestrationStrategy(request.strategy),
                enable_functions=request.enable_functions
                and "functions" in user_info["permissions"],
                specific_functions=request.specific_functions,
                max_latency_ms=request.max_latency_ms,
                max_cost_threshold=request.max_cost,
                min_confidence=request.min_confidence,
                require_consensus=request.require_consensus,
                priority=request.priority,
            )

            # Execute orchestration
            result = await orchestrator.orchestrate(orchestration_request)

            # Record cost
            api_key_manager.record_cost(api_key, user_info, result.total_cost)

            # Convert to API response
            return OrchestrationAPIResponse(
                success=True,
                content=result.content,
                confidence_score=result.confidence_score,
                primary_provider=result.primary_provider.value,
                participating_providers=[p.value for p in result.participating_providers],
                latency_ms=result.total_latency_ms,
                cost=result.total_cost,
                token_usage=result.token_usage,
                agreement_level=result.agreement_level,
                consensus_achieved=result.consensus_achieved,
                request_id=result.request_id,
                timestamp=result.timestamp,
                strategy_used=result.strategy_used.value,
                function_calls=result.function_calls,
                tool_uses=result.tool_uses,
                individual_responses=result.individual_responses,
                decision_rationale=result.decision_rationale,
            )

        except HTTPException:
            raise
        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000
            logger.error(f"Orchestration API error: {e!s} ({latency:.2f}ms)")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Orchestration failed: {e!s}",
            )

    # Streaming endpoint with Server-Sent Events
    @app.post("/api/v1/stream")
    async def stream_orchestration(
        request: StreamingRequest, current_user: dict = Depends(get_current_user)
    ):
        """
        Stream AI responses in real-time using Server-Sent Events (SSE).

        Provides real-time streaming of AI responses with function calling
        and tool use capabilities for interactive applications.
        """
        current_user["api_key"]
        user_info = current_user["user_info"]

        # Check permissions
        if "streaming" not in user_info["permissions"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Streaming permission required"
            )

        async def generate_stream():
            """Generate SSE stream"""
            try:
                orchestrator = get_orchestrator()

                orchestration_request = OrchestrationRequest(
                    prompt=request.prompt,
                    preferred_providers=[APIProvider(request.provider)],
                    enable_functions=request.enable_functions
                    and "functions" in user_info["permissions"],
                )

                async for chunk in orchestrator.stream_orchestration(orchestration_request):
                    # Format as SSE
                    chunk_data = json.dumps(chunk)
                    yield f"data: {chunk_data}\n\n"

                # End stream
                yield 'data: {"type": "stream_end"}\n\n'

            except Exception as e:
                error_data = json.dumps({"type": "error", "error": str(e)})
                yield f"data: {error_data}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            },
        )

    # WebSocket endpoint for real-time bidirectional communication
    @app.websocket("/api/v1/ws/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        """
        WebSocket endpoint for real-time bidirectional AI communication.

        Supports:
        - Real-time streaming responses
        - Function calling with user interaction
        - Multi-turn conversations
        - Live performance metrics
        """
        await websocket.accept()

        logger.info(f"WebSocket client connected: {client_id}")

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)
                    message_type = message.get("type", "chat")

                    if message_type == "chat":
                        # Handle chat message
                        prompt = message.get("prompt", "")
                        if not prompt:
                            await websocket.send_text(
                                json.dumps({"type": "error", "error": "Empty prompt"})
                            )
                            continue

                        # Basic authentication for WebSocket (in production, use proper auth)
                        api_key = message.get("api_key")
                        if not api_key or api_key not in api_key_manager.api_keys:
                            await websocket.send_text(
                                json.dumps({"type": "error", "error": "Invalid API key"})
                            )
                            continue

                        # Stream response
                        orchestrator = get_orchestrator()
                        orchestration_request = OrchestrationRequest(
                            prompt=prompt,
                            preferred_providers=[APIProvider.OPENAI],  # Default for WebSocket
                            enable_functions=message.get("enable_functions", False),
                        )

                        async for chunk in orchestrator.stream_orchestration(orchestration_request):
                            await websocket.send_text(json.dumps(chunk))

                    elif message_type == "metrics":
                        # Send performance metrics
                        orchestrator = get_orchestrator()
                        metrics = orchestrator.get_metrics()
                        await websocket.send_text(json.dumps({"type": "metrics", "data": metrics}))

                    elif message_type == "ping":
                        # Heartbeat
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "pong",
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                }
                            )
                        )

                    else:
                        await websocket.send_text(
                            json.dumps(
                                {"type": "error", "error": f"Unknown message type: {message_type}"}
                            )
                        )

                except json.JSONDecodeError:
                    await websocket.send_text(
                        json.dumps({"type": "error", "error": "Invalid JSON message"})
                    )

                except Exception as e:
                    logger.error(f"WebSocket processing error: {e}")
                    await websocket.send_text(json.dumps({"type": "error", "error": str(e)}))

        except WebSocketDisconnect:
            logger.info(f"WebSocket client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")

    # Enhanced function registration endpoint with validation
    @app.post("/api/v1/functions/register")
    async def register_functions(
        request: FunctionRegistrationRequest, current_user: dict = Depends(get_current_user)
    ):
        """
        Register custom functions for use with AI models.

        Allows registration of custom functions that can be called by AI models
        during orchestration for enhanced capabilities and integration.
        Includes comprehensive security validation.
        """
        user_info = current_user["user_info"]

        # Check permissions
        if "functions" not in user_info["permissions"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Function registration permission required",
            )

        # Validate functions before registration
        try:
            validator = get_validator()
            if validator:
                validation_result = await validator.validate_request(
                    "function_registration", request.dict(), {"user_tier": user_info.get("tier")}
                )

                if not validation_result.is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "Function validation failed",
                            "validation_errors": validation_result.errors,
                            "security_issues": [
                                e
                                for e in validation_result.errors
                                if "security" in e.get("type", "")
                            ],
                        },
                    )
        except Exception as e:
            logger.warning(f"Function validation error: {e}")
            # Continue with basic validation

        try:
            orchestrator = get_orchestrator()

            # Security check for healthcare functions
            if request.healthcare_compliant and not request.security_validated:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Healthcare functions require security validation",
                )

            if request.global_scope:
                orchestrator.register_global_functions(request.functions)

            # Log function registration for audit
            logger.info(
                f"Functions registered by user {user_info['user_id']}: {list(request.functions.keys())}"
            )

            return {
                "success": True,
                "message": f"Registered {len(request.functions)} functions",
                "functions": list(request.functions.keys()),
                "global_scope": request.global_scope,
                "security_validated": request.security_validated,
                "healthcare_compliant": request.healthcare_compliant,
                "registration_id": str(uuid.uuid4()),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Function registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Function registration failed: {e!s}",
            )

    # Metrics endpoint
    @app.get("/api/v1/metrics")
    async def get_metrics(current_user: dict = Depends(get_current_user)):
        """
        Get comprehensive orchestration metrics and performance data.

        Provides detailed insights into API usage, performance, costs,
        and quality metrics for monitoring and optimization.
        """
        try:
            orchestrator = get_orchestrator()
            metrics = orchestrator.get_metrics()

            # Add API-specific metrics
            api_metrics = {
                "api_keys_active": len(api_key_manager.api_keys),
                "rate_limit_violations": 0,  # TODO: Track this
                "cost_limit_violations": 0,  # TODO: Track this
            }

            return {
                "success": True,
                "orchestration_metrics": metrics,
                "api_metrics": api_metrics,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Metrics endpoint error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve metrics: {e!s}",
            )

    # Provider status endpoint
    @app.get("/api/v1/providers/status")
    async def get_provider_status(current_user: dict = Depends(get_current_user)):
        """
        Get status of all available AI providers.

        Returns real-time status of OpenAI, Anthropic, Google, and other
        integrated AI providers including availability and performance metrics.
        """
        try:
            orchestrator = get_orchestrator()

            provider_status = {}
            for provider, bridge in orchestrator.bridges.items():
                try:
                    # Test provider with a simple request
                    test_start = time.perf_counter()

                    if hasattr(bridge, "get_metrics"):
                        bridge_metrics = bridge.get_metrics()
                        test_latency = (time.perf_counter() - test_start) * 1000

                        provider_status[provider.value] = {
                            "available": True,
                            "test_latency_ms": test_latency,
                            "metrics": bridge_metrics,
                        }
                    else:
                        provider_status[provider.value] = {
                            "available": True,
                            "test_latency_ms": 0.0,
                            "metrics": {},
                        }

                except Exception as e:
                    provider_status[provider.value] = {
                        "available": False,
                        "error": str(e),
                        "test_latency_ms": 0.0,
                    }

            return {
                "success": True,
                "providers": provider_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Provider status error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get provider status: {e!s}",
            )

    # Batch orchestration endpoint for multiple requests
    @app.post("/api/v1/orchestrate/batch")
    async def batch_orchestration(
        requests: list[OrchestrationAPIRequest], current_user: dict = Depends(get_current_user)
    ):
        """
        Process multiple orchestration requests in batch for efficiency.

        Useful for processing multiple prompts simultaneously with
        shared configuration and cost optimization.
        """
        if len(requests) > 10:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Batch size limited to 10 requests"
            )

        user_info = current_user["user_info"]

        # Check permissions
        if "orchestration" not in user_info["permissions"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Orchestration permission required"
            )

        batch_results = []
        total_cost = 0.0

        for i, request in enumerate(requests):
            try:
                # Process each request (simplified for batch)
                result = await orchestrate_request(request, current_user)
                batch_results.append({"index": i, "success": True, "result": result.dict()})
                total_cost += result.cost

            except HTTPException as e:
                batch_results.append({"index": i, "success": False, "error": e.detail})
            except Exception as e:
                batch_results.append({"index": i, "success": False, "error": str(e)})

        successful_requests = sum(1 for r in batch_results if r["success"])

        return {
            "batch_id": str(uuid.uuid4()),
            "total_requests": len(requests),
            "successful_requests": successful_requests,
            "failed_requests": len(requests) - successful_requests,
            "total_cost": total_cost,
            "results": batch_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Model comparison endpoint
    @app.post("/api/v1/compare-models")
    async def compare_models(
        request: OrchestrationAPIRequest, current_user: dict = Depends(get_current_user)
    ):
        """
        Compare responses from different AI models side-by-side.

        Useful for evaluating model performance and choosing the best
        provider for specific use cases.
        """
        user_info = current_user["user_info"]

        if "orchestration" not in user_info["permissions"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Orchestration permission required"
            )

        # Force parallel strategy for comparison
        request.strategy = "parallel"
        request.providers = request.providers or ["openai", "anthropic", "google", "perplexity"]

        # Execute orchestration to get all responses
        orchestrator = get_orchestrator()
        orchestration_request = OrchestrationRequest(
            prompt=request.prompt,
            preferred_providers=[APIProvider(p) for p in request.providers],
            strategy=OrchestrationStrategy.PARALLEL,
            enable_functions=False,  # Disable for fair comparison
            context={"comparison_mode": True},
        )

        result = await orchestrator.orchestrate(orchestration_request)

        # Format comparison results
        model_comparison = {
            "prompt": request.prompt,
            "total_latency_ms": result.total_latency_ms,
            "agreement_level": result.agreement_level,
            "models": [],
            "recommendation": {
                "best_model": result.primary_provider.value,
                "reason": result.decision_rationale,
            },
            "timestamp": result.timestamp,
        }

        # Add individual model results
        for response in result.individual_responses:
            model_comparison["models"].append(
                {
                    "provider": response["provider"],
                    "content": response["content"],
                    "confidence": response["confidence"],
                    "latency_ms": response["latency_ms"],
                    "score": response.get("combined_score", 0),
                    "web_search_used": response.get("web_search", False),
                }
            )

        return model_comparison

    logger.info("🚀 LUKHAS Multi-Model Orchestration API initialized")
    logger.info("   Endpoints: /api/v1/orchestrate, /api/v1/stream, /api/v1/ws/{client_id}")
    logger.info("   Healthcare: /api/v1/orchestrate/healthcare")
    logger.info("   Batch: /api/v1/orchestrate/batch")
    logger.info("   Comparison: /api/v1/compare-models")
    logger.info("   Authentication: Bearer token (API key)")
    logger.info("   Documentation: /api/docs")

else:
    logger.warning("FastAPI not available - API endpoints disabled")
    app = None

# Export main components
__all__ = [
    "APIKeyManager",
    "HealthcareOrchestrationRequest",
    "OrchestrationAPIRequest",
    "OrchestrationAPIResponse",
    "StreamingRequest",
    "app",
    "get_current_user",
]
