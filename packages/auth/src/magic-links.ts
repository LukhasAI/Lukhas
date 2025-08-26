/**
 * ΛiD Authentication System - Magic Links
 *
 * One-time tokens with TTL 600s, IP/email throttling and security features
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

import {
  MagicLinkToken,
  MagicLinkOptions,
  MagicLinkResult,
  MagicLinkValidationResult,
  ThrottleConfig,
  SecurityEvent
} from '../types/auth.types';
import { checkRateLimit } from './rate-limits';
import { UserTier } from '../types/auth.types';

/**
 * Magic link configuration
 */
export interface MagicLinkConfig {
  tokenTTL: number;           // Token time-to-live in seconds
  maxAttempts: number;        // Max attempts per email/IP
  attemptWindow: number;      // Time window for attempt counting (seconds)
  secretLength: number;       // Length of generated secrets
  ipThrottleLimit: number;    // Max requests per IP per window
  emailThrottleLimit: number; // Max requests per email per window
  baseUrl: string;           // Base URL for magic links
  templatePath: string;       // Email template path
}

/**
 * Default magic link configuration
 */
export const DEFAULT_MAGIC_LINK_CONFIG: MagicLinkConfig = {
  tokenTTL: 600,             // 10 minutes
  maxAttempts: 5,            // 5 attempts max
  attemptWindow: 3600,       // 1 hour window
  secretLength: 32,          // 32 character secrets
  ipThrottleLimit: 10,       // 10 requests per IP per hour
  emailThrottleLimit: 3,     // 3 requests per email per hour
  baseUrl: 'https://lukhas.ai',
  templatePath: '/templates/magic-link'
};

/**
 * Throttle tracking for IPs and emails
 */
interface ThrottleEntry {
  count: number;
  firstAttempt: number;
  lastAttempt: number;
  blocked: boolean;
  blockExpiry?: number;
}

/**
 * Magic link token store
 */
interface TokenEntry {
  token: string;
  email: string;
  userId?: string;
  purpose: 'login' | 'register' | 'password-reset' | 'email-verification';
  createdAt: number;
  expiresAt: number;
  attempts: number;
  maxAttempts: number;
  ipAddress: string;
  userAgent: string;
  metadata?: Record<string, any>;
  used: boolean;
  usedAt?: number;
}

/**
 * In-memory stores (in production, use Redis/database)
 */
class MagicLinkStore {
  private tokens = new Map<string, TokenEntry>();
  private ipThrottles = new Map<string, ThrottleEntry>();
  private emailThrottles = new Map<string, ThrottleEntry>();
  private securityEvents: SecurityEvent[] = [];

  constructor(private config: MagicLinkConfig) {
    // Cleanup expired entries every minute
    setInterval(() => this.cleanup(), 60000);
  }

  /**
   * Store a magic link token
   */
  storeToken(tokenEntry: TokenEntry): void {
    this.tokens.set(tokenEntry.token, tokenEntry);
  }

  /**
   * Get token entry
   */
  getToken(token: string): TokenEntry | null {
    const entry = this.tokens.get(token);
    if (!entry) return null;

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.tokens.delete(token);
      return null;
    }

