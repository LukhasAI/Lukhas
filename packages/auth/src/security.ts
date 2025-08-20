/**
 * ΛiD Authentication System - Security Features
 * 
 * Advanced security features: refresh token family tracking, device binding,
 * session rotation, account lockout with exponential backoff
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

import {
  User,
  Session,
  DeviceHandle,
  RefreshTokenData,
  SecurityEvent,
  SecurityEventSeverity,
  UserTier,
  AuthScope
} from '../types/auth.types';

// =============================================================================
// REFRESH TOKEN FAMILY TRACKING
// =============================================================================

/**
 * Refresh token family manager for reuse detection
 */
export class RefreshTokenFamilyManager {
  private familyStore = new Map<string, RefreshTokenData[]>();

  /**
   * Create new token family
   */
  createFamily(
    userId: string,
    deviceHandle: string,
    tier: UserTier,
    scopes: AuthScope[],
    ipAddress?: string,
    userAgent?: string
  ): string {
    const familyId = `family_${Date.now()}_${Math.random().toString(36).substring(2)}`;
    
    const initialToken: RefreshTokenData = {
      id: `rt_${Date.now()}_${Math.random().toString(36).substring(2)}`,
      userId,
      familyId,
      tokenHash: '', // Will be set when token is generated
      deviceHandle,
      jti: `jti_${Date.now()}_${Math.random().toString(36).substring(2)}`,
      scopes,
      tier,
      ipAddress,
      userAgent,
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days
      metadata: {}
    };

    this.familyStore.set(familyId, [initialToken]);
    
    this.logSecurityEvent('REFRESH_TOKEN_FAMILY_CREATED', {
      familyId,
      userId,
      deviceHandle
    });

    return familyId;
  }

  /**
   * Add token to family (during refresh)
   */
  addToFamily(familyId: string, tokenData: RefreshTokenData): boolean {
    const family = this.familyStore.get(familyId);
    if (!family) {
      this.logSecurityEvent('REFRESH_TOKEN_FAMILY_NOT_FOUND', {
        familyId,
        tokenId: tokenData.id
      });
      return false;
    }

    // Check if family is compromised
    if (this.isFamilyCompromised(familyId)) {
      this.logSecurityEvent('REFRESH_TOKEN_FAMILY_COMPROMISED_ATTEMPT', {
        familyId,
        tokenId: tokenData.id,
        userId: tokenData.userId
      });
      return false;
    }

    family.push(tokenData);
    this.familyStore.set(familyId, family);

    return true;
  }

  /**
   * Validate token in family
   */
  validateTokenInFamily(familyId: string, jti: string): {
    valid: boolean;
    reason?: string;
    tokenData?: RefreshTokenData;
  } {
    const family = this.familyStore.get(familyId);
    if (!family) {
      return { valid: false, reason: 'Family not found' };
    }

    // Find token in family
    const token = family.find(t => t.jti === jti);
    if (!token) {
      return { valid: false, reason: 'Token not in family' };
    }

    // Check if token is revoked
    if (token.revokedAt) {
      return { valid: false, reason: 'Token revoked' };
    }

    // Check if token is expired
    if (new Date() > new Date(token.expiresAt)) {
      return { valid: false, reason: 'Token expired' };
    }

    // Check if token was already used
    if (token.usedAt) {
      // Token reuse detected - compromise the entire family
      this.compromiseFamily(familyId, 'Token reuse detected');
      return { valid: false, reason: 'Token reuse detected - family compromised' };
    }

    return { valid: true, tokenData: token };
  }

  /**
   * Mark token as used
   */
  markTokenUsed(familyId: string, jti: string): boolean {
    const family = this.familyStore.get(familyId);
    if (!family) return false;

    const tokenIndex = family.findIndex(t => t.jti === jti);
    if (tokenIndex === -1) return false;

    family[tokenIndex].usedAt = new Date().toISOString();
    this.familyStore.set(familyId, family);

    return true;
  }

