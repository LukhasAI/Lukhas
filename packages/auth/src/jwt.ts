/**
 * ΛiD Authentication System - JWT Management
 * 
 * RS256 JWT issue/verify with JWKS support and key rotation
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

import { 
  JWTPayload, 
  JWTHeader, 
  JWKSResponse, 
  TokenPair, 
  TokenVerificationResult,
  JWTOptions,
  RefreshTokenData
} from '../types/auth.types';
import { UserTier, AuthScope } from '../types/auth.types';

/**
 * JWT Configuration
 */
export interface JWTConfig {
  issuer: string;
  audience: string;
  accessTokenTTL: number;   // seconds
  refreshTokenTTL: number;  // seconds
  keyRotationInterval: number; // seconds
  jwksEndpoint: string;
  algorithm: 'RS256';
}

/**
 * Default JWT configuration for LUKHAS
 */
export const DEFAULT_JWT_CONFIG: JWTConfig = {
  issuer: 'https://auth.lukhas.ai',
  audience: 'https://api.lukhas.ai',
  accessTokenTTL: 900,      // 15 minutes
  refreshTokenTTL: 2592000, // 30 days
  keyRotationInterval: 86400, // 24 hours
  jwksEndpoint: 'https://auth.lukhas.ai/.well-known/jwks.json',
  algorithm: 'RS256'
};

/**
 * Key pair for JWT signing
 */
interface KeyPair {
  kid: string;
  publicKey: string;
  privateKey: string;
  createdAt: number;
  expiresAt: number;
  algorithm: 'RS256';
}

/**
 * JWKS (JSON Web Key Set) key
 */
interface JWK {
  kty: 'RSA';
  use: 'sig';
  kid: string;
  alg: 'RS256';
  n: string; // modulus
  e: string; // exponent
}

/**
 * Key store for managing signing keys
 */
class KeyStore {
  private keys: Map<string, KeyPair> = new Map();
  private activeKeyId: string | null = null;
  private config: JWTConfig;

  constructor(config: JWTConfig) {
    this.config = config;
  }

  /**
   * Generate a new RSA key pair
   */
  async generateKeyPair(): Promise<KeyPair> {
    // In a real implementation, use Node.js crypto or Web Crypto API
    const kid = `key_${Date.now()}_${Math.random().toString(36).substring(2)}`;
    const now = Date.now();
    
    // Placeholder for actual key generation
    const keyPair: KeyPair = {
      kid,
      publicKey: `-----BEGIN PUBLIC KEY-----\n${this.generateMockKey('public')}\n-----END PUBLIC KEY-----`,
      privateKey: `-----BEGIN PRIVATE KEY-----\n${this.generateMockKey('private')}\n-----END PRIVATE KEY-----`,
      createdAt: now,
      expiresAt: now + (this.config.keyRotationInterval * 1000),
      algorithm: 'RS256'
    };

    this.keys.set(kid, keyPair);
    
    if (!this.activeKeyId) {
      this.activeKeyId = kid;
    }

    return keyPair;
  }

  /**
   * Get active signing key
   */
  getActiveKey(): KeyPair | null {
    if (!this.activeKeyId) return null;
    return this.keys.get(this.activeKeyId) || null;
  }

  /**
   * Get key by ID
   */
  getKey(kid: string): KeyPair | null {
    return this.keys.get(kid) || null;
  }

  /**
   * Get all public keys for JWKS
   */
  getPublicKeys(): JWK[] {
    return Array.from(this.keys.values()).map(key => ({
      kty: 'RSA',
      use: 'sig',
      kid: key.kid,
      alg: 'RS256',
      n: this.extractModulus(key.publicKey),
      e: 'AQAB' // Standard RSA exponent
    }));
  }

  /**
   * Rotate keys if necessary
   */
  rotateKeysIfNeeded(): boolean {
    const activeKey = this.getActiveKey();
    if (!activeKey) return false;

    const now = Date.now();
    if (now >= activeKey.expiresAt) {
      // Generate new key
      this.generateKeyPair();
      return true;
    }

    return false;
  }

