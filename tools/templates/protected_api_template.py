"""
LUKHAS  Protected API Template
=================================
Template for creating tier-protected API endpoints with proper authentication.

Copy this template when creating new API endpoints.
"""

# Configure logging
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel

# LUKHAS Identity Integration - PLACEHOLDER
# Note: Update these imports based on your actual identity middleware location
try:
    from identity.middleware import (
        AuthContext,
        get_current_user,
        require_permission,
        require_t2_or_above,
        require_t3_or_above,
        require_t4_or_above,
        require_t5,
        require_tier,
    )
except ImportError:
    # Fallback mock implementations for template testing
    class AuthContext:
        def __init__(self):
            self.user_id = "template_user"
            self.email = "test@ai"
            self.tier = "T2"
            self.lambda_id = "λ-template-123"
            self.permissions: dict[str, bool] = {
                "can_create_content": True,
                "can_use_consciousness": False,
                "can_use_quantum": False,
                "can_admin": False,
            }
            self.triad_score = 0.5

        def has_permission(self, permission: str) -> bool:
            return self.permissions.get(permission, False)

    def get_current_user():
        return AuthContext()

    def require_t2_or_above():
        return get_current_user()

    def require_t3_or_above():
        return get_current_user()

    def require_t4_or_above():
        return get_current_user()

    def require_t5():
        return get_current_user()

    def require_tier(tier: str):
        def decorator(func):
            return func

        return decorator

    def require_permission(permission: str):
        def decorator(func):
            return func

        return decorator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LUKHAS Protected API",
    description="Template for tier-protected API endpoints",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# ==================== Request/Response Models ====================


