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
