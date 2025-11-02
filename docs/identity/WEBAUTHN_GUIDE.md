# WebAuthn in LUKHAS: Developer Guide

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

## Overview
WebAuthn is a web standard for secure, passwordless authentication. It uses public-key cryptography to protect users from phishing attacks. LUKHAS provides a comprehensive implementation of the W3C WebAuthn Level 2 specification, enabling developers to integrate passwordless authentication into their applications with ease.

This guide provides a step-by-step walkthrough of how to use the WebAuthn features within the LUKHAS ecosystem.

## Quick Start
To get started with WebAuthn in LUKHAS, you need to implement two main flows: registration and authentication.

**Registration:**
1.  The client requests registration from the LUKHAS backend.
2.  The backend generates credential creation options and sends them to the client.
3.  The client uses `navigator.credentials.create()` to create a new credential.
4.  The client sends the new credential to the backend for verification and storage.

**Authentication:**
1.  The client requests authentication from the LUKHAS backend.
2.  The backend generates credential request options and sends them to the client.
3.  The client uses `navigator.credentials.get()` to get an assertion.
4.  The client sends the assertion to the backend for verification.

## Registration Flow
The registration flow consists of a backend and a frontend component.

### Backend (Python)
The backend is responsible for generating the registration options and verifying the attestation response.

```python
#!/usr/bin/env python3
"""
WebAuthn Registration Example (Backend)

This script demonstrates the server-side flow for WebAuthn credential registration.
"""
import base64
from webauthn import generate_registration_options, verify_registration_response
from webauthn.helpers.structs import RegistrationCredential

from lukhas_website.lukhas.identity.webauthn_types import (
    CredentialCreationOptions,
    PublicKeyCredentialCreation,
)

RP_ID = "localhost"
RP_NAME = "LUKHAS Demo"
ORIGIN = "http://localhost:3000"


def generate_options(user_id: str, username: str) -> CredentialCreationOptions:
    """Generate registration options for the client."""
    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=user_id.encode(),
        user_name=username,
    )
    return options.model_dump(mode="json")


def verify_registration(credential: PublicKeyCredentialCreation, challenge: str) -> None:
    """Verify the registration response from the client."""
    webauthn_credential = RegistrationCredential.parse_raw(credential.json())

    verification = verify_registration_response(
        credential=webauthn_credential,
        expected_challenge=challenge.encode(),
        expected_origin=ORIGIN,
        expected_rp_id=RP_ID,
    )

    if not verification.verified:
        raise Exception("Registration verification failed")

    print("Registration successful!")
    print(f"  Credential ID: {base64.b64encode(verification.credential_id).decode('utf-8')}")
    print(f"  Sign count: {verification.sign_count}")


if __name__ == "__main__":
    # 1. Generate registration options
    user_id = "testuser"
    username = "Test User"
    options = generate_options(user_id, username)
    challenge = options["challenge"]

    print("** Registration Options **")
    print(options)

    # 2. In a real application, the client would use these options to create a
    #    credential and send it back to the server. Here, we simulate a
    #    successful registration for demonstration purposes.
```

### Frontend (TypeScript)
The frontend uses the options from the backend to create a new credential.

```typescript
// WebAuthn Frontend Example (TypeScript)

import { CredentialCreationOptions, CredentialRequestOptions } from './webauthn_types';

// --- Registration ---

async function register(options: CredentialCreationOptions): Promise<void> {
  try {
    const credential = await navigator.credentials.create({ publicKey: options });
    console.log("Registration successful!", credential);

    // Send the credential to the backend for verification
    // await sendToServer('/register/finish', credential);
  } catch (err) {
    console.error("Registration failed:", err);
  }
}

// --- Authentication ---

async function authenticate(options: CredentialRequestOptions): Promise<void> {
  try {
    const assertion = await navigator.credentials.get({ publicKey: options });
    console.log("Authentication successful!", assertion);

    // Send the assertion to the backend for verification
    // await sendToServer('/authenticate/finish', assertion);
  } catch (err) {
    console.error("Authentication failed:", err);
  }
}

// --- Example Usage ---

// In a real application, you would fetch these options from your backend.

// Example registration options
const registrationOptions: CredentialCreationOptions = {
  challenge: "...".toString(), // Replace with a real challenge from the server
  rp: {
    name: "LUKHAS Demo",
    id: "localhost",
  },
  user: {
    id: "...".toString(), // Replace with a real user ID
    name: "testuser",
    displayName: "Test User",
  },
  pubKeyCredParams: [{ alg: -7, type: "public-key" }],
  timeout: 60000,
  attestation: "direct",
};

// Example authentication options
const authenticationOptions: CredentialRequestOptions = {
  challenge: "...".toString(), // Replace with a real challenge from the server
  allowCredentials: [
    {
      type: "public-key",
      id: "...".toString(), // Replace with a real credential ID
    },
  ],
  timeout: 60000,
};

// You would call these functions based on user actions.
// For example, when a user clicks a "Register" or "Login" button.

// register(registrationOptions);
// authenticate(authenticationOptions);
```

## Authentication Flow
The authentication flow also consists of a backend and a frontend component.

### Backend (Python)
The backend generates the authentication options and verifies the assertion.