class BaseRequest(BaseModel):
    """Base request model with user context tracking."""

    class Config:
        extra = "allow"

    def add_user_context(self, user: AuthContext) -> dict[str, Any]:
        """Add user context to request data."""
        data = self.dict()
        data.update(
            {
                "user_id": user.user_id,
                "user_email": user.email,
                "user_tier": user.tier,
                "lambda_id": user.lambda_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return data


class BaseResponse(BaseModel):
    """Base response model with user context."""

    success: bool = True
    message: Optional[str] = None
    user_context: Optional[dict[str, str]] = None

    @classmethod
    def create_success(cls, data: Any = None, user: AuthContext = None, message: Optional[str] = None):
        """Create successful response with user context."""
        response_data = {"success": True, "message": message, "data": data}

        if user:
            response_data["user_context"] = {
                "user_id": user.user_id,
                "tier": user.tier,
                "permissions": list(user.permissions.keys()),
            }

        return cls(**response_data)

    @classmethod
    def create_error(cls, message: str, user: AuthContext = None):
        """Create error response with user context."""
        response_data = {"success": False, "message": message}

        if user:
            response_data["user_context"] = {"user_id": user.user_id, "tier": user.tier}

        return cls(**response_data)


# ==================== API Endpoints ====================


@app.get("/", tags=["General"])
async def root():
    """Public endpoint - no authentication required."""
    return {"message": "LUKHAS Protected API Template"}


@app.get("/health", tags=["System"])
async def health_check():
    """Public health check - no authentication required."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# ==================== T2 Protected Endpoints (Creator Tier) ====================


@app.get("/protected/basic", response_model=BaseResponse, tags=["T2-Protected"])
async def basic_protected_endpoint(
    user: AuthContext = Depends(require_t2_or_above),  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_templates_protected_api_template_py_L181"}
) -> BaseResponse:
    """
    T2+ Protected endpoint - Requires Creator tier or above.

    Features:
    - Authentication required
    - User context automatically injected
    - Proper error handling
    """
    try:
        # Your business logic here
        data = {
            "message": "Access granted to T2+ endpoint",
            "user_tier": user.tier,
            "available_permissions": [p for p, v in user.permissions.items() if v],
        }

        # Log user activity
        logger.info(f"T2 endpoint accessed by user {user.user_id} (tier: {user.tier})")

        return BaseResponse.create_success(data=data, user=user, message="T2+ access granted")

    except Exception as e:
        logger.error(f"Error in T2 endpoint for user {user.user_id}: {e}")
        return BaseResponse.create_error(f"Internal error: {e!s}", user=user)


@app.post("/protected/create", response_model=BaseResponse, tags=["T2-Protected"])
async def create_content_endpoint(
    request: BaseRequest,
    user: AuthContext = Depends(require_t2_or_above),  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_templates_protected_api_template_py_L212"}
) -> BaseResponse:
    """T2+ Protected content creation endpoint."""

    # Check specific permission
    if not user.has_permission("can_create_content"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: can_create_content",
        )

    try:
        # Add user context to request
        data = request.add_user_context(user)

        # Your creation logic here
        result = {
            "created_item_id": "item_123",
            "created_by": user.user_id,
            "creation_time": data["timestamp"],
        }

        logger.info(f"Content created by user {user.user_id}")

        return BaseResponse.create_success(data=result, user=user, message="Content created successfully")

    except Exception as e:
        logger.error(f"Content creation error for user {user.user_id}: {e}")
        return BaseResponse.create_error(f"Creation failed: {e!s}", user=user)


# ==================== T3 Protected Endpoints (Advanced Tier) ====================


@app.post("/protected/consciousness", response_model=BaseResponse, tags=["T3-Protected"])
async def consciousness_endpoint(
    request: BaseRequest,
    user: AuthContext = Depends(require_t3_or_above),  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_templates_protected_api_template_py_L249"}
) -> BaseResponse:
    """
    T3+ Protected consciousness endpoint.
    Requires Advanced tier for consciousness module access.
    """

    # Check specific permission
    if not user.has_permission("can_use_consciousness"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: can_use_consciousness",
        )

    try:
        request.add_user_context(user)

        # Your consciousness logic here
        # from consciousness import process_consciousness_request
        # result = await process_consciousness_request(data)

        result = {
            "consciousness_response": "Simulated consciousness response",
            "processed_by": user.user_id,
            "user_tier": user.tier,
        }

        logger.info(f"Consciousness accessed by user {user.user_id} (T3+)")

        return BaseResponse.create_success(data=result, user=user, message="Consciousness processing complete")

    except Exception as e:
        logger.error(f"Consciousness error for user {user.user_id}: {e}")
        return BaseResponse.create_error(f"Consciousness processing failed: {e!s}", user=user)


# ==================== T4 Protected Endpoints (Quantum Tier) ====================


@app.post("/protected/quantum", response_model=BaseResponse, tags=["T4-Protected"])
async def qi_endpoint(request: BaseRequest, user: AuthContext = Depends(require_t4_or_above)) -> BaseResponse:  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_templates_protected_api_template_py_L289"}
    """
    T4+ Protected quantum endpoint.
    Requires Quantum tier for quantum processing access.
    """

    if not user.has_permission("can_use_quantum"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: can_use_quantum",
        )

    try:
        request.add_user_context(user)

        # Your quantum logic here
        # from qi import process_quantum_computation
        # result = await process_quantum_computation(data)

        result = {
            "qi_result": "Simulated quantum computation result",
            "processed_by": user.user_id,
            "qi_tier_verified": True,
        }

        logger.info(f"Quantum processing accessed by user {user.user_id} (T4+)")

        return BaseResponse.create_success(data=result, user=user, message="Quantum computation complete")

    except Exception as e:
        logger.error(f"Quantum error for user {user.user_id}: {e}")
        return BaseResponse.create_error(f"Quantum processing failed: {e!s}", user=user)


# ==================== T5 Protected Endpoints (Guardian Tier) ====================


@app.post("/protected/admin", response_model=BaseResponse, tags=["T5-Protected"])
async def admin_endpoint(request: BaseRequest, user: AuthContext = Depends(require_t5)) -> BaseResponse:  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_templates_protected_api_template_py_L327"}
    """
    T5 Protected admin endpoint.
    Requires Guardian tier (T5) for administrative access.
    """

    if not user.has_permission("can_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: can_admin",
        )

    try:
        request.add_user_context(user)

        # Your admin logic here
        # from governance import process_admin_request
        # result = await process_admin_request(data)

        result = {
            "admin_action": "Simulated admin action",
            "processed_by": user.user_id,
            "guardian_verified": True,
            "triad_score": user.triad_score,
        }

        logger.info(f"Admin action accessed by Guardian user {user.user_id}")

        return BaseResponse.create_success(data=result, user=user, message="Administrative action complete")

    except Exception as e:
        logger.error(f"Admin error for Guardian user {user.user_id}: {e}")
        return BaseResponse.create_error(f"Administrative action failed: {e!s}", user=user)


# ==================== Custom Tier Protection Examples ====================


@app.get("/protected/custom", tags=["Custom-Protection"])
@require_tier("T3")  # Decorator approach
async def custom_tier_endpoint(user: AuthContext = Depends(get_current_user)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_templates_protected_api_template_py_L367"}
    """Example using @require_tier decorator."""
    return {"message": "Custom tier protection applied", "user_tier": user.tier}


@app.get("/protected/permission", tags=["Permission-Protection"])
@require_permission("can_use_consciousness")  # Permission-based protection
async def permission_based_endpoint(user: AuthContext = Depends(get_current_user)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_templates_protected_api_template_py_L374"}
    """Example using @require_permission decorator."""
    return {
        "message": "Permission-based protection applied",
        "user_permissions": [p for p, v in user.permissions.items() if v],
    }


# ==================== Error Handlers ====================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom error handler with user context if available."""

    # Try to extract user context from request
    user_context = getattr(request.state, "user", None) if hasattr(request, "state") else None

    response_data = {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code,
    }

    if user_context:
        response_data["user_context"] = {
            "user_id": user_context.user_id,
            "tier": user_context.tier,
        }

    return JSONResponse(status_code=exc.status_code, content=response_data)


# ==================== Startup/Shutdown Events ====================


@app.on_event("startup")
async def startup_event():
    """Initialize the protected API."""
    logger.info("LUKHAS Protected API started - Authentication enabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("LUKHAS Protected API shutting down")


# ==================== Usage Examples ====================
"""
USAGE EXAMPLES:

1. Basic T2+ Endpoint:
   GET /protected/basic
   Headers: Authorization: Bearer <token>

2. Content Creation (T2+):
   POST /protected/create
   Headers: Authorization: Bearer <token>
   Body: {"title": "My Content", "content": "..."}

3. Consciousness Access (T3+):
   POST /protected/consciousness
   Headers: Authorization: Bearer <token>
   Body: {"prompt": "What is consciousness?"}

4. Quantum Processing (T4+):
   POST /protected/quantum
   Headers: Authorization: Bearer <token>
   Body: {"algorithm": "qi_search", "data": [...]}

5. Admin Actions (T5):
   POST /protected/admin
   Headers: Authorization: Bearer <token>
   Body: {"action": "system_maintenance"}

TESTING:
1. Get a token from identity service
2. Use token in Authorization header
3. API will automatically validate tier and permissions
4. User context is injected into all protected endpoints

CUSTOMIZATION:
- Modify tier requirements per endpoint
- Add custom permission checks
- Extend BaseRequest/BaseResponse models
- Add business logic in try/catch blocks
- Customize error messages and responses
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
