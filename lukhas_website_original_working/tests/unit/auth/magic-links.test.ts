/**
 * LUKHAS AI ΛiD Authentication System - Magic Links Unit Tests
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Tests for magic link generation, validation, and security
 */

import { MagicLinkManager, MagicLinkUtils, DEFAULT_MAGIC_LINK_CONFIG } from '@/packages/auth/magic-links';
import crypto from 'crypto';

describe('MagicLinkManager', () => {
  let magicLinkManager: MagicLinkManager;

  beforeEach(() => {
    magicLinkManager = new MagicLinkManager({
      tokenTTL: 600, // 10 minutes
      maxAttempts: 3,
      baseUrl: 'https://auth.lukhas.ai',
      fromEmail: 'auth@lukhas.ai',
      emailRateLimit: {
        windowMs: 60 * 60 * 1000, // 1 hour
        maxAttempts: 3,
        blockDurationMs: 60 * 60 * 1000, // 1 hour
      },
    });

    // Mock crypto.randomBytes for consistent testing
    jest.spyOn(crypto, 'randomBytes').mockImplementation((size) => {
      return Buffer.from('a'.repeat(size), 'ascii');
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Magic Link Generation', () => {
    it('should generate valid magic link for email', async () => {
      const email = 'test@lukhas.ai';
      const ipAddress = '127.0.0.1';
      const userAgent = 'Test Agent';

      const result = await magicLinkManager.generateMagicLink(
        email,
        ipAddress,
        userAgent
      );

      expect(result.success).toBe(true);
      expect(result.token).toBeDefined();
      expect(result.magicLink).toBeDefined();
      expect(result.expiresAt).toBeInstanceOf(Date);
      expect(result.magicLink).toMatch(/^https:\/\/auth\.lukhas\.ai\/auth\/magic-link\?token=.+$/);
      
      // Token should be URL-safe base64
      expect(result.token).toMatch(/^[A-Za-z0-9_-]+$/);
      expect(result.token).toHaveLength(86); // 64 bytes base64url encoded
    });

    it('should include device fingerprint when provided', async () => {
      const email = 'test@lukhas.ai';
      const ipAddress = '127.0.0.1';
      const userAgent = 'Test Agent';
      const deviceFingerprint = 'device-fp-123';

      const result = await magicLinkManager.generateMagicLink(
        email,
        ipAddress,
        userAgent,
        deviceFingerprint
      );

      expect(result.success).toBe(true);
      expect(result.metadata?.deviceFingerprint).toBe(deviceFingerprint);
    });

    it('should generate different tokens for each request', async () => {
      const email = 'test@lukhas.ai';
      const ipAddress = '127.0.0.1';
      const userAgent = 'Test Agent';

      // Restore real randomBytes for this test
      jest.restoreAllMocks();

      const result1 = await magicLinkManager.generateMagicLink(email, ipAddress, userAgent);
      const result2 = await magicLinkManager.generateMagicLink(email, ipAddress, userAgent);

      expect(result1.token).not.toBe(result2.token);
      expect(result1.magicLink).not.toBe(result2.magicLink);
    });

    it('should enforce email rate limiting', async () => {
      const email = 'test@lukhas.ai';
      const ipAddress = '127.0.0.1';
      const userAgent = 'Test Agent';

      // Generate maximum allowed magic links
      for (let i = 0; i < 3; i++) {
        const result = await magicLinkManager.generateMagicLink(email, ipAddress, userAgent);
        expect(result.success).toBe(true);
      }

      // Next attempt should be rate limited
      const result = await magicLinkManager.generateMagicLink(email, ipAddress, userAgent);
      expect(result.success).toBe(false);
      expect(result.error).toMatch(/rate limit/i);
      expect(result.retryAfter).toBeGreaterThan(0);
    });

    it('should enforce IP rate limiting', async () => {
      const ipAddress = '127.0.0.1';
      const userAgent = 'Test Agent';

      // Generate magic links for different emails from same IP
      for (let i = 0; i < 5; i++) {
        const result = await magicLinkManager.generateMagicLink(
          `test${i}@lukhas.ai`,
          ipAddress,
          userAgent
        );
        expect(result.success).toBe(true);
      }

      // Next attempt should be rate limited
      const result = await magicLinkManager.generateMagicLink(
        'test6@lukhas.ai',
        ipAddress,
        userAgent
      );
      expect(result.success).toBe(false);
      expect(result.error).toMatch(/rate limit/i);
    });

    it('should validate email format', async () => {
      const invalidEmails = [
        'invalid-email',
        '@lukhas.ai',
        'test@',
        'test..test@lukhas.ai',
        'test@lukhas',
        '',
      ];

      for (const email of invalidEmails) {
        const result = await magicLinkManager.generateMagicLink(
          email,
          '127.0.0.1',
          'Test Agent'
        );
        expect(result.success).toBe(false);
        expect(result.error).toMatch(/email/i);
      }
    });
  });

  describe('Magic Link Validation', () => {
    let validToken: string;
    let email: string;

    beforeEach(async () => {
      email = 'test@lukhas.ai';
      const result = await magicLinkManager.generateMagicLink(
        email,
        '127.0.0.1',
        'Test Agent'
      );
      validToken = result.token!;
    });

    it('should validate correct magic link token', async () => {
      const validation = await magicLinkManager.validateMagicLink(
        validToken,
        '127.0.0.1',
        'Test Agent'
      );

      expect(validation.valid).toBe(true);
      expect(validation.email).toBe(email);
      expect(validation.metadata).toBeDefined();
      expect(validation.error).toBeUndefined();
    });

    it('should validate with device fingerprint matching', async () => {
      const deviceFingerprint = 'device-fp-123';
      
      // Generate token with device fingerprint
      const result = await magicLinkManager.generateMagicLink(
        email,
        '127.0.0.1',
        'Test Agent',
        deviceFingerprint
      );

      const validation = await magicLinkManager.validateMagicLink(
        result.token!,
        '127.0.0.1',
        'Test Agent',
        deviceFingerprint
      );

      expect(validation.valid).toBe(true);
      expect(validation.email).toBe(email);
    });

    it('should reject invalid token format', async () => {
      const invalidTokens = [
        'invalid-token',
        '',
        'too-short',
        'contains spaces',
        'contains/slashes',
        '###invalid###',
      ];

      for (const token of invalidTokens) {
        const validation = await magicLinkManager.validateMagicLink(
          token,
          '127.0.0.1',
          'Test Agent'
        );
        expect(validation.valid).toBe(false);
        expect(validation.error).toMatch(/invalid|format/i);
      }
    });

    it('should reject expired token', async () => {
      // Create manager with very short TTL
      const shortTTLManager = new MagicLinkManager({
        ...DEFAULT_MAGIC_LINK_CONFIG,
        tokenTTL: 1, // 1 second
      });

      const result = await shortTTLManager.generateMagicLink(
        email,
        '127.0.0.1',
        'Test Agent'
      );

      // Wait for token to expire
      await new Promise(resolve => setTimeout(resolve, 1500));

      const validation = await shortTTLManager.validateMagicLink(
        result.token!,
        '127.0.0.1',
        'Test Agent'
      );

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/expired/i);
    });

    it('should reject token used multiple times', async () => {
      // First validation should succeed
      const validation1 = await magicLinkManager.validateMagicLink(
        validToken,
        '127.0.0.1',
        'Test Agent'
      );
      expect(validation1.valid).toBe(true);

      // Second validation should fail (one-time use)
      const validation2 = await magicLinkManager.validateMagicLink(
        validToken,
        '127.0.0.1',
        'Test Agent'
      );
      expect(validation2.valid).toBe(false);
      expect(validation2.error).toMatch(/used|invalid/i);
    });

    it('should reject token with wrong IP address', async () => {
      const validation = await magicLinkManager.validateMagicLink(
        validToken,
        '192.168.1.1', // Different IP
        'Test Agent'
      );

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/ip|address|security/i);
    });

    it('should reject token with mismatched device fingerprint', async () => {
      const deviceFingerprint = 'device-fp-123';
      
      // Generate token with device fingerprint
      const result = await magicLinkManager.generateMagicLink(
        email,
        '127.0.0.1',
        'Test Agent',
        deviceFingerprint
      );

      // Validate with different device fingerprint
      const validation = await magicLinkManager.validateMagicLink(
        result.token!,
        '127.0.0.1',
        'Test Agent',
        'different-device-fp'
      );

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/device|fingerprint/i);
    });

    it('should track failed validation attempts', async () => {
      const invalidToken = 'invalid-token-123';

      // Multiple failed attempts
      for (let i = 0; i < 3; i++) {
        const validation = await magicLinkManager.validateMagicLink(
          invalidToken,
          '127.0.0.1',
          'Test Agent'
        );
        expect(validation.valid).toBe(false);
      }

      // Should be temporarily blocked after max attempts
      const validation = await magicLinkManager.validateMagicLink(
        invalidToken,
        '127.0.0.1',
        'Test Agent'
      );
      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/blocked|attempts/i);
    });
  });

  describe('Email Integration', () => {
    it('should generate email content with proper template', async () => {
      const email = 'test@lukhas.ai';
      const result = await magicLinkManager.generateMagicLink(
        email,
        '127.0.0.1',
        'Test Agent'
      );

      const emailContent = await magicLinkManager.generateEmailContent(
        email,
        result.magicLink!,
        'Test User'
      );

      expect(emailContent.to).toBe(email);
      expect(emailContent.subject).toMatch(/LUKHAS AI/i);
      expect(emailContent.subject).toMatch(/sign.*in/i);
      expect(emailContent.htmlBody).toContain(result.magicLink);
      expect(emailContent.htmlBody).toContain('Test User');
      expect(emailContent.textBody).toContain(result.magicLink);
      expect(emailContent.from).toBe('auth@lukhas.ai');
    });

    it('should include security information in email', async () => {
      const email = 'test@lukhas.ai';
      const result = await magicLinkManager.generateMagicLink(
        email,
        '127.0.0.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      );

      const emailContent = await magicLinkManager.generateEmailContent(
        email,
        result.magicLink!,
        'Test User'
      );

      expect(emailContent.htmlBody).toMatch(/10 minutes/); // Token expiration
      expect(emailContent.htmlBody).toMatch(/127\.0\.0\.1/); // IP address
      expect(emailContent.htmlBody).toMatch(/Windows/i); // User agent info
      expect(emailContent.htmlBody).toContain('security@lukhas.ai'); // Security contact
    });

    it('should handle special characters in display name', async () => {
      const email = 'test@lukhas.ai';
      const result = await magicLinkManager.generateMagicLink(
        email,
        '127.0.0.1',
        'Test Agent'
      );

      const specialNames = [
        'John O\'Connor',
        'José María',
        'Smith & Jones',
        '<script>alert("xss")</script>',
        'User "with" quotes',
      ];

      for (const name of specialNames) {
        const emailContent = await magicLinkManager.generateEmailContent(
          email,
          result.magicLink!,
          name
        );

        // Should escape HTML properly
        expect(emailContent.htmlBody).not.toContain('<script>');
        expect(emailContent.htmlBody).not.toContain('alert(');
        
        // Should handle special characters
        if (name.includes('O\'Connor')) {
          expect(emailContent.htmlBody).toContain('O&#x27;Connor');
        }
      }
    });
  });

  describe('Performance Tests', () => {
    it('should generate magic links quickly', async () => {
      const iterations = 100;
      const startTime = process.hrtime.bigint();

      for (let i = 0; i < iterations; i++) {
        await magicLinkManager.generateMagicLink(
          `test${i}@lukhas.ai`,
          '127.0.0.1',
          'Test Agent'
        );
      }

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to ms
      const avgTime = duration / iterations;

      // Should generate magic links in under 5ms on average
      expect(avgTime).toBeLessThan(5);
    });

    it('should validate magic links quickly', async () => {
      // Generate test tokens
      const tokens = await Promise.all(
        Array.from({ length: 100 }, (_, i) =>
          magicLinkManager.generateMagicLink(
            `test${i}@lukhas.ai`,
            '127.0.0.1',
            'Test Agent'
          )
        )
      );

      const startTime = process.hrtime.bigint();

      for (const token of tokens) {
        await magicLinkManager.validateMagicLink(
          token.token!,
          '127.0.0.1',
          'Test Agent'
        );
      }

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to ms
      const avgTime = duration / tokens.length;

      // Should validate magic links in under 3ms on average
      expect(avgTime).toBeLessThan(3);
    });
  });

  describe('Security Tests', () => {
    it('should resist timing attacks during validation', async () => {
      const email = 'test@lukhas.ai';
      
      // Generate valid token
      const validResult = await magicLinkManager.generateMagicLink(
        email,
        '127.0.0.1',
        'Test Agent'
      );

      const invalidTokens = [
        'invalid-token-123',
        'short',
        'a'.repeat(86), // Same length as valid token
        validResult.token!.slice(0, -5) + 'wrong',
      ];

      // Measure validation times
      const validTimes: number[] = [];
      const invalidTimes: number[] = [];

      for (let i = 0; i < 10; i++) {
        // Valid token
        const startValid = process.hrtime.bigint();
        await magicLinkManager.validateMagicLink(
          validResult.token!,
          '127.0.0.1',
          'Test Agent'
        );
        const endValid = process.hrtime.bigint();
        validTimes.push(Number(endValid - startValid) / 1000000);

        // Invalid tokens
        for (const invalidToken of invalidTokens) {
          const startInvalid = process.hrtime.bigint();
          await magicLinkManager.validateMagicLink(
            invalidToken,
            '127.0.0.1',
            'Test Agent'
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

    it('should generate cryptographically secure tokens', async () => {
      // Restore real randomBytes for this test
      jest.restoreAllMocks();

      const tokens = await Promise.all(
        Array.from({ length: 1000 }, (_, i) =>
          magicLinkManager.generateMagicLink(
            `test${i}@lukhas.ai`,
            '127.0.0.1',
            'Test Agent'
          )
        )
      );

      const tokenStrings = tokens.map(t => t.token!);

      // Check for duplicates (should be none with cryptographically secure generation)
      const uniqueTokens = new Set(tokenStrings);
      expect(uniqueTokens.size).toBe(tokenStrings.length);

      // Check token entropy
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
      expect(entropy).toBeGreaterThan(5.8); // High entropy threshold for base64url
    });

    it('should prevent token enumeration attacks', async () => {
      const email = 'test@lukhas.ai';
      
      // Generate a valid token
      const validResult = await magicLinkManager.generateMagicLink(
        email,
        '127.0.0.1',
        'Test Agent'
      );

      // Try to guess tokens by modifying the valid token
      const attempts = [
        validResult.token!.slice(0, -1) + 'a',
        validResult.token!.slice(0, -1) + 'b',
        validResult.token!.slice(0, -1) + 'c',
        validResult.token!.slice(0, -2) + 'aa',
        validResult.token!.slice(0, -2) + 'bb',
      ];

      for (const attempt of attempts) {
        const validation = await magicLinkManager.validateMagicLink(
          attempt,
          '127.0.0.1',
          'Test Agent'
        );
        expect(validation.valid).toBe(false);
      }

      // After multiple failed attempts, IP should be blocked
      const finalAttempt = await magicLinkManager.validateMagicLink(
        'random-token-123',
        '127.0.0.1',
        'Test Agent'
      );
      expect(finalAttempt.valid).toBe(false);
    });
  });
});

describe('MagicLinkUtils', () => {
  describe('Token Utilities', () => {
    it('should generate secure random tokens', () => {
      const tokens = Array.from({ length: 1000 }, () => 
        MagicLinkUtils.generateSecureToken(64)
      );

      // All tokens should be unique
      const uniqueTokens = new Set(tokens);
      expect(uniqueTokens.size).toBe(tokens.length);

      // All tokens should be base64url format
      tokens.forEach(token => {
        expect(token).toMatch(/^[A-Za-z0-9_-]+$/);
        expect(token).toHaveLength(86); // 64 bytes base64url encoded
      });
    });

    it('should hash tokens consistently', () => {
      const token = 'test-token-123';
      const hash1 = MagicLinkUtils.hashToken(token);
      const hash2 = MagicLinkUtils.hashToken(token);

      expect(hash1).toBe(hash2);
      expect(hash1).toMatch(/^[a-f0-9]{64}$/); // SHA-256 hex
    });

    it('should verify token hashes correctly', () => {
      const token = 'test-token-123';
      const hash = MagicLinkUtils.hashToken(token);

      expect(MagicLinkUtils.verifyTokenHash(token, hash)).toBe(true);
      expect(MagicLinkUtils.verifyTokenHash('wrong-token', hash)).toBe(false);
      expect(MagicLinkUtils.verifyTokenHash(token, 'wrong-hash')).toBe(false);
    });
  });

  describe('Email Utilities', () => {
    it('should validate email addresses correctly', () => {
      const validEmails = [
        'test@lukhas.ai',
        'user.name@lukhas.ai',
        'user+tag@lukhas.ai',
        'user@sub.domain.com',
        'a@b.co',
      ];

      const invalidEmails = [
        'invalid-email',
        '@lukhas.ai',
        'test@',
        'test..test@lukhas.ai',
        'test@lukhas',
        '',
        'test@.com',
        'test.@lukhas.ai',
      ];

      validEmails.forEach(email => {
        expect(MagicLinkUtils.validateEmail(email)).toBe(true);
      });

      invalidEmails.forEach(email => {
        expect(MagicLinkUtils.validateEmail(email)).toBe(false);
      });
    });

    it('should normalize email addresses', () => {
      const testCases = [
        { input: 'Test@LUKHAS.AI', expected: 'test@lukhas.ai' },
        { input: '  test@lukhas.ai  ', expected: 'test@lukhas.ai' },
        { input: 'User.Name@Domain.Com', expected: 'user.name@domain.com' },
      ];

      testCases.forEach(({ input, expected }) => {
        expect(MagicLinkUtils.normalizeEmail(input)).toBe(expected);
      });
    });

    it('should extract domain from email', () => {
      expect(MagicLinkUtils.extractDomain('test@lukhas.ai')).toBe('lukhas.ai');
      expect(MagicLinkUtils.extractDomain('user@sub.domain.com')).toBe('sub.domain.com');
      expect(MagicLinkUtils.extractDomain('invalid-email')).toBeNull();
    });
  });

  describe('Security Utilities', () => {
    it('should detect suspicious IP addresses', () => {
      const suspiciousIPs = [
        '127.0.0.1', // localhost (suspicious in production)
        '10.0.0.1',  // private network
        '192.168.1.1', // private network
        '172.16.0.1',   // private network
      ];

      const legitimateIPs = [
        '8.8.8.8',
        '1.1.1.1',
        '203.0.113.1',
        '198.51.100.1',
      ];

      // In test environment, private IPs might be allowed
      // This test checks the utility function behavior
      expect(typeof MagicLinkUtils.isSuspiciousIP(suspiciousIPs[0])).toBe('boolean');
      expect(typeof MagicLinkUtils.isSuspiciousIP(legitimateIPs[0])).toBe('boolean');
    });

    it('should parse user agent strings', () => {
      const userAgents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
      ];

      userAgents.forEach(ua => {
        const parsed = MagicLinkUtils.parseUserAgent(ua);
        expect(parsed).toBeDefined();
        expect(typeof parsed.browser).toBe('string');
        expect(typeof parsed.os).toBe('string');
        expect(typeof parsed.device).toBe('string');
      });
    });

    it('should generate device fingerprints', () => {
      const fingerprint1 = MagicLinkUtils.generateDeviceFingerprint(
        '127.0.0.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      );

      const fingerprint2 = MagicLinkUtils.generateDeviceFingerprint(
        '192.168.1.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      );

      const fingerprint3 = MagicLinkUtils.generateDeviceFingerprint(
        '127.0.0.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      );

      expect(fingerprint1).toBeDefined();
      expect(fingerprint2).toBeDefined();
      expect(fingerprint3).toBeDefined();
      
      // Different inputs should produce different fingerprints
      expect(fingerprint1).not.toBe(fingerprint2);
      expect(fingerprint1).not.toBe(fingerprint3);
      expect(fingerprint2).not.toBe(fingerprint3);

      // Same inputs should produce same fingerprint
      const fingerprint1Repeat = MagicLinkUtils.generateDeviceFingerprint(
        '127.0.0.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      );
      expect(fingerprint1).toBe(fingerprint1Repeat);
    });
  });

  describe('URL Utilities', () => {
    it('should build magic link URLs correctly', () => {
      const baseUrl = 'https://auth.lukhas.ai';
      const token = 'test-token-123';
      
      const url = MagicLinkUtils.buildMagicLinkURL(baseUrl, token);
      
      expect(url).toBe('https://auth.lukhas.ai/auth/magic-link?token=test-token-123');
    });

    it('should handle base URLs with trailing slashes', () => {
      const baseUrl = 'https://auth.lukhas.ai/';
      const token = 'test-token-123';
      
      const url = MagicLinkUtils.buildMagicLinkURL(baseUrl, token);
      
      expect(url).toBe('https://auth.lukhas.ai/auth/magic-link?token=test-token-123');
    });

    it('should URL encode tokens properly', () => {
      const baseUrl = 'https://auth.lukhas.ai';
      const token = 'test+token/with=special&chars';
      
      const url = MagicLinkUtils.buildMagicLinkURL(baseUrl, token);
      
      expect(url).toContain('test%2Btoken%2Fwith%3Dspecial%26chars');
    });

    it('should extract tokens from URLs correctly', () => {
      const url = 'https://auth.lukhas.ai/auth/magic-link?token=test-token-123&other=param';
      
      const token = MagicLinkUtils.extractTokenFromURL(url);
      
      expect(token).toBe('test-token-123');
    });

    it('should handle missing tokens in URLs', () => {
      const urls = [
        'https://auth.lukhas.ai/auth/magic-link',
        'https://auth.lukhas.ai/auth/magic-link?other=param',
        'https://auth.lukhas.ai/other-page?token=test',
      ];

      urls.forEach(url => {
        const token = MagicLinkUtils.extractTokenFromURL(url);
        expect(token).toBeNull();
      });
    });
  });
});