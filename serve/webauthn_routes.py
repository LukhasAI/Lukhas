"""WebAuthn Routes - Stub Implementation"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter

router = None


def register_credential(data):
    return {"success": True, "credential_id": "stub_cred"}


__all__ = ["router", "register_credential"]
