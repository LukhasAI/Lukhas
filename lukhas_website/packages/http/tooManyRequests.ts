import { NextResponse } from 'next/server';

export type Locale = 'en'|'es'|'fr'|'pt-BR'|'de';
export type Plan = 'free'|'plus'|'team'|'enterprise'|'core';

const MESSAGES: Record<Locale,(s:number)=>string> = {
  en: (s)=>`You've hit a limit. Try again in ~${s} seconds.`,
  es: (s)=>`Has alcanzado un límite. Inténtalo de nuevo en ~${s} segundos.`,
  fr: (s)=>`Vous avez atteint une limite. Réessayez dans ~${s} secondes.`,
  'pt-BR': (s)=>`Você atingiu um limite. Tente novamente em ~${s} segundos.`,
  de: (s)=>`Du hast ein Limit erreicht. Versuche es in ~${s} Sekunden erneut.`
};

export function respond429JSON(opts: {
  retryAfterSec: number;
  locale?: Locale;
  plan?: Plan;
  scope?: string;            // e.g., "api:inference"
  limit?: { rpm?: number; rpd?: number };
  remaining?: number;
  resetAt?: number;          // epoch ms
  requestId?: string;
}) {
  const {
    retryAfterSec, locale='en', plan, scope, limit, remaining, resetAt, requestId
  } = opts;

  const body = {
    ok: false,
    error: 'rate_limited',
    message: MESSAGES[locale](retryAfterSec),
    meta: { plan, scope, limit, remaining, resetAt, requestId }
  };

  return new NextResponse(JSON.stringify(body), {
    status: 429,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Retry-After': String(Math.max(1, Math.ceil(retryAfterSec))),
      'Cache-Control': 'no-store',
      'X-RateLimit-Limit': limit ? String(limit.rpm || limit.rpd || '') : '',
      'X-RateLimit-Remaining': remaining !== undefined ? String(Math.max(0, Math.floor(remaining))) : '',
      'X-RateLimit-Reset': resetAt ? String(Math.floor(resetAt / 1000)) : ''
    }
  });
}
