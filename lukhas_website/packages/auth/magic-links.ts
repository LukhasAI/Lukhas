/**
 * Magic Link Authentication for ΛiD Authentication System
 * 
 * Implements secure one-time magic links with TTL 600s, IP/email throttling,
 * and comprehensive abuse prevention mechanisms.
 */

import { TierLevel } from './scopes';
import { SecurityManager, SecurityConfig } from './security';
import { createHash, randomBytes, timingSafeEqual } from 'crypto';

export interface MagicLinkToken {
  id: string;                    // Unique token ID
  token: string;                 // Base64url encoded token
  tokenHash: string;             // SHA-256 hash of token (stored)
  email: string;                 // Target email address
  emailHash: string;             // Hashed email for privacy
  userId?: string;               // User ID if known
  purpose: 'login' | 'signup' | 'verify' | 'reset' | 'invite';
  createdAt: number;             // Unix timestamp
  expiresAt: number;             // Unix timestamp
  usedAt?: number;               // Unix timestamp when used
  ipAddress: string;             // IP address that requested token
  ipHash: string;                // Hashed IP for privacy
  userAgent: string;             // User agent string
  attempts: number;              // Number of use attempts
  maxAttempts: number;           // Maximum allowed attempts
  tier: TierLevel;               // User tier for rate limiting
  metadata: {
    redirectUrl?: string;        // Post-auth redirect URL
    sessionId?: string;          // Associated session ID
    deviceFingerprint?: string;  // Device fingerprint
    customData?: Record<string, any>; // Custom application data
  };
}

export interface MagicLinkConfig {
  tokenTTL: number;              // Token TTL in seconds (default: 600)
  maxAttempts: number;           // Max attempts per token (default: 3)
  cleanupInterval: number;       // Cleanup interval in ms (default: 5 minutes)
  baseUrl: string;               // Base URL for magic links
  fromEmail: string;             // From email address
  rateLimiting: {
    emailWindow: number;         // Email rate limit window (seconds)
    emailLimit: number;          // Max emails per window
    ipWindow: number;            // IP rate limit window (seconds)
    ipLimit: number;             // Max requests per IP per window
  };
  security: {
    requireSameIP: boolean;      // Require same IP for token use
    requireSameDevice: boolean;  // Require same device fingerprint
    allowedDomains: string[];    // Allowed email domains (empty = all)
    blockedDomains: string[];    // Blocked email domains
  };
}

export interface MagicLinkRequest {
  email: string;
  purpose: 'login' | 'signup' | 'verify' | 'reset' | 'invite';
  tier: TierLevel;
  ipAddress: string;
  userAgent: string;
  redirectUrl?: string;
  deviceFingerprint?: string;
  customData?: Record<string, any>;
}

export interface MagicLinkResult {
  success: boolean;
  tokenId?: string;
  expiresAt?: number;
  expiresIn?: number;
  reason?: string;
  retryAfter?: number;
  metadata?: Record<string, any>;
}

export interface MagicLinkValidation {
  valid: boolean;
  token?: MagicLinkToken;
  email?: string;
  userId?: string;
  purpose?: string;
  tier?: TierLevel;
  metadata?: Record<string, any>;
  error?: string;
  expired?: boolean;
  exhausted?: boolean;
}

/**
 * In-memory token store (use Redis in production)
 */
class MagicLinkStore {
  private tokens: Map<string, MagicLinkToken> = new Map();
  private emailIndex: Map<string, Set<string>> = new Map(); // email hash -> token IDs
  private cleanupInterval?: NodeJS.Timer;