  /**
   * Compromise entire token family
   */
  compromiseFamily(familyId: string, reason: string): void {
    const family = this.familyStore.get(familyId);
    if (!family) return;

    const now = new Date().toISOString();
    
    // Revoke all tokens in family
    family.forEach(token => {
      if (!token.revokedAt) {
        token.revokedAt = now;
        token.revokedReason = reason;
      }
    });

    this.familyStore.set(familyId, family);

    this.logSecurityEvent('REFRESH_TOKEN_FAMILY_COMPROMISED', {
      familyId,
      reason,
      tokensRevoked: family.length,
      severity: 'high' as SecurityEventSeverity
    });
  }

  /**
   * Check if family is compromised
   */
  isFamilyCompromised(familyId: string): boolean {
    const family = this.familyStore.get(familyId);
    if (!family) return true;

    return family.some(token => token.revokedAt && token.revokedReason === 'Token reuse detected');
  }

  /**
   * Cleanup expired families
   */
  cleanupExpiredFamilies(): number {
    let cleanedCount = 0;
    const now = new Date();

    for (const [familyId, family] of this.familyStore.entries()) {
      // Remove if all tokens are expired or revoked
      const hasActiveTokens = family.some(token => 
        !token.revokedAt && new Date(token.expiresAt) > now
      );

      if (!hasActiveTokens) {
        this.familyStore.delete(familyId);
        cleanedCount++;
      }
    }

    return cleanedCount;
  }

  private logSecurityEvent(type: string, metadata: any): void {
    console.log('[ΛiD REFRESH TOKEN FAMILY]', JSON.stringify({
      type,
      timestamp: new Date().toISOString(),
      metadata
    }));
  }
}

// =============================================================================
// DEVICE BINDING AND FINGERPRINTING
// =============================================================================

/**
 * Device fingerprinting and binding manager
 */
export class DeviceBindingManager {
  private deviceStore = new Map<string, DeviceHandle>();
  private fingerprintStore = new Map<string, string[]>(); // fingerprint -> device handles

  /**
   * Generate device fingerprint from request
   */
  generateFingerprint(
    userAgent: string,
    ipAddress?: string,
    additionalData?: Record<string, any>
  ): string {
    const components = [
      userAgent,
      this.extractPlatformInfo(userAgent),
      this.extractBrowserInfo(userAgent),
      additionalData?.screenResolution,
      additionalData?.timezone,
      additionalData?.language,
      additionalData?.hardwareConcurrency,
      additionalData?.deviceMemory
    ].filter(Boolean);

    // Create hash of components (in production, use proper crypto)
    const fingerprint = this.simpleHash(components.join('|'));
    return `fp_${fingerprint}`;
  }

  /**
   * Create or update device handle
   */
  createOrUpdateDevice(
    userId: string,
    fingerprint: string,
    userAgent: string,
    ipAddress?: string,
    deviceName?: string
  ): DeviceHandle {
    const handle = `device_${Date.now()}_${Math.random().toString(36).substring(2)}`;
    
    // Check if device exists by fingerprint
    const existingHandles = this.fingerprintStore.get(fingerprint) || [];
    const existingDevice = existingHandles
      .map(h => this.deviceStore.get(h))
      .find(d => d?.userId === userId);

    if (existingDevice) {
      // Update existing device
      existingDevice.lastSeenAt = new Date().toISOString();
      existingDevice.lastIpAddress = ipAddress;
      existingDevice.useCount++;
      
      this.deviceStore.set(existingDevice.handle, existingDevice);
      
      this.logSecurityEvent('DEVICE_UPDATED', {
        deviceHandle: existingDevice.handle,
        userId,
        useCount: existingDevice.useCount
      });

      return existingDevice;
    }

    // Create new device
    const device: DeviceHandle = {
      id: `dev_${Date.now()}_${Math.random().toString(36).substring(2)}`,
      userId,
      handle,
      deviceType: this.detectDeviceType(userAgent),
      fingerprintHash: fingerprint,
      deviceName: deviceName || this.generateDeviceName(userAgent),
      platform: this.extractPlatformInfo(userAgent),
      browser: this.extractBrowserInfo(userAgent),
      browserVersion: this.extractBrowserVersion(userAgent),
      trusted: false,
      firstSeenAt: new Date().toISOString(),
      lastSeenAt: new Date().toISOString(),
      lastIpAddress: ipAddress,
      useCount: 1,
      blocked: false,
      metadata: {}
    };

    this.deviceStore.set(handle, device);
    
    // Update fingerprint mapping
    existingHandles.push(handle);
    this.fingerprintStore.set(fingerprint, existingHandles);

    this.logSecurityEvent('DEVICE_REGISTERED', {
      deviceHandle: handle,
      userId,
      deviceType: device.deviceType,
      platform: device.platform
    });

    return device;
  }

