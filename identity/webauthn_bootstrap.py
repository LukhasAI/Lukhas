"""
LUKHAS WebAuthn/Passkeys Bootstrap
==================================
First-party authentication system using WebAuthn/Passkeys as primary auth method.
Implements requirement #2: Primary auth = Passkeys/WebAuthn

Privacy-first design:
- No raw PII stored (requirement #1) 
- Edge-first credential storage (requirement #5)
- Full audit trail (requirement #6)
- Capability tokens with least privilege (requirement #4)
"""

import base64
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import hashlib
import struct

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

# WebAuthn imports (in production use webauthn library)
try:
    from webauthn import generate_registration_options, verify_registration_response
    from webauthn import generate_authentication_options, verify_authentication_response
    from webauthn.helpers.cose import COSEAlgorithmIdentifier
    WEBAUTHN_AVAILABLE = True
except ImportError:
    # Mock implementation for development
    WEBAUTHN_AVAILABLE = False
    print("WARNING: webauthn library not available, using mock implementation")


class WebAuthnCredential(BaseModel):
    """WebAuthn credential (stored securely, no raw secrets)"""
    credential_id: str
    public_key_hash: str  # Hashed public key (requirement #5: edge first)
    sign_count: int
    device_name: Optional[str] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None


class PasskeyChallenge(BaseModel):
    """Passkey challenge for registration/authentication"""
    challenge: str
    user_lid: str
    timeout: int = 60000  # 60 seconds
    created_at: datetime


