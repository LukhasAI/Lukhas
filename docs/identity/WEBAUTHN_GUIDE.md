# WebAuthn Developer Guide

A comprehensive guide to implementing Web Authentication (WebAuthn) with LUKHAS AI's identity system. This guide covers registration, authentication, credential management, and security best practices for passwordless authentication.

**Framework**: Constellation Framework - Identity ⚛️ pillar
**W3C Specification**: [WebAuthn Level 2](https://www.w3.org/TR/webauthn-2/)
**Issue**: #563

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Registration Flow](#registration-flow)
4. [Authentication Flow](#authentication-flow)
5. [Credential Management](#credential-management)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)
9. [W3C Spec Compliance](#w3c-spec-compliance)
10. [Browser Support](#browser-support)

## Overview

### What is WebAuthn?

WebAuthn is a W3C standard that enables web applications to use strong, attested, public key credentials for authentication. Instead of passwords or SMS-based two-factor authentication, users authenticate using hardware security keys, platform authenticators (Face ID, Touch ID, Windows Hello), or other FIDO2-compliant devices.

### Key Benefits

- **Passwordless**: Eliminates password theft and reuse attacks
- **Phishing-resistant**: Origin-binding prevents redirects to fraudulent sites
- **Replay-attack resistant**: Per-authentication cryptographic signatures
- **User-friendly**: Quick biometric or tap-based verification
- **Standardized**: W3C specification with broad browser support

### How WebAuthn Works

```
[Registration Flow]
User Registration → Frontend creates credential → Backend verifies attestation → Store public key

[Authentication Flow]
User Authentication → Frontend signs challenge → Backend verifies signature → Grant access
```

### LUKHAS WebAuthn Implementation Architecture

LUKHAS provides a complete WebAuthn implementation integrated with the Identity ⚛️ pillar:

- **Type Definitions** (`webauthn_types.py`): W3C-compliant TypedDict structures for all WebAuthn operations
- **Credential Storage** (`webauthn_credential.py`): Thread-safe in-memory credential store with metadata tracking
- **Web Integration**: Backend API endpoints for registration and authentication flows

### W3C WebAuthn Level 2 Compliance

LUKHAS implements W3C WebAuthn Level 2 specification features including:

- **Enterprise Attestation**: Request uniquely identifying information from authenticators
- **Discoverable Credentials**: Support for passwordless re-authentication flows
- **Cross-Origin iFrame Support**: Works within payment and multi-origin flows
- **Large Blob Storage**: Store opaque data associated with credentials
- **Apple Attestation Format**: Support for Apple's attestation format

### FIDO2 CTAP2 Support

LUKHAS supports FIDO2 CTAP2 (Client to Authenticator Protocol 2) enabling integration with:

- **Hardware Security Keys**: Yubico, Google Titan, Ledger, etc.
- **Platform Authenticators**: Windows Hello, Face ID, Touch ID
- **Mobile Authenticators**: Android/iOS built-in authenticators
- **Transport Methods**: USB, NFC, Bluetooth (BLE), internal, hybrid (Phone Sign-in)

## Quick Start

### 5-Minute Setup

Get WebAuthn registration and authentication working in 5 minutes:

#### 1. Install Dependencies

```bash
pip install webauthn python-jose pydantic fastapi uvicorn
```

#### 2. Backend Setup (Python)

```python
from lukhas.identity.webauthn_credential import WebAuthnCredentialStore
from lukhas_website.lukhas.identity.webauthn_types import (
    CredentialCreationOptions,
    PublicKeyCredentialCreation
)
import secrets
import base64

# Initialize credential store
credential_store = WebAuthnCredentialStore()

# Configuration
RP_ID = "example.com"
RP_NAME = "My Application"
ORIGIN = "https://example.com"

# Step 1: Generate registration options
challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

registration_options: CredentialCreationOptions = {
    "challenge": challenge,
    "rp": {"name": RP_NAME, "id": RP_ID},
    "user": {
        "id": base64.urlsafe_b64encode(b"user123").decode(),
        "name": "user@example.com",
        "displayName": "John Doe"
    },
    "pubKeyCredParams": [{"type": "public-key", "alg": -7}],
    "timeout": 60000,
    "attestation": "direct"
}

# Step 2: Send registration_options to frontend
# ... (frontend creates credential)

# Step 3: Receive and verify credential from frontend
# Using webauthn library for verification
from webauthn import verify_registration_response

credential: PublicKeyCredentialCreation = {
    # Response from frontend
}

verified = verify_registration_response(
    credential=credential,
    expected_challenge=challenge.encode(),
    expected_origin=ORIGIN,
    expected_rp_id=RP_ID
)

# Step 4: Store credential
credential_store.store_credential(
    user_id="user123",
    credential={
        "credential_id": verified.credential_id.hex(),
        "public_key": verified.credential_public_key.hex(),
        "counter": verified.sign_count,
        "created_at": "2024-11-02T00:00:00Z",
        "device_name": "Security Key"
    }
)
```

#### 3. Frontend Setup (TypeScript)

```typescript
// Step 1: Get registration options from backend
const response = await fetch('/api/auth/webauthn/register/begin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'user@example.com' })
});
const options = await response.json();

// Step 2: Create credential on device
const credential = await navigator.credentials.create({
    publicKey: options
});

// Step 3: Send credential back to backend
await fetch('/api/auth/webauthn/register/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        id: credential.id,
        rawId: credential.id,
        type: credential.type,
        response: {
            clientDataJSON: credential.response.clientDataJSON,
            attestationObject: credential.response.attestationObject
        }
    })
});
```

## Registration Flow

### Backend (Python) - Step-by-Step

#### Step 1: Generate Registration Options

Create random challenge and build credential creation options:

```python
import secrets
import base64
from datetime import datetime, timezone
from lukhas_website.lukhas.identity.webauthn_types import (
    CredentialCreationOptions,
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
    PublicKeyCredentialParameters,
    AuthenticatorSelectionCriteria
)

def generate_registration_options(
    user_id: str,
    username: str,
    display_name: str,
    rp_id: str = "example.com",
    rp_name: str = "My App",
    timeout_ms: int = 60000
) -> tuple[CredentialCreationOptions, str]:
    """Generate WebAuthn registration options.

    Args:
        user_id: Unique user identifier
        username: User's email or username
        display_name: User's display name
        rp_id: Relying Party ID (your domain)
        rp_name: Relying Party name
        timeout_ms: Registration timeout in milliseconds

    Returns:
        Tuple of (options, challenge_for_storage)
    """
    # Generate cryptographically secure challenge
    challenge_bytes = secrets.token_bytes(32)
    challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')

    # Encode user ID
    user_id_encoded = base64.urlsafe_b64encode(user_id.encode()).decode('utf-8').rstrip('=')

    # Build Relying Party entity
    rp: PublicKeyCredentialRpEntity = {
        "name": rp_name,
        "id": rp_id
    }

    # Build user entity
    user: PublicKeyCredentialUserEntity = {
        "id": user_id_encoded,
        "name": username,
        "displayName": display_name
    }

    # Supported public key algorithms (COSE format)
    # -7 = ES256 (ECDSA with SHA-256)
    # -257 = RS256 (RSA with SHA-256)
    # -8 = EdDSA (Edwards-curve Digital Signature Algorithm)
    pub_key_cred_params: list[PublicKeyCredentialParameters] = [
        {"type": "public-key", "alg": -7},     # Preferred: ES256
        {"type": "public-key", "alg": -257},   # Fallback: RS256
        {"type": "public-key", "alg": -8},     # Optional: EdDSA
    ]

    # Authenticator selection criteria
    authenticator_selection: AuthenticatorSelectionCriteria = {
        "authenticatorAttachment": "platform",  # Use platform authenticator
        "residentKey": "preferred",             # Prefer discoverable credentials
        "userVerification": "preferred"          # Require user verification
    }

    # Build complete registration options
    options: CredentialCreationOptions = {
        "challenge": challenge,
        "rp": rp,
        "user": user,
        "pubKeyCredParams": pub_key_cred_params,
        "timeout": timeout_ms,
        "excludeCredentials": [],  # Add existing credentials to prevent duplicates
        "authenticatorSelection": authenticator_selection,
        "attestation": "direct",  # Request attestation statement
        "extensions": {}
    }

    return options, challenge
```

#### Step 2: Send Challenge to Frontend

Store challenge server-side (in session) and send options to frontend:

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json

app = FastAPI()

# Simple session storage (use database in production)
challenges: dict[str, dict] = {}

@app.post("/api/auth/webauthn/register/begin")
async def start_registration(request_data: dict):
    """Start WebAuthn registration process."""
    user_id = request_data.get("user_id")
    username = request_data.get("username")
    display_name = request_data.get("display_name", username)

    if not all([user_id, username]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Generate options
    options, challenge = generate_registration_options(
        user_id=user_id,
        username=username,
        display_name=display_name
    )

    # Store challenge for later verification
    challenges[user_id] = {
        "challenge": challenge,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Send options to frontend
    return JSONResponse(content=options)
```

#### Step 3: Receive and Verify Attestation

Verify the credential response from frontend:

```python
from webauthn import verify_registration_response
from lukhas_website.lukhas.identity.webauthn_types import PublicKeyCredentialCreation

def verify_credential_registration(
    credential: PublicKeyCredentialCreation,
    expected_challenge: str,
    expected_origin: str,
    expected_rp_id: str,
    user_id: str
) -> dict:
    """Verify WebAuthn registration response.

    Args:
        credential: Credential response from frontend
        expected_challenge: Challenge sent to frontend
        expected_origin: Expected origin (HTTPS domain)
        expected_rp_id: Relying Party ID
        user_id: User identifier

    Returns:
        Verified registration data with public key and other metadata
    """
    try:
        # Decode challenge for comparison
        challenge_bytes = base64.urlsafe_b64decode(
            expected_challenge + '=' * (4 - len(expected_challenge) % 4)
        )

        # Verify using webauthn library
        verified = verify_registration_response(
            credential=credential,
            expected_challenge=challenge_bytes,
            expected_origin=expected_origin,
            expected_rp_id=expected_rp_id,
            require_user_verification=True  # Require biometric/PIN verification
        )

        if not verified.verified:
            raise ValueError("Credential verification failed")

        return {
            "credential_id": verified.credential_id.hex(),
            "public_key": verified.credential_public_key.hex(),
            "counter": verified.sign_count,
            "aaguid": verified.aaguid.hex() if verified.aaguid else None,
            "transports": credential.get("response", {}).get("transports", []),
            "backup_eligible": verified.backup_eligible,
            "backup_state": verified.backup_state,
            "user_verified": verified.user_verified
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration verification failed: {str(e)}")
```

#### Step 4: Store Credential

Save the verified credential to persistent storage:

```python
from lukhas.identity.webauthn_credential import WebAuthnCredentialStore
from datetime import datetime, timezone

credential_store = WebAuthnCredentialStore()

@app.post("/api/auth/webauthn/register/complete")
async def complete_registration(request_data: dict):
    """Complete WebAuthn registration."""
    user_id = request_data.get("user_id")
    credential = request_data.get("credential")
    device_name = request_data.get("device_name", "Security Key")

    if not all([user_id, credential]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Verify credential
    verified_data = verify_credential_registration(
        credential=credential,
        expected_challenge=challenges[user_id]["challenge"],
        expected_origin="https://example.com",
        expected_rp_id="example.com",
        user_id=user_id
    )

    # Store credential
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
                "backup_state": verified_data.get("backup_state", False)
            }
        )

        # Clean up challenge
        del challenges[user_id]

        return {"status": "success", "message": "Registration complete"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Frontend (TypeScript) - Step-by-Step

#### Step 1: Request Registration Options from Backend

```typescript
async function startRegistration(username: string): Promise<CredentialCreationOptions> {
    const response = await fetch('/api/auth/webauthn/register/begin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: 'user123',
            username: username,
            display_name: username.split('@')[0]
        })
    });

    if (!response.ok) {
        throw new Error('Failed to get registration options');
    }

    return response.json();
}
```

#### Step 2: Call navigator.credentials.create()

```typescript
async function createCredential(
    options: CredentialCreationOptions
): Promise<PublicKeyCredentialCreation> {
    // Convert challenge from base64url to ArrayBuffer
    const challengeBuffer = base64urlToBuffer(options.challenge);

    // Convert user ID to ArrayBuffer
    const userIdBuffer = base64urlToBuffer(options.user.id);

    // Build WebAuthn creation options
    const credentialOptions: CredentialCreationOptions = {
        ...options,
        challenge: challengeBuffer,
        user: {
            ...options.user,
            id: userIdBuffer
        }
    };

    try {
        // Call browser's WebAuthn API
        const credential = await navigator.credentials.create({
            publicKey: credentialOptions
        }) as PublicKeyCredential | null;

        if (!credential) {
            throw new Error('Failed to create credential');
        }

        // Convert response to proper format
        const attestationResponse = credential.response as AuthenticatorAttestationResponse;

        return {
            id: credential.id,
            rawId: bufferToBase64url(credential.rawId),
            type: credential.type,
            response: {
                clientDataJSON: bufferToBase64url(attestationResponse.clientDataJSON),
                attestationObject: bufferToBase64url(attestationResponse.attestationObject),
                transports: attestationResponse.getTransports?.() || []
            },
            authenticatorAttachment: credential.authenticatorAttachment,
            clientExtensionResults: credential.getClientExtensionResults()
        };

    } catch (error: any) {
        if (error.name === 'NotAllowedError') {
            throw new Error('Registration cancelled by user');
        } else if (error.name === 'InvalidStateError') {
            throw new Error('Authenticator already registered for this account');
        } else if (error.name === 'SecurityError') {
            throw new Error('HTTPS required for WebAuthn');
        }
        throw error;
    }
}
```

#### Step 3: Send Credential to Backend

```typescript
async function completeRegistration(
    credential: PublicKeyCredentialCreation,
    deviceName: string
): Promise<void> {
    const response = await fetch('/api/auth/webauthn/register/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: 'user123',
            credential: credential,
            device_name: deviceName
        })
    });

    if (!response.ok) {
        throw new Error('Registration failed');
    }

    const result = await response.json();
    console.log('Registration successful:', result);
}

// Helper functions
function base64urlToBuffer(base64url: string): ArrayBuffer {
    const base64 = base64url
        .replace(/-/g, '+')
        .replace(/_/g, '/');
    const padded = base64 + '='.repeat((4 - base64.length % 4) % 4);
    const binary = atob(padded);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

function bufferToBase64url(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary)
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}
```

#### Complete Registration Example

```typescript
async function handleRegistration() {
    const username = 'user@example.com';
    const deviceName = 'My Security Key';

    try {
        // Step 1: Get registration options
        const options = await startRegistration(username);
        console.log('Registration options received');

        // Step 2: Create credential on device
        const credential = await createCredential(options);
        console.log('Credential created on authenticator');

        // Step 3: Send to backend
        await completeRegistration(credential, deviceName);
        console.log('Registration complete!');

    } catch (error) {
        console.error('Registration failed:', error);
    }
}
```

## Authentication Flow

### Backend (Python) - Step-by-Step

#### Step 1: Generate Authentication Options

Create challenge for user to sign:

```python
def generate_authentication_options(
    username: str,
    rp_id: str = "example.com",
    timeout_ms: int = 60000,
    user_verification: str = "preferred"
) -> tuple[CredentialRequestOptions, str]:
    """Generate WebAuthn authentication options.

    Args:
        username: User's username/email
        rp_id: Relying Party ID
        timeout_ms: Authentication timeout in milliseconds
        user_verification: "required", "preferred", or "discouraged"

    Returns:
        Tuple of (options, challenge_for_storage)
    """
    # Generate cryptographically secure challenge
    challenge_bytes = secrets.token_bytes(32)
    challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')

    # Get user's registered credentials
    user_credentials = credential_store.list_credentials(username)

    # Build allow credentials list
    allow_credentials = [
        {
            "type": "public-key",
            "id": cred["credential_id"],
            "transports": cred.get("transports", [])
        }
        for cred in user_credentials
    ]

    # Build authentication options
    options: CredentialRequestOptions = {
        "challenge": challenge,
        "timeout": timeout_ms,
        "rpId": rp_id,
        "allowCredentials": allow_credentials,
        "userVerification": user_verification,
        "extensions": {}
    }

    return options, challenge
```

#### Step 2: Send Challenge to Frontend

Store challenge and send options:

```python
@app.post("/api/auth/webauthn/authenticate/begin")
async def start_authentication(request_data: dict):
    """Start WebAuthn authentication process."""
    username = request_data.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="Username required")

    # Generate options
    options, challenge = generate_authentication_options(username)

    # Store challenge for verification
    challenges[username] = {
        "challenge": challenge,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    return JSONResponse(content=options)
```

#### Step 3: Verify Assertion

Verify signature from authenticator:

```python
from webauthn import verify_authentication_response
from lukhas_website.lukhas.identity.webauthn_types import PublicKeyCredentialAssertion

def verify_credential_authentication(
    credential: PublicKeyCredentialAssertion,
    expected_challenge: str,
    expected_origin: str,
    expected_rp_id: str,
    username: str
) -> dict:
    """Verify WebAuthn authentication assertion.

    Args:
        credential: Assertion response from frontend
        expected_challenge: Challenge sent to frontend
        expected_origin: Expected origin (HTTPS domain)
        expected_rp_id: Relying Party ID
        username: Username being authenticated

    Returns:
        Verified authentication data with updated sign counter
    """
    # Find the credential being used
    credential_id = credential["id"]
    stored_credential = credential_store.get_credential(credential_id)

    if not stored_credential:
        raise HTTPException(status_code=400, detail="Credential not found")

    # Verify username matches
    if stored_credential["user_id"] != username:
        raise HTTPException(status_code=403, detail="Credential mismatch")

    try:
        # Decode challenge for comparison
        challenge_bytes = base64.urlsafe_b64decode(
            expected_challenge + '=' * (4 - len(expected_challenge) % 4)
        )

        # Decode stored public key
        public_key_bytes = bytes.fromhex(stored_credential["public_key"])

        # Verify using webauthn library
        verified = verify_authentication_response(
            credential=credential,
            expected_challenge=challenge_bytes,
            expected_origin=expected_origin,
            expected_rp_id=expected_rp_id,
            credential_public_key=public_key_bytes,
            credential_current_sign_count=stored_credential["counter"],
            require_user_verification=True
        )

        if not verified.verified:
            raise ValueError("Authentication verification failed")

        # Check sign counter to prevent replay attacks
        if verified.new_sign_count <= stored_credential["counter"]:
            raise ValueError("Sign counter invalid - possible cloned authenticator")

        return {
            "new_sign_count": verified.new_sign_count,
            "user_verified": verified.user_verified,
            "backup_eligible": verified.backup_eligible,
            "backup_state": verified.backup_state
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication verification failed: {str(e)}")
```

#### Step 4: Update Sign Counter

Update the signature counter to prevent replay attacks:

```python
@app.post("/api/auth/webauthn/authenticate/complete")
async def complete_authentication(request_data: dict):
    """Complete WebAuthn authentication."""
    username = request_data.get("username")
    credential = request_data.get("credential")

    if not all([username, credential]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Verify assertion
    verified_data = verify_credential_authentication(
        credential=credential,
        expected_challenge=challenges[username]["challenge"],
        expected_origin="https://example.com",
        expected_rp_id="example.com",
        username=username
    )

    # Update sign counter
    credential_store.update_credential(
        credential_id=credential["id"],
        updates={
            "counter": verified_data["new_sign_count"],
            "last_used": datetime.now(timezone.utc).isoformat()
        }
    )

    # Clean up challenge
    del challenges[username]

    # Generate session/JWT token
    return {
        "status": "success",
        "message": "Authentication successful",
        "session_token": "..."  # Your session/JWT token
    }
```

### Frontend (TypeScript) - Step-by-Step

#### Step 1: Request Authentication Options

```typescript
async function startAuthentication(username: string): Promise<CredentialRequestOptions> {
    const response = await fetch('/api/auth/webauthn/authenticate/begin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
    });

    if (!response.ok) {
        throw new Error('Failed to get authentication options');
    }

    return response.json();
}
```

#### Step 2: Call navigator.credentials.get()

```typescript
async function getAssertion(
    options: CredentialRequestOptions
): Promise<PublicKeyCredentialAssertion> {
    // Convert challenge from base64url to ArrayBuffer
    const challengeBuffer = base64urlToBuffer(options.challenge);

    // Convert allow credentials to proper format
    const allowCredentials = options.allowCredentials?.map((cred: any) => ({
        type: cred.type,
        id: base64urlToBuffer(cred.id),
        transports: cred.transports
    })) || [];

    // Build WebAuthn get options
    const getOptions: CredentialRequestOptions = {
        challenge: challengeBuffer,
        rpId: options.rpId,
        allowCredentials: allowCredentials,
        userVerification: options.userVerification,
        timeout: options.timeout
    };

    try {
        // Call browser's WebAuthn API
        const assertion = await navigator.credentials.get({
            publicKey: getOptions
        }) as PublicKeyCredential | null;

        if (!assertion) {
            throw new Error('Authentication cancelled');
        }

        // Convert response to proper format
        const assertionResponse = assertion.response as AuthenticatorAssertionResponse;

        return {
            id: assertion.id,
            rawId: bufferToBase64url(assertion.rawId),
            type: assertion.type,
            response: {
                clientDataJSON: bufferToBase64url(assertionResponse.clientDataJSON),
                authenticatorData: bufferToBase64url(assertionResponse.authenticatorData),
                signature: bufferToBase64url(assertionResponse.signature),
                userHandle: assertionResponse.userHandle ?
                    bufferToBase64url(assertionResponse.userHandle) : undefined
            },
            authenticatorAttachment: assertion.authenticatorAttachment,
            clientExtensionResults: assertion.getClientExtensionResults()
        };

    } catch (error: any) {
        if (error.name === 'NotAllowedError') {
            throw new Error('Authentication cancelled by user');
        } else if (error.name === 'TimeoutError') {
            throw new Error('Authentication timed out');
        } else if (error.name === 'SecurityError') {
            throw new Error('HTTPS required for WebAuthn');
        }
        throw error;
    }
}
```

#### Step 3: Send Assertion to Backend

```typescript
async function completeAuthentication(
    assertion: PublicKeyCredentialAssertion,
    username: string
): Promise<string> {
    const response = await fetch('/api/auth/webauthn/authenticate/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: username,
            credential: assertion
        })
    });

    if (!response.ok) {
        throw new Error('Authentication failed');
    }

    const result = await response.json();
    return result.session_token;
}

// Complete authentication example
async function handleAuthentication(username: string) {
    try {
        // Step 1: Get authentication options
        const options = await startAuthentication(username);
        console.log('Authentication options received');

        // Step 2: Get assertion from authenticator
        const assertion = await getAssertion(options);
        console.log('Assertion created');

        // Step 3: Send to backend
        const token = await completeAuthentication(assertion, username);
        console.log('Authentication successful!');

        return token;

    } catch (error) {
        console.error('Authentication failed:', error);
        throw error;
    }
}
```

## Credential Management

### List User's Credentials

```python
@app.get("/api/auth/webauthn/credentials")
async def list_credentials(user_id: str):
    """List all registered WebAuthn credentials for a user."""
    credentials = credential_store.list_credentials(user_id)

    return {
        "count": len(credentials),
        "credentials": [
            {
                "credential_id": cred["credential_id"],
                "device_name": cred.get("device_name", "Unknown Device"),
                "created_at": cred["created_at"],
                "last_used": cred.get("last_used"),
                "aaguid": cred.get("aaguid"),
                "transports": cred.get("transports", [])
            }
            for cred in credentials
        ]
    }
```

### Delete/Revoke Credential

```python
@app.delete("/api/auth/webauthn/credentials/{credential_id}")
async def delete_credential(user_id: str, credential_id: str):
    """Delete a WebAuthn credential."""
    credential = credential_store.get_credential(credential_id)

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Verify ownership
    if credential["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Delete credential
    if credential_store.delete_credential(credential_id):
        return {"status": "success", "message": "Credential deleted"}

    raise HTTPException(status_code=500, detail="Failed to delete credential")
```

### Update Credential Metadata

```python
@app.patch("/api/auth/webauthn/credentials/{credential_id}")
async def update_credential(
    user_id: str,
    credential_id: str,
    request_data: dict
):
    """Update credential metadata (device name, etc)."""
    credential = credential_store.get_credential(credential_id)

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Verify ownership
    if credential["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Extract allowed updates
    updates = {}
    if "device_name" in request_data:
        updates["device_name"] = request_data["device_name"]

    # Update credential
    if credential_store.update_credential(credential_id, updates):
        return {"status": "success", "message": "Credential updated"}

    raise HTTPException(status_code=500, detail="Failed to update credential")
```

### Frontend - Credential Management UI

```typescript
async function loadCredentials(userId: string): Promise<Credential[]> {
    const response = await fetch(`/api/auth/webauthn/credentials?user_id=${userId}`);
    return response.json();
}

async function deleteCredential(credentialId: string, userId: string): Promise<void> {
    const response = await fetch(
        `/api/auth/webauthn/credentials/${credentialId}?user_id=${userId}`,
        { method: 'DELETE' }
    );

    if (!response.ok) {
        throw new Error('Failed to delete credential');
    }
}

async function updateCredentialName(
    credentialId: string,
    userId: string,
    newName: string
): Promise<void> {
    const response = await fetch(
        `/api/auth/webauthn/credentials/${credentialId}?user_id=${userId}`,
        {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_name: newName })
        }
    );

    if (!response.ok) {
        throw new Error('Failed to update credential');
    }
}
```

## API Reference

### Type Definitions (WebAuthn Types)

All types are imported from `lukhas_website.lukhas.identity.webauthn_types`.

#### PublicKeyCredentialRpEntity

Describes the Relying Party (your application).

```python
class PublicKeyCredentialRpEntity(TypedDict):
    name: str              # RP name (e.g., "My App")
    id: NotRequired[str]   # RP ID (your domain, e.g., "example.com")
```

#### PublicKeyCredentialUserEntity

Describes the user account.

```python
class PublicKeyCredentialUserEntity(TypedDict):
    id: str         # Base64url-encoded user handle
    name: str       # Username or email
    displayName: str  # User's display name
```

#### PublicKeyCredentialParameters

Specifies supported cryptographic algorithms.

```python
class PublicKeyCredentialParameters(TypedDict):
    type: Literal["public-key"]  # Type is always "public-key"
    alg: int  # COSE algorithm identifier:
              # -7 = ES256 (ECDSA with SHA-256)
              # -257 = RS256 (RSA with SHA-256)
              # -8 = EdDSA
```

#### PublicKeyCredentialDescriptor

Identifies a credential (used in allow/exclude lists).

```python
class PublicKeyCredentialDescriptor(TypedDict):
    type: Literal["public-key"]
    id: str  # Base64url-encoded credential ID
    transports: NotRequired[list[Literal["usb", "nfc", "ble", "internal", "hybrid"]]]
```

#### AuthenticatorSelectionCriteria

Specifies requirements for authenticator selection during registration.

```python
class AuthenticatorSelectionCriteria(TypedDict):
    authenticatorAttachment: NotRequired[Literal["platform", "cross-platform"]]
    # "platform" = built-in (Face ID, Touch ID, Windows Hello)
    # "cross-platform" = external (security keys)

    residentKey: NotRequired[Literal["discouraged", "preferred", "required"]]
    # Whether credential should be stored on authenticator

    userVerification: NotRequired[Literal["required", "preferred", "discouraged"]]
    # Require biometric or PIN verification
```

#### CredentialCreationOptions

Options passed to `navigator.credentials.create()`.

```python
class CredentialCreationOptions(TypedDict):
    challenge: str  # Base64url-encoded random challenge
    rp: PublicKeyCredentialRpEntity
    user: PublicKeyCredentialUserEntity
    pubKeyCredParams: list[PublicKeyCredentialParameters]
    timeout: NotRequired[int]  # Milliseconds (recommended: 60000)
    excludeCredentials: NotRequired[list[PublicKeyCredentialDescriptor]]
    authenticatorSelection: NotRequired[AuthenticatorSelectionCriteria]
    attestation: NotRequired[Literal["none", "indirect", "direct", "enterprise"]]
    # "none" = Don't request attestation
    # "direct" = Request attestation (recommended)
    # "indirect" = Indirect attestation
    # "enterprise" = Enterprise attestation
    extensions: NotRequired[dict[str, Any]]
```

#### CredentialRequestOptions

Options passed to `navigator.credentials.get()`.

```python
class CredentialRequestOptions(TypedDict):
    challenge: str  # Base64url-encoded random challenge
    timeout: NotRequired[int]  # Milliseconds
    rpId: NotRequired[str]  # Relying Party ID
    allowCredentials: NotRequired[list[PublicKeyCredentialDescriptor]]
    userVerification: NotRequired[Literal["required", "preferred", "discouraged"]]
    extensions: NotRequired[dict[str, Any]]
```

### WebAuthnCredentialStore API

Complete API reference for the `WebAuthnCredentialStore` class.

#### store_credential()

Store a new WebAuthn credential.

```python
def store_credential(self, user_id: str, credential: Dict[str, Any]) -> None:
    """
    Args:
        user_id: User identifier
        credential: Dictionary with keys:
            - credential_id (str, required): Base64url-encoded credential ID
            - public_key (str, required): Base64url-encoded public key
            - counter (int, required): Signature counter
            - created_at (str, required): ISO 8601 timestamp
            - device_name (str, optional): User-friendly name
            - aaguid (str, optional): Authenticator AAGUID
            - transports (list, optional): Transport types
            - backup_eligible (bool, optional): Can be backed up
            - backup_state (bool, optional): Is backed up

    Raises:
        ValueError: If credential_id already exists or missing required fields
        TypeError: If data types are invalid
    """
```

#### get_credential()

Retrieve a credential by ID.

```python
def get_credential(self, credential_id: str) -> Optional[WebAuthnCredential]:
    """
    Args:
        credential_id: Unique credential identifier

    Returns:
        WebAuthnCredential if found, None otherwise
    """
```

#### list_credentials()

List all credentials for a user.

```python
def list_credentials(self, user_id: str) -> List[WebAuthnCredential]:
    """
    Args:
        user_id: User identifier

    Returns:
        List of WebAuthnCredential objects (empty if none)
    """
```

#### delete_credential()

Delete a credential by ID.

```python
def delete_credential(self, credential_id: str) -> bool:
    """
    Args:
        credential_id: Credential to delete

    Returns:
        True if deleted, False if not found
    """
```

#### update_credential()

Update credential fields.

```python
def update_credential(
    self,
    credential_id: str,
    updates: Dict[str, Any]
) -> bool:
    """
    Args:
        credential_id: Credential to update
        updates: Dictionary of fields to update:
            - counter (int): New signature counter
            - last_used (str): ISO 8601 timestamp
            - device_name (str): Device name
            - aaguid (str): Authenticator AAGUID
            - transports (list): Transport types
            - backup_eligible (bool): Backup eligibility
            - backup_state (bool): Backup state
            - metadata (dict): Additional metadata

    Returns:
        True if updated, False if not found

    Raises:
        ValueError: If trying to update credential_id or user_id
        TypeError: If update values have invalid types
    """
```

#### count_credentials()

Count credentials.

```python
def count_credentials(self, user_id: Optional[str] = None) -> int:
    """
    Args:
        user_id: Optional user ID (if None, counts all credentials)

    Returns:
        Number of credentials
    """
```

## Troubleshooting

### Common Issues and Solutions

#### NotAllowedError during Registration

**Symptoms**: Registration fails with "The operation either timed out or was not allowed"

**Causes**:
- User cancelled the operation
- Authenticator doesn't support the requested algorithm
- TLS certificate issues
- Timeout before user could complete operation
- User name exceeds 64 UTF-8 encoded bytes

**Solutions**:
```python
try:
    credential = await navigator.credentials.create({
        publicKey: options
    })
except Error as error:
    if error.name == "NotAllowedError":
        # Check username length
        if username.encode('utf-8').__len__() > 64:
            return "Username too long. Use shorter username."

        # Could be timeout - retry
        return "Registration cancelled. Please try again."

    if error.name == "SecurityError":
        return "HTTPS required for WebAuthn"
```

#### InvalidStateError during Registration

**Symptoms**: Registration fails with "An attempt was made to use an object that is not, or is no longer, usable"

**Causes**:
- Credential already exists for this user on this authenticator
- excludeCredentials list includes a credential that exists

**Solutions**:
```python
# Always get user's existing credentials and exclude them
existing_creds = credential_store.list_credentials(user_id)
exclude_list = [
    {
        "type": "public-key",
        "id": cred["credential_id"]
    }
    for cred in existing_creds
]

# Pass to registration options
options["excludeCredentials"] = exclude_list
```

#### InvalidStateError during Authentication

**Symptoms**: Authentication fails with InvalidStateError

**Causes**:
- Credential is no longer valid
- User account deleted or credential revoked
- Sign counter validation failed (replay attack detected)

**Solutions**:
```python
# Check if credential still exists
stored_cred = credential_store.get_credential(credential_id)
if not stored_cred:
    raise HTTPException(status_code=403, detail="Credential no longer valid")

# Validate sign counter
if verified.new_sign_count <= stored_cred["counter"]:
    # Possible cloned authenticator
    # Recommend user to re-register
    raise HTTPException(
        status_code=403,
        detail="Security check failed. Please re-register."
    )
```

#### Browser Compatibility Issues

**Firefox doesn't support ES256**:
```python
# Firefox may not support some algorithms. Provide fallback:
pubKeyCredParams = [
    {"type": "public-key", "alg": -7},    # ES256
    {"type": "public-key", "alg": -257},  # RS256 (fallback)
    {"type": "public-key", "alg": -8},    # EdDSA (fallback)
]
```

**Safari on macOS requires specific options**:
```python
# For Safari, ensure:
authenticatorSelection = {
    "authenticatorAttachment": "platform",
    "userVerification": "preferred",
    "residentKey": "preferred"
}
```

#### HTTPS Requirement

**Symptoms**: SecurityError when trying to use WebAuthn

**Cause**: WebAuthn requires HTTPS (or localhost for testing)

**Solution**:
```python
# Development: Use localhost
ORIGIN = "http://localhost:3000"

# Production: Must use HTTPS
ORIGIN = "https://example.com"

# Check origin in backend
if not ORIGIN.startswith("https://") and ORIGIN != "http://localhost":
    raise ValueError("HTTPS required for production WebAuthn")
```

#### Timeout Issues

**Symptoms**: Registration/authentication times out without error

**Cause**: Authenticator not responding within timeout period

**Solutions**:
```python
# Increase timeout
options["timeout"] = 120000  # 2 minutes instead of 60 seconds

# Implement retry logic
MAX_RETRIES = 3
for attempt in range(MAX_RETRIES):
    try:
        credential = await navigator.credentials.create({
            publicKey: options
        })
        break
    except TimeoutError:
        if attempt < MAX_RETRIES - 1:
            console.log(f"Timeout, retry {attempt + 1}")
        else:
            raise
```

#### User Gesture Requirement

**Symptoms**: "User activation is required" error

**Cause**: WebAuthn operations require user interaction

**Solution**:
```typescript
// Only call from user gesture (click, keyboard, etc)
button.addEventListener('click', async () => {
    // This is user gesture, OK to use WebAuthn
    const credential = await navigator.credentials.create({
        publicKey: options
    });
});

// This will fail - not triggered by user
setTimeout(() => {
    // No user gesture here!
    const credential = await navigator.credentials.create({
        publicKey: options
    });
}, 1000);
```

## Security Best Practices

### Challenge Randomness

Always use cryptographically secure random challenges:

```python
import secrets
import base64

# Correct: Use secrets module
challenge_bytes = secrets.token_bytes(32)  # 256 bits
challenge = base64.urlsafe_b64encode(challenge_bytes).decode()

# Incorrect: Using random module
import random
challenge = base64.b64encode(str(random.random()).encode())  # NOT SECURE
```

### Timeout Values

Recommend 60-120 seconds:

```python
# Too short - may not give user enough time
timeout_ms = 10000  # 10 seconds

# Recommended
timeout_ms = 60000  # 60 seconds

# For accessibility
timeout_ms = 120000  # 2 minutes
```

### User Verification Requirements

Require verification for sensitive operations:

```python
# Registration: Always verify user
authenticatorSelection = {
    "userVerification": "required"  # Require biometric/PIN
}

# Authentication: Require verification
userVerification = "required"  # Enforce biometric/PIN

# Less sensitive: Prefer but don't require
userVerification = "preferred"  # Try but allow fallback
```

### Attestation Handling

Validate attestation statements:

```python
# Request attestation
attestation = "direct"  # Get authenticator manufacturer info

# Verify attestation
verified = verify_registration_response(
    credential=credential,
    expected_challenge=challenge,
    expected_origin=origin,
    expected_rp_id=rp_id
)

# Check authenticator was genuine (if needed)
if verified.aaguid and is_malicious_aaguid(verified.aaguid):
    raise ValueError("Authenticator not approved")
```

### Credential Storage Security

Store credentials securely:

```python
# Store public key, not private key
# Never store attestation objects unless needed
credential_store.store_credential(
    user_id=user_id,
    credential={
        "credential_id": verified.credential_id.hex(),
        "public_key": verified.credential_public_key.hex(),  # Only public key
        "counter": verified.sign_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
        # Don't store: attestation_object, clientDataJSON
    }
)

# Use encrypted database for production
# Consider using hardware security modules (HSM) for keys
```

### Sign Counter Validation

Prevent replay attacks:

```python
# Check sign counter increases
if verified.new_sign_count <= stored_credential["counter"]:
    # Possible cloned authenticator
    logger.critical(
        f"Replay attack detected: {credential_id}",
        extra={"user_id": user_id}
    )
    raise SecurityException("Possible cloned authenticator detected")

# Update counter
credential_store.update_credential(
    credential_id,
    {"counter": verified.new_sign_count}
)
```

### Exclude Previously Registered Credentials

Prevent duplicate registrations:

```python
# During registration, exclude existing credentials
existing = credential_store.list_credentials(user_id)
options["excludeCredentials"] = [
    {
        "type": "public-key",
        "id": cred["credential_id"],
        "transports": cred.get("transports", [])
    }
    for cred in existing
]
```

### Transport Hints

Use transport information for UX:

```python
# Store transport info
credential_store.store_credential(
    user_id=user_id,
    credential={
        ...
        "transports": response.get("transports", [])
        # e.g., ["usb", "nfc"] for security keys
        # e.g., ["internal"] for platform authenticators
    }
)

# Use in authentication to hint which authenticator to use
allow_credentials = [
    {
        "type": "public-key",
        "id": cred["credential_id"],
        "transports": cred.get("transports", [])
    }
    for cred in credentials
]
```

## W3C Spec Compliance

### WebAuthn Level 2 Features Supported

- **Attestation Formats**: Packed, TPM, Android Key Attestation, Apple, FIDO U2F
- **Public Key Algorithms**: ES256 (-7), RS256 (-257), EdDSA (-8)
- **Authenticator Types**: Platform (Touch ID, Face ID, Windows Hello), Cross-platform (FIDO keys)
- **Credential Types**: Discoverable (resident keys) and non-discoverable
- **User Verification**: Required, preferred, or discouraged
- **Backup Eligibility**: Track if credentials can be backed up

### FIDO2 CTAP2 Support

Authenticators must support:

- **FIDO2 Level**: Tested and registered authenticators
- **CTAP Protocol**: Client to Authenticator Protocol 2 minimum
- **Crypto Algorithms**: At least EC2 with SHA-256
- **User Verification**: PIN or biometric verification capability

### Supported Credential Types

```python
# Public Key Credential Type
type = "public-key"  # Only supported type in WebAuthn

# Algorithms (COSE format)
alg = -7       # ES256 (ECDSA with SHA-256) - RECOMMENDED
alg = -257     # RS256 (RSA with SHA-256) - Fallback
alg = -8       # EdDSA - Fallback
```

### Transport Methods

```python
# Supported transports
transports = [
    "usb",       # USB security keys
    "nfc",       # NFC-capable devices
    "ble",       # Bluetooth Low Energy
    "internal",  # Platform authenticators (Touch ID, Face ID)
    "hybrid"     # Phone sign-in (QR code)
]
```

### Reference Implementation

Full spec reference: https://www.w3.org/TR/webauthn-2/

Key sections:
- Section 4: Terminology and Concepts
- Section 5: Registration Ceremony
- Section 6: Authentication Ceremony
- Section 7: WebAuthn Extensions
- Section 8: Attestation Formats

## Browser Support

### Desktop Browsers

| Browser | WebAuthn | Platform Auth | Security Keys | Min Version |
|---------|----------|---------------|---------------|------------|
| Chrome | Yes | Yes | Yes | 67+ |
| Firefox | Yes | No | Yes | 60+ |
| Safari | Yes | Yes | Yes | 13+ |
| Edge | Yes | Yes | Yes | 18+ |
| Opera | Yes | Yes | Yes | 54+ |

### Mobile Browsers

| Browser | WebAuthn | Biometric | Min Version |
|---------|----------|-----------|------------|
| Chrome Android | Yes | Yes | 90+ |
| Firefox Android | Yes | Yes | 68+ |
| Safari iOS | Yes | Yes | 14.5+ |
| Samsung Internet | Yes | Yes | 14+ |
| Edge Android | Yes | Yes | 90+ |

### Platform Authenticators

| Platform | Authenticator | Support |
|----------|--------------|---------|
| Windows | Windows Hello | Yes |
| macOS | Touch ID | Yes |
| iOS | Face ID / Touch ID | Yes |
| Android | Biometric API | Yes |
| ChromeOS | ChromeOS authenticator | Yes |

### Required Features for Production

Before launching production WebAuthn:

- Test in all target browsers
- Implement graceful fallback (password + WebAuthn)
- Provide clear user documentation
- Monitor error rates and user feedback
- Have recovery mechanism for lost keys

### Polyfills

For older browsers, consider:

```html
<!-- WebAuthn polyfill for unsupported browsers -->
<script src="https://cdn.jsdelivr.net/npm/webauthn-json@5.1.0/dist/index.umd.js"></script>
```

However, polyfills cannot provide true security - they cannot perform cryptographic operations. Recommend modern browsers for production.

---

## Additional Resources

- **W3C WebAuthn Level 2 Specification**: https://www.w3.org/TR/webauthn-2/
- **FIDO2 Specifications**: https://fidoalliance.org/
- **WebAuthn.io**: https://webauthn.io/ (Test WebAuthn implementation)
- **Yubico WebAuthn Guide**: https://developers.yubico.com/WebAuthn/
- **WebAuthn Documentation**: https://passkeys.dev/
- **OWASP Authentication Cheat Sheet**: https://cheatsheetseries.owasp.org/

---

**Document Version**: 1.0
**Last Updated**: November 2, 2024
**LUKHAS AI - Constellation Framework - Identity ⚛️ Pillar**
