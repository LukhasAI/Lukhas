/**
 * Advanced Session Management for ΛiD Authentication
 * 
 * Implements secure session handling with rotation, multi-device support,
 * device binding, and comprehensive security features for LUKHAS AI.
 */

import { TierLevel } from './tier-system';
import { Role } from './rbac';
import { generateJWT, verifyJWT } from './jwt';

export interface SessionData {
  sessionId: string;
  userId: string;
  tier: TierLevel;
  role?: Role;
  organizationId?: string;
  
  // Security context
  deviceId: string;
  deviceFingerprint: string;
  ipAddress: string;
  userAgent: string;
  country?: string;
  
  // Authentication state
  isVerified: boolean;
  isSSOAuthenticated: boolean;
  authMethods: string[];
  lastAuthAt: Date;
  lastStepUpAt?: Date;
  
  // Session metadata
  createdAt: Date;
  lastActiveAt: Date;
  expiresAt: Date;
  rotatedAt?: Date;
  rotationCount: number;
  
  // Security flags
  isSecure: boolean;
  requiresRotation: boolean;
  isSuspicious: boolean;
  riskScore: number;
  
  // Session type and constraints
  sessionType: 'web' | 'api' | 'mobile' | 'service';
  maxIdleTime: number; // milliseconds
  maxSessionTime: number; // milliseconds
  
  // Features and permissions
  scopes: string[];
  permissions: string[];
  featureFlags: Record<string, boolean>;
}

export interface DeviceInfo {
  deviceId: string;
  deviceName: string;
  deviceType: 'desktop' | 'mobile' | 'tablet' | 'unknown';
  fingerprint: string;
  firstSeen: Date;
  lastSeen: Date;
  trusted: boolean;
  location?: {
    country: string;
    region: string;
    city: string;
  };
  userAgent: string;
  sessionCount: number;
}

export interface SessionSecurityEvent {
  eventId: string;
  sessionId: string;
  userId: string;
  eventType: 'rotation' | 'suspicious_activity' | 'location_change' | 'device_change' | 'concurrent_limit';
  description: string;
  timestamp: Date;
  ipAddress: string;
  userAgent: string;
  riskScore: number;
  actionTaken: string;
  metadata?: Record<string, any>;
}

/**
 * Advanced session manager with security features
 */
export class SessionManager {
  private static readonly MAX_SESSIONS_PER_USER = 10;
  private static readonly SESSION_ROTATION_INTERVAL = 30 * 60 * 1000; // 30 minutes
  private static readonly MAX_IDLE_TIME = 60 * 60 * 1000; // 1 hour
  private static readonly SUSPICIOUS_THRESHOLD = 0.7;
  
  // In-memory storage (replace with Redis/database in production)
  private static sessions = new Map<string, SessionData>();
  private static userSessions = new Map<string, Set<string>>();
  private static deviceSessions = new Map<string, Set<string>>();
  private static securityEvents: SessionSecurityEvent[] = [];

