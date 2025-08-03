#!/usr/bin/env python3
"""
LUKHAS Enterprise API Framework
Production-grade API with versioning, type safety, and OpenAPI documentation
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, TypeVar, Generic, Union
from enum import Enum
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends, Header, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.generics import GenericModel
import structlog
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as redis
from typing_extensions import Annotated

# Configure structured logging
logger = structlog.get_logger()

# Type variables for generic responses
T = TypeVar('T')

# Metrics
request_count = Counter(
    'lukhas_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'version', 'status']
)

request_duration = Histogram(
    'lukhas_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint', 'version']
)

# API Versioning
class APIVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    
    def is_deprecated(self) -> bool:
        """Check if version is deprecated"""
        return self == APIVersion.V1

# Base Models with strict typing
class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RequestMetadata(BaseModel):
    """Standard request metadata"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    api_version: APIVersion = APIVersion.V2

class ResponseMetadata(BaseModel):
    """Standard response metadata"""
    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str
    duration_ms: float

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, le=1000)
    per_page: int = Field(20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

class PaginationMetadata(BaseModel):
    """Pagination metadata for responses"""
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class APIResponse(GenericModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: ResponseMetadata
    pagination: Optional[PaginationMetadata] = None

class APIError(BaseModel):
    """Standard error response"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# LUKHAS-specific models
class TierLevel(int, Enum):
    """LUKHAS tier levels"""
    PUBLIC = 0
    BASIC = 1
    ADVANCED = 2
    PREMIUM = 3
    ELITE = 4

class EmotionalState(BaseModel):
    """Emotional state representation"""
    valence: float = Field(..., ge=-1, le=1)
    arousal: float = Field(..., ge=-1, le=1)
    dominance: float = Field(..., ge=-1, le=1)
    
    @validator('valence', 'arousal', 'dominance')
    def validate_range(cls, v):
        if not -1 <= v <= 1:
            raise ValueError('Value must be between -1 and 1')
        return v

class MemoryFoldRequest(BaseModel):
    """Request to fold memory with emotional context"""
    data: Dict[str, Any]
    emotional_context: EmotionalState
    tier_level: TierLevel
    fold_options: Optional[Dict[str, Any]] = None
    
    @root_validator
    def validate_tier_requirements(cls, values):
        tier = values.get('tier_level')
        options = values.get('fold_options', {})
        
        # Advanced folding requires higher tier
        if options.get('quantum_fold') and tier < TierLevel.ADVANCED:
            raise ValueError('Quantum folding requires ADVANCED tier or higher')
            
        return values

class MemoryFoldResponse(BaseModel):
    """Response from memory fold operation"""
    fold_id: str
    status: str
    folded_data: Dict[str, Any]
    emotional_signature: str
    metadata: Dict[str, Any]

# Middleware
class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Add request tracing and logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Add to request state
        request.state.request_id = request_id
        request.state.start_time = datetime.utcnow()
        
        # Log request
        logger.info("api_request_started",
                   request_id=request_id,
                   method=request.method,
                   path=request.url.path,
                   client=request.client.host if request.client else None)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (datetime.utcnow() - request.state.start_time).total_seconds() * 1000
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        
        # Log response
        logger.info("api_request_completed",
                   request_id=request_id,
                   status_code=response.status_code,
                   duration_ms=duration_ms)
        
        # Update metrics
        endpoint = request.url.path.split('/')
        version = endpoint[2] if len(endpoint) > 2 and endpoint[2] in ['v1', 'v2', 'v3'] else 'unknown'
        
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            version=version,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path,
            version=version
        ).observe(duration_ms / 1000.0)
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, redis_client: redis.Redis, default_limit: int = 100):
        super().__init__(app)
        self.redis_client = redis_client
        self.default_limit = default_limit
        
    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_id = request.headers.get('X-API-Key', request.client.host if request.client else 'unknown')
        
        # Check rate limit
        key = f"rate_limit:{client_id}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        
        try:
            current = await self.redis_client.incr(key)
            if current == 1:
                await self.redis_client.expire(key, 60)
                
            if current > self.default_limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": 60
                    },
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(self.default_limit),
                        "X-RateLimit-Remaining": "0"
                    }
                )
                
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.default_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.default_limit - current))
            
            return response
            
        except Exception as e:
            logger.error("rate_limit_check_failed", error=str(e))
            # Fail open - allow request if rate limiting fails
            return await call_next(request)

# Security
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token and extract claims"""
    token = credentials.credentials
    
    # TODO: Implement proper JWT verification
    # For now, mock verification
    if not token or token == "invalid":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
    return {
        "user_id": "user_123",
        "tier_level": TierLevel.ADVANCED,
        "permissions": ["read", "write"]
    }

async def get_current_user(token_data: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """Get current user from token"""
    return token_data

# Dependency injection
async def get_redis_client() -> redis.Redis:
    """Get Redis client"""
    return redis.from_url("redis://localhost:6379", decode_responses=True)

# Application factory
def create_app(config: Optional[Dict[str, Any]] = None) -> FastAPI:
    """Create FastAPI application with all configurations"""
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        logger.info("lukhas_api_starting", version="2.0.0")
        
        # Initialize connections
        app.state.redis = await get_redis_client()
        
        yield
        
        # Shutdown
        await app.state.redis.close()
        logger.info("lukhas_api_stopped")
    
    app = FastAPI(
        title="LUKHAS AI API",
        description="Enterprise-grade API for LUKHAS AI System",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get("cors_origins", ["*"]) if config else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestTracingMiddleware)
    
    # Add rate limiting if Redis is available
    @app.on_event("startup")
    async def startup_event():
        try:
            redis_client = await get_redis_client()
            app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
        except Exception as e:
            logger.warning("rate_limiting_disabled", error=str(e))
    
    return app

# Create app instance
app = create_app()

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check(
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """Detailed health check with subsystem status"""
    checks = {
        "api": "healthy",
        "redis": "unknown",
        "database": "unknown"
    }
    
    # Check Redis
    try:
        await redis_client.ping()
        checks["redis"] = "healthy"
    except Exception:
        checks["redis"] = "unhealthy"
        
    overall_status = "healthy" if all(v == "healthy" for v in checks.values()) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "checks": checks
    }

# Metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# API v1 endpoints (deprecated)
@app.post("/api/v1/memory/fold", 
         tags=["Memory", "Deprecated"],
         deprecated=True,
         response_model=APIResponse[MemoryFoldResponse])
async def fold_memory_v1(
    request: MemoryFoldRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    req: Request = None
) -> APIResponse[MemoryFoldResponse]:
    """
    Fold memory with emotional context (DEPRECATED - Use v2)
    
    This endpoint is deprecated and will be removed in v3.
    Please migrate to /api/v2/memory/fold
    """
    # Implementation would call memory service
    response = MemoryFoldResponse(
        fold_id=str(uuid.uuid4()),
        status="completed",
        folded_data={"sample": "data"},
        emotional_signature="e1234567",
        metadata={"version": "v1"}
    )
    
    return APIResponse(
        data=response,
        metadata=ResponseMetadata(
            request_id=req.state.request_id,
            version="v1",
            duration_ms=(datetime.utcnow() - req.state.start_time).total_seconds() * 1000
        )
    )

# API v2 endpoints (current)
@app.post("/api/v2/memory/fold",
         tags=["Memory"],
         response_model=APIResponse[MemoryFoldResponse],
         summary="Fold memory with emotional context",
         description="""
         Folds memory data with emotional context using LUKHAS's proprietary
         memory folding algorithm. Requires appropriate tier level for advanced features.
         """)
async def fold_memory_v2(
    request: MemoryFoldRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    req: Request = None
) -> APIResponse[MemoryFoldResponse]:
    """Fold memory with emotional context"""
    
    # Verify tier access
    user_tier = user.get("tier_level", TierLevel.BASIC)
    if request.tier_level > user_tier:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient tier level. Required: {request.tier_level.name}, Current: {user_tier.name}"
        )
    
    # Process fold (mock implementation)
    fold_id = str(uuid.uuid4())
    
    # Add background task for async processing
    background_tasks.add_task(
        process_fold_async,
        fold_id,
        request.data,
        request.emotional_context
    )
    
    response = MemoryFoldResponse(
        fold_id=fold_id,
        status="processing",
        folded_data={},
        emotional_signature=generate_emotional_signature(request.emotional_context),
        metadata={
            "version": "v2",
            "tier": request.tier_level.name,
            "async": True
        }
    )
    
    return APIResponse(
        data=response,
        metadata=ResponseMetadata(
            request_id=req.state.request_id,
            version="v2",
            duration_ms=(datetime.utcnow() - req.state.start_time).total_seconds() * 1000
        )
    )

@app.get("/api/v2/memory/fold/{fold_id}",
        tags=["Memory"],
        response_model=APIResponse[MemoryFoldResponse])
async def get_fold_status(
    fold_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    req: Request = None
) -> APIResponse[MemoryFoldResponse]:
    """Get status of memory fold operation"""
    
    # Mock implementation - would check actual status
    response = MemoryFoldResponse(
        fold_id=fold_id,
        status="completed",
        folded_data={"processed": True},
        emotional_signature="e" + fold_id[:7],
        metadata={"completion_time": datetime.utcnow().isoformat()}
    )
    
    return APIResponse(
        data=response,
        metadata=ResponseMetadata(
            request_id=req.state.request_id,
            version="v2",
            duration_ms=10.5
        )
    )

@app.get("/api/v2/consciousness/state",
        tags=["Consciousness"],
        response_model=APIResponse[Dict[str, Any]])
async def get_consciousness_state(
    user: Dict[str, Any] = Depends(get_current_user),
    req: Request = None
) -> APIResponse[Dict[str, Any]]:
    """Get current consciousness state"""
    
    state = {
        "awareness_level": 0.85,
        "emotional_state": {
            "valence": 0.3,
            "arousal": 0.5,
            "dominance": 0.6
        },
        "active_processes": ["perception", "reflection", "memory_consolidation"],
        "drift_score": 0.12
    }
    
    return APIResponse(
        data=state,
        metadata=ResponseMetadata(
            request_id=req.state.request_id,
            version="v2",
            duration_ms=5.2
        )
    )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=APIError(
            code=f"HTTP_{exc.status_code}",
            message=exc.detail,
            request_id=getattr(request.state, 'request_id', 'unknown'),
            details={"path": request.url.path}
        ).dict()
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=400,
        content=APIError(
            code="VALIDATION_ERROR",
            message=str(exc),
            request_id=getattr(request.state, 'request_id', 'unknown')
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error("unhandled_exception",
                error=str(exc),
                request_id=getattr(request.state, 'request_id', 'unknown'))
    
    return JSONResponse(
        status_code=500,
        content=APIError(
            code="INTERNAL_ERROR",
            message="An internal error occurred",
            request_id=getattr(request.state, 'request_id', 'unknown')
        ).dict()
    )

# Helper functions
def generate_emotional_signature(state: EmotionalState) -> str:
    """Generate unique signature for emotional state"""
    data = f"{state.valence}{state.arousal}{state.dominance}"
    return hashlib.sha256(data.encode()).hexdigest()[:8]

async def process_fold_async(fold_id: str, data: Dict[str, Any], emotional_context: EmotionalState):
    """Process fold asynchronously"""
    # Mock async processing
    logger.info("processing_fold_async", fold_id=fold_id)
    await asyncio.sleep(2)
    logger.info("fold_completed", fold_id=fold_id)

# API v3 endpoints (future)
# These would include GraphQL support, WebSocket subscriptions, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)