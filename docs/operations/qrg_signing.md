# QRG Operational Signing Guide
**Version**: 1.0.0
**Last Updated**: 2025-11-12
**Status**: Production

## Overview

This guide documents operational procedures for QRG (Quantum Resilient Glyph) cryptographic signing of critical system events. QRG signatures provide tamper-evident provenance for release notes, policy changes, and operational decisions requiring accountability and non-repudiation.

**Key Principles**:
- All critical system changes MUST be signed with QRG signatures
- Signatures provide cryptographic proof of authenticity and integrity
- Verification MUST occur before applying signed changes
- Private keys MUST be secured with strict access controls

## When to Sign Events

### MUST Sign (Required)

QRG signatures are **REQUIRED** for the following operational events:

#### 1. Software Releases
- Release notes for production deployments
- Version updates with security implications
- Breaking changes requiring user notification
- Emergency patches and hotfixes

**Rationale**: Release notes affect user trust and system integrity. Unsigned releases are vulnerable to tampering and impersonation attacks.

#### 2. Guardian Policy Changes
- Drift detection threshold modifications
- Constitutional AI principle updates
- Safety validation rule changes
- Feature flag configuration changes

**Rationale**: Guardian policies enforce ethical constraints. Unauthorized modifications could bypass safety mechanisms and lead to alignment drift.

#### 3. Security Configuration Updates
- Authentication policy changes
- Access control rule modifications
- Key rotation procedures
- Certificate updates

**Rationale**: Security configurations protect system integrity. Tampering could enable unauthorized access or privilege escalation.

#### 4. Consent Policy Changes
- User consent requirements
- Data retention policies
- Privacy configuration updates
- GDPR compliance settings

**Rationale**: Consent policies implement legal requirements. Unauthorized changes could violate regulations and user rights.

### SHOULD Sign (Recommended)

QRG signatures are **RECOMMENDED** for the following operational events:

#### 1. System Configuration Changes
- Database connection string updates
- External API endpoint changes
- Feature rollout configurations
- Performance tuning parameters

#### 2. Operational Decisions
- Incident response actions
- Emergency maintenance procedures
- System degradation decisions
- Capacity planning changes

#### 3. Audit Events
- Access control decisions
- Data deletion events
- System administrator actions
- Compliance audit triggers

### MAY Sign (Optional)

QRG signatures are **OPTIONAL** but beneficial for:

- Internal documentation updates
- Development environment changes
- Testing configuration updates
- Non-production experiments

### MUST NOT Sign

Do NOT use QRG signatures for:

- Routine logging events (excessive overhead)
- High-frequency operational metrics (performance impact)
- Temporary development changes (unnecessary)
- Non-critical informational messages

## How to Sign Events

### Prerequisites

1. **Private Key**: Obtain authorized private key for signing
2. **Python Environment**: Python 3.9+ with `cryptography` library
3. **QRG Tools**: `scripts/qrg/sign_ops_event.py` script
4. **Permissions**: Authorization to sign on behalf of organization

### Signing Release Notes

#### Command-Line Usage

```bash
python scripts/qrg/sign_ops_event.py sign-release \
  --version 1.0.0 \
  --notes "Security fixes for Guardian drift detection" \
  --key /path/to/release_key.pem \
  --author "LUKHAS AI Team" \
  --output release_1.0.0_signed.json
```

#### Programmatic Usage

```python
from scripts.qrg.sign_ops_event import sign_release_notes

signature_data = sign_release_notes(
    version="1.0.0",
    notes="Security fixes for Guardian drift detection",
    key_path="/path/to/release_key.pem",
    author="LUKHAS AI Team",
    date="2025-11-12"
)

# Save to file
import json
with open("release_1.0.0_signed.json", "w") as f:
    json.dump(signature_data, f, indent=2)
```

#### Output Structure

