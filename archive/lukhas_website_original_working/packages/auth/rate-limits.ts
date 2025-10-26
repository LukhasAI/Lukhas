/**
 * Rate Limiting System for ΛiD Authentication System
 * 
 * Implements tier-based rate limits (T1-T5) with RPM/RPD controls and
 * comprehensive abuse prevention mechanisms.
 */

import { TierLevel, TIER_ENVELOPES } from './scopes';
import { createHash } from 'crypto';

export interface RateLimitRule {
  tier: TierLevel;
  rpm: number;        // Requests per minute
  rpd: number;        // Requests per day
  burstLimit: number; // Burst allowance
  windowMs: number;   // Time window in milliseconds
}

export interface RateLimitConfig {
  enabled: boolean;
  strictMode: boolean;
  alertThreshold: number;
  blockDuration: number;
  whitelistedIPs: string[];
  bypassTiers: TierLevel[];
}

export interface RateLimitEntry {
  key: string;
  count: number;
  resetTime: number;
  dailyCount: number;
  dailyResetTime: number;
  burstCount: number;
  burstResetTime: number;
  blocked: boolean;
  blockExpiry?: number;
}

export interface RateLimitResult {
  allowed: boolean;
  tier: TierLevel;
  remaining: number;
  resetTime: number;
  dailyRemaining: number;
  dailyResetTime: number;
  retryAfter?: number;
  reason?: string;
  metadata?: Record<string, any>;
}

export interface RateLimitContext {
  userId?: string;
  userTier: TierLevel;
  ipAddress: string;
  endpoint: string;
  method: string;
  userAgent?: string;
  apiKey?: string;
}

/**
 * Tier-based rate limit rules derived from TIER_ENVELOPES
 */
export const RATE_LIMIT_RULES: Record<TierLevel, RateLimitRule> = {
  'T1': {
    tier: 'T1',
    rpm: TIER_ENVELOPES.T1.maxRpm,
    rpd: TIER_ENVELOPES.T1.maxRpd,
    burstLimit: Math.floor(TIER_ENVELOPES.T1.maxRpm * 0.5), // 50% burst
    windowMs: 60 * 1000 // 1 minute
  },
  'T2': {
    tier: 'T2',
    rpm: TIER_ENVELOPES.T2.maxRpm,
    rpd: TIER_ENVELOPES.T2.maxRpd,
    burstLimit: Math.floor(TIER_ENVELOPES.T2.maxRpm * 0.5),
    windowMs: 60 * 1000
  },
  'T3': {
    tier: 'T3',
    rpm: TIER_ENVELOPES.T3.maxRpm,
    rpd: TIER_ENVELOPES.T3.maxRpd,
    burstLimit: Math.floor(TIER_ENVELOPES.T3.maxRpm * 0.75), // Higher burst for teams
    windowMs: 60 * 1000
  },
  'T4': {
    tier: 'T4',
    rpm: TIER_ENVELOPES.T4.maxRpm,
    rpd: TIER_ENVELOPES.T4.maxRpd,
    burstLimit: Math.floor(TIER_ENVELOPES.T4.maxRpm * 1.0), // Full burst for enterprise
    windowMs: 60 * 1000
  },
  'T5': {
    tier: 'T5',
    rpm: TIER_ENVELOPES.T5.maxRpm,
    rpd: TIER_ENVELOPES.T5.maxRpd,
    burstLimit: Math.floor(TIER_ENVELOPES.T5.maxRpm * 1.5), // Extra burst for core team
    windowMs: 60 * 1000
  }
};

/**
 * In-memory rate limit store (use Redis in production)
 */
class MemoryRateLimitStore {
  private store: Map<string, RateLimitEntry> = new Map();
  private cleanupInterval?: NodeJS.Timer;

  constructor() {
    // Cleanup expired entries every 5 minutes
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 5 * 60 * 1000);
  }

  get(key: string): RateLimitEntry | undefined {
    return this.store.get(key);
  }

  set(key: string, entry: RateLimitEntry): void {
    this.store.set(key, entry);
  }

  delete(key: string): void {
    this.store.delete(key);
  }

  getAll(): RateLimitEntry[] {
    return Array.from(this.store.values());
  }

  cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.store.entries()) {
      // Remove entries that are past their daily reset and not blocked
      if (now > entry.dailyResetTime && (!entry.blocked || (entry.blockExpiry && now > entry.blockExpiry))) {
        this.store.delete(key);
      }
    }
  }

  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.store.clear();
  }
}

/**
 * Core rate limiting engine
 */
export class RateLimitManager {
  private store: MemoryRateLimitStore;
  private config: RateLimitConfig;

