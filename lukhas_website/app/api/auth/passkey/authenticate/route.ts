import { NextRequest, NextResponse } from 'next/server';
import { startAuthentication, finishAuthentication } from '@/packages/auth/passkeys';
import { issueAccessToken, issueRefreshToken } from '@/packages/auth/jwt';

export async function POST(req: NextRequest) {
  const { userId } = await req.json();
  const options = await startAuthentication({ userId });
  return NextResponse.json(options);
}

export async function PUT(req: NextRequest) {
  const { userId, response, deviceId } = await req.json();
  const { ok } = await finishAuthentication({ userId, response, deviceId });
  if (!ok) return new NextResponse('Unauthorized', { status: 401 });
  const access = await issueAccessToken({ sub: userId });
  const refresh = await issueRefreshToken({ sub: userId, deviceId });
  return NextResponse.json({ access, refresh });
}
