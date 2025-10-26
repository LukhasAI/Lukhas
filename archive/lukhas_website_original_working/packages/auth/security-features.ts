/**
 * Advanced Security Features for ΛiD Authentication System
 * 
 * Implements refresh token family tracking, device binding, session rotation,
 * account lockout, and comprehensive security monitoring.
 */

import { TierLevel } from './scopes';
import { createHash, randomBytes, timingSafeEqual } from 'crypto';
import type { DatabaseInterface, RefreshToken, DeviceHandle, Session, SecurityEvent, User } from './database';

export interface RefreshTokenFamily {
  familyId: string;
  userId: string;
  deviceId: string;
  deviceFingerprint?: string;
  createdAt: Date;
  lastUsed: Date;
  tokenCount: number;
  revoked: boolean;
  revokedAt?: Date;
  revokedReason?: string;
  maxTokenAge: number; // Maximum age for tokens in this family
  rotationPolicy: 'always' | 'on_use' | 'scheduled';
}

export interface DeviceBinding {
  deviceId: string;
  userId: string;
  fingerprint: string;
  trusted: boolean;
  trustScore: number;
  bindingStrength: 'weak' | 'medium' | 'strong';
  lastVerified: Date;
  verificationHistory: DeviceVerification[];
}

export interface DeviceVerification {
  timestamp: Date;
  method: 'fingerprint' | 'passkey' | 'location' | 'behavior';
  success: boolean;
  confidence: number; // 0.0 to 1.0
  metadata: Record<string, any>;
}

export interface SessionRotationEvent {
  sessionId: string;
  userId: string;
  trigger: 'tier_change' | 'role_change' | 'privilege_escalation' | 'security_event' | 'policy_update';
  oldTokenHash: string;
  newTokenHash: string;
  timestamp: Date;
  rotatedFields: string[];
}

export interface AccountLockoutState {
  userId: string;
  lockedAt: Date;
  lockReason: string;
  lockLevel: 'soft' | 'hard' | 'permanent';
  unlockAt?: Date;
  unlockToken?: string;
  attemptCount: number;
  maxAttempts: number;
  backoffMultiplier: number;
  lockHistory: LockoutEvent[];
}

export interface LockoutEvent {
  timestamp: Date;
  reason: string;
  lockLevel: 'soft' | 'hard' | 'permanent';
  duration: number; // seconds
  unlockMethod?: string;
  ipAddress?: string;
  userAgent?: string;
}

export interface SecurityConfig {
  refreshTokenFamily: {
    maxFamilySize: number;
    maxFamilyAge: number; // seconds
    rotationPolicy: 'always' | 'on_use' | 'scheduled';
    reuseDetectionWindow: number; // seconds
  };
  deviceBinding: {
    enabled: boolean;
    trustThreshold: number; // 0.0 to 1.0
    fingerprintComponents: string[];
    verificationInterval: number; // seconds
    maxUntrustedDevices: number;
  };
  sessionRotation: {
    rotateOnTierChange: boolean;
    rotateOnRoleChange: boolean;
    rotateOnPrivilegeEscalation: boolean;
    rotateOnSuspiciousActivity: boolean;
    maxSessionAge: number; // seconds
  };
  accountLockout: {
    enabled: boolean;
    maxFailedAttempts: number;
    lockoutDuration: number; // seconds
    backoffMultiplier: number;
    maxLockoutDuration: number; // seconds
    permanentLockThreshold: number;
  };
}

/**
 * Refresh Token Family Tracker
 * Implements secure token rotation with family tracking for reuse detection
 */
export class RefreshTokenFamilyTracker {
  private families: Map<string, RefreshTokenFamily> = new Map();
  private config: SecurityConfig['refreshTokenFamily'];
  private db: DatabaseInterface;

  constructor(config: SecurityConfig['refreshTokenFamily'], db: DatabaseInterface) {
    this.config = config;
    this.db = db;
  }

