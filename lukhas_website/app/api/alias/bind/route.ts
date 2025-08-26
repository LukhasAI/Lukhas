import { NextRequest } from 'next/server';
import { BindAlias } from '@/packages/api/schemas';
import { prisma } from '@/lib/prisma';
import { ok, badRequest, softError } from '@/packages/api/respond';
import { hmacSHA256 } from '@/packages/util/hash';
import { buildAlias } from '@/packages/identity/lid-alias';
import { randomUUID } from 'crypto';
import { verifyJWT } from '@/packages/auth/jwt';

const PEPPER = process.env.SECRET_PEPPER || 'CHANGE_ME_DEV';

// Get current user from JWT token
async function getCurrentUserId(req: NextRequest): Promise<string|null> {
  const token = req.cookies.get('auth-token')?.value;
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
  const parsed = BindAlias.safeParse(body);
  if (!parsed.success) return badRequest('Invalid payload');

  const userId = await getCurrentUserId(req);
  if (!userId) return softError(); // enumeration-safe

  const { realm, zone, identifier, idType } = parsed.data;
  const valueHash = hmacSHA256(identifier, PEPPER);

  await prisma.verifiedIdentifier.upsert({
    where: { type_valueHash: { type: idType as any, valueHash } },
    update: { userId, verifiedAt: new Date() },
    create: {
      id: randomUUID(),
      userId,
      type: idType as any,
      valueHash,
      valueNorm: identifier,
      verifiedAt: new Date(),
      primary: false
    }
  });

  const aliasResult = await buildAlias({
    realm,
    zone,
    identifier,
    idType: idType as 'email' | 'phone' | 'other'
  });

  await prisma.lidAlias.upsert({
    where: { aliasKey: aliasResult.aliasKey },
    update: {
      userId,
      verifiedAt: new Date(),
      realm,
      zone,
      aliasDisplay: aliasResult.aliasDisplay
    },
    create: {
      id: randomUUID(),
      userId,
      aliasKey: aliasResult.aliasKey,
      aliasDisplay: aliasResult.aliasDisplay,
      realm,
      zone,
      idType: idType as any,
      verifiedAt: new Date()
    }
  });

  return ok({ aliasDisplay: aliasResult.aliasDisplay });
}
