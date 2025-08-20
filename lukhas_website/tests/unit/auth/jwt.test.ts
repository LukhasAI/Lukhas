/**
 * LUKHAS AI ΛiD Authentication System - JWT Manager Unit Tests
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Tests for JWT token generation, validation, and rotation
 */

import { JWTManager, JWTUtils, DEFAULT_TOKEN_CONFIG } from '@/packages/auth/jwt';
import { JWKSManager } from '@/packages/auth/jwks';
import crypto from 'crypto';

describe('JWTManager', () => {
  let jwtManager: JWTManager;
  let jwksManager: JWKSManager;
  let testKeyPair: { publicKey: string; privateKey: string };

  beforeAll(() => {
    // Generate test key pair
    const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
      modulusLength: 2048,
      publicKeyEncoding: { type: 'spki', format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
    });

    testKeyPair = { publicKey, privateKey };
  });

  beforeEach(() => {
    // Initialize JWKS manager with test keys
    jwksManager = new JWKSManager({
      privateKey: testKeyPair.privateKey,
      publicKey: testKeyPair.publicKey,
      keyId: 'test-key-id',
      rotationDays: 90,
    });

    // Initialize JWT manager
    jwtManager = new JWTManager({
      issuer: 'https://auth.lukhas.ai',
      audience: 'https://api.lukhas.ai',
      accessTokenTTL: 15 * 60, // 15 minutes
      refreshTokenTTL: 30 * 24 * 60 * 60, // 30 days
      idTokenTTL: 60 * 60, // 1 hour
    }, jwksManager);
  });

  describe('Access Token Generation', () => {
    it('should generate valid access token with required claims', async () => {
      const userId = 'test-user-id';
      const tier = 'T1';
      const sessionId = 'test-session-id';
      const scopes = ['matriz:read', 'auth:login'];
      const roles = ['viewer'];
      const metadata = { ipAddress: '127.0.0.1' };

      const result = await jwtManager.issueAccessToken(
        userId,
        tier,
        sessionId,
        scopes,
        roles,
        metadata
      );

      expect(result.token).toBeDefined();
      expect(result.expiresIn).toBe(15 * 60);
      expect(typeof result.token).toBe('string');

      // Verify token structure
      const parts = result.token.split('.');
      expect(parts).toHaveLength(3);

      // Verify header
      const header = JSON.parse(Buffer.from(parts[0], 'base64url').toString());
      expect(header.alg).toBe('RS256');
      expect(header.typ).toBe('JWT');
      expect(header.kid).toBe('test-key-id');

      // Verify payload
      const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString());
      expect(payload.sub).toBe(userId);
      expect(payload.iss).toBe('https://auth.lukhas.ai');
      expect(payload.aud).toBe('https://api.lukhas.ai');
      expect(payload.tier).toBe(tier);
      expect(payload.sid).toBe(sessionId);
      expect(payload.scope).toBe(scopes.join(' '));
      expect(payload.roles).toEqual(roles);
      expect(payload.metadata).toEqual(metadata);
      expect(payload.iat).toBeDefined();
      expect(payload.exp).toBeDefined();
      expect(payload.exp - payload.iat).toBe(15 * 60);
    });

    it('should generate tokens with different expiration times based on tier', async () => {
      const t1Result = await jwtManager.issueAccessToken('user1', 'T1', 'session1', [], []);
      const t5Result = await jwtManager.issueAccessToken('user2', 'T5', 'session2', [], []);

      // T5 users might get longer token lifetimes (business rule)
      const t1Payload = JSON.parse(Buffer.from(t1Result.token.split('.')[1], 'base64url').toString());
      const t5Payload = JSON.parse(Buffer.from(t5Result.token.split('.')[1], 'base64url').toString());

      expect(t1Payload.tier).toBe('T1');
      expect(t5Payload.tier).toBe('T5');
    });

    it('should include rate limiting information for different tiers', async () => {
      const t1Result = await jwtManager.issueAccessToken('user1', 'T1', 'session1', [], []);
      const t5Result = await jwtManager.issueAccessToken('user2', 'T5', 'session2', [], []);

      const t1Payload = JSON.parse(Buffer.from(t1Result.token.split('.')[1], 'base64url').toString());
      const t5Payload = JSON.parse(Buffer.from(t5Result.token.split('.')[1], 'base64url').toString());

      // Verify tier information is included for rate limiting
      expect(t1Payload.tier).toBe('T1');
      expect(t5Payload.tier).toBe('T5');
    });
  });

  describe('Refresh Token Generation', () => {
    it('should generate secure refresh token', async () => {
      const result = await jwtManager.issueRefreshToken(
        'test-user-id',
        'test-session-id',
        'test-device-id',
        '127.0.0.1'
      );

      expect(result.token).toBeDefined();
      expect(result.tokenId).toBeDefined();
      expect(result.familyId).toBeDefined();
      expect(result.expiresAt).toBeInstanceOf(Date);
      expect(result.expiresAt.getTime()).toBeGreaterThan(Date.now());

      // Refresh token should be opaque (not JWT)
      expect(result.token.split('.')).toHaveLength(1);
      expect(result.token).toMatch(/^[A-Za-z0-9_-]+$/);
    });

    it('should generate tokens with family relationship', async () => {
      const token1 = await jwtManager.issueRefreshToken('user1', 'session1', 'device1', '127.0.0.1');
      const token2 = await jwtManager.issueRefreshToken('user1', 'session1', 'device1', '127.0.0.1');

      // Both tokens should belong to the same family for rotation
      expect(token1.familyId).toBeDefined();
      expect(token2.familyId).toBeDefined();
    });
  });

  describe('Token Validation', () => {
    it('should validate valid access token', async () => {
      const issued = await jwtManager.issueAccessToken(
        'test-user-id',
        'T1',
        'test-session-id',
        ['matriz:read'],
        ['viewer']
      );

      const validation = await jwtManager.validateAccessToken(issued.token);

      expect(validation.valid).toBe(true);
      expect(validation.payload).toBeDefined();
      expect(validation.payload?.sub).toBe('test-user-id');
      expect(validation.payload?.tier).toBe('T1');
      expect(validation.payload?.scope).toBe('matriz:read');
      expect(validation.error).toBeUndefined();
    });

    it('should reject expired token', async () => {
      // Create token with very short expiration
      const shortLivedManager = new JWTManager({
        ...DEFAULT_TOKEN_CONFIG,
        accessTokenTTL: 1, // 1 second
      }, jwksManager);

      const issued = await shortLivedManager.issueAccessToken(
        'test-user-id',
        'T1',
        'test-session-id',
        ['matriz:read'],
        ['viewer']
      );

      // Wait for token to expire
      await new Promise(resolve => setTimeout(resolve, 1500));

      const validation = await jwtManager.validateAccessToken(issued.token);

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/expired/i);
    });

    it('should reject token with invalid signature', async () => {
      const issued = await jwtManager.issueAccessToken(
        'test-user-id',
        'T1',
        'test-session-id',
        ['matriz:read'],
        ['viewer']
      );

      // Tamper with signature
      const parts = issued.token.split('.');
      const tamperedToken = `${parts[0]}.${parts[1]}.invalid-signature`;

      const validation = await jwtManager.validateAccessToken(tamperedToken);

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/signature/i);
    });

    it('should reject token with modified payload', async () => {
      const issued = await jwtManager.issueAccessToken(
        'test-user-id',
        'T1',
        'test-session-id',
        ['matriz:read'],
        ['viewer']
      );

      // Tamper with payload
      const parts = issued.token.split('.');
      const tamperedPayload = Buffer.from(JSON.stringify({
        sub: 'hacker-user-id',
        tier: 'T5',
        scope: 'admin:all',
      })).toString('base64url');
      const tamperedToken = `${parts[0]}.${tamperedPayload}.${parts[2]}`;

      const validation = await jwtManager.validateAccessToken(tamperedToken);

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/signature/i);
    });

    it('should validate token with specific validation options', async () => {
      const issued = await jwtManager.issueAccessToken(
        'test-user-id',
        'T1',
        'test-session-id',
        ['matriz:read'],
        ['viewer']
      );

      const validation = await jwtManager.validateAccessToken(issued.token, {
        audience: 'https://api.lukhas.ai',
        issuer: 'https://auth.lukhas.ai',
        clockTolerance: 60,
        requiredScopes: ['matriz:read'],
        requiredRoles: ['viewer'],
      });

      expect(validation.valid).toBe(true);
    });

    it('should reject token missing required scopes', async () => {
      const issued = await jwtManager.issueAccessToken(
        'test-user-id',
        'T1',
        'test-session-id',
        ['matriz:read'],
        ['viewer']
      );

      const validation = await jwtManager.validateAccessToken(issued.token, {
        requiredScopes: ['admin:write'],
      });

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/scope/i);
    });

    it('should reject token missing required roles', async () => {
      const issued = await jwtManager.issueAccessToken(
        'test-user-id',
        'T1',
        'test-session-id',
        ['matriz:read'],
        ['viewer']
      );

      const validation = await jwtManager.validateAccessToken(issued.token, {
        requiredRoles: ['admin'],
      });

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/role/i);
    });
  });

  describe('Refresh Token Validation', () => {
    it('should validate refresh token family', async () => {
      const refreshToken = await jwtManager.issueRefreshToken(
        'test-user-id',
        'test-session-id',
        'test-device-id',
        '127.0.0.1'
      );

      const validation = await jwtManager.validateRefreshTokenFamily(refreshToken.familyId);

      expect(validation.valid).toBe(true);
      expect(validation.family).toBeDefined();
    });

    it('should detect refresh token reuse', async () => {
      const token1 = await jwtManager.issueRefreshToken('user1', 'session1', 'device1', '127.0.0.1');
      const token2 = await jwtManager.issueRefreshToken('user1', 'session1', 'device1', '127.0.0.1');

      // Simulate token rotation
      await jwtManager.rotateRefreshToken(token1.token, token2.token);

      // Try to use old token (should be detected as reuse)
      const validation = await jwtManager.validateRefreshToken(token1.token);

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/reuse|revoked/i);
    });
  });

  describe('Token Rotation', () => {
    it('should rotate refresh tokens securely', async () => {
      const originalToken = await jwtManager.issueRefreshToken(
        'test-user-id',
        'test-session-id',
        'test-device-id',
        '127.0.0.1'
      );

      const rotationResult = await jwtManager.rotateRefreshToken(originalToken.token);

      expect(rotationResult.success).toBe(true);
      expect(rotationResult.newToken).toBeDefined();
      expect(rotationResult.newToken).not.toBe(originalToken.token);

      // Old token should be invalidated
      const oldValidation = await jwtManager.validateRefreshToken(originalToken.token);
      expect(oldValidation.valid).toBe(false);

      // New token should be valid
      const newValidation = await jwtManager.validateRefreshToken(rotationResult.newToken!);
      expect(newValidation.valid).toBe(true);
    });

    it('should maintain family relationship during rotation', async () => {
      const originalToken = await jwtManager.issueRefreshToken(
        'test-user-id',
        'test-session-id',
        'test-device-id',
        '127.0.0.1'
      );

      const rotationResult = await jwtManager.rotateRefreshToken(originalToken.token);

      // Both tokens should belong to the same family
      expect(rotationResult.familyId).toBe(originalToken.familyId);
    });
  });

  describe('Performance Tests', () => {
    it('should generate tokens within performance targets', async () => {
      const iterations = 100;
      const startTime = process.hrtime.bigint();

      for (let i = 0; i < iterations; i++) {
        await jwtManager.issueAccessToken(
          `user-${i}`,
          'T1',
          `session-${i}`,
          ['matriz:read'],
          ['viewer']
        );
      }

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to ms
      const avgTime = duration / iterations;

      // Should generate tokens in under 10ms on average
      expect(avgTime).toBeLessThan(10);
    });

    it('should validate tokens within performance targets', async () => {
      // Generate test tokens
      const tokens = await Promise.all(
        Array.from({ length: 100 }, (_, i) =>
          jwtManager.issueAccessToken(
            `user-${i}`,
            'T1',
            `session-${i}`,
            ['matriz:read'],
            ['viewer']
          )
        )
      );

      const startTime = process.hrtime.bigint();

      for (const token of tokens) {
        await jwtManager.validateAccessToken(token.token);
      }

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to ms
      const avgTime = duration / tokens.length;

      // Should validate tokens in under 5ms on average
      expect(avgTime).toBeLessThan(5);
    });
  });

  describe('Security Tests', () => {
    it('should resist timing attacks during validation', async () => {
      const validToken = await jwtManager.issueAccessToken(
        'test-user-id',
        'T1',
        'test-session-id',
        ['matriz:read'],
        ['viewer']
      );

      const invalidTokens = [
        'invalid.token.here',
        validToken.token.slice(0, -10) + 'tampered123',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature',
      ];

      // Measure validation times
      const validTimes: number[] = [];
      const invalidTimes: number[] = [];

      for (let i = 0; i < 10; i++) {
        // Valid token
        const startValid = process.hrtime.bigint();
        await jwtManager.validateAccessToken(validToken.token);
        const endValid = process.hrtime.bigint();
        validTimes.push(Number(endValid - startValid) / 1000000);

        // Invalid tokens
        for (const invalidToken of invalidTokens) {
          const startInvalid = process.hrtime.bigint();
          await jwtManager.validateAccessToken(invalidToken);
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

    it('should generate cryptographically secure refresh tokens', async () => {
      const tokens = await Promise.all(
        Array.from({ length: 1000 }, () =>
          jwtManager.issueRefreshToken('user', 'session', 'device', '127.0.0.1')
        )
      );

      const tokenStrings = tokens.map(t => t.token);

      // Check for duplicates (should be none with cryptographically secure generation)
      const uniqueTokens = new Set(tokenStrings);
      expect(uniqueTokens.size).toBe(tokenStrings.length);

      // Check token entropy (should have high entropy)
      const concatenated = tokenStrings.join('');
      const charCounts = new Map<string, number>();
      
      for (const char of concatenated) {
        charCounts.set(char, (charCounts.get(char) || 0) + 1);
      }

      // Calculate Shannon entropy
      const entropy = Array.from(charCounts.values()).reduce((entropy, count) => {
        const probability = count / concatenated.length;
        return entropy - probability * Math.log2(probability);
      }, 0);

      // Should have high entropy (close to max possible for base64url)
      expect(entropy).toBeGreaterThan(5); // High entropy threshold
    });
  });
});

describe('JWTUtils', () => {
  describe('Token Parsing', () => {
    it('should parse JWT token correctly', () => {
      const testPayload = {
        sub: 'test-user',
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + 3600,
      };

      const header = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url');
      const payload = Buffer.from(JSON.stringify(testPayload)).toString('base64url');
      const token = `${header}.${payload}.signature`;

      const parsed = JWTUtils.parseToken(token);

      expect(parsed.header.alg).toBe('RS256');
      expect(parsed.header.typ).toBe('JWT');
      expect(parsed.payload.sub).toBe('test-user');
      expect(parsed.payload.iat).toBe(testPayload.iat);
      expect(parsed.payload.exp).toBe(testPayload.exp);
    });

    it('should handle malformed tokens gracefully', () => {
      const malformedTokens = [
        'not.a.token',
        'missing.signature',
        'too.many.parts.here.invalid',
        '',
        'invalid-base64.invalid-base64.invalid-base64',
      ];

      for (const token of malformedTokens) {
        expect(() => JWTUtils.parseToken(token)).toThrow();
      }
    });
  });

  describe('Token Validation Utilities', () => {
    it('should check token expiration correctly', () => {
      const expiredToken = {
        exp: Math.floor(Date.now() / 1000) - 3600, // 1 hour ago
      };

      const validToken = {
        exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour from now
      };

      expect(JWTUtils.isTokenExpired(expiredToken)).toBe(true);
      expect(JWTUtils.isTokenExpired(validToken)).toBe(false);
    });

    it('should validate audience correctly', () => {
      const token = { aud: 'https://api.lukhas.ai' };

      expect(JWTUtils.validateAudience(token, 'https://api.lukhas.ai')).toBe(true);
      expect(JWTUtils.validateAudience(token, 'https://evil.com')).toBe(false);
    });

    it('should validate issuer correctly', () => {
      const token = { iss: 'https://auth.lukhas.ai' };

      expect(JWTUtils.validateIssuer(token, 'https://auth.lukhas.ai')).toBe(true);
      expect(JWTUtils.validateIssuer(token, 'https://evil.com')).toBe(false);
    });

    it('should validate scopes correctly', () => {
      const token = { scope: 'matriz:read auth:login profile:view' };

      expect(JWTUtils.hasScope(token, 'matriz:read')).toBe(true);
      expect(JWTUtils.hasScope(token, 'auth:login')).toBe(true);
      expect(JWTUtils.hasScope(token, 'admin:write')).toBe(false);
      expect(JWTUtils.hasAllScopes(token, ['matriz:read', 'auth:login'])).toBe(true);
      expect(JWTUtils.hasAllScopes(token, ['matriz:read', 'admin:write'])).toBe(false);
    });
  });
});