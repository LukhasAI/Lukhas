/**
 * Security Infrastructure for ΛiD Authentication System
 *
 * Implements rate limiting, enumeration protection, and abuse prevention
 * with production-ready security measures.
 */

import { createHash } from 'crypto';
import AuditLogger from './audit-logger';
import { DatabaseInterface, CreateSecurityEventInput } from './database';

export interface AlertConfig {
  enabled: boolean;
  webhookUrl?: string;
  slackWebhook?: string;
  emailRecipients?: string[];
  alertThresholds: {
    failedAuthAttempts: number;
    rateLimitHits: number;
    suspiciousActivity: number;
  };
}

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
  alertConfig?: AlertConfig;
  db?: DatabaseInterface;
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
  private db?: DatabaseInterface;

  constructor(config: SecurityConfig) {
    this.config = config;
    this.rateLimitStore = new MemoryRateLimitStore();
    this.db = config.db;

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
   * Log security audit event with persistent storage
   */
  async logAuditEvent(event: Omit<AuditEvent, 'timestamp'>): Promise<void> {
    if (!this.config.auditLogging) return;

    const auditEvent: AuditEvent = {
      timestamp: new Date().toISOString(),
      ...event
    };

    this.auditLog.push(auditEvent);

    // Persistent audit logging to database
    if (this.db) {
      try {
        const securityEvent: CreateSecurityEventInput = {
          user_id: event.email,
          event_type: event.event as any,
          severity: event.success ? 'info' : 'warning',
          description: event.reason || `${event.event} event`,
          result: event.success ? 'success' : 'failure',
          ip_address: event.ip,
          user_agent: event.userAgent,
          event_timestamp: new Date(),
          metadata: event.metadata || {}
        };

        await this.db.createSecurityEvent(securityEvent);
      } catch (error) {
        console.error('[SecurityManager] Failed to persist audit event to database:', error);
      }
    }

    // Also log via AuditLogger for comprehensive trail
    await AuditLogger.logSecurityEvent({
      eventType: this.mapEventTypeToAuditType(event.event),
      description: event.reason || `${event.event} event`,
      context: {
        ipAddress: event.ip,
        userAgent: event.userAgent || 'Unknown'
      },
      actionTaken: event.success ? 'allowed' : 'blocked',
      metadata: event.metadata
    });

    // Write to file in production for backup
    if (process.env.NODE_ENV === 'production') {
      this.writeAuditToFile(auditEvent);
    }
  }

  /**
   * Map security event type to audit log event type
   */
  private mapEventTypeToAuditType(eventType: string): any {
    const mapping: Record<string, string> = {
      'login_attempt': 'auth_login_failure',
      'magic_link_request': 'auth_login_success',
      'auth_success': 'auth_login_success',
      'auth_failure': 'auth_login_failure',
      'rate_limit_hit': 'security_rate_limit_exceeded',
      'enumeration_attempt': 'security_suspicious_activity'
    };

    return mapping[eventType] || 'security_suspicious_activity';
  }

  /**
   * Write audit event to file for backup
   */
  private async writeAuditToFile(event: AuditEvent): Promise<void> {
    try {
      const logDir = process.env.AUDIT_LOG_DIR || './logs/security';
      const logFile = `${logDir}/security-${new Date().toISOString().split('T')[0]}.log`;

      // Ensure directory exists
      const fs = await import('fs/promises');
      await fs.mkdir(logDir, { recursive: true });

      // Append audit event
      const logLine = JSON.stringify(event) + '\n';
      await fs.appendFile(logFile, logLine, 'utf8');
    } catch (error) {
      console.error('[SecurityManager] Failed to write audit to file:', error);
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
   * Send security alert to configured channels
   */
  private async sendSecurityAlert(alert: any): Promise<void> {
    const alertConfig = this.config.alertConfig;

    if (!alertConfig || !alertConfig.enabled) {
      console.warn('🚨 SECURITY ALERT (alerting disabled):', JSON.stringify(alert));
      return;
    }

    // Send to Slack
    if (alertConfig.slackWebhook) {
      await this.sendSlackAlert(alertConfig.slackWebhook, alert);
    }

    // Send to generic webhook
    if (alertConfig.webhookUrl) {
      await this.sendWebhookAlert(alertConfig.webhookUrl, alert);
    }

    // Send via email
    if (alertConfig.emailRecipients?.length) {
      await this.sendEmailAlert(alertConfig.emailRecipients, alert);
    }

    // Log to audit trail
    await AuditLogger.logSecurityEvent({
      eventType: 'security_anomaly_detected',
      description: `Security alert triggered: ${alert.type}`,
      context: {
        ipAddress: alert.ip || 'system',
        userAgent: 'security_monitor'
      },
      riskScore: this.calculateRiskScore(alert),
      actionTaken: 'alert_sent',
      metadata: alert
    });

    console.warn('🚨 SECURITY ALERT:', JSON.stringify(alert));
  }

  /**
   * Send alert to Slack
   */
  private async sendSlackAlert(webhookUrl: string, alert: any): Promise<void> {
    try {
      const payload = {
        text: `🚨 Security Alert: ${alert.type}`,
        blocks: [
          {
            type: 'header',
            text: {
              type: 'plain_text',
              text: `🚨 Security Alert: ${alert.type}`,
              emoji: true
            }
          },
          {
            type: 'section',
            fields: [
              { type: 'mrkdwn', text: `*IP Address:*\n${alert.ip}` },
              { type: 'mrkdwn', text: `*Failure Count:*\n${alert.failureCount}` },
              { type: 'mrkdwn', text: `*Time Window:*\n${alert.timeWindow}` },
              { type: 'mrkdwn', text: `*Timestamp:*\n${new Date().toISOString()}` }
            ]
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `*Details:*\n\`\`\`${JSON.stringify(alert, null, 2)}\`\`\``
            }
          }
        ]
      };

      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Slack webhook failed: ${response.statusText}`);
      }

      console.log('[SecurityManager] Slack alert sent successfully');
    } catch (error) {
      console.error('[SecurityManager] Failed to send Slack alert:', error);
    }
  }

  /**
   * Send alert to generic webhook
   */
  private async sendWebhookAlert(webhookUrl: string, alert: any): Promise<void> {
    try {
      const payload = {
        type: 'security_alert',
        severity: 'high',
        timestamp: new Date().toISOString(),
        alert
      };

      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Webhook failed: ${response.statusText}`);
      }

      console.log('[SecurityManager] Webhook alert sent successfully');
    } catch (error) {
      console.error('[SecurityManager] Failed to send webhook alert:', error);
    }
  }

  /**
   * Send alert via email
   */
  private async sendEmailAlert(recipients: string[], alert: any): Promise<void> {
    try {
      // Import email service dynamically to avoid circular dependencies
      const { createEmailServiceFromEnv } = await import('./email-service');
      const emailService = createEmailServiceFromEnv();

      for (const recipient of recipients) {
        await emailService.sendEmail({
          to: recipient,
          template: {
            subject: `🚨 Security Alert: ${alert.type}`,
            htmlBody: `
              <h2>Security Alert</h2>
              <p><strong>Type:</strong> ${alert.type}</p>
              <p><strong>IP Address:</strong> ${alert.ip}</p>
              <p><strong>Failure Count:</strong> ${alert.failureCount}</p>
              <p><strong>Time Window:</strong> ${alert.timeWindow}</p>
              <p><strong>Timestamp:</strong> ${new Date().toISOString()}</p>
              <pre>${JSON.stringify(alert, null, 2)}</pre>
            `,
            textBody: `
Security Alert: ${alert.type}
IP Address: ${alert.ip}
Failure Count: ${alert.failureCount}
Time Window: ${alert.timeWindow}
Timestamp: ${new Date().toISOString()}

Details:
${JSON.stringify(alert, null, 2)}
            `
          }
        });
      }

      console.log('[SecurityManager] Email alerts sent successfully');
    } catch (error) {
      console.error('[SecurityManager] Failed to send email alerts:', error);
    }
  }

  /**
   * Calculate risk score for alert
   */
  private calculateRiskScore(alert: any): number {
    let score = 0;

    // Higher failure count = higher risk
    if (alert.failureCount >= 10) score += 0.5;
    else if (alert.failureCount >= 5) score += 0.3;
    else score += 0.1;

    // Add risk based on alert type
    if (alert.type === 'high_failure_rate') score += 0.3;
    if (alert.type === 'suspicious_pattern') score += 0.2;

    return Math.min(1.0, score);
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
