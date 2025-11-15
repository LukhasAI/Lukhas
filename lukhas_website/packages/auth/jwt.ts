import jwt from 'jsonwebtoken';
import { randomUUID } from 'crypto';
import { JWTTokenPersistence } from './jwt-persistence';
import { DatabaseInterface } from './database';

const ACCESS_TTL_MIN = parseInt(process.env.AUTH_ACCESS_TTL_MINUTES || '15', 10);
const REFRESH_TTL_DAYS = parseInt(process.env.AUTH_REFRESH_TTL_DAYS || '30', 10);

const privJwk = JSON.parse(process.env.AUTH_JWT_PRIVATE_JWK || '{}');
const pubSet  = JSON.parse(process.env.AUTH_JWKS_JSON || '[]');

// Token persistence service - initialize with database instance
let tokenPersistence: JWTTokenPersistence | null = null;

export function initializeTokenPersistence(db: DatabaseInterface): void {
  tokenPersistence = new JWTTokenPersistence({
    db,
    maxFamilyAge: 30 * 24 * 60 * 60 * 1000, // 30 days
    enableAutomaticCleanup: true
  });
}

function signRS256(payload: any, ttlSec: number) {
  const kid = privJwk.kid;
  return jwt.sign(payload, privJwk as any, { algorithm: 'RS256', expiresIn: ttlSec, keyid: kid });
}

export async function issueAccessToken(claims: { sub: string; [k: string]: any }) {
  return signRS256({ ...claims, typ: 'access' }, ACCESS_TTL_MIN * 60);
}

export async function issueRefreshToken(params: {
  sub: string;
  deviceId?: string;
  familyId?: string;
  scopes?: string[];
  ipAddress?: string;
  userAgent?: string;
}) {
  const { sub, deviceId, familyId, scopes = [], ipAddress = '127.0.0.1', userAgent } = params;
  const fid = familyId || randomUUID();
  const jti = randomUUID();
  const expiresAt = new Date(Date.now() + REFRESH_TTL_DAYS * 24 * 60 * 60 * 1000);

  // Persist token metadata in database for rotation tracking and reuse detection
  if (tokenPersistence) {
    try {
      await tokenPersistence.persistRefreshToken({
        jti,
        familyId: fid,
        userId: sub,
        deviceId,
        expiresAt,
        scopes,
        ipAddress,
        userAgent
      });
    } catch (error) {
      console.error('[JWT] Failed to persist refresh token:', error);
      // Continue - token can still work without persistence, but rotation won't be tracked
    }
  }

  const token = signRS256({ sub, typ: 'refresh', fid, jti, deviceId }, REFRESH_TTL_DAYS * 24 * 3600);
  return { token, familyId: fid, jti };
}

export async function rotateRefreshToken(params: {
  token: string;
  scopes?: string[];
  ipAddress?: string;
  userAgent?: string;
}) {
  const { token, scopes = [], ipAddress = '127.0.0.1', userAgent } = params;

  try {
    // Verify and decode old token
    const decoded = jwt.verify(token, privJwk as any, { algorithms: ['RS256'] }) as any;

    if (decoded.typ !== 'refresh') {
      return {
        success: false,
        error: 'invalid_token_type',
        shouldRevoke: false
      };
    }

    const { sub, jti: oldJti, fid: familyId, deviceId } = decoded;

    if (!tokenPersistence) {
      // Fallback: issue new token without rotation tracking
      console.warn('[JWT] Token persistence not initialized - rotation not tracked');
      const newJti = randomUUID();
      const expiresAt = new Date(Date.now() + REFRESH_TTL_DAYS * 24 * 60 * 60 * 1000);
      const newToken = signRS256({ sub, typ: 'refresh', fid: familyId, jti: newJti, deviceId }, REFRESH_TTL_DAYS * 24 * 3600);

      return {
        success: true,
        token: newToken,
        familyId,
        jti: newJti
      };
    }

    // Rotate token with reuse detection
    const newJti = randomUUID();
    const expiresAt = new Date(Date.now() + REFRESH_TTL_DAYS * 24 * 60 * 60 * 1000);

    const rotationResult = await tokenPersistence.rotateRefreshToken({
      oldJti,
      newJti,
      userId: sub,
      deviceId,
      expiresAt,
      scopes,
      ipAddress,
      userAgent
    });

    if (!rotationResult.success) {
      return {
        success: false,
        error: rotationResult.error,
        shouldRevoke: rotationResult.reuseDetected || false,
        reuseDetected: rotationResult.reuseDetected
      };
    }

    // Issue new JWT with new jti
    const newToken = signRS256({ sub, typ: 'refresh', fid: familyId, jti: newJti, deviceId }, REFRESH_TTL_DAYS * 24 * 3600);

    return {
      success: true,
      token: newToken,
      familyId,
      jti: newJti
    };
  } catch (error: any) {
    console.error('[JWT] Token rotation failed:', error);
    return {
      success: false,
      error: error.message || 'rotation_failed',
      shouldRevoke: false
    };
  }
}

export async function verifyAccessToken(token: string) {
  try {
    const payload = jwt.verify(token, privJwk as any, { algorithms: ['RS256'] });
    return { valid: true, payload };
  } catch (error) {
    return { valid: false, error };
  }
}
