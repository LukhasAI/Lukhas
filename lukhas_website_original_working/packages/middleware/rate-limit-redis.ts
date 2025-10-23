import Redis from 'ioredis';

export type RateHit = {
  limited: boolean;
  count: number;
  remaining: number;
  resetAt: number; // epoch ms
};

export type RateLimiter = {
  limit: (opts: { key: string; windowMs: number; max: number }) => Promise<RateHit>;
};

export function createRedisRateLimiter(opts?: { url?: string; namespace?: string }): RateLimiter {
  const redis = new Redis(opts?.url || process.env.REDIS_URL!);
  const ns = (opts?.namespace || 'rl') + ':';

  // Sliding window using ZSET of timestamps (ms)
  async function limit({ key, windowMs, max }: { key: string; windowMs: number; max: number }): Promise<RateHit> {
    const now = Date.now();
    const bucket = `${ns}${key}`;
    const min = now - windowMs;

    // Remove old hits, add current hit, get count — atomic via MULTI
    const tx = redis.multi()
      .zremrangebyscore(bucket, 0, min)
      .zadd(bucket, now, String(now))
      .zcard(bucket)
      .pexpire(bucket, windowMs + 50); // keep key live for the whole window

    const results = await tx.exec() as [any, any, [null, number], any];
    const count = results[2][1];
    const limited = count > max;
    const remaining = Math.max(0, max - count);
    const resetAt = now + windowMs;

    return { limited, count, remaining, resetAt };
  }

  return { limit };
}
