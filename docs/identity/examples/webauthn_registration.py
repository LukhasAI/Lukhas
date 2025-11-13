#!/usr/bin/env python3
"""
WebAuthn Registration Example (Backend - Python)

Complete server-side implementation of WebAuthn credential registration flow.
This example demonstrates:
1. Generating registration options
2. Sending challenge to frontend
3. Receiving credential from frontend
4. Verifying attestation
5. Storing credential

Prerequisites:
- Python 3.9+
- FastAPI
- webauthn library
- LUKHAS identity modules

Usage:
    python webauthn_registration.py

Then POST to /api/auth/webauthn/register/begin and /api/auth/webauthn/register/complete

Constellation Framework: Identity ⚛️ pillar
W3C WebAuthn Level 2 Specification: https://www.w3.org/TR/webauthn-2/
"""
import base64
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# External dependencies
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# WebAuthn library
from webauthn import verify_registration_response
from webauthn.helpers import base64url_to_bytes

# LUKHAS imports
try:
    from lukhas_website.lukhas.identity.webauthn_types import (
        AuthenticatorSelectionCriteria,
        CredentialCreationOptions,
        PublicKeyCredentialCreation,
        PublicKeyCredentialParameters,
        PublicKeyCredentialRpEntity,
        PublicKeyCredentialUserEntity,
    )

    from lukhas.identity.webauthn_credential import WebAuthnCredentialStore
except ImportError:
    print("Note: LUKHAS modules not available. Using simplified types.")
    # Fallback type definitions for testing without LUKHAS installed
    class WebAuthnCredentialStore:
        def __init__(self):
            self._credentials = {}

        def store_credential(self, user_id: str, credential: Dict) -> None:
            self._credentials[credential["credential_id"]] = credential

        def get_credential(self, credential_id: str) -> Optional[Dict]:
            return self._credentials.get(credential_id)

        def list_credentials(self, user_id: str) -> List[Dict]:
            return [c for c in self._credentials.values() if c.get("user_id") == user_id]


# Configuration
RP_ID = "localhost"              # Relying Party ID (your domain)
RP_NAME = "LUKHAS Demo App"      # Relying Party name
ORIGIN = "http://localhost:5000" # Expected origin (HTTPS in production)
TIMEOUT_MS = 60000               # Registration timeout (60 seconds)


@dataclass
class RegistrationSession:
    """Stores registration challenge and metadata."""
    user_id: str
    username: str
    challenge: str
    created_at: str
    ip_address: str = ""


# In-memory storage for challenges and credentials
# In production, use a database with session/credential tables
challenge_store: Dict[str, RegistrationSession] = {}
credential_store = WebAuthnCredentialStore()

# In-memory user database (for demo)
users_db: Dict[str, Dict] = {
    "testuser": {
        "user_id": "user_123",
        "username": "testuser@example.com",
        "display_name": "Test User"
    }
}

# Initialize FastAPI app
app = FastAPI(title="WebAuthn Registration Service")

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_registration_options(
    user_id: str,
    username: str,
    display_name: str,
    rp_id: str = RP_ID,
    rp_name: str = RP_NAME,
    timeout_ms: int = TIMEOUT_MS,
    require_resident_key: bool = False
) -> Tuple[CredentialCreationOptions, str]:
    """Generate WebAuthn registration options.

    Generates a cryptographically secure challenge and builds the credential
    creation options to send to the frontend. The challenge must be stored
    on the server for later verification.

    Args:
        user_id: Unique user identifier (e.g., database ID or ΛID)
        username: User's username or email address
        display_name: User's display name (can include Unicode)
        rp_id: Relying Party ID (your domain)
        rp_name: Relying Party name (app name)
        timeout_ms: Time in milliseconds user has to complete registration
        require_resident_key: If True, credential must be stored on authenticator

    Returns:
        Tuple of (credential_creation_options, challenge_string)

    Security Notes:
        - Challenge must be cryptographically random
        - Challenge must be stored securely on server
        - Challenge should expire after timeout
        - Challenge can only be used once
    """
    # Generate cryptographically secure challenge (256 bits = 32 bytes)
    challenge_bytes = secrets.token_bytes(32)
    challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')

    # Encode user ID as base64url
    user_id_bytes = user_id.encode('utf-8')
    user_id_encoded = base64.urlsafe_b64encode(user_id_bytes).decode('utf-8').rstrip('=')

    # Relying Party entity
    rp: PublicKeyCredentialRpEntity = {
        "name": rp_name,
        "id": rp_id
    }

    # User entity
    user: PublicKeyCredentialUserEntity = {
        "id": user_id_encoded,
        "name": username,
        "displayName": display_name
    }

    # Supported public key algorithms (in COSE format)
    # Recommendation order: prefer ES256, fallback to RS256, EdDSA
    pub_key_cred_params: List[PublicKeyCredentialParameters] = [
        {"type": "public-key", "alg": -7},     # ES256: ECDSA with SHA-256 (Recommended)
        {"type": "public-key", "alg": -257},   # RS256: RSA with SHA-256 (Fallback)
        {"type": "public-key", "alg": -8},     # EdDSA: Edwards-curve DSA (Fallback)
    ]

    # Authenticator selection criteria
    authenticator_selection: AuthenticatorSelectionCriteria = {
        "authenticatorAttachment": "platform",  # Prefer platform authenticators (Face ID, Touch ID)
        "residentKey": "preferred" if not require_resident_key else "required",
        "userVerification": "preferred"  # Require user verification (biometric/PIN)
    }

    # Build credential creation options
    options: CredentialCreationOptions = {
        "challenge": challenge,
        "rp": rp,
        "user": user,
        "pubKeyCredParams": pub_key_cred_params,
        "timeout": timeout_ms,
        "excludeCredentials": [],  # Will be populated with existing credentials
        "authenticatorSelection": authenticator_selection,
        "attestation": "direct",  # Request attestation statement
        "extensions": {}  # No extensions used in this example
    }

    return options, challenge