  constructor(cleanupIntervalMs: number = 5 * 60 * 1000) {
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, cleanupIntervalMs);
  }

  store(token: MagicLinkToken): void {
    this.tokens.set(token.id, token);
    
    // Update email index
    const emailTokens = this.emailIndex.get(token.emailHash) || new Set();
    emailTokens.add(token.id);
    this.emailIndex.set(token.emailHash, emailTokens);
  }

  get(tokenId: string): MagicLinkToken | undefined {
    return this.tokens.get(tokenId);
  }

  getByToken(tokenHash: string): MagicLinkToken | undefined {
    for (const token of this.tokens.values()) {
      if (token.tokenHash === tokenHash) {
        return token;
      }
    }
    return undefined;
  }

  getActiveTokensForEmail(emailHash: string): MagicLinkToken[] {
    const tokenIds = this.emailIndex.get(emailHash) || new Set();
    const tokens: MagicLinkToken[] = [];
    const now = Date.now() / 1000;

    for (const tokenId of tokenIds) {
      const token = this.tokens.get(tokenId);
      if (token && token.expiresAt > now && !token.usedAt) {
        tokens.push(token);
      }
    }

    return tokens;
  }

  update(token: MagicLinkToken): void {
    this.tokens.set(token.id, token);
  }

  delete(tokenId: string): boolean {
    const token = this.tokens.get(tokenId);
    if (!token) return false;

    this.tokens.delete(tokenId);
    
    // Update email index
    const emailTokens = this.emailIndex.get(token.emailHash);
    if (emailTokens) {
      emailTokens.delete(tokenId);
      if (emailTokens.size === 0) {
        this.emailIndex.delete(token.emailHash);
      }
    }

    return true;
  }

  cleanup(): void {
    const now = Date.now() / 1000;
    const expiredTokens: string[] = [];

    for (const [tokenId, token] of this.tokens.entries()) {
      // Remove tokens that are expired by more than 1 hour
      if (token.expiresAt < now - 3600) {
        expiredTokens.push(tokenId);
      }
    }

    expiredTokens.forEach(tokenId => this.delete(tokenId));
  }

  getStats(): {
    totalTokens: number;
    activeTokens: number;
    usedTokens: number;
    expiredTokens: number;
  } {
    const now = Date.now() / 1000;
    let active = 0, used = 0, expired = 0;

    for (const token of this.tokens.values()) {
      if (token.usedAt) {
        used++;
      } else if (token.expiresAt < now) {
        expired++;
      } else {
        active++;
      }
    }

    return {
      totalTokens: this.tokens.size,
      activeTokens: active,
      usedTokens: used,
      expiredTokens: expired
    };
  }

  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.tokens.clear();
    this.emailIndex.clear();
  }
}

/**
 * Core magic link manager
 */
export class MagicLinkManager {
  private config: MagicLinkConfig;
  private store: MagicLinkStore;
  private securityManager: SecurityManager;

  constructor(config: Partial<MagicLinkConfig>, securityConfig?: SecurityConfig) {
    this.config = {
      tokenTTL: 600, // 10 minutes
      maxAttempts: 3,
      cleanupInterval: 5 * 60 * 1000,
      baseUrl: 'https://auth.lukhas.ai',
      fromEmail: 'auth@lukhas.ai',
      rateLimiting: {
        emailWindow: 3600, // 1 hour
        emailLimit: 3,
        ipWindow: 3600, // 1 hour
        ipLimit: 5
      },
      security: {
        requireSameIP: false,
        requireSameDevice: false,
        allowedDomains: [],
        blockedDomains: ['tempmail.org', '10minutemail.com', 'guerrillamail.com']
      },
      ...config
    };

    this.store = new MagicLinkStore(this.config.cleanupInterval);
    this.securityManager = new SecurityManager(securityConfig || {
      emailRateLimit: {
        windowMs: this.config.rateLimiting.emailWindow * 1000,
        maxAttempts: this.config.rateLimiting.emailLimit,
        blockDurationMs: this.config.rateLimiting.emailWindow * 1000
      },
      ipRateLimit: {
        windowMs: this.config.rateLimiting.ipWindow * 1000,
        maxAttempts: this.config.rateLimiting.ipLimit,
        blockDurationMs: this.config.rateLimiting.ipWindow * 1000
      },
      failedAuthLimit: {
        windowMs: 15 * 60 * 1000,
        maxAttempts: 5,
        blockDurationMs: 30 * 60 * 1000
      },
      preventEnumeration: true,
      auditLogging: true,
      alertThreshold: 3
    });
  }