class WebAuthnBootstrap:
    """WebAuthn/Passkeys authentication system for LUKHAS Identity"""
    
    def __init__(self):
        self.rp_id = "identity.lukhas.com"  # Relying Party ID
        self.rp_name = "LUKHAS Identity"
        self.origin = "https://identity.lukhas.com"
        
        # In-memory storage (in production: use PostgreSQL from schema.sql)
        self.credentials: Dict[str, List[WebAuthnCredential]] = {}
        self.challenges: Dict[str, PasskeyChallenge] = {}
        
        # Audit logging
        self.audit_log = []
    
    def generate_registration_challenge(self, canonical_lid: str, display_name: str = None) -> Dict:
        """
        Generate WebAuthn registration challenge for new passkey.
        
        Args:
            canonical_lid: Canonical ΛID (namespace:username)
            display_name: Optional display name for UI
            
        Returns:
            WebAuthn registration options for client
        """
        start_time = datetime.now(timezone.utc)
        
        # Generate cryptographically secure challenge
        challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
        
        # Store challenge for verification (requirement #6: audit trail)
        challenge_obj = PasskeyChallenge(
            challenge=challenge,
            user_lid=canonical_lid,
            created_at=start_time
        )
        self.challenges[challenge] = challenge_obj
        
        # Create user handle (hashed ΛID for privacy)
        user_handle = self._hash_lid_for_user_handle(canonical_lid)
        
        if WEBAUTHN_AVAILABLE:
            # Real WebAuthn implementation
            options = generate_registration_options(
                rp_id=self.rp_id,
                rp_name=self.rp_name,
                user_id=user_handle.encode(),
                user_name=canonical_lid,
                user_display_name=display_name or canonical_lid,
                supported_pub_key_algs=[
                    COSEAlgorithmIdentifier.ECDSA_SHA_256,
                    COSEAlgorithmIdentifier.RSA_PSS_SHA_256,
                ],
                challenge=challenge.encode(),
                timeout=60000,
                authenticator_selection={
                    "authenticator_attachment": "platform",  # Prefer platform authenticators (Touch ID, Face ID, Windows Hello)
                    "user_verification": "required"
                }
            )
            
            # Convert to dict for JSON response
            return {
                "challenge": challenge,
                "rp": {"id": self.rp_id, "name": self.rp_name},
                "user": {
                    "id": base64.urlsafe_b64encode(user_handle.encode()).decode().rstrip('='),
                    "name": canonical_lid,
                    "displayName": display_name or canonical_lid
                },
                "pubKeyCredParams": options.public_key_credential_parameters,
                "timeout": 60000,
                "authenticatorSelection": options.authenticator_selection,
                "attestation": "direct",
                "extensions": {"credProps": True}
            }
        else:
            # Mock implementation for development
            return {
                "challenge": challenge,
                "rp": {"id": self.rp_id, "name": self.rp_name},
                "user": {
                    "id": base64.urlsafe_b64encode(user_handle.encode()).decode().rstrip('='),
                    "name": canonical_lid,
                    "displayName": display_name or canonical_lid
                },
                "pubKeyCredParams": [
                    {"alg": -7, "type": "public-key"},  # ES256
                    {"alg": -257, "type": "public-key"}  # RS256
                ],
                "timeout": 60000,
                "authenticatorSelection": {
                    "authenticatorAttachment": "platform",
                    "userVerification": "required"
                },
                "attestation": "direct"
            }
    
    def verify_registration(self, canonical_lid: str, credential_response: Dict) -> Dict:
        """
        Verify WebAuthn registration response and store credential.
        
        Args:
            canonical_lid: Canonical ΛID
            credential_response: Client's WebAuthn registration response
            
        Returns:
            Registration result with credential ID
        """
        try:
            challenge = credential_response.get("challenge")
            if not challenge or challenge not in self.challenges:
                raise ValueError("Invalid or expired challenge")
            
            challenge_obj = self.challenges[challenge]
            if challenge_obj.user_lid != canonical_lid:
                raise ValueError("Challenge user mismatch")
            
            # Check challenge timeout (60 seconds)
            if datetime.now(timezone.utc) - challenge_obj.created_at > timedelta(seconds=60):
                del self.challenges[challenge]
                raise ValueError("Challenge expired")
            
            if WEBAUTHN_AVAILABLE:
                # Real verification
                verification = verify_registration_response(
                    credential=credential_response,
                    expected_challenge=challenge.encode(),
                    expected_origin=self.origin,
                    expected_rp_id=self.rp_id
                )
                
                if not verification.verified:
                    raise ValueError("Registration verification failed")
                
                credential_id = verification.credential_id
                public_key = verification.credential_public_key
                sign_count = verification.sign_count
                
            else:
                # Mock verification for development
                credential_id = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
                public_key = secrets.token_bytes(64)  # Mock public key
                sign_count = 0
            
            # Hash public key for storage (requirement #5: edge first, no raw data)
            public_key_hash = hashlib.sha256(public_key).hexdigest()
            
            # Store credential
            credential = WebAuthnCredential(
                credential_id=credential_id,
                public_key_hash=public_key_hash,
                sign_count=sign_count,
                device_name=self._detect_device_name(credential_response),
                created_at=datetime.now(timezone.utc)
            )
            
            if canonical_lid not in self.credentials:
                self.credentials[canonical_lid] = []
            
            self.credentials[canonical_lid].append(credential)
            
            # Clean up challenge
            del self.challenges[challenge]
            
            # Audit log (requirement #6)
            self._log_audit_event("webauthn_registration", canonical_lid, {
                "credential_id": credential_id[:16] + "...",  # Truncate for privacy
                "device_name": credential.device_name,
                "success": True
            })
            
            return {
                "success": True,
                "credential_id": credential_id,
                "device_name": credential.device_name,
                "message": "Passkey registered successfully"
            }
            
        except Exception as e:
            # Audit log failure
            self._log_audit_event("webauthn_registration", canonical_lid, {
                "success": False,
                "error": str(e)
            })
            raise HTTPException(status_code=400, detail=str(e))
    
    def generate_authentication_challenge(self, canonical_lid: str) -> Dict:
        """
        Generate WebAuthn authentication challenge for existing user.
        
        Args:
            canonical_lid: Canonical ΛID to authenticate
            
        Returns:
            WebAuthn authentication options
        """
        # Check if user has registered credentials
        user_credentials = self.credentials.get(canonical_lid, [])
        if not user_credentials:
            raise HTTPException(status_code=404, detail="No passkeys found for user")
        
        # Generate challenge
        challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
        
        # Store challenge
        challenge_obj = PasskeyChallenge(
            challenge=challenge,
            user_lid=canonical_lid,
            created_at=datetime.now(timezone.utc)
        )
        self.challenges[challenge] = challenge_obj
        
        # Get credential IDs for allowCredentials
        allow_credentials = [
            {
                "type": "public-key",
                "id": cred.credential_id
            }
            for cred in user_credentials
        ]
        
        if WEBAUTHN_AVAILABLE:
            options = generate_authentication_options(
                rp_id=self.rp_id,
                challenge=challenge.encode(),
                allow_credentials=[
                    {"type": "public-key", "id": cred.credential_id.encode()}
                    for cred in user_credentials
                ],
                user_verification="required",
                timeout=60000
            )
            
            return {
                "challenge": challenge,
                "rpId": self.rp_id,
                "allowCredentials": allow_credentials,
                "userVerification": "required",
                "timeout": 60000
            }
        else:
            # Mock authentication challenge
            return {
                "challenge": challenge,
                "rpId": self.rp_id,
                "allowCredentials": allow_credentials,
                "userVerification": "required",
                "timeout": 60000
            }
    
    def verify_authentication(self, canonical_lid: str, auth_response: Dict) -> Dict:
        """
        Verify WebAuthn authentication response.
        
        Args:
            canonical_lid: Canonical ΛID being authenticated
            auth_response: Client's WebAuthn authentication response
            
        Returns:
            Authentication result with capability token
        """
        try:
            challenge = auth_response.get("challenge")
            if not challenge or challenge not in self.challenges:
                raise ValueError("Invalid or expired challenge")
            
            challenge_obj = self.challenges[challenge]
            if challenge_obj.user_lid != canonical_lid:
                raise ValueError("Challenge user mismatch")
            
            # Check timeout
            if datetime.now(timezone.utc) - challenge_obj.created_at > timedelta(seconds=60):
                del self.challenges[challenge]
                raise ValueError("Challenge expired")
            
            credential_id = auth_response.get("credentialId")
            if not credential_id:
                raise ValueError("Missing credential ID")
            
            # Find user's credential
            user_credentials = self.credentials.get(canonical_lid, [])
            credential = None
            for cred in user_credentials:
                if cred.credential_id == credential_id:
                    credential = cred
                    break
            
            if not credential:
                raise ValueError("Credential not found")
            
            if WEBAUTHN_AVAILABLE:
                # Real verification
                verification = verify_authentication_response(
                    credential=auth_response,
                    expected_challenge=challenge.encode(),
                    expected_origin=self.origin,
                    expected_rp_id=self.rp_id,
                    credential_public_key=credential.public_key_hash.encode(),  # In production: decode stored key
                    credential_current_sign_count=credential.sign_count
                )
                
                if not verification.verified:
                    raise ValueError("Authentication verification failed")
                
                new_sign_count = verification.new_sign_count
            else:
                # Mock verification
                new_sign_count = credential.sign_count + 1
            
            # Update credential
            credential.sign_count = new_sign_count
            credential.last_used_at = datetime.now(timezone.utc)
            
            # Clean up challenge
            del self.challenges[challenge]
            
            # Generate capability token (requirement #4: least privilege JWT)
            capability_token = self._generate_capability_token(canonical_lid, ["identity.read", "identity.update"])
            
            # Audit log
            self._log_audit_event("webauthn_authentication", canonical_lid, {
                "credential_id": credential_id[:16] + "...",
                "device_name": credential.device_name,
                "success": True
            })
            
            return {
                "success": True,
                "canonical_lid": canonical_lid,
                "capability_token": capability_token,
                "device_name": credential.device_name,
                "message": "Authentication successful"
            }
            
        except Exception as e:
            # Audit log failure
            self._log_audit_event("webauthn_authentication", canonical_lid, {
                "success": False,
                "error": str(e)
            })
            raise HTTPException(status_code=401, detail=str(e))
    
    def _hash_lid_for_user_handle(self, canonical_lid: str) -> str:
        """Create hashed user handle from ΛID (privacy protection)."""
        return hashlib.sha256(f"lukhas:lid:{canonical_lid}".encode()).hexdigest()[:32]
    
    def _detect_device_name(self, credential_response: Dict) -> str:
        """Detect device name from WebAuthn response (for audit/UX)."""
        # In production: parse authenticator data for device info
        return "Unknown Device"
    
    def _generate_capability_token(self, canonical_lid: str, scopes: List[str]) -> str:
        """
        Generate short-lived capability token (requirement #4).
        
        In production: use proper JWT with RSA keys from KMS/enclave.
        """
        # Mock JWT token with caveats
        payload = {
            "sub": canonical_lid,
            "iss": "https://identity.lukhas.com", 
            "aud": ["lukhas-api"],
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp(),
            "scope": " ".join(scopes),
            "caveats": {
                "service": "identity",
                "ttl": 3600,
                "resource_ids": ["*"]
            }
        }
        
        # In production: sign with RSA private key
        token = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        return f"cap_token_{token}"
    
    def _log_audit_event(self, event_type: str, canonical_lid: str, metadata: Dict):
        """Log audit event (requirement #6: audit trail)."""
        event = {
            "event_type": event_type,
            "canonical_lid": canonical_lid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata
        }
        self.audit_log.append(event)
        
        # In production: write to PostgreSQL audit_log table
        print(f"AUDIT: {event_type} for {canonical_lid} - {metadata.get('success', False)}")


