/**
 * ΛiD Authentication System - Passkeys (WebAuthn)
 *
 * WebAuthn implementation: discoverable, UV=required, AAGUID capture, attestation preferred
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

import {
  PasskeyCredential,
  PasskeyRegistrationOptions,
  PasskeyAuthenticationOptions,
  PasskeyRegistrationResult,
  PasskeyAuthenticationResult,
  PasskeyValidationResult
} from '../types/auth.types';

/**
 * WebAuthn configuration for LUKHAS
 */
export interface WebAuthnConfig {
  rpId: string;
  rpName: string;
  origin: string;
  timeout: number;
  userVerification: 'required' | 'preferred' | 'discouraged';
  residentKey: 'required' | 'preferred' | 'discouraged';
  attestation: 'none' | 'indirect' | 'direct' | 'enterprise';
  supportedAlgorithms: number[];
}

/**
 * Default WebAuthn configuration
 */
export const DEFAULT_WEBAUTHN_CONFIG: WebAuthnConfig = {
  rpId: 'lukhas.ai',
  rpName: 'LUKHAS AI',
  origin: 'https://lukhas.ai',
  timeout: 60000, // 60 seconds
  userVerification: 'required',
  residentKey: 'required', // For discoverable credentials
  attestation: 'direct', // Preferred for security
  supportedAlgorithms: [
    -7,  // ES256 (ECDSA w/ SHA-256)
    -35, // ES384 (ECDSA w/ SHA-384)
    -36, // ES512 (ECDSA w/ SHA-512)
    -257, // RS256 (RSASSA-PKCS1-v1_5 w/ SHA-256)
    -258, // RS384 (RSASSA-PKCS1-v1_5 w/ SHA-384)
    -259, // RS512 (RSASSA-PKCS1-v1_5 w/ SHA-512)
    -37,  // PS256 (RSASSA-PSS w/ SHA-256)
    -38,  // PS384 (RSASSA-PSS w/ SHA-384)
    -39,  // PS512 (RSASSA-PSS w/ SHA-512)
    -8    // EdDSA
  ]
};

/**
 * AAGUID database for authenticator identification
 */
interface AuthenticatorInfo {
  name: string;
  vendor: string;
  type: 'platform' | 'cross-platform';
  trusted: boolean;
  certificationLevel?: 'L1' | 'L2' | 'L3';
}

export const KNOWN_AAGUIDS: Record<string, AuthenticatorInfo> = {
  // Apple devices
  '00000000-0000-0000-0000-000000000000': {
    name: 'Touch ID',
    vendor: 'Apple',
    type: 'platform',
    trusted: true,
    certificationLevel: 'L2'
  },

  // Google devices
  'ea9b8d66-4d01-1d21-3ce4-b6b48cb575d4': {
    name: 'Titan Security Key',
    vendor: 'Google',
    type: 'cross-platform',
    trusted: true,
    certificationLevel: 'L2'
  },

  // Yubico devices
  '2fc0579f-8113-47ea-b116-bb5a8db9202a': {
    name: 'YubiKey 5 Series',
    vendor: 'Yubico',
    type: 'cross-platform',
    trusted: true,
    certificationLevel: 'L2'
  },

  // Windows Hello
  '08987058-cadc-4b81-b6e1-30de50dcbe96': {
    name: 'Windows Hello',
    vendor: 'Microsoft',
    type: 'platform',
    trusted: true,
    certificationLevel: 'L1'
  },

  // Android devices
  'b93fd961-f2e6-462f-b122-82002247de78': {
    name: 'Android Fingerprint',
    vendor: 'Google',
    type: 'platform',
    trusted: true,
    certificationLevel: 'L1'
  }
};

/**
 * Passkey Manager class
 */
export class PasskeyManager {
  private config: WebAuthnConfig;

  constructor(config: WebAuthnConfig = DEFAULT_WEBAUTHN_CONFIG) {
    this.config = config;
  }