  /**
   * Create new refresh token family
   */
  async createFamily(
    userId: string,
    deviceId: string,
    deviceFingerprint?: string
  ): Promise<RefreshTokenFamily> {
    const familyId = this.generateFamilyId();
    const now = new Date();

    const family: RefreshTokenFamily = {
      familyId,
      userId,
      deviceId,
      deviceFingerprint,
      createdAt: now,
      lastUsed: now,
      tokenCount: 0,
      revoked: false,
      maxTokenAge: this.config.maxFamilyAge,
      rotationPolicy: this.config.rotationPolicy
    };

    this.families.set(familyId, family);

    // Log family creation
    await this.db.createSecurityEvent({
      user_id: userId,
      event_type: 'token_refresh',
      event_category: 'auth',
      severity: 'info',
      description: 'Refresh token family created',
      result: 'success',
      metadata: {
        familyId,
        deviceId,
        rotationPolicy: family.rotationPolicy
      }
    });

    return family;
  }

  /**
   * Add token to family
   */
  async addTokenToFamily(
    familyId: string,
    tokenHash: string,
    parentTokenId?: string
  ): Promise<{ success: boolean; reason?: string }> {
    const family = this.families.get(familyId);
    if (!family) {
      return { success: false, reason: 'Family not found' };
    }

    if (family.revoked) {
      return { success: false, reason: 'Family revoked' };
    }

    // Check family size limits
    if (family.tokenCount >= this.config.maxFamilySize) {
      await this.revokeFamily(familyId, 'Family size limit exceeded');
      return { success: false, reason: 'Family size limit exceeded' };
    }

    // Check family age
    const age = (Date.now() - family.createdAt.getTime()) / 1000;
    if (age > this.config.maxFamilyAge) {
      await this.revokeFamily(familyId, 'Family age limit exceeded');
      return { success: false, reason: 'Family age limit exceeded' };
    }

    // Create refresh token in database
    const tokenResult = await this.db.createRefreshToken({
      user_id: family.userId,
      family_id: familyId,
      token_hash: tokenHash,
      sequence_number: family.tokenCount + 1,
      parent_token_id: parentTokenId,
      expires_at: new Date(Date.now() + family.maxTokenAge * 1000),
      ip_address: '0.0.0.0', // This should be provided by caller
      scopes: [],
      metadata: { deviceId: family.deviceId }
    });

    if (!tokenResult.success) {
      return { success: false, reason: 'Failed to create token' };
    }

    // Update family
    family.tokenCount++;
    family.lastUsed = new Date();
    this.families.set(familyId, family);

    return { success: true };
  }

  /**
   * Validate token family and check for reuse
   */
  async validateTokenFamily(
    tokenHash: string,
    ipAddress: string
  ): Promise<{ valid: boolean; family?: RefreshTokenFamily; reason?: string }> {
    // Get token from database
    const tokenResult = await this.db.getRefreshTokenByHash(tokenHash);
    if (!tokenResult.success || !tokenResult.data) {
      return { valid: false, reason: 'Token not found' };
    }

    const token = tokenResult.data;
    const family = this.families.get(token.family_id);

    if (!family) {
      return { valid: false, reason: 'Family not found' };
    }

    if (family.revoked) {
      return { valid: false, reason: 'Family revoked' };
    }

    // Check if token was already used (potential reuse attack)
    if (token.used_at) {
      const reuseDelta = (Date.now() - token.used_at.getTime()) / 1000;
      if (reuseDelta < this.config.reuseDetectionWindow) {
        // Possible token reuse attack - revoke entire family
        await this.revokeFamily(token.family_id, 'Potential token reuse detected');
        
        await this.db.createSecurityEvent({
          user_id: family.userId,
          event_type: 'suspicious_activity',
          event_category: 'security',
          severity: 'critical',
          description: 'Refresh token reuse detected',
          result: 'blocked',
          ip_address: ipAddress,
          risk_score: 0.9,
          risk_factors: ['token_reuse', 'family_revoked'],
          metadata: {
            familyId: token.family_id,
            tokenSequence: token.sequence_number,
            reuseDelta
          }
        });

        return { valid: false, reason: 'Token reuse detected - family revoked' };
      }
    }

    return { valid: true, family };
  }

  /**
   * Revoke entire token family
   */
  async revokeFamily(familyId: string, reason: string): Promise<boolean> {
    const family = this.families.get(familyId);
    if (!family) return false;

    family.revoked = true;
    family.revokedAt = new Date();
    family.revokedReason = reason;
    this.families.set(familyId, family);

    // Revoke all tokens in database
    const revokeResult = await this.db.revokeRefreshTokenFamily(familyId, reason);

    // Log family revocation
    await this.db.createSecurityEvent({
      user_id: family.userId,
      event_type: 'token_revocation',
      event_category: 'security',
      severity: 'warning',
      description: `Refresh token family revoked: ${reason}`,
      result: 'success',
      metadata: {
        familyId,
        reason,
        tokenCount: family.tokenCount,
        deviceId: family.deviceId
      }
    });

    return revokeResult.success;
  }