  /**
   * Generate and send magic link
   */
  async generateMagicLink(request: MagicLinkRequest): Promise<MagicLinkResult> {
    try {
      // Validate email format
      if (!this.isValidEmail(request.email)) {
        return {
          success: false,
          reason: 'Invalid email format'
        };
      }

      // Check domain restrictions
      const domainCheck = this.checkEmailDomain(request.email);
      if (!domainCheck.allowed) {
        return {
          success: false,
          reason: domainCheck.reason
        };
      }

      // Check rate limits
      const rateLimitCheck = await this.securityManager.checkEmailRateLimit(
        request.email,
        request.ipAddress
      );

      if (!rateLimitCheck.allowed) {
        await this.securityManager.logAuditEvent({
          event: 'magic_link_request',
          ip: request.ipAddress,
          email: request.email,
          success: false,
          reason: rateLimitCheck.reason,
          metadata: { tier: request.tier, purpose: request.purpose }
        });

        return {
          success: false,
          reason: 'Rate limit exceeded',
          retryAfter: rateLimitCheck.resetTime ? Math.ceil((rateLimitCheck.resetTime - Date.now()) / 1000) : undefined
        };
      }

      // Check for existing active tokens
      const emailHash = this.hashEmail(request.email);
      const existingTokens = this.store.getActiveTokensForEmail(emailHash);
      
      // Limit active tokens per email
      if (existingTokens.length >= 2) {
        return {
          success: false,
          reason: 'Too many active tokens for this email'
        };
      }

      // Generate token
      const tokenData = this.generateToken();
      const now = Math.floor(Date.now() / 1000);

      const magicLinkToken: MagicLinkToken = {
        id: this.generateTokenId(),
        token: tokenData.token,
        tokenHash: tokenData.hash,
        email: request.email,
        emailHash,
        userId: request.customData?.userId,
        purpose: request.purpose,
        createdAt: now,
        expiresAt: now + this.config.tokenTTL,
        ipAddress: request.ipAddress,
        ipHash: this.hashIP(request.ipAddress),
        userAgent: request.userAgent,
        attempts: 0,
        maxAttempts: this.config.maxAttempts,
        tier: request.tier,
        metadata: {
          redirectUrl: request.redirectUrl,
          deviceFingerprint: request.deviceFingerprint,
          customData: request.customData
        }
      };

      // Store token
      this.store.store(magicLinkToken);

      // Generate magic link URL
      const magicLink = this.buildMagicLinkUrl(magicLinkToken);

      // Send email (this would integrate with your email service)
      const emailSent = await this.sendMagicLinkEmail(magicLinkToken, magicLink);

      if (!emailSent) {
        // Clean up token if email failed
        this.store.delete(magicLinkToken.id);
        return {
          success: false,
          reason: 'Failed to send email'
        };
      }

      // Log success
      await this.securityManager.logAuditEvent({
        event: 'magic_link_request',
        ip: request.ipAddress,
        email: request.email,
        success: true,
        metadata: {
          tokenId: magicLinkToken.id,
          tier: request.tier,
          purpose: request.purpose,
          expiresAt: magicLinkToken.expiresAt
        }
      });

      return {
        success: true,
        tokenId: magicLinkToken.id,
        expiresAt: magicLinkToken.expiresAt,
        expiresIn: this.config.tokenTTL,
        metadata: {
          purpose: request.purpose,
          tier: request.tier
        }
      };

    } catch (error) {
      await this.securityManager.logAuditEvent({
        event: 'magic_link_request',
        ip: request.ipAddress,
        email: request.email,
        success: false,
        reason: error instanceof Error ? error.message : 'Unknown error'
      });

      return {
        success: false,
        reason: 'Internal error generating magic link'
      };
    }
  }

