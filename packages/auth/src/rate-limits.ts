/**
 * ΛiD Authentication System - Rate Limiting
 *
 * Tier-based rate limiting with advanced monitoring and adaptive controls
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

import { UserTier, RateLimitConfig, RateLimitResult, RateLimitWindow } from '../types/auth.types';
import { Tier } from './scopes';

/**
 * Rate limit configurations per tier
 * RPM = Requests Per Minute, RPD = Requests Per Day
 */
export const TIER_RATE_LIMITS: Record<Tier, RateLimitConfig> = {
  [Tier.T1_EXPLORER]: {
    rpm: 30,           // 30 requests per minute
    rpd: 1000,         // 1,000 requests per day
    burst: 5,          // Burst allowance
    concurrency: 2,    // Max concurrent requests
    resetWindow: 'minute'
  },

  [Tier.T2_BUILDER]: {
    rpm: 60,           // 60 requests per minute
    rpd: 5000,         // 5,000 requests per day
    burst: 10,         // Burst allowance
    concurrency: 5,    // Max concurrent requests
    resetWindow: 'minute'
  },

  [Tier.T3_STUDIO]: {
    rpm: 120,          // 120 requests per minute
    rpd: 20000,        // 20,000 requests per day
    burst: 20,         // Burst allowance
    concurrency: 10,   // Max concurrent requests
    resetWindow: 'minute'
  },

  [Tier.T4_ENTERPRISE]: {
    rpm: 300,          // 300 requests per minute
    rpd: 100000,       // 100,000 requests per day
    burst: 50,         // Burst allowance
    concurrency: 25,   // Max concurrent requests
    resetWindow: 'minute'
  },

  [Tier.T5_CORE_TEAM]: {
    rpm: 1000,         // 1,000 requests per minute
    rpd: 1000000,      // 1,000,000 requests per day
    burst: 100,        // Burst allowance
    concurrency: 50,   // Max concurrent requests
    resetWindow: 'minute'
  }
};

/**
 * Specialized rate limits for different operation types
 */
export const OPERATION_RATE_LIMITS: Record<string, Partial<RateLimitConfig>> = {
  // Authentication operations
  'auth:login': {
    rpm: 10,
    burst: 3,
    resetWindow: 'minute'
  },

  'auth:register': {
    rpm: 5,
    burst: 2,
    resetWindow: 'hour'
  },

  'auth:password-reset': {
    rpm: 3,
    burst: 1,
    resetWindow: 'hour'
  },

  'auth:magic-link': {
    rpm: 5,
    burst: 2,
    resetWindow: 'minute'
  },

  // API operations
  'api:read': {
    rpm: 100,
    burst: 20
  },

  'api:write': {
    rpm: 50,
    burst: 10
  },

  'api:delete': {
    rpm: 20,
    burst: 5
  },

  // Consciousness operations
  'consciousness:query': {
    rpm: 30,
    burst: 5
  },

  'consciousness:modify': {
    rpm: 10,
    burst: 2
  },

  // Memory operations
  'memory:read': {
    rpm: 200,
    burst: 50
  },

  'memory:write': {
    rpm: 100,
    burst: 20
  },

  // Guardian operations
  'guardian:check': {
    rpm: 500,
    burst: 100
  }
};

/**
 * In-memory rate limit store (in production, use Redis/similar)
 */
class RateLimitStore {
  private store = new Map<string, RateLimitWindow>();
  private concurrencyStore = new Map<string, number>();

  /**
   * Get current rate limit window for a key
   */
  getWindow(key: string): RateLimitWindow | null {
    const window = this.store.get(key);
    if (!window) return null;

    // Check if window has expired
    if (Date.now() > window.expiresAt) {
      this.store.delete(key);
      return null;
    }

    return window;
  }

  /**
   * Update rate limit window
   */
  setWindow(key: string, window: RateLimitWindow): void {
    this.store.set(key, window);
  }

