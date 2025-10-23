/**
 * LUKHAS AI ΛiD Authentication System - Session Management Unit Tests
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Tests for session creation, validation, rotation, and security features
 */

import { SessionManager, type SessionData, type DeviceInfo } from '@/packages/auth/session';
import crypto from 'crypto';

describe('SessionManager', () => {
  let sessionManager: SessionManager;

  beforeEach(() => {
    sessionManager = new SessionManager({
      sessionTTL: 24 * 60 * 60 * 1000, // 24 hours
      idleTimeout: 30 * 60 * 1000, // 30 minutes
      maxSessions: 5,
      rotateOnTierChange: true,
      rotateOnRoleChange: true,
      deviceBinding: true,
      ipValidation: true,
      userAgentValidation: true,
      securityEvents: true,
    });
  });

  describe('Session Creation', () => {
    it('should create valid session with proper metadata', async () => {
      const userId = 'user1';
      const deviceInfo: DeviceInfo = {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ipAddress: '192.168.1.100',
        fingerprint: 'device-fp-123',
        platform: 'Windows',
        browser: 'Chrome',
      };

      const sessionData: SessionData = {
        userId,
        tier: 'T2',
        scopes: ['matriz:read', 'matriz:write'],
        roles: ['user'],
        organizationId: 'org1',
        metadata: { loginMethod: 'passkey' },
      };

      const session = await sessionManager.createSession(sessionData, deviceInfo);

      expect(session.sessionId).toBeDefined();
      expect(session.sessionToken).toBeDefined();
      expect(session.sessionId).toMatch(/^[a-f0-9]{32}$/); // 32-char hex
      expect(session.sessionToken).toMatch(/^[A-Za-z0-9_-]+$/); // Base64url
      expect(session.expiresAt).toBeInstanceOf(Date);
      expect(session.lastActivityAt).toBeInstanceOf(Date);
      expect(session.deviceInfo).toEqual(deviceInfo);
      expect(session.sessionData).toEqual(sessionData);
    });

    it('should generate unique session identifiers', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'test-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const sessions = await Promise.all(
        Array.from({ length: 100 }, () =>
          sessionManager.createSession(sessionData, deviceInfo)
        )
      );

      const sessionIds = sessions.map(s => s.sessionId);
      const uniqueIds = new Set(sessionIds);
      expect(uniqueIds.size).toBe(sessionIds.length);

      const sessionTokens = sessions.map(s => s.sessionToken);
      const uniqueTokens = new Set(sessionTokens);
      expect(uniqueTokens.size).toBe(sessionTokens.length);
    });

    it('should enforce maximum sessions per user', async () => {
      const userId = 'user1';
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'test-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId,
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      // Create maximum allowed sessions (5)
      const sessions = [];
      for (let i = 0; i < 5; i++) {
        const session = await sessionManager.createSession(
          sessionData,
          { ...deviceInfo, fingerprint: `device-${i}` }
        );
        sessions.push(session);
      }

      // 6th session should trigger cleanup of oldest
      const newSession = await sessionManager.createSession(
        sessionData,
        { ...deviceInfo, fingerprint: 'device-new' }
      );

      expect(newSession).toBeDefined();

      // First session should be invalidated
      const firstSessionValidation = await sessionManager.validateSession(
        sessions[0].sessionToken
      );
      expect(firstSessionValidation.valid).toBe(false);
      expect(firstSessionValidation.reason).toMatch(/limit|expired/i);
    });

    it('should bind sessions to device fingerprints', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'unique-device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const session = await sessionManager.createSession(sessionData, deviceInfo);

      // Validation with same device should work
      const validValidation = await sessionManager.validateSession(
        session.sessionToken,
        deviceInfo
      );
      expect(validValidation.valid).toBe(true);

      // Validation with different device should fail
      const differentDevice: DeviceInfo = {
        ...deviceInfo,
        fingerprint: 'different-device-fp',
      };

      const invalidValidation = await sessionManager.validateSession(
        session.sessionToken,
        differentDevice
      );
      expect(invalidValidation.valid).toBe(false);
      expect(invalidValidation.reason).toMatch(/device|fingerprint/i);
    });
  });

  describe('Session Validation', () => {
    let validSession: any;
    let deviceInfo: DeviceInfo;

    beforeEach(async () => {
      deviceInfo = {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ipAddress: '192.168.1.100',
        fingerprint: 'device-fp-123',
        platform: 'Windows',
        browser: 'Chrome',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T2',
        scopes: ['matriz:read', 'matriz:write'],
        roles: ['user'],
      };

      validSession = await sessionManager.createSession(sessionData, deviceInfo);
    });

    it('should validate active sessions successfully', async () => {
      const validation = await sessionManager.validateSession(
        validSession.sessionToken,
        deviceInfo
      );

      expect(validation.valid).toBe(true);
      expect(validation.session).toBeDefined();
      expect(validation.session!.userId).toBe('user1');
      expect(validation.session!.tier).toBe('T2');
      expect(validation.lastActivity).toBeInstanceOf(Date);
    });

    it('should reject invalid session tokens', async () => {
      const invalidTokens = [
        'invalid-token',
        '',
        'too-short',
        validSession.sessionToken.slice(0, -5) + 'wrong',
        'completely-different-token-that-looks-valid-but-isnt',
      ];

      for (const token of invalidTokens) {
        const validation = await sessionManager.validateSession(token, deviceInfo);
        expect(validation.valid).toBe(false);
        expect(validation.reason).toMatch(/invalid|not found/i);
      }
    });

    it('should reject expired sessions', async () => {
      // Create session manager with very short TTL
      const shortTTLManager = new SessionManager({
        sessionTTL: 100, // 100ms
        idleTimeout: 50,
        maxSessions: 5,
        rotateOnTierChange: false,
        rotateOnRoleChange: false,
        deviceBinding: false,
        ipValidation: false,
        userAgentValidation: false,
        securityEvents: false,
      });

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const session = await shortTTLManager.createSession(sessionData, deviceInfo);

      // Wait for session to expire
      await new Promise(resolve => setTimeout(resolve, 150));

      const validation = await shortTTLManager.validateSession(
        session.sessionToken,
        deviceInfo
      );

      expect(validation.valid).toBe(false);
      expect(validation.reason).toMatch(/expired/i);
    });

    it('should reject sessions after idle timeout', async () => {
      // Create session manager with very short idle timeout
      const shortIdleManager = new SessionManager({
        sessionTTL: 60000, // 1 minute
        idleTimeout: 100, // 100ms
        maxSessions: 5,
        rotateOnTierChange: false,
        rotateOnRoleChange: false,
        deviceBinding: false,
        ipValidation: false,
        userAgentValidation: false,
        securityEvents: false,
      });

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const session = await shortIdleManager.createSession(sessionData, deviceInfo);

      // Wait for idle timeout
      await new Promise(resolve => setTimeout(resolve, 150));

      const validation = await shortIdleManager.validateSession(
        session.sessionToken,
        deviceInfo
      );

      expect(validation.valid).toBe(false);
      expect(validation.reason).toMatch(/idle|timeout/i);
    });

    it('should validate IP address consistency', async () => {
      const validation1 = await sessionManager.validateSession(
        validSession.sessionToken,
        deviceInfo
      );
      expect(validation1.valid).toBe(true);

      // Try with different IP
      const differentIPDevice: DeviceInfo = {
        ...deviceInfo,
        ipAddress: '203.0.113.1',
      };

      const validation2 = await sessionManager.validateSession(
        validSession.sessionToken,
        differentIPDevice
      );

      expect(validation2.valid).toBe(false);
      expect(validation2.reason).toMatch(/ip|address/i);
    });

    it('should validate user agent consistency', async () => {
      const validation1 = await sessionManager.validateSession(
        validSession.sessionToken,
        deviceInfo
      );
      expect(validation1.valid).toBe(true);

      // Try with different user agent
      const differentUADevice: DeviceInfo = {
        ...deviceInfo,
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      };

      const validation2 = await sessionManager.validateSession(
        validSession.sessionToken,
        differentUADevice
      );

      expect(validation2.valid).toBe(false);
      expect(validation2.reason).toMatch(/user.agent|browser/i);
    });

    it('should update last activity on validation', async () => {
      const initialLastActivity = validSession.lastActivityAt;

      // Wait a bit
      await new Promise(resolve => setTimeout(resolve, 10));

      const validation = await sessionManager.validateSession(
        validSession.sessionToken,
        deviceInfo
      );

      expect(validation.valid).toBe(true);
      expect(validation.lastActivity!.getTime()).toBeGreaterThan(
        initialLastActivity.getTime()
      );
    });
  });

  describe('Session Rotation', () => {
    let originalSession: any;
    let deviceInfo: DeviceInfo;

    beforeEach(async () => {
      deviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp-123',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T2',
        scopes: ['matriz:read', 'matriz:write'],
        roles: ['user'],
      };

      originalSession = await sessionManager.createSession(sessionData, deviceInfo);
    });

    it('should rotate session on manual request', async () => {
      const rotationResult = await sessionManager.rotateSession(
        originalSession.sessionToken,
        deviceInfo
      );

      expect(rotationResult.success).toBe(true);
      expect(rotationResult.newSession).toBeDefined();
      expect(rotationResult.newSession!.sessionId).not.toBe(originalSession.sessionId);
      expect(rotationResult.newSession!.sessionToken).not.toBe(originalSession.sessionToken);

      // Old session should be invalidated
      const oldValidation = await sessionManager.validateSession(
        originalSession.sessionToken,
        deviceInfo
      );
      expect(oldValidation.valid).toBe(false);

      // New session should be valid
      const newValidation = await sessionManager.validateSession(
        rotationResult.newSession!.sessionToken,
        deviceInfo
      );
      expect(newValidation.valid).toBe(true);
    });

    it('should rotate session on tier change', async () => {
      // Update user tier
      const updateResult = await sessionManager.updateSessionData(
        originalSession.sessionToken,
        { tier: 'T5' },
        deviceInfo
      );

      expect(updateResult.rotated).toBe(true);
      expect(updateResult.newSession).toBeDefined();

      // Original session should be invalidated
      const validation = await sessionManager.validateSession(
        originalSession.sessionToken,
        deviceInfo
      );
      expect(validation.valid).toBe(false);
    });

    it('should rotate session on role change', async () => {
      // Update user roles
      const updateResult = await sessionManager.updateSessionData(
        originalSession.sessionToken,
        { roles: ['admin'] },
        deviceInfo
      );

      expect(updateResult.rotated).toBe(true);
      expect(updateResult.newSession).toBeDefined();

      // Check new session has updated roles
      const newValidation = await sessionManager.validateSession(
        updateResult.newSession!.sessionToken,
        deviceInfo
      );
      expect(newValidation.session!.roles).toContain('admin');
    });

    it('should maintain session continuity during rotation', async () => {
      const rotationResult = await sessionManager.rotateSession(
        originalSession.sessionToken,
        deviceInfo
      );

      const newSession = rotationResult.newSession!;

      // New session should have same user data but different tokens
      expect(newSession.sessionData.userId).toBe(originalSession.sessionData.userId);
      expect(newSession.sessionData.tier).toBe(originalSession.sessionData.tier);
      expect(newSession.sessionData.scopes).toEqual(originalSession.sessionData.scopes);
      expect(newSession.deviceInfo).toEqual(originalSession.deviceInfo);
    });
  });

  describe('Multi-Session Management', () => {
    it('should track multiple sessions per user', async () => {
      const userId = 'user1';
      const sessions = [];

      for (let i = 0; i < 3; i++) {
        const deviceInfo: DeviceInfo = {
          userAgent: `Browser ${i}`,
          ipAddress: `192.168.1.${100 + i}`,
          fingerprint: `device-${i}`,
          platform: 'Test',
          browser: `Browser${i}`,
        };

        const sessionData: SessionData = {
          userId,
          tier: 'T2',
          scopes: ['matriz:read'],
          roles: ['user'],
        };

        const session = await sessionManager.createSession(sessionData, deviceInfo);
        sessions.push({ session, deviceInfo });
      }

      // All sessions should be valid
      for (const { session, deviceInfo } of sessions) {
        const validation = await sessionManager.validateSession(
          session.sessionToken,
          deviceInfo
        );
        expect(validation.valid).toBe(true);
      }

      // Get all user sessions
      const userSessions = await sessionManager.getUserSessions(userId);
      expect(userSessions).toHaveLength(3);
    });

    it('should revoke specific sessions', async () => {
      const userId = 'user1';
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId,
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const session1 = await sessionManager.createSession(sessionData, deviceInfo);
      const session2 = await sessionManager.createSession(sessionData, {
        ...deviceInfo,
        fingerprint: 'device-fp-2',
      });

      // Revoke first session
      await sessionManager.revokeSession(session1.sessionToken);

      // First session should be invalid
      const validation1 = await sessionManager.validateSession(
        session1.sessionToken,
        deviceInfo
      );
      expect(validation1.valid).toBe(false);

      // Second session should still be valid
      const validation2 = await sessionManager.validateSession(
        session2.sessionToken,
        { ...deviceInfo, fingerprint: 'device-fp-2' }
      );
      expect(validation2.valid).toBe(true);
    });

    it('should revoke all user sessions', async () => {
      const userId = 'user1';
      const sessions = [];

      for (let i = 0; i < 3; i++) {
        const deviceInfo: DeviceInfo = {
          userAgent: 'Test Agent',
          ipAddress: '127.0.0.1',
          fingerprint: `device-${i}`,
          platform: 'Test',
          browser: 'Test',
        };

        const sessionData: SessionData = {
          userId,
          tier: 'T1',
          scopes: ['matriz:read'],
          roles: ['viewer'],
        };

        const session = await sessionManager.createSession(sessionData, deviceInfo);
        sessions.push({ session, deviceInfo });
      }

      // Revoke all sessions for user
      await sessionManager.revokeAllUserSessions(userId);

      // All sessions should be invalid
      for (const { session, deviceInfo } of sessions) {
        const validation = await sessionManager.validateSession(
          session.sessionToken,
          deviceInfo
        );
        expect(validation.valid).toBe(false);
      }
    });
  });

  describe('Security Events and Monitoring', () => {
    it('should log security events for suspicious activity', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const session = await sessionManager.createSession(sessionData, deviceInfo);

      // Try to validate from different IP (suspicious)
      const suspiciousDevice: DeviceInfo = {
        ...deviceInfo,
        ipAddress: '203.0.113.1',
      };

      await sessionManager.validateSession(session.sessionToken, suspiciousDevice);

      // Check security events
      const events = await sessionManager.getSecurityEvents(session.sessionId);
      expect(events.length).toBeGreaterThan(0);

      const suspiciousEvent = events.find(e => e.type === 'ip_mismatch');
      expect(suspiciousEvent).toBeDefined();
      expect(suspiciousEvent!.severity).toBe('warning');
    });

    it('should detect session hijacking attempts', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ipAddress: '192.168.1.100',
        fingerprint: 'device-fp-original',
        platform: 'Windows',
        browser: 'Chrome',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T2',
        scopes: ['matriz:read'],
        roles: ['user'],
      };

      const session = await sessionManager.createSession(sessionData, deviceInfo);

      // Simulate hijacking attempt with different device characteristics
      const hijackingDevice: DeviceInfo = {
        userAgent: 'curl/7.68.0', // Bot user agent
        ipAddress: '198.51.100.1', // Different IP
        fingerprint: 'different-fp', // Different fingerprint
        platform: 'Linux',
        browser: 'curl',
      };

      const validation = await sessionManager.validateSession(
        session.sessionToken,
        hijackingDevice
      );

      expect(validation.valid).toBe(false);
      expect(validation.reason).toMatch(/suspicious|hijack|mismatch/i);

      // Should log security event
      const events = await sessionManager.getSecurityEvents(session.sessionId);
      const hijackEvent = events.find(e => e.type === 'session_hijack_attempt');
      expect(hijackEvent).toBeDefined();
      expect(hijackEvent!.severity).toBe('high');
    });

    it('should implement session lockout after repeated violations', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const session = await sessionManager.createSession(sessionData, deviceInfo);

      // Make multiple suspicious requests
      for (let i = 0; i < 5; i++) {
        await sessionManager.validateSession(session.sessionToken, {
          ...deviceInfo,
          ipAddress: `203.0.113.${i}`,
        });
      }

      // Session should be locked out
      const validation = await sessionManager.validateSession(
        session.sessionToken,
        deviceInfo
      );

      expect(validation.valid).toBe(false);
      expect(validation.reason).toMatch(/locked|suspended/i);
    });
  });

  describe('Session Cleanup and Maintenance', () => {
    it('should clean up expired sessions', async () => {
      // Create session manager with short TTL
      const shortTTLManager = new SessionManager({
        sessionTTL: 100, // 100ms
        idleTimeout: 50,
        maxSessions: 10,
        rotateOnTierChange: false,
        rotateOnRoleChange: false,
        deviceBinding: false,
        ipValidation: false,
        userAgentValidation: false,
        securityEvents: false,
      });

      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      // Create multiple sessions
      const sessions = await Promise.all(
        Array.from({ length: 5 }, () =>
          shortTTLManager.createSession(sessionData, deviceInfo)
        )
      );

      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));

      // Run cleanup
      const cleanupResult = await shortTTLManager.cleanup();
      expect(cleanupResult.cleaned).toBeGreaterThan(0);

      // Sessions should be gone
      for (const session of sessions) {
        const validation = await shortTTLManager.validateSession(
          session.sessionToken,
          deviceInfo
        );
        expect(validation.valid).toBe(false);
      }
    });

    it('should provide session statistics', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      // Create sessions for different users and tiers
      const sessionConfigs = [
        { userId: 'user1', tier: 'T1' as const },
        { userId: 'user2', tier: 'T2' as const },
        { userId: 'user3', tier: 'T5' as const },
      ];

      for (const config of sessionConfigs) {
        const sessionData: SessionData = {
          userId: config.userId,
          tier: config.tier,
          scopes: ['matriz:read'],
          roles: ['user'],
        };

        await sessionManager.createSession(sessionData, deviceInfo);
      }

      const stats = await sessionManager.getStatistics();

      expect(stats.totalSessions).toBe(3);
      expect(stats.activeSessions).toBe(3);
      expect(stats.sessionsByTier.T1).toBe(1);
      expect(stats.sessionsByTier.T2).toBe(1);
      expect(stats.sessionsByTier.T5).toBe(1);
      expect(stats.averageSessionDuration).toBeGreaterThan(0);
    });
  });

  describe('Performance Tests', () => {
    it('should create sessions efficiently', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const iterations = 100;
      const startTime = process.hrtime.bigint();

      for (let i = 0; i < iterations; i++) {
        await sessionManager.createSession(
          { ...sessionData, userId: `user${i}` },
          { ...deviceInfo, fingerprint: `device-${i}` }
        );
      }

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to ms
      const avgTime = duration / iterations;

      // Should create sessions in under 5ms on average
      expect(avgTime).toBeLessThan(5);
    });

    it('should validate sessions efficiently', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      // Create test sessions
      const sessions = await Promise.all(
        Array.from({ length: 100 }, (_, i) =>
          sessionManager.createSession(
            {
              userId: `user${i}`,
              tier: 'T1',
              scopes: ['matriz:read'],
              roles: ['viewer'],
            },
            { ...deviceInfo, fingerprint: `device-${i}` }
          )
        )
      );

      const startTime = process.hrtime.bigint();

      for (let i = 0; i < sessions.length; i++) {
        await sessionManager.validateSession(
          sessions[i].sessionToken,
          { ...deviceInfo, fingerprint: `device-${i}` }
        );
      }

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to ms
      const avgTime = duration / sessions.length;

      // Should validate sessions in under 2ms on average
      expect(avgTime).toBeLessThan(2);
    });

    it('should handle concurrent session operations', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      // Concurrent session creation
      const createPromises = Array.from({ length: 50 }, (_, i) =>
        sessionManager.createSession(
          {
            userId: `user${i}`,
            tier: 'T1',
            scopes: ['matriz:read'],
            roles: ['viewer'],
          },
          { ...deviceInfo, fingerprint: `device-${i}` }
        )
      );

      const sessions = await Promise.all(createPromises);

      // Concurrent session validation
      const validatePromises = sessions.map((session, i) =>
        sessionManager.validateSession(
          session.sessionToken,
          { ...deviceInfo, fingerprint: `device-${i}` }
        )
      );

      const validations = await Promise.all(validatePromises);

      // All operations should succeed
      expect(sessions).toHaveLength(50);
      expect(validations).toHaveLength(50);
      validations.forEach(validation => {
        expect(validation.valid).toBe(true);
      });
    });
  });

  describe('Security Tests', () => {
    it('should resist timing attacks during validation', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const validSession = await sessionManager.createSession(sessionData, deviceInfo);

      const invalidTokens = [
        'invalid-token-123',
        'short',
        validSession.sessionToken.slice(0, -5) + 'wrong',
        crypto.randomBytes(32).toString('base64url'),
      ];

      // Measure validation times
      const validTimes: number[] = [];
      const invalidTimes: number[] = [];

      for (let i = 0; i < 10; i++) {
        // Valid session
        const startValid = process.hrtime.bigint();
        await sessionManager.validateSession(validSession.sessionToken, deviceInfo);
        const endValid = process.hrtime.bigint();
        validTimes.push(Number(endValid - startValid) / 1000000);

        // Invalid sessions
        for (const invalidToken of invalidTokens) {
          const startInvalid = process.hrtime.bigint();
          await sessionManager.validateSession(invalidToken, deviceInfo);
          const endInvalid = process.hrtime.bigint();
          invalidTimes.push(Number(endInvalid - startInvalid) / 1000000);
        }
      }

      // Calculate averages
      const avgValidTime = validTimes.reduce((sum, t) => sum + t, 0) / validTimes.length;
      const avgInvalidTime = invalidTimes.reduce((sum, t) => sum + t, 0) / invalidTimes.length;

      // Timing difference should be minimal to prevent timing attacks
      const timingDifference = Math.abs(avgValidTime - avgInvalidTime);
      const maxAllowedDifference = Math.max(avgValidTime, avgInvalidTime) * 0.5;

      expect(timingDifference).toBeLessThan(maxAllowedDifference);
    });

    it('should generate cryptographically secure session tokens', async () => {
      const deviceInfo: DeviceInfo = {
        userAgent: 'Test Agent',
        ipAddress: '127.0.0.1',
        fingerprint: 'device-fp',
        platform: 'Test',
        browser: 'Test',
      };

      const sessionData: SessionData = {
        userId: 'user1',
        tier: 'T1',
        scopes: ['matriz:read'],
        roles: ['viewer'],
      };

      const sessions = await Promise.all(
        Array.from({ length: 1000 }, (_, i) =>
          sessionManager.createSession(
            { ...sessionData, userId: `user${i}` },
            { ...deviceInfo, fingerprint: `device-${i}` }
          )
        )
      );

      const tokens = sessions.map(s => s.sessionToken);

      // Check for duplicates
      const uniqueTokens = new Set(tokens);
      expect(uniqueTokens.size).toBe(tokens.length);

      // Check token entropy
      const concatenated = tokens.join('');
      const charCounts = new Map<string, number>();

      for (const char of concatenated) {
        charCounts.set(char, (charCounts.get(char) || 0) + 1);
      }

      // Calculate Shannon entropy
      const entropy = Array.from(charCounts.values()).reduce((entropy, count) => {
        const probability = count / concatenated.length;
        return entropy - probability * Math.log2(probability);
      }, 0);

      // Should have high entropy for base64url
      expect(entropy).toBeGreaterThan(5.8);
    });
  });
});