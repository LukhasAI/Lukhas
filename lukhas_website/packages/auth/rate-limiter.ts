/**
 * Redis-backed Rate Limiting System for ΛiD Authentication
 *
 * Implements sophisticated rate limiting with multiple algorithms, tier-based limits,
 * graceful degradation, and proper 429 response handling for LUKHAS AI.
 */

import { TierLevel, TierManager } from './tier-system';

export interface RateLimitConfig {
  rpm: number;           // Requests per minute
  rpd: number;           // Requests per day
  identifier: string;    // Unique identifier (user ID, IP, etc.)
  burst?: number;        // Burst allowance
  algorithm?: 'sliding_window' | 'token_bucket' | 'fixed_window';
  skipSuccessfulAuth?: boolean; // Skip rate limiting for successful auth
}

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetTime: number;     // Unix timestamp
  retryAfter?: number;   // Seconds to wait
  algorithm: string;
  identifier: string;
  tier?: TierLevel;
}

export interface RateLimitStats {
  current: number;
  limit: number;
  resetTime: number;
  identifier: string;
  windowStart: number;
  algorithm: string;
}

/**
 * In-memory fallback when Redis is unavailable
 */
class MemoryRateLimiter {
  private windows = new Map<string, { count: number; resetTime: number; requests: number[] }>();
  private readonly cleanupInterval: NodeJS.Timeout;

  constructor() {
    // Clean up expired windows every minute
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000);
  }

  async checkLimit(config: RateLimitConfig): Promise<RateLimitResult> {
    const now = Date.now();
    const windowKey = `${config.identifier}:${config.rpm}:${config.rpd}`;

    let window = this.windows.get(windowKey);

    // Initialize or reset window if expired
    if (!window || now >= window.resetTime) {
      window = {
        count: 0,
        resetTime: now + (60 * 1000), // 1 minute window
        requests: []
      };
      this.windows.set(windowKey, window);
    }

    // Clean old requests from sliding window
    const cutoff = now - (60 * 1000);
    window.requests = window.requests.filter(time => time > cutoff);

    // Check RPM limit
    const rpmExceeded = window.requests.length >= config.rpm;

    // Check RPD limit (simplified daily check)
    const dailyKey = `${config.identifier}:daily:${new Date().toDateString()}`;
    const dailyWindow = this.windows.get(dailyKey);
    const dailyCount = dailyWindow?.count || 0;
    const rpdExceeded = dailyCount >= config.rpd;

    if (rpmExceeded || rpdExceeded) {
      return {
        allowed: false,
        remaining: Math.max(0, config.rpm - window.requests.length),
        resetTime: Math.ceil(window.resetTime / 1000),
        retryAfter: Math.ceil((window.resetTime - now) / 1000),
        algorithm: 'memory_sliding_window',
        identifier: config.identifier
      };
    }

    // Record the request
    window.requests.push(now);

    // Update daily counter
    if (dailyWindow) {
      dailyWindow.count++;
    } else {
      this.windows.set(dailyKey, {
        count: 1,
        resetTime: now + (24 * 60 * 60 * 1000), // 24 hours
        requests: []
      });
    }

    return {
      allowed: true,
      remaining: Math.max(0, config.rpm - window.requests.length),
      resetTime: Math.ceil(window.resetTime / 1000),
      algorithm: 'memory_sliding_window',
      identifier: config.identifier
    };
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, window] of this.windows.entries()) {
      if (now >= window.resetTime) {
        this.windows.delete(key);
      }
    }
  }

  destroy(): void {
    clearInterval(this.cleanupInterval);
    this.windows.clear();
  }
}

/**
 * Redis-backed rate limiter with fallback to memory
 */
class RedisRateLimiter {
  private redis: any; // Redis client
  private memoryFallback: MemoryRateLimiter;
  private isRedisAvailable = false;

  constructor() {
    this.memoryFallback = new MemoryRateLimiter();
    this.initializeRedis();
  }

