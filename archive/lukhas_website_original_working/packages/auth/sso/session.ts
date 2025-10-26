/**
 * SSO Session Management with Single Logout (SLO) Support
 * Enterprise session lifecycle management for LUKHAS AI ΛiD System
 * 
 * Supports:
 * - SSO session linking with local sessions
 * - Single Logout (SLO) support for SAML and OIDC
 * - Session timeout synchronization
 * - Cross-domain session management
 * - Session security and monitoring
 */

import { AuditLogger } from '../audit-logger';
import { SecurityFeatures } from '../security-features';
import { SAMLProvider } from './saml-provider';
import { OIDCProvider } from './oidc-provider';
import { ssoConfigManager } from './sso-config';

export interface SSOSession {
  id: string;
  tenantId: string;
  userId: string;
  userEmail: string;
  
  // SSO session details
  ssoSessionId?: string; // IdP session ID
  ssoSessionIndex?: string; // SAML session index
  idToken?: string; // OIDC ID token
  accessToken?: string; // OIDC access token
  refreshToken?: string; // OIDC refresh token
  
  // Provider information
  providerType: 'saml' | 'oidc';
  providerId: string;
  issuer: string;
  
  // Local session linking
  localSessionId: string;
  
  // Timing and lifecycle
  createdAt: Date;
  lastActivityAt: Date;
  expiresAt: Date;
  idpExpiresAt?: Date; // When IdP session expires
  
  // Session state
  status: 'active' | 'expired' | 'terminated' | 'logged_out';
  logoutInitiator?: 'user' | 'idp' | 'admin' | 'timeout' | 'security';
  
  // Security tracking
  ipAddress: string;
  userAgent: string;
  deviceFingerprint?: string;
  
  // Logout URLs and tokens
  logoutUrl?: string;
  logoutToken?: string; // For backchannel logout
  
  // Metadata
  metadata: {
    loginMethod: 'sp_initiated' | 'idp_initiated';
    attributes?: Record<string, any>;
    groups?: string[];
    roles?: string[];
  };
}

export interface SLORequest {
  id: string;
  sessionId: string;
  tenantId: string;
  userId: string;
  
  // SLO details
  sloType: 'front_channel' | 'back_channel' | 'admin_initiated';
  initiator: 'user' | 'idp' | 'admin' | 'security' | 'timeout';
  
  // Provider-specific data
  samlLogoutRequest?: string; // Base64 encoded SAML logout request
  oidcLogoutToken?: string; // OIDC logout token
  
  // Processing status
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'partial';
  startedAt: Date;
  completedAt?: Date;
  
  // Steps to complete
  steps: Array<{
    type: 'local_logout' | 'idp_logout' | 'session_cleanup' | 'notify_applications';
    status: 'pending' | 'completed' | 'failed';
    completedAt?: Date;
    error?: string;
  }>;
  
  // Related sessions (for global logout)
  relatedSessions?: string[];
  
  // Error handling
  errors: string[];
  warnings: string[];
}

export interface SessionSyncResult {
  sessionId: string;
  syncType: 'refresh' | 'validate' | 'cleanup';
  success: boolean;
  
  // Sync details
  tokenRefreshed?: boolean;
  sessionExtended?: boolean;
  issuesFound?: string[];
  actionsPerformed?: string[];
  
  timestamp: Date;
}

export class SSOSessionManager {
  private auditLogger: AuditLogger;
  private security: SecurityFeatures;
  private sessions = new Map<string, SSOSession>();
  private sloRequests = new Map<string, SLORequest>();
  private userSessions = new Map<string, string[]>(); // userId -> sessionIds
  private tenantSessions = new Map<string, string[]>(); // tenantId -> sessionIds
  private backgroundJobs = new Map<string, NodeJS.Timeout>();

  // Configuration
  private readonly SESSION_TIMEOUT_MINUTES = 480; // 8 hours default
  private readonly SESSION_SYNC_INTERVAL_MINUTES = 5;
  private readonly SLO_TIMEOUT_SECONDS = 30;

  constructor(auditLogger: AuditLogger) {
    this.auditLogger = auditLogger;
    this.security = new SecurityFeatures();

    this.startBackgroundJobs();
  }

