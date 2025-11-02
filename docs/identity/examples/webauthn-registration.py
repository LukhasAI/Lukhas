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
