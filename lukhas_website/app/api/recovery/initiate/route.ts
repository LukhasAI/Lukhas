import { NextRequest } from 'next/server';
import { RecoveryInit } from '@/packages/api/schemas';
import { ok, badRequest } from '@/packages/api/respond';
import { prisma } from '@/lib/prisma';
import { randomUUID } from 'crypto';
import { verifyJWT } from '@/packages/auth/jwt';
import { getRequiredGuardianApprovals, notifyGuardian } from '@/packages/auth/guardian-helpers';

// Get current user from JWT token (may be partially authenticated)
async function getCurrentUserId(req: NextRequest): Promise<string|null> {
  const token = req.cookies.get('auth-token')?.value || req.cookies.get('recovery-token')?.value;
  if (!token) return null;

  try {
    const payload = await verifyJWT(token);
    return payload?.sub || null;
  } catch {
    return null;
  }
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(()=>null);
  const parsed = RecoveryInit.safeParse(body);
  if (!parsed.success) return badRequest('Invalid payload');

  const userId = await getCurrentUserId(req);
  if (!userId) {
    // Could implement identifier-based recovery here
    return badRequest('User context required for recovery');
  }

  const requiredApprovals = await getRequiredGuardianApprovals(userId);

  const ticketId = randomUUID();
  await prisma.recoveryTicket.create({
    data: {
      id: ticketId,
      userId,
      state: 'open',
      requiredApprovals,
      approvalsCount: 0,
      reason: parsed.data.reason,
      expiresAt: new Date(Date.now() + 24*60*60*1000),
      meta: {}
    }
  });

  // Send notifications to guardians
  const guardians = await prisma.guardian.findMany({
    where: { userId, revokedAt: null },
    select: { id: true }
  });

  for (const guardian of guardians) {
    await notifyGuardian(guardian.id, ticketId, parsed.data.reason || 'Account recovery requested');
  }

  // Get user's identifiers for additional notifications
  const identifiers = await prisma.verifiedIdentifier.findMany({
    where: { userId },
    select: { type: true, valueNorm: true }
  });

  // Log notification attempts (in production, send actual notifications)
  console.log(`[Recovery] Ticket ${ticketId} created for user ${userId}`);
  console.log(`[Recovery] Notified ${guardians.length} guardians`);

  for (const id of identifiers) {
    console.log(`[Recovery] Notification queued for ${id.type}: ${id.valueNorm}`);
  }

  return ok({ ticketId });
}
