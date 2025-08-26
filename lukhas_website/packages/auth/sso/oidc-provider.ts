/**
 * OpenID Connect 1.0 Provider Implementation
 * Enterprise-grade OIDC integration for LUKHAS AI ΛiD System
 *
 * Supports:
 * - Authorization Code Flow with PKCE
 * - ID token validation and claims extraction
 * - Okta, Azure AD, Google Workspace
 * - Security: state validation, nonce verification, JWT validation
 */

import { randomBytes, createHash } from 'crypto';
import { JWTVerifier, JWKSManager } from '../jwt';
import { AuditLogger } from '../audit-logger';
import { SecurityFeatures } from '../security-features';

export interface OIDCConfig {
  issuer: string;
  clientId: string;
  clientSecret?: string;
  redirectUri: string;
  scopes: string[];
  responseType?: string;
  responseMode?: string;
  prompt?: string;
  maxAge?: number;
  acrValues?: string[];
  uiLocales?: string[];
  claimsLocales?: string[];
  clockTolerance?: number; // seconds
  usePKCE?: boolean;
  codeChallenge?: 'S256' | 'plain';
}

export interface OIDCEndpoints {
  authorization: string;
  token: string;
  userinfo: string;
  jwks: string;
  endSession?: string;
  introspection?: string;
  revocation?: string;
}

export interface OIDCClaims {
  sub: string;
  iss: string;
  aud: string | string[];
  exp: number;
  iat: number;
  auth_time?: number;
  nonce?: string;
  acr?: string;
  amr?: string[];
  azp?: string;

  // Standard profile claims
  name?: string;
  given_name?: string;
  family_name?: string;
  middle_name?: string;
  nickname?: string;
  preferred_username?: string;
  profile?: string;
  picture?: string;
  website?: string;
  gender?: string;
  birthdate?: string;
  zoneinfo?: string;
  locale?: string;
  updated_at?: number;

  // Standard email claims
  email?: string;
  email_verified?: boolean;

  // Standard address claims
  address?: {
    formatted?: string;
    street_address?: string;
    locality?: string;
    region?: string;
    postal_code?: string;
    country?: string;
  };

  // Standard phone claims
  phone_number?: string;
  phone_number_verified?: boolean;

  // Custom claims
  [key: string]: any;
}

export interface OIDCTokens {
  accessToken: string;
  idToken: string;
  refreshToken?: string;
  tokenType: string;
  expiresIn: number;
  scope?: string;
}

export interface OIDCState {
  state: string;
  nonce: string;
  codeVerifier?: string;
  codeChallenge?: string;
  codeChallengeMethod?: string;
  timestamp: number;
  redirectUri: string;
}

export class OIDCProvider {
  private config: OIDCConfig;
  private endpoints: OIDCEndpoints;
  private auditLogger: AuditLogger;
  private security: SecurityFeatures;
  private jwtVerifier: JWTVerifier;
  private jwksManager: JWKSManager;
  private pendingStates = new Map<string, OIDCState>();

  constructor(
    config: OIDCConfig,
    endpoints: OIDCEndpoints,
    auditLogger: AuditLogger
  ) {
    this.config = config;
    this.endpoints = endpoints;
    this.auditLogger = auditLogger;
    this.security = new SecurityFeatures();
    this.jwksManager = new JWKSManager(endpoints.jwks);
    this.jwtVerifier = new JWTVerifier(this.jwksManager);

    // Cleanup expired states every 10 minutes
    setInterval(() => this.cleanupExpiredStates(), 10 * 60 * 1000);
  }

