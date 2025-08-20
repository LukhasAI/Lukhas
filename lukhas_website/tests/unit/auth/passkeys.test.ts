/**
 * LUKHAS AI ΛiD Authentication System - Passkeys WebAuthn Unit Tests
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Tests for WebAuthn passkey registration, authentication, and management
 */

import { PasskeyManager, PasskeyUtils, WEBAUTHN_CONFIG } from '@/packages/auth/passkeys';
import crypto from 'crypto';

// Mock WebAuthn globals
global.navigator = {
  credentials: {
    create: jest.fn(),
    get: jest.fn(),
  },
} as any;

// Mock crypto.randomUUID
global.crypto = {
  ...global.crypto,
  randomUUID: jest.fn(() => 'test-uuid-' + Math.random().toString(36).substr(2, 9)),
} as any;

describe('PasskeyManager', () => {
  let passkeyManager: PasskeyManager;

  beforeEach(() => {
    passkeyManager = new PasskeyManager();
    jest.clearAllMocks();
  });

  describe('Registration Challenge Generation', () => {
    it('should generate valid registration challenge', async () => {
      const userInfo = {
        id: 'test-user-id',
        email: 'test@lukhas.ai',
        displayName: 'Test User',
      };

      const options = await passkeyManager.generateRegistrationOptions(
        userInfo,
        'lukhas.ai',
        'https://lukhas.ai'
      );

      expect(options.challenge).toBeDefined();
      expect(options.challenge).toHaveLength(128); // 64 bytes = 128 hex chars
      expect(options.rp.id).toBe('lukhas.ai');
      expect(options.rp.name).toBe('LUKHAS AI');
      expect(options.user.id).toBe(userInfo.id);
      expect(options.user.name).toBe(userInfo.email);
      expect(options.user.displayName).toBe(userInfo.displayName);
      expect(options.pubKeyCredParams).toEqual([
        { alg: -7, type: 'public-key' },  // ES256
        { alg: -257, type: 'public-key' }, // RS256
      ]);
      expect(options.authenticatorSelection.authenticatorAttachment).toBe('platform');
      expect(options.authenticatorSelection.userVerification).toBe('required');
      expect(options.authenticatorSelection.residentKey).toBe('required');
      expect(options.timeout).toBe(60000);
      expect(options.attestation).toBe('direct');
    });

    it('should include existing credentials in excludeCredentials', async () => {
      const userInfo = {
        id: 'test-user-id',
        email: 'test@lukhas.ai',
        displayName: 'Test User',
      };

      const existingCredentials = [
        { credentialId: 'cred1', transports: ['internal'] },
        { credentialId: 'cred2', transports: ['usb', 'nfc'] },
      ];

      const options = await passkeyManager.generateRegistrationOptions(
        userInfo,
        'lukhas.ai',
        'https://lukhas.ai',
        existingCredentials
      );

      expect(options.excludeCredentials).toHaveLength(2);
      expect(options.excludeCredentials![0].id).toBe('cred1');
      expect(options.excludeCredentials![0].transports).toEqual(['internal']);
      expect(options.excludeCredentials![1].id).toBe('cred2');
      expect(options.excludeCredentials![1].transports).toEqual(['usb', 'nfc']);
    });

    it('should generate different challenges for each request', async () => {
      const userInfo = {
        id: 'test-user-id',
        email: 'test@lukhas.ai',
        displayName: 'Test User',
      };

      const options1 = await passkeyManager.generateRegistrationOptions(userInfo, 'lukhas.ai', 'https://lukhas.ai');
      const options2 = await passkeyManager.generateRegistrationOptions(userInfo, 'lukhas.ai', 'https://lukhas.ai');

      expect(options1.challenge).not.toBe(options2.challenge);
    });
  });

  describe('Authentication Challenge Generation', () => {
    it('should generate valid authentication challenge', async () => {
      const allowedCredentials = [
        { credentialId: 'cred1', transports: ['internal'] },
        { credentialId: 'cred2', transports: ['usb'] },
      ];

      const options = await passkeyManager.generateAuthenticationOptions(
        'lukhas.ai',
        allowedCredentials
      );

      expect(options.challenge).toBeDefined();
      expect(options.challenge).toHaveLength(128);
      expect(options.rpId).toBe('lukhas.ai');
      expect(options.userVerification).toBe('required');
      expect(options.timeout).toBe(60000);
      expect(options.allowCredentials).toHaveLength(2);
      expect(options.allowCredentials![0].id).toBe('cred1');
      expect(options.allowCredentials![0].transports).toEqual(['internal']);
    });

    it('should support usernameless authentication', async () => {
      const options = await passkeyManager.generateAuthenticationOptions('lukhas.ai');

      expect(options.challenge).toBeDefined();
      expect(options.allowCredentials).toBeUndefined();
    });
  });

  describe('Registration Verification', () => {
    let mockCredential: any;
    let mockChallenge: string;

    beforeEach(() => {
      mockChallenge = crypto.randomBytes(64).toString('hex');
      
      mockCredential = {
        id: 'test-credential-id',
        rawId: Buffer.from('test-credential-id'),
        type: 'public-key',
        response: {
          clientDataJSON: Buffer.from(JSON.stringify({
            type: 'webauthn.create',
            challenge: mockChallenge,
            origin: 'https://lukhas.ai',
          })),
          attestationObject: Buffer.from('mock-attestation-object'),
          getPublicKey: jest.fn(() => Buffer.from('mock-public-key')),
          getAuthenticatorData: jest.fn(() => Buffer.from('mock-auth-data')),
        },
        getClientExtensionResults: jest.fn(() => ({})),
      };
    });

    it('should verify valid registration credential', async () => {
      const verification = await passkeyManager.verifyRegistration(
        mockChallenge,
        mockCredential,
        'https://lukhas.ai'
      );

      expect(verification.verified).toBe(true);
      expect(verification.registrationInfo).toBeDefined();
      expect(verification.registrationInfo?.credentialId).toBe('test-credential-id');
      expect(verification.registrationInfo?.credentialPublicKey).toBeDefined();
      expect(verification.registrationInfo?.counter).toBeDefined();
    });

    it('should reject registration with wrong challenge', async () => {
      const wrongCredential = {
        ...mockCredential,
        response: {
          ...mockCredential.response,
          clientDataJSON: Buffer.from(JSON.stringify({
            type: 'webauthn.create',
            challenge: 'wrong-challenge',
            origin: 'https://lukhas.ai',
          })),
        },
      };

      const verification = await passkeyManager.verifyRegistration(
        mockChallenge,
        wrongCredential,
        'https://lukhas.ai'
      );

      expect(verification.verified).toBe(false);
      expect(verification.error).toMatch(/challenge/i);
    });

    it('should reject registration with wrong origin', async () => {
      const wrongCredential = {
        ...mockCredential,
        response: {
          ...mockCredential.response,
          clientDataJSON: Buffer.from(JSON.stringify({
            type: 'webauthn.create',
            challenge: mockChallenge,
            origin: 'https://evil.com',
          })),
        },
      };

      const verification = await passkeyManager.verifyRegistration(
        mockChallenge,
        wrongCredential,
        'https://lukhas.ai'
      );

      expect(verification.verified).toBe(false);
      expect(verification.error).toMatch(/origin/i);
    });

    it('should reject registration with wrong type', async () => {
      const wrongCredential = {
        ...mockCredential,
        response: {
          ...mockCredential.response,
          clientDataJSON: Buffer.from(JSON.stringify({
            type: 'webauthn.get', // Should be 'webauthn.create'
            challenge: mockChallenge,
            origin: 'https://lukhas.ai',
          })),
        },
      };

      const verification = await passkeyManager.verifyRegistration(
        mockChallenge,
        wrongCredential,
        'https://lukhas.ai'
      );

      expect(verification.verified).toBe(false);
      expect(verification.error).toMatch(/type/i);
    });
  });

  describe('Authentication Verification', () => {
    let mockCredential: any;
    let mockChallenge: string;
    let mockStoredCredential: any;

    beforeEach(() => {
      mockChallenge = crypto.randomBytes(64).toString('hex');
      
      mockCredential = {
        id: 'test-credential-id',
        rawId: Buffer.from('test-credential-id'),
        type: 'public-key',
        response: {
          clientDataJSON: Buffer.from(JSON.stringify({
            type: 'webauthn.get',
            challenge: mockChallenge,
            origin: 'https://lukhas.ai',
          })),
          authenticatorData: Buffer.from('mock-auth-data'),
          signature: Buffer.from('mock-signature'),
          userHandle: Buffer.from('test-user-id'),
        },
        getClientExtensionResults: jest.fn(() => ({})),
      };

      mockStoredCredential = {
        credentialId: 'test-credential-id',
        credentialPublicKey: Buffer.from('mock-public-key'),
        counter: 100,
        transports: ['internal'],
      };
    });

    it('should verify valid authentication credential', async () => {
      const verification = await passkeyManager.verifyAuthentication(
        mockChallenge,
        mockCredential,
        'https://lukhas.ai',
        mockStoredCredential
      );

      expect(verification.verified).toBe(true);
      expect(verification.authenticationInfo).toBeDefined();
      expect(verification.authenticationInfo?.credentialId).toBe('test-credential-id');
      expect(verification.authenticationInfo?.newCounter).toBeGreaterThan(mockStoredCredential.counter);
      expect(verification.userHandle).toBe('test-user-id');
    });

    it('should reject authentication with wrong challenge', async () => {
      const wrongCredential = {
        ...mockCredential,
        response: {
          ...mockCredential.response,
          clientDataJSON: Buffer.from(JSON.stringify({
            type: 'webauthn.get',
            challenge: 'wrong-challenge',
            origin: 'https://lukhas.ai',
          })),
        },
      };

      const verification = await passkeyManager.verifyAuthentication(
        mockChallenge,
        wrongCredential,
        'https://lukhas.ai',
        mockStoredCredential
      );

      expect(verification.verified).toBe(false);
      expect(verification.error).toMatch(/challenge/i);
    });

    it('should reject authentication with wrong origin', async () => {
      const wrongCredential = {
        ...mockCredential,
        response: {
          ...mockCredential.response,
          clientDataJSON: Buffer.from(JSON.stringify({
            type: 'webauthn.get',
            challenge: mockChallenge,
            origin: 'https://evil.com',
          })),
        },
      };

      const verification = await passkeyManager.verifyAuthentication(
        mockChallenge,
        wrongCredential,
        'https://lukhas.ai',
        mockStoredCredential
      );

      expect(verification.verified).toBe(false);
      expect(verification.error).toMatch(/origin/i);
    });

    it('should detect counter rollback attack', async () => {
      const credentialWithOldCounter = {
        ...mockCredential,
        response: {
          ...mockCredential.response,
          authenticatorData: Buffer.from('mock-auth-data-old-counter'),
        },
      };

      // Mock counter check to simulate rollback
      jest.spyOn(passkeyManager as any, 'parseAuthenticatorData').mockReturnValue({
        counter: 50, // Lower than stored counter (100)
      });

      const verification = await passkeyManager.verifyAuthentication(
        mockChallenge,
        credentialWithOldCounter,
        'https://lukhas.ai',
        mockStoredCredential
      );

      expect(verification.verified).toBe(false);
      expect(verification.error).toMatch(/counter/i);
    });
  });

  describe('Backup Code Integration', () => {
    it('should generate backup codes during registration', async () => {
      const backupCodes = await passkeyManager.generateBackupCodes('test-user-id');

      expect(backupCodes).toHaveLength(8);
      backupCodes.forEach(code => {
        expect(code).toMatch(/^[0-9]{6}$/); // 6-digit numeric codes
      });

      // All codes should be unique
      const uniqueCodes = new Set(backupCodes);
      expect(uniqueCodes.size).toBe(backupCodes.length);
    });

    it('should validate backup codes correctly', async () => {
      const backupCodes = await passkeyManager.generateBackupCodes('test-user-id');
      const validCode = backupCodes[0];
      const invalidCode = '000000';

      const validResult = await passkeyManager.validateBackupCode('test-user-id', validCode);
      expect(validResult.valid).toBe(true);

      const invalidResult = await passkeyManager.validateBackupCode('test-user-id', invalidCode);
      expect(invalidResult.valid).toBe(false);
    });

    it('should mark backup codes as used after validation', async () => {
      const backupCodes = await passkeyManager.generateBackupCodes('test-user-id');
      const code = backupCodes[0];

      // First use should succeed
      const firstUse = await passkeyManager.validateBackupCode('test-user-id', code);
      expect(firstUse.valid).toBe(true);

      // Second use should fail
      const secondUse = await passkeyManager.validateBackupCode('test-user-id', code);
      expect(secondUse.valid).toBe(false);
      expect(secondUse.error).toMatch(/used|invalid/i);
    });
  });

  describe('Performance Tests', () => {
    it('should generate challenges quickly', async () => {
      const userInfo = {
        id: 'test-user-id',
        email: 'test@lukhas.ai',
        displayName: 'Test User',
      };

      const startTime = process.hrtime.bigint();

      for (let i = 0; i < 100; i++) {
        await passkeyManager.generateRegistrationOptions(userInfo, 'lukhas.ai', 'https://lukhas.ai');
      }

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to ms
      const avgTime = duration / 100;

      // Should generate challenges in under 1ms on average
      expect(avgTime).toBeLessThan(1);
    });

    it('should handle concurrent registrations', async () => {
      const userInfo = {
        id: 'test-user-id',
        email: 'test@lukhas.ai',
        displayName: 'Test User',
      };

      const promises = Array.from({ length: 50 }, () =>
        passkeyManager.generateRegistrationOptions(userInfo, 'lukhas.ai', 'https://lukhas.ai')
      );

      const results = await Promise.all(promises);

      // All requests should succeed
      expect(results).toHaveLength(50);
      
      // All challenges should be unique
      const challenges = results.map(r => r.challenge);
      const uniqueChallenges = new Set(challenges);
      expect(uniqueChallenges.size).toBe(challenges.length);
    });
  });

  describe('Security Tests', () => {
    it('should resist timing attacks during verification', async () => {
      const mockChallenge = crypto.randomBytes(64).toString('hex');
      
      const validCredential = {
        id: 'valid-credential-id',
        rawId: Buffer.from('valid-credential-id'),
        type: 'public-key',
        response: {
          clientDataJSON: Buffer.from(JSON.stringify({
            type: 'webauthn.get',
            challenge: mockChallenge,
            origin: 'https://lukhas.ai',
          })),
          authenticatorData: Buffer.from('valid-auth-data'),
          signature: Buffer.from('valid-signature'),
          userHandle: Buffer.from('test-user-id'),
        },
      };

      const invalidCredentials = [
        { ...validCredential, id: 'invalid-credential-id' },
        { 
          ...validCredential, 
          response: { 
            ...validCredential.response, 
            signature: Buffer.from('invalid-signature') 
          } 
        },
        { 
          ...validCredential, 
          response: { 
            ...validCredential.response, 
            clientDataJSON: Buffer.from(JSON.stringify({
              type: 'webauthn.get',
              challenge: 'wrong-challenge',
              origin: 'https://lukhas.ai',
            }))
          } 
        },
      ];

      const mockStoredCredential = {
        credentialId: 'valid-credential-id',
        credentialPublicKey: Buffer.from('mock-public-key'),
        counter: 100,
        transports: ['internal'],
      };

      // Measure verification times
      const validTimes: number[] = [];
      const invalidTimes: number[] = [];

      for (let i = 0; i < 10; i++) {
        // Valid credential
        const startValid = process.hrtime.bigint();
        await passkeyManager.verifyAuthentication(
          mockChallenge,
          validCredential,
          'https://lukhas.ai',
          mockStoredCredential
        );
        const endValid = process.hrtime.bigint();
        validTimes.push(Number(endValid - startValid) / 1000000);

        // Invalid credentials
        for (const invalidCredential of invalidCredentials) {
          const startInvalid = process.hrtime.bigint();
          await passkeyManager.verifyAuthentication(
            mockChallenge,
            invalidCredential,
            'https://lukhas.ai',
            mockStoredCredential
          );
          const endInvalid = process.hrtime.bigint();
          invalidTimes.push(Number(endInvalid - startInvalid) / 1000000);
        }
      }

      // Calculate averages
      const avgValidTime = validTimes.reduce((sum, t) => sum + t, 0) / validTimes.length;
      const avgInvalidTime = invalidTimes.reduce((sum, t) => sum + t, 0) / invalidTimes.length;

      // Timing difference should be minimal (within 50% to prevent timing attacks)
      const timingDifference = Math.abs(avgValidTime - avgInvalidTime);
      const maxAllowedDifference = Math.max(avgValidTime, avgInvalidTime) * 0.5;

      expect(timingDifference).toBeLessThan(maxAllowedDifference);
    });

    it('should generate cryptographically secure challenges', async () => {
      const challenges = await Promise.all(
        Array.from({ length: 1000 }, () =>
          passkeyManager.generateRegistrationOptions(
            { id: 'user', email: 'test@lukhas.ai', displayName: 'Test' },
            'lukhas.ai',
            'https://lukhas.ai'
          )
        )
      );

      const challengeStrings = challenges.map(c => c.challenge);

      // Check for duplicates (should be none with cryptographically secure generation)
      const uniqueChallenges = new Set(challengeStrings);
      expect(uniqueChallenges.size).toBe(challengeStrings.length);

      // Check challenge entropy
      const concatenated = challengeStrings.join('');
      const charCounts = new Map<string, number>();
      
      for (const char of concatenated) {
        charCounts.set(char, (charCounts.get(char) || 0) + 1);
      }

      // Calculate Shannon entropy
      const entropy = Array.from(charCounts.values()).reduce((entropy, count) => {
        const probability = count / concatenated.length;
        return entropy - probability * Math.log2(probability);
      }, 0);

      // Should have high entropy (close to max possible for hex)
      expect(entropy).toBeGreaterThan(3.8); // High entropy threshold for hex
    });
  });
});

