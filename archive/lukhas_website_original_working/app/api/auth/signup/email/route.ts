import { NextRequest, NextResponse } from 'next/server';
import { sendSignupEmail } from '@/packages/auth/signup';

export async function POST(req: NextRequest) {
  const { email } = await req.json();
  await sendSignupEmail({ email });
  return NextResponse.json({ ok: true, success: true });
}