  /**
   * Validate and consume magic link token
   */
  async validateMagicLink(
    token: string,
    ipAddress: string,
    userAgent: string,
    deviceFingerprint?: string
  ): Promise<MagicLinkValidation> {
    try {
      // Hash token for lookup
      const tokenHash = this.hashToken(token);
      const magicLinkToken = this.store.getByToken(tokenHash);

      if (!magicLinkToken) {
        await this.securityManager.logAuditEvent({
          event: 'auth_failure',
          ip: ipAddress,
          success: false,
          reason: 'Invalid magic link token'
        });

        return {
          valid: false,
          error: 'Invalid or expired token'
        };
      }

      // Increment attempt counter
      magicLinkToken.attempts++;
      this.store.update(magicLinkToken);

      const now = Math.floor(Date.now() / 1000);

      // Check if token is expired
      if (magicLinkToken.expiresAt < now) {
        await this.securityManager.logAuditEvent({
          event: 'auth_failure',
          ip: ipAddress,
          email: magicLinkToken.email,
          success: false,
          reason: 'Expired magic link token',
          metadata: { tokenId: magicLinkToken.id }
        });

        return {
          valid: false,
          error: 'Token expired',
          expired: true
        };
      }

      // Check if token is already used
      if (magicLinkToken.usedAt) {
        await this.securityManager.logAuditEvent({
          event: 'auth_failure',
          ip: ipAddress,
          email: magicLinkToken.email,
          success: false,
          reason: 'Magic link token already used',
          metadata: { tokenId: magicLinkToken.id }
        });

        return {
          valid: false,
          error: 'Token already used'
        };
      }

      // Check attempt limits
      if (magicLinkToken.attempts > magicLinkToken.maxAttempts) {
        await this.securityManager.logAuditEvent({
          event: 'auth_failure',
          ip: ipAddress,
          email: magicLinkToken.email,
          success: false,
          reason: 'Magic link attempts exhausted',
          metadata: { tokenId: magicLinkToken.id, attempts: magicLinkToken.attempts }
        });

        return {
          valid: false,
          error: 'Too many attempts',
          exhausted: true
        };
      }

      // Security checks
      if (this.config.security.requireSameIP && magicLinkToken.ipHash !== this.hashIP(ipAddress)) {
        await this.securityManager.logAuditEvent({
          event: 'auth_failure',
          ip: ipAddress,
          email: magicLinkToken.email,
          success: false,
          reason: 'IP address mismatch',
          metadata: { tokenId: magicLinkToken.id }
        });

        return {
          valid: false,
          error: 'Security validation failed'
        };
      }

      if (this.config.security.requireSameDevice && 
          deviceFingerprint && 
          magicLinkToken.metadata.deviceFingerprint !== deviceFingerprint) {
        await this.securityManager.logAuditEvent({
          event: 'auth_failure',
          ip: ipAddress,
          email: magicLinkToken.email,
          success: false,
          reason: 'Device fingerprint mismatch',
          metadata: { tokenId: magicLinkToken.id }
        });

        return {
          valid: false,
          error: 'Security validation failed'
        };
      }

      // Mark token as used
      magicLinkToken.usedAt = now;
      this.store.update(magicLinkToken);

      // Log successful validation
      await this.securityManager.logAuditEvent({
        event: 'auth_success',
        ip: ipAddress,
        email: magicLinkToken.email,
        success: true,
        metadata: {
          tokenId: magicLinkToken.id,
          purpose: magicLinkToken.purpose,
          tier: magicLinkToken.tier,
          attempts: magicLinkToken.attempts
        }
      });

      return {
        valid: true,
        token: magicLinkToken,
        email: magicLinkToken.email,
        userId: magicLinkToken.userId,
        purpose: magicLinkToken.purpose,
        tier: magicLinkToken.tier,
        metadata: magicLinkToken.metadata
      };

    } catch (error) {
      await this.securityManager.logAuditEvent({
        event: 'auth_failure',
        ip: ipAddress,
        success: false,
        reason: error instanceof Error ? error.message : 'Unknown error'
      });

      return {
        valid: false,
        error: 'Validation error'
      };
    }
  }