  /**
   * Trust a device
   */
  trustDevice(handle: string, trustedBy: string): boolean {
    const device = this.deviceStore.get(handle);
    if (!device) return false;

    device.trusted = true;
    device.trustedAt = new Date().toISOString();
    device.trustedBy = trustedBy;

    this.deviceStore.set(handle, device);

    this.logSecurityEvent('DEVICE_TRUSTED', {
      deviceHandle: handle,
      userId: device.userId,
      trustedBy
    });

    return true;
  }

  /**
   * Block a device
   */
  blockDevice(handle: string, reason: string): boolean {
    const device = this.deviceStore.get(handle);
    if (!device) return false;

    device.blocked = true;
    device.blockedAt = new Date().toISOString();
    device.blockedReason = reason;

    this.deviceStore.set(handle, device);

    this.logSecurityEvent('DEVICE_BLOCKED', {
      deviceHandle: handle,
      userId: device.userId,
      reason,
      severity: 'high' as SecurityEventSeverity
    });

    return true;
  }

  /**
   * Validate device access
   */
  validateDevice(handle: string): {
    valid: boolean;
    reason?: string;
    device?: DeviceHandle;
    requiresTrust?: boolean;
  } {
    const device = this.deviceStore.get(handle);
    if (!device) {
      return { valid: false, reason: 'Device not found' };
    }

    if (device.blocked) {
      return { 
        valid: false, 
        reason: `Device blocked: ${device.blockedReason}` 
      };
    }

    // Check for suspicious activity patterns
    const suspiciousActivity = this.detectSuspiciousActivity(device);
    if (suspiciousActivity.suspicious) {
      return {
        valid: false,
        reason: `Suspicious activity detected: ${suspiciousActivity.reason}`
      };
    }

    return { 
      valid: true, 
      device,
      requiresTrust: !device.trusted 
    };
  }

  /**
   * Detect suspicious device activity
   */
  private detectSuspiciousActivity(device: DeviceHandle): {
    suspicious: boolean;
    reason?: string;
  } {
    // Check for rapid location changes
    if (device.metadata?.rapidLocationChanges) {
      return { suspicious: true, reason: 'Rapid location changes detected' };
    }

    // Check for unusual usage patterns
    const hoursSinceFirstSeen = (Date.now() - new Date(device.firstSeenAt).getTime()) / (1000 * 60 * 60);
    if (device.useCount > 100 && hoursSinceFirstSeen < 1) {
      return { suspicious: true, reason: 'Unusually high usage in short time' };
    }

    return { suspicious: false };
  }

  // Helper methods for device detection
  private detectDeviceType(userAgent: string): string {
    const ua = userAgent.toLowerCase();
    if (ua.includes('mobile') || ua.includes('android') || ua.includes('iphone')) {
      return 'mobile';
    }
    if (ua.includes('tablet') || ua.includes('ipad')) {
      return 'tablet';
    }
    return 'desktop';
  }

  private extractPlatformInfo(userAgent: string): string {
    const ua = userAgent.toLowerCase();
    if (ua.includes('windows')) return 'Windows';
    if (ua.includes('macintosh') || ua.includes('mac os')) return 'macOS';
    if (ua.includes('linux')) return 'Linux';
    if (ua.includes('android')) return 'Android';
    if (ua.includes('iphone') || ua.includes('ipad')) return 'iOS';
    return 'Unknown';
  }

  private extractBrowserInfo(userAgent: string): string {
    const ua = userAgent.toLowerCase();
    if (ua.includes('chrome') && !ua.includes('edge')) return 'Chrome';
    if (ua.includes('firefox')) return 'Firefox';
    if (ua.includes('safari') && !ua.includes('chrome')) return 'Safari';
    if (ua.includes('edge')) return 'Edge';
    return 'Unknown';
  }

  private extractBrowserVersion(userAgent: string): string {
    // Simplified version extraction
    const matches = userAgent.match(/(?:chrome|firefox|safari|edge)\/([0-9.]+)/i);
    return matches ? matches[1] : 'Unknown';
  }