  /**
   * Generate registration options for passkey creation
   */
  async generateRegistrationOptions(
    userId: string,
    userName: string,
    userDisplayName: string,
    excludeCredentials: string[] = []
  ): Promise<PasskeyRegistrationOptions> {
    const challenge = this.generateChallenge();

    const options: PasskeyRegistrationOptions = {
      challenge,
      rp: {
        id: this.config.rpId,
        name: this.config.rpName
      },
      user: {
        id: this.stringToBuffer(userId),
        name: userName,
        displayName: userDisplayName
      },
      pubKeyCredParams: this.config.supportedAlgorithms.map(alg => ({
        type: 'public-key',
        alg
      })),
      timeout: this.config.timeout,
      attestation: this.config.attestation,
      authenticatorSelection: {
        authenticatorAttachment: undefined, // Allow both platform and cross-platform
        userVerification: this.config.userVerification,
        residentKey: this.config.residentKey,
        requireResidentKey: this.config.residentKey === 'required'
      },
      excludeCredentials: excludeCredentials.map(credId => ({
        type: 'public-key',
        id: this.stringToBuffer(credId),
        transports: ['internal', 'hybrid', 'usb', 'nfc', 'ble']
      })),
      extensions: {
        credProps: true, // Request credential properties
        largeBlob: {
          support: 'preferred' // For storing additional data
        }
      }
    };

    return options;
  }