```json
{
  "payload": {
    "type": "release_notes",
    "version": "1.0.0",
    "date": "2025-11-12",
    "notes": "Security fixes for Guardian drift detection",
    "author": "LUKHAS AI Team"
  },
  "qrg_signature": {
    "algo": "ecdsa-sha256",
    "pubkey_pem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
    "sig_b64": "MEUCIQDExampleSignatureBase64...",
    "ts": "2025-11-12T18:30:00.000Z",
    "payload_hash": "a3f5d8c2e1b7f4a9c3d6e8b1a2f5c8d9...",
    "consent_hash": null
  }
}
```

### Signing Policy Changes

#### Command-Line Usage

```bash
python scripts/qrg/sign_ops_event.py sign-policy \
  --policy-id guardian_drift_threshold \
  --change "Increased threshold to reduce false positives" \
  --old-value 0.15 \
  --new-value 0.20 \
  --approved-by governance_committee \
  --reason "Based on 30-day analysis of drift patterns" \
  --key /path/to/policy_key.pem \
  --output policy_drift_threshold_20251112.json
```

#### Programmatic Usage

```python
from scripts.qrg.sign_ops_event import sign_policy_change

signature_data = sign_policy_change(
    policy_id="guardian_drift_threshold",
    change_desc="Increased threshold to reduce false positives",
    key_path="/path/to/policy_key.pem",
    old_value="0.15",
    new_value="0.20",
    approved_by="governance_committee",
    reason="Based on 30-day analysis of drift patterns"
)
```

#### Output Structure

```json
{
  "payload": {
    "type": "policy_change",
    "policy_id": "guardian_drift_threshold",
    "change_desc": "Increased threshold to reduce false positives",
    "old_value": "0.15",
    "new_value": "0.20",
    "approved_by": "governance_committee",
    "reason": "Based on 30-day analysis of drift patterns",
    "timestamp": "2025-11-12T18:30:00.000Z"
  },
  "qrg_signature": {...}
}
```

## How to Verify Signatures

### Command-Line Verification

```bash
python scripts/qrg/sign_ops_event.py verify \
  --signature release_1.0.0_signed.json
```

**Success Output**:
```
Verifying signature from: release_1.0.0_signed.json
Payload type: release_notes
✅ Signature is VALID
```

**Failure Output**:
```
Verifying signature from: release_1.0.0_signed.json
Payload type: release_notes
❌ Signature is INVALID
```

### Programmatic Verification

```python
import json
from scripts.qrg.sign_ops_event import verify_signature

# Load signed event
with open("release_1.0.0_signed.json", "r") as f:
    signature_data = json.load(f)

# Verify signature
if verify_signature(signature_data):
    print("Signature is valid")
    # Proceed with applying change
else:
    print("Signature is INVALID - DO NOT APPLY CHANGE")
    # Raise alert for potential tampering
```

### Low-Level Verification

```python
from core.qrg.signing import qrg_verify

payload = {...}  # Payload from signed event
qrg_signature = {...}  # QRG signature from signed event

is_valid = qrg_verify(payload, qrg_signature)
```

### Verification Checklist

Before applying a signed change, verify ALL of the following:

- [ ] **Signature cryptographically valid**: `qrg_verify()` returns `True`
- [ ] **Payload hash matches**: Signature `payload_hash` matches computed hash
- [ ] **Timestamp recent**: Signature `ts` within acceptable time window (e.g., 30 days)
- [ ] **Public key trusted**: Signature `pubkey_pem` belongs to authorized signer
- [ ] **Payload fields complete**: All required fields present in payload
- [ ] **Change authorized**: Change approved by appropriate authority
- [ ] **Consent verified**: If `consent_hash` present, consent document available

### Detecting Tampering

QRG signatures detect the following tampering attempts:

1. **Payload Modification**: Any change to payload fields invalidates signature
2. **Signature Byte Tampering**: Modifications to `sig_b64` fail verification
3. **Payload Hash Substitution**: Mismatched `payload_hash` detected during verification
4. **Public Key Substitution**: Different key produces different signature
5. **Timestamp Manipulation**: Replay protection detects old signatures

**Example - Tampering Detection**:

