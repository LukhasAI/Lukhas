import { NextRequest } from 'next/server';
import { VerifyOnboarding } from '@/packages/api/schemas';
import { ok, softError, badRequest } from '@/packages/api/respond';
import { prisma } from '@/lib/prisma';
import { hmacSHA256 } from '@/packages/util/hash';
import { generateUserId } from '@/packages/identity/lid';
import { buildAlias } from '@/packages/identity/lid-alias';
import { randomUUID } from 'crypto';

const PEPPER = process.env.SECRET_PEPPER || 'CHANGE_ME_DEV';

export async function POST(req: NextRequest) {
  const body = await req.json().catch(()=>null);
  const parsed = VerifyOnboarding.safeParse(body);
  if (!parsed.success) return badRequest('Invalid payload');

  const { onboardingId, code } = parsed.data;
  const s = await prisma.onboardingSession.findUnique({ where: { id: onboardingId } });
  if (!s || s.expiresAt < new Date()) return softError(); // enumeration-safe

  // verify code
  const codeHash = hmacSHA256(code, PEPPER);
  if (codeHash !== s.codeHash) {
    await prisma.onboardingSession.update({ where: { id: onboardingId }, data: { attempts: { increment: 1 } }});
    return softError();
  }

  // create user if not exists (by identifier hash)
  const valueHash = hmacSHA256(s.identifierNorm, PEPPER);
  let user = await prisma.user.findFirst({
    where: { identifiers: { some: { type: s.idType, valueHash } } }
  });

  if (!user) {
    user = await prisma.user.create({
      data: { id: generateUserId(), tier: 'free' }
    });
    await prisma.verifiedIdentifier.create({
      data: {
        id: randomUUID(),
        userId: user.id,
        type: s.idType,
        valueHash,
        valueNorm: s.identifierNorm,
        provider: s.idType === 'email' ? s.identifierNorm.split('@')[1] : null,
        verifiedAt: new Date(),
        primary: true
      }
    });
  }

  // alias mint
  const aliasResult = await buildAlias({
    realm: s.realm,
    zone: s.zone,
    identifier: s.identifierNorm,
    idType: s.idType as 'email' | 'phone' | 'other'
  });

  await prisma.lidAlias.upsert({
    where: { aliasKey: aliasResult.aliasKey },
    create: {
      id: randomUUID(),
      userId: user.id,
      aliasKey: aliasResult.aliasKey,
      aliasDisplay: aliasResult.aliasDisplay,
      realm: s.realm,
      zone: s.zone,
      idType: s.idType,
      verifiedAt: new Date()
    },
    update: {
      userId: user.id,
      verifiedAt: new Date(),
      realm: s.realm,
      zone: s.zone,
      aliasDisplay: aliasResult.aliasDisplay
    }
  });

  // cleanup session
  await prisma.onboardingSession.delete({ where: { id: onboardingId } });

  return ok({ lid: user.id, aliasDisplay: aliasResult.aliasDisplay });
}
