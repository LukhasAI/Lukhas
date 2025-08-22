from __future__ import annotations
import os
from typing import Dict, Any, Optional
from lukhas.observability.matriz_decorators import instrument

# Feature flag for WebAuthn
WEBAUTHN_ACTIVE = os.environ.get("WEBAUTHN_ACTIVE", "false").lower() == "true"

# Conditional import of WebAuthn implementation
_webauthn_manager = None
if WEBAUTHN_ACTIVE:
    try:
        from lukhas.identity.webauthn import WebAuthnManager
        _webauthn_manager = WebAuthnManager()
    except ImportError:
        pass

@instrument("DECISION", label="auth:lambda_id", capability="identity:auth")
def authenticate(lid: str, credential: Dict[str, Any] | None = None, *, mode: str="dry_run", **kwargs) -> Dict[str, Any]:
    """Authenticate with Lambda ID or WebAuthn"""
    if not isinstance(lid, str) or len(lid) < 3:
        return {"ok": False, "reason": "invalid_lid"}
    
    if mode != "dry_run" and WEBAUTHN_ACTIVE and _webauthn_manager:
        # Check if this is a WebAuthn authentication
        if credential and credential.get("type") == "webauthn":
            auth_result = _webauthn_manager.verify_authentication_response(
                authentication_id=credential.get("authentication_id"),
                response=credential.get("response", {})
            )
            return {
                "ok": auth_result.get("success", False),
                "user": {"lid": auth_result.get("user_id", lid)},
                "method": "webauthn",
                "tier_level": auth_result.get("tier_level", 0)
            }
    
    return {"ok": True, "user": {"lid": lid}, "method": "dry_run"}

@instrument("AWARENESS", label="auth:register", capability="identity:register")
def register_passkey(user_id: str, user_name: str, display_name: str, *, mode: str="dry_run", **kwargs) -> Dict[str, Any]:
    """Register a WebAuthn passkey"""
    if mode != "dry_run" and WEBAUTHN_ACTIVE and _webauthn_manager:
        result = _webauthn_manager.generate_registration_options(
            user_id=user_id,
            user_name=user_name,
            user_display_name=display_name,
            user_tier=kwargs.get("tier", 0)
        )
        return {
            "ok": result.get("success", False),
            "registration_id": result.get("registration_id"),
            "options": result.get("options"),
            "expires_at": result.get("expires_at")
        }
    
    return {"ok": True, "status": "registration_initiated(dry_run)"}

@instrument("DECISION", label="auth:passkey", capability="identity:passkey")
def verify_passkey(registration_id: str, response: Dict[str, Any], *, mode: str="dry_run", **kwargs) -> Dict[str, Any]:
    """Verify a WebAuthn passkey registration"""
    if mode != "dry_run" and WEBAUTHN_ACTIVE and _webauthn_manager:
        result = _webauthn_manager.verify_registration_response(
            registration_id=registration_id,
            response=response
        )
        return {
            "ok": result.get("success", False),
            "credential_id": result.get("credential_id"),
            "user_id": result.get("user_id"),
            "tier_level": result.get("tier_level", 0)
        }
    
    return {"ok": True, "status": "verified(dry_run)"}

@instrument("AWARENESS", label="auth:list", capability="identity:list")
def list_credentials(user_id: str, *, mode: str="dry_run", **kwargs) -> Dict[str, Any]:
    """List WebAuthn credentials for a user"""
    if mode != "dry_run" and WEBAUTHN_ACTIVE and _webauthn_manager:
        result = _webauthn_manager.get_user_credentials(user_id)
        return {
            "ok": result.get("success", False),
            "credentials": result.get("credentials", []),
            "total": result.get("total_credentials", 0)
        }
    
    return {"ok": True, "credentials": [], "total": 0}

@instrument("DECISION", label="auth:revoke", capability="identity:revoke")
def revoke_credential(user_id: str, credential_id: str, *, mode: str="dry_run", **kwargs) -> Dict[str, Any]:
    """Revoke a WebAuthn credential"""
    if mode != "dry_run" and WEBAUTHN_ACTIVE and _webauthn_manager:
        result = _webauthn_manager.revoke_credential(user_id, credential_id)
        return {
            "ok": result.get("success", False),
            "revoked_at": result.get("revoked_at")
        }
    
    return {"ok": True, "status": "revoked(dry_run)"}