  private async initializeRedis(): Promise<void> {
    try {
      // Initialize Redis client (placeholder - implement with actual Redis)
      // const Redis = require('ioredis');
      // this.redis = new Redis(process.env.REDIS_URL);
      // this.isRedisAvailable = true;

      // For now, use memory fallback
      this.isRedisAvailable = false;
      console.log('Redis not available, using memory fallback for rate limiting');
    } catch (error) {
      console.warn('Failed to initialize Redis, using memory fallback:', error);
      this.isRedisAvailable = false;
    }
  }

  async checkLimit(config: RateLimitConfig): Promise<RateLimitResult> {
    if (!this.isRedisAvailable) {
      return this.memoryFallback.checkLimit(config);
    }

    try {
      return await this.checkRedisLimit(config);
    } catch (error) {
      console.warn('Redis rate limit check failed, falling back to memory:', error);
      return this.memoryFallback.checkLimit(config);
    }
  }

  private async checkRedisLimit(config: RateLimitConfig): Promise<RateLimitResult> {
    const now = Date.now();
    const algorithm = config.algorithm || 'sliding_window';

    switch (algorithm) {
      case 'sliding_window':
        return this.slidingWindowLimit(config, now);
      case 'token_bucket':
        return this.tokenBucketLimit(config, now);
      case 'fixed_window':
        return this.fixedWindowLimit(config, now);
      default:
        return this.slidingWindowLimit(config, now);
    }
  }

  private async slidingWindowLimit(config: RateLimitConfig, now: number): Promise<RateLimitResult> {
    // Redis Lua script for atomic sliding window rate limiting
    const script = `
      local key = KEYS[1]
      local window = tonumber(ARGV[1])
      local limit = tonumber(ARGV[2])
      local now = tonumber(ARGV[3])
      local expiry = tonumber(ARGV[4])

      -- Remove expired entries
      redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

      -- Count current requests
      local count = redis.call('ZCARD', key)

      if count < limit then
        -- Add current request
        redis.call('ZADD', key, now, now)
        redis.call('EXPIRE', key, expiry)
        return {1, limit - count - 1, now + window}
      else
        return {0, 0, now + window}
      end
    `;

    const windowMs = 60 * 1000; // 1 minute
    const expirySec = 60; // 1 minute expiry

    const result = await this.redis.eval(
      script,
      1,
      `rate_limit:${config.identifier}:rpm`,
      windowMs,
      config.rpm,
      now,
      expirySec
    );

    const [allowed, remaining, resetTime] = result;

    return {
      allowed: Boolean(allowed),
      remaining: Number(remaining),
      resetTime: Math.ceil(Number(resetTime) / 1000),
      retryAfter: allowed ? undefined : Math.ceil((resetTime - now) / 1000),
      algorithm: 'redis_sliding_window',
      identifier: config.identifier
    };
  }

  private async tokenBucketLimit(config: RateLimitConfig, now: number): Promise<RateLimitResult> {
    // Token bucket implementation with Redis
    const script = `
      local key = KEYS[1]
      local capacity = tonumber(ARGV[1])
      local refill_rate = tonumber(ARGV[2])
      local now = tonumber(ARGV[3])
      local requested = tonumber(ARGV[4]) or 1

      local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
      local tokens = tonumber(bucket[1]) or capacity
      local last_refill = tonumber(bucket[2]) or now

      -- Calculate tokens to add based on time elapsed
      local elapsed = math.max(0, (now - last_refill) / 1000)
      local tokens_to_add = math.floor(elapsed * refill_rate)
      tokens = math.min(capacity, tokens + tokens_to_add)

      if tokens >= requested then
        tokens = tokens - requested
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 3600) -- 1 hour expiry
        return {1, tokens, now + ((capacity - tokens) / refill_rate) * 1000}
      else
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 3600)
        return {0, tokens, now + ((capacity - tokens) / refill_rate) * 1000}
      end
    `;

    const refillRate = config.rpm / 60; // Tokens per second
    const result = await this.redis.eval(
      script,
      1,
      `rate_limit:${config.identifier}:bucket`,
      config.rpm,
      refillRate,
      now,
      1
    );

    const [allowed, remaining, resetTime] = result;

    return {
      allowed: Boolean(allowed),
      remaining: Number(remaining),
      resetTime: Math.ceil(Number(resetTime) / 1000),
      retryAfter: allowed ? undefined : Math.ceil((resetTime - now) / 1000),
      algorithm: 'redis_token_bucket',
      identifier: config.identifier
    };
  }