  /**
   * Revoke magic link token
   */
  async revokeMagicLink(tokenId: string, reason: string): Promise<boolean> {
    const token = this.store.get(tokenId);
    if (!token) return false;

    // Mark as used to prevent further use
    token.usedAt = Math.floor(Date.now() / 1000);
    this.store.update(token);

    await this.securityManager.logAuditEvent({
      event: 'auth_failure',
      ip: token.ipAddress,
      email: token.email,
      success: false,
      reason: `Token revoked: ${reason}`,
      metadata: { tokenId }
    });

    return true;
  }

  /**
   * Get magic link statistics
   */
  getMagicLinkStats(): {
    store: ReturnType<MagicLinkStore['getStats']>;
    security: ReturnType<SecurityManager['getSecurityMetrics']>;
  } {
    return {
      store: this.store.getStats(),
      security: this.securityManager.getSecurityMetrics()
    };
  }

  /**
   * Validate email format
   */
  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email) && email.length <= 320;
  }

  /**
   * Check email domain restrictions
   */
  private checkEmailDomain(email: string): { allowed: boolean; reason?: string } {
    const domain = email.split('@')[1]?.toLowerCase();
    if (!domain) {
      return { allowed: false, reason: 'Invalid email domain' };
    }

    // Check blocked domains
    if (this.config.security.blockedDomains.includes(domain)) {
      return { allowed: false, reason: 'Email domain not allowed' };
    }

    // Check allowed domains (if configured)
    if (this.config.security.allowedDomains.length > 0 && 
        !this.config.security.allowedDomains.includes(domain)) {
      return { allowed: false, reason: 'Email domain not in allowed list' };
    }

    return { allowed: true };
  }

  /**
   * Generate secure token
   */
  private generateToken(): { token: string; hash: string } {
    const token = randomBytes(32).toString('base64url');
    const hash = this.hashToken(token);
    return { token, hash };
  }

  /**
   * Generate unique token ID
   */
  private generateTokenId(): string {
    const timestamp = Date.now().toString(36);
    const random = randomBytes(8).toString('hex');
    return `ml_${timestamp}_${random}`;
  }

  /**
   * Hash token for storage
   */
  private hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  /**
   * Hash email for privacy
   */
  private hashEmail(email: string): string {
    return createHash('sha256').update(email.toLowerCase()).digest('hex').slice(0, 16);
  }

  /**
   * Hash IP address for privacy
   */
  private hashIP(ip: string): string {
    return createHash('sha256').update(ip).digest('hex').slice(0, 16);
  }

  /**
   * Build magic link URL
   */
  private buildMagicLinkUrl(token: MagicLinkToken): string {
    const baseUrl = this.config.baseUrl.replace(/\/$/, '');
    const params = new URLSearchParams({
      token: token.token,
      purpose: token.purpose
    });

    if (token.metadata.redirectUrl) {
      params.set('redirect', token.metadata.redirectUrl);
    }

    return `${baseUrl}/auth/magic-link?${params.toString()}`;
  }

  /**
   * Send magic link email
   */
  private async sendMagicLinkEmail(token: MagicLinkToken, magicLink: string): Promise<boolean> {
    try {
      // TODO: Integrate with your email service (SendGrid, AWS SES, etc.)
      
      const emailData = {
        to: token.email,
        from: this.config.fromEmail,
        subject: this.getEmailSubject(token.purpose),
        html: this.generateEmailTemplate(token, magicLink),
        text: this.generateEmailText(token, magicLink)
      };

      // Mock email sending for now
      console.log('📧 Magic link email:', emailData);
      
      // In production, replace with actual email service
      // await emailService.send(emailData);
      
      return true;
    } catch (error) {
      console.error('Failed to send magic link email:', error);
      return false;
    }
  }

  /**
   * Get email subject based on purpose
   */
  private getEmailSubject(purpose: string): string {
    const subjects = {
      login: 'Sign in to LUKHAS AI',
      signup: 'Complete your LUKHAS AI registration',
      verify: 'Verify your LUKHAS AI account',
      reset: 'Reset your LUKHAS AI password',
      invite: 'You\'ve been invited to LUKHAS AI'
    };
    return subjects[purpose as keyof typeof subjects] || 'LUKHAS AI Authentication';
  }

  /**
   * Generate email HTML template
   */
  private generateEmailTemplate(token: MagicLinkToken, magicLink: string): string {
    const expiresIn = Math.ceil(this.config.tokenTTL / 60);
    
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>LUKHAS AI Authentication</title>
      </head>
      <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #333;">LUKHAS AI</h1>
        <p>Hello,</p>
        <p>Click the link below to ${token.purpose === 'login' ? 'sign in' : token.purpose} to your LUKHAS AI account:</p>
        <p>
          <a href="${magicLink}" style="background: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
            ${this.getEmailSubject(token.purpose)}
          </a>
        </p>
        <p>This link will expire in ${expiresIn} minutes.</p>
        <p>If you didn't request this, you can safely ignore this email.</p>
        <hr>
        <p style="font-size: 12px; color: #666;">
          LUKHAS AI • Trinity Framework (⚛️🧠🛡️)<br>
          This is an automated message, please do not reply.
        </p>
      </body>
      </html>
    `;
  }

  /**
   * Generate email plain text
   */
  private generateEmailText(token: MagicLinkToken, magicLink: string): string {
    const expiresIn = Math.ceil(this.config.tokenTTL / 60);
    
    return `
LUKHAS AI Authentication

Hello,

Click the link below to ${token.purpose === 'login' ? 'sign in' : token.purpose} to your LUKHAS AI account:

${magicLink}

This link will expire in ${expiresIn} minutes.

If you didn't request this, you can safely ignore this email.

--
LUKHAS AI • Trinity Framework (⚛️🧠🛡️)
This is an automated message, please do not reply.
    `.trim();
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    this.store.destroy();
    this.securityManager.destroy();
  }
}

/**
 * Magic link utilities
 */
export class MagicLinkUtils {
  /**
   * Parse magic link URL
   */
  static parseMagicLinkUrl(url: string): { token?: string; purpose?: string; redirect?: string } {
    try {
      const urlObj = new URL(url);
      const params = new URLSearchParams(urlObj.search);
      
      return {
        token: params.get('token') || undefined,
        purpose: params.get('purpose') || undefined,
        redirect: params.get('redirect') || undefined
      };
    } catch {
      return {};
    }
  }

  /**
   * Validate redirect URL
   */
  static isValidRedirectUrl(url: string, allowedDomains: string[]): boolean {
    try {
      const urlObj = new URL(url);
      
      // Must be HTTPS in production
      if (urlObj.protocol !== 'https:' && process.env.NODE_ENV === 'production') {
        return false;
      }

      // Check allowed domains
      if (allowedDomains.length > 0) {
        return allowedDomains.some(domain => 
          urlObj.hostname === domain || 
          urlObj.hostname.endsWith(`.${domain}`)
        );
      }

      return true;
    } catch {
      return false;
    }
  }

  /**
   * Generate device fingerprint (basic)
   */
  static generateDeviceFingerprint(userAgent: string, additionalData?: Record<string, any>): string {
    const data = {
      userAgent,
      ...additionalData
    };
    
    return createHash('sha256')
      .update(JSON.stringify(data))
      .digest('hex')
      .slice(0, 16);
  }
}

/**
 * Default magic link configuration
 */
export const DEFAULT_MAGIC_LINK_CONFIG: MagicLinkConfig = {
  tokenTTL: 600, // 10 minutes
  maxAttempts: 3,
  cleanupInterval: 5 * 60 * 1000,
  baseUrl: 'https://auth.lukhas.ai',
  fromEmail: 'auth@lukhas.ai',
  rateLimiting: {
    emailWindow: 3600, // 1 hour
    emailLimit: 3,
    ipWindow: 3600, // 1 hour
    ipLimit: 5
  },
  security: {
    requireSameIP: false,
    requireSameDevice: false,
    allowedDomains: [],
    blockedDomains: [
      'tempmail.org',
      '10minutemail.com',
      'guerrillamail.com',
      'mailinator.com',
      'yopmail.com'
    ]
  }
};

export default MagicLinkManager;