  /**
   * Create new session with security context
   */
  static async createSession(params: {
    userId: string;
    tier: TierLevel;
    role?: Role;
    organizationId?: string;
    deviceId: string;
    deviceFingerprint: string;
    ipAddress: string;
    userAgent: string;
    country?: string;
    isVerified: boolean;
    isSSOAuthenticated: boolean;
    authMethods: string[];
    sessionType?: 'web' | 'api' | 'mobile' | 'service';
    scopes?: string[];
    permissions?: string[];
  }): Promise<{ session: SessionData; token: string }> {
    
    // Generate unique session ID
    const sessionId = this.generateSessionId();
    
    // Check concurrent session limits
    await this.enforceConcurrentSessionLimits(params.userId);
    
    // Calculate session durations based on tier and risk
    const sessionDurations = this.calculateSessionDurations(params.tier, params.sessionType || 'web');
    
    // Calculate risk score
    const riskScore = await this.calculateRiskScore({
      userId: params.userId,
      deviceId: params.deviceId,
      ipAddress: params.ipAddress,
      userAgent: params.userAgent,
      country: params.country
    });

    // Create session data
    const session: SessionData = {
      sessionId,
      userId: params.userId,
      tier: params.tier,
      role: params.role,
      organizationId: params.organizationId,
      
      deviceId: params.deviceId,
      deviceFingerprint: params.deviceFingerprint,
      ipAddress: params.ipAddress,
      userAgent: params.userAgent,
      country: params.country,
      
      isVerified: params.isVerified,
      isSSOAuthenticated: params.isSSOAuthenticated,
      authMethods: [...params.authMethods],
      lastAuthAt: new Date(),
      
      createdAt: new Date(),
      lastActiveAt: new Date(),
      expiresAt: new Date(Date.now() + sessionDurations.maxSessionTime),
      rotationCount: 0,
      
      isSecure: true,
      requiresRotation: false,
      isSuspicious: riskScore > this.SUSPICIOUS_THRESHOLD,
      riskScore,
      
      sessionType: params.sessionType || 'web',
      maxIdleTime: sessionDurations.maxIdleTime,
      maxSessionTime: sessionDurations.maxSessionTime,
      
      scopes: params.scopes || [],
      permissions: params.permissions || [],
      featureFlags: {}
    };

    // Store session
    this.sessions.set(sessionId, session);
    
    // Update user session tracking
    if (!this.userSessions.has(params.userId)) {
      this.userSessions.set(params.userId, new Set());
    }
    this.userSessions.get(params.userId)!.add(sessionId);
    
    // Update device session tracking
    if (!this.deviceSessions.has(params.deviceId)) {
      this.deviceSessions.set(params.deviceId, new Set());
    }
    this.deviceSessions.get(params.deviceId)!.add(sessionId);

    // Generate JWT token
    const token = await generateJWT({
      sub: params.userId,
      sessionId,
      tier: params.tier,
      role: params.role,
      org: params.organizationId,
      verified: params.isVerified,
      sso: params.isSSOAuthenticated,
      deviceId: params.deviceId,
      riskScore
    });

    // Log security event if suspicious
    if (session.isSuspicious) {
      await this.logSecurityEvent({
        eventType: 'suspicious_activity',
        sessionId,
        userId: params.userId,
        description: `High risk session created (score: ${riskScore})`,
        ipAddress: params.ipAddress,
        userAgent: params.userAgent,
        riskScore,
        actionTaken: 'session_created_with_monitoring'
      });
    }

    return { session, token };
  }

  /**
   * Validate and refresh session
   */
  static async validateSession(sessionId: string, options?: {
    updateActivity?: boolean;
    checkRotation?: boolean;
    enforceIdle?: boolean;
  }): Promise<{ valid: boolean; session?: SessionData; requiresRotation?: boolean; reason?: string }> {
    
    const session = this.sessions.get(sessionId);
    if (!session) {
      return { valid: false, reason: 'Session not found' };
    }

    const now = new Date();
    
    // Check expiration
    if (now > session.expiresAt) {
      await this.destroySession(sessionId);
      return { valid: false, reason: 'Session expired' };
    }

    // Check idle timeout
    if (options?.enforceIdle !== false) {
      const idleTime = now.getTime() - session.lastActiveAt.getTime();
      if (idleTime > session.maxIdleTime) {
        await this.destroySession(sessionId);
        return { valid: false, reason: 'Session idle timeout' };
      }
    }

    // Check if rotation is required
    let requiresRotation = false;
    if (options?.checkRotation !== false) {
      const timeSinceRotation = session.rotatedAt 
        ? now.getTime() - session.rotatedAt.getTime()
        : now.getTime() - session.createdAt.getTime();
        
      if (timeSinceRotation > this.SESSION_ROTATION_INTERVAL || session.requiresRotation) {
        requiresRotation = true;
      }
    }

    // Update last activity
    if (options?.updateActivity !== false) {
      session.lastActiveAt = now;
    }

    return { valid: true, session, requiresRotation };
  }

