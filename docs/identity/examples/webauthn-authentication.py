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

    print("\n--- 2. Server generated authentication options: ---")
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

        print("\n--- 5. ✅ Authentication successful! ---")
        print(f"New sign count: {verified_auth_credential.new_sign_count}")
        print(f"User {username} is authenticated.")

    except Exception as e:
        print(f"\n--- ❌ Authentication failed: {e} ---")


if __name__ == "__main__":
    run_authentication_flow("testuser")
