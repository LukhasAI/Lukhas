type RateEvent = {
  kind: 'rate_limit.allow' | 'rate_limit.block';
  plan: 'free'|'plus'|'team'|'enterprise'|'core';
  scope: string;
  userId?: string;
  orgId?: string;
  ip?: string;
  remaining?: number;
  retryAfterSec?: number;
  resetAt?: number;
};

type AuthEvent = {
  kind: 'auth.login' | 'auth.logout' | 'auth.signup' | 'auth.passkey_created' | 'auth.token_rotated' | 'auth.token_reuse_detected';
  userId?: string;
  method?: 'passkey' | 'magic_link' | 'sso';
  provider?: string;
  ip?: string;
  userAgent?: string;
  success: boolean;
  error?: string;
};

type SecurityEvent = {
  kind: 'security.token_reuse' | 'security.family_revoked' | 'security.suspicious_activity';
  userId?: string;
  familyId?: string;
  reason: string;
  ip?: string;
  userAgent?: string;
};

let otel: any = null;
try { otel = require('@opentelemetry/api'); } catch { /* optional */ }

function nowIso() { return new Date().toISOString(); }

export const metrics = {
  rateLimit(ev: RateEvent) {
    // Console fallback (structured)
    // eslint-disable-next-line no-console
    console.log(JSON.stringify({ ts: nowIso(), event: ev.kind, ...ev }));

    // OpenTelemetry span (optional)
    if (otel) {
      const tracer = otel.trace.getTracer('lukhas-metrics');
      const span = tracer.startSpan(ev.kind);
      try {
        span.setAttribute('plan', ev.plan);
        span.setAttribute('scope', ev.scope);
        if (ev.userId) span.setAttribute('user.id', ev.userId);
        if (ev.orgId) span.setAttribute('org.id', ev.orgId);
        if (typeof ev.remaining === 'number') span.setAttribute('rate.remaining', ev.remaining);
        if (typeof ev.retryAfterSec === 'number') span.setAttribute('rate.retry_after_sec', ev.retryAfterSec);
        if (typeof ev.resetAt === 'number') span.setAttribute('rate.reset_at', ev.resetAt);
      } finally {
        span.end();
      }
    }
  },

  auth(ev: AuthEvent) {
    // Console log
    // eslint-disable-next-line no-console
    console.log(JSON.stringify({ ts: nowIso(), event: ev.kind, ...ev }));

    // OpenTelemetry
    if (otel) {
      const tracer = otel.trace.getTracer('lukhas-auth');
      const span = tracer.startSpan(ev.kind);
      try {
        if (ev.userId) span.setAttribute('user.id', ev.userId);
        if (ev.method) span.setAttribute('auth.method', ev.method);
        if (ev.provider) span.setAttribute('auth.provider', ev.provider);
        span.setAttribute('auth.success', ev.success);
        if (ev.error) span.setAttribute('auth.error', ev.error);
      } finally {
        span.end();
      }
    }
  },

  security(ev: SecurityEvent) {
    // Always log security events
    console.error(JSON.stringify({ 
      ts: nowIso(), 
      level: 'SECURITY', 
      event: ev.kind, 
      ...ev 
    }));

    // OpenTelemetry with high priority
    if (otel) {
      const tracer = otel.trace.getTracer('lukhas-security');
      const span = tracer.startSpan(ev.kind, {
        attributes: {
          'security.severity': 'high',
          'security.reason': ev.reason
        }
      });
      try {
        if (ev.userId) span.setAttribute('user.id', ev.userId);
        if (ev.familyId) span.setAttribute('family.id', ev.familyId);
        if (ev.ip) span.setAttribute('ip', ev.ip);
        span.setStatus({ code: otel.SpanStatusCode.ERROR, message: ev.reason });
      } finally {
        span.end();
      }
    }
  },

  // Convenience method for tracking API latency
  async trackLatency<T>(
    operation: string,
    fn: () => Promise<T>
  ): Promise<T> {
    const start = Date.now();
    try {
      const result = await fn();
      const duration = Date.now() - start;
      // eslint-disable-next-line no-console
      console.log(JSON.stringify({
        ts: nowIso(),
        event: 'latency',
        operation,
        duration_ms: duration,
        success: true
      }));
      return result;
    } catch (error) {
      const duration = Date.now() - start;
      // eslint-disable-next-line no-console
      console.error(JSON.stringify({
        ts: nowIso(),
        event: 'latency',
        operation,
        duration_ms: duration,
        success: false,
        error: String(error)
      }));
      throw error;
    }
  }
};