  constructor(config: Partial<RateLimitConfig> = {}) {
    this.store = new MemoryRateLimitStore();
    this.config = {
      enabled: true,
      strictMode: false,
      alertThreshold: 0.8, // Alert at 80% of limit
      blockDuration: 60 * 60 * 1000, // 1 hour
      whitelistedIPs: [],
      bypassTiers: [],
      ...config
    };
  }

  /**
   * Check if request is within rate limits
   */
  async checkRateLimit(context: RateLimitContext): Promise<RateLimitResult> {
    if (!this.config.enabled) {
      return this.createAllowedResult(context.userTier, 'Rate limiting disabled');
    }

    // Check IP whitelist
    if (this.config.whitelistedIPs.includes(context.ipAddress)) {
      return this.createAllowedResult(context.userTier, 'Whitelisted IP');
    }

    // Check tier bypass
    if (this.config.bypassTiers.includes(context.userTier)) {
      return this.createAllowedResult(context.userTier, 'Bypassed tier');
    }

    const rule = RATE_LIMIT_RULES[context.userTier];
    if (!rule) {
      return this.createDeniedResult(context.userTier, 'Invalid tier');
    }

    // Generate composite key for rate limiting
    const key = this.generateKey(context);
    const now = Date.now();

    // Get or create rate limit entry
    let entry = this.store.get(key);
    if (!entry) {
      entry = this.createNewEntry(key, now, rule);
      this.store.set(key, entry);
    }

    // Check if currently blocked
    if (entry.blocked && entry.blockExpiry && now < entry.blockExpiry) {
      return this.createDeniedResult(
        context.userTier,
        'Temporarily blocked',
        {
          retryAfter: Math.ceil((entry.blockExpiry - now) / 1000),
          blockExpiry: entry.blockExpiry
        }
      );
    }

    // Reset counters if windows have expired
    if (now >= entry.resetTime) {
      this.resetMinuteWindow(entry, now, rule);
    }

    if (now >= entry.dailyResetTime) {
      this.resetDailyWindow(entry, now);
    }

    if (now >= entry.burstResetTime) {
      this.resetBurstWindow(entry, now, rule);
    }

    // Check daily limit first
    if (entry.dailyCount >= rule.rpd) {
      entry.blocked = true;
      entry.blockExpiry = entry.dailyResetTime;
      this.store.set(key, entry);
      
      return this.createDeniedResult(
        context.userTier,
        'Daily limit exceeded',
        {
          retryAfter: Math.ceil((entry.dailyResetTime - now) / 1000),
          dailyLimit: rule.rpd
        }
      );
    }

    // Check minute limit
    if (entry.count >= rule.rpm) {
      if (this.config.strictMode) {
        entry.blocked = true;
        entry.blockExpiry = now + this.config.blockDuration;
        this.store.set(key, entry);
        
        return this.createDeniedResult(
          context.userTier,
          'Rate limit exceeded (strict mode)',
          {
            retryAfter: Math.ceil(this.config.blockDuration / 1000)
          }
        );
      } else {
        return this.createDeniedResult(
          context.userTier,
          'Rate limit exceeded',
          {
            retryAfter: Math.ceil((entry.resetTime - now) / 1000)
          }
        );
      }
    }

    // Check burst limit
    if (entry.burstCount >= rule.burstLimit && now < entry.burstResetTime) {
      return this.createDeniedResult(
        context.userTier,
        'Burst limit exceeded',
        {
          retryAfter: Math.ceil((entry.burstResetTime - now) / 1000)
        }
      );
    }

    // Allow request and increment counters
    entry.count++;
    entry.dailyCount++;
    entry.burstCount++;
    this.store.set(key, entry);

    // Check if we need to send alerts
    await this.checkAlertThresholds(context, entry, rule);

    return {
      allowed: true,
      tier: context.userTier,
      remaining: Math.max(0, rule.rpm - entry.count),
      resetTime: entry.resetTime,
      dailyRemaining: Math.max(0, rule.rpd - entry.dailyCount),
      dailyResetTime: entry.dailyResetTime,
      metadata: {
        burstRemaining: Math.max(0, rule.burstLimit - entry.burstCount),
        burstResetTime: entry.burstResetTime
      }
    };
  }

  /**
   * Get rate limit status without incrementing counters
   */
  async getRateLimitStatus(context: RateLimitContext): Promise<RateLimitResult> {
    const key = this.generateKey(context);
    const entry = this.store.get(key);
    const rule = RATE_LIMIT_RULES[context.userTier];

    if (!entry || !rule) {
      return this.createAllowedResult(context.userTier, 'No usage tracked');
    }

    const now = Date.now();

    return {
      allowed: true,
      tier: context.userTier,
      remaining: Math.max(0, rule.rpm - entry.count),
      resetTime: entry.resetTime,
      dailyRemaining: Math.max(0, rule.rpd - entry.dailyCount),
      dailyResetTime: entry.dailyResetTime,
      metadata: {
        currentCount: entry.count,
        dailyCount: entry.dailyCount,
        burstCount: entry.burstCount,
        blocked: entry.blocked,
        blockExpiry: entry.blockExpiry
      }
    };
  }

