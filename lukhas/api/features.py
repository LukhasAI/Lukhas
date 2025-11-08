"""
Feature Flags API for LUKHAS AI.

Provides FastAPI endpoints for managing and evaluating feature flags.

PRIVACY REQUIREMENTS:
- Authentication required (no anonymous flag checking)
- Audit logging for flag evaluations
- Rate limiting (100 requests/min per user)
- No PII in responses

ENDPOINTS:
- GET /api/features - List all flags (admin only)
- GET /api/features/{flag_name} - Get flag state
- POST /api/features/{flag_name}/evaluate - Evaluate for user
- PATCH /api/features/{flag_name} - Update flag (admin only)
"""

import logging
import time
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from lukhas.features.flags_service import (
    FeatureFlagsService,
    FlagEvaluationContext,
    FlagType,
    get_service,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/features", tags=["Feature Flags"])


# Request/Response Models


class FlagEvaluationRequest(BaseModel):
    """Request to evaluate a feature flag."""

    user_id: Optional[str] = Field(None, description="User ID for targeting")
    email: Optional[str] = Field(None, description="User email for domain targeting")
    environment: Optional[str] = Field(None, description="Environment (dev/staging/prod)")


class FlagEvaluationResponse(BaseModel):
    """Response from flag evaluation."""

    flag_name: str = Field(..., description="Name of the flag")
    enabled: bool = Field(..., description="Whether the flag is enabled")
    flag_type: str = Field(..., description="Type of the flag")


class FlagInfo(BaseModel):
    """Information about a feature flag."""

    name: str = Field(..., description="Flag name")
    enabled: bool = Field(..., description="Whether the flag is globally enabled")
    flag_type: str = Field(..., description="Type of the flag")
    description: str = Field(..., description="Description of the flag")
    owner: str = Field(..., description="Team/person responsible for the flag")
    created_at: str = Field(..., description="Creation date")
    jira_ticket: str = Field(..., description="Associated JIRA ticket")


class FlagUpdateRequest(BaseModel):
    """Request to update a feature flag."""

    enabled: Optional[bool] = Field(None, description="Enable/disable the flag")
    percentage: Optional[int] = Field(None, ge=0, le=100, description="Rollout percentage (0-100)")


class FlagListResponse(BaseModel):
    """Response with list of all flags."""

    flags: List[FlagInfo] = Field(..., description="List of all feature flags")
    total: int = Field(..., description="Total number of flags")


# Rate limiting (simple in-memory implementation)
_rate_limit_store: Dict[str, List[float]] = {}
_RATE_LIMIT = 100  # requests per minute
_RATE_LIMIT_WINDOW = 60  # seconds


def check_rate_limit(user_id: str) -> bool:
    """
    Check if user has exceeded rate limit.

    Args:
        user_id: User identifier

    Returns:
        True if within rate limit, False otherwise
    """
    now = time.time()

    # Get user's request history
    if user_id not in _rate_limit_store:
        _rate_limit_store[user_id] = []

    # Remove old requests outside the window
    _rate_limit_store[user_id] = [
        req_time
        for req_time in _rate_limit_store[user_id]
        if now - req_time < _RATE_LIMIT_WINDOW
    ]

    # Check if over limit
    if len(_rate_limit_store[user_id]) >= _RATE_LIMIT:
        return False

    # Add current request
    _rate_limit_store[user_id].append(now)
    return True


# Dependency injection


def get_feature_flags_service() -> FeatureFlagsService:
    """Get feature flags service instance."""
    return get_service()


def get_current_user(request: Request) -> str:
    """
    Get current authenticated user.

    In production, this would verify JWT tokens, API keys, etc.
    For now, returns a placeholder user ID.

    Args:
        request: FastAPI request object

    Returns:
        User ID

    Raises:
        HTTPException: If authentication fails
    """
    # TODO: Implement actual authentication
    # For now, check for API key in headers
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    # Placeholder user ID based on API key
    # In production, validate API key and return actual user ID
    return f"user_{api_key[:8]}"


def require_admin(user_id: str = Depends(get_current_user)) -> str:
    """
    Require admin role for endpoint.

    Args:
        user_id: Current user ID

    Returns:
        User ID

    Raises:
        HTTPException: If user is not admin
    """
    # TODO: Implement actual role checking
    # For now, check if user_id starts with "admin_"
    if not user_id.startswith("admin_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user_id


# API Endpoints


@router.get("/", response_model=FlagListResponse)
async def list_flags(
    user_id: str = Depends(require_admin),
    service: FeatureFlagsService = Depends(get_feature_flags_service),
) -> FlagListResponse:
    """
    List all feature flags (admin only).

    Returns:
        List of all feature flags with metadata
    """
    try:
        flags = service.get_all_flags()

        flag_infos = [
            FlagInfo(
                name=name,
                enabled=flag.enabled,
                flag_type=flag.flag_type.value,
                description=flag.description,
                owner=flag.owner,
                created_at=flag.created_at,
                jira_ticket=flag.jira_ticket,
            )
            for name, flag in flags.items()
        ]

        return FlagListResponse(flags=flag_infos, total=len(flag_infos))

    except Exception as e:
        logger.error(f"Error listing flags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing feature flags",
        )


@router.get("/{flag_name}", response_model=FlagInfo)
async def get_flag(
    flag_name: str,
    user_id: str = Depends(get_current_user),
    service: FeatureFlagsService = Depends(get_feature_flags_service),
) -> FlagInfo:
    """
    Get feature flag information.

    Args:
        flag_name: Name of the flag

    Returns:
        Flag information
    """
    try:
        flag = service.get_flag(flag_name)
        if not flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flag not found: {flag_name}",
            )

        return FlagInfo(
            name=flag_name,
            enabled=flag.enabled,
            flag_type=flag.flag_type.value,
            description=flag.description,
            owner=flag.owner,
            created_at=flag.created_at,
            jira_ticket=flag.jira_ticket,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting flag {flag_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting feature flag",
        )


@router.post("/{flag_name}/evaluate", response_model=FlagEvaluationResponse)
async def evaluate_flag(
    flag_name: str,
    request_data: FlagEvaluationRequest,
    user_id: str = Depends(get_current_user),
    service: FeatureFlagsService = Depends(get_feature_flags_service),
) -> FlagEvaluationResponse:
    """
    Evaluate feature flag for specific context.

    Args:
        flag_name: Name of the flag
        request_data: Evaluation context data

    Returns:
        Flag evaluation result
    """
    # Check rate limit
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded (100 requests/min)",
        )

    try:
        # Create evaluation context
        context = FlagEvaluationContext(
            user_id=request_data.user_id,
            email=request_data.email,
            environment=request_data.environment,
        )

        # Get flag
        flag = service.get_flag(flag_name)
        if not flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flag not found: {flag_name}",
            )

        # Evaluate flag
        enabled = service.is_enabled(flag_name, context)

        # Audit log (aggregate only, no PII)
        logger.info(
            f"Flag evaluation: {flag_name} = {enabled} "
            f"(type={flag.flag_type.value}, env={context.environment})"
        )

        return FlagEvaluationResponse(
            flag_name=flag_name,
            enabled=enabled,
            flag_type=flag.flag_type.value,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating flag {flag_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error evaluating feature flag",
        )


@router.patch("/{flag_name}", response_model=FlagInfo)
async def update_flag(
    flag_name: str,
    update_data: FlagUpdateRequest,
    user_id: str = Depends(require_admin),
    service: FeatureFlagsService = Depends(get_feature_flags_service),
) -> FlagInfo:
    """
    Update feature flag configuration (admin only).

    Args:
        flag_name: Name of the flag
        update_data: Update data

    Returns:
        Updated flag information
    """
    try:
        # Get flag
        flag = service.get_flag(flag_name)
        if not flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flag not found: {flag_name}",
            )

        # Update flag
        if update_data.enabled is not None:
            flag.enabled = update_data.enabled

        if update_data.percentage is not None:
            if flag.flag_type != FlagType.PERCENTAGE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot set percentage on {flag.flag_type.value} flag",
                )
            flag.percentage = update_data.percentage

        # Audit log
        logger.info(
            f"Flag updated by {user_id}: {flag_name} "
            f"(enabled={flag.enabled}, percentage={flag.percentage})"
        )

        return FlagInfo(
            name=flag_name,
            enabled=flag.enabled,
            flag_type=flag.flag_type.value,
            description=flag.description,
            owner=flag.owner,
            created_at=flag.created_at,
            jira_ticket=flag.jira_ticket,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating flag {flag_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating feature flag",
        )


@router.post("/{flag_name}/reload")
async def reload_flag(
    flag_name: str,
    user_id: str = Depends(require_admin),
    service: FeatureFlagsService = Depends(get_feature_flags_service),
) -> Dict[str, str]:
    """
    Force reload flag from configuration (admin only).

    Args:
        flag_name: Name of the flag to reload

    Returns:
        Success message
    """
    try:
        # Reload all flags
        service.reload()

        # Check if flag exists after reload
        if not service.get_flag(flag_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flag not found after reload: {flag_name}",
            )

        logger.info(f"Flag reloaded by {user_id}: {flag_name}")

        return {"message": f"Flag reloaded successfully: {flag_name}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reloading flag {flag_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reloading feature flag",
        )
