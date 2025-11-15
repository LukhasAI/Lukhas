"""Identity API - Stub Implementation"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter

router = None


def authenticate(credentials):
    return {"authenticated": True, "token": "stub_token"}


__all__ = ["router", "authenticate"]