  /**
   * Clean up expired families
   */
  async cleanupExpiredFamilies(): Promise<number> {
    const now = Date.now();
    let cleanedCount = 0;

    for (const [familyId, family] of this.families.entries()) {
      const age = (now - family.createdAt.getTime()) / 1000;
      if (age > this.config.maxFamilyAge) {
        await this.revokeFamily(familyId, 'Family expired');
        this.families.delete(familyId);
        cleanedCount++;
      }
    }

    return cleanedCount;
  }

  private generateFamilyId(): string {
    const timestamp = Date.now().toString(36);
    const random = randomBytes(8).toString('hex');
    return `rf_${timestamp}_${random}`;
  }
}

/**
 * Device Binding Manager
 * Implements device fingerprinting and trust management
 */
export class DeviceBindingManager {
  private bindings: Map<string, DeviceBinding> = new Map();
  private config: SecurityConfig['deviceBinding'];
  private db: DatabaseInterface;

  constructor(config: SecurityConfig['deviceBinding'], db: DatabaseInterface) {
    this.config = config;
    this.db = db;
  }

  /**
   * Create or update device binding
   */
  async bindDevice(
    userId: string,
    deviceId: string,
    fingerprint: string,
    verificationData: Partial<DeviceVerification>
  ): Promise<DeviceBinding> {
    const bindingKey = `${userId}:${deviceId}`;
    let binding = this.bindings.get(bindingKey);

    if (!binding) {
      // Create new binding
      binding = {
        deviceId,
        userId,
        fingerprint,
        trusted: false,
        trustScore: 0.1,
        bindingStrength: 'weak',
        lastVerified: new Date(),
        verificationHistory: []
      };
    }

    // Add verification event
    const verification: DeviceVerification = {
      timestamp: new Date(),
      method: verificationData.method || 'fingerprint',
      success: verificationData.success || true,
      confidence: verificationData.confidence || 0.5,
      metadata: verificationData.metadata || {}
    };

    binding.verificationHistory.push(verification);
    binding.lastVerified = verification.timestamp;

    // Update trust score based on verification history
    binding.trustScore = this.calculateTrustScore(binding.verificationHistory);
    binding.trusted = binding.trustScore >= this.config.trustThreshold;
    binding.bindingStrength = this.calculateBindingStrength(binding);

    this.bindings.set(bindingKey, binding);

    // Create or update device handle in database
    const deviceResult = await this.db.getDeviceHandleByDeviceId(deviceId);
    if (deviceResult.success && deviceResult.data) {
      await this.db.updateDeviceHandle(deviceResult.data.id, {
        trust_score: binding.trustScore,
        trusted: binding.trusted,
        last_used_at: binding.lastVerified,
        device_fingerprint: fingerprint
      });
    } else {
      await this.db.createDeviceHandle({
        user_id: userId,
        device_id: deviceId,
        device_fingerprint: fingerprint,
        device_type: 'unknown',
        trusted: binding.trusted,
        trust_score: binding.trustScore,
        metadata: { bindingStrength: binding.bindingStrength }
      });
    }

    // Log device binding event
    await this.db.createSecurityEvent({
      user_id: userId,
      event_type: 'suspicious_activity',
      event_category: 'security',
      severity: binding.trusted ? 'info' : 'warning',
      description: `Device ${binding.trusted ? 'trusted' : 'verified'}`,
      result: 'success',
      device_fingerprint: fingerprint,
      metadata: {
        deviceId,
        trustScore: binding.trustScore,
        bindingStrength: binding.bindingStrength,
        verificationMethod: verification.method
      }
    });

    return binding;
  }

