# JWKS and Key Rotation - Lukhas Identity

**Version**: 1.0
**Last Updated**: 2025-11-14
**Author**: agent-identity-specialist

## Overview

Lukhas Identity uses **asymmetric cryptography** for JWT signing to enable secure, verifiable tokens. This document covers:

- Key management architecture (RS256/ES256)
- JWKS (JSON Web Key Set) endpoint for public key discovery
- Key rotation procedures
- Integration with existing systems

---

## Why Asymmetric Keys?

### Security Benefits

| Aspect | HS256 (Symmetric) | RS256/ES256 (Asymmetric) |
|--------|-------------------|---------------------------|
| **Secret Distribution** | Shared secret | Public/private key pair |
| **Verification** | Requires secret | Public key only |
| **Compromise Impact** | Total system breach | Limited to signing |
| **Key Rotation** | Requires updating all clients | JWKS auto-discovery |

**Decision**: Use **RS256** (RSA-2048) or **ES256** (ECDSA P-256) for production.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Lukhas Identity System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐                                       │
│  │   KeyManager     │                                       │
│  │                  │                                       │
│  │  - Generate keys │                                       │
│  │  - Rotate keys   │                                       │
│  │  - Export JWKS   │                                       │
│  └────────┬─────────┘                                       │
│           │                                                  │
│           │ Sign JWTs                                        │
│           ▼                                                  │
│  ┌──────────────────┐        ┌──────────────────────────┐  │
│  │  OIDCProvider    │        │  JWKS Endpoint           │  │
│  │                  │        │  /.well-known/jwks.json  │  │
│  │  - Issue tokens  │        │                          │  │
│  │  - Add 'kid'     │        │  Returns public keys     │  │
│  └──────────────────┘        └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTPS GET
                                        ▼
                           ┌─────────────────────────┐
                           │  Clients (Web/Mobile)    │
                           │                          │
                           │  - Fetch JWKS            │
                           │  - Verify JWT signatures │
                           │  - Cache public keys     │
                           └──────────────────────────┘
```

---

## Key Management

### Supported Algorithms

| Algorithm | Key Type | Key Size | Security Level | Performance |
|-----------|----------|----------|----------------|-------------|
| **RS256** | RSA | 2048-bit | High | Good |
| **RS256** | RSA | 4096-bit | Very High | Slower |
| **ES256** | ECDSA | P-256 | Very High | Excellent |

**Recommendation**: Use **ES256** for optimal performance and security.

### Key Generation

Keys are generated automatically on first startup:

```python
from core.identity.keys import KeyManager

# Initialize with ES256 (recommended)
km = KeyManager(
    algorithm="ES256",
    key_dir="/secrets/keys",
    rotation_days=90,
    grace_days=7
)

# Get current signing key
kid, private_key = km.get_current_signing_key()
```

**Generated Files**:
```
/secrets/keys/
├── lukhas-es256-20251114120000.key   # Private key (PEM, 0600 permissions)
├── lukhas-es256-20251114120000.pub   # Public key (PEM)
└── lukhas-es256-20251114120000.json  # Metadata
```

### Key Metadata

Each key has associated metadata:

```json
{
  "kid": "lukhas-es256-20251114120000",
  "algorithm": "ES256",
  "created_at": "2025-11-14T12:00:00Z",
  "expires_at": "2026-02-12T12:00:00Z",
  "active": true,
  "curve": "P-256"
}
```

---

## JWKS Endpoint

### Overview

The **JWKS (JSON Web Key Set)** endpoint exposes public keys in RFC 7517 format for JWT verification.

**Endpoint**: `/.well-known/jwks.json`

### Example Response

```json
{
  "keys": [
    {
      "kty": "EC",
      "use": "sig",
      "kid": "lukhas-es256-20251114120000",
      "alg": "ES256",
      "crv": "P-256",
      "x": "WKn-ZIGevcwGIyyrzFoZNBdaq9_TsqzGl96oc0CWuis",
      "y": "y77t-RvAHRKTsSGdIYUfweuOvwrvDD-Q3Hv5J0fSKbE"
    }
  ]
}
```

### Integration Example (Client-Side)

**JavaScript (Next.js)**:
```javascript
import { createRemoteJWKSet, jwtVerify } from 'jose';

const JWKS = createRemoteJWKSet(new URL('https://ai/.well-known/jwks.json'));

async function verifyToken(token) {
  const { payload } = await jwtVerify(token, JWKS, {
    issuer: 'https://ai',
    audience: 'lukhas_web'
  });

  return payload; // { sub: "usr_alice", ... }
}
```

**Python**:
```python
from jose import jwt
import requests