  private async fixedWindowLimit(config: RateLimitConfig, now: number): Promise<RateLimitResult> {
    // Fixed window implementation
    const windowStart = Math.floor(now / (60 * 1000)) * (60 * 1000); // 1-minute windows
    const key = `rate_limit:${config.identifier}:fixed:${windowStart}`;

    const script = `
      local key = KEYS[1]
      local limit = tonumber(ARGV[1])
      local expiry = tonumber(ARGV[2])
      local reset_time = tonumber(ARGV[3])

      local count = redis.call('INCR', key)
      if count == 1 then
        redis.call('EXPIRE', key, expiry)
      end

      if count <= limit then
        return {1, limit - count, reset_time}
      else
        return {0, 0, reset_time}
      end
    `;

    const resetTime = windowStart + (60 * 1000);
    const result = await this.redis.eval(
      script,
      1,
      key,
      config.rpm,
      60, // 1 minute expiry
      resetTime
    );

    const [allowed, remaining, resetTimeResult] = result;

    return {
      allowed: Boolean(allowed),
      remaining: Number(remaining),
      resetTime: Math.ceil(Number(resetTimeResult) / 1000),
      retryAfter: allowed ? undefined : Math.ceil((resetTimeResult - now) / 1000),
      algorithm: 'redis_fixed_window',
      identifier: config.identifier
    };
  }

  async getStats(identifier: string): Promise<RateLimitStats | null> {
    if (!this.isRedisAvailable) {
      return null;
    }

    try {
      const key = `rate_limit:${identifier}:rpm`;
      const count = await this.redis.zcard(key);
      const ttl = await this.redis.ttl(key);

      return {
        current: count,
        limit: 0, // Would need to be stored separately
        resetTime: Date.now() + (ttl * 1000),
        identifier,
        windowStart: Date.now() - (60 * 1000),
        algorithm: 'redis_sliding_window'
      };
    } catch (error) {
      console.warn('Failed to get rate limit stats:', error);
      return null;
    }
  }

  destroy(): void {
    this.memoryFallback.destroy();
    if (this.redis) {
      this.redis.disconnect();
    }
  }
}

/**
 * Main rate limiter interface
 */
export class RateLimiter {
  private static instance: RedisRateLimiter;

  static getInstance(): RedisRateLimiter {
    if (!this.instance) {
      this.instance = new RedisRateLimiter();
    }
    return this.instance;
  }

  /**
   * Check rate limit for a request
   */
  static async checkLimit(config: RateLimitConfig): Promise<RateLimitResult> {
    const limiter = this.getInstance();
    return limiter.checkLimit(config);
  }

  /**
   * Check rate limit with tier-based configuration
   */
  static async checkTierLimit(
    identifier: string,
    tier: TierLevel,
    options?: {
      algorithm?: 'sliding_window' | 'token_bucket' | 'fixed_window';
      customLimits?: { rpm?: number; rpd?: number };
    }
  ): Promise<RateLimitResult> {
    const tierLimits = TierManager.getRateLimits(tier);

    const config: RateLimitConfig = {
      identifier,
      rpm: options?.customLimits?.rpm || tierLimits.rpm,
      rpd: options?.customLimits?.rpd || tierLimits.rpd,
      burst: tierLimits.burst,
      algorithm: options?.algorithm || 'sliding_window'
    };

    const result = await this.checkLimit(config);
    result.tier = tier;

    return result;
  }

  /**
   * Create rate limit response headers
   */
  static createHeaders(result: RateLimitResult): Record<string, string> {
    const headers: Record<string, string> = {
      'X-RateLimit-Limit': '60', // Default, should be actual limit
      'X-RateLimit-Remaining': result.remaining.toString(),
      'X-RateLimit-Reset': result.resetTime.toString()
    };

    if (!result.allowed && result.retryAfter) {
      headers['Retry-After'] = result.retryAfter.toString();
    }

    return headers;
  }