describe('PasskeyUtils', () => {
  describe('Credential ID Utilities', () => {
    it('should encode and decode credential IDs correctly', () => {
      const originalId = 'test-credential-id';
      const buffer = Buffer.from(originalId);
      
      const encoded = PasskeyUtils.encodeCredentialId(buffer);
      const decoded = PasskeyUtils.decodeCredentialId(encoded);

      expect(decoded.toString()).toBe(originalId);
    });

    it('should handle binary credential IDs', () => {
      const binaryId = crypto.randomBytes(32);
      
      const encoded = PasskeyUtils.encodeCredentialId(binaryId);
      const decoded = PasskeyUtils.decodeCredentialId(encoded);

      expect(decoded).toEqual(binaryId);
    });
  });

  describe('Client Data Parsing', () => {
    it('should parse client data JSON correctly', () => {
      const clientData = {
        type: 'webauthn.create',
        challenge: 'test-challenge',
        origin: 'https://lukhas.ai',
        crossOrigin: false,
      };

      const clientDataJSON = Buffer.from(JSON.stringify(clientData));
      const parsed = PasskeyUtils.parseClientDataJSON(clientDataJSON);

      expect(parsed.type).toBe('webauthn.create');
      expect(parsed.challenge).toBe('test-challenge');
      expect(parsed.origin).toBe('https://lukhas.ai');
      expect(parsed.crossOrigin).toBe(false);
    });

    it('should handle malformed client data gracefully', () => {
      const invalidJSON = Buffer.from('invalid json');
      
      expect(() => PasskeyUtils.parseClientDataJSON(invalidJSON)).toThrow();
    });
  });

  describe('Transport Utilities', () => {
    it('should validate transport arrays', () => {
      const validTransports = ['usb', 'nfc', 'ble', 'internal'];
      const invalidTransports = ['usb', 'invalid-transport', 'nfc'];

      expect(PasskeyUtils.validateTransports(validTransports)).toBe(true);
      expect(PasskeyUtils.validateTransports(invalidTransports)).toBe(false);
    });

    it('should convert transport strings correctly', () => {
      expect(PasskeyUtils.normalizeTransport('usb')).toBe('usb');
      expect(PasskeyUtils.normalizeTransport('nfc')).toBe('nfc');
      expect(PasskeyUtils.normalizeTransport('invalid')).toBeUndefined();
    });
  });

  describe('COSE Key Utilities', () => {
    it('should extract public key from COSE format', () => {
      // Mock COSE public key data
      const mockCOSEKey = Buffer.from([
        0xa5, // map with 5 entries
        0x01, 0x02, // kty: 2 (EC2)
        0x03, 0x38, 0x18, // alg: -7 (ES256)
        0x20, 0x01, // crv: 1 (P-256)
        0x21, 0x58, 0x20, // x coordinate (32 bytes)
        ...new Array(32).fill(0x01),
        0x22, 0x58, 0x20, // y coordinate (32 bytes)
        ...new Array(32).fill(0x02),
      ]);

      const publicKey = PasskeyUtils.extractPublicKeyFromCOSE(mockCOSEKey);
      expect(publicKey).toBeDefined();
      expect(Buffer.isBuffer(publicKey)).toBe(true);
    });
  });
});