  /**
   * Generate authorization URL with PKCE
   */
  async generateAuthorizationUrl(additionalParams?: Record<string, string>): Promise<{ url: string; state: string }> {
    const state = this.generateRandomString(32);
    const nonce = this.generateRandomString(32);

    let codeVerifier: string | undefined;
    let codeChallenge: string | undefined;
    let codeChallengeMethod: string | undefined;

    // Generate PKCE parameters if enabled
    if (this.config.usePKCE !== false) { // Default to true
      codeVerifier = this.generateRandomString(128);
      codeChallengeMethod = this.config.codeChallenge || 'S256';

      if (codeChallengeMethod === 'S256') {
        codeChallenge = createHash('sha256')
          .update(codeVerifier)
          .digest('base64url');
      } else {
        codeChallenge = codeVerifier;
      }
    }

    // Store state for validation
    this.pendingStates.set(state, {
      state,
      nonce,
      codeVerifier,
      codeChallenge,
      codeChallengeMethod,
      timestamp: Date.now(),
      redirectUri: this.config.redirectUri
    });

    // Build authorization URL
    const params = new URLSearchParams({
      response_type: this.config.responseType || 'code',
      client_id: this.config.clientId,
      redirect_uri: this.config.redirectUri,
      scope: this.config.scopes.join(' '),
      state,
      nonce
    });

    if (this.config.responseMode) {
      params.append('response_mode', this.config.responseMode);
    }

    if (this.config.prompt) {
      params.append('prompt', this.config.prompt);
    }

    if (this.config.maxAge !== undefined) {
      params.append('max_age', this.config.maxAge.toString());
    }

    if (this.config.acrValues) {
      params.append('acr_values', this.config.acrValues.join(' '));
    }

    if (this.config.uiLocales) {
      params.append('ui_locales', this.config.uiLocales.join(' '));
    }

    if (this.config.claimsLocales) {
      params.append('claims_locales', this.config.claimsLocales.join(' '));
    }

    if (codeChallenge) {
      params.append('code_challenge', codeChallenge);
      params.append('code_challenge_method', codeChallengeMethod!);
    }

    // Add additional parameters
    if (additionalParams) {
      for (const [key, value] of Object.entries(additionalParams)) {
        params.append(key, value);
      }
    }

    const url = `${this.endpoints.authorization}?${params.toString()}`;

    await this.auditLogger.logSecurityEvent('oidc_authorization_url_generated', {
      state,
      hasPKCE: !!codeChallenge,
      scopes: this.config.scopes,
      prompt: this.config.prompt,
      additionalParamsCount: additionalParams ? Object.keys(additionalParams).length : 0
    });

    return { url, state };
  }

  /**
   * Exchange authorization code for tokens
   */
  async exchangeCodeForTokens(code: string, state: string): Promise<OIDCTokens> {
    // Validate state
    const pendingState = this.pendingStates.get(state);
    if (!pendingState) {
      throw new Error('Invalid or expired state parameter');
    }

    this.pendingStates.delete(state);

    try {
      // Prepare token request
      const tokenParams = new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: pendingState.redirectUri,
        client_id: this.config.clientId
      });

      if (pendingState.codeVerifier) {
        tokenParams.append('code_verifier', pendingState.codeVerifier);
      }

      // Add client secret if available
      if (this.config.clientSecret) {
        tokenParams.append('client_secret', this.config.clientSecret);
      }