  private generateDeviceName(userAgent: string): string {
    const platform = this.extractPlatformInfo(userAgent);
    const browser = this.extractBrowserInfo(userAgent);
    const deviceType = this.detectDeviceType(userAgent);
    
    return `${platform} ${browser} (${deviceType})`;
  }

  private simpleHash(input: string): string {
    // Simple hash function (use proper crypto in production)
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
  }

  private logSecurityEvent(type: string, metadata: any): void {
    console.log('[ΛiD DEVICE BINDING]', JSON.stringify({
      type,
      timestamp: new Date().toISOString(),
      metadata
    }));
  }
}

// =============================================================================
// SESSION ROTATION AND MANAGEMENT
// =============================================================================

/**
 * Session rotation manager for security
 */
export class SessionRotationManager {
  private sessionStore = new Map<string, Session>();

  /**
   * Create new session
   */
  createSession(
    userId: string,
    deviceHandle: string,
    tier: UserTier,
    scopes: AuthScope[],
    ipAddress?: string,
    userAgent?: string
  ): Session {
    const sessionId = `sess_${Date.now()}_${Math.random().toString(36).substring(2)}`;
    const accessTokenJti = `access_${Date.now()}_${Math.random().toString(36).substring(2)}`;
    const refreshTokenJti = `refresh_${Date.now()}_${Math.random().toString(36).substring(2)}`;

    const session: Session = {
      id: sessionId,
      userId,
      deviceHandle,
      accessTokenJti,
      refreshTokenJti,
      ipAddress,
      userAgent,
      fingerprintHash: this.generateSessionFingerprint(userAgent, ipAddress),
      scopes,
      tier,
      role: 'viewer', // Will be updated based on user data
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24 hours
      lastUsedAt: new Date().toISOString(),
      metadata: {}
    };

    this.sessionStore.set(sessionId, session);

    this.logSecurityEvent('SESSION_CREATED', {
      sessionId,
      userId,
      deviceHandle,
      tier
    });

    return session;
  }

  /**
   * Rotate session on privilege changes
   */
  rotateSession(
    sessionId: string,
    reason: 'tier_change' | 'role_change' | 'scope_change' | 'security_event'
  ): Session | null {
    const session = this.sessionStore.get(sessionId);
    if (!session) return null;

    // Create new session with updated tokens
    const newAccessTokenJti = `access_${Date.now()}_${Math.random().toString(36).substring(2)}`;
    const newRefreshTokenJti = `refresh_${Date.now()}_${Math.random().toString(36).substring(2)}`;

    const rotatedSession: Session = {
      ...session,
      id: `sess_${Date.now()}_${Math.random().toString(36).substring(2)}`,
      accessTokenJti: newAccessTokenJti,
      refreshTokenJti: newRefreshTokenJti,
      createdAt: new Date().toISOString(),
      lastUsedAt: new Date().toISOString(),
      metadata: {
        ...session.metadata,
        rotatedFrom: sessionId,
        rotationReason: reason
      }
    };

    // Store new session
    this.sessionStore.set(rotatedSession.id, rotatedSession);

    // Invalidate old session
    this.invalidateSession(sessionId, `Rotated due to ${reason}`);

    this.logSecurityEvent('SESSION_ROTATED', {
      oldSessionId: sessionId,
      newSessionId: rotatedSession.id,
      reason,
      userId: session.userId
    });

    return rotatedSession;
  }

  /**
   * Update session activity
   */
  updateSessionActivity(sessionId: string, ipAddress?: string): boolean {
    const session = this.sessionStore.get(sessionId);
    if (!session) return false;

    session.lastUsedAt = new Date().toISOString();
    
    if (ipAddress && ipAddress !== session.ipAddress) {
      // IP address change - log security event
      this.logSecurityEvent('SESSION_IP_CHANGE', {
        sessionId,
        userId: session.userId,
        oldIP: session.ipAddress,
        newIP: ipAddress,
        severity: 'medium' as SecurityEventSeverity
      });
      
      session.ipAddress = ipAddress;
    }

    this.sessionStore.set(sessionId, session);
    return true;
  }