```python
#!/usr/bin/env python3
"""
WebAuthn Authentication Example (Backend)

This script demonstrates the server-side flow for WebAuthn credential authentication.
"""
import base64
from webauthn import (
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import AuthenticationCredential

from lukhas_website.lukhas.identity.webauthn_types import (
    CredentialRequestOptions,
    PublicKeyCredentialAssertion,
)

RP_ID = "localhost"
ORIGIN = "http://localhost:3000"


def generate_options(credential_id: str) -> CredentialRequestOptions:
    """Generate authentication options for the client."""
    options = generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=[{"id": base64.b64decode(credential_id), "type": "public-key"}],
    )
    return options.model_dump(mode="json")


def verify_authentication(
    credential: PublicKeyCredentialAssertion,
    challenge: str,
    cred_public_key: bytes,
    cred_sign_count: int,
) -> None:
    """Verify the authentication response from the client."""
    webauthn_credential = AuthenticationCredential.parse_raw(credential.json())

    verification = verify_authentication_response(
        credential=webauthn_credential,
        expected_challenge=challenge.encode(),
        expected_rp_id=RP_ID,
        expected_origin=ORIGIN,
        credential_public_key=cred_public_key,
        credential_current_sign_count=cred_sign_count,
    )

    if not verification.verified:
        raise Exception("Authentication verification failed")

    print("Authentication successful!")
    print(f"  New sign count: {verification.new_sign_count}")


if __name__ == "__main__":
    # This is a placeholder for a credential ID that would be stored in a database.
    CREDENTIAL_ID = "..."

    if CREDENTIAL_ID == "...":
        print("Please replace '...' with a valid credential ID from a registration.")
    else:
        # 1. Generate authentication options
        options = generate_options(CREDENTIAL_ID)
        challenge = options["challenge"]

        print("** Authentication Options **")
        print(options)

        # 2. In a real application, the client would use these options to get an
        #    assertion and send it back to the server. Here, we would need to
        #    simulate a successful authentication.
```

### Frontend (TypeScript)
The frontend uses the options from the backend to get a credential assertion.

```typescript
// WebAuthn Frontend Example (TypeScript)

import { CredentialCreationOptions, CredentialRequestOptions } from './webauthn_types';

// --- Registration ---

async function register(options: CredentialCreationOptions): Promise<void> {
  try {
    const credential = await navigator.credentials.create({ publicKey: options });
    console.log("Registration successful!", credential);

    // Send the credential to the backend for verification
    // await sendToServer('/register/finish', credential);
  } catch (err) {
    console.error("Registration failed:", err);
  }
}

// --- Authentication ---

async function authenticate(options: CredentialRequestOptions): Promise<void> {
  try {
    const assertion = await navigator.credentials.get({ publicKey: options });
    console.log("Authentication successful!", assertion);

    // Send the assertion to the backend for verification
    // await sendToServer('/authenticate/finish', assertion);
  } catch (err) {
    console.error("Authentication failed:", err);
  }
}

// --- Example Usage ---

// In a real application, you would fetch these options from your backend.

// Example registration options
const registrationOptions: CredentialCreationOptions = {
  challenge: "...".toString(), // Replace with a real challenge from the server
  rp: {
    name: "LUKHAS Demo",
    id: "localhost",
  },
  user: {
    id: "...".toString(), // Replace with a real user ID
    name: "testuser",
    displayName: "Test User",
  },
  pubKeyCredParams: [{ alg: -7, type: "public-key" }],
  timeout: 60000,
  attestation: "direct",
};

// Example authentication options
const authenticationOptions: CredentialRequestOptions = {
  challenge: "...".toString(), // Replace with a real challenge from the server
  allowCredentials: [
    {
      type: "public-key",
      id: "...".toString(), // Replace with a real credential ID
    },
  ],
  timeout: 60000,
};

// You would call these functions based on user actions.
// For example, when a user clicks a "Register" or "Login" button.

// register(registrationOptions);
// authenticate(authenticationOptions);
```

## Credential Management
LUKHAS provides functionalities to manage WebAuthn credentials, including:
-   **Listing user credentials:** Retrieve a list of all credentials associated with a user account.
-   **Removing credentials:** Delete a credential from a user account.
-   **Updating credential metadata:** Update information associated with a credential, such as its name.

## API Reference
For a detailed description of all the WebAuthn-related data structures and types, please refer to the [WebAuthn API Reference](./WEBAUTHN_API_REFERENCE.md).

## Troubleshooting
Here are some common issues you might encounter when implementing WebAuthn:

-   **"NotAllowedError" during registration:** This error can occur if the user cancels the registration ceremony or if the authenticator cannot create a new credential.
-   **"InvalidStateError" during authentication:** This error can happen if the authenticator is in an invalid state or if the request is malformed.
-   **Browser compatibility issues:** Ensure that the user's browser supports WebAuthn.
-   **HTTPS requirement:** WebAuthn requires a secure context (HTTPS) to operate.

## Security Best Practices
When implementing WebAuthn, it is crucial to follow these security best practices:

-   **Challenge randomness:** Always generate a new, cryptographically random challenge for each registration and authentication ceremony.
-   **Timeout values:** Set reasonable timeout values for the registration and authentication ceremonies to prevent replay attacks.
-   **User verification requirements:** Enforce user verification (`required`) for sensitive operations.
-   **Attestation handling:** Carefully consider the attestation type to use. For most cases, `none` is sufficient.

## W3C Spec Compliance
The LUKHAS WebAuthn implementation is compliant with the [W3C Web Authentication: An API for accessing Public Key Credentials Level 2](https://www.w3.org/TR/webauthn-2/) specification. It supports a wide range of authenticators and provides a secure and reliable way to implement passwordless authentication.