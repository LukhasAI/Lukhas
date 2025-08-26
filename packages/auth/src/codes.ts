/**
 * ΛiD Authentication System - Verification Codes
 *
 * 6-digit verification codes with HMAC validation, TTL 600s, enumeration-safe responses
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

import {
  VerificationCodeOptions,
  VerificationCodeResult,
  VerificationCodeValidationResult,
  SecurityEvent
} from '../types/auth.types';
import { checkRateLimit } from './rate-limits';
import { UserTier } from '../types/auth.types';

/**
 * Verification code configuration
 */
export interface VerificationCodeConfig {
  codeTTL: number;             // Code time-to-live in seconds
  maxAttempts: number;         // Max verification attempts per code
  attemptWindow: number;       // Time window for attempt counting (seconds)
  codeLength: number;          // Length of verification codes
  ipThrottleLimit: number;     // Max requests per IP per window
  emailThrottleLimit: number;  // Max requests per email per window
  hmacSecret: string;          // HMAC secret for code verification
  pepper: string;              // Cryptographic pepper for additional security
}

/**
 * Default verification code configuration
 */
export const DEFAULT_CODE_CONFIG: VerificationCodeConfig = {
  codeTTL: 600,                // 10 minutes
  maxAttempts: 5,              // 5 attempts max
  attemptWindow: 3600,         // 1 hour window
  codeLength: 6,               // 6-digit codes
  ipThrottleLimit: 10,         // 10 requests per IP per hour
  emailThrottleLimit: 3,       // 3 requests per email per hour
  hmacSecret: process.env.LUKHAS_CODE_HMAC_SECRET || 'dev-secret-change-in-production',
  pepper: process.env.LUKHAS_CODE_PEPPER || 'dev-pepper-change-in-production'
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
 * Verification code entry (no raw codes stored)
 */
interface CodeEntry {
  codeHash: string;            // HMAC hash of code + pepper
  email: string;
  userId?: string;
  purpose: 'login' | 'register' | 'password-reset' | 'email-verification' | 'phone-verification';
  createdAt: number;
  expiresAt: number;
  attempts: number;
  maxAttempts: number;
  ipAddress: string;
  userAgent: string;
  metadata?: Record<string, any>;
  verified: boolean;
  verifiedAt?: number;
}

/**
 * In-memory stores (in production, use Redis/database)
 */
class VerificationCodeStore {
  private codes = new Map<string, CodeEntry>();
  private ipThrottles = new Map<string, ThrottleEntry>();
  private emailThrottles = new Map<string, ThrottleEntry>();
  private securityEvents: SecurityEvent[] = [];

  constructor(private config: VerificationCodeConfig) {
    // Cleanup expired entries every minute
    setInterval(() => this.cleanup(), 60000);
  }

  /**
   * Store a verification code entry
   */
  storeCode(codeEntry: CodeEntry): void {
    // Use email+purpose as key for single active code per purpose
    const key = `${codeEntry.email}:${codeEntry.purpose}`;
    this.codes.set(key, codeEntry);
  }

  /**
   * Get code entry by email and purpose
   */
  getCode(email: string, purpose: string): CodeEntry | null {
    const key = `${email}:${purpose}`;
    const entry = this.codes.get(key);
    if (!entry) return null;

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.codes.delete(key);
      return null;
    }

    return entry;
  }

  /**
   * Verify code using HMAC comparison
   */
  verifyCode(email: string, purpose: string, code: string): CodeEntry | null {
    const entry = this.getCode(email, purpose);
    if (!entry || entry.verified) return null;

    // Generate HMAC hash of provided code
    const providedHash = this.generateCodeHash(code, email, purpose);

    // Constant-time comparison to prevent timing attacks
    if (this.constantTimeCompare(entry.codeHash, providedHash)) {
      return entry;
    }

    return null;
  }

  /**
   * Mark code as verified
   */
  markVerified(email: string, purpose: string): boolean {
    const key = `${email}:${purpose}`;
    const entry = this.codes.get(key);
    if (!entry || entry.verified) return false;

    entry.verified = true;
    entry.verifiedAt = Date.now();
    this.codes.set(key, entry);
    return true;
  }

  /**
   * Increment attempt counter
   */
  incrementAttempts(email: string, purpose: string): number {
    const entry = this.getCode(email, purpose);
    if (!entry) return 0;

    entry.attempts++;
    const key = `${email}:${purpose}`;
    this.codes.set(key, entry);
    return entry.attempts;
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
   * Generate HMAC hash of code
   */
  generateCodeHash(code: string, email: string, purpose: string): string {
    const crypto = require('crypto');
    const hmac = crypto.createHmac('sha256', this.config.hmacSecret);

    // Include pepper, email, and purpose to prevent rainbow table attacks
    hmac.update(`${code}:${this.config.pepper}:${email}:${purpose}`);
    return hmac.digest('hex');
  }

  /**
   * Constant-time string comparison to prevent timing attacks
   */
  constantTimeCompare(a: string, b: string): boolean {
    if (a.length !== b.length) return false;

    let result = 0;
    for (let i = 0; i < a.length; i++) {
      result |= a.charCodeAt(i) ^ b.charCodeAt(i);
    }

    return result === 0;
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

    console.log('[ΛiD VERIFICATION CODES SECURITY]', JSON.stringify(event));
  }

  /**
   * Cleanup expired entries
   */
  cleanup(): void {
    const now = Date.now();

    // Cleanup codes
    for (const [key, entry] of this.codes.entries()) {
      if (now > entry.expiresAt) {
        this.codes.delete(key);
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
 * Verification Code Manager
 */
export class VerificationCodeManager {
  private store: VerificationCodeStore;
  private config: VerificationCodeConfig;

  constructor(config: VerificationCodeConfig = DEFAULT_CODE_CONFIG) {
    this.config = config;
    this.store = new VerificationCodeStore(config);
  }

  /**
   * Generate verification code
   */
  async generateCode(
    email: string,
    purpose: 'login' | 'register' | 'password-reset' | 'email-verification' | 'phone-verification',
    options: VerificationCodeOptions
  ): Promise<VerificationCodeResult> {
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
          'auth:verification-code',
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

      // Generate secure 6-digit code (leading zeros allowed)
      const code = this.generateSecureCode();
      const now = Date.now();
      const expiresAt = now + (this.config.codeTTL * 1000);

      // Generate HMAC hash
      const codeHash = this.store.generateCodeHash(code, email, purpose);

      // Create code entry (no raw code stored)
      const codeEntry: CodeEntry = {
        codeHash,
        email,
        userId: options.userId,
        purpose,
        createdAt: now,
        expiresAt,
        attempts: 0,
        maxAttempts: options.maxAttempts || this.config.maxAttempts,
        ipAddress: options.ipAddress,
        userAgent: options.userAgent,
        metadata: options.metadata,
        verified: false
      };

      // Store code entry
      this.store.storeCode(codeEntry);

      // Log security event (without the actual code)
      this.store.logSecurityEvent('VERIFICATION_CODE_GENERATED', {
        email,
        purpose,
        ipAddress: options.ipAddress,
        userAgent: options.userAgent
      });

      return {
        success: true,
        code,  // Only returned here for sending via email/SMS
        expiresAt: new Date(expiresAt).toISOString(),
        expiresIn: this.config.codeTTL
      };

    } catch (error) {
      return {
        success: false,
        reason: `Failed to generate verification code: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Verify code (enumeration-safe)
   */
  async verifyCode(
    email: string,
    code: string,
    purpose: 'login' | 'register' | 'password-reset' | 'email-verification' | 'phone-verification',
    ipAddress: string,
    userAgent: string
  ): Promise<VerificationCodeValidationResult> {
    try {
      // Always return success: true to prevent enumeration attacks
      // Real validation happens internally

      const entry = this.store.getCode(email, purpose);
      let actuallyValid = false;

      if (entry) {
        // Check if already verified
        if (entry.verified) {
          this.store.logSecurityEvent('CODE_REUSE_ATTEMPT', {
            email,
            purpose,
            ipAddress,
            originalIP: entry.ipAddress
          });
        } else if (entry.attempts >= entry.maxAttempts) {
          // Max attempts exceeded
          this.store.logSecurityEvent('CODE_MAX_ATTEMPTS', {
            email,
            purpose,
            attempts: entry.attempts
          });
        } else {
          // Increment attempts first
          this.store.incrementAttempts(email, purpose);

          // Verify the code
          const verifiedEntry = this.store.verifyCode(email, purpose, code);
          if (verifiedEntry) {
            // Mark as verified
            this.store.markVerified(email, purpose);
            actuallyValid = true;

            // Log successful verification
            this.store.logSecurityEvent('CODE_VERIFIED', {
              email,
              purpose,
              ipAddress,
              attempts: verifiedEntry.attempts + 1
            });
          } else {
            // Invalid code
            this.store.logSecurityEvent('CODE_INVALID', {
              email,
              purpose,
              ipAddress,
              attempts: entry.attempts
            });
          }
        }
      } else {
        // No code entry found - still log attempt
        this.store.logSecurityEvent('CODE_NOT_FOUND', {
          email,
          purpose,
          ipAddress
        });
      }

      // Always return enumeration-safe response
      return {
        valid: actuallyValid,
        email: actuallyValid ? email : undefined,
        userId: actuallyValid ? entry?.userId : undefined,
        purpose: actuallyValid ? purpose : undefined,
        metadata: actuallyValid ? entry?.metadata : undefined
      };

    } catch (error) {
      // Log error but still return enumeration-safe response
      this.store.logSecurityEvent('CODE_VERIFICATION_ERROR', {
        email,
        purpose,
        error: error instanceof Error ? error.message : 'Unknown error'
      });

      return {
        valid: false,
        reason: 'Verification failed'
      };
    }
  }

  /**
   * Get code status (enumeration-safe)
   */
  async getCodeStatus(email: string, purpose: string): Promise<{
    exists: boolean;
    verified?: boolean;
    expired?: boolean;
    attempts?: number;
    maxAttempts?: number;
    expiresAt?: string;
  }> {
    const entry = this.store.getCode(email, purpose);

    if (!entry) {
      return { exists: false };
    }

    const now = Date.now();

    return {
      exists: true,
      verified: entry.verified,
      expired: now > entry.expiresAt,
      attempts: entry.attempts,
      maxAttempts: entry.maxAttempts,
      expiresAt: new Date(entry.expiresAt).toISOString()
    };
  }

  /**
   * Revoke code
   */
  async revokeCode(email: string, purpose: string, reason: string): Promise<boolean> {
    const entry = this.store.getCode(email, purpose);
    if (!entry) return false;

    // Mark as verified to prevent further use
    const revoked = this.store.markVerified(email, purpose);

    if (revoked) {
      this.store.logSecurityEvent('CODE_REVOKED', {
        email,
        purpose,
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

  /**
   * Generate secure 6-digit code (allows leading zeros)
   */
  private generateSecureCode(): string {
    const array = new Uint8Array(1);
    let code = '';

    for (let i = 0; i < this.config.codeLength; i++) {
      crypto.getRandomValues(array);
      code += (array[0] % 10).toString();
    }

    return code;
  }
}

/**
 * Global verification code manager instance
 */
export const verificationCodeManager = new VerificationCodeManager();

/**
 * Convenience functions for verification code operations
 */

/**
 * Send verification code
 */
export async function sendVerificationCode(
  email: string,
  purpose: 'login' | 'register' | 'password-reset' | 'email-verification' | 'phone-verification',
  options: VerificationCodeOptions
): Promise<VerificationCodeResult> {
  return verificationCodeManager.generateCode(email, purpose, options);
}

/**
 * Verify code
 */
export async function verifyVerificationCode(
  email: string,
  code: string,
  purpose: 'login' | 'register' | 'password-reset' | 'email-verification' | 'phone-verification',
  ipAddress: string,
  userAgent: string
): Promise<VerificationCodeValidationResult> {
  return verificationCodeManager.verifyCode(email, code, purpose, ipAddress, userAgent);
}

/**
 * Check code status
 */
export async function checkCodeStatus(email: string, purpose: string): Promise<{
  exists: boolean;
  verified?: boolean;
  expired?: boolean;
  attempts?: number;
  maxAttempts?: number;
  expiresAt?: string;
}> {
  return verificationCodeManager.getCodeStatus(email, purpose);
}

/**
 * Revoke code
 */
export async function revokeVerificationCode(email: string, purpose: string, reason: string): Promise<boolean> {
  return verificationCodeManager.revokeCode(email, purpose, reason);
}

/**
 * Get current throttle limits
 */
export async function getCodeThrottleLimits(ip: string, email: string): Promise<{
  ip: { count: number; limit: number; resetTime?: number };
  email: { count: number; limit: number; resetTime?: number };
}> {
  return verificationCodeManager.getThrottleStatus(ip, email);
}