  /**
   * Validate session
   */
  validateSession(sessionId: string): {
    valid: boolean;
    reason?: string;
    session?: Session;
    requiresRotation?: boolean;
  } {
    const session = this.sessionStore.get(sessionId);
    if (!session) {
      return { valid: false, reason: 'Session not found' };
    }

    // Check expiration
    if (new Date() > new Date(session.expiresAt)) {
      this.invalidateSession(sessionId, 'Session expired');
      return { valid: false, reason: 'Session expired' };
    }

    // Check for suspicious activity
    const suspiciousActivity = this.detectSuspiciousSessionActivity(session);
    if (suspiciousActivity.suspicious) {
      return {
        valid: false,
        reason: `Suspicious activity: ${suspiciousActivity.reason}`
      };
    }

    // Check if session needs rotation
    const needsRotation = this.sessionNeedsRotation(session);

    return { 
      valid: true, 
      session,
      requiresRotation: needsRotation
    };
  }

  /**
   * Invalidate session
   */
  invalidateSession(sessionId: string, reason: string): boolean {
    const session = this.sessionStore.get(sessionId);
    if (!session) return false;

    this.sessionStore.delete(sessionId);

    this.logSecurityEvent('SESSION_INVALIDATED', {
      sessionId,
      userId: session.userId,
      reason
    });

    return true;
  }

  /**
   * Cleanup expired sessions
   */
  cleanupExpiredSessions(): number {
    let cleanedCount = 0;
    const now = new Date();

    for (const [sessionId, session] of this.sessionStore.entries()) {
      if (now > new Date(session.expiresAt)) {
        this.sessionStore.delete(sessionId);
        cleanedCount++;
      }
    }

    return cleanedCount;
  }

  /**
   * Cleanup all user sessions (for security)
   */
  invalidateAllUserSessions(userId: string, keepSessionId?: string): number {
    let invalidatedCount = 0;

    for (const [sessionId, session] of this.sessionStore.entries()) {
      if (session.userId === userId && sessionId !== keepSessionId) {
        this.sessionStore.delete(sessionId);
        invalidatedCount++;
      }
    }

    this.logSecurityEvent('ALL_USER_SESSIONS_INVALIDATED', {
      userId,
      keptSession: keepSessionId,
      invalidatedCount
    });

    return invalidatedCount;
  }

  private sessionNeedsRotation(session: Session): boolean {
    // Rotate sessions that are over 12 hours old
    const twelveHoursAgo = Date.now() - (12 * 60 * 60 * 1000);
    return new Date(session.createdAt).getTime() < twelveHoursAgo;
  }

  private detectSuspiciousSessionActivity(session: Session): {
    suspicious: boolean;
    reason?: string;
  } {
    // Check for concurrent sessions from different locations
    const otherSessions = Array.from(this.sessionStore.values())
      .filter(s => s.userId === session.userId && s.id !== session.id);

    for (const otherSession of otherSessions) {
      if (otherSession.ipAddress && session.ipAddress && 
          otherSession.ipAddress !== session.ipAddress) {
        const timeDiff = Math.abs(
          new Date(session.lastUsedAt).getTime() - 
          new Date(otherSession.lastUsedAt).getTime()
        );
        
        // Concurrent usage from different IPs within 5 minutes
        if (timeDiff < 5 * 60 * 1000) {
          return { 
            suspicious: true, 
            reason: 'Concurrent sessions from different locations' 
          };
        }
      }
    }

    return { suspicious: false };
  }

  private generateSessionFingerprint(userAgent?: string, ipAddress?: string): string {
    const components = [userAgent, ipAddress].filter(Boolean);
    return this.simpleHash(components.join('|'));
  }

  private simpleHash(input: string): string {
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
  }

  private logSecurityEvent(type: string, metadata: any): void {
    console.log('[ΛiD SESSION ROTATION]', JSON.stringify({
      type,
      timestamp: new Date().toISOString(),
      metadata
    }));
  }
}

// =============================================================================
// ACCOUNT LOCKOUT WITH EXPONENTIAL BACKOFF
// =============================================================================

/**
 * Account lockout manager with exponential backoff
 */
export class AccountLockoutManager {
  private lockoutStore = new Map<string, {
    attempts: number;
    lockoutUntil?: number;
    backoffLevel: number;
    lastAttempt: number;
  }>();

