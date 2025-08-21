import { createTokenBucketLimiter } from './rate-limit-tokenbucket';

// Import from the existing plans file
const RATE_LIMITS = {
  free: { rpm: 30, rpd: 1000 },
  plus: { rpm: 60, rpd: 5000 },
  team: { rpm: 120, rpd: 20000 },
  enterprise: { rpm: 300, rpd: 100000 },
  core: { rpm: 1000, rpd: 1000000 }
};

const tb = createTokenBucketLimiter({ namespace: 'tb' });

export async function planTokenBucket(params: {
  plan: 'free' | 'plus' | 'team' | 'enterprise' | 'core';
  id: string;     // userId or orgId
  scope: string;  // e.g., 'api:inference'
  ip?: string;
  cost?: number;  // default 1 token per call
}) {
  const limits = RATE_LIMITS[params.plan];
  // Smooth flow at "rpm" with burst up to 1 minute worth (or higher if you want)
  const ratePerMinute = limits.rpm;
  const burst = Math.max(limits.rpm, 30); // allow at least 1-minute burst
  const key = `${params.plan}:${params.id}:${params.scope}:${params.ip || 'na'}`;
  return tb.consume({ key, ratePerMinute, burst, cost: params.cost ?? 1 });
}