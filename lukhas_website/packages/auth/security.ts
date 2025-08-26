/**
 * Security Infrastructure for ΛiD Authentication System
 *
 * Implements rate limiting, enumeration protection, and abuse prevention
 * with production-ready security measures.
 */

import { createHash } from 'crypto';

export interface RateLimitConfig {
  windowMs: number;
  maxAttempts: number;
  blockDurationMs: number;
}

export interface SecurityConfig {
  emailRateLimit: RateLimitConfig;
  ipRateLimit: RateLimitConfig;
  failedAuthLimit: RateLimitConfig;
  preventEnumeration: boolean;
  auditLogging: boolean;
  alertThreshold: number;
}

export interface RateLimitEntry {
  attempts: number;
  firstAttempt: number;
  lastAttempt: number;
  blockedUntil?: number;
}

export interface AuditEvent {
  timestamp: string;
  event: 'login_attempt' | 'magic_link_request' | 'auth_success' | 'auth_failure' | 'rate_limit_hit' | 'enumeration_attempt';
  ip: string;
  email?: string;
  userAgent?: string;
  success: boolean;
  reason?: string;
  metadata?: Record<string, any>;
}

/**
 * In-memory rate limiting store (use Redis in production)
 */
class MemoryRateLimitStore {
  private store: Map<string, RateLimitEntry> = new Map();

  get(key: string): RateLimitEntry | undefined {
    return this.store.get(key);
  }

  set(key: string, entry: RateLimitEntry): void {
    this.store.set(key, entry);
  }

  delete(key: string): void {
    this.store.delete(key);
  }

  cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.store.entries()) {
      // Clean up entries older than 1 hour
      if (now - entry.lastAttempt > 60 * 60 * 1000) {
        this.store.delete(key);
      }
    }
  }
}

export class SecurityManager {
  private config: SecurityConfig;
  private rateLimitStore: MemoryRateLimitStore;
  private auditLog: AuditEvent[] = [];
  private cleanupInterval?: NodeJS.Timer;

  constructor(config: SecurityConfig) {
    this.config = config;
    this.rateLimitStore = new MemoryRateLimitStore();

    // Start cleanup interval
    this.cleanupInterval = setInterval(() => {
      this.rateLimitStore.cleanup();
      this.cleanupAuditLog();
    }, 60 * 60 * 1000); // Every hour
  }

  /**
   * Check if email request is rate limited
   */
  async checkEmailRateLimit(email: string, ip: string): Promise<{ allowed: boolean; resetTime?: number; reason?: string }> {
    const emailKey = `email:${this.hashEmail(email)}`;
    const ipKey = `ip:${this.hashIP(ip)}`;

    // Check email-specific rate limit
    const emailCheck = this.checkRateLimit(emailKey, this.config.emailRateLimit);
    if (!emailCheck.allowed) {
      await this.logAuditEvent({
        event: 'rate_limit_hit',
        ip,
        email,
        success: false,
        reason: 'email_rate_limit',
        metadata: { resetTime: emailCheck.resetTime }
      });
      return emailCheck;
    }

    // Check IP-specific rate limit
    const ipCheck = this.checkRateLimit(ipKey, this.config.ipRateLimit);
    if (!ipCheck.allowed) {
      await this.logAuditEvent({
        event: 'rate_limit_hit',
        ip,
        success: false,
        reason: 'ip_rate_limit',
        metadata: { resetTime: ipCheck.resetTime }
      });
      return ipCheck;
    }

    // Update rate limit counters
    this.updateRateLimit(emailKey, this.config.emailRateLimit);
    this.updateRateLimit(ipKey, this.config.ipRateLimit);

    return { allowed: true };
  }

  /**
   * Check if authentication attempt is rate limited
   */
  async checkAuthRateLimit(identifier: string, ip: string): Promise<{ allowed: boolean; resetTime?: number; reason?: string }> {
    const key = `auth:${identifier}:${this.hashIP(ip)}`;

    const check = this.checkRateLimit(key, this.config.failedAuthLimit);
    if (!check.allowed) {
      await this.logAuditEvent({
        event: 'rate_limit_hit',
        ip,
        success: false,
        reason: 'auth_rate_limit',
        metadata: { resetTime: check.resetTime }
      });
    }

    return check;
  }

  /**
   * Record failed authentication attempt
   */
  async recordFailedAuth(identifier: string, ip: string, reason: string): Promise<void> {
    const key = `auth:${identifier}:${this.hashIP(ip)}`;
    this.updateRateLimit(key, this.config.failedAuthLimit);

    await this.logAuditEvent({
      event: 'auth_failure',
      ip,
      email: identifier,
      success: false,
      reason
    });

    // Check if we need to send alerts
    await this.checkFailureAlerts(ip);
  }

  /**
   * Generate safe response for enumeration protection
   */
  getSafeResponse(email: string): { message: string; success: boolean } {
    if (this.config.preventEnumeration) {
      return {
        message: 'If that email address exists in our system, we\'ve sent you a magic link.',
        success: true
      };
    } else {
      // In development, you might want more specific responses
      return {
        message: 'Magic link sent successfully.',
        success: true
      };
    }
  }

