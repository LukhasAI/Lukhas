import { createRedisRateLimiter } from './rate-limit-redis';

// Import from the existing plans file
const RATE_LIMITS = {
  free: { rpm: 30, rpd: 1000 },
  plus: { rpm: 60, rpd: 5000 },
  team: { rpm: 120, rpd: 20000 },
  enterprise: { rpm: 300, rpd: 100000 },
  core: { rpm: 1000, rpd: 1000000 }
};

const rl = createRedisRateLimiter({ namespace: 'rl' });

export async function planRateLimit(params: {
  plan: 'free' | 'plus' | 'team' | 'enterprise' | 'core';
  id: string;   // userId or orgId
  scope: string; // e.g. 'api:inference'
  ip?: string;
}) {
  const limits = RATE_LIMITS[params.plan];
  const keyBase = `${params.plan}:${params.id}:${params.scope}`;
  const minute = await rl.limit({
    key: `${keyBase}:1m:${params.ip || 'na'}`,
    windowMs: 60_000,
    max: limits.rpm
  });
  const day = await rl.limit({
    key: `${keyBase}:1d`,
    windowMs: 86_400_000,
    max: limits.rpd
  });

  const limited = minute.limited || day.limited;
  const resetAt = Math.min(minute.resetAt, day.resetAt);
  const remaining = Math.min(minute.remaining, day.remaining);

  return { limited, remaining, resetAt, minute, day };
}
