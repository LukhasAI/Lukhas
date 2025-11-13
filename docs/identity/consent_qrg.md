# Embedding Consent in Quantum Resonance Glyphs (QRGs)

This document outlines the process of embedding a cryptographic hash of a user's consent record into the payload of a Quantum Resonance Glyph (QRG). This mechanism provides a verifiable link between a user's authentication token (the QRG) and the specific consent they have provided for data processing, enhancing the integrity and auditability of the LUKHAS identity system.

## Overview

The `scripts/identity/embed_consent_in_qrg.py` script is responsible for this process. It performs the following key functions:

1.  **Generates a Consent Hash**: It creates a unique and verifiable hash from a user's `ConsentRecord`.
2.  **Generates a QRG**: It produces a standard QRG for a given user identity.
3.  **Embeds the Hash**: It embeds the consent hash into the QRG's hidden data payload.

This ensures that the QRG not only serves as an authentication credential but also carries a tamper-proof reference to the consent status of the user at the time of its generation.

## Consent Hash Generation

The integrity of the process relies on a consistent and secure hashing mechanism. The consent hash is generated from the following fields of a `ConsentRecord`:

-   `consent_id`: The unique identifier of the consent record.
-   `user_id`: The identifier of the user who gave consent.
-   `purpose_id`: The specific purpose for which consent was granted (e.g., `service_improvement`).
-   `granted_at`: The ISO 8601 formatted timestamp of when the consent was granted.
-   `method`: The method through which consent was obtained (e.g., `web_form`).
-   `consent_text`: The exact text presented to the user when they gave consent.

These fields are collected into a JSON object, which is then serialized and hashed using **SHA-256**.

### Example Hashing Logic:

```python
import json
import hashlib

hash_data = {
    "consent_id": "consent_abc_456",
    "user_id": "test_user_123",
    "purpose_id": "core_functionality",
    "granted_at": "2025-11-12T10:00:00Z",
    "method": "api_call",
    "consent_text": "I agree to the terms for core_functionality."
}

serialized_data = json.dumps(hash_data, sort_keys=True)
consent_hash = hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()
```

## QRG Payload Structure

The generated consent hash is embedded within the `hidden_payload` of the QRG. This payload is structured as a set of claims, similar to a JSON Web Token (JWT), providing context about the assertion being made.

The structure of the payload is as follows:

```json
{
  "iss": "lukhas.identity",
  "aud": "lukhas.qrg_verifier",
  "iat": "2025-11-12T13:19:14.151875",
  "sub": "user_7c5b8e9f",
  "claims": {
    "consent_hash": "95df9cd7a32c944618458174ab55d3e1776ca409cbf6fb869bf6c7766821ea3b",
    "consent_id": "consent_c1344beaadcd",
    "purpose": "service_improvement"
  }
}
```

-   `iss` (Issuer): Identifies the LUKHAS service that issued the token.
-   `aud` (Audience): The intended recipient or verifier of the token.
-   `iat` (Issued At): The timestamp when the QRG was generated.
-   `sub` (Subject): The user identity associated with the QRG.
-   `claims`: A nested object containing the specific assertions.
    -   `consent_hash`: The SHA-256 hash of the consent record.
    -   `consent_id`: The ID of the consent record, for easy lookup.
    -   `purpose`: The purpose ID associated with the consent.

## Verification Process

When a system component receives a QRG, it can verify the consent by:

1.  Extracting the `hidden_payload` from the QRG.
2.  Retrieving the `consent_id` from the payload.
3.  Looking up the full `ConsentRecord` from the consent management system using the `consent_id`.
4.  Re-generating the consent hash from the retrieved `ConsentRecord` using the same hashing logic.
5.  Comparing the re-generated hash with the `consent_hash` from the QRG payload. If they match, the consent is verified.
