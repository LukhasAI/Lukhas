/**
 * LUKHAS AI ΛiD Authentication System - Rate Limiting Unit Tests
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Tests for tier-based rate limiting, burst protection, and adaptive throttling
 */

import { 
  RateLimitManager, 
  RateLimitUtils, 
  DEFAULT_RATE_LIMIT_CONFIG,
  type RateLimitContext,
  type RateLimitResult 
} from '@/packages/auth/rate-limits';

describe('RateLimitManager', () => {
  let rateLimitManager: RateLimitManager;

  beforeEach(() => {
    rateLimitManager = new RateLimitManager({
      enabled: true,
      strictMode: false,
      alertThreshold: 0.8,
      blockDuration: 60 * 1000, // 1 minute
      rules: {
        T1: { rpm: 30, burst: 5, window: 60000 },
        T2: { rpm: 100, burst: 10, window: 60000 },
        T3: { rpm: 300, burst: 20, window: 60000 },
        T4: { rpm: 500, burst: 30, window: 60000 },
        T5: { rpm: 1000, burst: 50, window: 60000 },
        auth: { rpm: 10, burst: 3, window: 300000 }, // 5 minutes for auth
        email: { rpm: 3, burst: 1, window: 3600000 }, // 1 hour for emails
      },
    });
  });

  describe('Tier-based Rate Limiting', () => {
    it('should enforce T1 tier limits (30 RPM)', async () => {
      const context: RateLimitContext = {
        userId: 'user1',
        userTier: 'T1',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // T1 allows 30 requests per minute (0.5 per second)
      // Send 5 requests rapidly (within burst limit)
      for (let i = 0; i < 5; i++) {
        const result = await rateLimitManager.checkRateLimit(context);
        expect(result.allowed).toBe(true);
        expect(result.tier).toBe('T1');
        expect(result.limit).toBe(30);
      }

      // 6th request should be blocked (exceeds burst)
      const result = await rateLimitManager.checkRateLimit(context);
      expect(result.allowed).toBe(false);
      expect(result.retryAfter).toBeGreaterThan(0);
    });

    it('should enforce T2 tier limits (100 RPM)', async () => {
      const context: RateLimitContext = {
        userId: 'user2',
        userTier: 'T2',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // T2 allows 100 requests per minute with burst of 10
      for (let i = 0; i < 10; i++) {
        const result = await rateLimitManager.checkRateLimit(context);
        expect(result.allowed).toBe(true);
        expect(result.tier).toBe('T2');
        expect(result.limit).toBe(100);
      }

      // 11th request should be blocked
      const result = await rateLimitManager.checkRateLimit(context);
      expect(result.allowed).toBe(false);
    });

    it('should enforce T5 tier limits (1000 RPM)', async () => {
      const context: RateLimitContext = {
        userId: 'user5',
        userTier: 'T5',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // T5 allows 1000 requests per minute with burst of 50
      for (let i = 0; i < 50; i++) {
        const result = await rateLimitManager.checkRateLimit(context);
        expect(result.allowed).toBe(true);
        expect(result.tier).toBe('T5');
        expect(result.limit).toBe(1000);
      }

      // 51st request should be blocked
      const result = await rateLimitManager.checkRateLimit(context);
      expect(result.allowed).toBe(false);
    });
  });

  describe('Endpoint-specific Rate Limiting', () => {
    it('should enforce stricter limits for auth endpoints', async () => {
      const authContext: RateLimitContext = {
        userId: 'user1',
        userTier: 'T3',
        ipAddress: '127.0.0.1',
        endpoint: '/auth/login',
        method: 'POST',
        userAgent: 'Test Agent',
      };

      // Auth endpoints have stricter limits (10 RPM, burst 3)
      for (let i = 0; i < 3; i++) {
        const result = await rateLimitManager.checkRateLimit(authContext);
        expect(result.allowed).toBe(true);
        expect(result.ruleType).toBe('auth');
      }

      // 4th auth request should be blocked
      const result = await rateLimitManager.checkRateLimit(authContext);
      expect(result.allowed).toBe(false);
      expect(result.retryAfter).toBeGreaterThan(0);
    });

    it('should enforce email rate limits', async () => {
      const emailContext: RateLimitContext = {
        userId: 'user1',
        userTier: 'T2',
        ipAddress: '127.0.0.1',
        endpoint: '/auth/magic-link',
        method: 'POST',
        userAgent: 'Test Agent',
      };

      // Email endpoints have very strict limits (3 RPM, burst 1)
      const firstResult = await rateLimitManager.checkRateLimit(emailContext);
      expect(firstResult.allowed).toBe(true);
      expect(firstResult.ruleType).toBe('email');

      // 2nd email request should be blocked
      const secondResult = await rateLimitManager.checkRateLimit(emailContext);
      expect(secondResult.allowed).toBe(false);
      expect(secondResult.retryAfter).toBeGreaterThan(0);
    });

    it('should prioritize most restrictive rule', async () => {
      const context: RateLimitContext = {
        userId: 'user5', // T5 user (high limits)
        userTier: 'T5',
        ipAddress: '127.0.0.1',
        endpoint: '/auth/magic-link', // Email endpoint (strict limits)
        method: 'POST',
        userAgent: 'Test Agent',
      };

      // Should use email limits (stricter) not T5 limits
      const result = await rateLimitManager.checkRateLimit(context);
      expect(result.allowed).toBe(true);
      expect(result.ruleType).toBe('email');
      expect(result.limit).toBe(3); // Email limit, not T5 limit
    });
  });

  describe('IP-based Rate Limiting', () => {
    it('should track requests per IP address', async () => {
      const ip1Context: RateLimitContext = {
        userId: 'user1',
        userTier: 'T1',
        ipAddress: '192.168.1.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      const ip2Context: RateLimitContext = {
        userId: 'user2',
        userTier: 'T1',
        ipAddress: '192.168.1.2',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // Different IPs should have separate limits
      for (let i = 0; i < 5; i++) {
        const result1 = await rateLimitManager.checkRateLimit(ip1Context);
        const result2 = await rateLimitManager.checkRateLimit(ip2Context);
        expect(result1.allowed).toBe(true);
        expect(result2.allowed).toBe(true);
      }

      // Both IPs should be blocked after burst limit
      const result1 = await rateLimitManager.checkRateLimit(ip1Context);
      const result2 = await rateLimitManager.checkRateLimit(ip2Context);
      expect(result1.allowed).toBe(false);
      expect(result2.allowed).toBe(false);
    });

    it('should block suspicious IPs', async () => {
      const suspiciousContext: RateLimitContext = {
        userId: 'user1',
        userTier: 'T1',
        ipAddress: '127.0.0.1', // Localhost might be suspicious in production
        endpoint: '/auth/login',
        method: 'POST',
        userAgent: 'Test Agent',
      };

      // First request might be allowed
      const firstResult = await rateLimitManager.checkRateLimit(suspiciousContext);
      
      // But subsequent rapid requests should trigger IP-based blocking
      for (let i = 0; i < 10; i++) {
        await rateLimitManager.checkRateLimit(suspiciousContext);
      }

      const finalResult = await rateLimitManager.checkRateLimit(suspiciousContext);
      expect(finalResult.allowed).toBe(false);
    });
  });

  describe('User Agent and Device Tracking', () => {
    it('should track requests per user agent', async () => {
      const botContext: RateLimitContext = {
        userId: 'user1',
        userTier: 'T2',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Bot/1.0 (Automated)',
      };

      const humanContext: RateLimitContext = {
        userId: 'user1',
        userTier: 'T2',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      };

      // Bot should be more restricted
      const botResult = await rateLimitManager.checkRateLimit(botContext);
      const humanResult = await rateLimitManager.checkRateLimit(humanContext);

      // Both should work initially, but bot might have different limits
      expect(botResult.allowed).toBe(true);
      expect(humanResult.allowed).toBe(true);
    });

    it('should detect and limit automated requests', async () => {
      const automatedContext: RateLimitContext = {
        userId: 'user1',
        userTier: 'T2',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'curl/7.68.0',
      };

      // Make many rapid requests to simulate automation
      let blockedCount = 0;
      for (let i = 0; i < 20; i++) {
        const result = await rateLimitManager.checkRateLimit(automatedContext);
        if (!result.allowed) {
          blockedCount++;
        }
      }

      // Should block some requests due to automated pattern detection
      expect(blockedCount).toBeGreaterThan(0);
    });
  });

  describe('Adaptive Rate Limiting', () => {
    it('should adjust limits based on system load', async () => {
      const context: RateLimitContext = {
        userId: 'user1',
        userTier: 'T2',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // Simulate high system load
      rateLimitManager.setSystemLoad(0.9);

      const highLoadResult = await rateLimitManager.checkRateLimit(context);
      
      // Reset to normal load
      rateLimitManager.setSystemLoad(0.3);

      const normalLoadResult = await rateLimitManager.checkRateLimit(context);

      // Limits should be stricter under high load
      expect(highLoadResult.adjustedLimit).toBeLessThan(normalLoadResult.adjustedLimit || 100);
    });

    it('should implement backoff for repeated violations', async () => {
      const context: RateLimitContext = {
        userId: 'user1',
        userTier: 'T1',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // Trigger rate limit violation
      for (let i = 0; i < 10; i++) {
        await rateLimitManager.checkRateLimit(context);
      }

      const firstViolation = await rateLimitManager.checkRateLimit(context);
      expect(firstViolation.allowed).toBe(false);

      const firstRetryAfter = firstViolation.retryAfter;

      // Continue violating to trigger increased backoff
      for (let i = 0; i < 5; i++) {
        await rateLimitManager.checkRateLimit(context);
      }

      const subsequentViolation = await rateLimitManager.checkRateLimit(context);
      expect(subsequentViolation.retryAfter).toBeGreaterThan(firstRetryAfter!);
    });
  });

  describe('Rate Limit Recovery', () => {
    it('should reset limits after window expires', async () => {
      // Create manager with short window for testing
      const shortWindowManager = new RateLimitManager({
        ...DEFAULT_RATE_LIMIT_CONFIG,
        rules: {
          T1: { rpm: 30, burst: 2, window: 1000 }, // 1 second window
        },
      });

      const context: RateLimitContext = {
        userId: 'user1',
        userTier: 'T1',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // Exhaust burst limit
      for (let i = 0; i < 2; i++) {
        const result = await shortWindowManager.checkRateLimit(context);
        expect(result.allowed).toBe(true);
      }

      // Next request should be blocked
      const blockedResult = await shortWindowManager.checkRateLimit(context);
      expect(blockedResult.allowed).toBe(false);

      // Wait for window to reset
      await new Promise(resolve => setTimeout(resolve, 1100));

      // Should be allowed again
      const recoveredResult = await shortWindowManager.checkRateLimit(context);
      expect(recoveredResult.allowed).toBe(true);
    });

    it('should implement graceful degradation during recovery', async () => {
      const context: RateLimitContext = {
        userId: 'user1',
        userTier: 'T1',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // Trigger rate limit
      for (let i = 0; i < 10; i++) {
        await rateLimitManager.checkRateLimit(context);
      }

      // Should be blocked
      const blockedResult = await rateLimitManager.checkRateLimit(context);
      expect(blockedResult.allowed).toBe(false);

      // Simulate partial recovery period
      await new Promise(resolve => setTimeout(resolve, 100));

      // Should still be blocked but with reduced penalty
      const partialRecoveryResult = await rateLimitManager.checkRateLimit(context);
      expect(partialRecoveryResult.allowed).toBe(false);
      expect(partialRecoveryResult.retryAfter).toBeLessThan(blockedResult.retryAfter!);
    });
  });

  describe('Rate Limit Monitoring and Alerts', () => {
    it('should track rate limit metrics', async () => {
      const context: RateLimitContext = {
        userId: 'user1',
        userTier: 'T1',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // Make several requests
      for (let i = 0; i < 15; i++) {
        await rateLimitManager.checkRateLimit(context);
      }

      const metrics = await rateLimitManager.getMetrics();

      expect(metrics.totalRequests).toBeGreaterThan(0);
      expect(metrics.blockedRequests).toBeGreaterThan(0);
      expect(metrics.allowedRequests).toBeGreaterThan(0);
      expect(metrics.blockRate).toBeGreaterThan(0);
      expect(metrics.averageRetryAfter).toBeGreaterThan(0);
    });

    it('should trigger alerts at threshold', async () => {
      const alertSpy = jest.fn();
      rateLimitManager.onAlert(alertSpy);

      const context: RateLimitContext = {
        userId: 'user1',
        userTier: 'T1',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      // Trigger many violations to reach alert threshold
      for (let i = 0; i < 20; i++) {
        await rateLimitManager.checkRateLimit(context);
      }

      // Should trigger alert when block rate exceeds threshold (80%)
      expect(alertSpy).toHaveBeenCalled();
    });

    it('should provide rate limit analytics', async () => {
      const contexts = [
        { userId: 'user1', userTier: 'T1' as const, ipAddress: '127.0.0.1' },
        { userId: 'user2', userTier: 'T2' as const, ipAddress: '127.0.0.2' },
        { userId: 'user3', userTier: 'T5' as const, ipAddress: '127.0.0.3' },
      ];

      // Generate diverse traffic
      for (const base of contexts) {
        for (let i = 0; i < 10; i++) {
          await rateLimitManager.checkRateLimit({
            ...base,
            endpoint: '/api/matriz',
            method: 'GET',
            userAgent: 'Test Agent',
          });
        }
      }

      const analytics = await rateLimitManager.getAnalytics();

      expect(analytics.requestsByTier.T1).toBeGreaterThan(0);
      expect(analytics.requestsByTier.T2).toBeGreaterThan(0);
      expect(analytics.requestsByTier.T5).toBeGreaterThan(0);
      expect(analytics.topEndpoints).toBeDefined();
      expect(analytics.topIPs).toBeDefined();
    });
  });

  describe('Performance Tests', () => {
    it('should process rate limit checks quickly', async () => {
      const context: RateLimitContext = {
        userId: 'user1',
        userTier: 'T2',
        ipAddress: '127.0.0.1',
        endpoint: '/api/matriz',
        method: 'GET',
        userAgent: 'Test Agent',
      };

      const iterations = 1000;
      const startTime = process.hrtime.bigint();

      for (let i = 0; i < iterations; i++) {
        await rateLimitManager.checkRateLimit({
          ...context,
          userId: `user${i}`, // Different users to avoid rate limiting
        });
      }

      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000; // Convert to ms
      const avgTime = duration / iterations;

      // Should process rate limit checks in under 1ms on average
      expect(avgTime).toBeLessThan(1);
    });

    it('should handle concurrent rate limit checks', async () => {
      const promises = Array.from({ length: 100 }, (_, i) =>
        rateLimitManager.checkRateLimit({
          userId: `user${i}`,
          userTier: 'T2',
          ipAddress: '127.0.0.1',
          endpoint: '/api/matriz',
          method: 'GET',
          userAgent: 'Test Agent',
        })
      );

      const results = await Promise.all(promises);

      // All requests should complete successfully
      expect(results).toHaveLength(100);
      results.forEach(result => {
        expect(result).toBeDefined();
        expect(typeof result.allowed).toBe('boolean');
      });
    });
  });
});

describe('RateLimitUtils', () => {
  describe('Rate Calculation Utilities', () => {
    it('should calculate requests per minute correctly', () => {
      expect(RateLimitUtils.calculateRPM(10, 60)).toBe(10);
      expect(RateLimitUtils.calculateRPM(5, 30)).toBe(10);
      expect(RateLimitUtils.calculateRPM(1, 6)).toBe(10);
    });

    it('should convert between time units', () => {
      expect(RateLimitUtils.minutesToMs(1)).toBe(60000);
      expect(RateLimitUtils.hoursToMs(1)).toBe(3600000);
      expect(RateLimitUtils.msToSeconds(5000)).toBe(5);
    });

    it('should calculate token bucket parameters', () => {
      const params = RateLimitUtils.calculateTokenBucket(100, 10, 60);
      
      expect(params.capacity).toBe(10);
      expect(params.refillRate).toBeCloseTo(1.67, 1); // 100/60 ≈ 1.67 tokens per second
      expect(params.interval).toBe(60);
    });
  });

  describe('Window Management', () => {
    it('should calculate sliding window boundaries', () => {
      const now = Date.now();
      const window = RateLimitUtils.getSlidingWindow(now, 60000);

      expect(window.start).toBe(now - 60000);
      expect(window.end).toBe(now);
      expect(window.duration).toBe(60000);
    });

    it('should determine if timestamp is within window', () => {
      const now = Date.now();
      const windowStart = now - 60000;

      expect(RateLimitUtils.isWithinWindow(now - 30000, windowStart, now)).toBe(true);
      expect(RateLimitUtils.isWithinWindow(now - 70000, windowStart, now)).toBe(false);
      expect(RateLimitUtils.isWithinWindow(now + 10000, windowStart, now)).toBe(false);
    });

    it('should clean expired entries', () => {
      const now = Date.now();
      const entries = [
        { timestamp: now - 70000, count: 1 },
        { timestamp: now - 30000, count: 2 },
        { timestamp: now - 10000, count: 3 },
      ];

      const cleaned = RateLimitUtils.cleanExpiredEntries(entries, 60000);

      expect(cleaned).toHaveLength(2);
      expect(cleaned[0].timestamp).toBe(now - 30000);
      expect(cleaned[1].timestamp).toBe(now - 10000);
    });
  });

  describe('Rate Limit Rule Resolution', () => {
    it('should select most restrictive rule', () => {
      const rules = [
        { name: 'tier', rpm: 100, burst: 10, window: 60000 },
        { name: 'endpoint', rpm: 50, burst: 5, window: 60000 },
        { name: 'ip', rpm: 200, burst: 20, window: 60000 },
      ];

      const mostRestrictive = RateLimitUtils.getMostRestrictiveRule(rules);

      expect(mostRestrictive.name).toBe('endpoint');
      expect(mostRestrictive.rpm).toBe(50);
    });

    it('should merge rate limit rules correctly', () => {
      const tierRule = { rpm: 100, burst: 10, window: 60000 };
      const endpointRule = { rpm: 50, burst: 5, window: 300000 };

      const merged = RateLimitUtils.mergeRules(tierRule, endpointRule);

      expect(merged.rpm).toBe(50); // More restrictive
      expect(merged.burst).toBe(5); // More restrictive
      expect(merged.window).toBe(300000); // Longer window (more restrictive)
    });

    it('should calculate effective rate limit', () => {
      const baseRule = { rpm: 100, burst: 10, window: 60000 };
      const systemLoad = 0.8;
      const userViolations = 3;

      const effective = RateLimitUtils.calculateEffectiveLimit(
        baseRule,
        systemLoad,
        userViolations
      );

      // Should be reduced due to high system load and violations
      expect(effective.rpm).toBeLessThan(baseRule.rpm);
      expect(effective.burst).toBeLessThan(baseRule.burst);
    });
  });

  describe('Security and Detection', () => {
    it('should detect bot user agents', () => {
      const botAgents = [
        'Googlebot/2.1',
        'curl/7.68.0',
        'wget/1.20.3',
        'Python-urllib/3.8',
        'Bot/1.0',
      ];

      const humanAgents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
      ];

      botAgents.forEach(agent => {
        expect(RateLimitUtils.isBotUserAgent(agent)).toBe(true);
      });

      humanAgents.forEach(agent => {
        expect(RateLimitUtils.isBotUserAgent(agent)).toBe(false);
      });
    });

    it('should detect suspicious IP patterns', () => {
      const suspiciousIPs = [
        '127.0.0.1',    // Localhost
        '10.0.0.1',     // Private network
        '192.168.1.1',  // Private network
        '172.16.0.1',   // Private network
      ];

      const legitimateIPs = [
        '8.8.8.8',      // Google DNS
        '1.1.1.1',      // Cloudflare DNS
        '203.0.113.1',  // Documentation range
        '198.51.100.1', // Documentation range
      ];

      suspiciousIPs.forEach(ip => {
        expect(RateLimitUtils.isSuspiciousIP(ip)).toBe(true);
      });

      legitimateIPs.forEach(ip => {
        expect(RateLimitUtils.isSuspiciousIP(ip)).toBe(false);
      });
    });

    it('should detect rapid request patterns', () => {
      const now = Date.now();
      
      // Rapid requests (all within 1 second)
      const rapidRequests = [
        { timestamp: now - 100, ip: '127.0.0.1' },
        { timestamp: now - 200, ip: '127.0.0.1' },
        { timestamp: now - 300, ip: '127.0.0.1' },
        { timestamp: now - 400, ip: '127.0.0.1' },
        { timestamp: now - 500, ip: '127.0.0.1' },
      ];

      // Normal requests (spread over time)
      const normalRequests = [
        { timestamp: now - 5000, ip: '127.0.0.1' },
        { timestamp: now - 10000, ip: '127.0.0.1' },
        { timestamp: now - 15000, ip: '127.0.0.1' },
      ];

      expect(RateLimitUtils.isRapidRequestPattern(rapidRequests)).toBe(true);
      expect(RateLimitUtils.isRapidRequestPattern(normalRequests)).toBe(false);
    });

    it('should calculate risk score for requests', () => {
      const lowRiskContext = {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ipAddress: '203.0.113.1',
        requestCount: 5,
        violationCount: 0,
        timePattern: 'normal' as const,
      };

      const highRiskContext = {
        userAgent: 'curl/7.68.0',
        ipAddress: '127.0.0.1',
        requestCount: 50,
        violationCount: 10,
        timePattern: 'rapid' as const,
      };

      const lowRisk = RateLimitUtils.calculateRiskScore(lowRiskContext);
      const highRisk = RateLimitUtils.calculateRiskScore(highRiskContext);

      expect(lowRisk).toBeLessThan(0.3);
      expect(highRisk).toBeGreaterThan(0.7);
    });
  });

  describe('Analytics and Reporting', () => {
    it('should aggregate rate limit statistics', () => {
      const events = [
        { allowed: true, tier: 'T1', endpoint: '/api/matriz', timestamp: Date.now() },
        { allowed: false, tier: 'T1', endpoint: '/api/matriz', timestamp: Date.now() },
        { allowed: true, tier: 'T2', endpoint: '/api/data', timestamp: Date.now() },
        { allowed: false, tier: 'T2', endpoint: '/api/data', timestamp: Date.now() },
        { allowed: false, tier: 'T2', endpoint: '/api/data', timestamp: Date.now() },
      ];

      const stats = RateLimitUtils.aggregateStatistics(events);

      expect(stats.totalRequests).toBe(5);
      expect(stats.allowedRequests).toBe(2);
      expect(stats.blockedRequests).toBe(3);
      expect(stats.blockRate).toBe(0.6);
      expect(stats.requestsByTier.T1).toBe(2);
      expect(stats.requestsByTier.T2).toBe(3);
    });

    it('should generate rate limit reports', () => {
      const timeRange = {
        start: Date.now() - 3600000, // 1 hour ago
        end: Date.now(),
      };

      const events = [
        { allowed: true, tier: 'T1', timestamp: Date.now() - 1800000 },
        { allowed: false, tier: 'T1', timestamp: Date.now() - 1200000 },
        { allowed: true, tier: 'T2', timestamp: Date.now() - 600000 },
      ];

      const report = RateLimitUtils.generateReport(events, timeRange);

      expect(report.timeRange).toEqual(timeRange);
      expect(report.summary.totalRequests).toBe(3);
      expect(report.trends).toBeDefined();
      expect(report.topViolators).toBeDefined();
      expect(report.recommendations).toBeDefined();
    });

    it('should track rate limit trends over time', () => {
      const events = Array.from({ length: 100 }, (_, i) => ({
        allowed: i % 3 !== 0, // Block every 3rd request
        tier: `T${(i % 3) + 1}` as any,
        timestamp: Date.now() - (100 - i) * 60000, // Spread over 100 minutes
      }));

      const trends = RateLimitUtils.calculateTrends(events, 3600000); // 1 hour buckets

      expect(trends).toBeDefined();
      expect(trends.length).toBeGreaterThan(0);
      trends.forEach(bucket => {
        expect(bucket.timestamp).toBeDefined();
        expect(bucket.requestCount).toBeDefined();
        expect(bucket.blockRate).toBeDefined();
      });
    });
  });
});