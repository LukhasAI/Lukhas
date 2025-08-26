import Redis from 'ioredis';

export type ConsumeResult = {
  allowed: boolean;
  remaining: number;       // tokens left in bucket (float)
  nextAvailableAt: number; // epoch ms when next token is available
  retryAfterSec: number;   // convenience header
};

const LUA = `
-- KEYS[1] = tokens key
-- KEYS[2] = ts key
-- ARGV[1] = capacity (burst)
-- ARGV[2] = refill_per_ms (tokens/ms)
-- ARGV[3] = cost (tokens)
-- ARGV[4] = now (ms)

local kTokens = KEYS[1]
local kTs     = KEYS[2]
local capacity      = tonumber(ARGV[1])
local refill_per_ms = tonumber(ARGV[2])
local cost          = tonumber(ARGV[3])
local now           = tonumber(ARGV[4])

local tokens = tonumber(redis.call('GET', kTokens))
local ts     = tonumber(redis.call('GET', kTs))

if tokens == nil then tokens = capacity end
if ts == nil then ts = now end

local delta = now - ts
if delta < 0 then delta = 0 end

tokens = math.min(capacity, tokens + (delta * refill_per_ms))

local allowed = 0
local next_ms = 0
if tokens >= cost then
  tokens = tokens - cost
  allowed = 1
else
  local deficit = cost - tokens
  next_ms = math.ceil(deficit / refill_per_ms)
end

redis.call('SET', kTokens, tokens)
redis.call('SET', kTs, now)

-- TTL ≈ time to fully refill from empty
local ttl = math.ceil((capacity / refill_per_ms))
-- guard upper bound (e.g., 24h)
if ttl > 86400000 then ttl = 86400000 end
redis.call('PEXPIRE', kTokens, ttl)
redis.call('PEXPIRE', kTs, ttl)

return {allowed, tokens, now + next_ms}
`;

export function createTokenBucketLimiter(opts?: { url?: string; namespace?: string }) {
  const redis = new Redis(opts?.url || process.env.REDIS_URL!);
  const ns = (opts?.namespace || 'tb') + ':';
  let sha: string | null = null;

  async function ensureScript() {
    if (sha) return sha;
    sha = await redis.script('LOAD', LUA);
    return sha!;
  }

  return {
    /** ratePerMinute: tokens/min; burst: max capacity; cost: tokens per request (default 1) */
    async consume(params: { key: string; ratePerMinute: number; burst: number; cost?: number }): Promise<ConsumeResult> {
      const now = Date.now();
      const keyTokens = ns + params.key + ':t';
      const keyTs = ns + params.key + ':ts';
      const refillPerMs = params.ratePerMinute / 60000; // tokens per ms
      const cost = params.cost ?? 1;

      const _sha = await ensureScript();
      let res: any;
      try {
        res = await redis.evalsha(
          _sha,
          2, keyTokens, keyTs,
          String(params.burst),
          String(refillPerMs),
          String(cost),
          String(now)
        );
      } catch (e: any) {
        if (e && String(e.message || e).includes('NOSCRIPT')) {
          // Fallback: eval raw script once
          res = await redis.eval(
            LUA,
            2, keyTokens, keyTs,
            String(params.burst),
            String(refillPerMs),
            String(cost),
            String(now)
          );
        } else {
          throw e;
        }
      }

      const allowed = res[0] === 1;
      const remaining = Number(res[1]);
      const nextAvailableAt = Number(res[2]);
      const retryAfterSec = Math.max(0, Math.ceil((nextAvailableAt - now) / 1000));
      return { allowed, remaining, nextAvailableAt, retryAfterSec };
    },
    /** convenience closer if needed */
    async quit() { await redis.quit(); }
  };
}
