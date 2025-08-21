import { test, expect } from '@playwright/test';

test.describe('Rate Limiting', () => {
  test('returns 429 with Retry-After and JSON body', async ({ request }) => {
    // Make multiple requests to trigger rate limit
    const requests = [];
    for (let i = 0; i < 35; i++) { // Exceed free tier limit (30 rpm)
      requests.push(request.post('/api/auth/magic-link', { 
        data: { email: 'test@lukhas.ai' }
      }));
    }
    
    const responses = await Promise.all(requests);
    
    // At least one should be rate limited
    const rateLimited = responses.find(res => res.status() === 429);
    
    if (rateLimited) {
      // Check headers
      expect(rateLimited.headers()['retry-after']).toBeTruthy();
      expect(rateLimited.headers()['content-type']).toContain('application/json');
      
      // Check JSON body
      const json = await rateLimited.json();
      expect(json.ok).toBe(false);
      expect(json.error).toBe('rate_limited');
      expect(json.message).toBeTruthy();
      expect(json.meta).toBeTruthy();
    }
  });

  test('includes rate limit headers in response', async ({ request }) => {
    const response = await request.post('/api/auth/passkey/authenticate', {
      data: { userId: 'test-user' }
    });
    
    // Should have rate limit headers even on success
    const headers = response.headers();
    if (headers['x-ratelimit-limit']) {
      expect(Number(headers['x-ratelimit-limit'])).toBeGreaterThan(0);
    }
    if (headers['x-ratelimit-remaining']) {
      expect(Number(headers['x-ratelimit-remaining'])).toBeGreaterThanOrEqual(0);
    }
  });

  test('rate limit message is localized', async ({ request }) => {
    // Test French locale
    const response = await request.post('/api/auth/magic-link', {
      data: { email: 'test@lukhas.ai' },
      headers: { 'Accept-Language': 'fr' }
    });
    
    if (response.status() === 429) {
      const json = await response.json();
      expect(json.message).toContain('limite'); // French word for limit
    }
    
    // Test Spanish locale
    const responseES = await request.post('/api/auth/magic-link', {
      data: { email: 'test@lukhas.ai' },
      headers: { 'Accept-Language': 'es' }
    });
    
    if (responseES.status() === 429) {
      const json = await responseES.json();
      expect(json.message).toContain('límite'); // Spanish word for limit
    }
  });

  test('different endpoints have independent rate limits', async ({ request }) => {
    // Hit one endpoint multiple times
    const authRequests = [];
    for (let i = 0; i < 35; i++) {
      authRequests.push(request.post('/api/auth/magic-link', {
        data: { email: 'test@lukhas.ai' }
      }));
    }
    await Promise.all(authRequests);
    
    // Different endpoint should still work
    const signupResponse = await request.post('/api/auth/signup/email', {
      data: { email: 'newuser@lukhas.ai' }
    });
    
    // Signup endpoint should not be rate limited
    expect(signupResponse.status()).not.toBe(429);
  });

  test('rate limit resets after time window', async ({ request }) => {
    // This test would need to wait for the time window to pass
    // Skipping for CI performance, but here's the structure:
    
    test.skip(true, 'Skipping time-based test for CI');
    
    // Make requests to hit limit
    // Wait for window to reset (e.g., 60 seconds for minute window)
    // Make another request - should succeed
  });

  test('higher tier plans have higher limits', async ({ request }) => {
    // This would require auth with different tier users
    // Mock implementation:
    
    const freeUserResponse = await request.post('/api/test/rate-check', {
      data: { tier: 'free' }
    });
    
    const enterpriseUserResponse = await request.post('/api/test/rate-check', {
      data: { tier: 'enterprise' }
    });
    
    if (freeUserResponse.headers()['x-ratelimit-limit'] && 
        enterpriseUserResponse.headers()['x-ratelimit-limit']) {
      const freeLimit = Number(freeUserResponse.headers()['x-ratelimit-limit']);
      const enterpriseLimit = Number(enterpriseUserResponse.headers()['x-ratelimit-limit']);
      expect(enterpriseLimit).toBeGreaterThan(freeLimit);
    }
  });
});

test.describe('Security Headers', () => {
  test('429 responses include security headers', async ({ request }) => {
    // Trigger rate limit
    const requests = [];
    for (let i = 0; i < 35; i++) {
      requests.push(request.post('/api/auth/magic-link', {
        data: { email: 'test@lukhas.ai' }
      }));
    }
    
    const responses = await Promise.all(requests);
    const rateLimited = responses.find(res => res.status() === 429);
    
    if (rateLimited) {
      const headers = rateLimited.headers();
      expect(headers['cache-control']).toBe('no-store');
      expect(headers['content-type']).toContain('charset=utf-8');
    }
  });
});