      // Make token request
      const response = await fetch(this.endpoints.token, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        },
        body: tokenParams.toString()
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Token exchange failed: ${response.status} ${errorText}`);
      }

      const tokens = await response.json() as OIDCTokens;

      // Validate tokens
      await this.validateTokens(tokens, pendingState);

      await this.auditLogger.logSecurityEvent('oidc_tokens_exchanged', {
        state,
        tokenType: tokens.tokenType,
        expiresIn: tokens.expiresIn,
        hasRefreshToken: !!tokens.refreshToken,
        scope: tokens.scope
      });

      return tokens;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('oidc_token_exchange_failed', {
        state,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Validate and decode ID token
   */
  async validateIdToken(idToken: string, nonce?: string): Promise<OIDCClaims> {
    try {
      // Verify JWT signature and basic claims
      const payload = await this.jwtVerifier.verifyToken(idToken, {
        issuer: this.config.issuer,
        audience: this.config.clientId,
        clockTolerance: this.config.clockTolerance || 60
      }) as OIDCClaims;

      // Validate OIDC-specific claims
      if (!payload.sub) {
        throw new Error('Missing required "sub" claim in ID token');
      }

      if (payload.iss !== this.config.issuer) {
        throw new Error(`Invalid issuer: expected ${this.config.issuer}, got ${payload.iss}`);
      }

      // Validate audience
      const audiences = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
      if (!audiences.includes(this.config.clientId)) {
        throw new Error(`Invalid audience: token not intended for client ${this.config.clientId}`);
      }

      // Validate nonce if provided
      if (nonce && payload.nonce !== nonce) {
        throw new Error('Nonce mismatch in ID token');
      }

      // Validate auth_time if max_age was specified
      if (this.config.maxAge !== undefined && payload.auth_time) {
        const maxAuthTime = Math.floor(Date.now() / 1000) - this.config.maxAge;
        if (payload.auth_time < maxAuthTime) {
          throw new Error('Authentication is too old based on max_age requirement');
        }
      }

      await this.auditLogger.logSecurityEvent('oidc_id_token_validated', {
        sub: payload.sub,
        iss: payload.iss,
        aud: Array.isArray(payload.aud) ? payload.aud : [payload.aud],
        authTime: payload.auth_time,
        hasNonce: !!payload.nonce
      });

      return payload;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('oidc_id_token_validation_failed', {
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Get user info from userinfo endpoint
   */
  async getUserInfo(accessToken: string): Promise<OIDCClaims> {
    try {
      const response = await fetch(this.endpoints.userinfo, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`UserInfo request failed: ${response.status}`);
      }

      const userInfo = await response.json() as OIDCClaims;

      await this.auditLogger.logSecurityEvent('oidc_userinfo_retrieved', {
        sub: userInfo.sub,
        claimsCount: Object.keys(userInfo).length
      });

      return userInfo;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('oidc_userinfo_failed', {
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Refresh access token
   */
  async refreshAccessToken(refreshToken: string): Promise<OIDCTokens> {
    try {
      const tokenParams = new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
        client_id: this.config.clientId
      });

      if (this.config.clientSecret) {
        tokenParams.append('client_secret', this.config.clientSecret);
      }

      const response = await fetch(this.endpoints.token, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        },
        body: tokenParams.toString()
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Token refresh failed: ${response.status} ${errorText}`);
      }

      const tokens = await response.json() as OIDCTokens;

      await this.auditLogger.logSecurityEvent('oidc_token_refreshed', {
        tokenType: tokens.tokenType,
        expiresIn: tokens.expiresIn,
        hasNewRefreshToken: !!tokens.refreshToken
      });

      return tokens;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('oidc_token_refresh_failed', {
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Generate logout URL
   */
  generateLogoutUrl(idTokenHint?: string, postLogoutRedirectUri?: string): string | null {
    if (!this.endpoints.endSession) {
      return null;
    }

    const params = new URLSearchParams();

    if (idTokenHint) {
      params.append('id_token_hint', idTokenHint);
    }

    if (postLogoutRedirectUri) {
      params.append('post_logout_redirect_uri', postLogoutRedirectUri);
    }

    return `${this.endpoints.endSession}?${params.toString()}`;
  }

  /**
   * Introspect token (if supported)
   */
  async introspectToken(token: string): Promise<any> {
    if (!this.endpoints.introspection) {
      throw new Error('Token introspection not supported by this provider');
    }

    const params = new URLSearchParams({
      token,
      client_id: this.config.clientId
    });

    if (this.config.clientSecret) {
      params.append('client_secret', this.config.clientSecret);
    }

    const response = await fetch(this.endpoints.introspection, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      body: params.toString()
    });

    if (!response.ok) {
      throw new Error(`Token introspection failed: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Revoke token (if supported)
   */
  async revokeToken(token: string, tokenTypeHint?: 'access_token' | 'refresh_token'): Promise<void> {
    if (!this.endpoints.revocation) {
      throw new Error('Token revocation not supported by this provider');
    }

    const params = new URLSearchParams({
      token,
      client_id: this.config.clientId
    });

    if (tokenTypeHint) {
      params.append('token_type_hint', tokenTypeHint);
    }

    if (this.config.clientSecret) {
      params.append('client_secret', this.config.clientSecret);
    }

    const response = await fetch(this.endpoints.revocation, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params.toString()
    });

    if (!response.ok) {
      throw new Error(`Token revocation failed: ${response.status}`);
    }

    await this.auditLogger.logSecurityEvent('oidc_token_revoked', {
      tokenTypeHint
    });
  }

  private generateRandomString(length: number): string {
    return randomBytes(Math.ceil(length / 2))
      .toString('hex')
      .slice(0, length);
  }

  private async validateTokens(tokens: OIDCTokens, state: OIDCState): Promise<void> {
    if (!tokens.accessToken || !tokens.idToken) {
      throw new Error('Missing required tokens in response');
    }

    if (tokens.tokenType?.toLowerCase() !== 'bearer') {
      throw new Error(`Unsupported token type: ${tokens.tokenType}`);
    }

    // Validate ID token
    await this.validateIdToken(tokens.idToken, state.nonce);
  }

  private cleanupExpiredStates(): void {
    const now = Date.now();
    const maxAge = 10 * 60 * 1000; // 10 minutes

    for (const [state, stateData] of this.pendingStates.entries()) {
      if (now - stateData.timestamp > maxAge) {
        this.pendingStates.delete(state);
      }
    }
  }
}

/**
 * Discover OIDC endpoints from issuer
 */
export async function discoverOIDCEndpoints(issuer: string): Promise<OIDCEndpoints> {
  const discoveryUrl = `${issuer}/.well-known/openid_configuration`;

  const response = await fetch(discoveryUrl);
  if (!response.ok) {
    throw new Error(`OIDC discovery failed: ${response.status}`);
  }

  const config = await response.json();

  return {
    authorization: config.authorization_endpoint,
    token: config.token_endpoint,
    userinfo: config.userinfo_endpoint,
    jwks: config.jwks_uri,
    endSession: config.end_session_endpoint,
    introspection: config.introspection_endpoint,
    revocation: config.revocation_endpoint
  };
}

/**
 * Factory for creating OIDC providers for different IdPs
 */
export class OIDCProviderFactory {
  static async createOktaProvider(
    domain: string,
    clientId: string,
    clientSecret: string,
    redirectUri: string,
    auditLogger: AuditLogger
  ): Promise<OIDCProvider> {
    const issuer = `https://${domain}`;
    const endpoints = await discoverOIDCEndpoints(issuer);

    const config: OIDCConfig = {
      issuer,
      clientId,
      clientSecret,
      redirectUri,
      scopes: ['openid', 'profile', 'email'],
      usePKCE: true,
      codeChallenge: 'S256'
    };

    return new OIDCProvider(config, endpoints, auditLogger);
  }

  static async createAzureADProvider(
    tenantId: string,
    clientId: string,
    clientSecret: string,
    redirectUri: string,
    auditLogger: AuditLogger
  ): Promise<OIDCProvider> {
    const issuer = `https://login.microsoftonline.com/${tenantId}/v2.0`;
    const endpoints = await discoverOIDCEndpoints(issuer);

    const config: OIDCConfig = {
      issuer,
      clientId,
      clientSecret,
      redirectUri,
      scopes: ['openid', 'profile', 'email'],
      usePKCE: true,
      codeChallenge: 'S256'
    };

    return new OIDCProvider(config, endpoints, auditLogger);
  }

  static async createGoogleProvider(
    clientId: string,
    clientSecret: string,
    redirectUri: string,
    auditLogger: AuditLogger
  ): Promise<OIDCProvider> {
    const issuer = 'https://accounts.google.com';
    const endpoints = await discoverOIDCEndpoints(issuer);

    const config: OIDCConfig = {
      issuer,
      clientId,
      clientSecret,
      redirectUri,
      scopes: ['openid', 'profile', 'email'],
      usePKCE: true,
      codeChallenge: 'S256'
    };

    return new OIDCProvider(config, endpoints, auditLogger);
  }
}
