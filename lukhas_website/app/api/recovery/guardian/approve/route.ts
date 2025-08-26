import { NextRequest } from 'next/server';
import { RecoveryGuardianApprove } from '@/packages/api/schemas';
import { ok, badRequest } from '@/packages/api/respond';
import { prisma } from '@/lib/prisma';
import { randomUUID } from 'crypto';
import { validateGuardianToken } from '@/packages/auth/guardian-helpers';

export async function POST(req: NextRequest) {
  const body = await req.json().catch(()=>null);
  const parsed = RecoveryGuardianApprove.safeParse(body);
  if (!parsed.success) return badRequest('Invalid payload');

  const { ticketId, approve } = parsed.data;
  const ticket = await prisma.recoveryTicket.findUnique({ where: { id: ticketId } });
  if (!ticket || ticket.state !== 'open' || ticket.expiresAt < new Date()) return ok({ ok: false });

  // Resolve guardianId from auth token if provided
  const authToken = req.headers.get('authorization')?.replace('Bearer ', '');
  const guardianId = authToken ? await validateGuardianToken(authToken, ticketId) : null;

  await prisma.recoveryApproval.create({
    data: {
      id: randomUUID(),
      ticketId,
      guardianId,
      channel: guardianId ? 'guardian' : 'email',
      approved: !!approve
    }
  });

  const approvals = await prisma.recoveryApproval.count({
    where: { ticketId, approved: true }
  });

  const state = approvals >= ticket.requiredApprovals ? 'approved' : 'open';

  await prisma.recoveryTicket.update({
    where: { id: ticketId },
    data: { approvalsCount: approvals, state }
  });

  return ok({
    state,
    approvals,
    required: ticket.requiredApprovals
  });
}
