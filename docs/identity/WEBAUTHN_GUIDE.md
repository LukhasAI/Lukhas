# WebAuthn in LUKHAS: Developer Guide

This guide provides a comprehensive overview of how to implement WebAuthn for passwordless authentication in applications using the LUKHAS framework.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Registration Flow](#registration-flow)
- [Authentication Flow](#authentication-flow)
- [Credential Management](#credential-management)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [W3C Spec Compliance](#w3c-spec-compliance)

---

## Overview

WebAuthn (Web Authentication) is a W3C standard that enables passwordless authentication using public-key cryptography. Instead of a password, users register and authenticate with a hardware or software authenticator (like a YubiKey, Windows Hello, or a mobile device).

In LUKHAS, the WebAuthn implementation provides a type-safe and secure way to manage the entire lifecycle of passwordless credentials, from registration to authentication and credential management. Our implementation is compliant with the WebAuthn Level 2 specification.

---

## Quick Start

A minimal example to get started with WebAuthn registration and authentication.

*Backend (Python) - Registration:* 
```python
"""
WebAuthn Registration Example (Backend - Python)

This script demonstrates the server-side logic for a WebAuthn credential
registration flow. It uses a conceptual server-side WebAuthn library.

NOTE: This is a conceptual example. A complete implementation requires a
properly configured web server (e.g., using Flask or FastAPI) and a
library for handling the WebAuthn cryptographic operations.
"""
import base64
import os
from typing import Dict, Any

# A conceptual server-side WebAuthn library. In a real application,
# you would use a library like `webauthn`.
from webauthn import generate_registration_options, verify_registration_response
from webauthn.helpers.structs import RegistrationCredential

# Import the TypedDict definitions we created
from lukhas_website.lukhas.identity.webauthn_types import (
    CredentialCreationOptions,
    PublicKeyCredentialCreation,
)

# --- In-memory stores for demonstration purposes ---
# In a real app, use a database.
user_credentials: Dict[str, list[RegistrationCredential]] = {}
users: Dict[str, Dict[str, Any]] = {
    "testuser": {
        "id": b"testuser_id_12345",
        "name": "testuser",
        "display_name": "Test User",
    }
}
# --- End of in-memory stores ---

RP_ID = "localhost"  # Relying Party ID - Should be your domain
RP_NAME = "LUKHAS Demo App"
ORIGIN = "https://localhost:5000"


def run_registration_flow(username: str):
    """Demonstrates the full registration flow for a user."""
    print(f"--- 1. Starting registration for user: {username} ---")
    user = users.get(username)
    if not user:
        print(f"User {username} not found.")
        return

    # --- Server-Side: Generate Registration Options ---
    registration_options: CredentialCreationOptions = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=user["id"],
        user_name=user["name"],
        user_display_name=user["display_name"],
    )

    print(f"\n--- 2. Server generated registration options: ---")
    print(registration_options)

    # --- Frontend Simulation: Use options to create a credential ---
    # In a real app, the `registration_options` would be sent to the frontend,
    # and the frontend would call `navigator.credentials.create()`.
    # Here, we simulate the response the frontend would send back.
    print("\n--- 3. Simulating frontend credential creation... ---")
    # This is a simplified, conceptual representation of a frontend response.
    # A real response would be a complex JSON object.
    simulated_frontend_response: PublicKeyCredentialCreation = {
        "id": "credential_id_from_frontend_123",
        "rawId": "credential_id_from_frontend_123",
        "type": "public-key",
        "response": {
            "clientDataJSON": "base64_encoded_client_data",
            "attestationObject": "base64_encoded_attestation_object",
        },
    }
    print("Frontend would send back a response like this (simplified):")
    print(simulated_frontend_response)

    # --- Server-Side: Verify the Frontend Response ---
    print("\n--- 4. Server verifies the response from the frontend... ---")
    try:
        # The verification function would perform complex cryptographic checks.
        verified_credential = verify_registration_response(
            credential=simulated_frontend_response, # This would be the real credential
            expected_challenge=base64.b64decode(registration_options["challenge"]),
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
            require_user_verification=False,
        )

        # --- Store the new credential ---
        if username not in user_credentials:
            user_credentials[username] = []
        user_credentials[username].append(verified_credential)

        print(f"\n--- 5. ✅ Registration successful! ---")
        print(f"Credential ID: {verified_credential.id}")
        print(f"Stored for user: {username}")

    except Exception as e:
        print(f"\n--- ❌ Registration failed: {e} ---")


if __name__ == "__main__":
    run_registration_flow("testuser")
```

*Frontend (TypeScript) - Registration:* 
```typescript
/**
 * WebAuthn Frontend Example (TypeScript)
 *
 * This script provides a conceptual example of how a frontend application
 * would use the `navigator.credentials` API to handle WebAuthn registration
 * and authentication ceremonies.
 *
 * NOTE: This is a conceptual, browser-focused example. It is not a complete
 * frontend component (e.g., React, Vue, Angular) but demonstrates the core logic.
 */

// --- Type Definitions (from lukhas_website/lukhas/identity/webauthn_types.py) ---
// These would typically be generated or defined in a shared types file.

interface CredentialCreationOptions {
  challenge: string;
  rp: { name: string; id?: string };
  user: { id: string; name: string; displayName: string };
  pubKeyCredParams: { type: "public-key"; alg: number }[];
  // ... and other optional fields
}

// Helper function to convert Base64URL strings to ArrayBuffers
// (The browser API requires ArrayBuffers for many fields)
function base64urlToBuffer(base64urlString: string): ArrayBuffer {
  const padding = "=".repeat((4 - (base64urlString.length % 4)) % 4);
  const base64 = (base64urlString + padding).replace(/\-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray.buffer;
}

/**
 * Handles the WebAuthn registration process on the frontend.
 */
async function handleRegistration() {
  try {
    // 1. Fetch registration options from the server
    const response = await fetch("/api/webauthn/generate-registration-options");
    const options: CredentialCreationOptions = await response.json();

    // The server sends the challenge as a Base64URL string, but the API needs an ArrayBuffer
    options.challenge = base64urlToBuffer(options.challenge);
    // The user ID must also be an ArrayBuffer
    options.user.id = base64urlToBuffer(options.user.id);

    console.log("Registration Options from Server:", options);

    // 2. Call navigator.credentials.create() to prompt the user
    const credential = await navigator.credentials.create({ publicKey: options });

    console.log("Credential created:", credential);

    // 3. Send the resulting credential to the server for verification
    // The frontend does not need to understand the contents of the response object.
    // It just sends it back to the server to be verified and stored.
    await fetch("/api/webauthn/verify-registration", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credential),
    });

    alert("Registration successful!");
  } catch (error) {
    console.error("Registration failed:", error);
    alert(`Registration failed: ${error}`);
  }
}
```

---

## Registration Flow

The registration flow, or attestation, is how a user creates a new passwordless credential.

### Backend (Python)

1.  **Generate Registration Options**: The server generates `CredentialCreationOptions`, including a unique challenge and information about the Relying Party (your application).
2.  **Send to Frontend**: These options are sent to the frontend to be passed to the browser's WebAuthn API.
3.  **Receive and Verify Attestation**: The frontend returns a `PublicKeyCredentialCreation` object. The server verifies the attestation signature, challenge, and other parameters to ensure the credential was created securely.
4.  **Store Credential**: The server stores the new credential's public key and other metadata associated with the user.

```python
# Full implementation in: docs/identity/examples/webauthn-registration.py
# (See Quick Start section for the code)
```

### Frontend (TypeScript)

The frontend receives the creation options from the backend and uses `navigator.credentials.create()` to interact with the user's authenticator.

```typescript
// Full implementation in: docs/identity/examples/webauthn-frontend.ts
// (See Quick Start section for the code)
```

---

## Authentication Flow

The authentication flow, or assertion, is how a user signs in with a previously registered credential.

### Backend (Python)

1.  **Generate Authentication Options**: The server generates `CredentialRequestOptions`, including a new unique challenge.
2.  **Send Challenge to Frontend**: The options are sent to the frontend.
3.  **Verify Assertion**: The frontend returns a `PublicKeyCredentialAssertion`. The server verifies the signature, challenge, and sign count to confirm the user's identity.
4.  **Return Auth Result**: The server confirms successful authentication and establishes a user session.

```python
"""
WebAuthn Authentication Example (Backend - Python)

This script demonstrates the server-side logic for a WebAuthn credential
authentication flow. It uses a conceptual server-side WebAuthn library.

NOTE: This is a conceptual example that assumes a credential has already
been registered for the user (see webauthn-registration.py).
"""
import base64
from typing import Dict, Any

# A conceptual server-side WebAuthn library. In a real application,
# you would use a library like `webauthn`.
from webauthn import (
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    AuthenticationCredential,
    RegistrationCredential,
)

# Import the TypedDict definitions
from lukhas_website.lukhas.identity.webauthn_types import (
    CredentialRequestOptions,
    PublicKeyCredentialAssertion,
)

# --- In-memory stores for demonstration purposes ---
# This would be populated by the registration flow.
user_credentials: Dict[str, list[RegistrationCredential]] = {
    "testuser": [
        # A conceptual, pre-registered credential object
        RegistrationCredential(
            id=b"credential_id_from_registration",
            public_key=b"user_public_key_bytes",
            sign_count=0,
        )
    ]
}
# --- End of in-memory stores ---

RP_ID = "localhost"  # Relying Party ID - Should be your domain
ORIGIN = "https://localhost:5000"


def run_authentication_flow(username: str):
    """Demonstrates the full authentication flow for a user."""
    print(f"--- 1. Starting authentication for user: {username} ---")
    if username not in user_credentials:
        print(f"No credentials found for user: {username}")
        return

    # --- Server-Side: Generate Authentication Options ---
    auth_options: CredentialRequestOptions = generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=[cred.id for cred in user_credentials[username]],
    )

    print(f"\n--- 2. Server generated authentication options: ---")
    print(auth_options)

    # --- Frontend Simulation: Use options to get an assertion ---
    # In a real app, `auth_options` is sent to the frontend, which calls
    # `navigator.credentials.get()`.
    print("\n--- 3. Simulating frontend authentication... ---")
    # This is a simplified, conceptual representation of a frontend response.
    simulated_frontend_response: PublicKeyCredentialAssertion = {
        "id": "credential_id_from_registration",
        "rawId": "credential_id_from_registration",
        "type": "public-key",
        "response": {
            "clientDataJSON": "base64_encoded_client_data_auth",
            "authenticatorData": "base64_encoded_auth_data",
            "signature": "base64_encoded_signature",
        },
    }
    print("Frontend would send back a response like this (simplified):")
    print(simulated_frontend_response)

    # --- Server-Side: Verify the Frontend Response ---
    print("\n--- 4. Server verifies the assertion from the frontend... ---")
    try:
        # The verification function performs cryptographic checks against the stored public key.
        verified_auth_credential = verify_authentication_response(
            credential=simulated_frontend_response, # This would be the real assertion
            expected_challenge=base64.b64decode(auth_options["challenge"]),
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
            credential_public_key=user_credentials[username][0].public_key,
            credential_current_sign_count=user_credentials[username][0].sign_count,
            require_user_verification=False,
        )

        # --- Update the sign count to prevent replay attacks ---
        user_credentials[username][0].sign_count = verified_auth_credential.new_sign_count

        print(f"\n--- 5. ✅ Authentication successful! ---")
        print(f"New sign count: {verified_auth_credential.new_sign_count}")
        print(f"User {username} is authenticated.")

    except Exception as e:
        print(f"\n--- ❌ Authentication failed: {e} ---")


if __name__ == "__main__":
    run_authentication_flow("testuser")
```

### Frontend (TypeScript)

The frontend receives the request options and uses `navigator.credentials.get()` to prompt the user to use their authenticator.

```typescript
/**
 * Handles the WebAuthn authentication process on the frontend.
 */
async function handleAuthentication() {
  try {
    // 1. Fetch authentication options from the server
    const response = await fetch("/api/webauthn/generate-authentication-options");
    const options: CredentialRequestOptions = await response.json();

    // Convert challenge and any credential IDs from Base64URL to ArrayBuffer
    options.challenge = base64urlToBuffer(options.challenge);
    if (options.allowCredentials) {
      for (const cred of options.allowCredentials) {
        cred.id = base64urlToBuffer(cred.id);
      }
    }

    console.log("Authentication Options from Server:", options);

    // 2. Call navigator.credentials.get() to prompt the user
    const assertion = await navigator.credentials.get({ publicKey: options });

    console.log("Assertion created:", assertion);

    // 3. Send the assertion to the server for verification
    await fetch("/api/webauthn/verify-authentication", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(assertion),
    });

    alert("Authentication successful!");
  } catch (error) {
    console.error("Authentication failed:", error);
    alert(`Authentication failed: ${error}`);
  }
}
```

---

## Credential Management

LUKHAS provides hooks for managing user credentials, including:
- **Listing**: Displaying all credentials registered to a user account.
- **Removing**: De-registering an authenticator (e.g., if a user loses a device).
- **Updating**: Modifying credential metadata, such as a user-friendly name.

---

## API Reference

For a complete reference of all WebAuthn data structures and `TypedDict` definitions used in the LUKHAS framework, please see the [WebAuthn API Reference](./WEBAUTHN_API_REFERENCE.md).

---

## Troubleshooting

Common issues encountered during WebAuthn implementation:

-   **`NotAllowedError` during registration/authentication**: Often caused by the user canceling the prompt, or security policy violations (e.g., trying to register a credential for a domain that doesn't match the Relying Party ID).
-   **`InvalidStateError`**: Can occur if the authenticator is in an unexpected state or if the operation has already been processed.
-   **Browser Compatibility**: Ensure you are using a modern browser that supports WebAuthn Level 2. Check sites like [caniuse.com](https://caniuse.com/webauthn).
-   **HTTPS Requirement**: WebAuthn is a security-sensitive API and can only be used over a secure (HTTPS) connection. `localhost` is typically exempted for development purposes.

---

## Security Best Practices

-   **Challenge Randomness**: Always generate a cryptographically secure, random challenge for every registration and authentication ceremony. Never reuse challenges.
-   **Timeout Values**: Set a reasonable timeout for WebAuthn operations on the server to prevent challenges from being held open indefinitely.
-   **User Verification**: For sensitive operations, set `userVerification` to `"required"` in your authenticator selection criteria to ensure the user provides a PIN, password, or biometric gesture.
-   **Attestation Handling**: Decide on an attestation strategy. For most applications, `"none"` is sufficient. For higher security needs, `"indirect"` or `"direct"` can be used to verify the authenticator's model and origin.

---

## W3C Spec Compliance

-   **WebAuthn Level 2**: The LUKHAS implementation is compliant with the [W3C Web Authentication: An API for accessing Public Key Credentials Level 2](https://www.w3.org/TR/webauthn-2/) specification.
-   **FIDO2/CTAP2**: Our implementation is compatible with FIDO2 and CTAP2 compliant authenticators.
-   **Supported Authenticator Types**: Both platform authenticators (e.g., Windows Hello, Touch ID) and cross-platform authenticators (e.g., YubiKey, Google Titan Key) are supported.