type WindowOpts = { windowMs: number; max: number; key: string };

const store = new Map<string, { count: number; resetAt: number }>();

export async function rateLimit({ windowMs, max, key }: WindowOpts) {
  const now = Date.now();
  const slot = store.get(key) || { count: 0, resetAt: now + windowMs };
  if (now > slot.resetAt) { 
    slot.count = 0; 
    slot.resetAt = now + windowMs; 
  }
  slot.count += 1; 
  store.set(key, slot);
  const remaining = Math.max(0, max - slot.count);
  const limited = slot.count > max;
  return { limited, remaining, resetAt: slot.resetAt };
}

// Plan-based rate limits from LUKHAS
export const RATE_LIMITS = {
  free: { rpm: 30, rpd: 1000 },
  plus: { rpm: 60, rpd: 5000 },
  team: { rpm: 120, rpd: 20000 },
  enterprise: { rpm: 300, rpd: 100000 },
  core: { rpm: 1000, rpd: 1000000 }
};

export async function checkPlanLimit(plan: keyof typeof RATE_LIMITS, userId: string, endpoint: string) {
  const limits = RATE_LIMITS[plan];
  
  // Check per-minute limit
  const minuteCheck = await rateLimit({
    windowMs: 60_000,
    max: limits.rpm,
    key: `${userId}:${endpoint}:minute`
  });
  
  if (minuteCheck.limited) {
    return { 
      limited: true, 
      resetAt: minuteCheck.resetAt,
      remaining: 0,
      retryAfter: Math.ceil((minuteCheck.resetAt - Date.now()) / 1000)
    };
  }
  
  // Check per-day limit
  const dayCheck = await rateLimit({
    windowMs: 24 * 60 * 60_000,
    max: limits.rpd,
    key: `${userId}:${endpoint}:day`
  });
  
  return {
    limited: dayCheck.limited,
    resetAt: dayCheck.resetAt,
    remaining: Math.min(minuteCheck.remaining, dayCheck.remaining),
    retryAfter: dayCheck.limited ? Math.ceil((dayCheck.resetAt - Date.now()) / 1000) : 0
  };
}

// Example usage in a route:
// const { limited, retryAfter } = await checkPlanLimit('plus', userId, 'api/auth');
// if (limited) {
//   return new NextResponse('Too Many Requests', { 
//     status: 429, 
//     headers: { 'Retry-After': retryAfter.toString() }
//   });
// }