  /**
   * Rotate session for security (anti-session fixation)
   */
  static async rotateSession(currentSessionId: string, context?: {
    roleChanged?: boolean;
    tierChanged?: boolean;
    deviceChanged?: boolean;
    suspiciousActivity?: boolean;
  }): Promise<{ newSessionId: string; newToken: string } | null> {
    
    const session = this.sessions.get(currentSessionId);
    if (!session) {
      return null;
    }

    // Create new session ID
    const newSessionId = this.generateSessionId();
    
    // Update session data
    const rotatedSession: SessionData = {
      ...session,
      sessionId: newSessionId,
      rotatedAt: new Date(),
      rotationCount: session.rotationCount + 1,
      requiresRotation: false,
      lastActiveAt: new Date()
    };

    // Store new session
    this.sessions.set(newSessionId, rotatedSession);
    
    // Update tracking
    this.userSessions.get(session.userId)?.delete(currentSessionId);
    this.userSessions.get(session.userId)?.add(newSessionId);
    
    this.deviceSessions.get(session.deviceId)?.delete(currentSessionId);
    this.deviceSessions.get(session.deviceId)?.add(newSessionId);
    
    // Remove old session
    this.sessions.delete(currentSessionId);

    // Generate new JWT
    const newToken = await generateJWT({
      sub: session.userId,
      sessionId: newSessionId,
      tier: session.tier,
      role: session.role,
      org: session.organizationId,
      verified: session.isVerified,
      sso: session.isSSOAuthenticated,
      deviceId: session.deviceId,
      riskScore: session.riskScore
    });

    // Log rotation event
    await this.logSecurityEvent({
      eventType: 'rotation',
      sessionId: newSessionId,
      userId: session.userId,
      description: `Session rotated (count: ${rotatedSession.rotationCount})`,
      ipAddress: session.ipAddress,
      userAgent: session.userAgent,
      riskScore: session.riskScore,
      actionTaken: 'session_rotated',
      metadata: {
        oldSessionId: currentSessionId,
        rotationReason: context
      }
    });

    return { newSessionId, newToken };
  }

