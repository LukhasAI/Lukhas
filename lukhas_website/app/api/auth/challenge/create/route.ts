import { NextRequest } from 'next/server';
import { CreateChallenge } from '@/packages/api/schemas';
import { ok, badRequest } from '@/packages/api/respond';
import { prisma } from '@/lib/prisma';
import { randomUUID } from 'crypto';
import { verifyJWT } from '@/packages/auth/jwt';
import { getRandomEmojis } from '@/packages/auth/emoji-catalog';
import { hashAnswer } from '@/packages/auth/hash-utils';

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
  const parsed = CreateChallenge.safeParse(body);
  if (!parsed.success) return badRequest('Invalid payload');

  // get userId from session
  const userId = await getCurrentUserId(req);
  if (!userId) return badRequest('Authentication required');

  const type = parsed.data.type ?? 'grid';

  // Generate challenge based on type
  let challengeData: any = {};
  let expected: any = {};

  if (type === 'grid') {
    // Create a 3x3 grid of emojis
    const emojis = getRandomEmojis(9, { highContrast: false });
    const grid = [];
    for (let i = 0; i < 3; i++) {
      grid.push(emojis.slice(i * 3, (i + 1) * 3));
    }

    // Select 3 random positions as the answer
    const positions = [];
    for (let i = 0; i < 3; i++) {
      positions.push(Math.floor(Math.random() * 9));
    }
    expected = { positions: positions.sort() };

    challengeData = {
      grid: grid.map(row => row.map(e => ({
        emoji: e.emoji,
        label: e.label,
        ariaLabel: e.ariaLabel
      }))),
      targetCount: 3
    };
  }

  const payloadHash = hashAnswer(expected);
  const expiresAt = new Date(Date.now() + 2*60*1000);

  const id = randomUUID();
  await prisma.gridChallenge.create({
    data: {
      id,
      userId,
      type: type as any,
      payloadHash,
      expiresAt
    }
  });

  // Return only challenge payload (UI data), never the answer
  return ok({
    challengeId: id,
    type,
    payload: challengeData,
    ttlMs: 120000
  });
}
