import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ok, badRequest, softError, unauthorized, notFound } from '@/packages/api/respond';
import { hmacSHA256, generateSecureToken } from '@/packages/util/hash';
import { buildAlias } from '@/packages/identity/lid-alias';
import { randomUUID } from 'crypto';
import { verifyJWT } from '@/packages/auth/jwt';
import { hasExtendedScope } from '@/packages/identity/scopes';
import { z } from 'zod';

// Validation schema for rotation request
const RotateAliasSchema = z.object({
  currentAlias: z.string().min(1, 'Current alias required'),
  justification: z.string().min(10, 'Justification must be at least 10 characters').max(500, 'Justification too long'),
  emergencyRotation: z.boolean().optional().default(false)
});

type RotateAliasRequest = z.infer<typeof RotateAliasSchema>;

const PEPPER = process.env.SECRET_PEPPER || 'CHANGE_ME_DEV';
const ALIAS_VERSION_INCREMENT = 1;

// Get current user context from JWT token
async function getCurrentUserContext(req: NextRequest): Promise<{
  userId: string;
  tier: string;
  scopes: string[];
} | null> {
  const token = req.cookies.get('auth-token')?.value;
  if (!token) return null;
  
  try {
    const payload = await verifyJWT(token);
    if (!payload?.sub) return null;
    
    return {
      userId: payload.sub,
      tier: payload.tier || 'T1',
      scopes: payload.scope?.split(' ') || []
    };
  } catch {
    return null;
  }
}

