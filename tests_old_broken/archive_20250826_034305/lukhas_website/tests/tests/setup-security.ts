/**
 * LUKHAS AI ΛiD Authentication System - Security Test Setup
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Setup file for security tests - includes vulnerability testing utilities
 */

import crypto from 'crypto';

// Security test utilities
globalThis.securityTestUtils = {
  // Generate various types of malicious inputs
  generateSQLInjectionPayloads(): string[] {
    return [
      "'; DROP TABLE users; --",
      "' OR '1'='1",
      "'; UPDATE users SET admin=1; --",
      "' UNION SELECT password FROM users --",
      "1; EXEC xp_cmdshell('net user'); --",
    ];
  },

  generateXSSPayloads(): string[] {
    return [
      '<script>alert("XSS")</script>',
      '<img src="x" onerror="alert(1)">',
      '<svg onload="alert(1)">',
      'javascript:alert("XSS")',
      '<iframe src="javascript:alert(1)">',
      '"><script>alert(1)</script>',
      "'; alert('XSS'); //",
    ];
  },

  generateCSRFPayloads(): Record<string, any>[] {
    return [
      { referer: 'http://evil.com', origin: 'http://evil.com' },
      { referer: '', origin: '' },
      { referer: 'https://lukhas.ai.evil.com', origin: 'https://lukhas.ai.evil.com' },
    ];
  },

  generateJWTManipulations(validToken: string): string[] {
    const parts = validToken.split('.');
    const header = parts[0];
    const payload = parts[1];
    const signature = parts[2];

    return [
      // None algorithm attack
      header.replace(btoa('{"alg":"RS256","typ":"JWT"}'), btoa('{"alg":"none","typ":"JWT"}')),
      
      // Modified payload
      payload + 'modified',
      
      // Invalid signature
      `${header}.${payload}.invalid-signature`,
      
      // Empty signature
      `${header}.${payload}.`,
      
      // Wrong algorithm
      header.replace('RS256', 'HS256'),
    ];
  },

  generateTimingAttackInputs(): string[] {
    const validEmail = 'valid@lukhas.ai';
    const variations = [];
    
    // Generate strings with different lengths
    for (let i = 1; i <= 20; i++) {
      variations.push('a'.repeat(i) + '@lukhas.ai');
    }
    
    // Generate strings with same length but different content
    for (let i = 0; i < 10; i++) {
      variations.push(crypto.randomBytes(10).toString('hex') + '@lukhas.ai');
    }
    
    return variations;
  },

  generateRateLimitAttackPatterns(): Array<{ requests: number; interval: number; expected: 'blocked' | 'allowed' }> {
    return [
      { requests: 5, interval: 1000, expected: 'allowed' },   // Normal usage
      { requests: 100, interval: 1000, expected: 'blocked' }, // Burst attack
      { requests: 1000, interval: 60000, expected: 'blocked' }, // Sustained attack
      { requests: 10, interval: 100, expected: 'blocked' },   // High frequency
    ];
  },

  generateSessionFixationAttacks(): Record<string, any>[] {
    return [
      { sessionId: 'fixed-session-id', expected: 'rejected' },
      { sessionId: '', expected: 'rejected' },
      { sessionId: 'a'.repeat(1000), expected: 'rejected' },
      { sessionId: '../../../etc/passwd', expected: 'rejected' },
    ];
  },

  generateDirectoryTraversalPayloads(): string[] {
    return [
      '../../../etc/passwd',
      '..\\..\\..\\windows\\system32\\config\\sam',
      '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
      '....//....//....//etc/passwd',
      '..%252f..%252f..%252fetc%252fpasswd',
    ];
  },

  generatePasswordAttacks(): string[] {
    return [
      '', // Empty password
      ' ', // Space only
      'a'.repeat(10000), // Very long password
      '\x00\x01\x02', // Binary data
      '${process.env.SECRET}', // Template injection
      '<script>alert(1)</script>', // XSS in password
    ];
  },

  // Timing attack simulation
  async measureResponseTime(asyncFunc: Function, iterations: number = 10): Promise<number[]> {
    const times: number[] = [];
    
    for (let i = 0; i < iterations; i++) {
      const start = process.hrtime.bigint();
      await asyncFunc();
      const end = process.hrtime.bigint();
      times.push(Number(end - start) / 1000000); // Convert to milliseconds
    }
    
    return times;
  },

  // Statistical analysis for timing attacks
  analyzeTimingData(times: number[]): { mean: number; stdDev: number; suspicious: boolean } {
    const mean = times.reduce((sum, time) => sum + time, 0) / times.length;
    const variance = times.reduce((sum, time) => sum + Math.pow(time - mean, 2), 0) / times.length;
    const stdDev = Math.sqrt(variance);
    
    // Flag as suspicious if standard deviation is very low (constant time) or very high (variable time)
    const suspicious = stdDev < 0.1 || stdDev > mean * 0.5;
    
    return { mean, stdDev, suspicious };
  },

  // Generate concurrent requests for race condition testing
  generateConcurrentRequests(requestFunc: Function, count: number): Promise<any[]> {
    const requests = Array.from({ length: count }, () => requestFunc());
    return Promise.all(requests);
  },

  // Generate headers for header injection attacks
  generateHeaderInjectionPayloads(): Record<string, string>[] {
    return [
      { 'X-Forwarded-For': '127.0.0.1, evil.com' },
      { 'Host': 'evil.com' },
      { 'X-Real-IP': '127.0.0.1\r\nX-Evil: true' },
      { 'User-Agent': 'Agent\r\nX-Injected: true' },
      { 'Authorization': 'Bearer token\r\nX-Admin: true' },
    ];
  },
};

// Mock rate limiter for testing
globalThis.createMockRateLimiter = (options: { maxRequests: number; windowMs: number } = { maxRequests: 5, windowMs: 60000 }) => {
  const requests = new Map<string, number[]>();
  
  return {
    async checkLimit(key: string): Promise<{ allowed: boolean; retryAfter?: number }> {
      const now = Date.now();
      const windowStart = now - options.windowMs;
      
      if (!requests.has(key)) {
        requests.set(key, []);
      }
      
      const keyRequests = requests.get(key)!;
      
      // Remove old requests outside the window
      const validRequests = keyRequests.filter(time => time > windowStart);
      requests.set(key, validRequests);
      
      if (validRequests.length >= options.maxRequests) {
        const oldestRequest = Math.min(...validRequests);
        const retryAfter = Math.ceil((oldestRequest + options.windowMs - now) / 1000);
        return { allowed: false, retryAfter };
      }
      
      validRequests.push(now);
      requests.set(key, validRequests);
      
      return { allowed: true };
    },
    
    reset() {
      requests.clear();
    },
  };
};

// Security test environment setup
beforeEach(() => {
  // Reset security test state
  jest.clearAllMocks();
});

// Global security test timeout (longer for security tests)
jest.setTimeout(60000);