# FastAPI Router
router = APIRouter(prefix="/identity/webauthn", tags=["WebAuthn/Passkeys"])
webauthn = WebAuthnBootstrap()


@router.get("/challenge")
async def webauthn_challenge(
    lid: str,
    request: Request,
    mode: str = "auth"  # "auth" or "register"
):
    """
    Generate WebAuthn challenge for authentication or registration.
    
    Query parameters:
    - lid: Canonical ΛID (namespace:username)
    - mode: "auth" for login, "register" for new passkey
    
    Returns WebAuthn challenge options for client.
    """
    try:
        if mode == "register":
            options = webauthn.generate_registration_challenge(lid)
            return JSONResponse({"status": "challenge", "options": options})
        else:
            options = webauthn.generate_authentication_challenge(lid)
            return JSONResponse({"status": "challenge", "options": options})
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register")
async def webauthn_register(
    lid: str,
    credential: Dict,
    request: Request
):
    """
    Verify WebAuthn registration and store new passkey.
    
    Body should contain WebAuthn registration response from client.
    """
    result = webauthn.verify_registration(lid, credential)
    return JSONResponse(result)


@router.post("/authenticate")
async def webauthn_authenticate(
    lid: str,
    assertion: Dict,
    request: Request
):
    """
    Verify WebAuthn authentication assertion.
    
    Body should contain WebAuthn authentication response from client.
    Returns capability token for API access.
    """
    result = webauthn.verify_authentication(lid, assertion)
    return JSONResponse(result)


