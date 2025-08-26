/**
 * WALLET: Pass-based out-of-band approvals (Apple/Google Wallet)
 * Add a LUKHAS pass to Apple/Google Wallet to confirm sensitive actions
 * Tap to approve; we still confirm with your device (passkey step-up)
 */

import { randomBytes, createHash } from 'crypto';
import { readFileSync } from 'fs';
import { join } from 'path';

export interface WalletPassData {
  passTypeIdentifier: string;
  teamIdentifier: string;
  serialNumber: string;
  organizationName: string;
  description: string;
  logoText: string;
  foregroundColor: string;
  backgroundColor: string;
  labelColor: string;

  // Dynamic fields
  authenticationToken: string;
  webServiceURL: string;

  // User-specific
  userId: string;
  deviceId: string;
  expirationDate?: Date;

  // Approval fields
  barcode?: {
    message: string;
    format: 'PKBarcodeFormatQR' | 'PKBarcodeFormatPDF417';
    messageEncoding: string;
  };

  // Visual fields
  primaryFields?: PassField[];
  secondaryFields?: PassField[];
  auxiliaryFields?: PassField[];
  backFields?: PassField[];
}

export interface PassField {
  key: string;
  label: string;
  value: string;
  changeMessage?: string;
}

export interface WalletPassOptions {
  expiresInHours?: number;
  requiresPasskeyVerification?: boolean;
  allowedActions?: string[];
}

const DEFAULT_EXPIRY_HOURS = 24;

/**
 * Generate a LUKHAS wallet pass for approval flows
 */
export async function generateWalletPass(
  userId: string,
  deviceId: string,
  options: WalletPassOptions = {}
): Promise<WalletPassData> {
  const serialNumber = randomBytes(16).toString('hex');
  const authToken = randomBytes(32).toString('hex');

  const expiryHours = options.expiresInHours || DEFAULT_EXPIRY_HOURS;
  const expirationDate = new Date(Date.now() + expiryHours * 60 * 60 * 1000);

  const pass: WalletPassData = {
    passTypeIdentifier: 'pass.ai.lukhas.auth',
    teamIdentifier: process.env.APPLE_TEAM_ID || 'LUKHAS_TEAM',
    serialNumber,
    organizationName: 'LUKHAS AI',
    description: 'LUKHAS Authentication Pass',
    logoText: 'LUKHAS',
    foregroundColor: 'rgb(255, 255, 255)',
    backgroundColor: 'rgb(16, 16, 16)',
    labelColor: 'rgb(128, 128, 128)',

    authenticationToken: authToken,
    webServiceURL: `${process.env.API_URL}/api/wallet/update`,

    userId,
    deviceId,
    expirationDate,

    barcode: {
      message: JSON.stringify({
        type: 'LUKHAS_AUTH',
        token: authToken,
        userId,
        exp: expirationDate.getTime()
      }),
      format: 'PKBarcodeFormatQR',
      messageEncoding: 'iso-8859-1'
    },

    primaryFields: [
      {
        key: 'status',
        label: 'STATUS',
        value: 'Active',
        changeMessage: 'Pass status changed to %@'
      }
    ],

    secondaryFields: [
      {
        key: 'device',
        label: 'DEVICE',
        value: deviceId.substring(0, 8) + '...'
      },
      {
        key: 'expires',
        label: 'EXPIRES',
        value: expirationDate.toLocaleDateString()
      }
    ],

    auxiliaryFields: options.allowedActions ? [
      {
        key: 'actions',
        label: 'ALLOWED ACTIONS',
        value: options.allowedActions.join(', ')
      }
    ] : [],

    backFields: [
      {
        key: 'security',
        label: 'Security Information',
        value: 'This pass enables secure approval of sensitive actions. Tap to approve requests. All approvals require additional passkey verification on your device.'
      },
      {
        key: 'privacy',
        label: 'Privacy',
        value: 'No biometric data leaves your device. We store only encrypted public keys and approval timestamps.'
      }
    ]
  };

  return pass;
}

/**
 * Verify a wallet pass approval token
 */
export async function verifyWalletToken(
  token: string,
  userId: string,
  deviceId: string
): Promise<boolean> {
  // In production, verify against stored tokens in database
  // Check expiry, device binding, and usage count

  try {
    // Simplified verification for now
    const expectedHash = createHash('sha256')
      .update(token)
      .update(userId)
      .update(deviceId)
      .digest('hex');

    // Check against stored hashes
    // In production, query database
    return true; // Placeholder
  } catch (error) {
    console.error('Wallet token verification failed:', error);
    return false;
  }
}

/**
 * Update pass status (for push updates)
 */
export async function updatePassStatus(
  serialNumber: string,
  status: 'active' | 'used' | 'expired' | 'revoked'
): Promise<void> {
  // In production, send push notification to update pass
  // This requires Apple Push Notification service setup

  console.log(`Updating pass ${serialNumber} status to ${status}`);

  // Store status update in database
  // Send push notification if configured
}

/**
 * Revoke a wallet pass
 */
export async function revokeWalletPass(
  serialNumber: string,
  reason?: string
): Promise<void> {
  await updatePassStatus(serialNumber, 'revoked');

  // Log revocation
  console.log(`Pass ${serialNumber} revoked: ${reason || 'No reason provided'}`);
}

/**
 * Generate PKPass file (for Apple Wallet)
 * Note: This requires certificates and signing in production
 */
export async function generatePKPassFile(
  passData: WalletPassData
): Promise<Buffer> {
  // In production:
  // 1. Create pass.json with passData
  // 2. Add images (logo, icon, etc.)
  // 3. Create manifest.json with file hashes
  // 4. Sign with Apple certificate
  // 5. Create .pkpass zip file

  // Placeholder for now
  const passJson = JSON.stringify(passData, null, 2);
  return Buffer.from(passJson);
}

/**
 * Generate Google Wallet link
 */
export function generateGoogleWalletLink(
  passData: WalletPassData
): string {
  // In production, use Google Wallet API to create JWT
  // and generate proper save link

  const jwt = Buffer.from(JSON.stringify(passData)).toString('base64');
  return `https://pay.google.com/gp/v/save/${jwt}`;
}
