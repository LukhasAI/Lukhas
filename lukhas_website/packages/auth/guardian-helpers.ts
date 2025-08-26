import { prisma } from '@/lib/prisma';

/**
 * Check if a user has active guardians
 */
export async function hasActiveGuardians(userId: string): Promise<boolean> {
  const count = await prisma.guardian.count({
    where: {
      userId,
      revokedAt: null
    }
  });
  return count > 0;
}

/**
 * Get the required number of guardian approvals for recovery
 */
export async function getRequiredGuardianApprovals(userId: string): Promise<number> {
  const guardianCount = await prisma.guardian.count({
    where: {
      userId,
      revokedAt: null
    }
  });

  // Require 2-of-N guardians, or all if less than 2
  return Math.min(2, guardianCount);
}

/**
 * Send guardian notification (stub for implementation)
 */
export async function notifyGuardian(
  guardianId: string,
  ticketId: string,
  reason: string
): Promise<void> {
  // In production, this would:
  // 1. Look up guardian's preferred notification method
  // 2. Send secure notification with approval link
  // 3. Log the notification attempt

  console.log(`[Guardian Notification] Guardian: ${guardianId}, Ticket: ${ticketId}, Reason: ${reason}`);
}

/**
 * Validate guardian approval token
 */
export async function validateGuardianToken(
  token: string,
  ticketId: string
): Promise<string | null> {
  // In production, this would:
  // 1. Verify JWT or signed token
  // 2. Check token hasn't expired
  // 3. Extract guardian ID from token
  // 4. Verify guardian is still active for the user

  // For now, return null (no guardian context)
  return null;
}