// Parse alias to extract components
function parseAlias(alias: string): {
  realm: string;
  zone: string;
  token: string;
  version: number;
} | null {
  // Expected format: lid#REALM/ZONE/vN.token-checksum
  const match = alias.match(/^lid#([A-Z]+)\/([A-Z]+)\/v(\d+)\.(.+)$/);
  if (!match) return null;
  
  const [, realm, zone, versionStr, token] = match;
  return {
    realm,
    zone,
    token,
    version: parseInt(versionStr, 10)
  };
}

// Check if user can rotate alias (rate limiting, cooldown)
async function canRotateAlias(userId: string, emergencyRotation: boolean): Promise<{
  allowed: boolean;
  reason?: string;
  nextAllowedAt?: Date;
}> {
  const now = new Date();
  const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  
  // Check recent rotations
  const recentRotations = await prisma.aliasRotationHistory.count({
    where: {
      userId,
      rotatedAt: {
        gte: oneDayAgo
      }
    }
  });
  
  // Allow more rotations for emergency cases
  const maxDailyRotations = emergencyRotation ? 5 : 3;
  
  if (recentRotations >= maxDailyRotations) {
    const nextAllowed = new Date(now.getTime() + 24 * 60 * 60 * 1000);
    return {
      allowed: false,
      reason: `Daily rotation limit exceeded (${maxDailyRotations}). Try again tomorrow.`,
      nextAllowedAt: nextAllowed
    };
  }
  
  return { allowed: true };
}

// Generate new version of alias
async function generateRotatedAlias(
  currentAlias: string,
  userId: string
): Promise<{
  newAlias: string;
  newVersion: number;
  realm: string;
  zone: string;
} | null> {
  const parsed = parseAlias(currentAlias);
  if (!parsed) return null;
  
  const newVersion = parsed.version + ALIAS_VERSION_INCREMENT;
  const newToken = generateSecureToken(16); // Generate new secure token
  
  // Build new alias with incremented version
  const newAliasResult = await buildAlias({
    realm: parsed.realm,
    zone: parsed.zone,
    identifier: userId, // Use userId as stable identifier
    idType: 'uuid',
    version: newVersion,
    customToken: newToken
  });
  
  return {
    newAlias: newAliasResult.aliasDisplay,
    newVersion,
    realm: parsed.realm,
    zone: parsed.zone
  };
}

// Log rotation event for audit
async function logRotationEvent(
  userId: string,
  oldAlias: string,
  newAlias: string,
  justification: string,
  req: NextRequest,
  emergencyRotation: boolean = false
): Promise<void> {
  const ipAddress = req.headers.get('x-forwarded-for') || 
                    req.headers.get('x-real-ip') || 
                    req.ip || 'unknown';
  const userAgent = req.headers.get('user-agent') || 'unknown';
  
  await prisma.aliasRotationHistory.create({
    data: {
      id: randomUUID(),
      userId,
      oldAlias,
      newAlias,
      justification,
      emergencyRotation,
      ipAddress,
      userAgent,
      rotatedAt: new Date(),
      metadata: {
        timestamp: new Date().toISOString(),
        source: 'api_rotation',
        requestId: randomUUID()
      }
    }
  });
  
  // Log to audit system
  console.log('[ALIAS ROTATION AUDIT]', JSON.stringify({
    event: 'alias_rotated',
    userId,
    oldAlias,
    newAlias,
    justification,
    emergencyRotation,
    ipAddress,
    userAgent,
    timestamp: new Date().toISOString()
  }));
}

/**
 * POST /api/alias/rotate
 * 
 * Rotates a user's ΛiD alias to a new version
 * 
 * Body:
 * {
 *   "currentAlias": "lid#LUKHAS/EU/v1.abc123-4def",
 *   "justification": "Security concern - potential compromise",
 *   "emergencyRotation": false
 * }
 * 
 * Response:
 * {
 *   "success": true,
 *   "data": {
 *     "newAlias": "lid#LUKHAS/EU/v2.xyz789-1abc",
 *     "oldAlias": "lid#LUKHAS/EU/v1.abc123-4def",
 *     "version": 2,
 *     "expiresAt": "2025-08-24T10:30:00Z",
 *     "gracePeriod": "24h"
 *   }
 * }
 */
export async function POST(req: NextRequest) {
  try {
    // Parse and validate request body
    const body = await req.json().catch(() => null);
    const parsed = RotateAliasSchema.safeParse(body);
    if (!parsed.success) {
      return badRequest('Invalid request body', {
        errors: parsed.error.errors.map(e => ({
          field: e.path.join('.'),
          message: e.message
        }))
      });
    }
    
    const { currentAlias, justification, emergencyRotation } = parsed.data;
    
    // Get user context
    const userContext = await getCurrentUserContext(req);
    if (!userContext) {
      return unauthorized('Authentication required');
    }
    
    const { userId, tier, scopes } = userContext;
    
    // Check authorization for alias rotation
    const authResult = hasExtendedScope(
      tier as any,
      scopes as any,
      'identity:write',
      {
        module: 'identity',
        action: 'rotate_alias',
        conditions: {
          emergency: emergencyRotation,
          sensitive_operation: true
        }
      }
    );
    
    if (!authResult.allowed) {
      return unauthorized(`Insufficient permissions: ${authResult.reason}`);
    }
    
    // Verify user owns the current alias
    const existingAlias = await prisma.lidAlias.findFirst({
      where: {
        aliasDisplay: currentAlias,
        userId: userId,
        active: true
      }
    });
    
    if (!existingAlias) {
      return notFound('Alias not found or not owned by user');
    }
    
    // Check rotation eligibility
    const rotationCheck = await canRotateAlias(userId, emergencyRotation);
    if (!rotationCheck.allowed) {
      return badRequest('Rotation not allowed', {
        reason: rotationCheck.reason,
        nextAllowedAt: rotationCheck.nextAllowedAt?.toISOString()
      });
    }
    
    // Generate new alias
    const rotationResult = await generateRotatedAlias(currentAlias, userId);
    if (!rotationResult) {
      return badRequest('Failed to generate new alias - invalid current alias format');
    }
    
    const { newAlias, newVersion, realm, zone } = rotationResult;
    
    // Calculate expiry for old alias (24h grace period)
    const gracePeriodEnd = new Date(Date.now() + 24 * 60 * 60 * 1000);
    
    // Database transaction to update aliases
    await prisma.$transaction(async (tx) => {
      // Mark old alias as inactive (but keep for grace period)
      await tx.lidAlias.update({
        where: { id: existingAlias.id },
        data: {
          active: false,
          rotatedAt: new Date(),
          expiresAt: gracePeriodEnd
        }
      });
      
      // Create new alias
      await tx.lidAlias.create({
        data: {
          id: randomUUID(),
          userId,
          aliasKey: newAlias.replace('lid#', '').toLowerCase(),
          aliasDisplay: newAlias,
          realm,
          zone,
          idType: 'uuid',
          version: newVersion,
          active: true,
          verifiedAt: new Date(),
          createdAt: new Date()
        }
      });
    });
    
    // Log the rotation event
    await logRotationEvent(
      userId,
      currentAlias,
      newAlias,
      justification,
      req,
      emergencyRotation
    );
    
    // Return success response
    return ok({
      newAlias,
      oldAlias: currentAlias,
      version: newVersion,
      expiresAt: gracePeriodEnd.toISOString(),
      gracePeriod: '24h',
      metadata: {
        rotatedAt: new Date().toISOString(),
        emergencyRotation,
        justification
      }
    });
    
  } catch (error) {
    console.error('[ALIAS ROTATION ERROR]', error);
    return softError('Internal server error during alias rotation');
  }
}

/**
 * GET /api/alias/rotate
 * 
 * Get rotation history and eligibility status
 * 
 * Response:
 * {
 *   "success": true,
 *   "data": {
 *     "canRotate": true,
 *     "remainingRotations": 2,
 *     "nextAllowedAt": null,
 *     "recentRotations": [...],
 *     "currentAlias": "lid#LUKHAS/EU/v2.xyz789-1abc"
 *   }
 * }
 */
export async function GET(req: NextRequest) {
  try {
    // Get user context
    const userContext = await getCurrentUserContext(req);
    if (!userContext) {
      return unauthorized('Authentication required');
    }
    
    const { userId } = userContext;
    
    // Get current active alias
    const currentAlias = await prisma.lidAlias.findFirst({
      where: {
        userId,
        active: true
      },
      orderBy: {
        version: 'desc'
      }
    });
    
    // Check rotation eligibility
    const rotationCheck = await canRotateAlias(userId, false);
    
    // Get recent rotation history
    const recentRotations = await prisma.aliasRotationHistory.findMany({
      where: { userId },
      orderBy: { rotatedAt: 'desc' },
      take: 10,
      select: {
        oldAlias: true,
        newAlias: true,
        rotatedAt: true,
        justification: true,
        emergencyRotation: true
      }
    });
    
    const now = new Date();
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const todaysRotations = await prisma.aliasRotationHistory.count({
      where: {
        userId,
        rotatedAt: { gte: oneDayAgo }
      }
    });
    
    return ok({
      canRotate: rotationCheck.allowed,
      remainingRotations: Math.max(0, 3 - todaysRotations),
      nextAllowedAt: rotationCheck.nextAllowedAt?.toISOString() || null,
      recentRotations,
      currentAlias: currentAlias?.aliasDisplay || null,
      metadata: {
        timestamp: new Date().toISOString(),
        dailyLimit: 3,
        emergencyLimit: 5
      }
    });
    
  } catch (error) {
    console.error('[ALIAS ROTATION STATUS ERROR]', error);
    return softError('Internal server error retrieving rotation status');
  }
}