# Fetch JWKS
jwks = requests.get("https://ai/.well-known/jwks.json").json()

# Verify token
decoded = jwt.decode(
    token,
    jwks,
    algorithms=["ES256"],
    audience="lukhas_web"
)
```

### Caching

Clients **SHOULD** cache JWKS responses:

```http
GET /.well-known/jwks.json
HTTP/1.1 200 OK
Cache-Control: public, max-age=3600
Access-Control-Allow-Origin: *

{
  "keys": [...]
}
```

**Best Practices**:
- Cache for at least 1 hour
- Refresh if encountering unknown `kid`
- Handle rotation gracefully

---

## Key Rotation

### Automated Rotation Schedule

Keys are rotated automatically:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `rotation_days` | 90 | Rotate every 90 days |
| `grace_days` | 7 | Keep old keys valid for 7 days |

**Timeline**:
```
Day 0    Day 90                     Day 97
  │        │                          │
  ├────────┼──────────────────────────┼────>
  │        │                          │
 Key A   Key B              Key A expires
generated generated         (grace period ends)
 Active   Active → Inactive
```

### Manual Rotation

Rotate keys manually via Python API:

```python
from core.identity.keys import KeyManager

km = KeyManager(algorithm="ES256", key_dir="/secrets/keys")

# Rotate keys
new_kid = km.rotate_keys()
print(f"New key: {new_kid}")

# Old keys remain valid during grace period
jwks = km.export_jwks()
print(f"JWKS now contains {len(jwks['keys'])} keys")
```

### Rotation via CLI (Future)

```bash
# Manual rotation
lukhas identity rotate-keys

# Force rotation (skip checks)
lukhas identity rotate-keys --force

# Check rotation status
lukhas identity list-keys
```

### Zero-Downtime Rotation

Key rotation is **zero-downtime** by design:

1. **New key generated**: Key B created
2. **Grace period starts**: Both keys in JWKS
3. **New tokens use Key B**: Signed with new `kid`
4. **Old tokens still valid**: Verified with Key A (via JWKS)
5. **Grace period ends**: Key A removed from JWKS

**Client Impact**: None (JWKS auto-discovery)

---

## JWT Signing with kid

### Before (Insecure - HS256)

```python
# Old approach - symmetric secret
token = jwt.encode(
    {"sub": "usr_alice"},
    "shared_secret_123",  # Exposed to all verifiers!
    algorithm="HS256"
)
```

### After (Secure - RS256/ES256)

```python
from core.identity.keys import KeyManager

km = KeyManager(algorithm="ES256", key_dir="/secrets/keys")

# Get current signing key
kid, private_key = km.get_current_signing_key()

