import { NextRequest } from 'next/server';
import { planTokenBucket } from '@/packages/middleware/plan-tokenbucket';
import { respond429JSON } from '@/packages/http/tooManyRequests';
import { metrics } from '@/packages/metrics';
import { verifyAccessToken } from '@/packages/auth/jwt';

/**
 * Example protected API route with:
 * - JWT authentication
 * - Plan-based rate limiting
 * - Metrics tracking
 * - Localized 429 responses
 */

type Locale = 'en' | 'es' | 'fr' | 'pt-BR' | 'de';

function getLocale(req: NextRequest): Locale {
  const acceptLanguage = req.headers.get('accept-language') || 'en';
  if (acceptLanguage.includes('es')) return 'es';
  if (acceptLanguage.includes('fr')) return 'fr';
  if (acceptLanguage.includes('pt')) return 'pt-BR';
  if (acceptLanguage.includes('de')) return 'de';
  return 'en';
}

function getClientIp(req: NextRequest): string {
  return req.headers.get('x-forwarded-for')?.split(',')[0].trim() || 
         req.headers.get('x-real-ip') || 
         '0.0.0.0';
}

export async function POST(req: NextRequest) {
  const locale = getLocale(req);
  const ip = getClientIp(req);
  const requestId = crypto.randomUUID();
  
  // 1. Authenticate user
  const authHeader = req.headers.get('authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    metrics.auth({
      kind: 'auth.login',
      method: 'passkey',
      ip,
      success: false,
      error: 'missing_token'
    });
    
    return new Response('Unauthorized', { status: 401 });
  }
  
  const token = authHeader.slice(7);
  const { valid, payload } = await verifyAccessToken(token);
  
  if (!valid) {
    metrics.auth({
      kind: 'auth.login',
      userId: payload?.sub,
      method: 'passkey',
      ip,
      success: false,
      error: 'invalid_token'
    });
    
    return new Response('Unauthorized', { status: 401 });
  }
  
  // 2. Get user plan (from token or database)
  const userId = payload.sub as string;
  const userPlan = (payload.plan || 'free') as 'free' | 'plus' | 'team' | 'enterprise' | 'core';
  
  // 3. Check rate limit
  const rl = await planTokenBucket({
    plan: userPlan,
    id: userId,
    scope: 'api:protected',
    ip,
    cost: 1 // Adjust cost based on operation complexity
  });
  
  if (!rl.allowed) {
    // Log rate limit event
    metrics.rateLimit({
      kind: 'rate_limit.block',
      plan: userPlan,
      scope: 'api:protected',
      userId,
      ip,
      remaining: rl.remaining,
      retryAfterSec: rl.retryAfterSec,
      resetAt: rl.nextAvailableAt
    });
    
    // Return localized 429 response
    return respond429JSON({
      retryAfterSec: rl.retryAfterSec,
      locale,
      plan: userPlan,
      scope: 'api:protected',
      limit: {
        rpm: userPlan === 'free' ? 30 :
              userPlan === 'plus' ? 60 :
              userPlan === 'team' ? 120 :
              userPlan === 'enterprise' ? 300 : 1000
      },
      remaining: Math.floor(rl.remaining),
      resetAt: rl.nextAvailableAt,
      requestId
    });
  }
  
  // 4. Log successful rate limit check
  metrics.rateLimit({
    kind: 'rate_limit.allow',
    plan: userPlan,
    scope: 'api:protected',
    userId,
    ip,
    remaining: rl.remaining
  });
  
  // 5. Process the actual request
  try {
    const body = await req.json();
    
    // Track operation latency
    const result = await metrics.trackLatency('api:protected:process', async () => {
      // Your business logic here
      await new Promise(resolve => setTimeout(resolve, 100)); // Simulate work
      return { processed: true, data: body };
    });
    
    // Return success response with rate limit headers
    return new Response(JSON.stringify({
      ok: true,
      result,
      meta: {
        requestId,
        remaining: Math.floor(rl.remaining),
        plan: userPlan
      }
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'X-RateLimit-Limit': String(rl.remaining + 1),
        'X-RateLimit-Remaining': String(Math.floor(rl.remaining)),
        'X-RateLimit-Reset': String(Math.floor(rl.nextAvailableAt / 1000)),
        'X-Request-ID': requestId
      }
    });
    
  } catch (error) {
    // Log error
    console.error('API Error:', error);
    
    return new Response(JSON.stringify({
      ok: false,
      error: 'internal_error',
      requestId
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'X-Request-ID': requestId
      }
    });
  }
}

// GET endpoint to check rate limit status
export async function GET(req: NextRequest) {
  const locale = getLocale(req);
  const authHeader = req.headers.get('authorization');
  
  if (!authHeader?.startsWith('Bearer ')) {
    return new Response('Unauthorized', { status: 401 });
  }
  
  const token = authHeader.slice(7);
  const { valid, payload } = await verifyAccessToken(token);
  
  if (!valid) {
    return new Response('Unauthorized', { status: 401 });
  }
  
  const userId = payload.sub as string;
  const userPlan = (payload.plan || 'free') as 'free' | 'plus' | 'team' | 'enterprise' | 'core';
  
  // Check current rate limit status without consuming
  const limits = {
    free: { rpm: 30, rpd: 1000 },
    plus: { rpm: 60, rpd: 5000 },
    team: { rpm: 120, rpd: 20000 },
    enterprise: { rpm: 300, rpd: 100000 },
    core: { rpm: 1000, rpd: 1000000 }
  };
  
  return new Response(JSON.stringify({
    ok: true,
    plan: userPlan,
    limits: limits[userPlan],
    locale,
    info: {
      en: 'Check your current rate limit status',
      es: 'Verifica tu estado de límite de tasa actual',
      fr: 'Vérifiez votre statut de limite de taux actuel',
      'pt-BR': 'Verifique seu status de limite de taxa atual',
      de: 'Überprüfen Sie Ihren aktuellen Ratenlimit-Status'
    }[locale]
  }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json'
    }
  });
}