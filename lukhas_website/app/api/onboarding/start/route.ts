import { NextRequest } from 'next/server';
import { StartOnboarding } from '@/packages/api/schemas';
import { ok, softError, badRequest } from '@/packages/api/respond';
import { normalizeEmail, normalizePhoneE164 } from '@/packages/util/normalize';
import { hmacSHA256 } from '@/packages/util/hash';
import { prisma } from '@/lib/prisma';
import { randomUUID } from 'crypto';

const PEPPER = process.env.SECRET_PEPPER || 'CHANGE_ME_DEV';
const CODE_TTL_MIN = parseInt(process.env.AUTH_MAGIC_LINK_TTL_SECONDS || '600', 10) / 60;

async function sendCode(idType:'email'|'phone', identifierNorm:string, code: string) {
  // TODO: integrate email/SMS providers
  // For now, no-op. Keep enumeration-safe responses.
  console.log(`[DEV] Verification code for ${idType} ${identifierNorm}: ${code}`);
  return true;
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  const parsed = StartOnboarding.safeParse(body);
  if (!parsed.success) return badRequest('Invalid payload');
  const { realm, zone, identifier, idType } = parsed.data;

  const identifierNorm = idType === 'email' ? normalizeEmail(identifier)
                        : idType === 'phone' ? normalizePhoneE164(identifier)
                        : identifier.trim();

  const code = (Math.floor(100000 + Math.random()*900000)).toString(); // 6-digit
  const codeHash = hmacSHA256(code, PEPPER);
  const expiresAt = new Date(Date.now() + (parseInt(process.env.AUTH_MAGIC_LINK_TTL_SECONDS || '600',10)*1000));

  const onboardingId = randomUUID();
  await prisma.onboardingSession.create({
    data: { id: onboardingId, realm, zone, idType, identifierNorm, codeHash, expiresAt }
  });

  await sendCode(idType as 'email'|'phone', identifierNorm, code);
  return ok({ onboardingId, ttlMinutes: CODE_TTL_MIN });
}
