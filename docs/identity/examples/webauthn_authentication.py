#!/usr/bin/env python3
"""
WebAuthn Authentication Example (Backend - Python)

Complete server-side implementation of WebAuthn credential authentication flow.
This example demonstrates:
1. Generating authentication options (challenge)
2. Sending options to frontend
3. Receiving assertion from frontend
4. Verifying signature
5. Updating sign counter to prevent replay attacks

Prerequisites:
- Python 3.9+
- FastAPI
- webauthn library
- LUKHAS identity modules

Usage:
    python webauthn_authentication.py

Then POST to /api/auth/webauthn/authenticate/begin and /api/auth/webauthn/authenticate/complete

Constellation Framework: Identity ⚛️ pillar
W3C WebAuthn Level 2 Specification: https://www.w3.org/TR/webauthn-2/
"""
import base64
import secrets
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# External dependencies
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# WebAuthn library
from webauthn import verify_authentication_response
from webauthn.helpers import base64url_to_bytes

# LUKHAS imports (same as registration example)
try:
    from lukhas.identity.webauthn_credential import WebAuthnCredentialStore
    from lukhas_website.lukhas.identity.webauthn_types import (
        CredentialRequestOptions,
        PublicKeyCredentialAssertion,
    )
except ImportError:
    print("Note: LUKHAS modules not available. Using simplified types.")

    class WebAuthnCredentialStore:
        def __init__(self):
            self._credentials = {}

        def get_credential(self, credential_id: str) -> Optional[Dict]:
            return self._credentials.get(credential_id)

        def list_credentials(self, user_id: str) -> List[Dict]:
            return [c for c in self._credentials.values() if c.get("user_id") == user_id]

        def update_credential(self, credential_id: str, updates: Dict) -> bool:
            if credential_id in self._credentials:
                self._credentials[credential_id].update(updates)
                return True
            return False


# Configuration
RP_ID = "localhost"  # Relying Party ID (your domain)
ORIGIN = "http://localhost:5000"  # Expected origin (HTTPS in production)
TIMEOUT_MS = 60000  # Authentication timeout (60 seconds)


@dataclass
class AuthenticationSession:
    """Stores authentication challenge and metadata."""

    username: str
    challenge: str
    created_at: str
    ip_address: str = ""


# In-memory storage for challenges
# In production, use a database with session table
challenge_store: Dict[str, AuthenticationSession] = {}
credential_store = WebAuthnCredentialStore()

# Initialize FastAPI app
app = FastAPI(title="WebAuthn Authentication Service")

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_authentication_options(
    username: str, rp_id: str = RP_ID, timeout_ms: int = TIMEOUT_MS, user_verification: str = "preferred"
) -> Tuple[CredentialRequestOptions, str]:
    """Generate WebAuthn authentication options.

    Generates a cryptographically secure challenge for the user to sign
    with their authenticator. The challenge must be stored on the server
    for later verification.

    Args:
        username: Username or email to authenticate
        rp_id: Relying Party ID (your domain)
        timeout_ms: Time in milliseconds user has to complete authentication
        user_verification: "required", "preferred", or "discouraged"
            - "required": Must have biometric/PIN (strongest security)
            - "preferred": Try to get verification but allow fallback
            - "discouraged": Don't require verification (lowest security)

    Returns:
        Tuple of (credential_request_options, challenge_string)

    Security Notes:
        - Challenge must be cryptographically random
        - Challenge must be stored securely on server
        - Challenge should expire after timeout
        - Challenge can only be used once
        - Use "preferred" or "required" for user_verification when possible
    """
    # Generate cryptographically secure challenge (256 bits = 32 bytes)
    challenge_bytes = secrets.token_bytes(32)
    challenge = base64.urlsafe_b64encode(challenge_bytes).decode("utf-8").rstrip("=")

    # Get user's registered credentials (empty list OK - user picks which to use)
    user_credentials = credential_store.list_credentials(username)

    # Build allow credentials list (hints which credentials can be used)
    allow_credentials = [
        {"type": "public-key", "id": cred["credential_id"], "transports": cred.get("transports", [])}
        for cred in user_credentials
    ]

    # Build authentication options
    options: CredentialRequestOptions = {
        "challenge": challenge,
        "timeout": timeout_ms,
        "rpId": rp_id,
        "allowCredentials": allow_credentials,
        "userVerification": user_verification,
        "extensions": {},
    }

    return options, challenge