  /**
   * Verify device against existing binding
   */
  async verifyDevice(
    userId: string,
    deviceId: string,
    currentFingerprint: string
  ): Promise<{ verified: boolean; binding?: DeviceBinding; reason?: string }> {
    const bindingKey = `${userId}:${deviceId}`;
    const binding = this.bindings.get(bindingKey);

    if (!binding) {
      return { verified: false, reason: 'Device not bound' };
    }

    // Check fingerprint match
    const fingerprintMatch = this.compareFingerprintsFuzzy(
      binding.fingerprint,
      currentFingerprint
    );

    if (fingerprintMatch.similarity < 0.8) {
      // Potential device spoofing or significant hardware change
      await this.db.createSecurityEvent({
        user_id: userId,
        event_type: 'suspicious_activity',
        event_category: 'security',
        severity: 'warning',
        description: 'Device fingerprint mismatch',
        result: 'blocked',
        device_fingerprint: currentFingerprint,
        risk_score: 1.0 - fingerprintMatch.similarity,
        risk_factors: ['fingerprint_mismatch', 'device_spoofing'],
        metadata: {
          deviceId,
          expectedFingerprint: binding.fingerprint,
          actualFingerprint: currentFingerprint,
          similarity: fingerprintMatch.similarity
        }
      });

      return { 
        verified: false, 
        binding, 
        reason: `Fingerprint mismatch (similarity: ${fingerprintMatch.similarity.toFixed(2)})` 
      };
    }

    // Check if verification is needed
    const timeSinceVerification = (Date.now() - binding.lastVerified.getTime()) / 1000;
    if (timeSinceVerification > this.config.verificationInterval) {
      // Re-verification needed
      return { 
        verified: false, 
        binding, 
        reason: 'Re-verification required' 
      };
    }

    return { verified: true, binding };
  }

  /**
   * Calculate trust score based on verification history
   */
  private calculateTrustScore(history: DeviceVerification[]): number {
    if (history.length === 0) return 0.1;

    const recentHistory = history.slice(-10); // Last 10 verifications
    const successRate = recentHistory.filter(v => v.success).length / recentHistory.length;
    const avgConfidence = recentHistory.reduce((sum, v) => sum + v.confidence, 0) / recentHistory.length;
    const ageBonus = Math.min(history.length / 20, 0.2); // Bonus for long history

    return Math.min(successRate * avgConfidence + ageBonus, 1.0);
  }

  /**
   * Calculate binding strength
   */
  private calculateBindingStrength(binding: DeviceBinding): 'weak' | 'medium' | 'strong' {
    if (binding.trustScore >= 0.8 && binding.verificationHistory.length >= 5) {
      return 'strong';
    } else if (binding.trustScore >= 0.6 && binding.verificationHistory.length >= 3) {
      return 'medium';
    }
    return 'weak';
  }

  /**
   * Compare fingerprints with fuzzy matching
   */
  private compareFingerprintsFuzzy(
    fingerprint1: string, 
    fingerprint2: string
  ): { similarity: number; differences: string[] } {
    if (fingerprint1 === fingerprint2) {
      return { similarity: 1.0, differences: [] };
    }

    // Simple implementation - in production, use more sophisticated comparison
    const components1 = fingerprint1.split('|');
    const components2 = fingerprint2.split('|');
    
    if (components1.length !== components2.length) {
      return { similarity: 0.0, differences: ['component_count'] };
    }

    let matches = 0;
    const differences: string[] = [];

    for (let i = 0; i < components1.length; i++) {
      if (components1[i] === components2[i]) {
        matches++;
      } else {
        differences.push(`component_${i}`);
      }
    }

    return {
      similarity: matches / components1.length,
      differences
    };
  }
}

/**
 * Session Rotation Manager
 * Implements automatic session rotation on security events
 */
export class SessionRotationManager {
  private config: SecurityConfig['sessionRotation'];
  private db: DatabaseInterface;

  constructor(config: SecurityConfig['sessionRotation'], db: DatabaseInterface) {
    this.config = config;
    this.db = db;
  }

  /**
   * Check if session should be rotated based on trigger
   */
  shouldRotateSession(
    trigger: SessionRotationEvent['trigger'],
    sessionAge: number
  ): boolean {
    switch (trigger) {
      case 'tier_change':
        return this.config.rotateOnTierChange;
      case 'role_change':
        return this.config.rotateOnRoleChange;
      case 'privilege_escalation':
        return this.config.rotateOnPrivilegeEscalation;
      case 'security_event':
        return this.config.rotateOnSuspiciousActivity;
      case 'policy_update':
        return true; // Always rotate on policy updates
      default:
        return sessionAge > this.config.maxSessionAge;
    }
  }

