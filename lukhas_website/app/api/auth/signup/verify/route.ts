import { NextRequest, NextResponse } from 'next/server';
import { verifySignupEmail } from '@/packages/auth/signup';

export async function POST(req: NextRequest) {
  const { email, code } = await req.json();
  const result = await verifySignupEmail({ email, code });
  return NextResponse.json(result);
}
