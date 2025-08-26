import { NextResponse } from 'next/server';

export function ok(data: any = {}) {
  return NextResponse.json({ ok: true, ...data }, { status: 200 });
}

export function softError(message = 'If your info is correct, instructions have been sent.') {
  // same response for existent/non-existent to avoid enumeration
  return NextResponse.json({ ok: true, note: message }, { status: 200 });
}

export function badRequest(message = 'Invalid request') {
  return NextResponse.json({ ok: false, error: message }, { status: 400 });
}

export function tooMany(retryAfterSec: number) {
  const res = NextResponse.json({ ok: false, error: 'Too Many Requests', retryAfter: retryAfterSec }, { status: 429 });
  res.headers.set('Retry-After', String(retryAfterSec));
  return res;
}