  /**
   * Get current concurrency count
   */
  getConcurrency(key: string): number {
    return this.concurrencyStore.get(key) || 0;
  }

  /**
   * Increment concurrency counter
   */
  incrementConcurrency(key: string): number {
    const current = this.getConcurrency(key);
    const newCount = current + 1;
    this.concurrencyStore.set(key, newCount);
    return newCount;
  }

  /**
   * Decrement concurrency counter
   */
  decrementConcurrency(key: string): number {
    const current = this.getConcurrency(key);
    const newCount = Math.max(0, current - 1);
    this.concurrencyStore.set(key, newCount);
    return newCount;
  }

  /**
   * Clean expired entries
   */
  cleanup(): void {
    const now = Date.now();
    for (const [key, window] of this.store.entries()) {
      if (now > window.expiresAt) {
        this.store.delete(key);
      }
    }
  }
}

// Global rate limit store instance
const rateLimitStore = new RateLimitStore();

// Cleanup task runs every minute
setInterval(() => rateLimitStore.cleanup(), 60000);

/**
 * Check if request is within rate limits
 *
 * @param userId - User identifier
 * @param userTier - User's tier level
 * @param operation - Operation type (optional for specialized limits)
 * @param identifier - Additional identifier (IP, device, etc.)
 * @returns Rate limit result with decision and metadata
 */