  /**
   * Cleanup expired keys (keep them for verification but not signing)
   */
  cleanupExpiredKeys(): void {
    const now = Date.now();
    const cutoff = now - (7 * 24 * 60 * 60 * 1000); // Keep for 7 days
    
    for (const [kid, key] of this.keys.entries()) {
      if (key.expiresAt < cutoff) {
        this.keys.delete(kid);
      }
    }
  }

  // Helper methods
  private generateMockKey(type: 'public' | 'private'): string {
    // In production, this would generate actual RSA keys
    const length = type === 'private' ? 1024 : 512;
    return Array(length).fill(0).map(() => 
      Math.random().toString(36).charAt(Math.floor(Math.random() * 36))
    ).join('');
  }

  private extractModulus(publicKey: string): string {
    // In production, extract actual modulus from RSA public key
    return Buffer.from(publicKey.replace(/-----[^-]+-----/g, ''), 'base64')
      .toString('base64url');
  }
}

/**
 * JWT Manager class
 */
export class JWTManager {
  private keyStore: KeyStore;
  private config: JWTConfig;

  constructor(config: JWTConfig = DEFAULT_JWT_CONFIG) {
    this.config = config;
    this.keyStore = new KeyStore(config);
    
    // Initialize with a key pair
    this.keyStore.generateKeyPair();
    
    // Setup key rotation
    setInterval(() => {
      this.keyStore.rotateKeysIfNeeded();
      this.keyStore.cleanupExpiredKeys();
    }, 60000); // Check every minute
  }

  /**
   * Generate access token
   */
  async generateAccessToken(
    userId: string,
    userTier: UserTier,
    scopes: AuthScope[],
    options?: Partial<JWTOptions>
  ): Promise<string> {
    const key = this.keyStore.getActiveKey();
    if (!key) {
      throw new Error('No active signing key available');
    }

    const now = Math.floor(Date.now() / 1000);
    const exp = now + (options?.ttl || this.config.accessTokenTTL);

    const header: JWTHeader = {
      alg: 'RS256',
      typ: 'JWT',
      kid: key.kid
    };

    const payload: JWTPayload = {
      iss: this.config.issuer,
      aud: this.config.audience,
      sub: userId,
      iat: now,
      exp,
      jti: this.generateJTI(),
      scope: scopes.join(' '),
      tier: userTier,
      type: 'access',
      metadata: options?.metadata || {}
    };

    return this.signToken(header, payload, key.privateKey);
  }

  /**
   * Generate refresh token
   */
  async generateRefreshToken(
    userId: string,
    userTier: UserTier,
    deviceHandle: string,
    familyId: string,
    options?: Partial<JWTOptions>
  ): Promise<string> {
    const key = this.keyStore.getActiveKey();
    if (!key) {
      throw new Error('No active signing key available');
    }

    const now = Math.floor(Date.now() / 1000);
    const exp = now + (options?.ttl || this.config.refreshTokenTTL);

    const header: JWTHeader = {
      alg: 'RS256',
      typ: 'JWT',
      kid: key.kid
    };

    const payload: JWTPayload = {
      iss: this.config.issuer,
      aud: this.config.audience,
      sub: userId,
      iat: now,
      exp,
      jti: this.generateJTI(),
      type: 'refresh',
      tier: userTier,
      device: deviceHandle,
      family: familyId,
      metadata: options?.metadata || {}
    };

    return this.signToken(header, payload, key.privateKey);
  }

  /**
   * Generate token pair (access + refresh)
   */
  async generateTokenPair(
    userId: string,
    userTier: UserTier,
    scopes: AuthScope[],
    deviceHandle: string,
    familyId: string,
    options?: Partial<JWTOptions>
  ): Promise<TokenPair> {
    const [accessToken, refreshToken] = await Promise.all([
      this.generateAccessToken(userId, userTier, scopes, options),
      this.generateRefreshToken(userId, userTier, deviceHandle, familyId, options)
    ]);

    return {
      accessToken,
      refreshToken,
      tokenType: 'Bearer',
      expiresIn: options?.ttl || this.config.accessTokenTTL,
      scope: scopes.join(' ')
    };
  }