    return entry;
  }

  /**
   * Mark token as used
   */
  useToken(token: string): boolean {
    const entry = this.getToken(token);
    if (!entry || entry.used) return false;

    entry.used = true;
    entry.usedAt = Date.now();
    this.tokens.set(token, entry);
    return true;
  }

  /**
   * Check IP throttle
   */
  checkIPThrottle(ip: string): { allowed: boolean; reason?: string; resetTime?: number } {
    const entry = this.ipThrottles.get(ip);
    const now = Date.now();
    const windowStart = now - (this.config.attemptWindow * 1000);

    if (!entry) {
      this.ipThrottles.set(ip, {
        count: 1,
        firstAttempt: now,
        lastAttempt: now,
        blocked: false
      });
      return { allowed: true };
    }

    // Check if outside window - reset counter
    if (entry.firstAttempt < windowStart) {
      this.ipThrottles.set(ip, {
        count: 1,
        firstAttempt: now,
        lastAttempt: now,
        blocked: false
      });
      return { allowed: true };
    }

    // Check if blocked
    if (entry.blocked && entry.blockExpiry && now < entry.blockExpiry) {
      return {
        allowed: false,
        reason: 'IP temporarily blocked',
        resetTime: entry.blockExpiry
      };
    }

    // Check limit
    if (entry.count >= this.config.ipThrottleLimit) {
      const blockExpiry = now + (this.config.attemptWindow * 1000);
      this.ipThrottles.set(ip, {
        ...entry,
        blocked: true,
        blockExpiry
      });

      this.logSecurityEvent('IP_THROTTLE_EXCEEDED', { ip, count: entry.count });

      return {
        allowed: false,
        reason: 'Too many requests from this IP',
        resetTime: blockExpiry
      };
    }

    // Increment counter
    entry.count++;
    entry.lastAttempt = now;
    this.ipThrottles.set(ip, entry);

    return { allowed: true };
  }

  /**
   * Check email throttle
   */
  checkEmailThrottle(email: string): { allowed: boolean; reason?: string; resetTime?: number } {
    const entry = this.emailThrottles.get(email);
    const now = Date.now();
    const windowStart = now - (this.config.attemptWindow * 1000);

    if (!entry) {
      this.emailThrottles.set(email, {
        count: 1,
        firstAttempt: now,
        lastAttempt: now,
        blocked: false
      });
      return { allowed: true };
    }

    // Check if outside window - reset counter
    if (entry.firstAttempt < windowStart) {
      this.emailThrottles.set(email, {
        count: 1,
        firstAttempt: now,
        lastAttempt: now,
        blocked: false
      });
      return { allowed: true };
    }

    // Check if blocked
    if (entry.blocked && entry.blockExpiry && now < entry.blockExpiry) {
      return {
        allowed: false,
        reason: 'Email temporarily blocked',
        resetTime: entry.blockExpiry
      };
    }

    // Check limit
    if (entry.count >= this.config.emailThrottleLimit) {
      const blockExpiry = now + (this.config.attemptWindow * 1000);
      this.emailThrottles.set(email, {
        ...entry,
        blocked: true,
        blockExpiry
      });

      this.logSecurityEvent('EMAIL_THROTTLE_EXCEEDED', { email, count: entry.count });

      return {
        allowed: false,
        reason: 'Too many requests for this email',
        resetTime: blockExpiry
      };
    }

    // Increment counter
    entry.count++;
    entry.lastAttempt = now;
    this.emailThrottles.set(email, entry);

    return { allowed: true };
  }

  /**
   * Get throttle status
   */
  getThrottleStatus(ip: string, email: string): {
    ip: { count: number; limit: number; resetTime?: number };
    email: { count: number; limit: number; resetTime?: number };
  } {
    const ipEntry = this.ipThrottles.get(ip);
    const emailEntry = this.emailThrottles.get(email);
    const now = Date.now();
    const windowStart = now - (this.config.attemptWindow * 1000);

    return {
      ip: {
        count: (ipEntry && ipEntry.firstAttempt >= windowStart) ? ipEntry.count : 0,
        limit: this.config.ipThrottleLimit,
        resetTime: ipEntry?.blockExpiry
      },
      email: {
        count: (emailEntry && emailEntry.firstAttempt >= windowStart) ? emailEntry.count : 0,
        limit: this.config.emailThrottleLimit,
        resetTime: emailEntry?.blockExpiry
      }
    };
  }

  /**
   * Log security events
   */
  logSecurityEvent(type: string, metadata: Record<string, any>): void {
    const event: SecurityEvent = {
      id: `sec_${Date.now()}_${Math.random().toString(36).substring(2)}`,
      type,
      timestamp: new Date().toISOString(),
      metadata,
      severity: 'medium'
    };

    this.securityEvents.push(event);

    // Keep only recent events (last 1000)
    if (this.securityEvents.length > 1000) {
      this.securityEvents.splice(0, this.securityEvents.length - 1000);
    }

    console.log('[ΛiD MAGIC LINKS SECURITY]', JSON.stringify(event));
  }

  /**
   * Cleanup expired entries
   */
  cleanup(): void {
    const now = Date.now();

    // Cleanup tokens
    for (const [token, entry] of this.tokens.entries()) {
      if (now > entry.expiresAt) {
        this.tokens.delete(token);
      }
    }

    // Cleanup throttles
    const windowStart = now - (this.config.attemptWindow * 1000);

    for (const [ip, entry] of this.ipThrottles.entries()) {
      if (entry.firstAttempt < windowStart && (!entry.blockExpiry || now > entry.blockExpiry)) {
        this.ipThrottles.delete(ip);
      }
    }

    for (const [email, entry] of this.emailThrottles.entries()) {
      if (entry.firstAttempt < windowStart && (!entry.blockExpiry || now > entry.blockExpiry)) {
        this.emailThrottles.delete(email);
      }
    }
  }
}