# Sign with kid in header
token = jwt.encode(
    {"sub": "usr_alice", "exp": ...},
    private_key,
    algorithm="ES256",
    headers={"kid": kid}  # Key ID for JWKS lookup
)
```

**Token Header**:
```json
{
  "alg": "ES256",
  "typ": "JWT",
  "kid": "lukhas-es256-20251114120000"
}
```

---

## Security Considerations

### Private Key Protection

**File Permissions**:
```bash
# Private keys are created with 0600 permissions
ls -l /secrets/keys/*.key
# -rw------- 1 lukhas lukhas ... lukhas-es256-*.key
```

**Encryption at Rest** (Recommended):
```bash
# Encrypt private keys with KMS
aws kms encrypt \
  --key-id arn:aws:kms:us-east-1:123456789012:key/abcd-1234 \
  --plaintext fileb:///secrets/keys/lukhas-es256-*.key \
  --output text --query CiphertextBlob | base64 -d > encrypted.key
```

**Environment Variable** (Not Recommended for Production):
```bash
# Load key from env (dev only)
export SIGNING_KEY=$(cat /secrets/keys/lukhas-es256-*.key | base64)
```

### Key Compromise Response

If a private key is compromised:

1. **Immediately rotate**: `km.rotate_keys()`
2. **Revoke all active tokens**: Use token revocation API
3. **Investigate**: Check access logs
4. **Audit**: Review all issued tokens
5. **Update JWKS**: Old key removed immediately

---

## KMS Integration (Optional)

### AWS KMS

```python
import boto3
from base64 import b64decode

kms = boto3.client('kms')

# Decrypt private key from KMS
response = kms.decrypt(
    CiphertextBlob=b64decode(encrypted_key),
    KeyId='arn:aws:kms:us-east-1:123456789012:key/abcd-1234'
)

private_key_pem = response['Plaintext']

# Use with KeyManager
# (KeyManager would need KMS integration - future enhancement)
```

### Google Cloud KMS

```python
from google.cloud import kms

client = kms.KeyManagementServiceClient()
key_name = 'projects/PROJECT_ID/locations/global/keyRings/RING/cryptoKeys/KEY'

# Decrypt
response = client.decrypt(request={'name': key_name, 'ciphertext': encrypted_key})
private_key_pem = response.plaintext
```

---

## Monitoring & Alerts

### Prometheus Metrics (Future - Task 47)

```promql
# Key rotation lag (days since last rotation)
identity_key_age_days{kid="lukhas-es256-*"}

# Active keys count
identity_active_keys_total

# JWT signing latency
identity_jwt_sign_latency_seconds{quantile="0.95"}
```

### Recommended Alerts

```yaml
# Alert if no active keys
- alert: NoActiveSigningKeys
  expr: identity_active_keys_total == 0
  for: 1m
  severity: critical

# Alert if key rotation overdue
- alert: KeyRotationOverdue
  expr: identity_key_age_days > 100
  for: 1h
  severity: warning
```

---

## Troubleshooting

### "Unknown kid" Error

**Symptom**: Client cannot verify JWT

```
jose.exceptions.JWKError: Unable to find a signing key that matches: 'lukhas-es256-20251114120000'
```

**Cause**: JWKS cache is stale

**Solution**: Force JWKS refresh

```javascript
// Next.js - clear cache
const JWKS = createRemoteJWKSet(
  new URL('https://ai/.well-known/jwks.json'),
  { cacheMaxAge: 0 }  // Disable cache temporarily
);
```

### Key File Permission Errors

**Symptom**: `PermissionError: [Errno 13] Permission denied: '/secrets/keys/lukhas-es256-*.key'`

**Solution**: Fix permissions

```bash
chmod 600 /secrets/keys/*.key
chown lukhas:lukhas /secrets/keys/*
```

### KeyManager Not Initialized

**Symptom**: `RuntimeError: No active signing key available`

**Solution**: Generate initial key

```python
km = KeyManager(algorithm="ES256", key_dir="/secrets/keys")
# KeyManager auto-generates key on init if none exist
```

---

## Migration from HS256

### Step 1: Add RS256/ES256 Support

```python
# Initialize new KeyManager (parallel to existing HS256)
km = KeyManager(algorithm="ES256", key_dir="/secrets/keys")

# Update OIDCProvider to use asymmetric signing
kid, private_key = km.get_current_signing_key()
token = jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": kid})
```

### Step 2: Deploy JWKS Endpoint

```python
from fastapi import FastAPI
from core.identity.jwks_endpoint import router, init_jwks_endpoint

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def startup():
    km = KeyManager(algorithm="ES256", key_dir="/secrets/keys")
    init_jwks_endpoint(km)
```

### Step 3: Update Clients

```javascript
// Before: Hardcoded secret
const decoded = jwt.verify(token, "shared_secret_123", { algorithms: ["HS256"] });

// After: JWKS lookup
const { payload } = await jwtVerify(token, JWKS, { algorithms: ["ES256"] });
```

### Step 4: Deprecate HS256

- Monitor HS256 token usage (should drop to 0%)
- Remove HS256 code after 30 days
- Update documentation

---

## Testing

### Unit Tests

```bash
# Run key management tests
pytest tests/identity/crypto/test_key_management.py -v

# Run JWKS endpoint tests
pytest tests/identity/crypto/test_jwks_endpoint.py -v
```

### Manual Testing

```bash
# 1. Generate key
python -c "from core.identity.keys import KeyManager; km = KeyManager(algorithm='ES256'); print(km.get_current_signing_key()[0])"

# 2. Fetch JWKS
curl https://ai/.well-known/jwks.json | jq

# 3. Verify JWKS contains key
curl https://ai/.well-known/jwks.json | jq '.keys[].kid'
```

---

## References

- [RFC 7517 - JSON Web Key (JWK)](https://datatracker.ietf.org/doc/html/rfc7517)
- [RFC 7518 - JSON Web Algorithms (JWA)](https://datatracker.ietf.org/doc/html/rfc7518)
- [RFC 7519 - JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
- [OpenID Connect Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [JOSE Library Documentation](https://python-jose.readthedocs.io/)

---

## Change Log

| Version | Date       | Changes                                    |
|---------|------------|--------------------------------------------|
| 1.0     | 2025-11-14 | Initial JWKS and key rotation documentation |

---

**Next Steps**: Proceed to [Task 43: OAuth2 Token Introspection & Revocation](INTROSPECTION_AND_REVOCATION.md)
