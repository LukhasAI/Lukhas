---
status: wip
type: documentation
---
# QRG: Short-lived JWS-signed QR Approvals

## Overview
QRG (QR-based approval system) provides secure, time-limited approval tokens for sensitive actions in LUKHAS AI.

## Technical Specifications
- **Algorithm**: ES256 (ECDSA with P-256 and SHA-256)
- **Token Format**: JSON Web Signature (JWS)
- **TTL**: 60 seconds default
- **Replay Protection**: JTI-based with tracking
- **Nonce**: 16-byte random value for each token
- **Step-up**: Requires passkey verification for high-risk actions

## Security Features
1. **Short-lived tokens**: 60-second expiry prevents token theft
2. **Nonce validation**: Prevents replay attacks
3. **JTI tracking**: Each token ID is tracked to prevent reuse
4. **Passkey step-up**: High-risk actions require biometric confirmation
5. **Cryptographic signing**: ES256 ensures token integrity

## Implementation
```typescript
import { generateQRGToken, verifyQRGToken } from '@/packages/qrg/jws';

// Generate approval token
const token = await generateQRGToken(
  { action: 'transfer', userId: 'lid_xxx' },
  privateKey,
  { ttlSeconds: 60 }
);

// Verify token
const payload = await verifyQRGToken(token, publicKey);
```

## Data Flow
1. User initiates sensitive action
2. Server generates QRG token (60s TTL)
3. Token encoded as QR code
4. User scans with authenticated device
5. Device verifies token signature
6. Passkey step-up required for confirmation
7. Action approved with audit trail

## Privacy & Compliance
- No PII in QR codes
- Tokens contain only action IDs and timestamps
- All approvals logged with audit trail
- GDPR-compliant data minimization