def verify_credential_authentication(
    credential: PublicKeyCredentialAssertion,
    expected_challenge: str,
    expected_origin: str,
    expected_rp_id: str,
    username: str,
    credential_store: WebAuthnCredentialStore,
) -> Dict:
    """Verify WebAuthn authentication assertion.

    Performs cryptographic verification of the assertion (signature) returned
    from navigator.credentials.get(). This validates:
    - Challenge matches
    - Origin is correct
    - RP ID is correct
    - Signature is valid (using stored public key)
    - Sign counter increases (prevents replay/cloning attacks)

    Args:
        credential: Assertion response from frontend
        expected_challenge: Challenge originally sent to frontend
        expected_origin: Expected origin (HTTPS domain)
        expected_rp_id: Expected Relying Party ID
        username: Username being authenticated
        credential_store: Credential store to look up public key

    Returns:
        Dictionary with verified authentication data:
        {
            "new_sign_count": int,       # Updated counter
            "user_verified": bool,       # Was user verified?
            "backup_eligible": bool,     # Can credential be backed up?
            "backup_state": bool         # Is credential backed up?
        }

    Raises:
        ValueError: If verification fails
        HTTPException: If credential not found or ownership mismatch

    Security Notes:
        - Verification must happen on server (never trust client)
        - Use validated webauthn library for cryptographic checks
        - ALWAYS validate sign counter to prevent replay attacks
        - Check that origin matches exactly
        - Store updated sign counter back to database
    """
    # Find the credential being used
    credential_id = credential["id"]
    stored_credential = credential_store.get_credential(credential_id)

    if not stored_credential:
        raise HTTPException(status_code=400, detail="Credential not found")

    # Verify username matches (prevents using one user's credential for another)
    if stored_credential.get("user_id") != username:
        raise HTTPException(status_code=403, detail="Credential does not belong to this user")

    try:
        # Decode challenge for comparison
        challenge_bytes = base64url_to_bytes(expected_challenge)

        # Decode stored public key from hex
        public_key_bytes = bytes.fromhex(stored_credential["public_key"])

        # Call webauthn library to verify the assertion
        # This performs all cryptographic validation
        verified = verify_authentication_response(
            credential=credential,
            expected_challenge=challenge_bytes,
            expected_origin=expected_origin,
            expected_rp_id=expected_rp_id,
            credential_public_key=public_key_bytes,
            credential_current_sign_count=stored_credential["counter"],
            require_user_verification=True,  # Enforce user verification
        )

        if not verified.verified:
            raise ValueError("Authentication verification returned False")

        # CRITICAL: Check sign counter to prevent replay attacks
        # Sign counter must always increase
        if verified.new_sign_count <= stored_credential["counter"]:
            # This could indicate a cloned authenticator
            # Log security event and reject authentication
            raise ValueError(
                f"Sign counter invalid (possible cloned authenticator): "
                f"old={stored_credential['counter']}, new={verified.new_sign_count}"
            )

        # Extract verified data
        return {
            "new_sign_count": verified.new_sign_count,
            "user_verified": getattr(verified, "user_verified", False),
            "backup_eligible": getattr(verified, "backup_eligible", False),
            "backup_state": getattr(verified, "backup_state", False),
        }

    except ValueError as e:
        if "cloned authenticator" in str(e):
            # Log security alert for suspicious activity
            raise HTTPException(status_code=403, detail="Security check failed. Please re-register your device.")
        raise ValueError(f"Authentication verification failed: {str(e)}")


# --- API Endpoints ---


@app.post("/api/auth/webauthn/authenticate/begin")
async def start_authentication(request_data: Dict) -> JSONResponse:
    """Start WebAuthn authentication process.

    This endpoint is called from the frontend to initiate authentication.
    It returns authentication options (challenge) that are passed to
    navigator.credentials.get().

    Request JSON:
    {
        "username": "string"  # Required: username or email to authenticate
    }

    Response JSON:
    {
        "challenge": "string",           # Challenge to sign
        "rpId": "example.com",           # Relying Party ID
        "allowCredentials": [...],       # Credentials user can use
        "userVerification": "preferred", # User verification requirement
        "timeout": 60000                 # Timeout in ms
    }

    Error Responses:
    - 400: Missing username
    - 404: User not found or has no registered credentials
    """
    username = request_data.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="username is required")

    if not isinstance(username, str):
        raise HTTPException(status_code=400, detail="username must be a string")

    # Check if user has any registered credentials
    existing_creds = credential_store.list_credentials(username)
    if not existing_creds:
        # Note: In production, return same response even if user not found
        # (to prevent user enumeration attacks)
        raise HTTPException(status_code=404, detail="No credentials registered for this user")

    # Generate authentication options
    try:
        options, challenge = generate_authentication_options(
            username=username, user_verification="required"  # Require user verification for auth
        )

        # Store challenge in session for later verification
        challenge_store[username] = AuthenticationSession(
            username=username, challenge=challenge, created_at=datetime.now(timezone.utc).isoformat()
        )

        # Return options to frontend
        return JSONResponse(content=options)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate options: {str(e)}")


