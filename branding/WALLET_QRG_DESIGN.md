# WΛLLET & QRG — One-Pager (Design Tenets)

## Overview
**WALLET** and **QRG** are two complementary authentication methods for LUKHAS ΛiD that prioritize user convenience and security without requiring constant app switching or complex flows.

## WALLET: PKPass/Google Pay Integration

### Design Philosophy
- **Frictionless Identity**: Your ΛiD lives in Apple/Google Wallet alongside payment cards
- **No App Required**: Works with native wallet — no LUKHAS app installation needed
- **Rotating Security**: 6-digit codes refresh every 60 seconds (TOTP-style)
- **Transaction Context**: Each pass shows the specific action being authorized

### Implementation Approach
```typescript
// Simple PKPass generation (apple-pass.ts)
export async function generatePkPass(fields: PassFields): Promise<Buffer> {
  // Creates a black LUKHAS pass with:
  // - ΛiD alias display (PII-free)
  // - Current 6-digit code
  // - Transaction/action context
  // - QR code for fallback scanning
}
```

### User Experience
1. User requests wallet pass from settings
2. Pass downloads directly to Apple/Google Wallet
3. When authentication needed, user opens wallet
4. Shows current 6-digit code or scans QR
5. Code auto-refreshes every minute

## QRG: JWS-Signed QR Approvals

### Design Philosophy
- **Cryptographic Proof**: Every QR contains a signed JWT (ES256)
- **Time-Bounded**: 60-second validity window
- **Offline-Capable**: Works without network on scanning device
- **Action-Specific**: Each QR encodes the exact permitted action

### Implementation Approach
```typescript
// JWS signing for QR codes (qrg/jws.ts)
export function signQrg(claims: QrgClaims, pemPriv: string, kid: string) {
  // ES256 signature over:
  // - User ID (lid_xxx)
  // - Transaction ID
  // - Scope (e.g., "api.keys.create")
  // - Nonce & timestamps
}
```

### User Experience
1. Action triggers QR display on trusted device
2. User scans with phone camera or auth app
3. Signature verified cryptographically
4. Action approved without passwords or PINs
5. Automatic expiry prevents replay attacks

## Security Considerations

### WALLET Security
- **No Sensitive Data**: Pass contains only public alias and rotating codes
- **Device-Bound**: PKPass tied to device secure element
- **Revocable**: Passes can be remotely invalidated
- **Rate Limited**: Code generation throttled server-side

### QRG Security
- **Asymmetric Crypto**: Private key never leaves server
- **Single-Use Nonces**: Prevents replay attacks
- **Short TTL**: 60-second window minimizes exposure
- **Scope Limitation**: Each QR grants only specific action

## Integration Points

### With ΛiD Identity System
- Both methods use canonical `lid_<ULID>` internally
- Display PII-free `ΛiD#REALM/ZONE/TOKEN` aliases
- Integrate with existing WebAuthn as additional factors
- Support step-up authentication flows

### With Consent Ledger
- Every WALLET activation logged
- QRG approvals create audit entries
- Consent state affects available actions
- GDPR-compliant data handling

### With Guardian System
- Risk scoring influences TTL values
- Suspicious patterns trigger additional verification
- Guardian can force re-authentication
- Drift detection on authentication patterns

## Future Enhancements

### WALLET Evolution
- NFC tap-to-authenticate
- Biometric unlock for high-value actions
- Multi-device pass sync
- Customizable pass designs per tier

### QRG Evolution
- Animated QRs with higher data capacity
- Bluetooth proximity validation
- Multi-signature requirements for critical actions
- Hardware security key integration

## Implementation Status

### Complete
- ✅ TypeScript interfaces and types
- ✅ JWS signing/verification logic
- ✅ PKPass generation structure
- ✅ Database schema (Prisma)
- ✅ API route scaffolds

### Remaining
- [ ] Actual PKPass certificates setup
- [ ] Production key management
- [ ] Rate limiting implementation
- [ ] Monitoring and analytics
- [ ] End-to-end testing

## Quick Start for Developers

```bash
# Install dependencies
npm install passkit-generator jsonwebtoken

# Generate keys for QRG
openssl ecparam -name prime256v1 -genkey -out qrg-private.pem
openssl ec -in qrg-private.pem -pubout -out qrg-public.pem

# Set environment variables
QRG_JWS_PRIVATE_KEY=./keys/qrg-private.pem
QRG_JWS_PUBLIC_KEY=./keys/qrg-public.pem
QRG_JWS_KID=qrg-2024-01
WALLET_CODE_TTL_SECONDS=60
QRG_TTL_SECONDS=60

# For PKPass (requires Apple Developer cert)
PKPASS_TEAM_ID=XXXXXXXXXX
PKPASS_PASS_TYPE_ID=pass.com.lukhas.lid
PKPASS_CERT_P12=./certs/pass.p12
PKPASS_CERT_P12_PASSWORD=xxx
```

## Compliance Notes

- **GDPR**: No PII in QR codes or wallet passes
- **CCPA**: User can request pass deletion
- **SOC2**: All authentications logged with correlation IDs
- **FIDO Alliance**: Complements but doesn't replace WebAuthn

## Summary

WALLET and QRG provide convenient, secure authentication methods that work with existing user behaviors (scanning QRs, using digital wallets) while maintaining LUKHAS's security standards. They reduce friction without compromising on cryptographic integrity or audit requirements.