  /**
   * Verify JWT token
   */
  async verifyToken(token: string): Promise<TokenVerificationResult> {
    try {
      const [headerB64, payloadB64, signatureB64] = token.split('.');
      
      if (!headerB64 || !payloadB64 || !signatureB64) {
        return {
          valid: false,
          reason: 'Invalid token format'
        };
      }

      // Decode header and payload
      const header = JSON.parse(this.base64UrlDecode(headerB64)) as JWTHeader;
      const payload = JSON.parse(this.base64UrlDecode(payloadB64)) as JWTPayload;

      // Validate header
      if (header.alg !== 'RS256' || header.typ !== 'JWT') {
        return {
          valid: false,
          reason: 'Invalid token header'
        };
      }

      // Get signing key
      const key = this.keyStore.getKey(header.kid);
      if (!key) {
        return {
          valid: false,
          reason: 'Unknown signing key'
        };
      }

      // Verify signature
      const isValidSignature = await this.verifySignature(
        `${headerB64}.${payloadB64}`,
        signatureB64,
        key.publicKey
      );

      if (!isValidSignature) {
        return {
          valid: false,
          reason: 'Invalid signature'
        };
      }

      // Validate claims
      const now = Math.floor(Date.now() / 1000);
      
      if (payload.exp && now >= payload.exp) {
        return {
          valid: false,
          reason: 'Token expired',
          payload
        };
      }

      if (payload.iat && now < payload.iat - 60) { // Allow 60s clock skew
        return {
          valid: false,
          reason: 'Token used before valid',
          payload
        };
      }

      if (payload.iss !== this.config.issuer) {
        return {
          valid: false,
          reason: 'Invalid issuer',
          payload
        };
      }

      if (payload.aud !== this.config.audience) {
        return {
          valid: false,
          reason: 'Invalid audience',
          payload
        };
      }

      // Token is valid
      return {
        valid: true,
        payload,
        header
      };

    } catch (error) {
      return {
        valid: false,
        reason: `Token verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Get JWKS (JSON Web Key Set)
   */
  async getJWKS(): Promise<JWKSResponse> {
    return {
      keys: this.keyStore.getPublicKeys()
    };
  }

  /**
   * Revoke token (add to blacklist)
   */
  async revokeToken(jti: string): Promise<void> {
    // In production, add to distributed blacklist (Redis, etc.)
    console.log(`[ΛiD JWT] Token revoked: ${jti}`);
  }

  /**
   * Check if token is revoked
   */
  async isTokenRevoked(jti: string): Promise<boolean> {
    // In production, check distributed blacklist
    return false;
  }

  /**
   * Extract claims from token without verification (for debugging)
   */
  extractClaims(token: string): { header: JWTHeader; payload: JWTPayload } | null {
    try {
      const [headerB64, payloadB64] = token.split('.');
      
      const header = JSON.parse(this.base64UrlDecode(headerB64)) as JWTHeader;
      const payload = JSON.parse(this.base64UrlDecode(payloadB64)) as JWTPayload;

      return { header, payload };
    } catch {
      return null;
    }
  }

  // Private helper methods

  private async signToken(header: JWTHeader, payload: JWTPayload, privateKey: string): Promise<string> {
    const headerB64 = this.base64UrlEncode(JSON.stringify(header));
    const payloadB64 = this.base64UrlEncode(JSON.stringify(payload));
    const message = `${headerB64}.${payloadB64}`;
    
    // In production, use actual crypto signing
    const signature = await this.signMessage(message, privateKey);
    const signatureB64 = this.base64UrlEncode(signature);
    
    return `${message}.${signatureB64}`;
  }

  private async signMessage(message: string, privateKey: string): Promise<string> {
    // Placeholder for actual RS256 signing
    // In production, use crypto.sign() or similar
    return `signature_${message.length}_${Date.now()}`;
  }

  private async verifySignature(message: string, signature: string, publicKey: string): Promise<boolean> {
    // Placeholder for actual signature verification
    // In production, use crypto.verify() or similar
    const expectedSignature = `signature_${message.length}_`;
    return signature.startsWith(expectedSignature);
  }

  private base64UrlEncode(str: string): string {
    return Buffer.from(str)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  }

  private base64UrlDecode(str: string): string {
    str = str.replace(/-/g, '+').replace(/_/g, '/');
    while (str.length % 4) {
      str += '=';
    }
    return Buffer.from(str, 'base64').toString();
  }

  private generateJTI(): string {
    return `jti_${Date.now()}_${Math.random().toString(36).substring(2)}`;
  }
}

/**
 * Global JWT manager instance
 */
export const jwtManager = new JWTManager();

/**
 * Convenience functions for common operations
 */

/**
 * Generate access token
 */
export async function generateAccessToken(
  userId: string,
  userTier: UserTier,
  scopes: AuthScope[],
  options?: Partial<JWTOptions>
): Promise<string> {
  return jwtManager.generateAccessToken(userId, userTier, scopes, options);
}

/**
 * Generate refresh token
 */
export async function generateRefreshToken(
  userId: string,
  userTier: UserTier,
  deviceHandle: string,
  familyId: string,
  options?: Partial<JWTOptions>
): Promise<string> {
  return jwtManager.generateRefreshToken(userId, userTier, deviceHandle, familyId, options);
}

/**
 * Generate token pair
 */
export async function generateTokenPair(
  userId: string,
  userTier: UserTier,
  scopes: AuthScope[],
  deviceHandle: string,
  familyId: string,
  options?: Partial<JWTOptions>
): Promise<TokenPair> {
  return jwtManager.generateTokenPair(userId, userTier, scopes, deviceHandle, familyId, options);
}

/**
 * Verify token
 */
export async function verifyToken(token: string): Promise<TokenVerificationResult> {
  const result = await jwtManager.verifyToken(token);
  
  // Check if token is revoked
  if (result.valid && result.payload?.jti) {
    const isRevoked = await jwtManager.isTokenRevoked(result.payload.jti);
    if (isRevoked) {
      return {
        valid: false,
        reason: 'Token has been revoked',
        payload: result.payload
      };
    }
  }
  
  return result;
}

/**
 * Get JWKS endpoint
 */
export async function getJWKS(): Promise<JWKSResponse> {
  return jwtManager.getJWKS();
}

/**
 * Revoke token
 */
export async function revokeToken(jti: string): Promise<void> {
  return jwtManager.revokeToken(jti);
}

/**
 * Fetch JWKS from external endpoint
 */
export async function fetchJWKS(endpoint: string): Promise<JWKSResponse> {
  try {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error(`JWKS fetch failed: ${response.status}`);
    }
    
    return await response.json() as JWKSResponse;
  } catch (error) {
    throw new Error(`Failed to fetch JWKS: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * JWT middleware for request validation
 */
export function jwtMiddleware(
  extractToken: (request: any) => string | null,
  onVerificationFailed: (reason: string) => void
) {
  return async (request: any, response: any, next: () => void) => {
    try {
      const token = extractToken(request);
      
      if (!token) {
        onVerificationFailed('No token provided');
        return;
      }

      const result = await verifyToken(token);
      
      if (!result.valid) {
        onVerificationFailed(result.reason || 'Token verification failed');
        return;
      }

      // Attach token payload to request
      request.auth = result.payload;
      request.tokenHeader = result.header;
      
      next();
    } catch (error) {
      onVerificationFailed(`JWT middleware error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };
}

/**
 * Token refresh utility
 */
export async function refreshTokens(
  refreshToken: string,
  validateRefreshToken: (payload: JWTPayload) => Promise<boolean>
): Promise<TokenPair | null> {
  try {
    const result = await verifyToken(refreshToken);
    
    if (!result.valid || !result.payload) {
      return null;
    }

    if (result.payload.type !== 'refresh') {
      return null;
    }

    // Validate refresh token in database
    const isValid = await validateRefreshToken(result.payload);
    if (!isValid) {
      return null;
    }

    // Generate new token pair
    const scopes = result.payload.scope ? result.payload.scope.split(' ') as AuthScope[] : [];
    
    return generateTokenPair(
      result.payload.sub,
      result.payload.tier,
      scopes,
      result.payload.device || 'unknown',
      result.payload.family || 'unknown'
    );

  } catch (error) {
    console.error('Token refresh failed:', error);
    return null;
  }
}