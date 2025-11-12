"""FastAPI routes for GDPR compliance endpoints."""

from typing import ClassVar, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from lukhas.governance.gdpr.config import get_default_config
from lukhas.governance.gdpr.service import GDPRService

# Create router
router = APIRouter(prefix="/api/v1/gdpr", tags=["GDPR"])

# Initialize GDPR service
_gdpr_service = None


def get_gdpr_service() -> GDPRService:
    """Get or create GDPR service instance.

    Returns:
        GDPRService instance
    """
    global _gdpr_service
    if _gdpr_service is None:
        _gdpr_service = GDPRService(config=get_default_config())
    return _gdpr_service


def get_current_user_id(request: Request) -> str:
    """Extract user ID from request state.

    Args:
        request: FastAPI request

    Returns:
        User ID from validated JWT

    Raises:
        HTTPException: If user_id not found in request state
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User context not found. Authentication required."
        )
    return user_id


class DataExportRequest(BaseModel):
    """Request to export user data."""

    data_sources: Optional[List[str]] = None
    include_metadata: bool = True

    class Config:
        json_schema_extra: ClassVar[dict[str, object]] = {
            "example": {
                "data_sources": ["user_profile", "feedback_cards", "traces"],
                "include_metadata": True
            }
        }


class DataExportResponse(BaseModel):
    """Response with exported user data."""

    export_id: str
    user_id: str
    export_timestamp: float
    data_controller: str
    data: dict
    metadata: dict

    class Config:
        json_schema_extra: ClassVar[dict[str, object]] = {
            "example": {
                "export_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_abc",
                "export_timestamp": 1704067200.0,
                "data_controller": "LUKHAS AI",
                "data": {
                    "user_profile": {"user_id": "user_abc", "tier": 0},
                    "feedback_cards": [],
                },
                "metadata": {
                    "total_records_exported": 1,
                    "sources_exported": ["user_profile", "feedback_cards"],
                }
            }
        }


class DataDeletionRequest(BaseModel):
    """Request to delete user data."""

    data_sources: Optional[List[str]] = None
    confirm: bool = False

    class Config:
        json_schema_extra: ClassVar[dict[str, object]] = {
            "example": {
                "data_sources": ["feedback_cards", "traces"],
                "confirm": True
            }
        }


class DataDeletionResponse(BaseModel):
    """Response with deletion result."""

    deletion_id: str
    user_id: str
    deletion_timestamp: float
    success: bool
    items_deleted: dict
    errors: List[str]
    metadata: dict

    class Config:
        json_schema_extra: ClassVar[dict[str, object]] = {
            "example": {
                "deletion_id": "660e9511-f3ac-52e5-b827-557766551111",
                "user_id": "user_abc",
                "deletion_timestamp": 1704067200.0,
                "success": True,
                "items_deleted": {
                    "feedback_cards": 15,
                    "traces": 42,
                },
                "errors": [],
                "metadata": {
                    "total_items_deleted": 57,
                    "deletion_type": "soft",
                }
            }
        }


class PrivacyPolicyResponse(BaseModel):
    """Response with privacy policy information."""

    data_controller: dict
    data_processing: dict
    data_subject_rights: dict
    data_categories: dict
    data_recipients: List[str]
    international_transfers: dict
    automated_decision_making: dict
    contact: dict
    effective_date: str
    version: str


@router.post("/export", response_model=DataExportResponse)
async def export_user_data(
    request_body: DataExportRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    service: GDPRService = Depends(get_gdpr_service),
):
    """Export all user data (GDPR Article 15 - Right to Access).

    Exports all personal data held about the authenticated user in a structured,
    machine-readable format.

    **GDPR Article 15 Requirements:**
    - Confirmation that personal data is being processed
    - Access to the personal data
    - Information about processing (purposes, categories, recipients)
    - Storage period or criteria
    - Right to request rectification or erasure
    - Right to lodge a complaint with supervisory authority

    **Authentication:** Required (JWT token)

    **Rate Limiting:** 1 request per day per user recommended

    Args:
        request_body: Export request parameters
        request: FastAPI request
        user_id: Authenticated user ID (from JWT)
        service: GDPR service instance

    Returns:
        DataExportResponse with all user data

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 500: If export fails
    """
    try:
        # Export user data
        export = await service.export_user_data(
            user_id=user_id,
            data_sources=request_body.data_sources,
            include_metadata=request_body.include_metadata,
        )

        return DataExportResponse(
            export_id=export.export_id,
            user_id=export.user_id,
            export_timestamp=export.export_timestamp,
            data_controller=export.data_controller,
            data=export.data,
            metadata=export.metadata,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export user data: {e!s}"
        )


@router.post("/delete", response_model=DataDeletionResponse)
async def delete_user_data(
    request_body: DataDeletionRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    service: GDPRService = Depends(get_gdpr_service),
):
    """Delete all user data (GDPR Article 17 - Right to Erasure).

    Deletes all personal data held about the authenticated user.

    **GDPR Article 17 Requirements:**
    - Data is no longer necessary for the purposes
    - User withdraws consent
    - User objects to processing
    - Data has been unlawfully processed
    - Compliance with legal obligation

    **WARNING:** This action is irreversible (unless soft-delete is enabled).

    **Authentication:** Required (JWT token)

    **Confirmation:** Must set `confirm: true` to proceed

    **Rate Limiting:** 1 request per day per user recommended

    Args:
        request_body: Deletion request parameters
        request: FastAPI request
        user_id: Authenticated user ID (from JWT)
        service: GDPR service instance

    Returns:
        DataDeletionResponse with deletion result

    Raises:
        HTTPException 400: If confirm is not True
        HTTPException 401: If user is not authenticated
        HTTPException 500: If deletion fails
    """
    if not request_body.confirm:
        raise HTTPException(
            status_code=400,
            detail="Data deletion requires confirmation. Set 'confirm: true' to proceed."
        )

    try:
        # Delete user data
        result = await service.delete_user_data(
            user_id=user_id,
            data_sources=request_body.data_sources,
            confirm=request_body.confirm,
        )

        return DataDeletionResponse(
            deletion_id=result.deletion_id,
            user_id=result.user_id,
            deletion_timestamp=result.deletion_timestamp,
            success=result.success,
            items_deleted=result.items_deleted,
            errors=result.errors,
            metadata=result.metadata,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user data: {e!s}"
        )


@router.get("/privacy-policy", response_model=PrivacyPolicyResponse)
async def get_privacy_policy(
    service: GDPRService = Depends(get_gdpr_service),
):
    """Get privacy policy information (GDPR Article 13/14).

    Returns information about data processing that must be provided when
    collecting personal data.

    **GDPR Article 13/14 Requirements:**
    - Identity and contact details of controller
    - Purposes of processing and legal basis
    - Legitimate interests (if applicable)
    - Recipients or categories of recipients
    - International data transfers
    - Retention period
    - Data subject rights
    - Right to withdraw consent
    - Right to lodge complaint
    - Automated decision-making

    **Authentication:** Not required (public endpoint)

    Returns:
        PrivacyPolicyResponse with privacy policy information
    """
    policy = service.get_privacy_policy()

    return PrivacyPolicyResponse(
        data_controller=policy["data_controller"],
        data_processing=policy["data_processing"],
        data_subject_rights=policy["data_subject_rights"],
        data_categories=policy["data_categories"],
        data_recipients=policy["data_recipients"],
        international_transfers=policy["international_transfers"],
        automated_decision_making=policy["automated_decision_making"],
        contact=policy["contact"],
        effective_date=policy["effective_date"],
        version=policy["version"],
    )
