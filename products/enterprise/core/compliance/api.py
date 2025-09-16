"""
LUKHAS Data Protection API
========================
FastAPI endpoints for data protection services.
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .data_protection_service import DataProtectionService, ProtectionPolicy


class ProtectRequest(BaseModel):
    data: Any
    policy_id: str
    context: Optional[dict[str, Any]] = None


class UnprotectRequest(BaseModel):
    data: Any
    context: Optional[dict[str, Any]] = None


# Global data protection service instance
data_protection_service: Optional[DataProtectionService] = None


async def get_data_protection_service() -> DataProtectionService:
    """Dependency to get data protection service instance"""
    global data_protection_service
    if data_protection_service is None:
        data_protection_service = DataProtectionService()
        await data_protection_service.initialize()
    return data_protection_service


router = APIRouter(prefix="/protection", tags=["Data Protection"])
user_router = APIRouter(prefix="/users", tags=["User Data"])


@router.post("/protect")
async def protect_data(
    request_data: ProtectRequest,
    service: DataProtectionService = Depends(get_data_protection_service),
):
    """Protect data based on a policy."""
    try:
        protected_data, result = await service.protect_data(
            request_data.data, request_data.policy_id, request_data.context
        )
        return {"protected_data": protected_data, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Protection failed: {e!s}")


@router.post("/unprotect")
async def unprotect_data(
    request_data: UnprotectRequest,
    service: DataProtectionService = Depends(get_data_protection_service),
):
    """Unprotect data."""
    try:
        unprotected_data = await service.unprotect_data(request_data.data, request_data.context)
        return {"unprotected_data": unprotected_data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unprotection failed: {e!s}")


from consent.api import get_consent_service
from consent.service import ConsentService


@router.get("/policies", response_model=list[ProtectionPolicy])
async def list_policies(service: DataProtectionService = Depends(get_data_protection_service)):
    """List all protection policies."""
    return list(service.protection_policies.values())


@user_router.get("/{user_lid}/export")
async def export_user_data(
    user_lid: str,
    consent_service: ConsentService = Depends(get_consent_service),
    data_protection_service: DataProtectionService = Depends(get_data_protection_service),
):
    """Export all data for a user."""
    consent_grants = await consent_service.get_all_user_consent_grants(user_lid)
    protected_data = await data_protection_service.get_user_data(user_lid)

    return {
        "user_lid": user_lid,
        "consent_grants": consent_grants,
        "protected_data": protected_data,
    }


@user_router.delete("/{user_lid}")
async def delete_user_data(
    user_lid: str,
    consent_service: ConsentService = Depends(get_consent_service),
    data_protection_service: DataProtectionService = Depends(get_data_protection_service),
):
    """Delete all data for a user."""
    deleted_grants = await consent_service.delete_user_consent_grants(user_lid)
    deleted_data = await data_protection_service.delete_user_data(user_lid)

    return {
        "user_lid": user_lid,
        "deleted_consent_grants": deleted_grants,
        "deleted_protected_data_entries": deleted_data,
    }


@user_router.put("/{user_lid}")
async def update_user_data(
    user_lid: str,
    updates: dict,
    consent_service: ConsentService = Depends(get_consent_service),
    data_protection_service: DataProtectionService = Depends(get_data_protection_service),
):
    """Update user data."""
    # This is a simplified implementation. In a real system, we would need to
    # identify which grants and data entries to update based on the request.
    updated_grants = await consent_service.update_consent_grant("some_grant_id", updates)
    updated_data = await data_protection_service.update_protected_data("some_operation_id", updates)

    return {
        "user_lid": user_lid,
        "updated_consent_grants": updated_grants,
        "updated_protected_data_entries": updated_data,
    }


from .data_protection_service import DataProcessingActivity, GDPRAssessment


@router.post("/assessment", response_model=GDPRAssessment)
async def assess_processing_activity(
    activity: DataProcessingActivity,
    service: DataProtectionService = Depends(get_data_protection_service),
):
    """Assess the compliance of a data processing activity."""
    return await service.assess_processing_activity(activity)


@router.get("/users/{user_lid}/audit_trail")
async def get_user_audit_trail(user_lid: str, consent_service: ConsentService = Depends(get_consent_service)):
    """Get the audit trail for a user."""
    audit_trail = await consent_service.get_user_audit_trail(user_lid)
    return {"user_lid": user_lid, "audit_trail": audit_trail}