@app.post("/api/auth/webauthn/authenticate/complete")
async def complete_authentication(request_data: Dict) -> JSONResponse:
    """Complete WebAuthn authentication process.

    This endpoint is called from the frontend after the user has created
    an assertion using navigator.credentials.get(). It verifies the
    assertion and updates the credential's sign counter.

    Request JSON:
    {
        "username": "string",    # Required: username being authenticated
        "credential": {...}      # Required: assertion from navigator.credentials.get()
    }

    Response JSON:
    {
        "status": "success",
        "message": "Authentication successful",
        "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."  # Your auth token
    }

    Error Responses:
    - 400: Missing fields, verification failed, or session expired
    - 403: Unauthorized (credential mismatch, cloned authenticator detected)
    - 404: User or challenge not found
    - 500: Server error
    """
    username = request_data.get("username")
    credential = request_data.get("credential")

    # Validation
    if not username or not credential:
        raise HTTPException(status_code=400, detail="username and credential are required")

    # Check if challenge exists (prevents replay attacks)
    if username not in challenge_store:
        raise HTTPException(status_code=404, detail="Authentication session not found")

    session = challenge_store[username]

    # Verify challenge hasn't expired (optional - implement timeout check)
    created = datetime.fromisoformat(session.created_at)
    age_seconds = (datetime.now(timezone.utc) - created).total_seconds()
    if age_seconds > 600:  # 10 minute timeout
        del challenge_store[username]
        raise HTTPException(status_code=400, detail="Authentication session expired")

    # Verify the assertion
    try:
        verified_data = verify_credential_authentication(
            credential=credential,
            expected_challenge=session.challenge,
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
            username=username,
            credential_store=credential_store,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")

    # Update sign counter in database (prevents replay attacks)
    credential_id = credential["id"]
    try:
        updated = credential_store.update_credential(
            credential_id=credential_id,
            updates={"counter": verified_data["new_sign_count"], "last_used": datetime.now(timezone.utc).isoformat()},
        )

        if not updated:
            raise ValueError("Failed to update sign counter")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update credential: {str(e)}")

    # Clean up challenge
    del challenge_store[username]

    # Generate session token (JWT, session cookie, etc)
    # This is where you would create your application's authentication token
    session_token = f"session_{username}_{secrets.token_hex(32)}"

    return JSONResponse(
        {
            "status": "success",
            "message": "Authentication successful",
            "session_token": session_token,
            "user_verified": verified_data["user_verified"],
            "backup_state": verified_data["backup_state"],
        }
    )


@app.get("/api/auth/webauthn/credentials")
async def list_credentials(user_id: str) -> JSONResponse:
    """List all WebAuthn credentials for a user (for session management).

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
                "counter": 42,
                "transports": ["usb", "nfc"]
            }
        ]
    }
    """
    credentials = credential_store.list_credentials(user_id)

    return JSONResponse(
        {
            "count": len(credentials),
            "credentials": [
                {
                    "credential_id": cred["credential_id"],
                    "device_name": cred.get("device_name", "Unknown Device"),
                    "created_at": cred["created_at"],
                    "last_used": cred.get("last_used"),
                    "counter": cred["counter"],
                    "transports": cred.get("transports", []),
                }
                for cred in credentials
            ],
        }
    )


@app.delete("/api/auth/webauthn/credentials/{credential_id}")
async def delete_credential(user_id: str, credential_id: str) -> JSONResponse:
    """Delete a WebAuthn credential (logout from device).

    Query Parameters:
    - user_id (required): User identifier

    Path Parameters:
    - credential_id (required): Credential to delete

    Response JSON:
    {
        "status": "success",
        "message": "Credential revoked"
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
        return JSONResponse({"status": "success", "message": "Credential revoked"})

    raise HTTPException(status_code=500, detail="Failed to delete credential")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({"status": "healthy"})


if __name__ == "__main__":
    import uvicorn

    print("Starting WebAuthn Authentication Service...")
    print(f"RP_ID: {RP_ID}")
    print(f"ORIGIN: {ORIGIN}")
    print("Visit http://localhost:5000/docs for API documentation")

    uvicorn.run(app, host="0.0.0.0", port=5000)