  /**
   * Reset user's rate limits (admin function)
   */
  async resetUserLimits(userId: string, ipAddress?: string): Promise<boolean> {
    let resetCount = 0;
    
    for (const [key, entry] of this.store.getAll().entries()) {
      if (key.includes(userId) || (ipAddress && key.includes(this.hashIP(ipAddress)))) {
        this.store.delete(key);
        resetCount++;
      }
    }

    return resetCount > 0;
  }

  /**
   * Get rate limit metrics
   */
  getRateLimitMetrics(): {
    totalEntries: number;
    blockedEntries: number;
    tierDistribution: Record<TierLevel, number>;
    topConsumers: Array<{ key: string; count: number; dailyCount: number }>;
  } {
    const entries = this.store.getAll();
    const tierDistribution: Record<TierLevel, number> = {
      'T1': 0, 'T2': 0, 'T3': 0, 'T4': 0, 'T5': 0
    };

    entries.forEach(entry => {
      // Extract tier from key if possible
      const tierMatch = entry.key.match(/tier:(T[1-5])/);
      if (tierMatch) {
        tierDistribution[tierMatch[1] as TierLevel]++;
      }
    });

    const topConsumers = entries
      .sort((a, b) => b.dailyCount - a.dailyCount)
      .slice(0, 10)
      .map(entry => ({
        key: this.sanitizeKeyForLogging(entry.key),
        count: entry.count,
        dailyCount: entry.dailyCount
      }));

    return {
      totalEntries: entries.length,
      blockedEntries: entries.filter(e => e.blocked).length,
      tierDistribution,
      topConsumers
    };
  }

  /**
   * Generate composite key for rate limiting
   */
  private generateKey(context: RateLimitContext): string {
    const parts = [
      `tier:${context.userTier}`,
      `ip:${this.hashIP(context.ipAddress)}`,
      `endpoint:${context.endpoint}`
    ];

    if (context.userId) {
      parts.push(`user:${this.hashUserId(context.userId)}`);
    }

    if (context.apiKey) {
      parts.push(`key:${this.hashApiKey(context.apiKey)}`);
    }

    return parts.join('|');
  }

  /**
   * Create new rate limit entry
   */
  private createNewEntry(key: string, now: number, rule: RateLimitRule): RateLimitEntry {
    return {
      key,
      count: 0,
      resetTime: now + rule.windowMs,
      dailyCount: 0,
      dailyResetTime: this.getNextMidnight(now),
      burstCount: 0,
      burstResetTime: now + (rule.windowMs / 4), // Burst window is 1/4 of main window
      blocked: false
    };
  }

  /**
   * Reset minute window counters
   */
  private resetMinuteWindow(entry: RateLimitEntry, now: number, rule: RateLimitRule): void {
    entry.count = 0;
    entry.resetTime = now + rule.windowMs;
    entry.blocked = false;
    delete entry.blockExpiry;
  }

  /**
   * Reset daily window counters
   */
  private resetDailyWindow(entry: RateLimitEntry, now: number): void {
    entry.dailyCount = 0;
    entry.dailyResetTime = this.getNextMidnight(now);
    entry.blocked = false;
    delete entry.blockExpiry;
  }

  /**
   * Reset burst window counters
   */
  private resetBurstWindow(entry: RateLimitEntry, now: number, rule: RateLimitRule): void {
    entry.burstCount = 0;
    entry.burstResetTime = now + (rule.windowMs / 4);
  }

  /**
   * Create allowed result
   */
  private createAllowedResult(tier: TierLevel, reason: string): RateLimitResult {
    const rule = RATE_LIMIT_RULES[tier];
    const now = Date.now();
    
    return {
      allowed: true,
      tier,
      remaining: rule.rpm,
      resetTime: now + rule.windowMs,
      dailyRemaining: rule.rpd,
      dailyResetTime: this.getNextMidnight(now),
      reason,
      metadata: { bypass: true }
    };
  }

  /**
   * Create denied result
   */
  private createDeniedResult(
    tier: TierLevel, 
    reason: string, 
    metadata?: Record<string, any>
  ): RateLimitResult {
    const now = Date.now();
    
    return {
      allowed: false,
      tier,
      remaining: 0,
      resetTime: now + 60000, // Default 1 minute
      dailyRemaining: 0,
      dailyResetTime: this.getNextMidnight(now),
      reason,
      metadata
    };
  }