  private readonly maxAttempts = 5;
  private readonly baseLockoutDuration = 5 * 60 * 1000; // 5 minutes
  private readonly maxLockoutDuration = 24 * 60 * 60 * 1000; // 24 hours
  private readonly attemptWindow = 60 * 60 * 1000; // 1 hour

  /**
   * Record failed login attempt
   */
  recordFailedAttempt(
    userId: string,
    ipAddress?: string,
    userAgent?: string
  ): {
    locked: boolean;
    lockoutUntil?: Date;
    attemptsRemaining: number;
    nextBackoffLevel?: number;
  } {
    const key = userId;
    const now = Date.now();
    
    let record = this.lockoutStore.get(key);
    
    if (!record) {
      record = {
        attempts: 0,
        backoffLevel: 0,
        lastAttempt: now
      };
    }

    // Reset attempts if outside the window
    if (now - record.lastAttempt > this.attemptWindow) {
      record.attempts = 0;
      record.backoffLevel = 0;
    }

    record.attempts++;
    record.lastAttempt = now;

    this.logSecurityEvent('FAILED_LOGIN_ATTEMPT', {
      userId,
      ipAddress,
      userAgent,
      attempts: record.attempts,
      severity: 'medium' as SecurityEventSeverity
    });

    if (record.attempts >= this.maxAttempts) {
      // Calculate exponential backoff
      const lockoutDuration = Math.min(
        this.baseLockoutDuration * Math.pow(2, record.backoffLevel),
        this.maxLockoutDuration
      );
      
      record.lockoutUntil = now + lockoutDuration;
      record.backoffLevel++;

      this.logSecurityEvent('ACCOUNT_LOCKED', {
        userId,
        ipAddress,
        lockoutDuration,
        backoffLevel: record.backoffLevel,
        severity: 'high' as SecurityEventSeverity
      });

      this.lockoutStore.set(key, record);

      return {
        locked: true,
        lockoutUntil: new Date(record.lockoutUntil),
        attemptsRemaining: 0,
        nextBackoffLevel: record.backoffLevel
      };
    }

    this.lockoutStore.set(key, record);

    return {
      locked: false,
      attemptsRemaining: this.maxAttempts - record.attempts
    };
  }

  /**
   * Check if account is locked
   */
  isAccountLocked(userId: string): {
    locked: boolean;
    lockoutUntil?: Date;
    attemptsRemaining?: number;
  } {
    const record = this.lockoutStore.get(userId);
    if (!record) {
      return { locked: false, attemptsRemaining: this.maxAttempts };
    }

    const now = Date.now();

    // Check if lockout has expired
    if (record.lockoutUntil && now >= record.lockoutUntil) {
      // Reset attempts after lockout expires
      record.attempts = 0;
      record.lockoutUntil = undefined;
      this.lockoutStore.set(userId, record);

      this.logSecurityEvent('ACCOUNT_LOCKOUT_EXPIRED', {
        userId
      });

      return { locked: false, attemptsRemaining: this.maxAttempts };
    }

    // Check current lockout status
    if (record.lockoutUntil && now < record.lockoutUntil) {
      return {
        locked: true,
        lockoutUntil: new Date(record.lockoutUntil)
      };
    }

    return {
      locked: false,
      attemptsRemaining: this.maxAttempts - record.attempts
    };
  }

  /**
   * Clear failed attempts (on successful login)
   */
  clearFailedAttempts(userId: string): void {
    const record = this.lockoutStore.get(userId);
    if (record) {
      record.attempts = 0;
      record.lockoutUntil = undefined;
      this.lockoutStore.set(userId, record);

      this.logSecurityEvent('FAILED_ATTEMPTS_CLEARED', {
        userId
      });
    }
  }

  /**
   * Manual unlock (admin function)
   */
  unlockAccount(userId: string, adminUserId: string): boolean {
    const record = this.lockoutStore.get(userId);
    if (!record || !record.lockoutUntil) {
      return false;
    }

    record.attempts = 0;
    record.lockoutUntil = undefined;
    record.backoffLevel = 0;
    this.lockoutStore.set(userId, record);

    this.logSecurityEvent('ACCOUNT_MANUALLY_UNLOCKED', {
      userId,
      adminUserId,
      severity: 'medium' as SecurityEventSeverity
    });

    return true;
  }

