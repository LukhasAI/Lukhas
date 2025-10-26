import { NextRequest, NextResponse } from 'next/server';
import { RecoveryComplete } from '@/packages/api/schemas';
import { ok, badRequest } from '@/packages/api/respond';
import { prisma } from '@/lib/prisma';
import { signJWT } from '@/packages/auth/jwt';

export async function POST(req: NextRequest) {
  const body = await req.json().catch(()=>null);
  const parsed = RecoveryComplete.safeParse(body);
  if (!parsed.success) return badRequest('Invalid payload');

  const { ticketId, method } = parsed.data;
  const t = await prisma.recoveryTicket.findUnique({ where: { id: ticketId } });
  if (!t || t.state !== 'approved' || t.expiresAt < new Date()) return ok({ ok: false });

  // Issue ephemeral, reduced-scope session here (TTL short), require passkey rebind before full access
  const ephemeralToken = await signJWT(
    {
      sub: t.userId,
      scope: 'recovery',
      ephemeral: true,
      ticketId
    },
    '30m'
  );

  await prisma.recoveryTicket.update({ 
    where: { id: ticketId }, 
    data: { state: 'completed' } 
  });
  
  // Set ephemeral cookie
  const response = NextResponse.json({ 
    ephemeral: true, 
    ttlMinutes: 30, 
    method,
    message: 'Recovery complete. Please bind a new passkey immediately.'
  });
  
  response.cookies.set('recovery-token', ephemeralToken, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 1800 // 30 minutes
  });
  
  return response;
}