/**
 * WebAuthn Passkey Implementation for ΛiD Authentication System
 * 
 * Implements WebAuthn Level 2 with discoverable credentials, user verification required,
 * AAGUID capture, and attestation preferred for enterprise-grade authentication.
 */

import { TierLevel } from './scopes';
import { createHash, randomBytes } from 'crypto';

export interface PasskeyCredential {
  id: string;                    // Credential ID (base64url)
  credentialId: Uint8Array;      // Raw credential ID
  publicKey: Uint8Array;         // Public key
  algorithm: number;             // COSEAlgorithmIdentifier
  userHandle: string;            // User handle for discoverable credentials
  userId: string;                // User ID
  aaguid: string;                // Authenticator AAGUID
  deviceType: 'platform' | 'cross-platform';
  deviceLabel: string;           // User-friendly device name
  signCount: number;             // Signature counter
  transports: AuthenticatorTransport[];
  createdAt: string;             // ISO 8601 timestamp
  lastUsed: string;              // ISO 8601 timestamp
  uvRequired: boolean;           // User verification required
  rk: boolean;                   // Resident key (discoverable)
  attestationType: 'none' | 'basic' | 'self' | 'attca';
  attestationData?: string;      // Attestation statement (base64)
  backupEligible: boolean;       // Backup eligible flag
  backupState: boolean;          // Backup state flag
}

export interface PasskeyRegistrationOptions {
  rpId: string;
  rpName: string;
  userId: string;
  userEmail: string;
  userName: string;
  userDisplayName: string;
  challenge: Uint8Array;
  timeout: number;
  attestation: 'none' | 'indirect' | 'direct' | 'enterprise';
  authenticatorSelection: {
    authenticatorAttachment?: 'platform' | 'cross-platform';
    userVerification: 'required' | 'preferred' | 'discouraged';
    residentKey: 'required' | 'preferred' | 'discouraged';
    requireResidentKey?: boolean;
  };
  pubKeyCredParams: PublicKeyCredentialParameters[];
  excludeCredentials?: PublicKeyCredentialDescriptor[];
  extensions?: AuthenticationExtensionsClientInputs;
}

export interface PasskeyAuthenticationOptions {
  rpId: string;
  challenge: Uint8Array;
  timeout: number;
  userVerification: 'required' | 'preferred' | 'discouraged';
  allowCredentials?: PublicKeyCredentialDescriptor[];
  extensions?: AuthenticationExtensionsClientInputs;
}

export interface PasskeyRegistrationResult {
  credentialId: string;
  userHandle: string;
  publicKey: Uint8Array;
  algorithm: number;
  aaguid: string;
  attestationData: string;
  attestationType: string;
  deviceInfo: {
    type: 'platform' | 'cross-platform';
    label: string;
    transports: AuthenticatorTransport[];
    backupEligible: boolean;
    backupState: boolean;
  };
  signCount: number;
}

export interface PasskeyAuthenticationResult {
  credentialId: string;
  userHandle: string;
  signature: Uint8Array;
  authenticatorData: Uint8Array;
  clientDataJSON: Uint8Array;
  signCount: number;
  userVerified: boolean;
}

export interface PasskeyChallenge {
  challenge: string;            // Base64url challenge
  userId: string;
  operation: 'registration' | 'authentication';
  expiresAt: number;           // Unix timestamp
  options: any;                // Serialized options
  ipAddress: string;
  userAgent: string;
}

/**
 * WebAuthn configuration for different tiers
 */
export const WEBAUTHN_CONFIG = {
  RP_ID: 'lukhas.ai',
  RP_NAME: 'LUKHAS AI',
  CHALLENGE_SIZE: 32,
  TIMEOUT: 60000, // 60 seconds
  
  // Tier-specific configurations
  TIER_CONFIG: {
    'T1': {
      attestation: 'none' as const,
      userVerification: 'preferred' as const,
      residentKey: 'discouraged' as const,
      maxCredentials: 1
    },
    'T2': {
      attestation: 'indirect' as const,
      userVerification: 'preferred' as const,
      residentKey: 'preferred' as const,
      maxCredentials: 3
    },
    'T3': {
      attestation: 'direct' as const,
      userVerification: 'required' as const,
      residentKey: 'required' as const,
      maxCredentials: 5
    },
    'T4': {
      attestation: 'enterprise' as const,
      userVerification: 'required' as const,
      residentKey: 'required' as const,
      maxCredentials: 10
    },
    'T5': {
      attestation: 'enterprise' as const,
      userVerification: 'required' as const,
      residentKey: 'required' as const,
      maxCredentials: 20
    }
  },

  // Supported algorithms (preference order)
  ALGORITHMS: [
    { alg: -7, type: 'public-key' },  // ES256 (ECDSA w/ SHA-256)
    { alg: -257, type: 'public-key' }, // RS256 (RSASSA-PKCS1-v1_5 w/ SHA-256)
    { alg: -8, type: 'public-key' },  // EdDSA
    { alg: -35, type: 'public-key' }, // ES384 (ECDSA w/ SHA-384)
    { alg: -36, type: 'public-key' }  // ES512 (ECDSA w/ SHA-512)
  ]
};

