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
uers: Dict[str, Dict[str, Any]] = {
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

    print("\n--- 2. Server generated registration options: ---")
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

        print("\n--- 5. ✅ Registration successful! ---")
        print(f"Credential ID: {verified_credential.id}")
        print(f"Stored for user: {username}")

    except Exception as e:
        print(f"\n--- ❌ Registration failed: {e} ---")


if __name__ == "__main__":
    run_registration_flow("testuser")
