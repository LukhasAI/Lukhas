import { NextRequest, NextResponse } from 'next/server';
import { createMagicLink, verifyMagicLink } from '@/packages/auth/magic-links';

export async function POST(req: NextRequest) {
  const { email, ip } = await req.json();
  await createMagicLink({ email, ip }); // enumeration-safe
  return NextResponse.json({ ok: true });
}

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get('token') || '';
  const res = await verifyMagicLink({ token });
  return res.ok ? NextResponse.redirect(new URL('/app', req.url)) : new NextResponse('Invalid', { status: 400 });
}