def verify_credential_registration(
    credential: PublicKeyCredentialCreation,
    expected_challenge: str,
    expected_origin: str,
    expected_rp_id: str
) -> Dict:
    """Verify WebAuthn registration response.

    Performs cryptographic verification of the credential returned from
    navigator.credentials.create(). This validates:
    - Challenge matches
    - Origin is correct
    - RP ID is correct
    - Attestation statement is valid

    Args:
        credential: Credential response from frontend
        expected_challenge: Challenge originally sent to frontend
        expected_origin: Expected origin (HTTPS domain)
        expected_rp_id: Expected Relying Party ID

    Returns:
        Dictionary with verified credential data:
        {
            "credential_id": str,
            "public_key": str,
            "counter": int,
            "aaguid": Optional[str],
            "transports": List[str],
            "backup_eligible": bool,
            "backup_state": bool,
            "user_verified": bool
        }

    Raises:
        ValueError: If verification fails

    Security Notes:
        - Verification must happen on server (never trust client)
        - Use validated webauthn library for cryptographic checks
        - Check that origin matches exactly
        - Validate attestation statement if needed
    """
    try:
        # Decode challenge for comparison
        challenge_bytes = base64url_to_bytes(expected_challenge)

        # Call webauthn library to verify the credential
        # This performs all cryptographic validation
        verified = verify_registration_response(
            credential=credential,
            expected_challenge=challenge_bytes,
            expected_origin=expected_origin,
            expected_rp_id=expected_rp_id,
            require_user_verification=True  # Enforce user verification
        )

        if not verified.verified:
            raise ValueError("Credential verification returned False")

        # Extract verified data
        return {
            "credential_id": verified.credential_id.hex(),
            "public_key": verified.credential_public_key.hex(),
            "counter": verified.sign_count,
            "aaguid": verified.aaguid.hex() if verified.aaguid else None,
            "transports": credential.get("response", {}).get("transports", []),
            "backup_eligible": getattr(verified, 'backup_eligible', False),
            "backup_state": getattr(verified, 'backup_state', False),
            "user_verified": getattr(verified, 'user_verified', False)
        }

    except Exception as e:
        raise ValueError(f"Registration verification failed: {e!s}")


# --- API Endpoints ---

@app.post("/api/auth/webauthn/register/begin")
async def start_registration(request_data: Dict) -> JSONResponse:
    """Start WebAuthn registration process.

    This endpoint is called from the frontend to initiate registration.
    It returns registration options that are passed to navigator.credentials.create().

    Request JSON:
    {
        "user_id": "string",          # Required: unique user identifier
        "username": "string",         # Required: email or username
        "display_name": "string"      # Optional: user's display name
    }

    Response JSON:
    {
        "challenge": "string",        # Challenge to sign
        "rp": {...},                  # Relying Party info
        "user": {...},                # User info
        "pubKeyCredParams": [...],    # Supported algorithms
        "timeout": 60000,             # Timeout in ms
        "attestation": "direct",      # Attestation mode
        ...
    }

    Error Responses:
    - 400: Missing required fields
    - 409: User already has maximum credentials registered
    """
    user_id = request_data.get("user_id")
    username = request_data.get("username")
    display_name = request_data.get("display_name", username.split('@')[0] if username else "User")

    # Validation
    if not user_id or not username:
        raise HTTPException(status_code=400, detail="user_id and username are required")

    if not isinstance(user_id, str) or not isinstance(username, str):
        raise HTTPException(status_code=400, detail="user_id and username must be strings")

    # Optional: Check maximum credentials per user (e.g., 10 max)
    existing_creds = credential_store.list_credentials(user_id)
    if len(existing_creds) >= 10:
        raise HTTPException(status_code=409, detail="Maximum credentials reached")

    # Generate registration options
    try:
        options, challenge = generate_registration_options(
            user_id=user_id,
            username=username,
            display_name=display_name
        )

        # Populate excludeCredentials with user's existing credentials
        options["excludeCredentials"] = [
            {
                "type": "public-key",
                "id": cred["credential_id"],
                "transports": cred.get("transports", [])
            }
            for cred in existing_creds
        ]

        # Store challenge in session for later verification
        challenge_store[user_id] = RegistrationSession(
            user_id=user_id,
            username=username,
            challenge=challenge,
            created_at=datetime.now(timezone.utc).isoformat()
        )

        # Return options to frontend
        return JSONResponse(content=options)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate options: {e!s}")


