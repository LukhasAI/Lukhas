/**
 * JWT Token Persistence Service
 *
 * Production-ready implementation for persisting and rotating refresh tokens
 * with family tracking and automatic revocation on reuse detection.
 */

import { createHash } from 'crypto';
import { DatabaseInterface, CreateRefreshTokenInput, RefreshToken, DatabaseResult } from './database';

export interface TokenPersistenceConfig {
  db: DatabaseInterface;
  maxFamilyAge: number; // Maximum age of a token family in milliseconds
  enableAutomaticCleanup: boolean;
}

export interface PersistedTokenMetadata {
  jti: string;
  familyId: string;
  sequence: number;
  deviceId?: string;
  expiresAt: Date;
}

export class JWTTokenPersistence {
  private db: DatabaseInterface;
  private maxFamilyAge: number;
  private cleanupInterval?: NodeJS.Timer;

  constructor(config: TokenPersistenceConfig) {
    this.db = config.db;
    this.maxFamilyAge = config.maxFamilyAge || 30 * 24 * 60 * 60 * 1000; // 30 days default

    if (config.enableAutomaticCleanup) {
      this.startAutomaticCleanup();
    }
  }

  /**
   * Persist refresh token metadata to database
   */
  async persistRefreshToken(params: {
    jti: string;
    familyId: string;
    userId: string;
    deviceId?: string;
    expiresAt: Date;
    scopes: string[];
    ipAddress: string;
    userAgent?: string;
    parentTokenId?: string;
    sequence?: number;
  }): Promise<DatabaseResult<RefreshToken>> {
    const tokenHash = this.hashToken(params.jti);

    const input: CreateRefreshTokenInput = {
      user_id: params.userId,
      device_handle_id: params.deviceId,
      family_id: params.familyId,
      token_hash: tokenHash,
      sequence_number: params.sequence || 1,
      parent_token_id: params.parentTokenId,
      expires_at: params.expiresAt,
      ip_address: params.ipAddress,
      user_agent: params.userAgent,
      scopes: params.scopes,
      metadata: {
        created_via: 'jwt_service',
        jti: params.jti
      }
    };

    return await this.db.createRefreshToken(input);
  }

  /**
   * Verify refresh token and check for reuse
   * Returns token data if valid, null if revoked or expired
   */
  async verifyRefreshToken(jti: string): Promise<{
    valid: boolean;
    token?: RefreshToken;
    reuseDetected?: boolean;
    reason?: string;
  }> {
    const tokenHash = this.hashToken(jti);
    const result = await this.db.getRefreshTokenByHash(tokenHash);

    if (!result.success || !result.data) {
      return {
        valid: false,
        reason: 'token_not_found'
      };
    }

    const token = result.data;

    // Check if token was already used (reuse detection)
    if (token.used_at) {
      // Token reuse detected - revoke entire family
      await this.revokeTokenFamily(token.family_id, 'token_reuse_detected');

      return {
        valid: false,
        token,
        reuseDetected: true,
        reason: 'token_reuse_detected'
      };
    }

    // Check if token is revoked
    if (token.revoked_at) {
      return {
        valid: false,
        token,
        reason: token.revocation_reason || 'token_revoked'
      };
    }

    // Check if token is expired
    if (new Date() > new Date(token.expires_at)) {
      return {
        valid: false,
        token,
        reason: 'token_expired'
      };
    }

    return {
      valid: true,
      token
    };
  }

  /**
   * Mark token as used during rotation
   */
  async markTokenUsed(jti: string): Promise<DatabaseResult<void>> {
    const tokenHash = this.hashToken(jti);
    const result = await this.db.getRefreshTokenByHash(tokenHash);

    if (!result.success || !result.data) {
      return {
        success: false,
        error: 'Token not found'
      };
    }

    await this.db.transaction(async (tx) => {
      // Mark token as used with timestamp
      await tx.execute(
        `UPDATE refresh_tokens
         SET used_at = NOW(), updated_at = NOW()
         WHERE id = $1`,
        [result.data!.id]
      );
    });

    return { success: true };
  }