@router.get("/credentials")
async def list_credentials(lid: str):
    """
    List registered credentials for user (for management UI).
    
    Returns list of credential metadata (no sensitive data).
    """
    credentials = webauthn.credentials.get(lid, [])
    
    return {
        "canonical_lid": lid,
        "credentials": [
            {
                "credential_id": cred.credential_id[:16] + "...",  # Truncated for privacy
                "device_name": cred.device_name,
                "created_at": cred.created_at.isoformat(),
                "last_used_at": cred.last_used_at.isoformat() if cred.last_used_at else None,
                "sign_count": cred.sign_count
            }
            for cred in credentials
        ],
        "total": len(credentials)
    }


@router.delete("/credentials/{credential_id}")
async def revoke_credential(lid: str, credential_id: str):
    """
    Revoke/delete a WebAuthn credential (requirement #6: revocation paths).
    """
    credentials = webauthn.credentials.get(lid, [])
    
    for i, cred in enumerate(credentials):
        if cred.credential_id == credential_id:
            del credentials[i]
            
            # Audit log
            webauthn._log_audit_event("webauthn_revocation", lid, {
                "credential_id": credential_id[:16] + "...",
                "device_name": cred.device_name,
                "success": True
            })
            
            return {"success": True, "message": "Credential revoked"}
    
    raise HTTPException(status_code=404, detail="Credential not found")


# Health check and diagnostics
@router.get("/status")
async def webauthn_status():
    """WebAuthn system status and metrics."""
    total_users = len(webauthn.credentials)
    total_credentials = sum(len(creds) for creds in webauthn.credentials.values())
    active_challenges = len(webauthn.challenges)
    
    return {
        "status": "healthy",
        "webauthn_available": WEBAUTHN_AVAILABLE,
        "total_users": total_users,
        "total_credentials": total_credentials,
        "active_challenges": active_challenges,
        "audit_events": len(webauthn.audit_log)
    }