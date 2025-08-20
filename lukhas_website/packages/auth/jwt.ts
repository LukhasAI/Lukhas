/**
 * JWT Management for ΛiD Authentication System
 * 
 * Implements RS256 token issue/verify with JWKS integration, token validation,
 * and secure refresh mechanisms building on the Phase 0 JWKS infrastructure.
 */

import { SignJWT, jwtVerify, importPKCS8, importSPKI, JWTPayload, JWTVerifyResult } from 'jose';
import { JWKSManager, JWKSKey } from './jwks';
import { TierLevel } from './scopes';
import { createHash, randomBytes } from 'crypto';

export interface TokenClaims extends JWTPayload {
  // Standard claims
  sub: string;          // Subject (user ID)
  iss: string;          // Issuer (LUKHAS AI)
  aud: string | string[]; // Audience
  exp: number;          // Expiration time
  iat: number;          // Issued at
  jti: string;          // JWT ID (unique token identifier)
  
  // ΛiD specific claims
  'lukhas:tier': TierLevel;
  'lukhas:session_id': string;
  'lukhas:device_id'?: string;
  'lukhas:scopes': string[];
  'lukhas:roles': string[];
  'lukhas:org_id'?: string;
  'lukhas:refresh_family'?: string;
  'lukhas:token_type': 'access' | 'refresh' | 'id';
  'lukhas:ip_hash': string;
}

export interface TokenConfig {
  issuer: string;
  audience: string;
  accessTokenTTL: number;   // Access token TTL in seconds
  refreshTokenTTL: number;  // Refresh token TTL in seconds
  idTokenTTL: number;       // ID token TTL in seconds
  maxRefreshAge: number;    // Maximum refresh token age in seconds
  allowedClockSkew: number; // Clock skew tolerance in seconds
}

export interface TokenValidationOptions {
  audience?: string | string[];
  issuer?: string;
  clockTolerance?: number;
  maxTokenAge?: number;
  requiredClaims?: string[];
  allowExpired?: boolean;
}

export interface TokenValidationResult {
  valid: boolean;
  payload?: TokenClaims;
  error?: string;
  kid?: string;
  expired?: boolean;
  metadata?: Record<string, any>;
}

export interface RefreshTokenFamily {
  familyId: string;
  userId: string;
  deviceId: string;
  createdAt: number;
  lastUsed: number;
  revoked: boolean;
  revokedAt?: number;
  tokenCount: number;
}

/**
 * Core JWT management class
 */
export class JWTManager {
  private config: TokenConfig;
  private jwksManager: JWKSManager;
  private refreshFamilies: Map<string, RefreshTokenFamily> = new Map();

  constructor(config: TokenConfig, jwksManager: JWKSManager) {
    this.config = config;
    this.jwksManager = jwksManager;
  }