export function checkRateLimit(
  userId: string,
  userTier: UserTier,
  operation?: string,
  identifier?: string
): RateLimitResult {
  const tier = userTier as Tier;
  const config = TIER_RATE_LIMITS[tier];

  if (!config) {
    return {
      allowed: false,
      reason: 'Invalid tier configuration',
      resetTime: Date.now() + 60000
    };
  }

  // Apply operation-specific limits if provided
  const operationConfig = operation ? OPERATION_RATE_LIMITS[operation] : {};
  const finalConfig: RateLimitConfig = {
    ...config,
    ...operationConfig
  };

  const keys = generateRateLimitKeys(userId, operation, identifier);

  try {
    // Check each rate limit type
    const minuteResult = checkWindowLimit(keys.minute, finalConfig.rpm, 60000, finalConfig.burst);
    if (!minuteResult.allowed) {
      return minuteResult;
    }

    const dayResult = checkWindowLimit(keys.day, finalConfig.rpd, 86400000, finalConfig.burst);
    if (!dayResult.allowed) {
      return dayResult;
    }

    // Check concurrency limit
    const concurrencyResult = checkConcurrencyLimit(keys.concurrency, finalConfig.concurrency);
    if (!concurrencyResult.allowed) {
      return concurrencyResult;
    }

    // All checks passed
    return {
      allowed: true,
      remaining: {
        minute: finalConfig.rpm - minuteResult.count!,
        day: finalConfig.rpd - dayResult.count!,
        burst: finalConfig.burst - Math.max(minuteResult.burstUsed || 0, dayResult.burstUsed || 0)
      },
      resetTime: Math.min(minuteResult.resetTime!, dayResult.resetTime!),
      metadata: {
        tier: userTier,
        operation,
        appliedConfig: finalConfig
      }
    };

  } catch (error) {
    return {
      allowed: false,
      reason: `Rate limit check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      resetTime: Date.now() + 60000
    };
  }
}

/**
 * Generate rate limit keys for different time windows
 */
function generateRateLimitKeys(
  userId: string,
  operation?: string,
  identifier?: string
): { minute: string; day: string; concurrency: string } {
  const now = new Date();
  const minute = Math.floor(now.getTime() / 60000);
  const day = Math.floor(now.getTime() / 86400000);

  const baseKey = operation ? `${userId}:${operation}` : userId;
  const identifierSuffix = identifier ? `:${identifier}` : '';

  return {
    minute: `rl:m:${minute}:${baseKey}${identifierSuffix}`,
    day: `rl:d:${day}:${baseKey}${identifierSuffix}`,
    concurrency: `rl:c:${baseKey}${identifierSuffix}`
  };
}

/**
 * Check rate limit for a specific time window
 */
function checkWindowLimit(
  key: string,
  limit: number,
  windowMs: number,
  burstAllowance: number
): RateLimitResult & { count?: number; burstUsed?: number } {
  const now = Date.now();
  let window = rateLimitStore.getWindow(key);

  if (!window) {
    // Create new window
    window = {
      count: 0,
      burstUsed: 0,
      expiresAt: now + windowMs,
      createdAt: now
    };
  }

  // Check if we can use burst allowance
  const totalAllowed = limit + burstAllowance;

  if (window.count >= totalAllowed) {
    return {
      allowed: false,
      reason: 'Rate limit exceeded',
      resetTime: window.expiresAt,
      count: window.count,
      burstUsed: window.burstUsed
    };
  }

  // Increment counter
  window.count++;

  // Track burst usage
  if (window.count > limit) {
    window.burstUsed = window.count - limit;
  }

  // Update store
  rateLimitStore.setWindow(key, window);

  return {
    allowed: true,
    resetTime: window.expiresAt,
    count: window.count,
    burstUsed: window.burstUsed
  };
}

/**
 * Check concurrency limit
 */
function checkConcurrencyLimit(key: string, limit: number): RateLimitResult {
  const current = rateLimitStore.getConcurrency(key);

  if (current >= limit) {
    return {
      allowed: false,
      reason: 'Concurrency limit exceeded',
      resetTime: Date.now() + 5000 // Retry in 5 seconds
    };
  }

  return {
    allowed: true,
    resetTime: Date.now() + 60000
  };
}

/**
 * Acquire concurrency slot (call before processing request)
 */
export function acquireConcurrencySlot(
  userId: string,
  operation?: string,
  identifier?: string
): boolean {
  const keys = generateRateLimitKeys(userId, operation, identifier);
  const current = rateLimitStore.incrementConcurrency(keys.concurrency);
  return true; // Could implement max check here
}

/**
 * Release concurrency slot (call after processing request)
 */
export function releaseConcurrencySlot(
  userId: string,
  operation?: string,
  identifier?: string
): void {
  const keys = generateRateLimitKeys(userId, operation, identifier);
  rateLimitStore.decrementConcurrency(keys.concurrency);
}

/**
 * Get current rate limit status for a user
 */
export function getRateLimitStatus(
  userId: string,
  userTier: UserTier,
  operation?: string,
  identifier?: string
): {
  limits: RateLimitConfig;
  current: {
    minute: number;
    day: number;
    concurrency: number;
  };
  remaining: {
    minute: number;
    day: number;
    burst: number;
  };
  resetTimes: {
    minute: number;
    day: number;
  };
} {
  const tier = userTier as Tier;
  const config = TIER_RATE_LIMITS[tier];
  const operationConfig = operation ? OPERATION_RATE_LIMITS[operation] : {};
  const finalConfig: RateLimitConfig = { ...config, ...operationConfig };

  const keys = generateRateLimitKeys(userId, operation, identifier);

  const minuteWindow = rateLimitStore.getWindow(keys.minute);
  const dayWindow = rateLimitStore.getWindow(keys.day);
  const concurrency = rateLimitStore.getConcurrency(keys.concurrency);

  const minuteCount = minuteWindow?.count || 0;
  const dayCount = dayWindow?.count || 0;
  const burstUsed = Math.max(minuteWindow?.burstUsed || 0, dayWindow?.burstUsed || 0);

  return {
    limits: finalConfig,
    current: {
      minute: minuteCount,
      day: dayCount,
      concurrency
    },
    remaining: {
      minute: Math.max(0, finalConfig.rpm - minuteCount),
      day: Math.max(0, finalConfig.rpd - dayCount),
      burst: Math.max(0, finalConfig.burst - burstUsed)
    },
    resetTimes: {
      minute: minuteWindow?.expiresAt || Date.now() + 60000,
      day: dayWindow?.expiresAt || Date.now() + 86400000
    }
  };
}

/**
 * Reset rate limits for a user (admin function)
 */
export function resetRateLimits(
  userId: string,
  operation?: string,
  identifier?: string
): void {
  const keys = generateRateLimitKeys(userId, operation, identifier);

  // Clear rate limit windows
  rateLimitStore.setWindow(keys.minute, {
    count: 0,
    burstUsed: 0,
    expiresAt: Date.now() + 60000,
    createdAt: Date.now()
  });

  rateLimitStore.setWindow(keys.day, {
    count: 0,
    burstUsed: 0,
    expiresAt: Date.now() + 86400000,
    createdAt: Date.now()
  });

  // Reset concurrency
  rateLimitStore.decrementConcurrency(keys.concurrency);
}

/**
 * Adaptive rate limiting based on system load
 */
export function getAdaptiveRateLimit(
  baseTier: UserTier,
  systemLoad: number, // 0.0 to 1.0
  userBehaviorScore: number // 0.0 to 1.0, higher is better
): RateLimitConfig {
  const tier = baseTier as Tier;
  const baseConfig = TIER_RATE_LIMITS[tier];

  // Adjust limits based on system load
  let loadMultiplier = 1.0;
  if (systemLoad > 0.8) {
    loadMultiplier = 0.5; // Reduce limits by 50% under high load
  } else if (systemLoad > 0.6) {
    loadMultiplier = 0.75; // Reduce limits by 25% under medium load
  }

  // Adjust limits based on user behavior
  let behaviorMultiplier = 1.0;
  if (userBehaviorScore > 0.8) {
    behaviorMultiplier = 1.2; // Increase limits for well-behaved users
  } else if (userBehaviorScore < 0.3) {
    behaviorMultiplier = 0.5; // Reduce limits for problematic users
  }

  const finalMultiplier = loadMultiplier * behaviorMultiplier;

  return {
    ...baseConfig,
    rpm: Math.floor(baseConfig.rpm * finalMultiplier),
    rpd: Math.floor(baseConfig.rpd * finalMultiplier),
    burst: Math.floor(baseConfig.burst * finalMultiplier),
    concurrency: Math.floor(baseConfig.concurrency * finalMultiplier)
  };
}

/**
 * Rate limit middleware for request processing
 */
export function rateLimitMiddleware(
  getUserTier: (userId: string) => Promise<UserTier>,
  getSystemLoad: () => Promise<number>,
  getUserBehaviorScore: (userId: string) => Promise<number>
) {
  return async (
    userId: string,
    operation?: string,
    identifier?: string
  ): Promise<RateLimitResult> => {
    try {
      const userTier = await getUserTier(userId);
      const systemLoad = await getSystemLoad();
      const behaviorScore = await getUserBehaviorScore(userId);

      // Get adaptive rate limits
      const adaptiveConfig = getAdaptiveRateLimit(userTier, systemLoad, behaviorScore);

      // Override base config temporarily
      const originalConfig = TIER_RATE_LIMITS[userTier as Tier];
      TIER_RATE_LIMITS[userTier as Tier] = adaptiveConfig;

      try {
        const result = checkRateLimit(userId, userTier, operation, identifier);

        // Add adaptive metadata
        if (result.metadata) {
          result.metadata.adaptive = {
            systemLoad,
            behaviorScore,
            adjustmentFactor: adaptiveConfig.rpm / originalConfig.rpm
          };
        }

        return result;
      } finally {
        // Restore original config
        TIER_RATE_LIMITS[userTier as Tier] = originalConfig;
      }

    } catch (error) {
      return {
        allowed: false,
        reason: `Rate limit middleware error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        resetTime: Date.now() + 60000
      };
    }
  };
}

/**
 * Export helper functions for external use
 */
export {
  TIER_RATE_LIMITS,
  OPERATION_RATE_LIMITS,
  acquireConcurrencySlot,
  releaseConcurrencySlot,
  getRateLimitStatus,
  resetRateLimits,
  getAdaptiveRateLimit
};
