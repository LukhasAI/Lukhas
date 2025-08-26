/**
 * LUKHAS AI - Rate Limiting Utility
 *
 * In-memory rate limiting for API endpoints
 * In production, use Redis or a dedicated rate limiting service
 */

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

// In-memory store (use Redis in production)
const rateLimitStore = new Map<string, RateLimitEntry>();

interface RateLimitOptions {
  key: string;
  limit: number;
  window: number; // in milliseconds
}

interface RateLimitResult {
  success: boolean;
  remaining: number;
  resetTime: number;
}

/**
 * Check rate limit for a given key
 */
export async function rateLimit(options: RateLimitOptions): Promise<RateLimitResult> {
  const { key, limit, window } = options;
  const now = Date.now();
  const resetTime = now + window;

  const existing = rateLimitStore.get(key);

  if (!existing || now > existing.resetTime) {
    // No existing entry or window expired - create new entry
    rateLimitStore.set(key, {
      count: 1,
      resetTime
    });

    return {
      success: true,
      remaining: limit - 1,
      resetTime
    };
  }

  if (existing.count >= limit) {
    // Rate limit exceeded
    return {
      success: false,
      remaining: 0,
      resetTime: existing.resetTime
    };
  }

  // Increment count
  existing.count++;
  rateLimitStore.set(key, existing);

  return {
    success: true,
    remaining: limit - existing.count,
    resetTime: existing.resetTime
  };
}

/**
 * Cleanup expired entries (call periodically)
 */
export function cleanupRateLimit(): void {
  const now = Date.now();

  for (const [key, entry] of rateLimitStore.entries()) {
    if (now > entry.resetTime) {
      rateLimitStore.delete(key);
    }
  }
}

// Cleanup every 5 minutes
if (typeof window === 'undefined') {
  setInterval(cleanupRateLimit, 5 * 60 * 1000);
}

export default rateLimit;