  /**
   * Issue access token
   */
  async issueAccessToken(
    userId: string,
    userTier: TierLevel,
    sessionId: string,
    scopes: string[],
    roles: string[],
    options?: {
      deviceId?: string;
      organizationId?: string;
      ipAddress?: string;
      customClaims?: Record<string, any>;
      ttlOverride?: number;
    }
  ): Promise<{ token: string; expiresIn: number; jti: string }> {
    try {
      const now = Math.floor(Date.now() / 1000);
      const jti = this.generateJTI();
      const ttl = options?.ttlOverride || this.config.accessTokenTTL;
      
      const payload: TokenClaims = {
        sub: userId,
        iss: this.config.issuer,
        aud: this.config.audience,
        exp: now + ttl,
        iat: now,
        jti,
        'lukhas:tier': userTier,
        'lukhas:session_id': sessionId,
        'lukhas:scopes': scopes,
        'lukhas:roles': roles,
        'lukhas:token_type': 'access',
        'lukhas:ip_hash': options?.ipAddress ? this.hashIP(options.ipAddress) : '',
        ...options?.customClaims
      };

      if (options?.deviceId) {
        payload['lukhas:device_id'] = options.deviceId;
      }

      if (options?.organizationId) {
        payload['lukhas:org_id'] = options.organizationId;
      }

      const token = await this.signToken(payload);
      
      return {
        token,
        expiresIn: ttl,
        jti
      };

    } catch (error) {
      throw new Error(`Failed to issue access token: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Issue refresh token with family tracking
   */
  async issueRefreshToken(
    userId: string,
    sessionId: string,
    deviceId: string,
    ipAddress: string,
    familyId?: string
  ): Promise<{ token: string; familyId: string; expiresIn: number }> {
    try {
      const now = Math.floor(Date.now() / 1000);
      const jti = this.generateJTI();
      
      // Create or update refresh token family
      const actualFamilyId = familyId || this.generateRefreshFamilyId();
      let family = this.refreshFamilies.get(actualFamilyId);
      
      if (!family) {
        family = {
          familyId: actualFamilyId,
          userId,
          deviceId,
          createdAt: now,
          lastUsed: now,
          revoked: false,
          tokenCount: 0
        };
      }

      family.lastUsed = now;
      family.tokenCount++;
      this.refreshFamilies.set(actualFamilyId, family);

      const payload: TokenClaims = {
        sub: userId,
        iss: this.config.issuer,
        aud: this.config.audience,
        exp: now + this.config.refreshTokenTTL,
        iat: now,
        jti,
        'lukhas:tier': 'T1', // Refresh tokens don't carry tier info
        'lukhas:session_id': sessionId,
        'lukhas:device_id': deviceId,
        'lukhas:scopes': ['refresh'],
        'lukhas:roles': [],
        'lukhas:refresh_family': actualFamilyId,
        'lukhas:token_type': 'refresh',
        'lukhas:ip_hash': this.hashIP(ipAddress)
      };

      const token = await this.signToken(payload);
      
      return {
        token,
        familyId: actualFamilyId,
        expiresIn: this.config.refreshTokenTTL
      };

    } catch (error) {
      throw new Error(`Failed to issue refresh token: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Issue ID token for OpenID Connect
   */
  async issueIdToken(
    userId: string,
    userTier: TierLevel,
    email: string,
    sessionId: string,
    nonce?: string,
    options?: {
      organizationId?: string;
      customClaims?: Record<string, any>;
    }
  ): Promise<{ token: string; expiresIn: number }> {
    try {
      const now = Math.floor(Date.now() / 1000);
      const jti = this.generateJTI();
      
      const payload: TokenClaims & {
        email: string;
        nonce?: string;
      } = {
        sub: userId,
        iss: this.config.issuer,
        aud: this.config.audience,
        exp: now + this.config.idTokenTTL,
        iat: now,
        jti,
        email,
        'lukhas:tier': userTier,
        'lukhas:session_id': sessionId,
        'lukhas:scopes': ['openid', 'profile', 'email'],
        'lukhas:roles': [],
        'lukhas:token_type': 'id',
        'lukhas:ip_hash': '',
        ...options?.customClaims
      };

      if (nonce) {
        payload.nonce = nonce;
      }

      if (options?.organizationId) {
        payload['lukhas:org_id'] = options.organizationId;
      }

      const token = await this.signToken(payload);
      
      return {
        token,
        expiresIn: this.config.idTokenTTL
      };

    } catch (error) {
      throw new Error(`Failed to issue ID token: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Verify and validate JWT token
   */
  async verifyToken(
    token: string,
    options?: TokenValidationOptions
  ): Promise<TokenValidationResult> {
    try {
      // Parse JWT header to get kid
      const headerMatch = token.match(/^([^.]+)\./);
      if (!headerMatch) {
        return { valid: false, error: 'Invalid token format' };
      }

      const header = JSON.parse(Buffer.from(headerMatch[1], 'base64url').toString());
      const kid = header.kid;

      if (!kid) {
        return { valid: false, error: 'Missing key ID in token header' };
      }

      // Get public key from JWKS
      const jwksKey = this.jwksManager.getKey(kid);
      if (!jwksKey) {
        return { valid: false, error: 'Unknown key ID' };
      }

      // Import public key
      const publicKey = await this.importPublicKeyFromJWKS(jwksKey);

      // Verify token
      const result: JWTVerifyResult = await jwtVerify(token, publicKey, {
        issuer: options?.issuer || this.config.issuer,
        audience: options?.audience || this.config.audience,
        clockTolerance: options?.clockTolerance || this.config.allowedClockSkew
      });

      const payload = result.payload as TokenClaims;

      // Additional validation
      const validation = this.validateTokenClaims(payload, options);
      if (!validation.valid) {
        return validation;
      }

      // Check if token is in a revoked refresh family
      if (payload['lukhas:refresh_family']) {
        const family = this.refreshFamilies.get(payload['lukhas:refresh_family']);
        if (family?.revoked) {
          return {
            valid: false,
            error: 'Token from revoked refresh family',
            payload,
            kid
          };
        }
      }

      return {
        valid: true,
        payload,
        kid,
        metadata: {
          algorithm: result.protectedHeader.alg,
          keyId: kid,
          tokenType: payload['lukhas:token_type']
        }
      };

    } catch (error) {
      if (error instanceof Error) {
        if (error.message.includes('expired')) {
          return {
            valid: false,
            error: 'Token expired',
            expired: true
          };
        }
        return {
          valid: false,
          error: error.message
        };
      }
      return {
        valid: false,
        error: 'Token verification failed'
      };
    }
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(
    refreshToken: string,
    ipAddress: string
  ): Promise<{
    accessToken: string;
    refreshToken: string;
    accessExpiresIn: number;
    refreshExpiresIn: number;
  }> {
    // Verify refresh token
    const validation = await this.verifyToken(refreshToken);
    if (!validation.valid || !validation.payload) {
      throw new Error('Invalid refresh token');
    }

    const payload = validation.payload;

    // Ensure it's a refresh token
    if (payload['lukhas:token_type'] !== 'refresh') {
      throw new Error('Not a refresh token');
    }

    // Check refresh family
    const familyId = payload['lukhas:refresh_family'];
    if (!familyId) {
      throw new Error('Missing refresh family');
    }

    const family = this.refreshFamilies.get(familyId);
    if (!family || family.revoked) {
      // Possible token reuse attack - revoke entire family
      if (family) {
        await this.revokeRefreshFamily(familyId, 'Token reuse detected');
      }
      throw new Error('Refresh family revoked');
    }

    // Verify IP consistency (optional security measure)
    const tokenIPHash = payload['lukhas:ip_hash'];
    const currentIPHash = this.hashIP(ipAddress);
    
    // Note: In production, you might want to allow IP changes for mobile users
    // This is a security vs usability tradeoff
    
    // Get user's current session info (this would come from your user service)
    const userId = payload.sub;
    const sessionId = payload['lukhas:session_id'];
    const deviceId = payload['lukhas:device_id'];

    if (!deviceId) {
      throw new Error('Missing device ID in refresh token');
    }

    // TODO: Fetch user's current tier, scopes, and roles from database
    // For now, we'll use placeholder values
    const userTier: TierLevel = 'T2'; // This should be fetched from user service
    const scopes = ['matriz:read', 'matriz:write', 'api:read']; // Fetch from user service
    const roles = ['developer']; // Fetch from user service

    // Issue new access token
    const accessTokenResult = await this.issueAccessToken(
      userId,
      userTier,
      sessionId,
      scopes,
      roles,
      {
        deviceId,
        ipAddress
      }
    );

    // Issue new refresh token (rotate refresh token)
    const refreshTokenResult = await this.issueRefreshToken(
      userId,
      sessionId,
      deviceId,
      ipAddress,
      familyId
    );

    return {
      accessToken: accessTokenResult.token,
      refreshToken: refreshTokenResult.token,
      accessExpiresIn: accessTokenResult.expiresIn,
      refreshExpiresIn: refreshTokenResult.expiresIn
    };
  }

  /**
   * Revoke refresh token family (for logout or security incidents)
   */
  async revokeRefreshFamily(familyId: string, reason: string): Promise<boolean> {
    const family = this.refreshFamilies.get(familyId);
    if (!family) {
      return false;
    }

    family.revoked = true;
    family.revokedAt = Math.floor(Date.now() / 1000);
    this.refreshFamilies.set(familyId, family);

    // TODO: Log security event
    console.log(`Refresh family ${familyId} revoked: ${reason}`);

    return true;
  }

  /**
   * Get refresh family info
   */
  getRefreshFamily(familyId: string): RefreshTokenFamily | undefined {
    return this.refreshFamilies.get(familyId);
  }

  /**
   * Clean up expired refresh families
   */
  cleanupExpiredFamilies(): number {
    const now = Math.floor(Date.now() / 1000);
    let cleanedCount = 0;

    for (const [familyId, family] of this.refreshFamilies.entries()) {
      // Remove families older than max refresh age
      if (now - family.createdAt > this.config.maxRefreshAge) {
        this.refreshFamilies.delete(familyId);
        cleanedCount++;
      }
    }

    return cleanedCount;
  }

  /**
   * Sign JWT token using current active key
   */
  private async signToken(payload: TokenClaims): Promise<string> {
    // Get current JWKS configuration
    const jwks = this.jwksManager.getJWKS();
    const activeKey = jwks.keys[0]; // Use first active key

    if (!activeKey) {
      throw new Error('No active signing key available');
    }

    // TODO: This requires the private key, which should be injected securely
    // For now, we'll throw an error indicating this needs to be implemented
    throw new Error('Private key integration needed for JWT signing');
    
    // Implementation would look like:
    // const privateKey = await this.getPrivateKey(activeKey.kid);
    // const jwt = await new SignJWT(payload)
    //   .setProtectedHeader({ alg: 'RS256', kid: activeKey.kid })
    //   .sign(privateKey);
    // return jwt;
  }

  /**
   * Import public key from JWKS key
   */
  private async importPublicKeyFromJWKS(jwksKey: JWKSKey): Promise<CryptoKey> {
    const jwk = {
      kty: jwksKey.kty,
      use: jwksKey.use,
      alg: jwksKey.alg,
      n: jwksKey.n,
      e: jwksKey.e
    };

    return await importSPKI(this.jwkToPem(jwk), 'RS256');
  }

  /**
   * Convert JWK to PEM format
   */
  private jwkToPem(jwk: any): string {
    // This is a simplified implementation
    // In production, use a proper JWK to PEM conversion library
    throw new Error('JWK to PEM conversion needs implementation');
  }

  /**
   * Validate token claims
   */
  private validateTokenClaims(
    payload: TokenClaims,
    options?: TokenValidationOptions
  ): TokenValidationResult {
    // Check required ΛiD claims
    const requiredClaims = [
      'lukhas:tier',
      'lukhas:session_id',
      'lukhas:scopes',
      'lukhas:roles',
      'lukhas:token_type'
    ];

    for (const claim of requiredClaims) {
      if (!(claim in payload)) {
        return {
          valid: false,
          error: `Missing required claim: ${claim}`
        };
      }
    }

    // Validate token type
    const tokenType = payload['lukhas:token_type'];
    if (!['access', 'refresh', 'id'].includes(tokenType)) {
      return {
        valid: false,
        error: `Invalid token type: ${tokenType}`
      };
    }

    // Check maximum token age if specified
    if (options?.maxTokenAge) {
      const age = Math.floor(Date.now() / 1000) - payload.iat;
      if (age > options.maxTokenAge) {
        return {
          valid: false,
          error: 'Token exceeds maximum age'
        };
      }
    }

    // Additional custom claim validation
    if (options?.requiredClaims) {
      for (const claim of options.requiredClaims) {
        if (!(claim in payload)) {
          return {
            valid: false,
            error: `Missing required custom claim: ${claim}`
          };
        }
      }
    }

    return { valid: true };
  }

  /**
   * Generate unique JWT ID
   */
  private generateJTI(): string {
    const timestamp = Date.now().toString(36);
    const random = randomBytes(8).toString('hex');
    return `${timestamp}-${random}`;
  }

  /**
   * Generate refresh token family ID
   */
  private generateRefreshFamilyId(): string {
    const timestamp = Date.now().toString(36);
    const random = randomBytes(12).toString('hex');
    return `rf_${timestamp}_${random}`;
  }

  /**
   * Hash IP address for privacy
   */
  private hashIP(ip: string): string {
    return createHash('sha256').update(ip).digest('hex').slice(0, 16);
  }
}

/**
 * JWT utilities
 */
export class JWTUtils {
  /**
   * Decode JWT payload without verification (for debugging)
   */
  static decodePayload(token: string): any {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid JWT format');
      }
      
      const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString());
      return payload;
    } catch (error) {
      throw new Error('Failed to decode JWT payload');
    }
  }

  /**
   * Check if token is expired without verification
   */
  static isExpired(token: string): boolean {
    try {
      const payload = this.decodePayload(token);
      const now = Math.floor(Date.now() / 1000);
      return payload.exp && payload.exp < now;
    } catch {
      return true;
    }
  }

  /**
   * Get token expiry time
   */
  static getExpiryTime(token: string): number | null {
    try {
      const payload = this.decodePayload(token);
      return payload.exp || null;
    } catch {
      return null;
    }
  }

  /**
   * Extract token type
   */
  static getTokenType(token: string): string | null {
    try {
      const payload = this.decodePayload(token);
      return payload['lukhas:token_type'] || null;
    } catch {
      return null;
    }
  }
}

/**
 * Default token configuration
 */
export const DEFAULT_TOKEN_CONFIG: TokenConfig = {
  issuer: 'https://auth.lukhas.ai',
  audience: 'https://api.lukhas.ai',
  accessTokenTTL: 15 * 60,        // 15 minutes
  refreshTokenTTL: 30 * 24 * 60 * 60, // 30 days
  idTokenTTL: 60 * 60,            // 1 hour
  maxRefreshAge: 90 * 24 * 60 * 60,   // 90 days
  allowedClockSkew: 30            // 30 seconds
};

export default JWTManager;