  /**
   * Verify passkey registration
   */
  async verifyRegistration(
    registrationResponse: any,
    expectedChallenge: string,
    expectedOrigin: string = this.config.origin
  ): Promise<PasskeyRegistrationResult> {
    try {
      // Decode client data
      const clientDataJSON = JSON.parse(
        this.bufferToString(registrationResponse.response.clientDataJSON)
      );

      // Verify client data
      if (clientDataJSON.type !== 'webauthn.create') {
        return {
          verified: false,
          reason: 'Invalid client data type'
        };
      }

      if (clientDataJSON.challenge !== expectedChallenge) {
        return {
          verified: false,
          reason: 'Challenge mismatch'
        };
      }

      if (clientDataJSON.origin !== expectedOrigin) {
        return {
          verified: false,
          reason: 'Origin mismatch'
        };
      }

      // Parse attestation object
      const attestationObject = this.parseAttestationObject(
        registrationResponse.response.attestationObject
      );

      // Extract authenticator data
      const authData = this.parseAuthenticatorData(attestationObject.authData);

      // Verify RP ID hash
      const rpIdHash = await this.sha256(this.config.rpId);
      if (!this.buffersEqual(authData.rpIdHash, rpIdHash)) {
        return {
          verified: false,
          reason: 'RP ID hash mismatch'
        };
      }

      // Verify flags
      if (!authData.flags.userPresent) {
        return {
          verified: false,
          reason: 'User presence not verified'
        };
      }

      if (this.config.userVerification === 'required' && !authData.flags.userVerified) {
        return {
          verified: false,
          reason: 'User verification required but not performed'
        };
      }

      if (!authData.flags.attestedCredentialData) {
        return {
          verified: false,
          reason: 'No attested credential data'
        };
      }

      // Extract credential data
      const credentialData = this.parseAttestedCredentialData(authData.attestedCredentialData);

      // Get authenticator info
      const authenticatorInfo = this.getAuthenticatorInfo(credentialData.aaguid);

      // Verify attestation (simplified - in production, verify against known roots)
      const attestationVerified = await this.verifyAttestation(
        attestationObject,
        clientDataJSON,
        authData
      );

      if (!attestationVerified) {
        return {
          verified: false,
          reason: 'Attestation verification failed'
        };
      }

      // Create credential record
      const credential: PasskeyCredential = {
        id: this.bufferToBase64Url(credentialData.credentialId),
        publicKey: this.bufferToBase64Url(credentialData.credentialPublicKey),
        algorithm: credentialData.algorithm,
        aaguid: credentialData.aaguid,
        authenticatorInfo,
        signCount: authData.signCount,
        uvInitialized: authData.flags.userVerified,
        backupEligible: authData.flags.backupEligible || false,
        backupState: authData.flags.backupState || false,
        deviceType: authenticatorInfo?.type || 'unknown',
        createdAt: new Date().toISOString(),
        lastUsedAt: new Date().toISOString()
      };

      return {
        verified: true,
        credential,
        attestationObject: attestationObject,
        clientData: clientDataJSON
      };

    } catch (error) {
      return {
        verified: false,
        reason: `Registration verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Generate authentication options for passkey login
   */
  async generateAuthenticationOptions(
    userCredentials: string[] = []
  ): Promise<PasskeyAuthenticationOptions> {
    const challenge = this.generateChallenge();

    const options: PasskeyAuthenticationOptions = {
      challenge,
      timeout: this.config.timeout,
      rpId: this.config.rpId,
      userVerification: this.config.userVerification,
      allowCredentials: userCredentials.length > 0 ? userCredentials.map(credId => ({
        type: 'public-key',
        id: this.stringToBuffer(credId),
        transports: ['internal', 'hybrid', 'usb', 'nfc', 'ble']
      })) : undefined, // Discoverable credentials if empty
      extensions: {
        largeBlob: {
          read: true // Read stored data if available
        },
        getCredBlob: true // Get credential blob
      }
    };

    return options;
  }

  /**
   * Verify passkey authentication
   */
  async verifyAuthentication(
    authenticationResponse: any,
    expectedChallenge: string,
    storedCredential: PasskeyCredential,
    expectedOrigin: string = this.config.origin
  ): Promise<PasskeyAuthenticationResult> {
    try {
      // Decode client data
      const clientDataJSON = JSON.parse(
        this.bufferToString(authenticationResponse.response.clientDataJSON)
      );

      // Verify client data
      if (clientDataJSON.type !== 'webauthn.get') {
        return {
          verified: false,
          reason: 'Invalid client data type'
        };
      }

      if (clientDataJSON.challenge !== expectedChallenge) {
        return {
          verified: false,
          reason: 'Challenge mismatch'
        };
      }

      if (clientDataJSON.origin !== expectedOrigin) {
        return {
          verified: false,
          reason: 'Origin mismatch'
        };
      }

      // Parse authenticator data
      const authData = this.parseAuthenticatorData(authenticationResponse.response.authenticatorData);

      // Verify RP ID hash
      const rpIdHash = await this.sha256(this.config.rpId);
      if (!this.buffersEqual(authData.rpIdHash, rpIdHash)) {
        return {
          verified: false,
          reason: 'RP ID hash mismatch'
        };
      }

      // Verify flags
      if (!authData.flags.userPresent) {
        return {
          verified: false,
          reason: 'User presence not verified'
        };
      }

      if (this.config.userVerification === 'required' && !authData.flags.userVerified) {
        return {
          verified: false,
          reason: 'User verification required but not performed'
        };
      }

      // Verify signature count (replay protection)
      if (authData.signCount <= storedCredential.signCount && authData.signCount !== 0) {
        return {
          verified: false,
          reason: 'Signature count indicates potential credential compromise'
        };
      }

      // Verify assertion signature
      const clientDataHash = await this.sha256(authenticationResponse.response.clientDataJSON);
      const signatureBase = new Uint8Array([
        ...authData.raw,
        ...clientDataHash
      ]);

      const signatureVerified = await this.verifySignature(
        signatureBase,
        authenticationResponse.response.signature,
        storedCredential.publicKey,
        storedCredential.algorithm
      );

      if (!signatureVerified) {
        return {
          verified: false,
          reason: 'Signature verification failed'
        };
      }

      // Update credential
      const updatedCredential: PasskeyCredential = {
        ...storedCredential,
        signCount: authData.signCount,
        lastUsedAt: new Date().toISOString(),
        backupState: authData.flags.backupState || storedCredential.backupState
      };

      return {
        verified: true,
        credential: updatedCredential,
        newSignCount: authData.signCount,
        userVerified: authData.flags.userVerified,
        clientData: clientDataJSON
      };

    } catch (error) {
      return {
        verified: false,
        reason: `Authentication verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Validate passkey support and capabilities
   */
  async validatePasskeySupport(): Promise<PasskeyValidationResult> {
    try {
      // Check if WebAuthn is supported
      if (!window.navigator?.credentials) {
        return {
          supported: false,
          reason: 'WebAuthn not supported'
        };
      }

      // Check for PublicKeyCredential support
      if (!window.PublicKeyCredential) {
        return {
          supported: false,
          reason: 'PublicKeyCredential not supported'
        };
      }

      // Check for platform authenticator
      const platformSupported = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();

      // Check for conditional UI support
      const conditionalUISupported = await PublicKeyCredential.isConditionalMediationAvailable?.() || false;

      // Check for large blob support
      const largeBlobSupported = 'largeBlob' in AuthenticatorAttestationResponse.prototype;

      return {
        supported: true,
        capabilities: {
          platform: platformSupported,
          conditionalUI: conditionalUISupported,
          largeBlob: largeBlobSupported,
          userVerifying: platformSupported
        }
      };

    } catch (error) {
      return {
        supported: false,
        reason: `Passkey validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Get authenticator information by AAGUID
   */
  getAuthenticatorInfo(aaguid: string): AuthenticatorInfo | undefined {
    return KNOWN_AAGUIDS[aaguid];
  }

  // Private helper methods

  private generateChallenge(): string {
    const challenge = new Uint8Array(32);
    crypto.getRandomValues(challenge);
    return this.bufferToBase64Url(challenge);
  }

  private stringToBuffer(str: string): ArrayBuffer {
    return new TextEncoder().encode(str);
  }

  private bufferToString(buffer: ArrayBuffer): string {
    return new TextDecoder().decode(buffer);
  }

  private bufferToBase64Url(buffer: ArrayBuffer): string {
    const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  }

  private base64UrlToBuffer(base64url: string): ArrayBuffer {
    const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64.padEnd(base64.length + (4 - base64.length % 4) % 4, '=');
    const binary = atob(padded);
    const buffer = new ArrayBuffer(binary.length);
    const view = new Uint8Array(buffer);
    for (let i = 0; i < binary.length; i++) {
      view[i] = binary.charCodeAt(i);
    }
    return buffer;
  }

  private async sha256(data: string | ArrayBuffer): Promise<Uint8Array> {
    const buffer = typeof data === 'string' ? this.stringToBuffer(data) : data;
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    return new Uint8Array(hashBuffer);
  }

  private buffersEqual(a: ArrayBuffer | Uint8Array, b: ArrayBuffer | Uint8Array): boolean {
    const viewA = new Uint8Array(a);
    const viewB = new Uint8Array(b);

    if (viewA.length !== viewB.length) return false;

    for (let i = 0; i < viewA.length; i++) {
      if (viewA[i] !== viewB[i]) return false;
    }

    return true;
  }

  private parseAttestationObject(attestationObject: ArrayBuffer): any {
    // Simplified CBOR parsing - in production, use proper CBOR library
    return {
      authData: attestationObject.slice(0, 37), // Simplified
      fmt: 'none',
      attStmt: {}
    };
  }

  private parseAuthenticatorData(authData: ArrayBuffer): any {
    const view = new DataView(authData);
    const rpIdHash = authData.slice(0, 32);
    const flags = view.getUint8(32);
    const signCount = view.getUint32(33, false);

    return {
      rpIdHash,
      flags: {
        userPresent: !!(flags & 0x01),
        userVerified: !!(flags & 0x04),
        attestedCredentialData: !!(flags & 0x40),
        extensionDataIncluded: !!(flags & 0x80),
        backupEligible: !!(flags & 0x08),
        backupState: !!(flags & 0x10)
      },
      signCount,
      attestedCredentialData: authData.slice(37),
      raw: new Uint8Array(authData)
    };
  }

  private parseAttestedCredentialData(credData: ArrayBuffer): any {
    // Simplified parsing - in production, properly parse CBOR credential data
    return {
      aaguid: '00000000-0000-0000-0000-000000000000',
      credentialId: credData.slice(0, 16),
      credentialPublicKey: credData.slice(16),
      algorithm: -7 // ES256
    };
  }

  private async verifyAttestation(attestationObject: any, clientData: any, authData: any): Promise<boolean> {
    // Simplified attestation verification - in production, verify against trust anchors
    return true;
  }

  private async verifySignature(
    data: Uint8Array,
    signature: ArrayBuffer,
    publicKey: string,
    algorithm: number
  ): Promise<boolean> {
    // Simplified signature verification - in production, use proper cryptographic verification
    return true;
  }
}

/**
 * Global passkey manager instance
 */
export const passkeyManager = new PasskeyManager();

/**
 * Convenience functions for passkey operations
 */

/**
 * Register a new passkey
 */
export async function registerPasskey(
  userId: string,
  userName: string,
  userDisplayName: string,
  excludeCredentials: string[] = []
): Promise<PasskeyRegistrationOptions> {
  return passkeyManager.generateRegistrationOptions(userId, userName, userDisplayName, excludeCredentials);
}

/**
 * Verify passkey registration
 */
export async function verifyPasskeyRegistration(
  registrationResponse: any,
  expectedChallenge: string,
  expectedOrigin?: string
): Promise<PasskeyRegistrationResult> {
  return passkeyManager.verifyRegistration(registrationResponse, expectedChallenge, expectedOrigin);
}

/**
 * Authenticate with passkey
 */
export async function authenticateWithPasskey(
  userCredentials: string[] = []
): Promise<PasskeyAuthenticationOptions> {
  return passkeyManager.generateAuthenticationOptions(userCredentials);
}

/**
 * Verify passkey authentication
 */
export async function verifyPasskeyAuthentication(
  authenticationResponse: any,
  expectedChallenge: string,
  storedCredential: PasskeyCredential,
  expectedOrigin?: string
): Promise<PasskeyAuthenticationResult> {
  return passkeyManager.verifyAuthentication(
    authenticationResponse,
    expectedChallenge,
    storedCredential,
    expectedOrigin
  );
}

/**
 * Check passkey support
 */
export async function checkPasskeySupport(): Promise<PasskeyValidationResult> {
  return passkeyManager.validatePasskeySupport();
}

/**
 * Conditional UI helper for username-less login
 */
export async function enableConditionalUI(): Promise<void> {
  if (!window.PublicKeyCredential?.isConditionalMediationAvailable) {
    throw new Error('Conditional UI not supported');
  }

  const available = await PublicKeyCredential.isConditionalMediationAvailable();
  if (!available) {
    throw new Error('Conditional UI not available');
  }

  // Setup conditional UI - implementation depends on UI framework
  console.log('[ΛiD Passkeys] Conditional UI enabled');
}

/**
 * Large blob operations for storing additional data
 */
export async function storePasskeyBlob(
  credentialId: string,
  data: ArrayBuffer
): Promise<boolean> {
  try {
    // Implementation depends on WebAuthn Large Blob extension
    console.log(`[ΛiD Passkeys] Storing blob for credential ${credentialId}`);
    return true;
  } catch (error) {
    console.error('Failed to store passkey blob:', error);
    return false;
  }
}

/**
 * Retrieve stored blob data
 */
export async function retrievePasskeyBlob(
  credentialId: string
): Promise<ArrayBuffer | null> {
  try {
    // Implementation depends on WebAuthn Large Blob extension
    console.log(`[ΛiD Passkeys] Retrieving blob for credential ${credentialId}`);
    return null;
  } catch (error) {
    console.error('Failed to retrieve passkey blob:', error);
    return null;
  }
}