```python
# Original signed release
with open("release_1.0.0_signed.json", "r") as f:
    signed_release = json.load(f)

# Attacker tampers with version
signed_release["payload"]["version"] = "2.0.0"

# Verification detects tampering
if not verify_signature(signed_release):
    print("ALERT: Tampering detected!")
    print("Payload has been modified after signing")
    # Trigger incident response
```

## Key Management Procedures

### Key Generation

#### Generating Private Key

```bash
# Generate ECDSA P-256 private key
openssl ecparam -name prime256v1 -genkey -noout -out private_key.pem

# Extract public key
openssl ec -in private_key.pem -pubout -out public_key.pem
```

#### Programmatic Key Generation

```python
from core.qrg.signing import generate_private_key, private_key_to_pem, public_key_to_pem

# Generate key pair
priv_key = generate_private_key()

# Export private key
priv_pem = private_key_to_pem(priv_key)
with open("private_key.pem", "wb") as f:
    f.write(priv_pem)

# Export public key
pub_key = priv_key.public_key()
pub_pem = public_key_to_pem(pub_key)
with open("public_key.pem", "wb") as f:
    f.write(pub_pem)
```

### Key Storage

#### Private Key Storage Requirements

**MUST**:
- Store private keys encrypted at rest
- Use Hardware Security Module (HSM) or Key Management Service (KMS) in production
- Restrict file permissions to owner-only (`chmod 600 private_key.pem`)
- NEVER commit private keys to version control
- NEVER share private keys via email or chat

**SHOULD**:
- Use separate keys for different signing contexts (release vs. policy vs. security)
- Implement key escrow for business continuity
- Store backup keys in physically separate locations
- Use multi-party computation for high-value keys

**RECOMMENDED Storage Locations**:
- **Production**: AWS KMS, Azure Key Vault, Google Cloud KMS, Hardware Security Module
- **Development**: Encrypted file system with strong passphrase
- **Testing**: Temporary keys generated per test run (never reused)

#### Public Key Distribution

**Public keys MAY be**:
- Published in organization's public key directory
- Embedded in signed events (self-contained verification)
- Distributed via secure channel (TLS, PKI)
- Registered in blockchain or transparency log

**Example - Public Key Directory**:
```
https://lukhas.ai/.well-known/qrg-keys/
  - release_signing_key.pem
  - policy_signing_key.pem
  - security_signing_key.pem
```

### Key Rotation

#### When to Rotate Keys

Keys SHOULD be rotated:
- **Regularly**: Annual rotation as preventive measure
- **Compromise**: Immediate rotation if key suspected compromised
- **Personnel Changes**: Rotation when key holders leave organization
- **Algorithm Updates**: Rotation when upgrading to post-quantum algorithms

#### Key Rotation Procedure

1. **Generate New Key Pair**
   ```bash
   openssl ecparam -name prime256v1 -genkey -noout -out new_private_key.pem
   openssl ec -in new_private_key.pem -pubout -out new_public_key.pem
   ```

2. **Test New Key**
   ```bash
   # Sign test payload with new key
   python scripts/qrg/sign_ops_event.py sign-release \
     --version test-rotation \
     --notes "Key rotation test" \
     --key new_private_key.pem \
     --output test_signature.json

   # Verify test signature
   python scripts/qrg/sign_ops_event.py verify --signature test_signature.json
   ```

3. **Publish New Public Key**
   - Update public key directory
   - Announce key rotation in release notes
   - Maintain old public key for verification of past signatures

4. **Transition Period**
   - Sign with both old and new keys for 30 days
   - Accept signatures from both keys during transition
   - Monitor for verification failures

5. **Deprecate Old Key**
   - After transition period, sign only with new key
   - Archive old key for historical verification
   - Update documentation with new key fingerprint

6. **Revoke Old Key** (if compromised)
   - Publish key revocation notice immediately
   - Invalidate all signatures from old key
   - Trigger re-signing of active configurations

### Key Compromise Response

If private key is compromised:

1. **Immediate Actions** (within 1 hour)
   - Rotate to new key immediately
   - Revoke compromised key
   - Publish security advisory
   - Alert all stakeholders

2. **Investigation** (within 24 hours)
   - Audit all signatures from compromised key
   - Identify potentially malicious signatures
   - Assess scope of compromise

3. **Remediation** (within 1 week)
   - Re-sign all active configurations with new key
   - Invalidate signatures from compromised key
   - Update verification systems to reject old key
   - Conduct security review

4. **Post-Incident** (within 1 month)
   - Improve key storage procedures
   - Implement additional access controls
   - Update incident response playbook
   - Train personnel on key security

### Key Backup and Recovery

#### Backup Procedures

**Production Keys**:
- Store encrypted backup in secure offline location
- Use Shamir Secret Sharing for high-value keys (e.g., M-of-N recovery)
- Test recovery procedure quarterly
- Document recovery process in runbook

**Example - Shamir Secret Sharing**:
```bash
# Split key into 5 shares, require 3 to recover
ssss-split -t 3 -n 5 < private_key.pem

# Distribute shares to 5 trusted individuals
# To recover: gather 3 shares and run
ssss-combine -t 3
```

#### Recovery Testing

Test key recovery annually:

1. Simulate key loss scenario
2. Execute recovery procedure from documentation
3. Verify recovered key matches original (compare public key)
4. Document time to recover and issues encountered
5. Update recovery procedures based on lessons learned

## Integration with CI/CD

### Automated Release Signing

#### GitHub Actions Example

```yaml
name: Sign Release
on:
  release:
    types: [published]

jobs:
  sign-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install cryptography

      - name: Sign release notes
        env:
          RELEASE_KEY: ${{ secrets.RELEASE_SIGNING_KEY }}
        run: |
          echo "$RELEASE_KEY" > release_key.pem
          python scripts/qrg/sign_ops_event.py sign-release \
            --version ${{ github.event.release.tag_name }} \
            --notes "${{ github.event.release.body }}" \
            --key release_key.pem \
            --output release_${{ github.event.release.tag_name }}_signed.json
          rm release_key.pem

      - name: Upload signed release
        uses: actions/upload-artifact@v3
        with:
          name: signed-release
          path: release_*.json
```

### Pre-Deployment Verification

#### Deployment Script Example

```bash
#!/bin/bash
# deploy.sh - Verify signature before deploying

RELEASE_FILE="$1"

echo "Verifying release signature..."
if python scripts/qrg/sign_ops_event.py verify --signature "$RELEASE_FILE"; then
    echo "✅ Signature valid, proceeding with deployment"

    # Extract version and deploy
    VERSION=$(jq -r '.payload.version' "$RELEASE_FILE")
    ./deploy_version.sh "$VERSION"
else
    echo "❌ Signature invalid, ABORTING deployment"
    exit 1
fi
```

## Monitoring and Auditing

### Signature Audit Logging

Log ALL signature operations:

```python
import logging

logger = logging.getLogger("qrg_audit")

def audit_log_signature(operation: str, payload_type: str, payload_id: str, result: str):
    """Log signature operation to audit trail."""
    logger.info(
        f"QRG_AUDIT: operation={operation} type={payload_type} "
        f"id={payload_id} result={result} timestamp={datetime.utcnow().isoformat()}"
    )

# Example usage
audit_log_signature(
    operation="sign",
    payload_type="release_notes",
    payload_id="release-1.0.0",
    result="success"
)

audit_log_signature(
    operation="verify",
    payload_type="policy_change",
    payload_id="drift_threshold_change",
    result="failure"  # Potential tampering!
)
```

### Alerting on Verification Failures

Monitor for signature verification failures:

```python
from scripts.qrg.sign_ops_event import verify_signature

def verify_and_alert(signature_data: dict) -> bool:
    """Verify signature and alert on failure."""
    if verify_signature(signature_data):
        return True
    else:
        # ALERT: Potential tampering detected
        send_alert(
            severity="HIGH",
            message=f"QRG signature verification failed for {signature_data['payload']['type']}",
            details=signature_data
        )
        return False
```

