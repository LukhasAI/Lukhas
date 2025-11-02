# SLSA Runbook

This document provides instructions for managing the SLSA attestation process in the LUKHAS project.

## Key Generation

SLSA attestations rely on `cosign` for signing and `in-toto` for provenance. You will need to generate key pairs for both.

### Cosign Key Pair

To generate a new `cosign` key pair, run the following command:

```bash
cosign generate-key-pair
```

This will create `cosign.key` (private key) and `cosign.pub` (public key). You will be prompted to create a password for the private key. **Do not forget this password.**

### In-Toto Key Pair

For `in-toto`, we use an RSA key. Generate it with `openssl`:

```bash
openssl genpkey -algorithm RSA -out in_toto_key.pem -pkeyopt rsa_keygen_bits:2048
```

This will create `in_toto_key.pem`.

## GitHub Secrets Setup

Private keys must be stored as encrypted secrets in GitHub and should never be committed to the repository.

Use the `gh` CLI to set up the secrets:

```bash
# Set the cosign private key
gh secret set COSIGN_KEY --repo LukhasAI/Lukhas --body "$(cat cosign.key)"

# Set the in-toto private key
gh secret set IN_TOTO_KEY --repo LukhasAI/Lukhas --body "$(cat in_toto_key.pem)"

# Set the cosign key password
gh secret set COSIGN_PASSPHRASE --repo LukhasAI/Lukhas --body "your-password-here"
```

## Verification Commands

To verify an attestation, you need the attestation file and the `cosign` public key (`cosign.pub`).

```bash
python3 scripts/verify_attestation.py --att <path_to_attestation.json> --cosign-pub <path_to_cosign.pub>
```

To collect and verify all attestations, run:

```bash
python3 scripts/automation/collect_attestations.py --att-dir <directory_with_attestations> --cosign-pub <path_to_cosign.pub> --out security_posture_report.json
```

## Key Rotation Procedure (90-day cycle)

Keys should be rotated every 90 days for security.

1.  **Generate new key pairs** on a secure host as described in the "Key Generation" section.
2.  **Update the public key** in the repository. Commit the new `cosign.pub` to `docs/gonzo/cosign_pub.pem`.
3.  **Create a Pull Request** with the new public key. This allows for an audit trail.
4.  **After the PR is merged**, update the `COSIGN_KEY`, `IN_TOTO_KEY`, and `COSIGN_PASSPHRASE` secrets in the GitHub repository with the new private keys and password.
5.  **Re-run the `slsa-attest-matrix` workflow** to re-sign all artifacts with the new keys.
6.  **Revoke the old keys** and record the rotation in the audit log.

## Security Best Practices

-   **NEVER** commit private keys (`cosign.key`, `in_toto_key.pem`) to the repository.
-   Use strong, unique passwords for `cosign` keys.
-   Store private keys in a secure location, such as a password manager or hardware token.
-   Limit access to the GitHub secrets to a small number of trusted individuals.