  /**
   * Create SSO session after successful authentication
   */
  async createSSOSession(
    userId: string,
    userEmail: string,
    tenantId: string,
    providerType: 'saml' | 'oidc',
    authResult: any, // SAML or OIDC authentication result
    localSessionId: string,
    clientInfo: { ipAddress: string; userAgent: string }
  ): Promise<SSOSession> {
    try {
      const sessionId = this.generateSessionId();
      const now = new Date();
      const expiresAt = new Date(now.getTime() + (this.SESSION_TIMEOUT_MINUTES * 60 * 1000));

      const session: SSOSession = {
        id: sessionId,
        tenantId,
        userId,
        userEmail,
        providerType,
        providerId: authResult.issuer || authResult.provider,
        issuer: authResult.issuer,
        localSessionId,
        createdAt: now,
        lastActivityAt: now,
        expiresAt,
        status: 'active',
        ipAddress: clientInfo.ipAddress,
        userAgent: clientInfo.userAgent,
        metadata: {
          loginMethod: authResult.loginMethod || 'sp_initiated',
          attributes: authResult.attributes,
          groups: authResult.groups,
          roles: authResult.roles
        }
      };

      // Set provider-specific session data
      if (providerType === 'saml') {
        session.ssoSessionIndex = authResult.sessionIndex;
        session.idpExpiresAt = authResult.sessionNotOnOrAfter;
      } else if (providerType === 'oidc') {
        session.idToken = authResult.idToken;
        session.accessToken = authResult.accessToken;
        session.refreshToken = authResult.refreshToken;
        session.idpExpiresAt = new Date(Date.now() + (authResult.expiresIn * 1000));
      }

      // Generate device fingerprint for security
      session.deviceFingerprint = await this.security.generateDeviceFingerprint(
        clientInfo.userAgent,
        clientInfo.ipAddress
      );

      // Store session
      this.sessions.set(sessionId, session);

      // Update indexes
      if (!this.userSessions.has(userId)) {
        this.userSessions.set(userId, []);
      }
      this.userSessions.get(userId)!.push(sessionId);

      if (!this.tenantSessions.has(tenantId)) {
        this.tenantSessions.set(tenantId, []);
      }
      this.tenantSessions.get(tenantId)!.push(sessionId);

      await this.auditLogger.logSecurityEvent('sso_session_created', {
        sessionId,
        userId,
        userEmail,
        tenantId,
        providerType,
        providerId: session.providerId,
        ipAddress: clientInfo.ipAddress,
        userAgent: clientInfo.userAgent,
        loginMethod: session.metadata.loginMethod
      });

      return session;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('sso_session_create_failed', {
        userId,
        userEmail,
        tenantId,
        providerType,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Initiate Single Logout (SLO) process
   */
  async initiateSingleLogout(
    sessionId: string,
    initiator: SLORequest['initiator'],
    sloType: SLORequest['sloType'] = 'front_channel',
    globalLogout: boolean = false
  ): Promise<SLORequest> {
    try {
      const session = this.sessions.get(sessionId);
      if (!session) {
        throw new Error(`Session not found: ${sessionId}`);
      }

      const sloId = this.generateSLOId();
      const now = new Date();

      // Determine related sessions for global logout
      const relatedSessions = globalLogout 
        ? (this.userSessions.get(session.userId) || []).filter(id => id !== sessionId)
        : undefined;

      const sloRequest: SLORequest = {
        id: sloId,
        sessionId,
        tenantId: session.tenantId,
        userId: session.userId,
        sloType,
        initiator,
        status: 'pending',
        startedAt: now,
        steps: [
          { type: 'local_logout', status: 'pending' },
          { type: 'idp_logout', status: 'pending' },
          { type: 'session_cleanup', status: 'pending' }
        ],
        relatedSessions,
        errors: [],
        warnings: []
      };

      // Add application notification step if there are related sessions
      if (relatedSessions && relatedSessions.length > 0) {
        sloRequest.steps.push({ type: 'notify_applications', status: 'pending' });
      }

      this.sloRequests.set(sloId, sloRequest);

      await this.auditLogger.logSecurityEvent('slo_initiated', {
        sloId,
        sessionId,
        userId: session.userId,
        tenantId: session.tenantId,
        initiator,
        sloType,
        globalLogout,
        relatedSessionCount: relatedSessions?.length || 0
      });

      // Start SLO processing
      await this.processSLORequest(sloRequest);

      return sloRequest;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('slo_initiation_failed', {
        sessionId,
        initiator,
        sloType,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Process SAML logout request from IdP
   */
  async processSAMLLogoutRequest(
    logoutRequest: string,
    tenantId: string
  ): Promise<{ success: boolean; logoutResponse?: string; redirectUrl?: string }> {
    try {
      // Get tenant configuration
      const tenantConfig = ssoConfigManager.getTenantConfig(tenantId);
      if (!tenantConfig || tenantConfig.providerType !== 'saml') {
        throw new Error('Invalid tenant configuration for SAML logout');
      }

      // Create SAML provider
      const provider = await ssoConfigManager.createProvider(tenantId) as SAMLProvider;

      // Parse logout request (simplified - would use proper SAML library)
      const sessionIndex = this.extractSAMLSessionIndex(logoutRequest);
      const nameId = this.extractSAMLNameId(logoutRequest);

      // Find session by session index
      const session = this.findSessionBySessionIndex(sessionIndex, tenantId);
      if (!session) {
        await this.auditLogger.logSecurityEvent('saml_logout_session_not_found', {
          tenantId,
          sessionIndex,
          nameId
        });
        
        // Still return success to IdP
        return { success: true };
      }

      // Initiate SLO for this session
      await this.initiateSingleLogout(session.id, 'idp', 'back_channel');

      // Generate logout response
      const logoutResponse = await this.generateSAMLLogoutResponse(provider, true);

      await this.auditLogger.logSecurityEvent('saml_logout_processed', {
        tenantId,
        sessionId: session.id,
        userId: session.userId,
        sessionIndex,
        nameId
      });

      return {
        success: true,
        logoutResponse,
        redirectUrl: tenantConfig.providerConfig.sloUrl
      };

    } catch (error) {
      await this.auditLogger.logSecurityEvent('saml_logout_processing_failed', {
        tenantId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Process OIDC logout token for backchannel logout
   */
  async processOIDCLogoutToken(
    logoutToken: string,
    tenantId: string
  ): Promise<{ success: boolean }> {
    try {
      // Get tenant configuration
      const tenantConfig = ssoConfigManager.getTenantConfig(tenantId);
      if (!tenantConfig || tenantConfig.providerType !== 'oidc') {
        throw new Error('Invalid tenant configuration for OIDC logout');
      }

      // Create OIDC provider
      const provider = await ssoConfigManager.createProvider(tenantId) as OIDCProvider;

      // Validate logout token (simplified - would use proper JWT verification)
      const tokenClaims = await this.validateOIDCLogoutToken(logoutToken, provider);
      
      // Find sessions by user ID or session ID
      const sessions = this.findSessionsByUser(tokenClaims.sub, tenantId);

      // Initiate SLO for all matching sessions
      for (const session of sessions) {
        await this.initiateSingleLogout(session.id, 'idp', 'back_channel');
      }

      await this.auditLogger.logSecurityEvent('oidc_logout_token_processed', {
        tenantId,
        userId: tokenClaims.sub,
        sessionCount: sessions.length
      });

      return { success: true };

    } catch (error) {
      await this.auditLogger.logSecurityEvent('oidc_logout_token_processing_failed', {
        tenantId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Refresh session tokens (for OIDC)
   */
  async refreshSessionTokens(sessionId: string): Promise<SessionSyncResult> {
    const result: SessionSyncResult = {
      sessionId,
      syncType: 'refresh',
      success: false,
      timestamp: new Date()
    };

    try {
      const session = this.sessions.get(sessionId);
      if (!session) {
        throw new Error(`Session not found: ${sessionId}`);
      }

      if (session.providerType !== 'oidc' || !session.refreshToken) {
        result.warnings = ['Session does not support token refresh'];
        result.success = true;
        return result;
      }

      // Get OIDC provider
      const provider = await ssoConfigManager.createProvider(session.tenantId) as OIDCProvider;

      // Refresh tokens
      const newTokens = await provider.refreshAccessToken(session.refreshToken);

      // Update session
      session.accessToken = newTokens.accessToken;
      session.idToken = newTokens.idToken;
      if (newTokens.refreshToken) {
        session.refreshToken = newTokens.refreshToken;
      }
      session.lastActivityAt = new Date();
      session.idpExpiresAt = new Date(Date.now() + (newTokens.expiresIn * 1000));

      result.success = true;
      result.tokenRefreshed = true;
      result.actionsPerformed = ['refreshed_access_token', 'updated_session'];

      await this.auditLogger.logSecurityEvent('session_tokens_refreshed', {
        sessionId,
        userId: session.userId,
        tenantId: session.tenantId
      });

    } catch (error) {
      result.issuesFound = [error instanceof Error ? error.message : 'Unknown error'];
      
      await this.auditLogger.logSecurityEvent('session_token_refresh_failed', {
        sessionId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }

    return result;
  }

  /**
   * Get active sessions for user
   */
  getUserSessions(userId: string): SSOSession[] {
    const sessionIds = this.userSessions.get(userId) || [];
    return sessionIds
      .map(id => this.sessions.get(id))
      .filter(session => session && session.status === 'active') as SSOSession[];
  }

  /**
   * Get active sessions for tenant
   */
  getTenantSessions(tenantId: string): SSOSession[] {
    const sessionIds = this.tenantSessions.get(tenantId) || [];
    return sessionIds
      .map(id => this.sessions.get(id))
      .filter(session => session && session.status === 'active') as SSOSession[];
  }

  /**
   * Get SLO request status
   */
  getSLORequest(sloId: string): SLORequest | null {
    return this.sloRequests.get(sloId) || null;
  }

  private async processSLORequest(sloRequest: SLORequest): Promise<void> {
    try {
      sloRequest.status = 'in_progress';

      const session = this.sessions.get(sloRequest.sessionId);
      if (!session) {
        throw new Error('Session not found for SLO request');
      }

      // Step 1: Local logout
      await this.executeStep(sloRequest, 'local_logout', async () => {
        session.status = 'logged_out';
        session.logoutInitiator = sloRequest.initiator;
      });

      // Step 2: IdP logout (if not initiated by IdP)
      if (sloRequest.initiator !== 'idp') {
        await this.executeStep(sloRequest, 'idp_logout', async () => {
          await this.performIdPLogout(session, sloRequest);
        });
      }

      // Step 3: Session cleanup
      await this.executeStep(sloRequest, 'session_cleanup', async () => {
        await this.cleanupSession(session);
      });

      // Step 4: Notify applications (if global logout)
      if (sloRequest.relatedSessions && sloRequest.relatedSessions.length > 0) {
        await this.executeStep(sloRequest, 'notify_applications', async () => {
          await this.notifyRelatedApplications(sloRequest.relatedSessions!);
        });
      }

      sloRequest.status = 'completed';
      sloRequest.completedAt = new Date();

      await this.auditLogger.logSecurityEvent('slo_completed', {
        sloId: sloRequest.id,
        sessionId: sloRequest.sessionId,
        userId: sloRequest.userId,
        tenantId: sloRequest.tenantId,
        duration: sloRequest.completedAt.getTime() - sloRequest.startedAt.getTime()
      });

    } catch (error) {
      sloRequest.status = 'failed';
      sloRequest.errors.push(error instanceof Error ? error.message : 'Unknown error');

      await this.auditLogger.logSecurityEvent('slo_failed', {
        sloId: sloRequest.id,
        sessionId: sloRequest.sessionId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  private async executeStep(
    sloRequest: SLORequest,
    stepType: SLORequest['steps'][0]['type'],
    handler: () => Promise<void>
  ): Promise<void> {
    const step = sloRequest.steps.find(s => s.type === stepType);
    if (!step) return;

    try {
      await handler();
      step.status = 'completed';
      step.completedAt = new Date();
    } catch (error) {
      step.status = 'failed';
      step.error = error instanceof Error ? error.message : 'Unknown error';
      sloRequest.errors.push(`${stepType}: ${step.error}`);
    }
  }

  private async performIdPLogout(session: SSOSession, sloRequest: SLORequest): Promise<void> {
    if (session.providerType === 'saml') {
      // Generate SAML logout request
      const provider = await ssoConfigManager.createProvider(session.tenantId) as SAMLProvider;
      const logoutRequest = await provider.generateLogoutRequest(
        session.userEmail,
        session.ssoSessionIndex
      );
      sloRequest.samlLogoutRequest = logoutRequest;
    } else if (session.providerType === 'oidc') {
      // For OIDC, we would typically call the end_session_endpoint
      const provider = await ssoConfigManager.createProvider(session.tenantId) as OIDCProvider;
      const logoutUrl = provider.generateLogoutUrl(session.idToken);
      if (logoutUrl) {
        session.logoutUrl = logoutUrl;
      }
    }
  }

  private async cleanupSession(session: SSOSession): Promise<void> {
    // Remove from indexes
    const userSessions = this.userSessions.get(session.userId);
    if (userSessions) {
      const index = userSessions.indexOf(session.id);
      if (index >= 0) {
        userSessions.splice(index, 1);
      }
    }

    const tenantSessions = this.tenantSessions.get(session.tenantId);
    if (tenantSessions) {
      const index = tenantSessions.indexOf(session.id);
      if (index >= 0) {
        tenantSessions.splice(index, 1);
      }
    }

    // Remove session (could be moved to archive instead)
    this.sessions.delete(session.id);
  }

  private async notifyRelatedApplications(sessionIds: string[]): Promise<void> {
    // In a real implementation, this would notify other applications
    // about the logout event for session coordination
    for (const sessionId of sessionIds) {
      const session = this.sessions.get(sessionId);
      if (session) {
        await this.initiateSingleLogout(sessionId, 'admin', 'back_channel');
      }
    }
  }

  private findSessionBySessionIndex(sessionIndex: string, tenantId: string): SSOSession | null {
    for (const session of this.sessions.values()) {
      if (session.tenantId === tenantId && 
          session.ssoSessionIndex === sessionIndex &&
          session.status === 'active') {
        return session;
      }
    }
    return null;
  }

  private findSessionsByUser(userId: string, tenantId: string): SSOSession[] {
    const sessionIds = this.userSessions.get(userId) || [];
    return sessionIds
      .map(id => this.sessions.get(id))
      .filter(session => 
        session && 
        session.tenantId === tenantId && 
        session.status === 'active'
      ) as SSOSession[];
  }

  private extractSAMLSessionIndex(logoutRequest: string): string {
    // Simplified SAML parsing - would use proper SAML library
    return 'session_index_placeholder';
  }

  private extractSAMLNameId(logoutRequest: string): string {
    // Simplified SAML parsing - would use proper SAML library
    return 'nameid_placeholder';
  }

  private async generateSAMLLogoutResponse(provider: SAMLProvider, success: boolean): Promise<string> {
    // Would use the SAMLProvider to generate proper logout response
    return Buffer.from('<LogoutResponse>Success</LogoutResponse>').toString('base64');
  }

  private async validateOIDCLogoutToken(logoutToken: string, provider: OIDCProvider): Promise<any> {
    // Would use proper JWT validation
    return { sub: 'user_id_placeholder' };
  }

  private startBackgroundJobs(): void {
    // Session timeout monitoring
    const timeoutMonitor = setInterval(async () => {
      const now = new Date();
      
      for (const [sessionId, session] of this.sessions) {
        if (session.status === 'active' && session.expiresAt < now) {
          await this.initiateSingleLogout(sessionId, 'timeout', 'back_channel');
        }
      }
    }, 60 * 1000); // Check every minute

    this.backgroundJobs.set('timeout_monitor', timeoutMonitor);

    // Token refresh for OIDC sessions
    const tokenRefresh = setInterval(async () => {
      for (const [sessionId, session] of this.sessions) {
        if (session.status === 'active' && 
            session.providerType === 'oidc' &&
            session.idpExpiresAt &&
            session.idpExpiresAt.getTime() - Date.now() < (5 * 60 * 1000)) { // 5 minutes before expiry
          
          await this.refreshSessionTokens(sessionId);
        }
      }
    }, this.SESSION_SYNC_INTERVAL_MINUTES * 60 * 1000);

    this.backgroundJobs.set('token_refresh', tokenRefresh);
  }

  private generateSessionId(): string {
    return 'sso_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }

  private generateSLOId(): string {
    return 'slo_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Cleanup method for stopping background jobs
   */
  public cleanup(): void {
    for (const [jobName, intervalId] of this.backgroundJobs) {
      clearInterval(intervalId);
    }
    this.backgroundJobs.clear();
  }
}