### Metrics to Track

Monitor the following metrics:

- **Signature Generation Rate**: Signatures created per day
- **Verification Success Rate**: Percentage of successful verifications
- **Verification Failure Rate**: Percentage of failed verifications (should be near 0%)
- **Average Signature Age**: Time between signature creation and verification
- **Key Rotation Compliance**: Days since last key rotation

## Troubleshooting

### Common Issues

#### Issue: "Private key file not found"

**Cause**: Key file path incorrect or file missing

**Solution**:
```bash
# Verify file exists
ls -la /path/to/key.pem

# Check file permissions
ls -l /path/to/key.pem
# Should show: -rw------- (600)

# Use absolute path
python scripts/qrg/sign_ops_event.py sign-release \
  --key $(pwd)/private_key.pem \
  ...
```

#### Issue: "Signature verification failed"

**Cause**: Payload has been tampered with or wrong public key

**Solution**:
```python
# Check payload hash
from core.qrg.signing import canonical_payload_hash

expected_hash = canonical_payload_hash(payload)
actual_hash = qrg_signature["payload_hash"]

if expected_hash != actual_hash:
    print("Payload has been modified!")
    print(f"Expected: {expected_hash}")
    print(f"Actual: {actual_hash}")
```

#### Issue: "Invalid key format"

**Cause**: Key file is not PEM-encoded ECDSA P-256

**Solution**:
```bash
# Verify key format
openssl ec -in private_key.pem -text -noout

# Should show: "ASN1 OID: prime256v1"
# If not, regenerate key with correct curve
```

#### Issue: "Permission denied reading key file"

**Cause**: Insufficient file permissions

**Solution**:
```bash
# Check permissions
ls -l private_key.pem

# Fix permissions
chmod 600 private_key.pem

# Verify current user owns file
chown $USER:$USER private_key.pem
```

## Security Best Practices

### Do's ✅

- ✅ Use separate keys for different signing contexts
- ✅ Rotate keys annually or after personnel changes
- ✅ Store private keys in HSM/KMS in production
- ✅ Verify signatures before applying changes
- ✅ Log all signature operations to audit trail
- ✅ Test key recovery procedures regularly
- ✅ Implement timestamp validation for replay protection
- ✅ Monitor verification failure rate (should be ~0%)
- ✅ Publish public keys in trusted directory
- ✅ Use strong file permissions (600) on private keys

### Don'ts ❌

- ❌ NEVER commit private keys to version control
- ❌ NEVER share private keys via email or chat
- ❌ NEVER reuse keys across environments (prod vs. dev)
- ❌ NEVER skip signature verification before deploying
- ❌ NEVER ignore verification failures (investigate immediately)
- ❌ NEVER store private keys unencrypted in production
- ❌ NEVER use the same key for multiple organizations
- ❌ NEVER bypass key rotation schedules
- ❌ NEVER assume signatures are valid without verification
- ❌ NEVER delete old public keys (needed for historical verification)

## References

- **QRG Standard Proposal**: `docs/standards/QRG_PROPOSAL_v0.md`
- **QRG Implementation**: `core/qrg/signing.py`, `core/qrg/model.py`
- **Signing Script**: `scripts/qrg/sign_ops_event.py`
- **Test Suite**: `tests/unit/test_qrg_ops_signing.py`
- **LUKHAS Manifesto**: `docs/MANIFESTO.md`
- **Guardian System**: `docs/architecture/GUARDIAN_SYSTEM.md`

## Support

For questions or issues with QRG signing:

- **Security Issues**: Report to security team immediately (compromised keys, verification failures)
- **Operational Issues**: Consult this guide and troubleshooting section
- **Feature Requests**: Submit to LUKHAS AI Governance Team

---

**Version**: 1.0.0
**Status**: Production
**Last Updated**: 2025-11-12
**Maintainer**: LUKHAS AI Operations Team
