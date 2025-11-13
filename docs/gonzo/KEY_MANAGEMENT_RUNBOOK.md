# Key Management Runbook

This document provides instructions for managing cryptographic keys in the LUKHAS project.

## Key Generation

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

## GitHub Secrets Configuration

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

## Key Rotation Procedure (90-day cycle)

Keys should be rotated every 90 days for security. The `scripts/security/rotate_keys.sh` script can be used to automate this process.

1.  **Run the rotation script**: `bash scripts/security/rotate_keys.sh`
2.  **Follow the prompts** to generate new keys and create a pull request with the new public key.
3.  **After the PR is merged**, the script will guide you to update the secrets in GitHub.
4.  **The script will also re-run the SLSA attestation workflow** to re-sign all artifacts with the new keys.

## Emergency Key Revocation

In the event of a key compromise, you must immediately revoke the compromised key.

1.  **Generate new keys** as described in the "Key Generation" section.
2.  **Update the public key** in the repository and create a pull request.
3.  **After the PR is merged**, update the secrets in GitHub.
4.  **Re-run the SLSA attestation workflow** to re-sign all artifacts with the new keys.
5.  **Notify users** to re-verify any artifacts they have downloaded.

## Audit Log

All key rotation events must be recorded in `docs/gonzo/key_rotation_audit.log`. The `rotate_keys.sh` script will automatically add an entry to this log.

### Audit Log Template

```
Date | Key Type | Action | Operator | Notes
--- | --- | --- | --- | ---
2025-11-02 | cosign | rotated | ops@lukhas.ai | Routine 90-day rotation
```
