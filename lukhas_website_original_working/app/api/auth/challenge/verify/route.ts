import { NextRequest } from 'next/server';
import { VerifyChallenge } from '@/packages/api/schemas';
import { ok, badRequest, tooMany } from '@/packages/api/respond';
import { prisma } from '@/lib/prisma';
import { hashAnswer } from '@/packages/auth/hash-utils';

export async function POST(req: NextRequest) {
  const body = await req.json().catch(()=>null);
  const parsed = VerifyChallenge.safeParse(body);
  if (!parsed.success) return badRequest('Invalid payload');

  const { challengeId, response } = parsed.data;
  const ch = await prisma.gridChallenge.findUnique({ where: { id: challengeId } });
  if (!ch || ch.expiresAt < new Date() || ch.consumedAt) return ok({ ok: false });

  if (ch.tries >= 3) return tooMany(60);

  const match = hashAnswer(response) === ch.payloadHash;
  await prisma.gridChallenge.update({
    where: { id: ch.id },
    data: match ? { consumedAt: new Date() } : { tries: { increment: 1 } }
  });

  return ok({ ok: match });
}