/**
 * Magic Link Manager
 */
export class MagicLinkManager {
  private store: MagicLinkStore;
  private config: MagicLinkConfig;

  constructor(config: MagicLinkConfig = DEFAULT_MAGIC_LINK_CONFIG) {
    this.config = config;
    this.store = new MagicLinkStore(config);
  }

  /**
   * Generate magic link token
   */
  async generateMagicLink(
    email: string,
    purpose: 'login' | 'register' | 'password-reset' | 'email-verification',
    options: MagicLinkOptions
  ): Promise<MagicLinkResult> {
    try {
      // Check IP throttle
      const ipCheck = this.store.checkIPThrottle(options.ipAddress);
      if (!ipCheck.allowed) {
        return {
          success: false,
          reason: ipCheck.reason || 'IP throttled',
          resetTime: ipCheck.resetTime
        };
      }

      // Check email throttle
      const emailCheck = this.store.checkEmailThrottle(email);
      if (!emailCheck.allowed) {
        return {
          success: false,
          reason: emailCheck.reason || 'Email throttled',
          resetTime: emailCheck.resetTime
        };
      }

      // Check user tier rate limits if userId provided
      if (options.userId && options.userTier) {
        const rateLimitResult = checkRateLimit(
          options.userId,
          options.userTier,
          'auth:magic-link',
          options.ipAddress
        );

        if (!rateLimitResult.allowed) {
          return {
            success: false,
            reason: 'Rate limit exceeded',
            resetTime: rateLimitResult.resetTime
          };
        }
      }

      // Generate secure token
      const token = this.generateSecureToken();
      const now = Date.now();
      const expiresAt = now + (this.config.tokenTTL * 1000);

      // Create token entry
      const tokenEntry: TokenEntry = {
        token,
        email,
        userId: options.userId,
        purpose,
        createdAt: now,
        expiresAt,
        attempts: 0,
        maxAttempts: options.maxAttempts || 3,
        ipAddress: options.ipAddress,
        userAgent: options.userAgent,
        metadata: options.metadata,
        used: false
      };

      // Store token
      this.store.storeToken(tokenEntry);

      // Generate magic link URL
      const magicLink = this.generateMagicLinkURL(token, purpose);

      // Log security event
      this.store.logSecurityEvent('MAGIC_LINK_GENERATED', {
        email,
        purpose,
        ipAddress: options.ipAddress,
        userAgent: options.userAgent
      });

      return {
        success: true,
        token,
        magicLink,
        expiresAt: new Date(expiresAt).toISOString(),
        expiresIn: this.config.tokenTTL
      };

    } catch (error) {
      return {
        success: false,
        reason: `Failed to generate magic link: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Validate magic link token
   */
  async validateMagicLink(
    token: string,
    ipAddress: string,
    userAgent: string
  ): Promise<MagicLinkValidationResult> {
    try {
      // Get token entry
      const entry = this.store.getToken(token);
      if (!entry) {
        this.store.logSecurityEvent('MAGIC_LINK_INVALID_TOKEN', { token, ipAddress });
        return {
          valid: false,
          reason: 'Invalid or expired token'
        };
      }

      // Check if already used
      if (entry.used) {
        this.store.logSecurityEvent('MAGIC_LINK_REUSE_ATTEMPT', {
          token,
          email: entry.email,
          ipAddress,
          originalIP: entry.ipAddress
        });
        return {
          valid: false,
          reason: 'Token already used'
        };
      }

      // Check attempt limit
      if (entry.attempts >= entry.maxAttempts) {
        this.store.logSecurityEvent('MAGIC_LINK_MAX_ATTEMPTS', {
          token,
          email: entry.email,
          attempts: entry.attempts
        });
        return {
          valid: false,
          reason: 'Maximum attempts exceeded'
        };
      }

      // Increment attempt counter
      entry.attempts++;

      // Optional: Strict IP checking (can be disabled for mobile users)
      const strictIPCheck = entry.metadata?.strictIPCheck !== false;
      if (strictIPCheck && entry.ipAddress !== ipAddress) {
        this.store.logSecurityEvent('MAGIC_LINK_IP_MISMATCH', {
          token,
          email: entry.email,
          originalIP: entry.ipAddress,
          currentIP: ipAddress
        });

        // Don't fail immediately - log but allow (configurable behavior)
        if (entry.metadata?.allowIPChange !== true) {
          return {
            valid: false,
            reason: 'IP address mismatch'
          };
        }
      }

      // Mark as used
      if (!this.store.useToken(token)) {
        return {
          valid: false,
          reason: 'Failed to consume token'
        };
      }

      // Log successful validation
      this.store.logSecurityEvent('MAGIC_LINK_VALIDATED', {
        token,
        email: entry.email,
        purpose: entry.purpose,
        ipAddress
      });

      return {
        valid: true,
        email: entry.email,
        userId: entry.userId,
        purpose: entry.purpose,
        metadata: entry.metadata
      };

    } catch (error) {
      return {
        valid: false,
        reason: `Validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Get magic link status
   */
  async getMagicLinkStatus(token: string): Promise<{
    exists: boolean;
    used?: boolean;
    expired?: boolean;
    attempts?: number;
    maxAttempts?: number;
    expiresAt?: string;
  }> {
    const entry = this.store.getToken(token);

    if (!entry) {
      return { exists: false };
    }

    const now = Date.now();

    return {
      exists: true,
      used: entry.used,
      expired: now > entry.expiresAt,
      attempts: entry.attempts,
      maxAttempts: entry.maxAttempts,
      expiresAt: new Date(entry.expiresAt).toISOString()
    };
  }

  /**
   * Revoke magic link token
   */
  async revokeMagicLink(token: string, reason: string): Promise<boolean> {
    const entry = this.store.getToken(token);
    if (!entry) return false;

    // Mark as used to prevent further use
    const revoked = this.store.useToken(token);

    if (revoked) {
      this.store.logSecurityEvent('MAGIC_LINK_REVOKED', {
        token,
        email: entry.email,
        reason
      });
    }

    return revoked;
  }

  /**
   * Get throttle status for IP/email
   */
  async getThrottleStatus(ip: string, email: string): Promise<{
    ip: { count: number; limit: number; resetTime?: number };
    email: { count: number; limit: number; resetTime?: number };
  }> {
    return this.store.getThrottleStatus(ip, email);
  }

  /**
   * Reset throttles (admin function)
   */
  async resetThrottles(ip?: string, email?: string): Promise<void> {
    if (ip) {
      this.store['ipThrottles'].delete(ip);
    }

    if (email) {
      this.store['emailThrottles'].delete(email);
    }

    this.store.logSecurityEvent('THROTTLES_RESET', { ip, email });
  }

  // Private helper methods

  private generateSecureToken(): string {
    // Generate cryptographically secure random token
    const array = new Uint8Array(this.config.secretLength);
    crypto.getRandomValues(array);

    return Array.from(array, byte =>
      byte.toString(16).padStart(2, '0')
    ).join('');
  }

  private generateMagicLinkURL(token: string, purpose: string): string {
    const params = new URLSearchParams({
      token,
      purpose
    });

    return `${this.config.baseUrl}/auth/magic-link?${params.toString()}`;
  }
}

/**
 * Global magic link manager instance
 */
export const magicLinkManager = new MagicLinkManager();

/**
 * Convenience functions for magic link operations
 */

/**
 * Send magic link
 */
export async function sendMagicLink(
  email: string,
  purpose: 'login' | 'register' | 'password-reset' | 'email-verification',
  options: MagicLinkOptions
): Promise<MagicLinkResult> {
  return magicLinkManager.generateMagicLink(email, purpose, options);
}

/**
 * Verify magic link
 */
export async function verifyMagicLink(
  token: string,
  ipAddress: string,
  userAgent: string
): Promise<MagicLinkValidationResult> {
  return magicLinkManager.validateMagicLink(token, ipAddress, userAgent);
}

/**
 * Check magic link status
 */
export async function checkMagicLinkStatus(token: string): Promise<{
  exists: boolean;
  used?: boolean;
  expired?: boolean;
  attempts?: number;
  maxAttempts?: number;
  expiresAt?: string;
}> {
  return magicLinkManager.getMagicLinkStatus(token);
}

/**
 * Revoke magic link
 */
export async function revokeMagicLink(token: string, reason: string): Promise<boolean> {
  return magicLinkManager.revokeMagicLink(token, reason);
}

/**
 * Get current throttle limits
 */
export async function getThrottleLimits(ip: string, email: string): Promise<{
  ip: { count: number; limit: number; resetTime?: number };
  email: { count: number; limit: number; resetTime?: number };
}> {
  return magicLinkManager.getThrottleStatus(ip, email);
}

/**
 * Email sending helper (integrate with email service)
 */
export async function sendMagicLinkEmail(
  email: string,
  magicLink: string,
  purpose: string,
  metadata?: Record<string, any>
): Promise<boolean> {
  try {
    // In production, integrate with email service (SendGrid, AWS SES, etc.)
    const emailContent = {
      to: email,
      subject: `Your ${purpose} link for LUKHAS AI`,
      html: generateEmailHTML(magicLink, purpose, metadata),
      text: generateEmailText(magicLink, purpose, metadata)
    };

    console.log('[ΛiD MAGIC LINKS] Email would be sent:', emailContent);

    // Placeholder for actual email sending
    return true;
  } catch (error) {
    console.error('Failed to send magic link email:', error);
    return false;
  }
}

/**
 * Generate HTML email content
 */
function generateEmailHTML(magicLink: string, purpose: string, metadata?: Record<string, any>): string {
  return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LUKHAS AI - Magic Link</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 16px; }
        .content { margin: 30px 0; }
        .button { display: inline-block; background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
        .button:hover { background: #0056b3; }
        .security { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; font-size: 14px; color: #666; }
        .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">⚛️ LUKHAS AI</div>
            <div class="subtitle">Consciousness-Aware Authentication</div>
        </div>

        <div class="content">
            <h2>Your ${purpose} link is ready</h2>
            <p>Click the button below to ${purpose} to your LUKHAS AI account:</p>

            <div style="text-align: center;">
                <a href="${magicLink}" class="button">Complete ${purpose}</a>
            </div>

            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace; font-size: 12px;">
                ${magicLink}
            </p>
        </div>

        <div class="security">
            <strong>🛡️ Security Notice:</strong> This link will expire in 10 minutes and can only be used once.
            If you didn't request this ${purpose}, please ignore this email.
        </div>

        <div class="footer">
            <p>LUKHAS AI - Trinity Framework (⚛️🧠🛡️)</p>
            <p>This email was sent as part of your authentication request.</p>
        </div>
    </div>
</body>
</html>`;
}

/**
 * Generate plain text email content
 */
function generateEmailText(magicLink: string, purpose: string, metadata?: Record<string, any>): string {
  return `
LUKHAS AI - Your ${purpose} link

Click this link to ${purpose} to your LUKHAS AI account:
${magicLink}

Security Notice: This link will expire in 10 minutes and can only be used once.
If you didn't request this ${purpose}, please ignore this email.

---
LUKHAS AI - Trinity Framework (⚛️🧠🛡️)
This email was sent as part of your authentication request.
`;
}
