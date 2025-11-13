# Operational Event Signing

This document describes the process for signing operational events, such as release notes and policy changes, using the Quantum Resonance Glyph (QRG) system.

## Purpose

Signing operational events provides a verifiable and tamper-evident record of important changes within the LUKHAS ecosystem. By using the QRG system, we embed a unique, quantum-resistant signature into a JSON artifact that accompanies the original content. This ensures the authenticity and integrity of our operational artifacts.

## Signing Script

The signing process is automated via the `sign_ops_events.py` script.

### Usage

To sign a file, run the script from the root of the repository with the following command-line arguments:

```bash
python3 scripts/identity/sign_ops_events.py \
    --input-file <path_to_input_file> \
    --output-file <path_to_output_artifact.json> \
    --user-identity <your_symbolic_identity>
```

**Arguments:**

*   `--input-file`: The relative path to the file you want to sign (e.g., `release/notes/v1.2.3.md`).
*   `--output-file`: The relative path where the signed JSON artifact will be saved.
*   `--user-identity`: A symbolic name representing the signer (e.g., `ops-release-manager`, `policy-committee`).

### Example

```bash
python3 scripts/identity/sign_ops_events.py \
    --input-file docs/policies/new_policy.md \
    --output-file release_artifacts/new_policy.md.json \
    --user-identity 'policy-committee'
```

## Signed Artifact Structure

The output of the signing script is a JSON file with the following structure:

```json
{
  "signer_identity": "string",
  "timestamp_utc": "string (ISO 8601 format)",
  "content_sha256": "string (SHA256 hash of the original content)",
  "signature_type": "string (e.g., 'QRG-v1')",
  "signature": {
    "glyph_id": "string",
    "qi_signature": "string (quantum-resistant signature)",
    "consciousness_fingerprint": "string",
    "temporal_validity": "string (ISO 8601 format)",
    "hidden_payload": null
  },
  "original_content": "string (the full content of the input file)"
}
```

-   **`signer_identity`**: The user identity provided to the script.
-   **`timestamp_utc`**: The UTC timestamp of when the signing occurred.
-   **`content_sha256`**: The SHA256 hash of the original file content, for quick integrity checks.
-   **`signature`**: The QRG signature object.
-   **`original_content`**: A copy of the original content that was signed.

This signed artifact should be stored alongside the original document as a verifiable record of its authenticity.
