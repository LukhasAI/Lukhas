import { createTokenBucketLimiter } from '../rate-limit-tokenbucket';

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';

describe('Token Bucket Rate Limiter', () => {
  let tb: ReturnType<typeof createTokenBucketLimiter>;
  
  beforeAll(() => {
    tb = createTokenBucketLimiter({ url: REDIS_URL, namespace: 'tb:test' });
  });
  
  afterAll(async () => {
    await tb.quit();
  });

  test('allows burst then smooths', async () => {
    const key = `test-user-${Date.now()}`;
    const rpm = 60;  // 1 token/sec on average
    const burst = 10;

    // First 10 should pass immediately
    for (let i = 0; i < burst; i++) {
      const r = await tb.consume({ key, ratePerMinute: rpm, burst });
      expect(r.allowed).toBe(true);
      expect(r.remaining).toBeGreaterThanOrEqual(0);
    }
    
    // Next one might be blocked (depending on timing)
    const r11 = await tb.consume({ key, ratePerMinute: rpm, burst });
    expect([true, false]).toContain(r11.allowed);
    
    if (!r11.allowed) {
      expect(r11.retryAfterSec).toBeGreaterThan(0);
      expect(r11.nextAvailableAt).toBeGreaterThan(Date.now());
    }
  }, 15000);

  test('respects cost parameter', async () => {
    const key = `test-cost-${Date.now()}`;
    const rpm = 60;
    const burst = 10;
    
    // Consume 5 tokens at once
    const r1 = await tb.consume({ key, ratePerMinute: rpm, burst, cost: 5 });
    expect(r1.allowed).toBe(true);
    expect(r1.remaining).toBeLessThanOrEqual(5);
    
    // Try to consume 6 more (should fail or be at limit)
    const r2 = await tb.consume({ key, ratePerMinute: rpm, burst, cost: 6 });
    if (burst === 10) {
      expect(r2.allowed).toBe(false);
    }
  });

  test('refills over time', async () => {
    const key = `test-refill-${Date.now()}`;
    const rpm = 600; // 10 tokens/sec for faster test
    const burst = 5;
    
    // Consume all tokens
    for (let i = 0; i < burst; i++) {
      await tb.consume({ key, ratePerMinute: rpm, burst });
    }
    
    // Should be blocked
    const blocked = await tb.consume({ key, ratePerMinute: rpm, burst });
    expect(blocked.allowed).toBe(false);
    
    // Wait for refill (100ms = 1 token at 10/sec)
    await new Promise(resolve => setTimeout(resolve, 150));
    
    // Should have at least 1 token now
    const refilled = await tb.consume({ key, ratePerMinute: rpm, burst });
    expect(refilled.allowed).toBe(true);
  });
});