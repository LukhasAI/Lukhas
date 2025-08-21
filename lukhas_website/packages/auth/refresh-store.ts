import { PrismaClient } from '@prisma/client';
import { randomUUID } from 'crypto';

const prisma = new PrismaClient();

export async function createFamily(userId: string) {
  const fam = await prisma.refreshTokenFamily.create({ 
    data: { userId } 
  });
  return fam.id;
}

export async function issueRefreshDB(opts: {
  userId: string; 
  deviceId?: string; 
  familyId?: string; 
  ttlDays: number; 
  jti?: string; 
  ip?: string; 
  userAgent?: string;
}) {
  const familyId = opts.familyId ?? await createFamily(opts.userId);
  const jti = opts.jti ?? randomUUID();
  const expiresAt = new Date(Date.now() + opts.ttlDays * 24 * 60 * 60 * 1000);
  
  const token = await prisma.refreshToken.create({
    data: {
      userId: opts.userId,
      familyId,
      jti,
      deviceId: opts.deviceId,
      ip: opts.ip,
      userAgent: opts.userAgent,
      expiresAt,
    }
  });
  return { familyId, jti, tokenId: token.id };
}

export async function markUsed(jti: string) {
  const tok = await prisma.refreshToken.findUnique({ where: { jti } });
  if (!tok) return { ok: false, reason: 'not_found' as const };

  // Check if already used (reuse detection)
  if (tok.usedAt) {
    // Reuse detected: revoke entire family
    await prisma.refreshTokenFamily.update({
      where: { id: tok.familyId },
      data: { revokedAt: new Date(), reason: 'reuse_detected' }
    });
    await prisma.refreshToken.updateMany({
      where: { familyId: tok.familyId, invalidatedAt: null },
      data: { invalidatedAt: new Date(), reused: true }
    });
    return { ok: false, reason: 'reuse_detected' as const, familyId: tok.familyId };
  }

  // Check if expired
  if (new Date() > tok.expiresAt) {
    return { ok: false, reason: 'expired' as const };
  }

  // Mark as used
  await prisma.refreshToken.update({ 
    where: { jti }, 
    data: { usedAt: new Date() } 
  });
  
  return { ok: true, familyId: tok.familyId, userId: tok.userId };
}

export async function isFamilyRevoked(familyId: string) {
  const fam = await prisma.refreshTokenFamily.findUnique({ where: { id: familyId } });
  return Boolean(fam?.revokedAt);
}

export async function revokeFamily(familyId: string, reason: string) {
  await prisma.refreshTokenFamily.update({
    where: { id: familyId },
    data: { revokedAt: new Date(), reason }
  });
  await prisma.refreshToken.updateMany({
    where: { familyId, invalidatedAt: null },
    data: { invalidatedAt: new Date() }
  });
}

export async function rotateRefreshTokenSecure(oldJti: string, deviceId?: string, ip?: string, userAgent?: string) {
  // markUsed handles reuse detection + family revoke
  const result = await markUsed(oldJti);
  if (!result.ok) return { error: result.reason };

  // Issue new refresh in same family
  const { familyId, userId } = result;
  const { jti } = await issueRefreshDB({ 
    userId, 
    deviceId, 
    familyId, 
    ttlDays: parseInt(process.env.AUTH_REFRESH_TTL_DAYS || '30', 10),
    ip,
    userAgent
  });
  
  // Issue new access token
  const { issueAccessToken } = await import('./jwt');
  const access = await issueAccessToken({ sub: userId });

  return { access, refresh: { jti, familyId } };
}

// Cleanup expired tokens (run periodically)
export async function cleanupExpiredTokens() {
  const result = await prisma.refreshToken.deleteMany({
    where: {
      expiresAt: {
        lt: new Date()
      }
    }
  });
  return result.count;
}

// Get active sessions for a user
export async function getUserActiveSessions(userId: string) {
  const tokens = await prisma.refreshToken.findMany({
    where: {
      userId,
      expiresAt: {
        gt: new Date()
      },
      invalidatedAt: null
    },
    select: {
      id: true,
      deviceId: true,
      ip: true,
      userAgent: true,
      issuedAt: true,
      expiresAt: true,
      familyId: true
    }
  });
  
  return tokens;
}

// Revoke all sessions for a user
export async function revokeAllUserSessions(userId: string) {
  const families = await prisma.refreshTokenFamily.findMany({
    where: { userId, revokedAt: null }
  });
  
  for (const family of families) {
    await revokeFamily(family.id, 'user_logout_all');
  }
  
  return families.length;
}