  /**
   * Rotate refresh token - mark old one as used and create new one
   */
  async rotateRefreshToken(params: {
    oldJti: string;
    newJti: string;
    userId: string;
    deviceId?: string;
    expiresAt: Date;
    scopes: string[];
    ipAddress: string;
    userAgent?: string;
  }): Promise<{
    success: boolean;
    newToken?: RefreshToken;
    error?: string;
    reuseDetected?: boolean;
  }> {
    // Verify old token first
    const verification = await this.verifyRefreshToken(params.oldJti);

    if (!verification.valid) {
      return {
        success: false,
        error: verification.reason || 'invalid_token',
        reuseDetected: verification.reuseDetected
      };
    }

    const oldToken = verification.token!;

    // Mark old token as used
    await this.markTokenUsed(params.oldJti);

    // Create new token in same family
    const newTokenResult = await this.persistRefreshToken({
      jti: params.newJti,
      familyId: oldToken.family_id,
      userId: params.userId,
      deviceId: params.deviceId,
      expiresAt: params.expiresAt,
      scopes: params.scopes,
      ipAddress: params.ipAddress,
      userAgent: params.userAgent,
      parentTokenId: oldToken.id,
      sequence: oldToken.sequence_number + 1
    });

    if (!newTokenResult.success) {
      return {
        success: false,
        error: newTokenResult.error || 'failed_to_create_new_token'
      };
    }

    return {
      success: true,
      newToken: newTokenResult.data
    };
  }

  /**
   * Revoke entire token family (used when reuse is detected)
   */
  async revokeTokenFamily(familyId: string, reason: string): Promise<DatabaseResult<number>> {
    return await this.db.revokeRefreshTokenFamily(familyId, reason);
  }

  /**
   * Revoke specific token
   */
  async revokeToken(jti: string, reason: string): Promise<DatabaseResult<void>> {
    const tokenHash = this.hashToken(jti);
    const result = await this.db.getRefreshTokenByHash(tokenHash);

    if (!result.success || !result.data) {
      return {
        success: false,
        error: 'Token not found'
      };
    }

    await this.db.transaction(async (tx) => {
      await tx.execute(
        `UPDATE refresh_tokens
         SET revoked_at = NOW(),
             revocation_reason = $1,
             updated_at = NOW()
         WHERE id = $2`,
        [reason, result.data!.id]
      );
    });

    return { success: true };
  }

  /**
   * Clean up expired tokens
   */
  async cleanupExpiredTokens(): Promise<DatabaseResult<number>> {
    return await this.db.cleanupExpiredRefreshTokens();
  }

  /**
   * Get token family history for auditing
   */
  async getTokenFamilyHistory(familyId: string): Promise<DatabaseResult<RefreshToken[]>> {
    return await this.db.transaction(async (tx) => {
      const result = await tx.execute<RefreshToken[]>(
        `SELECT * FROM refresh_tokens
         WHERE family_id = $1
         ORDER BY sequence_number ASC`,
        [familyId]
      );
      return result;
    });
  }

  /**
   * Get all active tokens for a user
   */
  async getUserActiveTokens(userId: string): Promise<DatabaseResult<RefreshToken[]>> {
    return await this.db.transaction(async (tx) => {
      const result = await tx.execute<RefreshToken[]>(
        `SELECT * FROM refresh_tokens
         WHERE user_id = $1
           AND revoked_at IS NULL
           AND used_at IS NULL
           AND expires_at > NOW()
         ORDER BY created_at DESC`,
        [userId]
      );
      return result;
    });
  }

  /**
   * Hash token for secure storage
   */
  private hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  /**
   * Start automatic cleanup of expired tokens
   */
  private startAutomaticCleanup(): void {
    // Run cleanup every hour
    this.cleanupInterval = setInterval(async () => {
      try {
        await this.cleanupExpiredTokens();
        console.log('[JWT Persistence] Automatic cleanup completed');
      } catch (error) {
        console.error('[JWT Persistence] Automatic cleanup failed:', error);
      }
    }, 60 * 60 * 1000); // Every hour
  }

  /**
   * Stop automatic cleanup
   */
  stopAutomaticCleanup(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = undefined;
    }
  }

  /**
   * Cleanup resources
   */
  async destroy(): Promise<void> {
    this.stopAutomaticCleanup();
  }
}

export default JWTTokenPersistence;