  /**
   * Destroy specific session
   */
  static async destroySession(sessionId: string): Promise<boolean> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      return false;
    }

    // Remove from tracking
    this.userSessions.get(session.userId)?.delete(sessionId);
    this.deviceSessions.get(session.deviceId)?.delete(sessionId);
    
    // Remove session
    this.sessions.delete(sessionId);

    return true;
  }

  /**
   * Destroy all sessions for a user
   */
  static async destroyAllUserSessions(userId: string, exceptSessionId?: string): Promise<number> {
    const userSessionIds = this.userSessions.get(userId);
    if (!userSessionIds) {
      return 0;
    }

    let destroyedCount = 0;
    
    for (const sessionId of userSessionIds) {
      if (sessionId !== exceptSessionId) {
        const destroyed = await this.destroySession(sessionId);
        if (destroyed) {
          destroyedCount++;
        }
      }
    }

    return destroyedCount;
  }

  /**
   * Get all sessions for a user
   */
  static async getUserSessions(userId: string): Promise<SessionData[]> {
    const userSessionIds = this.userSessions.get(userId);
    if (!userSessionIds) {
      return [];
    }

    const sessions: SessionData[] = [];
    
    for (const sessionId of userSessionIds) {
      const session = this.sessions.get(sessionId);
      if (session) {
        sessions.push(session);
      }
    }

    return sessions.sort((a, b) => b.lastActiveAt.getTime() - a.lastActiveAt.getTime());
  }

  /**
   * Update session security context
   */
  static async updateSessionSecurity(sessionId: string, updates: {
    isVerified?: boolean;
    isSSOAuthenticated?: boolean;
    lastStepUpAt?: Date;
    riskScore?: number;
    addScope?: string;
    removeScope?: string;
    addPermission?: string;
    removePermission?: string;
  }): Promise<boolean> {
    
    const session = this.sessions.get(sessionId);
    if (!session) {
      return false;
    }

    // Update security flags
    if (updates.isVerified !== undefined) {
      session.isVerified = updates.isVerified;
    }
    
    if (updates.isSSOAuthenticated !== undefined) {
      session.isSSOAuthenticated = updates.isSSOAuthenticated;
    }
    
    if (updates.lastStepUpAt) {
      session.lastStepUpAt = updates.lastStepUpAt;
    }
    
    if (updates.riskScore !== undefined) {
      session.riskScore = updates.riskScore;
      session.isSuspicious = updates.riskScore > this.SUSPICIOUS_THRESHOLD;
    }

    // Update scopes and permissions
    if (updates.addScope) {
      if (!session.scopes.includes(updates.addScope)) {
        session.scopes.push(updates.addScope);
      }
    }
    
    if (updates.removeScope) {
      session.scopes = session.scopes.filter(s => s !== updates.removeScope);
    }
    
    if (updates.addPermission) {
      if (!session.permissions.includes(updates.addPermission)) {
        session.permissions.push(updates.addPermission);
      }
    }
    
    if (updates.removePermission) {
      session.permissions = session.permissions.filter(p => p !== updates.removePermission);
    }

    // Mark for rotation if significant security change
    if (updates.isVerified || updates.isSSOAuthenticated || updates.lastStepUpAt) {
      session.requiresRotation = true;
    }

    session.lastActiveAt = new Date();
    
    return true;
  }

  /**
   * Generate secure session ID
   */
  private static generateSessionId(): string {
    const timestamp = Date.now().toString(36);
    const randomPart = Math.random().toString(36).substring(2);
    const extraEntropy = crypto.getRandomValues(new Uint8Array(16))
      .reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '');
    
    return `sess_${timestamp}_${randomPart}_${extraEntropy}`;
  }

  /**
   * Calculate risk score based on context
   */
  private static async calculateRiskScore(context: {
    userId: string;
    deviceId: string;
    ipAddress: string;
    userAgent: string;
    country?: string;
  }): Promise<number> {
    
    let riskScore = 0.0;

    // Check for new device
    const knownDevice = this.deviceSessions.has(context.deviceId);
    if (!knownDevice) {
      riskScore += 0.3;
    }

    // Check for IP changes (simplified)
    const userSessions = await this.getUserSessions(context.userId);
    const recentSession = userSessions.find(s => s.userId === context.userId);
    if (recentSession && recentSession.ipAddress !== context.ipAddress) {
      riskScore += 0.2;
    }

    // Check for unusual user agent
    if (context.userAgent.includes('bot') || context.userAgent.includes('crawler')) {
      riskScore += 0.4;
    }

    // Check for suspicious country (simplified)
    const suspiciousCountries = ['CN', 'RU', 'KP', 'IR'];
    if (context.country && suspiciousCountries.includes(context.country)) {
      riskScore += 0.2;
    }

    // Check concurrent sessions
    const activeSessions = userSessions.filter(s => {
      const idleTime = Date.now() - s.lastActiveAt.getTime();
      return idleTime < this.MAX_IDLE_TIME;
    });
    
    if (activeSessions.length > 3) {
      riskScore += 0.1;
    }

    return Math.min(1.0, riskScore);
  }

  /**
   * Calculate session durations based on tier and type
   */
  private static calculateSessionDurations(tier: TierLevel, sessionType: string): {
    maxIdleTime: number;
    maxSessionTime: number;
  } {
    const baseDurations = {
      web: { idle: 60 * 60 * 1000, max: 8 * 60 * 60 * 1000 }, // 1h idle, 8h max
      api: { idle: 30 * 60 * 1000, max: 24 * 60 * 60 * 1000 }, // 30m idle, 24h max
      mobile: { idle: 4 * 60 * 60 * 1000, max: 30 * 24 * 60 * 60 * 1000 }, // 4h idle, 30d max
      service: { idle: 5 * 60 * 1000, max: 60 * 60 * 1000 } // 5m idle, 1h max
    };

    const base = baseDurations[sessionType as keyof typeof baseDurations] || baseDurations.web;
    
    // Extend durations for higher tiers
    const tierMultipliers = {
      T1: 1.0,
      T2: 1.5,
      T3: 2.0,
      T4: 3.0,
      T5: 5.0
    };

    const multiplier = tierMultipliers[tier] || 1.0;
    
    return {
      maxIdleTime: Math.floor(base.idle * multiplier),
      maxSessionTime: Math.floor(base.max * multiplier)
    };
  }

  /**
   * Enforce concurrent session limits
   */
  private static async enforceConcurrentSessionLimits(userId: string): Promise<void> {
    const userSessions = await this.getUserSessions(userId);
    
    if (userSessions.length >= this.MAX_SESSIONS_PER_USER) {
      // Remove oldest inactive sessions
      const sessionsToRemove = userSessions
        .sort((a, b) => a.lastActiveAt.getTime() - b.lastActiveAt.getTime())
        .slice(0, userSessions.length - this.MAX_SESSIONS_PER_USER + 1);
      
      for (const session of sessionsToRemove) {
        await this.destroySession(session.sessionId);
        
        await this.logSecurityEvent({
          eventType: 'concurrent_limit',
          sessionId: session.sessionId,
          userId,
          description: 'Session removed due to concurrent limit',
          ipAddress: session.ipAddress,
          userAgent: session.userAgent,
          riskScore: session.riskScore,
          actionTaken: 'session_destroyed'
        });
      }
    }
  }

  /**
   * Log security events
   */
  private static async logSecurityEvent(event: Omit<SessionSecurityEvent, 'eventId' | 'timestamp'>): Promise<void> {
    const securityEvent: SessionSecurityEvent = {
      eventId: this.generateSessionId(),
      timestamp: new Date(),
      ...event
    };

    this.securityEvents.push(securityEvent);
    
    // Keep only recent events (last 1000)
    if (this.securityEvents.length > 1000) {
      this.securityEvents = this.securityEvents.slice(-1000);
    }

    // In production, send to security monitoring system
    console.log('SECURITY_EVENT:', JSON.stringify(securityEvent, null, 2));
  }

  /**
   * Get security events for a user
   */
  static getSecurityEvents(userId: string, limit = 50): SessionSecurityEvent[] {
    return this.securityEvents
      .filter(event => event.userId === userId)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
  }

  /**
   * Clean up expired sessions
   */
  static async cleanupExpiredSessions(): Promise<number> {
    const now = new Date();
    let cleanedUp = 0;

    for (const [sessionId, session] of this.sessions.entries()) {
      const isExpired = now > session.expiresAt;
      const isIdle = (now.getTime() - session.lastActiveAt.getTime()) > session.maxIdleTime;
      
      if (isExpired || isIdle) {
        await this.destroySession(sessionId);
        cleanedUp++;
      }
    }

    return cleanedUp;
  }

  /**
   * Get session statistics
   */
  static getStats(): {
    totalSessions: number;
    activeSessions: number;
    userCount: number;
    deviceCount: number;
    averageRiskScore: number;
    suspiciousSessions: number;
  } {
    const sessions = Array.from(this.sessions.values());
    const now = Date.now();
    
    const activeSessions = sessions.filter(s => {
      const idleTime = now - s.lastActiveAt.getTime();
      return idleTime < s.maxIdleTime && now < s.expiresAt.getTime();
    });

    const riskScores = sessions.map(s => s.riskScore);
    const averageRiskScore = riskScores.length > 0 
      ? riskScores.reduce((sum, score) => sum + score, 0) / riskScores.length 
      : 0;

    return {
      totalSessions: sessions.length,
      activeSessions: activeSessions.length,
      userCount: this.userSessions.size,
      deviceCount: this.deviceSessions.size,
      averageRiskScore,
      suspiciousSessions: sessions.filter(s => s.isSuspicious).length
    };
  }
}

export default SessionManager;