  /**
   * Log security audit event
   */
  async logAuditEvent(event: Omit<AuditEvent, 'timestamp'>): Promise<void> {
    if (!this.config.auditLogging) return;

    const auditEvent: AuditEvent = {
      timestamp: new Date().toISOString(),
      ...event
    };

    this.auditLog.push(auditEvent);

    // In production, write to persistent storage (database, file, etc.)
    if (process.env.NODE_ENV === 'production') {
      // TODO: Implement persistent audit logging
      console.log('AUDIT:', JSON.stringify(auditEvent));
    }
  }

  /**
   * Get recent audit events (for monitoring)
   */
  getAuditEvents(limit: number = 100): AuditEvent[] {
    return this.auditLog.slice(-limit);
  }

  /**
   * Get security metrics
   */
  getSecurityMetrics(): {
    totalEvents: number;
    failedAttempts: number;
    rateLimitHits: number;
    successfulAuths: number;
    recentEvents: AuditEvent[];
  } {
    const events = this.auditLog.slice(-1000); // Last 1000 events

    return {
      totalEvents: events.length,
      failedAttempts: events.filter(e => e.event === 'auth_failure').length,
      rateLimitHits: events.filter(e => e.event === 'rate_limit_hit').length,
      successfulAuths: events.filter(e => e.event === 'auth_success').length,
      recentEvents: events.slice(-20)
    };
  }

  /**
   * Check rate limit for a specific key
   */
  private checkRateLimit(key: string, config: RateLimitConfig): { allowed: boolean; resetTime?: number; reason?: string } {
    const now = Date.now();
    const entry = this.rateLimitStore.get(key);

    if (!entry) {
      return { allowed: true };
    }

    // Check if currently blocked
    if (entry.blockedUntil && now < entry.blockedUntil) {
      return {
        allowed: false,
        resetTime: entry.blockedUntil,
        reason: 'temporarily_blocked'
      };
    }

    // Check if window has expired
    if (now - entry.firstAttempt > config.windowMs) {
      // Window expired, reset
      this.rateLimitStore.delete(key);
      return { allowed: true };
    }

    // Check if within limit
    if (entry.attempts >= config.maxAttempts) {
      // Block for the configured duration
      entry.blockedUntil = now + config.blockDurationMs;
      this.rateLimitStore.set(key, entry);

      return {
        allowed: false,
        resetTime: entry.blockedUntil,
        reason: 'rate_limit_exceeded'
      };
    }

    return { allowed: true };
  }

  /**
   * Update rate limit counter
   */
  private updateRateLimit(key: string, config: RateLimitConfig): void {
    const now = Date.now();
    const entry = this.rateLimitStore.get(key);

    if (!entry || now - entry.firstAttempt > config.windowMs) {
      // New or expired entry
      this.rateLimitStore.set(key, {
        attempts: 1,
        firstAttempt: now,
        lastAttempt: now
      });
    } else {
      // Update existing entry
      entry.attempts++;
      entry.lastAttempt = now;
      this.rateLimitStore.set(key, entry);
    }
  }

  /**
   * Hash email for privacy in rate limiting
   */
  private hashEmail(email: string): string {
    return createHash('sha256').update(email.toLowerCase()).digest('hex').slice(0, 16);
  }

  /**
   * Hash IP address for privacy in rate limiting
   */
  private hashIP(ip: string): string {
    return createHash('sha256').update(ip).digest('hex').slice(0, 16);
  }

  /**
   * Check if failure rate requires alerting
   */
  private async checkFailureAlerts(ip: string): Promise<void> {
    const recentFailures = this.auditLog
      .filter(event =>
        event.ip === ip &&
        event.event === 'auth_failure' &&
        Date.now() - new Date(event.timestamp).getTime() < 60 * 60 * 1000 // Last hour
      )
      .length;

    if (recentFailures >= this.config.alertThreshold) {
      await this.sendSecurityAlert({
        type: 'high_failure_rate',
        ip,
        failureCount: recentFailures,
        timeWindow: '1 hour'
      });
    }
  }

  /**
   * Send security alert (implement with your alerting system)
   */
  private async sendSecurityAlert(alert: any): Promise<void> {
    // TODO: Implement alerting (Slack, email, PagerDuty, etc.)
    console.warn('🚨 SECURITY ALERT:', JSON.stringify(alert));
  }

  /**
   * Clean up old audit log entries
   */
  private cleanupAuditLog(): void {
    const retentionMs = (this.config.auditLogging ? 365 : 30) * 24 * 60 * 60 * 1000; // 365 days or 30 days
    const cutoff = Date.now() - retentionMs;

    this.auditLog = this.auditLog.filter(event =>
      new Date(event.timestamp).getTime() > cutoff
    );
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

/**
 * Default security configuration
 */
export const DEFAULT_SECURITY_CONFIG: SecurityConfig = {
  emailRateLimit: {
    windowMs: 60 * 60 * 1000, // 1 hour
    maxAttempts: 3,
    blockDurationMs: 60 * 60 * 1000 // 1 hour
  },
  ipRateLimit: {
    windowMs: 60 * 60 * 1000, // 1 hour
    maxAttempts: 5,
    blockDurationMs: 60 * 60 * 1000 // 1 hour
  },
  failedAuthLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    maxAttempts: 5,
    blockDurationMs: 30 * 60 * 1000 // 30 minutes
  },
  preventEnumeration: true,
  auditLogging: true,
  alertThreshold: 5
};

export default SecurityManager;