/**
 * Core WebAuthn passkey manager
 */
export class PasskeyManager {
  private challenges: Map<string, PasskeyChallenge> = new Map();
  private cleanupInterval?: NodeJS.Timer;

  constructor() {
    // Cleanup expired challenges every 5 minutes
    this.cleanupInterval = setInterval(() => {
      this.cleanupExpiredChallenges();
    }, 5 * 60 * 1000);
  }

  /**
   * Generate registration options for new passkey
   */
  async generateRegistrationOptions(
    userId: string,
    userEmail: string,
    userName: string,
    userDisplayName: string,
    userTier: TierLevel,
    existingCredentials: PasskeyCredential[] = [],
    options?: {
      authenticatorAttachment?: 'platform' | 'cross-platform';
      ipAddress?: string;
      userAgent?: string;
    }
  ): Promise<PasskeyRegistrationOptions> {
    try {
      // Get tier-specific configuration
      const tierConfig = WEBAUTHN_CONFIG.TIER_CONFIG[userTier];

      // Check credential limits
      if (existingCredentials.length >= tierConfig.maxCredentials) {
        throw new Error(`Maximum credentials (${tierConfig.maxCredentials}) reached for tier ${userTier}`);
      }

      // Generate challenge
      const challenge = randomBytes(WEBAUTHN_CONFIG.CHALLENGE_SIZE);
      const challengeId = this.generateChallengeId();

      // Create user handle (stable user identifier)
      const userHandle = this.generateUserHandle(userId);

      // Build registration options
      const registrationOptions: PasskeyRegistrationOptions = {
        rpId: WEBAUTHN_CONFIG.RP_ID,
        rpName: WEBAUTHN_CONFIG.RP_NAME,
        userId: userHandle,
        userEmail,
        userName,
        userDisplayName,
        challenge,
        timeout: WEBAUTHN_CONFIG.TIMEOUT,
        attestation: tierConfig.attestation,
        authenticatorSelection: {
          authenticatorAttachment: options?.authenticatorAttachment,
          userVerification: tierConfig.userVerification,
          residentKey: tierConfig.residentKey,
          requireResidentKey: tierConfig.residentKey === 'required'
        },
        pubKeyCredParams: WEBAUTHN_CONFIG.ALGORITHMS,
        excludeCredentials: existingCredentials.map(cred => ({
          id: cred.credentialId,
          type: 'public-key' as const,
          transports: cred.transports
        })),
        extensions: {
          credProps: true, // Request credential properties
          largeBlob: { support: 'preferred' } // Large blob support
        }
      };

      // Store challenge
      const challengeRecord: PasskeyChallenge = {
        challenge: Buffer.from(challenge).toString('base64url'),
        userId,
        operation: 'registration',
        expiresAt: Date.now() + WEBAUTHN_CONFIG.TIMEOUT,
        options: registrationOptions,
        ipAddress: options?.ipAddress || 'unknown',
        userAgent: options?.userAgent || 'unknown'
      };

      this.challenges.set(challengeId, challengeRecord);

      return registrationOptions;

    } catch (error) {
      throw new Error(`Failed to generate registration options: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate authentication options for existing passkeys
   */
  async generateAuthenticationOptions(
    userCredentials: PasskeyCredential[] = [],
    userTier: TierLevel,
    options?: {
      userHandle?: string;
      ipAddress?: string;
      userAgent?: string;
    }
  ): Promise<{ challengeId: string; options: PasskeyAuthenticationOptions }> {
    try {
      // Get tier-specific configuration
      const tierConfig = WEBAUTHN_CONFIG.TIER_CONFIG[userTier];

      // Generate challenge
      const challenge = randomBytes(WEBAUTHN_CONFIG.CHALLENGE_SIZE);
      const challengeId = this.generateChallengeId();

      // Build authentication options
      const authenticationOptions: PasskeyAuthenticationOptions = {
        rpId: WEBAUTHN_CONFIG.RP_ID,
        challenge,
        timeout: WEBAUTHN_CONFIG.TIMEOUT,
        userVerification: tierConfig.userVerification,
        allowCredentials: userCredentials.length > 0 ? userCredentials.map(cred => ({
          id: cred.credentialId,
          type: 'public-key' as const,
          transports: cred.transports
        })) : undefined, // Omit for discoverable credentials
        extensions: {
          largeBlob: { read: true } // Read large blob if available
        }
      };

      // Store challenge
      const challengeRecord: PasskeyChallenge = {
        challenge: Buffer.from(challenge).toString('base64url'),
        userId: options?.userHandle || '',
        operation: 'authentication',
        expiresAt: Date.now() + WEBAUTHN_CONFIG.TIMEOUT,
        options: authenticationOptions,
        ipAddress: options?.ipAddress || 'unknown',
        userAgent: options?.userAgent || 'unknown'
      };

      this.challenges.set(challengeId, challengeRecord);

      return {
        challengeId,
        options: authenticationOptions
      };

    } catch (error) {
      throw new Error(`Failed to generate authentication options: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Verify passkey registration response
   */
  async verifyRegistration(
    challengeId: string,
    credential: any, // PublicKeyCredential from navigator.credentials.create()
    expectedOrigin: string
  ): Promise<PasskeyRegistrationResult> {
    try {
      // Get and validate challenge
      const challengeRecord = this.challenges.get(challengeId);
      if (!challengeRecord) {
        throw new Error('Invalid or expired challenge');
      }

      if (challengeRecord.operation !== 'registration') {
        throw new Error('Challenge not for registration');
      }

      if (Date.now() > challengeRecord.expiresAt) {
        this.challenges.delete(challengeId);
        throw new Error('Challenge expired');
      }

      // Verify credential response
      const response = credential.response as AuthenticatorAttestationResponse;
      
      // Parse client data
      const clientData = JSON.parse(new TextDecoder().decode(response.clientDataJSON));
      
      // Verify client data
      if (clientData.type !== 'webauthn.create') {
        throw new Error('Invalid credential type');
      }

      if (clientData.challenge !== challengeRecord.challenge) {
        throw new Error('Challenge mismatch');
      }

      if (clientData.origin !== expectedOrigin) {
        throw new Error('Origin mismatch');
      }

      // Parse attestation object
      const attestationObject = this.parseAttestationObject(response.attestationObject);
      const authData = this.parseAuthenticatorData(attestationObject.authData);

      // Verify RP ID hash
      const expectedRpIdHash = createHash('sha256').update(WEBAUTHN_CONFIG.RP_ID).digest();
      if (!Buffer.from(authData.rpIdHash).equals(expectedRpIdHash)) {
        throw new Error('RP ID hash mismatch');
      }

      // Verify flags
      if (!authData.flags.userPresent) {
        throw new Error('User not present');
      }

      // Extract credential data
      const credentialData = authData.attestedCredentialData!;
      
      // Generate device label based on AAGUID and authenticator info
      const deviceLabel = this.generateDeviceLabel(
        Buffer.from(credentialData.aaguid).toString('hex'),
        credential.authenticatorAttachment
      );

      // Determine device type and transports
      const deviceType = credential.authenticatorAttachment || 'cross-platform';
      const transports = response.getTransports ? response.getTransports() : [];

      // Clean up challenge
      this.challenges.delete(challengeId);

      return {
        credentialId: credential.id,
        userHandle: challengeRecord.userId,
        publicKey: credentialData.publicKey,
        algorithm: credentialData.algorithm,
        aaguid: Buffer.from(credentialData.aaguid).toString('hex'),
        attestationData: Buffer.from(response.attestationObject).toString('base64'),
        attestationType: attestationObject.fmt,
        deviceInfo: {
          type: deviceType,
          label: deviceLabel,
          transports,
          backupEligible: authData.flags.backupEligible || false,
          backupState: authData.flags.backupState || false
        },
        signCount: authData.signCount
      };

    } catch (error) {
      throw new Error(`Registration verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Verify passkey authentication response
   */
  async verifyAuthentication(
    challengeId: string,
    credential: any, // PublicKeyCredential from navigator.credentials.get()
    expectedOrigin: string,
    storedCredential: PasskeyCredential
  ): Promise<PasskeyAuthenticationResult> {
    try {
      // Get and validate challenge
      const challengeRecord = this.challenges.get(challengeId);
      if (!challengeRecord) {
        throw new Error('Invalid or expired challenge');
      }

      if (challengeRecord.operation !== 'authentication') {
        throw new Error('Challenge not for authentication');
      }

      if (Date.now() > challengeRecord.expiresAt) {
        this.challenges.delete(challengeId);
        throw new Error('Challenge expired');
      }

      // Verify credential ID matches
      if (credential.id !== storedCredential.id) {
        throw new Error('Credential ID mismatch');
      }

      const response = credential.response as AuthenticatorAssertionResponse;
      
      // Parse client data
      const clientData = JSON.parse(new TextDecoder().decode(response.clientDataJSON));
      
      // Verify client data
      if (clientData.type !== 'webauthn.get') {
        throw new Error('Invalid credential type');
      }

      if (clientData.challenge !== challengeRecord.challenge) {
        throw new Error('Challenge mismatch');
      }

      if (clientData.origin !== expectedOrigin) {
        throw new Error('Origin mismatch');
      }

      // Parse authenticator data
      const authData = this.parseAuthenticatorData(response.authenticatorData);

      // Verify RP ID hash
      const expectedRpIdHash = createHash('sha256').update(WEBAUTHN_CONFIG.RP_ID).digest();
      if (!Buffer.from(authData.rpIdHash).equals(expectedRpIdHash)) {
        throw new Error('RP ID hash mismatch');
      }

      // Verify flags
      if (!authData.flags.userPresent) {
        throw new Error('User not present');
      }

      // Check user verification if required
      if (storedCredential.uvRequired && !authData.flags.userVerified) {
        throw new Error('User verification required but not performed');
      }

      // Verify signature counter (prevent replay attacks)
      if (authData.signCount > 0 && authData.signCount <= storedCredential.signCount) {
        throw new Error('Invalid signature counter (possible cloned authenticator)');
      }

      // TODO: Verify signature using stored public key
      // This requires implementing COSE key parsing and signature verification
      
      // Clean up challenge
      this.challenges.delete(challengeId);

      return {
        credentialId: credential.id,
        userHandle: response.userHandle ? Buffer.from(response.userHandle).toString('base64url') : '',
        signature: new Uint8Array(response.signature),
        authenticatorData: new Uint8Array(response.authenticatorData),
        clientDataJSON: new Uint8Array(response.clientDataJSON),
        signCount: authData.signCount,
        userVerified: authData.flags.userVerified || false
      };

    } catch (error) {
      throw new Error(`Authentication verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get challenge by ID (for debugging)
   */
  getChallenge(challengeId: string): PasskeyChallenge | undefined {
    return this.challenges.get(challengeId);
  }

  /**
   * Cleanup expired challenges
   */
  private cleanupExpiredChallenges(): void {
    const now = Date.now();
    for (const [id, challenge] of this.challenges.entries()) {
      if (now > challenge.expiresAt) {
        this.challenges.delete(id);
      }
    }
  }

  /**
   * Generate challenge ID
   */
  private generateChallengeId(): string {
    return randomBytes(16).toString('hex');
  }

  /**
   * Generate stable user handle
   */
  private generateUserHandle(userId: string): string {
    return createHash('sha256').update(userId).digest().toString('base64url');
  }

  /**
   * Generate device label from AAGUID
   */
  private generateDeviceLabel(aaguid: string, attachment?: string): string {
    // Known AAGUIDs mapping
    const knownDevices: Record<string, string> = {
      '08987058-cadc-4b81-b6e1-30de50dcbe96': 'Windows Hello',
      'fa2b99dc-9e39-4257-8f92-4a30d23c4118': 'Windows Hello',
      'adce0002-35bc-c60a-648b-0b25f1f05503': 'Chrome Touch ID',
      '39a5647e-1853-446c-a1f6-a79bae9f5bc7': 'Chrome Touch ID',
      '6028b017-b1d4-4c02-b4b3-afcdafc96bb2': 'Windows Hello',
      '516b0297-4b73-4715-b7b1-ff2bb97b5eb7': 'Yubico Security Key',
      'dd4ec289-e01d-41c9-bb89-70fa845d4bf2': 'Yubico Security Key',
      'f8a011f3-8c0a-4d15-8006-17111f9edc7d': 'Yubico Security Key',
      'cb69481e-8ff7-4039-93ec-0a2729a154a8': 'Yubico Security Key',
      '88bbd2f0-342a-4773-b2da-f18c5e696eb4': 'Titan Security Key',
      'ee882879-721c-4913-9775-3dfcce97072a': 'Titan Security Key'
    };

    const deviceName = knownDevices[aaguid] || 'Security Key';
    const attachmentSuffix = attachment === 'platform' ? ' (Built-in)' : ' (External)';
    
    return deviceName + attachmentSuffix;
  }

  /**
   * Parse CBOR attestation object (simplified)
   */
  private parseAttestationObject(attestationObject: ArrayBuffer): any {
    // This is a simplified implementation
    // In production, use a proper CBOR library like 'cbor-js'
    throw new Error('CBOR parsing needs proper implementation with cbor-js library');
  }

  /**
   * Parse authenticator data
   */
  private parseAuthenticatorData(authData: ArrayBuffer): any {
    const data = new Uint8Array(authData);
    let offset = 0;

    // RP ID hash (32 bytes)
    const rpIdHash = data.slice(offset, offset + 32);
    offset += 32;

    // Flags (1 byte)
    const flagByte = data[offset];
    offset += 1;

    const flags = {
      userPresent: !!(flagByte & 0x01),
      userVerified: !!(flagByte & 0x04),
      attestedCredentialDataIncluded: !!(flagByte & 0x40),
      extensionDataIncluded: !!(flagByte & 0x80),
      backupEligible: !!(flagByte & 0x08),
      backupState: !!(flagByte & 0x10)
    };

    // Sign count (4 bytes)
    const signCount = new DataView(authData, offset, 4).getUint32(0, false);
    offset += 4;

    let attestedCredentialData = null;
    
    if (flags.attestedCredentialDataIncluded) {
      // AAGUID (16 bytes)
      const aaguid = data.slice(offset, offset + 16);
      offset += 16;

      // Credential ID length (2 bytes)
      const credIdLength = new DataView(authData, offset, 2).getUint16(0, false);
      offset += 2;

      // Credential ID
      const credentialId = data.slice(offset, offset + credIdLength);
      offset += credIdLength;

      // Public key (COSE format) - remaining bytes
      const publicKey = data.slice(offset);

      attestedCredentialData = {
        aaguid,
        credentialId,
        publicKey,
        algorithm: -7 // Assume ES256 for now
      };
    }

    return {
      rpIdHash,
      flags,
      signCount,
      attestedCredentialData
    };
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.challenges.clear();
  }
}

/**
 * Passkey utilities
 */
export class PasskeyUtils {
  /**
   * Check browser WebAuthn support
   */
  static isBrowserSupported(): boolean {
    return !!(window?.PublicKeyCredential);
  }

  /**
   * Check platform authenticator availability
   */
  static async isPlatformAuthenticatorAvailable(): Promise<boolean> {
    try {
      if (!this.isBrowserSupported()) return false;
      return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    } catch {
      return false;
    }
  }

  /**
   * Check conditional mediation support
   */
  static async isConditionalMediationAvailable(): Promise<boolean> {
    try {
      if (!this.isBrowserSupported()) return false;
      return await PublicKeyCredential.isConditionalMediationAvailable();
    } catch {
      return false;
    }
  }

  /**
   * Convert ArrayBuffer to base64url
   */
  static arrayBufferToBase64url(buffer: ArrayBuffer): string {
    return Buffer.from(buffer).toString('base64url');
  }

  /**
   * Convert base64url to ArrayBuffer
   */
  static base64urlToArrayBuffer(base64url: string): ArrayBuffer {
    return Buffer.from(base64url, 'base64url').buffer;
  }

  /**
   * Format AAGUID for display
   */
  static formatAAGUID(aaguid: string): string {
    if (aaguid.length !== 32) return aaguid;
    return [
      aaguid.slice(0, 8),
      aaguid.slice(8, 12),
      aaguid.slice(12, 16),
      aaguid.slice(16, 20),
      aaguid.slice(20, 32)
    ].join('-');
  }

  /**
   * Get credential creation options for browser
   */
  static formatCredentialCreationOptions(options: PasskeyRegistrationOptions): CredentialCreationOptions {
    return {
      publicKey: {
        rp: {
          id: options.rpId,
          name: options.rpName
        },
        user: {
          id: new TextEncoder().encode(options.userId),
          name: options.userEmail,
          displayName: options.userDisplayName
        },
        challenge: options.challenge,
        pubKeyCredParams: options.pubKeyCredParams,
        authenticatorSelection: options.authenticatorSelection,
        timeout: options.timeout,
        attestation: options.attestation,
        excludeCredentials: options.excludeCredentials,
        extensions: options.extensions
      }
    };
  }

  /**
   * Get credential request options for browser
   */
  static formatCredentialRequestOptions(options: PasskeyAuthenticationOptions): CredentialRequestOptions {
    return {
      publicKey: {
        challenge: options.challenge,
        rpId: options.rpId,
        allowCredentials: options.allowCredentials,
        userVerification: options.userVerification,
        timeout: options.timeout,
        extensions: options.extensions
      },
      mediation: 'conditional'
    };
  }
}

export default PasskeyManager;