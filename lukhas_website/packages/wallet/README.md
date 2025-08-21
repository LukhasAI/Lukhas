# WALLET: Pass-based Out-of-Band Approvals

## Overview
WALLET provides secure approval flows using Apple Wallet and Google Wallet passes for LUKHAS AI sensitive actions.

## Technical Specifications
- **Pass Format**: PKPass (Apple) / JWT (Google)
- **Authentication**: Per-device authentication tokens
- **Expiry**: 24-hour default TTL
- **Verification**: Passkey step-up required
- **Updates**: Push notifications for status changes

## Security Features
1. **Device binding**: Each pass is tied to a specific device
2. **Time-limited**: Passes expire after 24 hours
3. **Out-of-band**: Approval happens outside main session
4. **Passkey verification**: Biometric confirmation required
5. **Revocation**: Passes can be instantly revoked

## Implementation
```typescript
import { generateWalletPass, verifyWalletToken } from '@/packages/wallet/pkpass';

// Generate wallet pass
const pass = await generateWalletPass(
  userId,
  deviceId,
  { 
    expiresInHours: 24,
    requiresPasskeyVerification: true,
    allowedActions: ['transfer', 'delete_account']
  }
);

// Verify approval
const isValid = await verifyWalletToken(token, userId, deviceId);
```

## User Flow
1. User adds LUKHAS pass to Apple/Google Wallet
2. Pass contains QR code with auth token
3. For sensitive actions, user taps pass
4. App scans QR code from pass
5. Passkey verification required
6. Action approved with full audit trail

## Privacy & Data Handling
- **No biometrics stored**: Only public keys on server
- **Minimal data**: Pass contains only necessary identifiers
- **Encrypted tokens**: All auth tokens are encrypted
- **User control**: Users can delete passes anytime
- **GDPR compliant**: Full data portability and deletion

## Pass Contents
- **Primary Field**: Status (Active/Used/Expired)
- **Secondary Fields**: Device ID, Expiration date
- **Auxiliary Fields**: Allowed actions (if restricted)
- **Back Fields**: Security info, Privacy policy

## Certificate Requirements (Production)
- Apple Developer Program membership
- Pass Type ID certificate
- Apple WWDR certificate
- Google Wallet API access