  /**
   * Rotate session token
   */
  async rotateSession(
    sessionId: string,
    trigger: SessionRotationEvent['trigger'],
    rotatedFields: string[] = []
  ): Promise<{ success: boolean; newSessionToken?: string; reason?: string }> {
    try {
      // Get current session
      const sessionResult = await this.db.getSessionByToken(''); // This needs session ID lookup
      if (!sessionResult.success || !sessionResult.data) {
        return { success: false, reason: 'Session not found' };
      }

      const session = sessionResult.data;

      // Generate new session token
      const newSessionToken = this.generateSessionToken();
      const newTokenHash = this.hashToken(newSessionToken);

      // Update session in database
      const updateResult = await this.db.updateSession(sessionId, {
        session_token: newSessionToken,
        session_token_hash: newTokenHash,
        last_activity_at: new Date()
      });

      if (!updateResult.success) {
        return { success: false, reason: 'Failed to update session' };
      }

      // Log rotation event
      const rotationEvent: SessionRotationEvent = {
        sessionId,
        userId: session.user_id,
        trigger,
        oldTokenHash: session.session_token_hash,
        newTokenHash,
        timestamp: new Date(),
        rotatedFields
      };

      await this.db.createSecurityEvent({
        user_id: session.user_id,
        session_id: sessionId,
        event_type: 'session_created',
        event_category: 'security',
        severity: 'info',
        description: `Session rotated due to ${trigger}`,
        result: 'success',
        metadata: {
          trigger,
          rotatedFields,
          oldTokenHash: session.session_token_hash.slice(0, 8) + '...',
          newTokenHash: newTokenHash.slice(0, 8) + '...'
        }
      });

      return { success: true, newSessionToken };

    } catch (error) {
      return { 
        success: false, 
        reason: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  private generateSessionToken(): string {
    return randomBytes(32).toString('base64url');
  }

  private hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }
}

/**
 * Account Lockout Manager
 * Implements progressive lockout with exponential backoff
 */
export class AccountLockoutManager {
  private lockouts: Map<string, AccountLockoutState> = new Map();
  private config: SecurityConfig['accountLockout'];
  private db: DatabaseInterface;

  constructor(config: SecurityConfig['accountLockout'], db: DatabaseInterface) {
    this.config = config;
    this.db = db;
  }

  /**
   * Record failed authentication attempt
   */
  async recordFailedAttempt(
    userId: string,
    reason: string,
    ipAddress: string,
    userAgent?: string
  ): Promise<{ locked: boolean; lockout?: AccountLockoutState }> {
    if (!this.config.enabled) {
      return { locked: false };
    }

    let lockout = this.lockouts.get(userId);
    
    if (!lockout) {
      lockout = {
        userId,
        lockedAt: new Date(),
        lockReason: reason,
        lockLevel: 'soft',
        attemptCount: 0,
        maxAttempts: this.config.maxFailedAttempts,
        backoffMultiplier: this.config.backoffMultiplier,
        lockHistory: []
      };
    }

    lockout.attemptCount++;

    // Check if account should be locked
    if (lockout.attemptCount >= this.config.maxFailedAttempts) {
      const lockDuration = this.calculateLockDuration(lockout);
      const lockLevel = this.determineLockLevel(lockout);

      lockout.lockedAt = new Date();
      lockout.lockLevel = lockLevel;
      lockout.unlockAt = new Date(Date.now() + lockDuration * 1000);
      
      if (lockLevel !== 'permanent') {
        lockout.unlockToken = this.generateUnlockToken();
      }

      const lockEvent: LockoutEvent = {
        timestamp: new Date(),
        reason,
        lockLevel,
        duration: lockDuration,
        ipAddress,
        userAgent
      };

      lockout.lockHistory.push(lockEvent);
      this.lockouts.set(userId, lockout);

      // Log lockout event
      await this.db.createSecurityEvent({
        user_id: userId,
        event_type: 'account_locked',
        event_category: 'security',
        severity: lockLevel === 'permanent' ? 'critical' : 'warning',
        description: `Account locked (${lockLevel}): ${reason}`,
        result: 'blocked',
        ip_address: ipAddress,
        user_agent: userAgent,
        risk_score: lockLevel === 'permanent' ? 1.0 : 0.7,
        risk_factors: ['repeated_failures', 'account_lockout'],
        metadata: {
          lockLevel,
          duration: lockDuration,
          attemptCount: lockout.attemptCount,
          unlockAt: lockout.unlockAt?.toISOString()
        }
      });

      return { locked: true, lockout };
    }

    this.lockouts.set(userId, lockout);
    return { locked: false, lockout };
  }

  /**
   * Check if account is currently locked
   */
  isAccountLocked(userId: string): { locked: boolean; lockout?: AccountLockoutState; timeRemaining?: number } {
    const lockout = this.lockouts.get(userId);
    
    if (!lockout || !lockout.unlockAt) {
      return { locked: false };
    }

    const now = Date.now();
    const unlockTime = lockout.unlockAt.getTime();

    if (lockout.lockLevel === 'permanent') {
      return { locked: true, lockout };
    }

    if (now < unlockTime) {
      return { 
        locked: true, 
        lockout, 
        timeRemaining: Math.ceil((unlockTime - now) / 1000) 
      };
    }

    // Lockout has expired
    this.unlockAccount(userId, 'automatic');
    return { locked: false };
  }

  /**
   * Unlock account
   */
  async unlockAccount(
    userId: string,
    method: 'automatic' | 'admin' | 'token' | 'time',
    unlockToken?: string
  ): Promise<{ success: boolean; reason?: string }> {
    const lockout = this.lockouts.get(userId);
    
    if (!lockout) {
      return { success: true, reason: 'Account not locked' };
    }

    // Verify unlock token if provided
    if (method === 'token') {
      if (!unlockToken || !lockout.unlockToken) {
        return { success: false, reason: 'Invalid unlock token' };
      }

      if (!timingSafeEqual(
        Buffer.from(unlockToken),
        Buffer.from(lockout.unlockToken)
      )) {
        return { success: false, reason: 'Invalid unlock token' };
      }
    }

    // Remove lockout
    this.lockouts.delete(userId);

    // Log unlock event
    await this.db.createSecurityEvent({
      user_id: userId,
      event_type: 'account_unlocked',
      event_category: 'security',
      severity: 'info',
      description: `Account unlocked via ${method}`,
      result: 'success',
      metadata: {
        unlockMethod: method,
        previousLockLevel: lockout.lockLevel,
        lockDuration: lockout.unlockAt ? 
          (Date.now() - lockout.lockedAt.getTime()) / 1000 : 0
      }
    });

    return { success: true };
  }

  /**
   * Calculate lock duration with exponential backoff
   */
  private calculateLockDuration(lockout: AccountLockoutState): number {
    const baseSeconds = this.config.lockoutDuration;
    const multiplier = Math.pow(this.config.backoffMultiplier, lockout.lockHistory.length);
    const duration = baseSeconds * multiplier;
    
    return Math.min(duration, this.config.maxLockoutDuration);
  }

  /**
   * Determine lock level based on history
   */
  private determineLockLevel(lockout: AccountLockoutState): 'soft' | 'hard' | 'permanent' {
    if (lockout.lockHistory.length >= this.config.permanentLockThreshold) {
      return 'permanent';
    } else if (lockout.lockHistory.length >= 3) {
      return 'hard';
    }
    return 'soft';
  }

  /**
   * Generate unlock token
   */
  private generateUnlockToken(): string {
    return randomBytes(16).toString('hex');
  }
}

/**
 * Default security configuration
 */
export const DEFAULT_SECURITY_CONFIG: SecurityConfig = {
  refreshTokenFamily: {
    maxFamilySize: 10,
    maxFamilyAge: 90 * 24 * 60 * 60, // 90 days
    rotationPolicy: 'on_use',
    reuseDetectionWindow: 300 // 5 minutes
  },
  deviceBinding: {
    enabled: true,
    trustThreshold: 0.7,
    fingerprintComponents: ['userAgent', 'screen', 'timezone', 'language'],
    verificationInterval: 30 * 24 * 60 * 60, // 30 days
    maxUntrustedDevices: 5
  },
  sessionRotation: {
    rotateOnTierChange: true,
    rotateOnRoleChange: true,
    rotateOnPrivilegeEscalation: true,
    rotateOnSuspiciousActivity: true,
    maxSessionAge: 24 * 60 * 60 // 24 hours
  },
  accountLockout: {
    enabled: true,
    maxFailedAttempts: 5,
    lockoutDuration: 15 * 60, // 15 minutes
    backoffMultiplier: 2.0,
    maxLockoutDuration: 24 * 60 * 60, // 24 hours
    permanentLockThreshold: 10
  }
};

export {
  RefreshTokenFamilyTracker,
  DeviceBindingManager,
  SessionRotationManager,
  AccountLockoutManager
};