  /**
   * Check if we need to send alerts
   */
  private async checkAlertThresholds(
    context: RateLimitContext,
    entry: RateLimitEntry,
    rule: RateLimitRule
  ): Promise<void> {
    const minuteUsage = entry.count / rule.rpm;
    const dailyUsage = entry.dailyCount / rule.rpd;

    if (minuteUsage >= this.config.alertThreshold || dailyUsage >= this.config.alertThreshold) {
      await this.sendUsageAlert({
        tier: context.userTier,
        endpoint: context.endpoint,
        minuteUsage: Math.round(minuteUsage * 100),
        dailyUsage: Math.round(dailyUsage * 100),
        ipAddress: context.ipAddress,
        userAgent: context.userAgent
      });
    }
  }

  /**
   * Send usage alert
   */
  private async sendUsageAlert(alert: any): Promise<void> {
    // TODO: Implement alerting system
    console.warn('🚨 RATE LIMIT ALERT:', JSON.stringify(alert));
  }

  /**
   * Get next midnight timestamp
   */
  private getNextMidnight(now: number): number {
    const tomorrow = new Date(now);
    tomorrow.setUTCHours(24, 0, 0, 0);
    return tomorrow.getTime();
  }

  /**
   * Hash IP address for privacy
   */
  private hashIP(ip: string): string {
    return createHash('sha256').update(ip).digest('hex').slice(0, 16);
  }

  /**
   * Hash user ID for privacy
   */
  private hashUserId(userId: string): string {
    return createHash('sha256').update(userId).digest('hex').slice(0, 16);
  }

  /**
   * Hash API key for privacy
   */
  private hashApiKey(apiKey: string): string {
    return createHash('sha256').update(apiKey).digest('hex').slice(0, 16);
  }

  /**
   * Sanitize key for logging (remove sensitive data)
   */
  private sanitizeKeyForLogging(key: string): string {
    return key.replace(/(user|ip|key):([^|]+)/g, '$1:***');
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    this.store.destroy();
  }
}

/**
 * Helper functions for rate limit management
 */
export class RateLimitUtils {
  /**
   * Calculate optimal rate limits for custom tiers
   */
  static calculateRateLimits(
    baseRpm: number,
    multiplier: number = 1
  ): { rpm: number; rpd: number; burstLimit: number } {
    const rpm = Math.floor(baseRpm * multiplier);
    const rpd = Math.floor(rpm * 24 * 60 * 0.8); // 80% of theoretical max
    const burstLimit = Math.floor(rpm * 0.5); // 50% burst
    
    return { rpm, rpd, burstLimit };
  }

  /**
   * Get rate limit headers for API responses
   */
  static getRateLimitHeaders(result: RateLimitResult): Record<string, string> {
    const headers: Record<string, string> = {
      'X-RateLimit-Tier': result.tier,
      'X-RateLimit-Remaining': result.remaining.toString(),
      'X-RateLimit-Reset': Math.ceil(result.resetTime / 1000).toString(),
      'X-RateLimit-Daily-Remaining': result.dailyRemaining.toString(),
      'X-RateLimit-Daily-Reset': Math.ceil(result.dailyResetTime / 1000).toString()
    };

    if (!result.allowed && result.retryAfter) {
      headers['Retry-After'] = result.retryAfter.toString();
    }

    return headers;
  }

  /**
   * Parse rate limit context from request
   */
  static parseContextFromRequest(
    req: any, // Express request object
    userTier: TierLevel,
    userId?: string
  ): RateLimitContext {
    return {
      userId,
      userTier,
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      endpoint: req.path || req.url,
      method: req.method,
      userAgent: req.get('User-Agent'),
      apiKey: req.get('X-API-Key') || req.query.api_key
    };
  }

  /**
   * Format rate limit error response
   */
  static formatErrorResponse(result: RateLimitResult): {
    error: string;
    message: string;
    retryAfter?: number;
    tier: TierLevel;
  } {
    return {
      error: 'rate_limit_exceeded',
      message: result.reason || 'Rate limit exceeded for your tier',
      retryAfter: result.retryAfter,
      tier: result.tier
    };
  }
}

/**
 * Default rate limit configuration
 */
export const DEFAULT_RATE_LIMIT_CONFIG: RateLimitConfig = {
  enabled: true,
  strictMode: false,
  alertThreshold: 0.8,
  blockDuration: 60 * 60 * 1000, // 1 hour
  whitelistedIPs: ['127.0.0.1', '::1'],
  bypassTiers: []
};

export default RateLimitManager;