  /**
   * Check multiple rate limits (IP, user, tier, etc.)
   */
  static async checkMultipleLimits(checks: {
    name: string;
    config: RateLimitConfig;
  }[]): Promise<{
    allowed: boolean;
    results: Array<{ name: string; result: RateLimitResult }>;
    mostRestrictive: RateLimitResult;
  }> {
    const results: Array<{ name: string; result: RateLimitResult }> = [];
    let mostRestrictive: RateLimitResult | null = null;
    let allowed = true;

    for (const check of checks) {
      const result = await this.checkLimit(check.config);
      results.push({ name: check.name, result });

      if (!result.allowed) {
        allowed = false;
      }

      // Track most restrictive limit
      if (!mostRestrictive ||
          result.remaining < mostRestrictive.remaining ||
          (!result.allowed && result.retryAfter && result.retryAfter > (mostRestrictive.retryAfter || 0))) {
        mostRestrictive = result;
      }
    }

    return {
      allowed,
      results,
      mostRestrictive: mostRestrictive!
    };
  }

  /**
   * Get rate limit statistics
   */
  static async getStats(identifier: string): Promise<RateLimitStats | null> {
    const limiter = this.getInstance();
    return limiter.getStats(identifier);
  }

  /**
   * Create 429 response with proper headers
   */
  static create429Response(result: RateLimitResult, message?: string): Response {
    const headers = this.createHeaders(result);

    const body = {
      error: 'rate_limit_exceeded',
      message: message || `Rate limit exceeded. Try again in ${result.retryAfter || 60} seconds.`,
      limit: result.remaining + 1, // Approximate original limit
      remaining: result.remaining,
      resetTime: result.resetTime,
      retryAfter: result.retryAfter
    };

    return new Response(JSON.stringify(body), {
      status: 429,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      }
    });
  }

  /**
   * Graceful degradation when rate limiting fails
   */
  static async checkWithFallback(
    config: RateLimitConfig,
    fallbackAllowed = true
  ): Promise<RateLimitResult> {
    try {
      return await this.checkLimit(config);
    } catch (error) {
      console.error('Rate limiting failed, using fallback:', error);

      // Return fallback result
      return {
        allowed: fallbackAllowed,
        remaining: fallbackAllowed ? 999 : 0,
        resetTime: Math.ceil((Date.now() + 60000) / 1000),
        algorithm: 'fallback',
        identifier: config.identifier
      };
    }
  }

  /**
   * Clean up resources
   */
  static destroy(): void {
    if (this.instance) {
      this.instance.destroy();
    }
  }
}

/**
 * Rate limiting middleware helpers
 */
export class RateLimitMiddleware {
  /**
   * Create middleware function for Express/Next.js
   */
  static create(options: {
    keyGenerator?: (req: any) => string;
    tierExtractor?: (req: any) => TierLevel;
    customLimits?: { rpm: number; rpd: number };
    skip?: (req: any) => boolean;
    onLimitReached?: (req: any, result: RateLimitResult) => void;
  } = {}) {
    return async (req: any, res: any, next: any) => {
      try {
        // Skip if condition met
        if (options.skip && options.skip(req)) {
          return next();
        }

        // Generate rate limit key
        const identifier = options.keyGenerator
          ? options.keyGenerator(req)
          : req.ip || 'unknown';

        // Get tier
        const tier = options.tierExtractor
          ? options.tierExtractor(req)
          : 'T1';

        // Check rate limit
        const result = await RateLimiter.checkTierLimit(identifier, tier, {
          customLimits: options.customLimits
        });

        // Add headers
        const headers = RateLimiter.createHeaders(result);
        Object.entries(headers).forEach(([key, value]) => {
          res.setHeader(key, value);
        });

        if (!result.allowed) {
          // Call hook if provided
          if (options.onLimitReached) {
            options.onLimitReached(req, result);
          }

          // Return 429 response
          return res.status(429).json({
            error: 'rate_limit_exceeded',
            message: `Rate limit exceeded. Try again in ${result.retryAfter || 60} seconds.`,
            retryAfter: result.retryAfter
          });
        }

        next();
      } catch (error) {
        console.error('Rate limiting middleware error:', error);
        // Continue on error (fail open)
        next();
      }
    };
  }
}

export default RateLimiter;