  /**
   * Get lockout statistics
   */
  getLockoutStats(userId: string): {
    attempts: number;
    locked: boolean;
    lockoutUntil?: Date;
    backoffLevel: number;
    lastAttempt?: Date;
  } {
    const record = this.lockoutStore.get(userId);
    if (!record) {
      return {
        attempts: 0,
        locked: false,
        backoffLevel: 0
      };
    }

    const locked = record.lockoutUntil ? Date.now() < record.lockoutUntil : false;

    return {
      attempts: record.attempts,
      locked,
      lockoutUntil: record.lockoutUntil ? new Date(record.lockoutUntil) : undefined,
      backoffLevel: record.backoffLevel,
      lastAttempt: new Date(record.lastAttempt)
    };
  }

  /**
   * Cleanup expired lockout records
   */
  cleanupExpiredLockouts(): number {
    let cleanedCount = 0;
    const now = Date.now();
    const cleanupThreshold = now - (7 * 24 * 60 * 60 * 1000); // 7 days

    for (const [userId, record] of this.lockoutStore.entries()) {
      // Remove old records that are no longer relevant
      if (record.lastAttempt < cleanupThreshold && 
          (!record.lockoutUntil || now > record.lockoutUntil)) {
        this.lockoutStore.delete(userId);
        cleanedCount++;
      }
    }

    return cleanedCount;
  }

  private logSecurityEvent(type: string, metadata: any): void {
    console.log('[ΛiD ACCOUNT LOCKOUT]', JSON.stringify({
      type,
      timestamp: new Date().toISOString(),
      metadata
    }));
  }
}

// =============================================================================
// GLOBAL SECURITY MANAGER
// =============================================================================

/**
 * Unified security manager combining all security features
 */
export class SecurityManager {
  public readonly refreshTokenFamilyManager = new RefreshTokenFamilyManager();
  public readonly deviceBindingManager = new DeviceBindingManager();
  public readonly sessionRotationManager = new SessionRotationManager();
  public readonly accountLockoutManager = new AccountLockoutManager();

  /**
   * Initialize security manager with cleanup tasks
   */
  constructor() {
    // Setup periodic cleanup tasks
    setInterval(() => {
      this.performCleanupTasks();
    }, 60 * 60 * 1000); // Every hour
  }

  /**
   * Perform all cleanup tasks
   */
  private performCleanupTasks(): void {
    const familiesCleared = this.refreshTokenFamilyManager.cleanupExpiredFamilies();
    const sessionsCleared = this.sessionRotationManager.cleanupExpiredSessions();
    const lockoutsCleared = this.accountLockoutManager.cleanupExpiredLockouts();

    console.log('[ΛiD SECURITY CLEANUP]', {
      timestamp: new Date().toISOString(),
      familiesCleared,
      sessionsCleared,
      lockoutsCleared
    });
  }

  /**
   * Comprehensive security check for authentication request
   */
  performSecurityCheck(
    userId: string,
    ipAddress?: string,
    userAgent?: string,
    deviceHandle?: string
  ): {
    allowed: boolean;
    reason?: string;
    lockoutInfo?: any;
    deviceInfo?: any;
    requiresAdditionalAuth?: boolean;
  } {
    // Check account lockout
    const lockoutStatus = this.accountLockoutManager.isAccountLocked(userId);
    if (lockoutStatus.locked) {
      return {
        allowed: false,
        reason: 'Account locked',
        lockoutInfo: lockoutStatus
      };
    }

    // Check device if provided
    if (deviceHandle) {
      const deviceStatus = this.deviceBindingManager.validateDevice(deviceHandle);
      if (!deviceStatus.valid) {
        return {
          allowed: false,
          reason: deviceStatus.reason,
          deviceInfo: deviceStatus
        };
      }

      // Require additional auth for untrusted devices
      if (deviceStatus.requiresTrust) {
        return {
          allowed: true,
          requiresAdditionalAuth: true,
          deviceInfo: deviceStatus
        };
      }
    }

    return { allowed: true };
  }
}

// Global security manager instance
export const securityManager = new SecurityManager();

// Export individual managers for specific use cases
export {
  RefreshTokenFamilyManager,
  DeviceBindingManager,
  SessionRotationManager,
  AccountLockoutManager
};