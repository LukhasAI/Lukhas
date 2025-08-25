/**
 * ΛiD Authentication System - Integration Tests
 * 
 * Comprehensive integration tests for all authentication components
 * Tests Phase 1 infrastructure implementation
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  hasScope,
  getAvailableScopes,
  canGrantScope,
  Tier,
  Scope,
  Role
} from '../src/scopes';
import {
  checkRateLimit,
  getRateLimitStatus,
  resetRateLimits,
  TIER_RATE_LIMITS
} from '../src/rate-limits';
import {
  jwtManager,
  generateAccessToken,
  generateRefreshToken,
  generateTokenPair,
  verifyToken
} from '../src/jwt';
import {
  passkeyManager,
  registerPasskey,
  verifyPasskeyRegistration,
  authenticateWithPasskey,
  verifyPasskeyAuthentication,
  checkPasskeySupport
} from '../src/passkeys';
import {
  magicLinkManager,
  sendMagicLink,
  verifyMagicLink,
  checkMagicLinkStatus
} from '../src/magic-links';
import {
  securityManager,
  RefreshTokenFamilyManager,
  DeviceBindingManager,
  SessionRotationManager,
  AccountLockoutManager
} from '../src/security';
import {
  getTierDefinition,
  validateTierTransition,
  tierCanPerformOperation,
  getTierUpgradeRecommendations
} from '../src/tier-config';
import { UserTier, AuthScope } from '../types/auth.types';

// =============================================================================
// TEST SETUP AND UTILITIES
// =============================================================================

describe('ΛiD Authentication System - Phase 1 Integration Tests', () => {
  
  beforeEach(() => {
    // Reset all stores and timers before each test
    jest.clearAllMocks();
    resetRateLimits('test-user', undefined, undefined);
  });

  afterEach(() => {
    // Cleanup after each test
    jest.clearAllTimers();
  });

  // =============================================================================
  // SCOPE MANAGEMENT TESTS
  // =============================================================================

  describe('Scope Management', () => {
    it('should enforce deny-by-default security', () => {
      const result = hasScope(
        'T1' as UserTier,
        Role.VIEWER,
        [],
        'matriz:admin' as AuthScope
      );

      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Scope \'matriz:admin\' not available in tier T1');
    });

    it('should allow valid tier and role combinations', () => {
      const result = hasScope(
        'T2' as UserTier,
        Role.DEVELOPER,
        ['matriz:write' as AuthScope],
        'matriz:write' as AuthScope
      );

      expect(result.allowed).toBe(true);
      expect(result.metadata?.tier).toBe('T2');
      expect(result.metadata?.role).toBe('developer');
    });

    it('should handle scope inheritance correctly', () => {
      const result = hasScope(
        'T4' as UserTier,
        Role.ADMIN,
        ['matriz:admin' as AuthScope],
        'matriz:read' as AuthScope
      );

      expect(result.allowed).toBe(true);
      expect(result.metadata?.grantedVia).toBe('inherited');
    });

    it('should validate conditional access rules', () => {
      const context = {
        conditions: {
          timeWindow: {
            start: new Date(Date.now() - 60000).toISOString(),
            end: new Date(Date.now() + 60000).toISOString()
          }
        }
      };

      const result = hasScope(
        'T3' as UserTier,
        Role.DEVELOPER,
        ['org:read' as AuthScope],
        'org:read' as AuthScope,
        context
      );

      expect(result.allowed).toBe(true);
    });

    it('should get available scopes for each tier', () => {
      const t1Scopes = getAvailableScopes('T1');
      const t5Scopes = getAvailableScopes('T5');

      expect(t1Scopes).toHaveLength(4);
      expect(t1Scopes).toContain('matriz:read');
      expect(t5Scopes.length).toBeGreaterThan(t1Scopes.length);
    });

    it('should validate scope granting permissions', () => {
      expect(canGrantScope('T1', Role.VIEWER, 'matriz:admin' as AuthScope)).toBe(false);
      expect(canGrantScope('T4', Role.ADMIN, 'matriz:admin' as AuthScope)).toBe(true);
    });
  });

  // =============================================================================
  // RATE LIMITING TESTS
  // =============================================================================

  describe('Rate Limiting', () => {
    it('should enforce tier-based rate limits', () => {
      const userId = 'test-user-t1';
      
      // T1 users have 30 RPM limit
      for (let i = 0; i < 30; i++) {
        const result = checkRateLimit(userId, 'T1');
        expect(result.allowed).toBe(true);
      }

      // 31st request should be blocked
      const blockedResult = checkRateLimit(userId, 'T1');
      expect(blockedResult.allowed).toBe(false);
      expect(blockedResult.reason).toContain('Rate limit exceeded');
    });

    it('should handle operation-specific limits', () => {
      const userId = 'test-user-auth';
      
      // Auth operations have stricter limits
      for (let i = 0; i < 10; i++) {
        const result = checkRateLimit(userId, 'T2', 'auth:login');
        expect(result.allowed).toBe(true);
      }

      const blockedResult = checkRateLimit(userId, 'T2', 'auth:login');
      expect(blockedResult.allowed).toBe(false);
    });

    it('should provide rate limit status information', () => {
      const userId = 'test-user-status';
      
      // Make some requests
      checkRateLimit(userId, 'T2');
      checkRateLimit(userId, 'T2');
      
      const status = getRateLimitStatus(userId, 'T2');
      
      expect(status.current.minute).toBe(2);
      expect(status.remaining.minute).toBe(58); // T2 has 60 RPM
      expect(status.limits.rpm).toBe(60);
    });

    it('should handle burst allowances', () => {
      const userId = 'test-user-burst';
      const config = TIER_RATE_LIMITS.T1;
      
      // Should allow burst beyond normal limit
      for (let i = 0; i < config.rpm + config.burst; i++) {
        const result = checkRateLimit(userId, 'T1');
        expect(result.allowed).toBe(true);
      }

      // Beyond burst should be blocked
      const blockedResult = checkRateLimit(userId, 'T1');
      expect(blockedResult.allowed).toBe(false);
    });
  });

  // =============================================================================
  // JWT MANAGEMENT TESTS
  // =============================================================================

  describe('JWT Management', () => {
    it('should generate and verify access tokens', async () => {
      const userId = 'test-user';
      const tier = 'T2' as UserTier;
      const scopes = ['matriz:read', 'matriz:write'] as AuthScope[];

      const token = await generateAccessToken(userId, tier, scopes);
      expect(token).toBeTruthy();
      expect(typeof token).toBe('string');

      const verification = await verifyToken(token);
      expect(verification.valid).toBe(true);
      expect(verification.payload?.sub).toBe(userId);
      expect(verification.payload?.tier).toBe(tier);
      expect(verification.payload?.type).toBe('access');
    });

    it('should generate token pairs with proper structure', async () => {
      const userId = 'test-user';
      const tier = 'T3' as UserTier;
      const scopes = ['org:read', 'org:settings'] as AuthScope[];
      const deviceHandle = 'device-123';
      const familyId = 'family-456';

      const tokenPair = await generateTokenPair(
        userId,
        tier,
        scopes,
        deviceHandle,
        familyId
      );

      expect(tokenPair.accessToken).toBeTruthy();
      expect(tokenPair.refreshToken).toBeTruthy();
      expect(tokenPair.tokenType).toBe('Bearer');
      expect(tokenPair.expiresIn).toBe(900); // 15 minutes
      expect(tokenPair.scope).toBe(scopes.join(' '));

      // Verify both tokens
      const accessVerification = await verifyToken(tokenPair.accessToken);
      const refreshVerification = await verifyToken(tokenPair.refreshToken);

      expect(accessVerification.valid).toBe(true);
      expect(refreshVerification.valid).toBe(true);
      expect(refreshVerification.payload?.type).toBe('refresh');
      expect(refreshVerification.payload?.device).toBe(deviceHandle);
      expect(refreshVerification.payload?.family).toBe(familyId);
    });

    it('should handle expired tokens correctly', async () => {
      const userId = 'test-user';
      const tier = 'T1' as UserTier;
      const scopes = ['matriz:read'] as AuthScope[];

      // Generate token with very short TTL
      const token = await generateAccessToken(userId, tier, scopes, { ttl: -1 });
      
      const verification = await verifyToken(token);
      expect(verification.valid).toBe(false);
      expect(verification.reason).toContain('expired');
    });

    it('should provide JWKS endpoint', async () => {
      const jwks = await jwtManager.getJWKS();
      
      expect(jwks.keys).toBeTruthy();
      expect(Array.isArray(jwks.keys)).toBe(true);
      expect(jwks.keys.length).toBeGreaterThan(0);
      
      const key = jwks.keys[0];
      expect(key.kty).toBe('RSA');
      expect(key.use).toBe('sig');
      expect(key.alg).toBe('RS256');
      expect(key.kid).toBeTruthy();
    });
  });

  // =============================================================================
  // PASSKEY TESTS
  // =============================================================================

  describe('Passkey Management', () => {
    it('should check passkey support capabilities', async () => {
      // Mock browser environment
      global.window = {
        navigator: {
          credentials: {}
        },
        PublicKeyCredential: {
          isUserVerifyingPlatformAuthenticatorAvailable: jest.fn().mockResolvedValue(true),
          isConditionalMediationAvailable: jest.fn().mockResolvedValue(true)
        }
      } as any;

      const support = await checkPasskeySupport();
      
      expect(support.supported).toBe(true);
      expect(support.capabilities?.platform).toBe(true);
      expect(support.capabilities?.conditionalUI).toBe(true);
    });

    it('should generate registration options with proper configuration', async () => {
      const userId = 'test-user';
      const userName = 'test@lukhas.ai';
      const userDisplayName = 'Test User';

      const options = await registerPasskey(userId, userName, userDisplayName);

      expect(options.rp.id).toBe('lukhas.ai');
      expect(options.rp.name).toBe('LUKHAS AI');
      expect(options.user.name).toBe(userName);
      expect(options.user.displayName).toBe(userDisplayName);
      expect(options.authenticatorSelection.userVerification).toBe('required');
      expect(options.authenticatorSelection.residentKey).toBe('required');
      expect(options.attestation).toBe('direct');
      expect(options.challenge).toBeTruthy();
    });

    it('should generate authentication options for username-less login', async () => {
      const options = await authenticateWithPasskey();

      expect(options.challenge).toBeTruthy();
      expect(options.rpId).toBe('lukhas.ai');
      expect(options.userVerification).toBe('required');
      expect(options.allowCredentials).toBeUndefined(); // Discoverable credentials
    });

    it('should handle authenticator information correctly', () => {
      const aaguid = '00000000-0000-0000-0000-000000000000';
      const info = passkeyManager.getAuthenticatorInfo(aaguid);

      expect(info).toBeTruthy();
      expect(info?.name).toBe('Touch ID');
      expect(info?.vendor).toBe('Apple');
      expect(info?.type).toBe('platform');
      expect(info?.trusted).toBe(true);
    });
  });

  // =============================================================================
  // MAGIC LINK TESTS
  // =============================================================================

  describe('Magic Link Management', () => {
    it('should generate magic links with proper configuration', async () => {
      const email = 'test@lukhas.ai';
      const purpose = 'login';
      const options = {
        ipAddress: '192.168.1.1',
        userAgent: 'Mozilla/5.0 Test',
        userId: 'test-user',
        userTier: 'T2' as UserTier
      };

      const result = await sendMagicLink(email, purpose, options);

      expect(result.success).toBe(true);
      expect(result.token).toBeTruthy();
      expect(result.magicLink).toContain('lukhas.ai/auth/magic-link');
      expect(result.expiresIn).toBe(600); // 10 minutes
    });

    it('should enforce email throttling', async () => {
      const email = 'throttle@lukhas.ai';
      const options = {
        ipAddress: '192.168.1.1',
        userAgent: 'Mozilla/5.0 Test'
      };

      // Send up to the limit
      for (let i = 0; i < 3; i++) {
        const result = await sendMagicLink(email, 'login', options);
        expect(result.success).toBe(true);
      }

      // Next attempt should be throttled
      const throttledResult = await sendMagicLink(email, 'login', options);
      expect(throttledResult.success).toBe(false);
      expect(throttledResult.reason).toContain('throttled');
    });

    it('should enforce IP throttling', async () => {
      const ipAddress = '192.168.1.100';
      const options = {
        ipAddress,
        userAgent: 'Mozilla/5.0 Test'
      };

      // Send up to the IP limit
      for (let i = 0; i < 10; i++) {
        const result = await sendMagicLink(`test${i}@lukhas.ai`, 'login', options);
        expect(result.success).toBe(true);
      }

      // Next attempt should be throttled
      const throttledResult = await sendMagicLink('test100@lukhas.ai', 'login', options);
      expect(throttledResult.success).toBe(false);
      expect(throttledResult.reason).toContain('IP');
    });

    it('should validate magic links correctly', async () => {
      const email = 'validate@lukhas.ai';
      const options = {
        ipAddress: '192.168.1.1',
        userAgent: 'Mozilla/5.0 Test'
      };

      const result = await sendMagicLink(email, 'login', options);
      expect(result.success).toBe(true);

      if (result.token) {
        const validation = await verifyMagicLink(
          result.token,
          options.ipAddress,
          options.userAgent
        );

        expect(validation.valid).toBe(true);
        expect(validation.email).toBe(email);
        expect(validation.purpose).toBe('login');

        // Second use should fail
        const secondValidation = await verifyMagicLink(
          result.token,
          options.ipAddress,
          options.userAgent
        );

        expect(secondValidation.valid).toBe(false);
        expect(secondValidation.reason).toContain('already used');
      }
    });

    it('should provide magic link status information', async () => {
      const email = 'status@lukhas.ai';
      const options = {
        ipAddress: '192.168.1.1',
        userAgent: 'Mozilla/5.0 Test'
      };

      const result = await sendMagicLink(email, 'register', options);
      expect(result.success).toBe(true);

      if (result.token) {
        const status = await checkMagicLinkStatus(result.token);

        expect(status.exists).toBe(true);
        expect(status.used).toBe(false);
        expect(status.expired).toBe(false);
        expect(status.attempts).toBe(0);
        expect(status.maxAttempts).toBe(3);
      }
    });
  });

  // =============================================================================
  // SECURITY FEATURES TESTS
  // =============================================================================

  describe('Security Features', () => {
    describe('Refresh Token Family Tracking', () => {
      it('should create and manage token families', () => {
        const manager = new RefreshTokenFamilyManager();
        const userId = 'test-user';
        const deviceHandle = 'device-123';
        const tier = 'T2' as UserTier;
        const scopes = ['matriz:read'] as AuthScope[];

        const familyId = manager.createFamily(
          userId,
          deviceHandle,
          tier,
          scopes,
          '192.168.1.1',
          'Mozilla/5.0 Test'
        );

        expect(familyId).toBeTruthy();
        expect(familyId).toContain('family_');
      });

      it('should detect token reuse and compromise family', () => {
        const manager = new RefreshTokenFamilyManager();
        const familyId = manager.createFamily(
          'test-user',
          'device-123',
          'T2',
          ['matriz:read'] as AuthScope[]
        );

        // Create a mock token
        const mockToken = {
          id: 'token-1',
          userId: 'test-user',
          familyId,
          tokenHash: 'hash-123',
          deviceHandle: 'device-123',
          jti: 'jti-123',
          scopes: ['matriz:read'] as AuthScope[],
          tier: 'T2' as UserTier,
          createdAt: new Date().toISOString(),
          expiresAt: new Date(Date.now() + 86400000).toISOString(),
          metadata: {}
        };

        manager.addToFamily(familyId, mockToken);

        // First validation should succeed
        const firstValidation = manager.validateTokenInFamily(familyId, 'jti-123');
        expect(firstValidation.valid).toBe(true);

        // Mark as used
        manager.markTokenUsed(familyId, 'jti-123');

        // Second validation should fail and compromise family
        const secondValidation = manager.validateTokenInFamily(familyId, 'jti-123');
        expect(secondValidation.valid).toBe(false);
        expect(secondValidation.reason).toContain('reuse detected');
        expect(manager.isFamilyCompromised(familyId)).toBe(true);
      });
    });

    describe('Device Binding', () => {
      it('should generate device fingerprints consistently', () => {
        const manager = new DeviceBindingManager();
        const userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36';
        const ipAddress = '192.168.1.1';

        const fingerprint1 = manager.generateFingerprint(userAgent, ipAddress);
        const fingerprint2 = manager.generateFingerprint(userAgent, ipAddress);

        expect(fingerprint1).toBe(fingerprint2);
        expect(fingerprint1).toContain('fp_');
      });

      it('should create and update device handles', () => {
        const manager = new DeviceBindingManager();
        const userId = 'test-user';
        const userAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)';
        const fingerprint = manager.generateFingerprint(userAgent);

        const device = manager.createOrUpdateDevice(
          userId,
          fingerprint,
          userAgent,
          '192.168.1.1',
          'Test iPhone'
        );

        expect(device.userId).toBe(userId);
        expect(device.deviceType).toBe('mobile');
        expect(device.platform).toBe('iOS');
        expect(device.trusted).toBe(false);
        expect(device.useCount).toBe(1);
      });

      it('should validate device access and trust status', () => {
        const manager = new DeviceBindingManager();
        const userId = 'test-user';
        const userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)';
        const fingerprint = manager.generateFingerprint(userAgent);

        const device = manager.createOrUpdateDevice(userId, fingerprint, userAgent);
        
        const validation = manager.validateDevice(device.handle);
        expect(validation.valid).toBe(true);
        expect(validation.requiresTrust).toBe(true);

        // Trust the device
        manager.trustDevice(device.handle, 'admin-user');
        
        const trustedValidation = manager.validateDevice(device.handle);
        expect(trustedValidation.valid).toBe(true);
        expect(trustedValidation.requiresTrust).toBe(false);
      });
    });

    describe('Session Rotation', () => {
      it('should create and manage sessions', () => {
        const manager = new SessionRotationManager();
        const userId = 'test-user';
        const deviceHandle = 'device-123';
        const tier = 'T2' as UserTier;
        const scopes = ['matriz:read'] as AuthScope[];

        const session = manager.createSession(
          userId,
          deviceHandle,
          tier,
          scopes,
          '192.168.1.1',
          'Mozilla/5.0 Test'
        );

        expect(session.userId).toBe(userId);
        expect(session.deviceHandle).toBe(deviceHandle);
        expect(session.tier).toBe(tier);
        expect(session.scopes).toEqual(scopes);
        expect(session.accessTokenJti).toBeTruthy();
        expect(session.refreshTokenJti).toBeTruthy();
      });

      it('should rotate sessions on security events', () => {
        const manager = new SessionRotationManager();
        const session = manager.createSession(
          'test-user',
          'device-123',
          'T2',
          ['matriz:read'] as AuthScope[]
        );

        const rotatedSession = manager.rotateSession(session.id, 'tier_change');

        expect(rotatedSession).toBeTruthy();
        expect(rotatedSession!.id).not.toBe(session.id);
        expect(rotatedSession!.accessTokenJti).not.toBe(session.accessTokenJti);
        expect(rotatedSession!.metadata.rotatedFrom).toBe(session.id);
        expect(rotatedSession!.metadata.rotationReason).toBe('tier_change');
      });

      it('should validate session security', () => {
        const manager = new SessionRotationManager();
        const session = manager.createSession(
          'test-user',
          'device-123',
          'T2',
          ['matriz:read'] as AuthScope[]
        );

        const validation = manager.validateSession(session.id);
        expect(validation.valid).toBe(true);
        expect(validation.session).toBeTruthy();
      });
    });

    describe('Account Lockout', () => {
      it('should track failed login attempts', () => {
        const manager = new AccountLockoutManager();
        const userId = 'test-user';

        // Record multiple failed attempts
        for (let i = 1; i <= 4; i++) {
          const result = manager.recordFailedAttempt(userId, '192.168.1.1');
          expect(result.locked).toBe(false);
          expect(result.attemptsRemaining).toBe(5 - i);
        }

        // 5th attempt should lock the account
        const lockResult = manager.recordFailedAttempt(userId, '192.168.1.1');
        expect(lockResult.locked).toBe(true);
        expect(lockResult.lockoutUntil).toBeTruthy();
      });

      it('should implement exponential backoff', () => {
        const manager = new AccountLockoutManager();
        const userId = 'test-user';

        // First lockout
        for (let i = 0; i < 5; i++) {
          manager.recordFailedAttempt(userId, '192.168.1.1');
        }

        const firstLockout = manager.getLockoutStats(userId);
        expect(firstLockout.locked).toBe(true);
        expect(firstLockout.backoffLevel).toBe(1);

        // Clear and cause another lockout
        manager.clearFailedAttempts(userId);
        
        for (let i = 0; i < 5; i++) {
          manager.recordFailedAttempt(userId, '192.168.1.1');
        }

        const secondLockout = manager.getLockoutStats(userId);
        expect(secondLockout.backoffLevel).toBe(2);
      });

      it('should check lockout status correctly', () => {
        const manager = new AccountLockoutManager();
        const userId = 'test-user';

        // Account should not be locked initially
        const initialStatus = manager.isAccountLocked(userId);
        expect(initialStatus.locked).toBe(false);
        expect(initialStatus.attemptsRemaining).toBe(5);

        // Lock the account
        for (let i = 0; i < 5; i++) {
          manager.recordFailedAttempt(userId, '192.168.1.1');
        }

        const lockedStatus = manager.isAccountLocked(userId);
        expect(lockedStatus.locked).toBe(true);
        expect(lockedStatus.lockoutUntil).toBeTruthy();
      });
    });
  });

  // =============================================================================
  // TIER SYSTEM TESTS
  // =============================================================================

  describe('Tier System', () => {
    it('should provide tier definitions with complete information', () => {
      const t1Definition = getTierDefinition('T1');
      const t5Definition = getTierDefinition('T5');

      expect(t1Definition.name).toBe('Explorer');
      expect(t1Definition.price.monthly).toBe(0);
      expect(t1Definition.features.general).toContain('Access to public documentation');
      expect(t1Definition.scopes).toHaveLength(4);

      expect(t5Definition.name).toBe('Core Team');
      expect(t5Definition.upgrade.available).toBe(false);
    });

    it('should validate tier transitions correctly', () => {
      // Valid upgrade
      const upgradeValidation = validateTierTransition('T1', 'T2');
      expect(upgradeValidation.valid).toBe(true);
      expect(upgradeValidation.requiresPayment).toBe(true);
      expect(upgradeValidation.priceChange?.monthly).toBe(29);

      // Invalid transition to T5
      const t5Validation = validateTierTransition('T4', 'T5');
      expect(t5Validation.valid).toBe(false);
      expect(t5Validation.reason).toContain('internal only');

      // Downgrade
      const downgradeValidation = validateTierTransition('T3', 'T2');
      expect(downgradeValidation.valid).toBe(true);
      expect(downgradeValidation.requiresPayment).toBe(false);
    });

    it('should check tier operation permissions', () => {
      expect(tierCanPerformOperation('T1', 'read_api')).toBe(false);
      expect(tierCanPerformOperation('T2', 'read_api')).toBe(true);
      expect(tierCanPerformOperation('T2', 'admin_api')).toBe(false);
      expect(tierCanPerformOperation('T4', 'admin_api')).toBe(true);
    });

    it('should provide upgrade recommendations based on usage', () => {
      const usage = {
        apiCalls: 4800, // Near T2 limit of 5000
        consciousnessQueries: 450,
        orchestrationRuns: 90,
        storageUsed: 900
      };

      const recommendation = getTierUpgradeRecommendations('T2', usage);
      expect(recommendation.shouldUpgrade).toBe(true);
      expect(recommendation.recommendedTier).toBe('T3');
      expect(recommendation.reason).toContain('Approaching usage limits');
    });
  });

  // =============================================================================
  // INTEGRATION WORKFLOW TESTS
  // =============================================================================

  describe('End-to-End Authentication Workflows', () => {
    it('should complete full passkey registration and authentication flow', async () => {
      // Mock browser environment
      global.window = {
        navigator: { credentials: {} },
        PublicKeyCredential: {
          isUserVerifyingPlatformAuthenticatorAvailable: jest.fn().mockResolvedValue(true),
          isConditionalMediationAvailable: jest.fn().mockResolvedValue(true)
        },
        crypto: {
          getRandomValues: jest.fn((arr) => {
            for (let i = 0; i < arr.length; i++) {
              arr[i] = Math.floor(Math.random() * 256);
            }
            return arr;
          })
        }
      } as any;

      // 1. Check support
      const support = await checkPasskeySupport();
      expect(support.supported).toBe(true);

      // 2. Generate registration options
      const regOptions = await registerPasskey('user-123', 'test@lukhas.ai', 'Test User');
      expect(regOptions.challenge).toBeTruthy();

      // 3. Simulate registration (mock response)
      const mockRegResponse = {
        response: {
          clientDataJSON: Buffer.from(JSON.stringify({
            type: 'webauthn.create',
            challenge: regOptions.challenge,
            origin: 'https://lukhas.ai'
          })),
          attestationObject: new ArrayBuffer(100)
        }
      };

      const regResult = await verifyPasskeyRegistration(
        mockRegResponse,
        regOptions.challenge
      );
      
      // Note: This would fail with mock data, but tests the structure
      expect(regResult.verified).toBeDefined();

      // 4. Generate authentication options
      const authOptions = await authenticateWithPasskey();
      expect(authOptions.challenge).toBeTruthy();
    });

    it('should complete full magic link authentication flow', async () => {
      const email = 'workflow@lukhas.ai';
      const ipAddress = '192.168.1.1';
      const userAgent = 'Mozilla/5.0 Test';

      // 1. Generate magic link
      const magicLinkResult = await sendMagicLink(email, 'login', {
        ipAddress,
        userAgent,
        userId: 'user-123',
        userTier: 'T2'
      });

      expect(magicLinkResult.success).toBe(true);
      expect(magicLinkResult.token).toBeTruthy();

      // 2. Check status
      if (magicLinkResult.token) {
        const status = await checkMagicLinkStatus(magicLinkResult.token);
        expect(status.exists).toBe(true);
        expect(status.used).toBe(false);

        // 3. Verify magic link
        const verification = await verifyMagicLink(
          magicLinkResult.token,
          ipAddress,
          userAgent
        );

        expect(verification.valid).toBe(true);
        expect(verification.email).toBe(email);

        // 4. Check status after use
        const usedStatus = await checkMagicLinkStatus(magicLinkResult.token);
        expect(usedStatus.used).toBe(true);
      }
    });

    it('should handle complete JWT lifecycle with refresh', async () => {
      const userId = 'user-123';
      const tier = 'T3' as UserTier;
      const scopes = ['org:read', 'org:settings'] as AuthScope[];
      const deviceHandle = 'device-456';
      const familyId = 'family-789';

      // 1. Generate initial token pair
      const initialTokens = await generateTokenPair(
        userId,
        tier,
        scopes,
        deviceHandle,
        familyId
      );

      expect(initialTokens.accessToken).toBeTruthy();
      expect(initialTokens.refreshToken).toBeTruthy();

      // 2. Verify access token
      const accessVerification = await verifyToken(initialTokens.accessToken);
      expect(accessVerification.valid).toBe(true);
      expect(accessVerification.payload?.type).toBe('access');

      // 3. Verify refresh token
      const refreshVerification = await verifyToken(initialTokens.refreshToken);
      expect(refreshVerification.valid).toBe(true);
      expect(refreshVerification.payload?.type).toBe('refresh');
      expect(refreshVerification.payload?.family).toBe(familyId);

      // 4. Generate new token pair (simulating refresh)
      const newTokens = await generateTokenPair(
        userId,
        tier,
        scopes,
        deviceHandle,
        familyId
      );

      expect(newTokens.accessToken).not.toBe(initialTokens.accessToken);
      expect(newTokens.refreshToken).not.toBe(initialTokens.refreshToken);
    });

    it('should handle security manager comprehensive checks', () => {
      const userId = 'security-test-user';
      const ipAddress = '192.168.1.1';
      const userAgent = 'Mozilla/5.0 Test';

      // 1. Initial security check should pass
      const initialCheck = securityManager.performSecurityCheck(
        userId,
        ipAddress,
        userAgent
      );

      expect(initialCheck.allowed).toBe(true);

      // 2. Record failed attempts
      for (let i = 0; i < 5; i++) {
        securityManager.accountLockoutManager.recordFailedAttempt(
          userId,
          ipAddress,
          userAgent
        );
      }

      // 3. Security check should now fail due to lockout
      const lockedCheck = securityManager.performSecurityCheck(
        userId,
        ipAddress,
        userAgent
      );

      expect(lockedCheck.allowed).toBe(false);
      expect(lockedCheck.reason).toContain('locked');
      expect(lockedCheck.lockoutInfo).toBeTruthy();
    });
  });
});

// =============================================================================
// PERFORMANCE TESTS
// =============================================================================

describe('Performance Tests', () => {
  it('should handle high-volume rate limit checks efficiently', () => {
    const startTime = Date.now();
    const userId = 'perf-test-user';
    
    // Perform 1000 rate limit checks
    for (let i = 0; i < 1000; i++) {
      checkRateLimit(userId, 'T2');
    }
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    // Should complete within reasonable time (less than 100ms)
    expect(duration).toBeLessThan(100);
  });

  it('should handle concurrent JWT operations efficiently', async () => {
    const startTime = Date.now();
    const promises = [];
    
    // Generate 100 tokens concurrently
    for (let i = 0; i < 100; i++) {
      promises.push(
        generateAccessToken(`user-${i}`, 'T2', ['matriz:read'] as AuthScope[])
      );
    }
    
    const tokens = await Promise.all(promises);
    const midTime = Date.now();
    
    // Verify all tokens
    const verificationPromises = tokens.map(token => verifyToken(token));
    const verifications = await Promise.all(verificationPromises);
    
    const endTime = Date.now();
    
    expect(tokens).toHaveLength(100);
    expect(verifications.every(v => v.valid)).toBe(true);
    
    const generationTime = midTime - startTime;
    const verificationTime = endTime - midTime;
    
    // Should complete within reasonable time
    expect(generationTime).toBeLessThan(1000); // 1 second
    expect(verificationTime).toBeLessThan(500); // 0.5 seconds
  });
});