@app.post("/api/auth/webauthn/register/complete")
async def complete_registration(request_data: Dict) -> JSONResponse:
    """Complete WebAuthn registration process.

    This endpoint is called from the frontend after the user has created
    a credential using navigator.credentials.create(). It verifies the
    credential and stores it.

    Request JSON:
    {
        "user_id": "string",          # Required: user identifier
        "credential": {...},          # Required: credential from navigator.credentials.create()
        "device_name": "string"       # Optional: user-friendly device name
    }

    Response JSON:
    {
        "status": "success",
        "credential_id": "string",
        "message": "Registration complete"
    }

    Error Responses:
    - 400: Missing fields or verification failed
    - 403: Unauthorized (user_id mismatch)
    - 404: Challenge not found (expired or invalid user)
    - 500: Server error
    """
    user_id = request_data.get("user_id")
    credential = request_data.get("credential")
    device_name = request_data.get("device_name", "My Device")

    # Validation
    if not user_id or not credential:
        raise HTTPException(status_code=400, detail="user_id and credential are required")

    # Check if challenge exists (prevents replay attacks)
    if user_id not in challenge_store:
        raise HTTPException(status_code=404, detail="Registration session not found")

    session = challenge_store[user_id]

    # Verify challenge hasn't expired (optional - implement timeout check)
    created = datetime.fromisoformat(session.created_at)
    age_seconds = (datetime.now(timezone.utc) - created).total_seconds()
    if age_seconds > 600:  # 10 minute timeout
        del challenge_store[user_id]
        raise HTTPException(status_code=400, detail="Registration session expired")

    # Verify the credential
    try:
        verified_data = verify_credential_registration(
            credential=credential,
            expected_challenge=session.challenge,
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {e!s}")

    # Store credential in database
    try:
        credential_store.store_credential(
            user_id=user_id,
            credential={
                "credential_id": verified_data["credential_id"],
                "public_key": verified_data["public_key"],
                "counter": verified_data["counter"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "device_name": device_name,
                "aaguid": verified_data.get("aaguid"),
                "transports": verified_data.get("transports", []),
                "backup_eligible": verified_data.get("backup_eligible", False),
                "backup_state": verified_data.get("backup_state", False),
                "metadata": {
                    "registration_ip": "127.0.0.1",  # Would come from request
                    "user_agent": "Mozilla/5.0..."   # Would come from request
                }
            }
        )

        # Clean up challenge
        del challenge_store[user_id]

        return JSONResponse({
            "status": "success",
            "credential_id": verified_data["credential_id"],
            "message": "Registration complete"
        })

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store credential: {e!s}")


@app.get("/api/auth/webauthn/credentials")
async def list_credentials(user_id: str) -> JSONResponse:
    """List all WebAuthn credentials for a user.

    Query Parameters:
    - user_id (required): User identifier

    Response JSON:
    {
        "count": 2,
        "credentials": [
            {
                "credential_id": "string",
                "device_name": "string",
                "created_at": "2024-11-02T00:00:00Z",
                "last_used": "2024-11-02T12:00:00Z",
                "transports": ["usb", "nfc"]
            }
        ]
    }
    """
    credentials = credential_store.list_credentials(user_id)

    return JSONResponse({
        "count": len(credentials),
        "credentials": [
            {
                "credential_id": cred["credential_id"],
                "device_name": cred.get("device_name", "Unknown Device"),
                "created_at": cred["created_at"],
                "last_used": cred.get("last_used"),
                "transports": cred.get("transports", []),
                "backup_eligible": cred.get("backup_eligible", False)
            }
            for cred in credentials
        ]
    })


@app.delete("/api/auth/webauthn/credentials/{credential_id}")
async def delete_credential(user_id: str, credential_id: str) -> JSONResponse:
    """Delete a WebAuthn credential.

    Query Parameters:
    - user_id (required): User identifier

    Path Parameters:
    - credential_id (required): Credential to delete

    Response JSON:
    {
        "status": "success",
        "message": "Credential deleted"
    }
    """
    credential = credential_store.get_credential(credential_id)

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Verify ownership
    if credential.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Delete credential
    if credential_store.delete_credential(credential_id):
        return JSONResponse({
            "status": "success",
            "message": "Credential deleted"
        })

    raise HTTPException(status_code=500, detail="Failed to delete credential")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({"status": "healthy"})


if __name__ == "__main__":
    import uvicorn

    print("Starting WebAuthn Registration Service...")
    print(f"RP_ID: {RP_ID}")
    print(f"ORIGIN: {ORIGIN}")
    print("Visit http://localhost:5000/docs for API documentation")

    uvicorn.run(app, host="0.0.0.0", port=5000)
