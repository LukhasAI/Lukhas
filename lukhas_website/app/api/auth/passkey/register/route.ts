import { NextRequest, NextResponse } from 'next/server';
import { startRegistration, finishRegistration } from '@/packages/auth/passkeys';

export async function POST(req: NextRequest) {
  const { userId, username, displayName } = await req.json();
  const options = await startRegistration({ userId, username, displayName });
  return NextResponse.json(options);
}

export async function PUT(req: NextRequest) {
  const { userId, response } = await req.json();
  const result = await finishRegistration({ userId, response });
  return NextResponse.json(result);
}